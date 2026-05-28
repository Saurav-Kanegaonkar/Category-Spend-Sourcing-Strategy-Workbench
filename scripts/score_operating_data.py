import csv
import json
import math
import random
from collections import defaultdict
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
OUT = ROOT / "analysis" / "outputs"
ANALYSIS = ROOT / "analysis"

SEED = 74219
random.seed(SEED)

MONTHS = [
    "2025-01",
    "2025-02",
    "2025-03",
    "2025-04",
    "2025-05",
    "2025-06",
    "2025-07",
    "2025-08",
    "2025-09",
    "2025-10",
    "2025-11",
    "2025-12",
    "2026-01",
    "2026-02",
    "2026-03",
    "2026-04",
    "2026-05",
    "2026-06",
]

CATEGORIES = [
    {
        "category_id": "CAT-001",
        "category_name": "Rail and Track Materials",
        "category_family": "Engineering materials",
        "manager": "Track sourcing",
        "annual_spend": 184_000_000,
        "criticality": 96,
        "coverage": 0.83,
        "suppliers": 5,
        "tier": "Strategic",
        "index": "Steel mill products",
        "gap": 0.064,
        "owner": "Engineering",
    },
    {
        "category_id": "CAT-002",
        "category_name": "Locomotive Components",
        "category_family": "Mechanical parts",
        "manager": "Mechanical sourcing",
        "annual_spend": 142_000_000,
        "criticality": 93,
        "coverage": 0.76,
        "suppliers": 4,
        "tier": "Strategic",
        "index": "Industrial machinery",
        "gap": 0.082,
        "owner": "Mechanical",
    },
    {
        "category_id": "CAT-003",
        "category_name": "Signal and Communications",
        "category_family": "Technology equipment",
        "manager": "Technology sourcing",
        "annual_spend": 78_000_000,
        "criticality": 91,
        "coverage": 0.71,
        "suppliers": 6,
        "tier": "Strategic",
        "index": "Electronic components",
        "gap": 0.071,
        "owner": "Network operations",
    },
    {
        "category_id": "CAT-004",
        "category_name": "Diesel Fuel and Lubricants",
        "category_family": "Energy",
        "manager": "Fuel sourcing",
        "annual_spend": 312_000_000,
        "criticality": 99,
        "coverage": 0.88,
        "suppliers": 7,
        "tier": "Strategic",
        "index": "Diesel fuel",
        "gap": 0.035,
        "owner": "Transportation",
    },
    {
        "category_id": "CAT-005",
        "category_name": "MRO Tools and Shop Supplies",
        "category_family": "Indirect materials",
        "manager": "MRO sourcing",
        "annual_spend": 54_000_000,
        "criticality": 72,
        "coverage": 0.59,
        "suppliers": 18,
        "tier": "Leverage",
        "index": "Industrial supplies",
        "gap": 0.112,
        "owner": "Mechanical",
    },
    {
        "category_id": "CAT-006",
        "category_name": "Intermodal Terminal Services",
        "category_family": "Operations services",
        "manager": "Terminal sourcing",
        "annual_spend": 96_000_000,
        "criticality": 87,
        "coverage": 0.66,
        "suppliers": 9,
        "tier": "Bottleneck",
        "index": "Freight labor",
        "gap": 0.093,
        "owner": "Intermodal",
    },
    {
        "category_id": "CAT-007",
        "category_name": "Engineering Contractors",
        "category_family": "Field services",
        "manager": "Engineering sourcing",
        "annual_spend": 121_000_000,
        "criticality": 89,
        "coverage": 0.62,
        "suppliers": 12,
        "tier": "Strategic",
        "index": "Construction labor",
        "gap": 0.088,
        "owner": "Engineering",
    },
    {
        "category_id": "CAT-008",
        "category_name": "IT and Network Services",
        "category_family": "Technology services",
        "manager": "IT sourcing",
        "annual_spend": 68_000_000,
        "criticality": 79,
        "coverage": 0.73,
        "suppliers": 10,
        "tier": "Leverage",
        "index": "Cloud services",
        "gap": 0.059,
        "owner": "Information technology",
    },
    {
        "category_id": "CAT-009",
        "category_name": "Facilities Maintenance",
        "category_family": "Corporate services",
        "manager": "Facilities sourcing",
        "annual_spend": 37_000_000,
        "criticality": 58,
        "coverage": 0.53,
        "suppliers": 22,
        "tier": "Routine",
        "index": "Facilities services",
        "gap": 0.126,
        "owner": "Facilities",
    },
    {
        "category_id": "CAT-010",
        "category_name": "Professional Services",
        "category_family": "Corporate services",
        "manager": "Services sourcing",
        "annual_spend": 42_000_000,
        "criticality": 46,
        "coverage": 0.48,
        "suppliers": 26,
        "tier": "Routine",
        "index": "Professional labor",
        "gap": 0.137,
        "owner": "Finance",
    },
]

