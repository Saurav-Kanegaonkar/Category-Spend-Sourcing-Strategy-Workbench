const state = {
  payload: null,
  selectedCategoryId: null,
  tier: "All tiers",
};

const money = (value, compact = true) =>
  Number(value).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    notation: compact ? "compact" : "standard",
    maximumFractionDigits: compact ? 1 : 0,
  });

const pct = (value, digits = 1) => `${(Number(value) * 100).toFixed(digits)}%`;

const scoreClass = (score) => {
  if (Number(score) >= 82) return "good";
  if (Number(score) >= 72) return "watch";
  return "risk";
};

const byId = (id) => document.getElementById(id);

function renderSummary(summary) {
  byId("runDate").textContent = summary.generated_on;
  byId("summaryGrid").innerHTML = [
    ["Modeled spend", money(summary.modeled_spend), "invoice-line category baseline"],
    ["Non-compliant spend", money(summary.off_contract_spend), `${pct(summary.off_contract_pct)} of modeled spend`],
    ["Savings potential", money(summary.savings_potential), "from compliance, TCO, and should-cost gaps"],
    ["Supplier base", summary.supplier_count, `${summary.scorecard_row_count.toLocaleString()} scorecard rows`],
  ]
    .map(
      ([label, value, note]) => `
        <article class="metric-card">
          <span>${label}</span>
          <strong>${value}</strong>
          <small>${note}</small>
        </article>
      `
    )
    .join("");
}

function categoryRows() {
  const rows = state.payload.category_queue;
  if (state.tier === "All tiers") return rows;
  return rows.filter((row) => row.strategic_tier === state.tier);
}

function renderTierFilter() {
  const tiers = ["All tiers", ...new Set(state.payload.category_queue.map((row) => row.strategic_tier))];
  byId("tierFilter").innerHTML = tiers.map((tier) => `<option>${tier}</option>`).join("");
  byId("tierFilter").value = state.tier;
}

function renderCategoryTable() {
  const rows = categoryRows();
  byId("queueCount").textContent = `${rows.length} categories`;
  if (!state.selectedCategoryId || !rows.some((row) => row.category_id === state.selectedCategoryId)) {
    state.selectedCategoryId = rows[0]?.category_id;
  }

  byId("categoryRows").innerHTML = rows
    .map(
      (row) => `
        <tr class="${row.category_id === state.selectedCategoryId ? "is-selected" : ""}" data-category-id="${row.category_id}">
          <td>${row.rank}</td>
          <td>
            <button class="link-button" type="button" data-category-id="${row.category_id}">
              ${row.category_name}
            </button>
            <small>${row.category_family} · ${row.strategic_tier}</small>
          </td>
          <td><span class="score ${scoreClass(row.criticality_score)}">${row.criticality_score}</span></td>
          <td>${pct(row.off_contract_pct)}</td>
          <td>${money(row.savings_potential)}</td>
          <td>${row.recommended_move}</td>
        </tr>
      `
    )
    .join("");

  document.querySelectorAll("[data-category-id]").forEach((button) => {
    button.addEventListener("click", () => {
      state.selectedCategoryId = button.dataset.categoryId;
      renderCriticality();
    });
  });
}

function renderCategoryDetail() {
  const row = state.payload.category_queue.find((item) => item.category_id === state.selectedCategoryId);
  if (!row) return;
  byId("categoryDetail").innerHTML = `
    <p class="eyebrow">Selected category</p>
    <h3>${row.category_name}</h3>
    <dl class="detail-list">
      <div><dt>Business owner</dt><dd>${row.business_owner}</dd></div>
      <div><dt>Modeled spend</dt><dd>${money(row.modeled_spend, false)}</dd></div>
      <div><dt>Off-contract leakage</dt><dd>${money(row.off_contract_spend, false)} · ${pct(row.off_contract_pct)}</dd></div>
      <div><dt>Market pressure</dt><dd>${row.market_index} · ${pct(row.six_month_market_pressure_pct)}</dd></div>
      <div><dt>Supplier service</dt><dd>${row.avg_supplier_service_score} average score</dd></div>
      <div><dt>Highest leakage BU</dt><dd>${row.highest_leakage_business_unit}</dd></div>
    </dl>
    <div class="callout">
      <span>Recommended move</span>
      <strong>${row.recommended_move}</strong>
    </div>
  `;
}

