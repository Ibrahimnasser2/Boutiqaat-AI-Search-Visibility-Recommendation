let chart = null;

async function api(path, opts) {
  const r = await fetch(path, { headers: { "Content-Type": "application/json" }, ...opts });
  if (!r.ok) throw new Error(await r.text());
  return r.json();
}

function showError(msg) {
  const el = document.getElementById("errorBox");
  el.textContent = msg;
  el.classList.remove("hidden");
}

function setCaption(text) {
  const bar = document.getElementById("caption");
  if (!text) {
    bar.style.display = "none";
    document.body.classList.remove("has-caption");
    return;
  }
  bar.textContent = text;
  bar.style.display = "block";
  document.body.classList.add("has-caption");
}
window.setCaption = setCaption;

function setStep(n) {
  document.querySelectorAll(".pill").forEach((el) => {
    const s = Number(el.dataset.step);
    el.classList.remove("active", "done");
    if (s === n) el.classList.add("active");
    else if (s < n) el.classList.add("done");
  });
}
window.setStep = setStep;

function sev(s) {
  return (
    {
      high: "bg-red-100 text-red-700",
      medium: "bg-amber-100 text-amber-700",
      low: "bg-green-100 text-green-700",
    }[s] || "bg-slate-100"
  );
}

function renderQueries(queries) {
  const list = document.getElementById("queriesList");
  const empty = document.getElementById("queriesEmpty");
  document.getElementById("lblQueryCount").textContent = queries.length + " loaded";
  if (!queries.length) {
    empty.classList.remove("hidden");
    list.classList.add("hidden");
    document.getElementById("btnRun").disabled = true;
    return;
  }
  empty.classList.add("hidden");
  list.classList.remove("hidden");
  list.innerHTML = queries
    .map(
      (q, i) => `
    <div class="py-3 flex gap-3 items-start">
      <span class="text-xs font-mono text-violet-500 mt-0.5 w-6">${i + 1}</span>
      <div class="flex-1">
        <p class="text-sm font-medium">${q.text}</p>
        <p class="text-xs text-slate-400 mt-1">
          <span class="inline-block bg-slate-100 rounded px-1.5 mr-1">${q.intent}</span>
          <span class="inline-block bg-slate-100 rounded px-1.5 mr-1">${q.category}</span>
          <span class="inline-block bg-slate-100 rounded px-1.5">${q.geography}</span>
        </p>
      </div>
    </div>`
    )
    .join("");
  document.getElementById("btnRun").disabled = false;
  setStep(2);
}

function renderMetrics(o) {
  const items = [
    ["Total Queries", o.total_queries],
    ["Mention Rate", o.mention_rate + "%"],
    ["Recommendation Rate", o.recommendation_rate + "%"],
    ["Visibility Score", o.visibility_score],
    ["Avg Position", o.average_position ?? "N/A"],
    ["Top-3 Rate", o.top3_rate + "%"],
    ["Source Coverage", o.source_coverage + "%"],
    ["AI Runs", o.total_runs],
  ];
  document.getElementById("metricsGrid").innerHTML = items
    .map(
      ([l, v]) =>
        `<div class="bg-white rounded-xl p-5 border shadow-sm"><p class="text-sm text-slate-500">${l}</p><p class="text-2xl font-semibold text-violet-600 mt-1">${v}</p></div>`
    )
    .join("");
}

function renderCompetitors(comps) {
  const rows = comps
    .slice(0, 8)
    .map(
      (c) =>
        `<tr class="border-b"><td class="py-2 font-medium">${c.name}</td><td>${c.mention_rate}%</td><td>${c.recommendation_rate}%</td><td>${c.average_position ?? "—"}</td><td>${c.top3_rate}%</td></tr>`
    )
    .join("");
  document.getElementById("tableCompetitors").innerHTML =
    `<table class="w-full"><thead><tr class="text-slate-500 text-left"><th class="pb-2">Company</th><th>Mention</th><th>Recommended</th><th>Avg Pos</th><th>Top-3</th></tr></thead><tbody>${rows}</tbody></table>`;
}