INDEX_DRIFT = {
    "Steel mill products": (0.9, 1.9),
    "Industrial machinery": (0.5, 1.4),
    "Electronic components": (0.4, 1.7),
    "Diesel fuel": (1.2, 4.8),
    "Industrial supplies": (0.3, 1.2),
    "Freight labor": (0.5, 1.5),
    "Construction labor": (0.7, 1.6),
    "Cloud services": (-0.2, 0.7),
    "Facilities services": (0.4, 1.0),
    "Professional labor": (0.6, 1.3),
}

BUSINESS_UNITS = [
    "Transportation",
    "Mechanical",
    "Engineering",
    "Intermodal",
    "Network operations",
    "Information technology",
    "Facilities",
    "Finance",
]

REGIONS = ["Southeast", "Mid-Atlantic", "Midwest", "Gulf", "Systemwide"]
CONTRACT_STATUS = ["On contract", "Off contract", "Expired agreement", "Catalog mismatch"]
SERVICE_LEVELS = ["Meets SLA", "Watch", "Recovery plan", "Executive review"]


def money(value):
    return round(float(value), 2)


def pct(value):
    return round(float(value), 4)


def write_csv(path, rows, fieldnames):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path):
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def build_categories():
    rows = []
    for cat in CATEGORIES:
        rows.append(
            {
                "category_id": cat["category_id"],
                "category_name": cat["category_name"],
                "category_family": cat["category_family"],
                "category_manager": cat["manager"],
                "annual_baseline_spend": cat["annual_spend"],
                "contract_coverage_pct": pct(cat["coverage"]),
                "operational_criticality": cat["criticality"],
                "incumbent_supplier_count": cat["suppliers"],
                "strategic_tier": cat["tier"],
                "primary_market_index": cat["index"],
                "should_cost_gap_pct": pct(cat["gap"]),
                "business_owner": cat["owner"],
                "baseline_status": random.choice(["Current", "Refresh due", "Needs BU signoff"]),
            }
        )
    return rows


def build_suppliers():
    rows = []
    supplier_id = 1
    for cat in CATEGORIES:
        for idx in range(cat["suppliers"]):
            base_score = max(52, min(96, random.gauss(78, 9)))
            status = "Preferred" if idx < 2 else random.choice(["Approved", "Approved", "Watch", "Development"])
            rows.append(
                {
                    "supplier_id": f"SUP-{supplier_id:03d}",
                    "supplier_name": f"{cat['category_family'].split()[0]} Supplier {idx + 1}",
                    "category_id": cat["category_id"],
                    "category_name": cat["category_name"],
                    "supplier_type": random.choice(["Incumbent", "Challenger", "Regional specialist", "Distributor"]),
                    "diversity_status": random.choice(["Diverse", "Non-diverse", "Small business", "Not classified"]),
                    "rail_qualified": "Yes" if random.random() > 0.12 else "Conditional",
                    "financial_risk": random.choice(["Low", "Low", "Medium", "Medium", "High"]),
                    "capacity_score": round(max(45, min(98, base_score + random.gauss(0, 5))), 1),
                    "safety_score": round(max(45, min(99, base_score + random.gauss(2, 6))), 1),
                    "innovation_score": round(max(35, min(96, base_score + random.gauss(-3, 8))), 1),
                    "service_region": random.choice(REGIONS),
                    "status": status,
                }
            )
            supplier_id += 1
    return rows


