const form = document.getElementById("autopsy");
const repoInput = document.getElementById("repo");
const loading = document.getElementById("loading");
const errBox = document.getElementById("error");
const cert = document.getElementById("certificate");
const examplesEl = document.getElementById("examples");
const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

async function loadExamples() {
  try {
    const r = await fetch("/examples");
    const ex = await r.json();
    examplesEl.innerHTML = "try: " + ex.map(e =>
      `<button data-repo="${e.repo}" class="underline hover:text-amber-400">${e.repo}</button>`).join(" · ");
    examplesEl.querySelectorAll("button").forEach(b =>
      b.addEventListener("click", () => { repoInput.value = b.dataset.repo; form.requestSubmit(); }));
  } catch (_) {}
}

function pct(x) { return Math.round((x || 0) * 100); }

function render(d) {
  const f = d.features || {};
  const engineLabel = d.verdict.engine === "tabpfn"
    ? "classified by TabPFN" : "forensic-rules estimate — model unavailable";
  cert.innerHTML = `
    <div class="cert-head"><span class="sigil">☠</span><h2>Certificate of Death</h2>
      <span class="cert-id">No. ${d.certificate_id}</span></div>
    <dl class="cert-body">
      <dt>Deceased</dt><dd>${d.owner}/${d.repo}</dd>
      <dt>Cause of death</dt><dd class="verdict verdict--${d.verdict.mode}">${d.verdict.mode}</dd>
      <dt>Certainty</dt><dd>${pct(d.verdict.confidence)}%</dd>
      <dt>Born</dt><dd>${d.meta.created_at || "—"}</dd>
      <dt>Last seen</dt><dd>${d.meta.last_commit_at || "—"}</dd>
    </dl>
    <table class="evidence"><caption>Forensic evidence</caption>
      <tr><th>Days since last commit</th><td>${f.days_since_last_commit}</td></tr>
      <tr><th>Commit-cadence decay</th><td>${f.commit_cadence_decay}</td></tr>
      <tr><th>Lifespan (days)</th><td>${f.lifespan_days}</td></tr>
      <tr><th>Contributors</th><td>${f.contributor_count}</td></tr>
      <tr><th>Bus factor</th><td>${f.bus_factor}</td></tr>
      <tr><th>Velocity ratio</th><td>${f.velocity_ratio}</td></tr>
    </table>
    <blockquote class="coroner" id="coroner"></blockquote>
    <footer class="cert-foot"><span class="engine engine--${d.verdict.engine}">${engineLabel}</span></footer>`;
  cert.hidden = false;
  typeOut(document.getElementById("coroner"), d.narration);
}

function typeOut(el, text) {
  if (reduced) { el.textContent = text; return; }
  el.textContent = "";
  let i = 0;
  const step = () => { el.textContent = text.slice(0, i); i += 2; if (i <= text.length) setTimeout(step, 12); };
  step();
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  errBox.hidden = true; cert.hidden = true; loading.hidden = false;
  try {
    const r = await fetch("/autopsy", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ repo_url: repoInput.value }) });
    const d = await r.json();
    loading.hidden = true;
    if (!r.ok) { errBox.textContent = d.detail || "Something went wrong."; errBox.hidden = false; return; }
    render(d);
  } catch (_) {
    loading.hidden = true; errBox.textContent = "Network error — try again."; errBox.hidden = false;
  }
});

loadExamples();
