# Data Quality Summary - Day 1

## Anomalies found while loading raw CSVs

- **01_fund_master.launch_date**: date column not parsed as datetime
- **02_nav_history.date**: date column not parsed as datetime
- **03_aum_by_fund_house.date**: date column not parsed as datetime
- **04_monthly_sip_inflows**: missing values in columns ['yoy_growth_pct']
- **08_investor_transactions.transaction_date**: date column not parsed as datetime
- **09_portfolio_holdings.portfolio_date**: date column not parsed as datetime
- **10_benchmark_indices.date**: date column not parsed as datetime

## AMFI scheme code validation (fund_master vs nav_history)

- Total scheme codes in fund_master: 40
- Total scheme codes in nav_history: 40
- Codes in fund_master with NO nav_history: 0
- Codes in nav_history with NO fund_master entry: 0

## Live NAV Fetch Findings

While fetching live NAV data from mfapi.in for the 6 key schemes, a scheme code mismatch was discovered. Out of the 6 provided AMFI codes, only one (118632 - Nippon Large Cap) returned the correct fund. The other 5 codes returned completely unrelated funds:

- 125497 (expected: HDFC Top 100) → returned SBI Small Cap Fund
- 119551 (expected: SBI Bluechip) → returned Aditya Birla Sun Life Banking and PSU Debt Fund
- 120503 (expected: ICICI Bluechip) → returned Axis ELSS Fund
- 119092 (expected: Axis Bluechip) → returned HDFC Money Market Fund
- 120841 (expected: Kotak Bluechip) → returned quant Mid Cap Fund

This suggests the AMFI scheme codes provided in the task instructions are either outdated or incorrect. Recommend flagging this to the project team for corrected codes before using this live data in any further analysis.