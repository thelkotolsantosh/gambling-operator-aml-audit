"""Generate fully synthetic gambling-operator AML audit data."""
from pathlib import Path
import numpy as np
import pandas as pd

SEED = 42
COUNTRIES = ["US", "GB", "IN", "CA", "AU", "DE", "FR", "XX", "YY", "ZZ"]

def generate(output_dir="data", customers=800, transactions=16000):
    rng = np.random.default_rng(SEED)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    ids = [f"C{i:05d}" for i in range(1, customers + 1)]
    countries = rng.choice(COUNTRIES, customers, p=[.12,.12,.25,.08,.08,.08,.07,.06,.07,.07])
    signup = pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 600, customers), unit="D")
    kyc = rng.choice(["VERIFIED", "PENDING", "FAILED", "EXPIRED"], customers, p=[.78,.10,.06,.06])
    risk = rng.choice(["LOW", "MEDIUM", "HIGH"], customers, p=[.65,.27,.08])
    customers_df = pd.DataFrame({
        "customer_id": ids, "signup_date": signup.date.astype(str),
        "country_code": countries, "kyc_status": kyc,
        "declared_occupation": rng.choice(["EMPLOYED","SELF_EMPLOYED","STUDENT","OTHER","UNKNOWN"], customers),
        "customer_risk_rating": risk,
        "account_status": rng.choice(["ACTIVE","ACTIVE","ACTIVE","SUSPENDED","CLOSED"], customers)
    })

    tx_customer = rng.choice(ids, transactions)
    start = pd.Timestamp("2026-01-01")
    timestamps = start + pd.to_timedelta(rng.integers(0, 300*24*60, transactions), unit="m")
    types = rng.choice(["DEPOSIT","WITHDRAWAL","BET","WINNINGS","BONUS"], transactions, p=[.30,.17,.30,.18,.05])
    amounts = np.round(np.clip(rng.lognormal(5.2, 1.0, transactions), 5, 12000), 2)
    tx = pd.DataFrame({
        "transaction_id": [f"T{i:07d}" for i in range(1, transactions+1)],
        "customer_id": tx_customer,
        "timestamp": timestamps,
        "transaction_type": types,
        "amount": amounts,
        "currency": "USD",
        "payment_method": rng.choice(["CARD","BANK_TRANSFER","E_WALLET","CRYPTO"], transactions, p=[.42,.28,.22,.08]),
        "country_code": rng.choice(COUNTRIES, transactions),
        "device_id": [f"D{x:04d}" for x in rng.integers(1, customers*0.65, transactions)],
        "ip_address": [f"198.51.100.{x}" for x in rng.integers(1, 250, transactions)],
        "status": rng.choice(["SETTLED","SETTLED","SETTLED","REVERSED","PENDING"], transactions, p=[.72,.12,.08,.04,.04])
    })

    # Inject deterministic, labelled scenarios for audit validation. Labels are for
    # testing only; the audit engine never reads this column.
    scenarios = [
        ("C00001", "DEPOSIT", [1200, 1300, 1400, 1100, 1250]),
        ("C00002", "DEPOSIT", [9000]),
        ("C00003", "WITHDRAWAL", [8500]),
    ]
    for cid, typ, vals in scenarios:
        for j, val in enumerate(vals):
            row = {
                "transaction_id": f"INJECT_{cid}_{j}", "customer_id": cid,
                "timestamp": pd.Timestamp("2026-10-15 10:00") + pd.Timedelta(hours=j*2),
                "transaction_type": typ, "amount": float(val), "currency": "USD",
                "payment_method": "BANK_TRANSFER", "country_code": "XX",
                "device_id": "D_SHARED_001", "ip_address": "203.0.113.10",
                "status": "SETTLED"
            }
            tx = pd.concat([tx, pd.DataFrame([row])], ignore_index=True)

    # A few customers intentionally share one device, for a synthetic control test.
    tx.loc[tx["customer_id"].isin(["C00004","C00005","C00006"]), "device_id"] = "D_SHARED_002"
    tx["timestamp"] = pd.to_datetime(tx["timestamp"])
    tx = tx.sort_values("timestamp").reset_index(drop=True)

    customers_df.to_csv(out / "customers.csv", index=False)
    tx.to_csv(out / "transactions.csv", index=False)
    print(f"Generated {len(customers_df):,} customers and {len(tx):,} transactions in {out}")

if __name__ == "__main__":
    generate()
