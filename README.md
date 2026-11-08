# Synthetic Gambling Operator AML Audit (Python)

A portfolio-ready, end-to-end **synthetic** AML monitoring audit for an online gambling operator. It generates fictional customer and transaction data, runs transparent risk rules, scores customers, produces an audit report and includes unit tests.

> **Important:** This is an educational simulation, not legal advice, a regulatory compliance certification, or a production AML system. All data and country codes are fictional/test data. A rule hit is an alert for human review—not proof of money laundering.

## Project structure

```text
gambling-aml-audit/
├── config/
│   └── risk_rules.json
├── data/
│   ├── customers.csv              # generated
│   └── transactions.csv           # generated
├── outputs/                       # generated audit evidence
├── src/
│   ├── __init__.py
│   ├── generate_data.py
│   ├── risk_engine.py
│   └── audit.py
├── tests/
│   └── test_risk_engine.py
├── .gitignore
├── requirements.txt
└── README.md
```

## What the audit tests

| Control area | Illustrative test |
|---|---|
| KYC | Pending, failed or expired KYC |
| Customer geography | Configured country-code review list |
| Large transactions | Large deposits and withdrawals |
| Rapid movement | Withdrawal soon after deposit |
| Possible structuring | Repeated mid-value deposits in a rolling window |
| Velocity | High number of settled transactions in 24 hours |
| Customer profile | Deposit materially above historical median |
| Dormancy | Activity after a long observed transaction gap |
| Device linkage | Device associated with multiple customer IDs |

All thresholds and weights are configurable in `config/risk_rules.json`.

## Quick start (Windows PowerShell)

```powershell
# 1. Clone your repository, then enter its folder
cd gambling-aml-audit

# 2. Create and activate a virtual environment
py -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Install dependencies
python -m pip install -r requirements.txt

# 4. Generate synthetic records
python -m src.generate_data

# 5. Run the audit
python -m src.audit

# 6. Run tests
python -m pytest -q
```

If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that terminal, then activate again.

## Run on macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m src.generate_data
python -m src.audit
python -m pytest -q
```

## Data dictionary

### customers.csv
- `customer_id`: synthetic unique customer key
- `signup_date`: account creation date
- `country_code`: synthetic two-letter country code
- `kyc_status`: VERIFIED, PENDING, FAILED or EXPIRED
- `declared_occupation`: synthetic occupation category
- `customer_risk_rating`: LOW, MEDIUM or HIGH
- `account_status`: ACTIVE, SUSPENDED or CLOSED

### transactions.csv
- `transaction_id`, `customer_id`, `timestamp`
- `transaction_type`: DEPOSIT, WITHDRAWAL, BET, WINNINGS or BONUS
- `amount`, `currency`, `payment_method`
- `country_code`, `device_id`, `ip_address`, `status`

IP ranges in generated records are documentation/test ranges, not real customer IP addresses.

## Audit outputs

After running `python -m src.audit`, see:
- `outputs/aml_alerts.csv`
- `outputs/customer_risk_scores.csv`
- `outputs/audit_summary.json`
- `outputs/audit_report.md`
- `outputs/alerts_by_rule.png`

## Suggested auditor workflow

1. Inspect the audit summary and data population.
2. Filter `aml_alerts.csv` by rule and customer.
3. Review the linked transaction IDs in the source transaction file.
4. Record disposition, rationale, evidence, reviewer and approval in a separate case-management process.
5. Tune thresholds only after documenting risk appetite, jurisdiction, product design and validation evidence.
6. Perform false-positive/false-negative testing and independent model validation before any production use.

## Known limitations / next improvements

- This starter project does not implement sanctions/PEP screening, adverse media, payment-account ownership verification, geolocation, source-of-funds evidence, game-play behavioral analytics, bonus abuse detection, case workflow, SAR/STR filing or regulatory reporting.
- The shared-device rule is a simple linkage indicator; shared households, workplaces and public networks can create legitimate matches.
- The sample country codes `XX`, `YY`, `ZZ` are placeholders only.
- For production, use secure access controls, encryption, retention policies, audit logging, explainability, documented governance and jurisdiction-specific legal review.

## License

Add a license of your choice before public distribution. The project contains synthetic data only.
