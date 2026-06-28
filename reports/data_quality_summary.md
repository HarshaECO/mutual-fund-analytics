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