function renderIntentChart(intents) {
  const ctx = document.getElementById("chartIntent").getContext("2d");
  if (chart) chart.destroy();
  chart = new Chart(ctx, {
    type: "bar",
    data: {
      labels: intents.map((i) => i.intent),
      datasets: [
        { label: "Mention %", data: intents.map((i) => i.mention_rate), backgroundColor: "#a78bfa" },
        {
          label: "Recommended %",
          data: intents.map((i) => i.recommendation_rate),
          backgroundColor: "#6d28d9",
        },
      ],
    },
    options: { responsive: true, scales: { y: { beginAtZero: true, max: 100 } } },
  });
}

function bindRunClicks() {
  document.querySelectorAll("[data-run]").forEach((btn) => {
    btn.onclick = () => openDetail(Number(btn.dataset.run));
  });
}

function renderOpportunities(opps) {
  document.getElementById("listOpportunities").innerHTML = opps
    .slice(0, 9)
    .map(
      (o) => `
    <div class="border rounded-lg p-4">
      <div class="flex justify-between gap-2">
        <h3 class="font-medium text-sm">${o.title}</h3>
        <span class="text-xs px-2 py-0.5 rounded-full ${sev(o.severity)}">${o.severity}</span>
      </div>
      <p class="text-xs text-slate-500 mt-2">${(o.explanation || "").slice(0, 140)}…</p>
      <p class="text-xs text-violet-600 mt-1">${o.recommendation || ""}</p>
      <button data-run="${o.run_id}" class="text-xs text-violet-500 mt-2 hover:underline">View query →</button>
    </div>`
    )
    .join("");
  bindRunClicks();
}

function renderRuns(runs) {
  document.getElementById("listRuns").innerHTML = runs
    .slice(0, 15)
    .map(
      (r) =>
        `<button data-run="${r.id}" class="w-full flex justify-between gap-4 border rounded-lg px-4 py-3 hover:bg-violet-50 text-left">
      <span class="text-sm font-medium flex-1">${r.query_text || "Query #" + r.query_id}</span>
      <span class="text-xs text-violet-600 whitespace-nowrap">View analysis →</span>
    </button>`
    )
    .join("");
  bindRunClicks();
}

async function loadQueriesOnly() {
  setStep(1);
  await api("/api/queries/load-sample", { method: "POST" });
  const queries = await api("/api/queries");
  renderQueries(queries);
  document.getElementById("panelDashboard").classList.add("hidden");
  document.getElementById("panelDetail").classList.add("hidden");
  document.getElementById("panelQueries").classList.remove("hidden");
}
window.loadQueriesOnly = loadQueriesOnly;

async function loadDashboard() {
  const [overview, intents, competitors, opportunities, runs, health] = await Promise.all([
    api("/api/analysis/overview"),
    api("/api/analysis/intents"),
    api("/api/analysis/competitors"),
    api("/api/analysis/opportunities"),
    api("/api/runs"),
    api("/api/health"),
  ]);
  if (health.mock_mode) document.getElementById("badgeOffline").classList.remove("hidden");

  const queries = await api("/api/queries");
  if (queries.length) {
    renderQueries(queries);
  }

  if (!overview.total_runs) return;

  document.getElementById("panelDashboard").classList.remove("hidden");
  document.getElementById("panelDetail").classList.add("hidden");
  document.getElementById("panelQueries").classList.remove("hidden");
  document.getElementById("btnReport").disabled = false;
  renderMetrics(overview);
  renderIntentChart(intents);
  renderCompetitors(competitors);
  renderOpportunities(opportunities);
  renderRuns(runs);
  setStep(3);
}
window.loadDashboard = loadDashboard;