def build_indices():
    rows = []
    for index_name, (drift, volatility) in INDEX_DRIFT.items():
        level = random.uniform(96, 104)
        for month in MONTHS:
            shock = random.gauss(drift, volatility)
            if index_name == "Diesel fuel" and month in {"2025-07", "2026-03"}:
                shock += random.uniform(5.5, 8.5)
            if index_name == "Steel mill products" and month in {"2025-10", "2026-04"}:
                shock += random.uniform(2.5, 4.5)
            level = max(82, level * (1 + shock / 100))
            rows.append(
                {
                    "month": month,
                    "market_index": index_name,
                    "index_value": round(level, 2),
                    "monthly_change_pct": pct(shock / 100),
                }
            )
    return rows


def supplier_lookup(suppliers):
    by_cat = defaultdict(list)
    for supplier in suppliers:
        by_cat[supplier["category_id"]].append(supplier)
    return by_cat


def build_spend_lines(suppliers_by_cat):
    rows = []
    invoice_id = 10001
    for cat in CATEGORIES:
        suppliers = suppliers_by_cat[cat["category_id"]]
        weights = [max(1, len(suppliers) - idx) ** 1.25 for idx, _ in enumerate(suppliers)]
        monthly_budget = cat["annual_spend"] / 12
        for month in MONTHS:
            line_count = random.randint(52, 84)
            month_factor = random.uniform(0.86, 1.16)
            for _ in range(line_count):
                supplier = random.choices(suppliers, weights=weights, k=1)[0]
                status_roll = random.random()
                if status_roll < cat["coverage"]:
                    status = "On contract"
                elif status_roll < cat["coverage"] + 0.45 * (1 - cat["coverage"]):
                    status = "Off contract"
                elif status_roll < cat["coverage"] + 0.74 * (1 - cat["coverage"]):
                    status = "Catalog mismatch"
                else:
                    status = "Expired agreement"
                spend = random.lognormvariate(math.log(monthly_budget / line_count), 0.55) * month_factor
                if status != "On contract":
                    spend *= random.uniform(1.08, 1.24)
                volume = max(1, int(random.lognormvariate(3.7, 0.7)))
                unit_price = spend / volume
                variance = random.gauss(cat["gap"] * 100, 3.7)
                if status != "On contract":
                    variance += random.uniform(4.0, 11.0)
                rows.append(
                    {
                        "invoice_id": f"INV-{invoice_id}",
                        "month": month,
                        "category_id": cat["category_id"],
                        "supplier_id": supplier["supplier_id"],
                        "business_unit": random.choice(BUSINESS_UNITS),
                        "region": random.choice(REGIONS),
                        "contract_status": status,
                        "spend_amount": money(spend),
                        "volume": volume,
                        "unit_price": money(unit_price),
                        "price_variance_pct": pct(variance / 100),
                        "payment_terms_days": random.choice([30, 45, 60, 75]),
                        "critical_purchase": "Yes" if random.random() < cat["criticality"] / 125 else "No",
                    }
                )
                invoice_id += 1
    return rows


def build_scorecards(suppliers):
    rows = []
    for supplier in suppliers:
        supplier_bias = (float(supplier["capacity_score"]) - 76) / 5
        for month in MONTHS:
            otif = max(58, min(99, random.gauss(87 + supplier_bias, 5.5)))
            defect = max(0.1, random.gauss(2.2 - supplier_bias / 6, 0.9))
            invoice_accuracy = max(74, min(99.8, random.gauss(93 + supplier_bias / 2, 3.4)))
            responsiveness = max(55, min(99, random.gauss(84 + supplier_bias, 6.6)))
            safety_incidents = 1 if random.random() < max(0.015, (88 - float(supplier["safety_score"])) / 750) else 0
            service = (otif * 0.36) + ((100 - defect * 8) * 0.18) + (invoice_accuracy * 0.18) + (responsiveness * 0.18) + ((100 - safety_incidents * 25) * 0.10)
            rows.append(
                {
                    "month": month,
                    "supplier_id": supplier["supplier_id"],
                    "category_id": supplier["category_id"],
                    "otif_pct": round(otif, 1),
                    "defect_rate_pct": round(defect, 2),
                    "safety_incidents": safety_incidents,
                    "invoice_accuracy_pct": round(invoice_accuracy, 1),
                    "responsiveness_score": round(responsiveness, 1),
                    "service_level_score": round(max(40, min(99, service)), 1),
                    "sla_status": SERVICE_LEVELS[0 if service >= 86 else 1 if service >= 78 else 2 if service >= 70 else 3],
                }
            )
    return rows


