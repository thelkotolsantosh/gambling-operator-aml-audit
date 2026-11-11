"""Run the end-to-end synthetic gambling AML audit and produce audit evidence."""
from pathlib import Path
import json
import pandas as pd
import matplotlib.pyplot as plt
from .generate_data import generate
from .risk_engine import load_rules, run_audit, build_customer_scores

def main():
    data_dir, out_dir = Path("data"), Path("outputs")
    data_dir.mkdir(exist_ok=True); out_dir.mkdir(exist_ok=True)
    if not (data_dir/"customers.csv").exists() or not (data_dir/"transactions.csv").exists():
        generate(data_dir)
    customers = pd.read_csv(data_dir/"customers.csv")
    tx = pd.read_csv(data_dir/"transactions.csv", parse_dates=["timestamp"])
    rules = load_rules()
    alerts = run_audit(customers, tx, rules)
    scores = build_customer_scores(customers, alerts, rules)

    alerts.to_csv(out_dir/"aml_alerts.csv", index=False)
    scores.to_csv(out_dir/"customer_risk_scores.csv", index=False)
    summary = {
        "audit_type": "Synthetic gambling operator AML monitoring review",
        "data_scope": {"customers": int(len(customers)), "transactions": int(len(tx)),
                       "settled_transactions": int((tx.status=="SETTLED").sum())},
        "alerts": int(len(alerts)),
        "customers_with_alerts": int(alerts.customer_id.nunique()) if not alerts.empty else 0,
        "risk_level_counts": scores.risk_level.value_counts().to_dict(),
        "rule_counts": alerts.rule.value_counts().to_dict() if not alerts.empty else {},
        "limitations": [
            "All records are synthetic and are not evidence of real customer conduct.",
            "Rules are illustrative and require jurisdiction-specific legal and compliance approval.",
            "A rule hit is an investigative lead, not proof of money laundering.",
            "No automated SAR/STR filing or customer action is performed."
        ]
    }
    (out_dir/"audit_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    if not alerts.empty:
        alerts.rule.value_counts().sort_values().plot(kind="barh", figsize=(9,5), title="AML alerts by rule")
        plt.tight_layout(); plt.savefig(out_dir/"alerts_by_rule.png", dpi=150); plt.close()
    report = [
        "# Synthetic Gambling Operator — AML Audit Report", "",
        "## 1. Executive summary",
        f"- Customers reviewed: **{len(customers):,}**",
        f"- Transactions reviewed: **{len(tx):,}** ({summary['data_scope']['settled_transactions']:,} settled)",
        f"- Alerts generated: **{len(alerts):,}**",
        f"- Customers with alerts: **{summary['customers_with_alerts']:,}**", "",
        "This is a simulated, rule-based monitoring review. Alert counts are not findings of criminal conduct.", "",
        "## 2. Scope and methodology",
        "- Reviewed synthetic customer/KYC attributes and settled deposits, withdrawals, bets, winnings and bonuses.",
        "- Applied configurable rules for large transactions, rapid movement, possible structuring, velocity, high-risk country codes, incomplete KYC, shared devices, dormancy and unusual deposits.",
        "- Aggregated rule hits into capped customer risk scores.", "",
        "## 3. Rule results",
        "| Rule | Alert count |", "|---|---:|"
    ]
    for rule, count in summary["rule_counts"].items():
        report.append(f"| {rule} | {count} |")
    report += ["", "## 4. Risk distribution", "| Risk level | Customers |", "|---|---:|"]
    for level, count in scores.risk_level.value_counts().items():
        report.append(f"| {level} | {count} |")
    report += ["", "## 5. Audit observations and recommended testing",
        "1. Validate that KYC status is current, complete and risk-rated before relevant activity is permitted.",
        "2. Review large deposits/withdrawals against customer profile, source of funds and payment ownership.",
        "3. Investigate rapid deposit-to-withdrawal movement and repeated mid-value deposits using full account context.",
        "4. Examine shared devices/IPs for legitimate household or network explanations before escalation.",
        "5. Test monitoring coverage, alert timeliness, case documentation, escalation and SAR/STR decision governance.",
        "6. Validate country risk methodology against the operator's applicable legal and regulatory framework.",
        "", "## 6. Limitations",
        "- The data is artificial, generated with a fixed random seed and includes a few injected test scenarios.",
        "- Thresholds are examples only; do not use them as legal thresholds or production controls.",
        "- The dormancy rule uses observed transaction gaps as a proxy, not verified login/account inactivity.",
        "- The country-code list is fictional/configurable and is not a sanctions or FATF list.",
        "- No conclusions can be drawn about real individuals or an actual gambling business.",
        "", "## 7. Output files",
        "- `aml_alerts.csv`: explainable rule-level alerts.",
        "- `customer_risk_scores.csv`: customer-level score and risk band.",
        "- `audit_summary.json`: machine-readable summary.",
        "- `alerts_by_rule.png`: alert distribution chart.", ""]
    (out_dir/"audit_report.md").write_text("\n".join(report), encoding="utf-8")
    print("Audit complete. Review the outputs/ directory.")

if __name__ == "__main__":
    main()
