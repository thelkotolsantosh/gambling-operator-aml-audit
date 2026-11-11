"""Transparent, explainable rule-based AML alert engine for synthetic data."""
import json
from pathlib import Path
import pandas as pd

def load_rules(path="config/risk_rules.json"):
    with open(path, encoding="utf-8") as f:
        return json.load(f)

def _add(alerts, customer_id, rule, score, detail, tx_ids=""):
    alerts.append({
        "customer_id": customer_id, "rule": rule, "score": int(score),
        "detail": detail, "transaction_ids": tx_ids
    })

def run_audit(customers, transactions, rules=None):
    rules = rules or load_rules()
    t, c = transactions.copy(), customers.copy()
    t["timestamp"] = pd.to_datetime(t["timestamp"], errors="coerce")
    t["amount"] = pd.to_numeric(t["amount"], errors="coerce")
    t = t[t["status"].eq("SETTLED")].copy()
    th, wt = rules["thresholds"], rules["weights"]
    alerts = []

    # Customer-level KYC and country controls.
    for row in c.itertuples():
        if row.kyc_status != "VERIFIED":
            _add(alerts, row.customer_id, "KYC_INCOMPLETE", wt["kyc_incomplete"],
                 f"KYC status is {row.kyc_status}")
        if row.country_code in th["high_risk_countries"]:
            _add(alerts, row.customer_id, "HIGH_RISK_CUSTOMER_COUNTRY",
                 wt["high_risk_country"], f"Customer country code {row.country_code} is on configured review list")

    # Transaction pattern rules.
    for cid, g in t.groupby("customer_id"):
        g = g.sort_values("timestamp")
        dep = g[g.transaction_type.eq("DEPOSIT")]
        wd = g[g.transaction_type.eq("WITHDRAWAL")]
        large_dep = dep[dep.amount >= th["large_deposit"]]
        large_wd = wd[wd.amount >= th["large_withdrawal"]]
        if not large_dep.empty:
            _add(alerts, cid, "LARGE_DEPOSIT", wt["large_deposit"],
                 f"{len(large_dep)} settled deposit(s) at/above {th['large_deposit']}",
                 ",".join(large_dep.transaction_id.astype(str)))
        if not large_wd.empty:
            _add(alerts, cid, "LARGE_WITHDRAWAL", wt["large_withdrawal"],
                 f"{len(large_wd)} settled withdrawal(s) at/above {th['large_withdrawal']}",
                 ",".join(large_wd.transaction_id.astype(str)))

        # Rolling 24h deposit-to-withdrawal movement.
        if not dep.empty and not wd.empty:
            for d in dep.itertuples():
                window = wd[(wd.timestamp >= d.timestamp) &
                            (wd.timestamp <= d.timestamp + pd.Timedelta(hours=th["rapid_movement_hours"]))]
                if not window.empty:
                    ratio = window.amount.sum() / max(float(d.amount), 1)
                    if ratio >= th["rapid_movement_ratio"]:
                        _add(alerts, cid, "RAPID_DEPOSIT_WITHDRAWAL",
                             wt["rapid_movement"],
                             f"Withdrawal(s) within {th['rapid_movement_hours']}h equal {ratio:.0%} of deposit {d.transaction_id}",
                             ",".join([str(d.transaction_id)] + window.transaction_id.astype(str).tolist()))
                        break

        # Multiple mid-value deposits within a rolling 24h period.
        d = dep.sort_values("timestamp")
        for i, row in enumerate(d.itertuples()):
            w = d[(d.timestamp >= row.timestamp) &
                  (d.timestamp <= row.timestamp + pd.Timedelta(hours=th["structuring_window_hours"]))]
            candidates = w[(w.amount >= th["structuring_amount_min"]) &
                           (w.amount <= th["structuring_amount_max"])]
            if len(candidates) >= th["structuring_min_transactions"]:
                _add(alerts, cid, "POSSIBLE_STRUCTURING", wt["possible_structuring"],
                     f"{len(candidates)} deposits in configured mid-value range within rolling window",
                     ",".join(candidates.transaction_id.astype(str)))
                break

        # High transaction count in any rolling calendar day.
        for row in g.itertuples():
            w = g[(g.timestamp >= row.timestamp) &
                  (g.timestamp < row.timestamp + pd.Timedelta(hours=24))]
            if len(w) >= th["high_velocity_24h"]:
                _add(alerts, cid, "HIGH_TRANSACTION_VELOCITY", wt["high_velocity"],
                     f"{len(w)} settled transactions in a 24-hour window",
                     ",".join(w.transaction_id.astype(str)))
                break

        # Deposit compared with customer's historical median deposit.
        if len(dep) >= 3:
            med = dep.amount.median()
            unusual = dep[dep.amount >= med * th["unusual_deposit_multiplier"]]
            if not unusual.empty:
                _add(alerts, cid, "UNUSUAL_DEPOSIT", wt["unusual_deposit"],
                     f"Deposit at least {th['unusual_deposit_multiplier']}x customer median ({med:.2f})",
                     ",".join(unusual.transaction_id.astype(str)))

        # Reactivation after long gap (observed activity gap proxy).
        if len(g) >= 2:
            gaps = g.timestamp.diff()
            if (gaps > pd.Timedelta(days=th["dormant_days"])).any():
                _add(alerts, cid, "DORMANT_REACTIVATION", wt["dormant_reactivation"],
                     f"Activity resumed after a gap exceeding {th['dormant_days']} days")

    # Shared-device indicator across multiple customer IDs.
    device_counts = t.groupby("device_id").customer_id.nunique()
    shared = set(device_counts[device_counts >= 3].index)
    if shared:
        for cid, g in t[t.device_id.isin(shared)].groupby("customer_id"):
            devices = sorted(set(g.device_id) & shared)
            _add(alerts, cid, "SHARED_DEVICE", wt["shared_device"],
                 f"Device(s) associated with at least 3 customers: {', '.join(devices)}",
                 ",".join(g.transaction_id.astype(str)))

    if not alerts:
        return pd.DataFrame(columns=["customer_id","rule","score","detail","transaction_ids"])
    return pd.DataFrame(alerts).drop_duplicates(subset=["customer_id","rule"])

def build_customer_scores(customers, alerts, rules=None):
    rules = rules or load_rules()
    if alerts.empty:
        scores = pd.DataFrame({"customer_id": customers.customer_id, "risk_score": 0})
    else:
        scores = alerts.groupby("customer_id", as_index=False).score.sum().rename(columns={"score":"risk_score"})
        scores["risk_score"] = scores.risk_score.clip(upper=100)
        scores = customers[["customer_id"]].merge(scores, on="customer_id", how="left").fillna({"risk_score":0})
    bands = rules["risk_bands"]
    def band(x):
        if x <= bands["low_max"]: return "LOW"
        if x <= bands["medium_max"]: return "MEDIUM"
        if x <= bands["high_max"]: return "HIGH"
        return "CRITICAL"
    scores["risk_level"] = scores.risk_score.map(band)
    return scores