def build_rfp_events(suppliers_by_cat):
    target_ids = ["CAT-002", "CAT-003", "CAT-005", "CAT-006", "CAT-007", "CAT-010"]
    rows = []
    for cat_id in target_ids:
        cat = next(item for item in CATEGORIES if item["category_id"] == cat_id)
        suppliers = suppliers_by_cat[cat_id][:5]
        if len(suppliers) < 3:
            suppliers = suppliers_by_cat[cat_id]
        baseline_unit = random.uniform(110, 480) * (1 + cat["gap"])
        for idx, supplier in enumerate(suppliers):
            commercial = max(52, min(98, random.gauss(78, 8)))
            technical = max(50, min(98, float(supplier["capacity_score"]) + random.gauss(0, 5)))
            risk = max(45, min(98, float(supplier["safety_score"]) + random.gauss(0, 6)))
            implementation = max(42, min(96, random.gauss(82 - idx * 2, 7)))
            bid_unit = baseline_unit * random.uniform(0.86, 1.08)
            transition_cost = random.uniform(90_000, 850_000) * (1.6 if idx > 1 else 1)
            annual_volume = random.randint(18_000, 76_000)
            tco = bid_unit * annual_volume + transition_cost + (100 - risk) * 18_000
            weighted = commercial * 0.32 + technical * 0.27 + risk * 0.21 + implementation * 0.20
            rows.append(
                {
                    "event_id": f"RFP-{cat_id[-3:]}",
                    "category_id": cat_id,
                    "category_name": cat["category_name"],
                    "supplier_id": supplier["supplier_id"],
                    "supplier_name": supplier["supplier_name"],
                    "baseline_unit_cost": money(baseline_unit),
                    "bid_unit_cost": money(bid_unit),
                    "annual_volume": annual_volume,
                    "transition_cost": money(transition_cost),
                    "risk_adjusted_tco": money(tco),
                    "commercial_score": round(commercial, 1),
                    "technical_score": round(technical, 1),
                    "risk_score": round(risk, 1),
                    "implementation_score": round(implementation, 1),
                    "weighted_evaluation_score": round(weighted, 1),
                    "negotiation_target_pct": pct(max(0.02, (baseline_unit - bid_unit) / baseline_unit + cat["gap"] / 2)),
                    "recommended_position": "Shortlist" if weighted >= 82 else "Negotiate" if weighted >= 74 else "Hold",
                }
            )
    return rows


def latest_index_pressure(indices):
    values = defaultdict(list)
    for row in indices:
        values[row["market_index"]].append((row["month"], float(row["index_value"])))
    pressure = {}
    for index_name, points in values.items():
        points.sort()
        recent = points[-1][1]
        prior = points[-7][1]
        pressure[index_name] = (recent / prior - 1) * 100
    return pressure


