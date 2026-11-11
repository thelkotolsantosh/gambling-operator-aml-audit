# Synthetic Gambling Operator — AML Audit Report

## 1. Executive summary
- Customers reviewed: **800**
- Transactions reviewed: **16,007** (14,706 settled)
- Alerts generated: **1,586**
- Customers with alerts: **800**

This is a simulated, rule-based monitoring review. Alert counts are not findings of criminal conduct.

## 2. Scope and methodology
- Reviewed synthetic customer/KYC attributes and settled deposits, withdrawals, bets, winnings and bonuses.
- Applied configurable rules for large transactions, rapid movement, possible structuring, velocity, high-risk country codes, incomplete KYC, shared devices, dormancy and unusual deposits.
- Aggregated rule hits into capped customer risk scores.

## 3. Rule results
| Rule | Alert count |
|---|---:|
| SHARED_DEVICE | 800 |
| UNUSUAL_DEPOSIT | 367 |
| KYC_INCOMPLETE | 188 |
| HIGH_RISK_CUSTOMER_COUNTRY | 154 |
| DORMANT_REACTIVATION | 46 |
| RAPID_DEPOSIT_WITHDRAWAL | 26 |
| LARGE_DEPOSIT | 3 |
| POSSIBLE_STRUCTURING | 1 |
| LARGE_WITHDRAWAL | 1 |

## 4. Risk distribution
| Risk level | Customers |
|---|---:|
| MEDIUM | 459 |
| LOW | 232 |
| HIGH | 103 |
| CRITICAL | 6 |

## 5. Audit observations and recommended testing
1. Validate that KYC status is current, complete and risk-rated before relevant activity is permitted.
2. Review large deposits/withdrawals against customer profile, source of funds and payment ownership.
3. Investigate rapid deposit-to-withdrawal movement and repeated mid-value deposits using full account context.
4. Examine shared devices/IPs for legitimate household or network explanations before escalation.
5. Test monitoring coverage, alert timeliness, case documentation, escalation and SAR/STR decision governance.
6. Validate country risk methodology against the operator's applicable legal and regulatory framework.

## 6. Limitations
- The data is artificial, generated with a fixed random seed and includes a few injected test scenarios.
- Thresholds are examples only; do not use them as legal thresholds or production controls.
- The dormancy rule uses observed transaction gaps as a proxy, not verified login/account inactivity.
- The country-code list is fictional/configurable and is not a sanctions or FATF list.
- No conclusions can be drawn about real individuals or an actual gambling business.

## 7. Output files
- `aml_alerts.csv`: explainable rule-level alerts.
- `customer_risk_scores.csv`: customer-level score and risk band.
- `audit_summary.json`: machine-readable summary.
- `alerts_by_rule.png`: alert distribution chart.