async function openDetail(runId) {
  const d = await api("/api/analysis/runs/" + runId);
  document.getElementById("panelDashboard").classList.add("hidden");
  document.getElementById("panelQueries").classList.add("hidden");
  document.getElementById("panelDetail").classList.remove("hidden");
  setStep(4);
  const v = d.visibility;
  document.getElementById("detailBody").innerHTML = `
    <div class="bg-white border rounded-xl p-6">
      <p class="text-xs text-violet-600 font-medium mb-1">CUSTOMER QUESTION</p>
      <h1 class="text-lg font-bold">${d.query_text}</h1>
      <p class="text-sm text-slate-500 mt-1">${d.provider} · ${d.model}</p>
    </div>
    <div class="grid md:grid-cols-4 gap-4">
      ${[
        ["Mentioned?", v.boutiqaat_mentioned ? "Yes" : "No"],
        ["Recommended?", v.boutiqaat_recommended ? "Yes" : "No"],
        ["Position", v.boutiqaat_position ?? "N/A"],
        ["Visibility Score", v.visibility_score],
      ]
        .map(
          ([l, val]) =>
            `<div class="bg-white border rounded-xl p-4"><p class="text-xs text-slate-500">${l}</p><p class="text-xl font-semibold text-violet-700">${val}</p></div>`
        )
        .join("")}
    </div>
    <div class="bg-white border rounded-xl p-6">
      <h2 class="font-semibold">AI Answer</h2>
      <pre class="mt-3 text-sm bg-slate-50 p-4 rounded-lg whitespace-pre-wrap">${d.raw_answer}</pre>
      <p class="mt-2 text-xs text-slate-400">${v.explanation || ""}</p>
    </div>
    <div class="grid md:grid-cols-2 gap-4">
      <div class="bg-white border rounded-xl p-6">
        <h2 class="font-semibold">Competitors in this answer</h2>
        ${
          d.competitors.map((c) => `<p class="text-sm py-1 border-b">${c.position ?? "—"}. ${c.name}</p>`).join("") ||
          '<p class="text-slate-400 text-sm mt-2">None</p>'
        }
      </div>
      <div class="bg-white border rounded-xl p-6">
        <h2 class="font-semibold">Sources</h2>
        ${
          d.sources
            .map(
              (s) =>
                `<p class="text-sm py-1"><a class="text-violet-600" href="${s.url}" target="_blank">${s.title || s.domain}</a> ${
                  s.supports_boutiqaat ? '<span class="text-xs bg-violet-50 text-violet-600 px-1 rounded">Boutiqaat</span>' : ""
                }</p>`
            )
            .join("") || '<p class="text-slate-400 text-sm mt-2">None</p>'
        }
      </div>
    </div>
    <div class="bg-white border rounded-xl p-6">
      <h2 class="font-semibold">Opportunities for this query</h2>
      ${
        d.opportunities
          .map(
            (o) =>
              `<div class="border rounded p-4 mt-2"><strong>${o.title}</strong> <span class="text-xs ${sev(
                o.severity
              )} px-2 py-0.5 rounded-full">${o.severity}</span><p class="text-sm mt-1">${o.explanation}</p><p class="text-sm text-violet-600 mt-1">${
                o.recommendation
              }</p></div>`
          )
          .join("") || '<p class="text-slate-400 text-sm mt-2">None</p>'
      }
    </div>`;
}
window.openDetail = openDetail;

document.getElementById("btnLoad").onclick = async () => {
  const btn = document.getElementById("btnLoad");
  btn.disabled = true;
  btn.textContent = "Loading queries…";
  try {
    await loadQueriesOnly();
    btn.textContent = "Step 1 · Queries Loaded ✓";
  } catch (e) {
    showError(e.message);
    btn.textContent = "Step 1 · Load Customer Queries";
    btn.disabled = false;
  }
};

document.getElementById("btnRun").onclick = async () => {
  const btn = document.getElementById("btnRun");
  btn.disabled = true;
  btn.textContent = "Running analysis…";
  setStep(2);
  try {
    await api("/api/analysis/run-full", { method: "POST" });
    await loadDashboard();
    btn.textContent = "Step 2 · Analysis Complete ✓";
  } catch (e) {
    showError(e.message);
    btn.textContent = "Step 2 · Run AI Analysis";
    btn.disabled = false;
  }
};

document.getElementById("btnReport").onclick = async () => {
  setStep(5);
  await api("/api/reports/sample");
  window.open("/api/reports/sample/html", "_blank");
};

document.getElementById("btnBack").onclick = () => {
  document.getElementById("panelDetail").classList.add("hidden");
  document.getElementById("panelQueries").classList.remove("hidden");
  document.getElementById("panelDashboard").classList.remove("hidden");
  setStep(3);
};

api("/api/health")
  .then((h) => {
    if (h.mock_mode) document.getElementById("badgeOffline").classList.remove("hidden");
  })
  .catch(() => {});
api("/api/queries")
  .then((q) => {
    if (q.length) renderQueries(q);
  })
  .catch(() => {});
loadDashboard().catch(() => {});