function renderComplianceBars() {
  const topRows = state.payload.category_queue.slice(0, 8);
  const maxSpend = Math.max(...topRows.map((row) => Number(row.modeled_spend)));
  byId("complianceBars").innerHTML = topRows
    .map((row) => {
      const totalWidth = (Number(row.modeled_spend) / maxSpend) * 100;
      const leakageWidth = Math.max(4, Number(row.off_contract_pct) * totalWidth);
      return `
        <div class="bar-row">
          <div>
            <strong>${row.category_name}</strong>
            <span>${money(row.modeled_spend)} spend · ${pct(row.off_contract_pct)} non-compliant</span>
          </div>
          <div class="bar-track" aria-hidden="true">
            <span class="bar-total" style="width:${totalWidth}%"></span>
            <span class="bar-risk" style="width:${leakageWidth}%"></span>
          </div>
        </div>
      `;
    })
    .join("");
}

function renderCriticality() {
  renderTierFilter();
  renderCategoryTable();
  renderCategoryDetail();
  renderComplianceBars();
}

function renderSourcing() {
  const rows = state.payload.sourcing_recommendations;
  byId("sourcingCards").innerHTML = rows
    .map(
      (row) => `
        <article class="scenario-card">
          <span class="pill">${row.recommended_position}</span>
          <h3>${row.category_name}</h3>
          <p>${row.supplier_name}</p>
          <div class="scenario-stats">
            <div><span>Weighted score</span><strong>${row.weighted_evaluation_score}</strong></div>
            <div><span>Risk TCO</span><strong>${money(row.risk_adjusted_tco)}</strong></div>
            <div><span>Savings</span><strong>${money(row.modeled_savings_vs_baseline)}</strong></div>
          </div>
          <div class="callout compact">
            <span>Negotiation lever</span>
            <strong>${row.negotiation_lever}</strong>
          </div>
        </article>
      `
    )
    .join("");

  byId("tcoMatrix").innerHTML = rows
    .map(
      (row) => `
        <div class="matrix-row">
          <span>${row.category_name}</span>
          <strong>${row.supplier_name}</strong>
          <em>${pct(row.negotiation_target_pct)} target</em>
          <small>${money(row.transition_cost, false)} transition cost</small>
        </div>
      `
    )
    .join("");
}

function renderSuppliers() {
  byId("supplierList").innerHTML = state.payload.supplier_risk_queue
    .slice(0, 12)
    .map(
      (row) => `
        <article class="supplier-item">
          <div>
            <strong>${row.supplier_name}</strong>
            <span>${row.category_name} · ${row.financial_risk} financial risk</span>
          </div>
          <div class="supplier-score">
            <b>${row.supplier_risk_score}</b>
            <small>${row.follow_up}</small>
          </div>
        </article>
      `
    )
    .join("");

  byId("actionList").innerHTML = state.payload.actions
    .slice(0, 8)
    .map(
      (row) => `
        <article class="action-item">
          <span>${row.priority}</span>
          <div>
            <strong>${row.action}</strong>
            <p>${row.category_name}</p>
            <small>${row.owner} · ${row.due_window} · ${row.evidence}</small>
          </div>
        </article>
      `
    )
    .join("");
}

function setupTabs() {
  document.querySelectorAll(".tab").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab").forEach((tab) => tab.classList.remove("is-active"));
      document.querySelectorAll(".surface").forEach((surface) => surface.classList.remove("is-active"));
      button.classList.add("is-active");
      byId(button.dataset.surface).classList.add("is-active");
    });
  });
}

async function init() {
  const response = await fetch("analysis/outputs/app_payload.json");
  state.payload = await response.json();
  state.selectedCategoryId = state.payload.category_queue[0].category_id;
  renderSummary(state.payload.summary);
  renderCriticality();
  renderSourcing();
  renderSuppliers();
  setupTabs();

  byId("tierFilter").addEventListener("change", (event) => {
    state.tier = event.target.value;
    renderCriticality();
  });
}

init().catch((error) => {
  document.body.innerHTML = `<main class="app-shell"><div class="panel"><h1>Unable to load workbench data</h1><p>${error.message}</p></div></main>`;
});
