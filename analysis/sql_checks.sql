-- SQL checks mirror the synthetic CSV outputs in this public portfolio artifact.
-- They are written in portable SQL style for explanation, not bound to a live warehouse.

-- 1. Category spend and compliance leakage.
select
  category_id,
  sum(spend_amount) as total_spend,
  sum(case when contract_status <> 'On contract' then spend_amount else 0 end) as non_compliant_spend
from spend_lines
group by category_id;

-- 2. Supplier KPI watch list.
select
  supplier_id,
  category_id,
  avg(service_level_score) as trailing_service_score,
  sum(safety_incidents) as safety_incidents
from supplier_scorecards
where month >= '2026-01'
group by supplier_id, category_id
having avg(service_level_score) < 78 or sum(safety_incidents) > 0;

-- 3. Sourcing award scenario review.
select
  event_id,
  supplier_id,
  weighted_evaluation_score,
  risk_adjusted_tco,
  negotiation_target_pct
from rfp_evaluations
where recommended_position in ('Shortlist', 'Negotiate')
order by event_id, weighted_evaluation_score desc;