def analyze(categories, suppliers, spend_lines, scorecards, rfp_events, indices):
    category_by_id = {row["category_id"]: row for row in categories}
    suppliers_by_id = {row["supplier_id"]: row for row in suppliers}
    pressure_by_index = latest_index_pressure(indices)

    spend_by_cat = defaultdict(float)
    off_contract_by_cat = defaultdict(float)
    status_by_cat = defaultdict(lambda: defaultdict(float))
    supplier_spend = defaultdict(lambda: defaultdict(float))
    variance_sum = defaultdict(float)
    variance_count = defaultdict(int)
    bu_leakage = defaultdict(lambda: defaultdict(float))

    for row in spend_lines:
        cat_id = row["category_id"]
        spend = float(row["spend_amount"])
        spend_by_cat[cat_id] += spend
        supplier_spend[cat_id][row["supplier_id"]] += spend
        status_by_cat[cat_id][row["contract_status"]] += spend
        variance_sum[cat_id] += float(row["price_variance_pct"])
        variance_count[cat_id] += 1
        if row["contract_status"] != "On contract":
            off_contract_by_cat[cat_id] += spend
            bu_leakage[cat_id][row["business_unit"]] += spend

    score_by_cat = defaultdict(list)
    problem_suppliers = []
    for row in scorecards:
        score = float(row["service_level_score"])
        score_by_cat[row["category_id"]].append(score)
        if row["sla_status"] in {"Recovery plan", "Executive review"}:
            supplier = suppliers_by_id[row["supplier_id"]]
            problem_suppliers.append(
                {
                    "supplier_id": row["supplier_id"],
                    "supplier_name": supplier["supplier_name"],
                    "category_id": row["category_id"],
                    "category_name": category_by_id[row["category_id"]]["category_name"],
                    "month": row["month"],
                    "service_level_score": score,
                    "sla_status": row["sla_status"],
                    "otif_pct": row["otif_pct"],
                    "defect_rate_pct": row["defect_rate_pct"],
                    "next_step": "Escalate supplier recovery plan" if row["sla_status"] == "Executive review" else "Review KPI trend in supplier QBR",
                }
            )

    category_rows = []
    for cat in categories:
        cat_id = cat["category_id"]
        spend = spend_by_cat[cat_id]
        off_contract = off_contract_by_cat[cat_id]
        leakage_pct = off_contract / spend if spend else 0
        supplier_values = list(supplier_spend[cat_id].values())
        total = sum(supplier_values) or 1
        hhi = sum((value / total) ** 2 for value in supplier_values)
        concentration_score = min(100, hhi * 100)
        market_pressure = pressure_by_index[cat["primary_market_index"]]
        avg_service = sum(score_by_cat[cat_id]) / len(score_by_cat[cat_id])
        quality_risk = max(0, 100 - avg_service)
        avg_variance = variance_sum[cat_id] / max(1, variance_count[cat_id])
        gap = float(cat["should_cost_gap_pct"])
        savings = off_contract * 0.085 + spend * gap * 0.28 + max(0, avg_variance) * spend * 0.12
        criticality_score = (
            float(cat["operational_criticality"]) * 0.30
            + min(100, leakage_pct * 180) * 0.20
            + min(100, max(0, market_pressure) * 6) * 0.16
            + concentration_score * 0.12
            + min(100, quality_risk * 3.2) * 0.12
            + min(100, savings / 1_500_000) * 0.10
        )
        if criticality_score >= 58:
            next_move = "Advance sourcing strategy"
        elif leakage_pct > 0.26:
            next_move = "Tighten contract compliance"
        elif quality_risk > 18:
            next_move = "Supplier recovery review"
        else:
            next_move = "Monitor in category cadence"

        highest_leakage_bu = "-"
        if bu_leakage[cat_id]:
            highest_leakage_bu = max(bu_leakage[cat_id].items(), key=lambda item: item[1])[0]

        category_rows.append(
            {
                "category_id": cat_id,
                "category_name": cat["category_name"],
                "category_family": cat["category_family"],
                "strategic_tier": cat["strategic_tier"],
                "business_owner": cat["business_owner"],
                "modeled_spend": money(spend),
                "off_contract_spend": money(off_contract),
                "off_contract_pct": pct(leakage_pct),
                "supplier_count": cat["incumbent_supplier_count"],
                "supplier_concentration_score": round(concentration_score, 1),
                "market_index": cat["primary_market_index"],
                "six_month_market_pressure_pct": pct(market_pressure / 100),
                "avg_price_variance_pct": pct(avg_variance),
                "avg_supplier_service_score": round(avg_service, 1),
                "quality_risk_score": round(quality_risk, 1),
                "savings_potential": money(savings),
                "criticality_score": round(criticality_score, 1),
                "highest_leakage_business_unit": highest_leakage_bu,
                "recommended_move": next_move,
            }
        )

    category_rows.sort(key=lambda row: float(row["criticality_score"]), reverse=True)
    for rank, row in enumerate(category_rows, start=1):
        row["rank"] = rank

    best_rfp = []
    by_event = defaultdict(list)
    for row in rfp_events:
        by_event[row["event_id"]].append(row)
    for event_id, rows in by_event.items():
        rows.sort(key=lambda row: (float(row["weighted_evaluation_score"]), -float(row["risk_adjusted_tco"])), reverse=True)
        best = rows[0].copy()
        baseline = float(best["baseline_unit_cost"]) * int(best["annual_volume"]) * (
            1 + float(best["negotiation_target_pct"]) + 0.04
        )
        tco = float(best["risk_adjusted_tco"])
        best["event_id"] = event_id
        best["rank"] = 1
        best["modeled_savings_vs_baseline"] = money(max(0, baseline - tco))
        best["negotiation_lever"] = choose_lever(best)
        best_rfp.append(best)

    supplier_summary = []
    latest_month = MONTHS[-1]
    supplier_scores = defaultdict(list)
    for row in scorecards:
        supplier_scores[row["supplier_id"]].append(row)
    for supplier in suppliers:
        rows = supplier_scores[supplier["supplier_id"]]
        latest = [row for row in rows if row["month"] == latest_month][0]
        trailing = sum(float(row["service_level_score"]) for row in rows[-6:]) / 6
        defect = sum(float(row["defect_rate_pct"]) for row in rows[-6:]) / 6
        incident_count = sum(int(row["safety_incidents"]) for row in rows[-6:])
        risk = (100 - trailing) * 0.52 + defect * 4 + incident_count * 6
        supplier_summary.append(
            {
                "supplier_id": supplier["supplier_id"],
                "supplier_name": supplier["supplier_name"],
                "category_id": supplier["category_id"],
                "category_name": supplier["category_name"],
                "supplier_type": supplier["supplier_type"],
                "diversity_status": supplier["diversity_status"],
                "financial_risk": supplier["financial_risk"],
                "latest_service_score": latest["service_level_score"],
                "trailing_service_score": round(trailing, 1),
                "trailing_defect_rate_pct": round(defect, 2),
                "six_month_safety_incidents": incident_count,
                "supplier_risk_score": round(risk, 1),
                "sla_status": latest["sla_status"],
                "follow_up": "Executive QBR" if risk >= 22 else "Recovery check" if risk >= 15 else "Standard scorecard",
            }
        )
    supplier_summary.sort(key=lambda row: float(row["supplier_risk_score"]), reverse=True)

    actions = []
    for row in category_rows[:12]:
        if row["recommended_move"] == "Advance sourcing strategy":
            action = "Launch RFI or sourcing wave"
            owner = "Category manager"
        elif row["recommended_move"] == "Tighten contract compliance":
            action = "Review off-contract requester pattern"
            owner = "Procurement operations"
        elif row["recommended_move"] == "Supplier recovery review":
            action = "Schedule supplier KPI recovery review"
            owner = "Supplier performance"
        else:
            action = "Keep in monthly category monitor"
            owner = "Category analyst"
        actions.append(
            {
                "category_id": row["category_id"],
                "category_name": row["category_name"],
                "priority": row["rank"],
                "action": action,
                "owner": owner,
                "business_owner": row["business_owner"],
                "expected_value": row["savings_potential"],
                "due_window": "Next 30 days" if row["rank"] <= 4 else "This quarter",
                "evidence": f"{round(float(row['off_contract_pct']) * 100, 1)}% off-contract, {round(float(row['six_month_market_pressure_pct']) * 100, 1)}% market pressure",
            }
        )

    executive_summary = {
        "generated_on": str(date.today()),
        "seed": SEED,
        "category_count": len(categories),
        "supplier_count": len(suppliers),
        "spend_line_count": len(spend_lines),
        "scorecard_row_count": len(scorecards),
        "rfp_bid_count": len(rfp_events),
        "modeled_spend": money(sum(float(row["modeled_spend"]) for row in category_rows)),
        "off_contract_spend": money(sum(float(row["off_contract_spend"]) for row in category_rows)),
        "off_contract_pct": pct(sum(float(row["off_contract_spend"]) for row in category_rows) / sum(float(row["modeled_spend"]) for row in category_rows)),
        "savings_potential": money(sum(float(row["savings_potential"]) for row in category_rows)),
        "top_category": category_rows[0]["category_name"],
        "top_recommended_move": category_rows[0]["recommended_move"],
        "top_supplier_risk": supplier_summary[0]["supplier_name"],
    }

    app_payload = {
        "summary": executive_summary,
        "category_queue": category_rows,
        "sourcing_recommendations": best_rfp,
        "supplier_risk_queue": supplier_summary[:24],
        "actions": actions,
        "market_indices": indices,
        "status_breakout": [
            {
                "category_id": cat_id,
                "category_name": category_by_id[cat_id]["category_name"],
                "status": status,
                "spend": money(spend),
            }
            for cat_id, statuses in status_by_cat.items()
            for status, spend in statuses.items()
        ],
    }

    return category_rows, best_rfp, supplier_summary, actions, executive_summary, app_payload


