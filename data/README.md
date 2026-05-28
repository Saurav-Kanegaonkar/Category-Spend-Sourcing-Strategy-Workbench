# Data Sources

All datasets are deterministic synthetic data for a public category sourcing portfolio artifact. They do not represent real railroad procurement records, suppliers, invoices, contracts, bids, market prices, or operating performance.

The synthetic data is modeled on common procurement and category-management structures: category spend baselines, invoice-line contract compliance, supplier master records, market-index movement, supplier KPI scorecards, weighted RFP evaluation, and total-cost-of-ownership scenarios.

- `categories.csv`: category baseline, criticality, market index, contract coverage, and ownership fields.
- `suppliers.csv`: supplier master with qualification, capacity, safety, diversity, and status fields.
- `spend_lines.csv`: synthetic invoice-line spend with contract status, unit price variance, volume, region, and business unit.
- `market_indices.csv`: synthetic monthly index series for commodity, labor, energy, and technology cost drivers.
- `supplier_scorecards.csv`: monthly supplier KPI metrics for OTIF, defect rate, invoice accuracy, responsiveness, safety, and SLA status.
- `rfp_evaluations.csv`: weighted sourcing evaluation and risk-adjusted TCO scenarios for selected categories.
