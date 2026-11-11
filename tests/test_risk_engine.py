import pandas as pd
from src.risk_engine import run_audit, build_customer_scores

def test_large_deposit_generates_alert():
    customers = pd.DataFrame([{"customer_id":"C1","kyc_status":"VERIFIED","country_code":"US"}])
    tx = pd.DataFrame([{
        "transaction_id":"T1","customer_id":"C1","timestamp":"2026-01-01 10:00:00",
        "transaction_type":"DEPOSIT","amount":6000,"status":"SETTLED",
        "device_id":"D1","country_code":"US"
    }])
    alerts = run_audit(customers, tx)
    assert "LARGE_DEPOSIT" in set(alerts.rule)

def test_unsettled_transaction_is_ignored():
    customers = pd.DataFrame([{"customer_id":"C1","kyc_status":"VERIFIED","country_code":"US"}])
    tx = pd.DataFrame([{
        "transaction_id":"T1","customer_id":"C1","timestamp":"2026-01-01 10:00:00",
        "transaction_type":"DEPOSIT","amount":9000,"status":"PENDING",
        "device_id":"D1","country_code":"US"
    }])
    alerts = run_audit(customers, tx)
    assert "LARGE_DEPOSIT" not in set(alerts.rule)

def test_scores_include_all_customers():
    customers = pd.DataFrame([{"customer_id":"C1"},{"customer_id":"C2"}])
    alerts = pd.DataFrame([{"customer_id":"C1","score":20}])
    scores = build_customer_scores(customers, alerts)
    assert len(scores) == 2
    assert scores.loc[scores.customer_id=="C2","risk_score"].iloc[0] == 0