def choose_lever(row):
    target = float(row["negotiation_target_pct"])
    if target >= 0.09:
        return "Use should-cost gap and challenger bid to reset rate card"
    if float(row["transition_cost"]) > 500_000:
        return "Trade transition support for longer price protection"
    if float(row["risk_score"]) < 76:
        return "Tie award share to KPI recovery milestones"
    return "Bundle volume and service-level credits"


def write_markdown(summary, category_rows, sourcing_rows, supplier_rows):
    DATA.joinpath("README.md").write_text(
        """# Data Sources

All datasets are deterministic synthetic data for a public category sourcing portfolio artifact. They do not represent real railroad procurement records, suppliers, invoices, contracts, bids, market prices, or operating performance.

The synthetic data is modeled on common procurement and category-management structures: category spend baselines, invoice-line contract compliance, supplier master records, market-index movement, supplier KPI scorecards, weighted RFP evaluation, and total-cost-of-ownership scenarios.

- `categories.csv`: category baseline, criticality, market index, contract coverage, and ownership fields.
- `suppliers.csv`: supplier master with qualification, capacity, safety, diversity, and status fields.
- `spend_lines.csv`: synthetic invoice-line spend with contract status, unit price variance, volume, region, and business unit.
- `market_indices.csv`: synthetic monthly index series for commodity, labor, energy, and technology cost drivers.
- `supplier_scorecards.csv`: monthly supplier KPI metrics for OTIF, defect rate, invoice accuracy, responsiveness, safety, and SLA status.
- `rfp_evaluations.csv`: weighted sourcing evaluation and risk-adjusted TCO scenarios for selected categories.
""",
        encoding="utf-8",
    )

    ANALYSIS.joinpath("analysis_plan.md").write_text(
        """# Analysis Plan

1. Build a spend cube across category, supplier, business unit, region, and contract status.
2. Estimate category criticality using operational importance, off-contract leakage, market pressure, supplier concentration, supplier service risk, price variance, and savings potential.
3. Create a sourcing evaluation surface with weighted supplier scoring, risk-adjusted TCO, transition costs, and negotiation targets.
4. Build supplier scorecards from KPI history and identify suppliers needing recovery plans or executive QBRs.
5. Convert the highest-risk categories into a stakeholder-ready action queue.
""",
        encoding="utf-8",
    )

    top = category_rows[0]
    best = sourcing_rows[0]
    supplier = supplier_rows[0]
    ANALYSIS.joinpath("executive_findings.md").write_text(
        f"""# Executive Findings

## What I Analyzed

I modeled {summary['spend_line_count']:,} invoice-line spend records, {summary['supplier_count']} suppliers, {summary['scorecard_row_count']:,} supplier scorecard rows, {summary['rfp_bid_count']} sourcing bids, and {len(category_rows)} category baselines for a freight rail category-management workflow.

## Findings

- The modeled spend base is ${summary['modeled_spend']:,.0f}, with ${summary['off_contract_spend']:,.0f} classified as off-contract, expired-agreement, or catalog-mismatch leakage.
- The top category priority is {top['category_name']} with a criticality score of {top['criticality_score']}, {round(float(top['off_contract_pct']) * 100, 1)}% non-compliant spend, and ${float(top['savings_potential']):,.0f} in modeled savings potential.
- The strongest sourcing scenario is {best['category_name']} with {best['supplier_name']}, a weighted score of {best['weighted_evaluation_score']}, and ${float(best['modeled_savings_vs_baseline']):,.0f} modeled savings versus baseline.
- The highest supplier follow-up risk is {supplier['supplier_name']} in {supplier['category_name']} with a risk score of {supplier['supplier_risk_score']} and current status of {supplier['sla_status']}.

## Recommendation

Use the criticality queue to choose the next sourcing wave, use the sourcing studio to pressure-test supplier award options, and use the scorecard monitor to separate negotiation opportunities from supplier recovery work.
""",
        encoding="utf-8",
    )

    ANALYSIS.joinpath("methodology.md").write_text(
        """# Methodology

The artifact uses deterministic synthetic data because real procurement data for a freight rail operator is confidential and not publicly available. The generator uses a fixed random seed and category-specific assumptions so the outputs are reproducible.

## Criticality Score

The category criticality score weights operational criticality, off-contract leakage, six-month market pressure, supplier concentration, supplier quality risk, and modeled savings potential.

## Sourcing Evaluation

Supplier bids are scored with a transparent weighted model: commercial score, technical fit, risk score, and implementation readiness. Risk-adjusted TCO combines bid unit cost, annual volume, transition cost, and risk penalty.

## Supplier Scorecard

Supplier service risk is based on trailing service score, defect rate, safety incidents, invoice accuracy, responsiveness, and current SLA status.
""",
        encoding="utf-8",
    )

    ROOT.joinpath("data_dictionary.md").write_text(
        """# Data Dictionary

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
""",
        encoding="utf-8",
    )

    ANALYSIS.joinpath("sql_checks.sql").write_text(
        """-- SQL checks mirror the synthetic CSV outputs in this public portfolio artifact.
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
""",
        encoding="utf-8",
    )

    ROOT.joinpath("STATUS.md").write_text(
        """# Status

- Status: upgraded through the Portfolio Artifact Upgrade Workflow.
- Safe to link as a category sourcing, spend analysis, supplier performance, TCO modeling, and negotiation analytics portfolio artifact after changes are pushed.
- Data: deterministic synthetic data, documented in `data/README.md`.
""",
        encoding="utf-8",
    )


