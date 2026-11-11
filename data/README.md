# Data

Run `python -m src.generate_data` from the repository root to generate `customers.csv` and `transactions.csv`.

The generator uses a fixed seed for repeatable test data. It includes injected synthetic scenarios to exercise selected alert rules. The injected scenario labels are not included in the transaction data and are not consumed by the alert engine.

All names, IDs, transactions and IP addresses are fictional. Do not combine these records with real personal data.
