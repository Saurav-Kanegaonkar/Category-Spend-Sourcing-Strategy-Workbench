# Data Dictionary

## `data/categories.csv`

Category baselines, contract coverage, operational criticality, supplier count, strategic tier, primary market index, should-cost gap, and business owner.

## `data/suppliers.csv`

Supplier master records, including supplier type, diversity status, rail qualification, financial risk, capacity, safety, innovation, service region, and approval status.

## `data/spend_lines.csv`

Synthetic invoice-line spend, including month, category, supplier, business unit, region, contract status, spend amount, volume, unit price, price variance, payment terms, and critical purchase flag.

## `data/market_indices.csv`

Synthetic monthly cost-driver index values by index type and monthly change.

## `data/supplier_scorecards.csv`

Monthly supplier KPI records for on-time in-full performance, defect rate, safety incidents, invoice accuracy, responsiveness, service score, and SLA status.

## `data/rfp_evaluations.csv`

Weighted sourcing-event bid records, including baseline unit cost, bid unit cost, annual volume, transition cost, risk-adjusted TCO, score dimensions, negotiation target, and recommended position.

## `analysis/outputs/category_criticality_queue.csv`

Computed category prioritization, including off-contract leakage, market pressure, supplier concentration, supplier service score, savings potential, criticality score, and recommended next move.

## `analysis/outputs/sourcing_scenario_recommendations.csv`

Best sourcing scenario by event, including risk-adjusted TCO, modeled savings, negotiation target, and negotiation lever.

## `analysis/outputs/supplier_scorecard_risk_queue.csv`

Supplier performance risk queue with trailing score, defect rate, safety incidents, current SLA status, and recommended follow-up.