def main():
    DATA.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    ANALYSIS.mkdir(exist_ok=True)

    categories = build_categories()
    suppliers = build_suppliers()
    suppliers_by_cat = supplier_lookup(suppliers)
    indices = build_indices()
    spend_lines = build_spend_lines(suppliers_by_cat)
    scorecards = build_scorecards(suppliers)
    rfp_events = build_rfp_events(suppliers_by_cat)

    write_csv(DATA / "categories.csv", categories, list(categories[0].keys()))
    write_csv(DATA / "suppliers.csv", suppliers, list(suppliers[0].keys()))
    write_csv(DATA / "market_indices.csv", indices, list(indices[0].keys()))
    write_csv(DATA / "spend_lines.csv", spend_lines, list(spend_lines[0].keys()))
    write_csv(DATA / "supplier_scorecards.csv", scorecards, list(scorecards[0].keys()))
    write_csv(DATA / "rfp_evaluations.csv", rfp_events, list(rfp_events[0].keys()))

    category_rows, sourcing_rows, supplier_rows, actions, summary, app_payload = analyze(
        categories, suppliers, spend_lines, scorecards, rfp_events, indices
    )

    write_csv(OUT / "category_criticality_queue.csv", category_rows, list(category_rows[0].keys()))
    write_csv(OUT / "sourcing_scenario_recommendations.csv", sourcing_rows, list(sourcing_rows[0].keys()))
    write_csv(OUT / "supplier_scorecard_risk_queue.csv", supplier_rows, list(supplier_rows[0].keys()))
    write_csv(OUT / "category_action_queue.csv", actions, list(actions[0].keys()))
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    (OUT / "app_payload.json").write_text(json.dumps(app_payload, indent=2), encoding="utf-8")

    write_markdown(summary, category_rows, sourcing_rows, supplier_rows)

    print(f"Generated {len(spend_lines):,} spend lines, {len(scorecards):,} scorecards, and {len(rfp_events)} sourcing bids.")
    print(f"Top category: {summary['top_category']} with next move: {summary['top_recommended_move']}.")
    print(f"Modeled savings potential: ${summary['savings_potential']:,.0f}.")


if __name__ == "__main__":
    main()
