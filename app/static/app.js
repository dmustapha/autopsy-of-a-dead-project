const REDUCED = matchMedia("(prefers-reduced-motion:reduce)").matches;

const form = document.getElementById("autopsy");
const repoInput = document.getElementById("repo");
const loadingEl = document.getElementById("loading");
const errEl = document.getElementById("error");
const cert = document.getElementById("cert");
const examplesEl = document.getElementById("examples");
const submitBtn = form.querySelector("button");

/* ---------- color carries truth: each death mode its own restrained signal ---------- */
const MODE_COLOR = {abandoned:"#c9623f", burned_out:"#d98324", pivoted:"#6fa8c9",
  completed:"#6f9f7a", alive:"#8FB339", insufficient_history:"#9a948a"};
const DRIVERS = {abandoned:["days_since_last_commit","commit_cadence_decay"],
  burned_out:["commit_cadence_decay","bus_factor"],
  pivoted:["velocity_ratio","days_since_last_commit"],
  completed:["commit_cadence_decay","velocity_ratio"],
  alive:["days_since_last_commit","velocity_ratio"]};
function traceColor(mode){ return MODE_COLOR[mode] || "#D4A017"; }

const ENGLABEL = {tabpfn:"classified by TabPFN", "tabpfn+llm":"tabpfn + llm · adjudicated",
  rules:"forensic-rules estimate · model offline", "rules+llm":"rules + llm · adjudicated"};
const ENGCLASS = {tabpfn:"eng-tabpfn", "tabpfn+llm":"eng-tabpfnllm",
  rules:"eng-rules", "rules+llm":"eng-rulesllm"};
const FEAT = [["days_since_last_commit","Days since last commit",""],
  ["commit_cadence_decay","Commit-cadence slope",""],
  ["lifespan_days","Lifespan","days"],
  ["contributor_count","Contributors",""],
  ["bus_factor","Bus factor",""],
  ["velocity_ratio","Velocity ratio (recent / lifetime)",""]];

let LAST = null; // last rendered result, for resize redraws

/* ---------- THE SIGNATURE: the flatline (vital-signs trace) ---------- */
function beats(mode){
  const pts=[]; const push=(x,y)=>pts.push({x,y});
  const qrs=(cx,amp,w)=>{ push(cx-w*1.1,0); push(cx-w*.5,-.08*amp); push(cx-w*.22,.12*amp);
    push(cx,-amp); push(cx+w*.18,.5*amp); push(cx+w*.5,-.04*amp); push(cx+w*1.1,0); };
  let tod=.72, live=false;
  if(mode==="alive"){ tod=1.0; live=true;
    for(let i=0;i<14;i++){ const x=.03+i*.07; qrs(x,.8+.12*Math.sin(i),.022); }
  } else if(mode==="abandoned"){ tod=.62;
    for(let i=0;i<9;i++){ const x=.03+i*.066; const a=.92-i*.085; qrs(x,Math.max(.12,a),.02); } push(tod,0);
  } else if(mode==="burned_out"){ tod=.58;
    for(let i=0;i<8;i++){ const x=.03+i*.07; const a=.7+.3*Math.sin(i*2.1); qrs(x,a,.018); }
    qrs(.57,1.0,.02); push(tod,0);
  } else if(mode==="pivoted"){ tod=.52;
    for(let i=0;i<6;i++){ const x=.03+i*.07; qrs(x,.85-i*.05,.02); }
    push(.5,0); push(.62,0);
    for(let i=0;i<4;i++){ const x=.66+i*.06; qrs(x,.32,.016); } push(1,0); live=true;
  } else if(mode==="completed"){ tod=.6;
    for(let i=0;i<7;i++){ const x=.03+i*.07; qrs(x,.78,.02); } qrs(.57,.95,.024); push(tod,0);
  } else { tod=.3; for(let i=0;i<2;i++) qrs(.05+i*.08,.5,.02); push(tod,0); }
  if(!live) push(1,0);
  return {pts, todX:tod, live};
}

function strokeTrace(ctx, pts, X, Y, cut, color, width, glow){
  ctx.save();
  if(glow){ctx.shadowColor=color; ctx.shadowBlur=glow;}
  ctx.strokeStyle=color; ctx.lineWidth=width; ctx.lineJoin="round"; ctx.lineCap="round"; ctx.beginPath();
  let started=false;
  for(let i=0;i<pts.length;i++){
    const px=X(pts[i].x), py=Y(pts[i].y);
    if(px<=cut){ started?ctx.lineTo(px,py):ctx.moveTo(px,py); started=true; }
    else { if(started && i>0){ const a=pts[i-1],b=pts[i]; const ax=X(a.x),ay=Y(a.y),bx=X(b.x),by=Y(b.y);
        const t=(cut-ax)/Math.max(.0001,(bx-ax)); ctx.lineTo(ax+(bx-ax)*t, ay+(by-ay)*t);} break; }
  }
  ctx.stroke(); ctx.restore();
}

function setupCanvas(canvas, h){
  const dpr=Math.min(2,devicePixelRatio||1);
  const cssW=canvas.clientWidth||canvas.parentElement.clientWidth, cssH=canvas.clientHeight||h;
  canvas.width=cssW*dpr; canvas.height=cssH*dpr; const ctx=canvas.getContext("2d");
  ctx.setTransform(dpr,0,0,dpr,0,0); return {ctx,cssW,cssH};
}

function drawTrace(canvas, mode, opts={}){
  const {ctx,cssW,cssH}=setupCanvas(canvas,70);
  const padX=12, midY=cssH*0.56, amp=cssH*0.34, W=cssW-padX*2;
  const {pts,todX,live}=beats(mode); const color=opts.color||traceColor(mode);
  const X=x=>padX+x*W, Y=y=>midY-y*amp;
  function render(p){
    ctx.clearRect(0,0,cssW,cssH);
    ctx.strokeStyle="rgba(236,229,214,.08)"; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(padX,midY); ctx.lineTo(cssW-padX,midY); ctx.stroke();
    if(!live || mode==="pivoted"){ const tx=X(todX);
      ctx.save(); ctx.setLineDash([2,3]); ctx.strokeStyle="rgba(212,160,23,.55)"; ctx.lineWidth=1;
      ctx.beginPath(); ctx.moveTo(tx,6); ctx.lineTo(tx,cssH-6); ctx.stroke(); ctx.restore(); }
    strokeTrace(ctx, pts, X, Y, padX+p*W, color, 1.9, 10);
    if(p<1 && !REDUCED){ ctx.fillStyle=color; ctx.shadowColor=color; ctx.shadowBlur=12;
      ctx.beginPath(); ctx.arc(Math.min(padX+p*W,cssW-padX), midY, 2.6,0,7); ctx.fill(); }
    if(p>=1){ ctx.fillStyle=color; ctx.shadowColor=color; ctx.shadowBlur= live?12:6;
      ctx.beginPath(); ctx.arc(cssW-padX, midY, live?2.6:2,0,7); ctx.fill(); }
  }
  if(REDUCED||opts.static){ render(1); if(opts.onDone)opts.onDone(); return; }
  const dur=opts.dur||1600; let t0=null;
  function frame(ts){ if(t0===null)t0=ts; const p=Math.min(1,(ts-t0)/dur); render(p);
    if(p<1) requestAnimationFrame(frame); else if(opts.onDone)opts.onDone(); }
  requestAnimationFrame(frame);
}

/* ---------- field: drifting dust in the lamplight ---------- */
let dustRAF=null;
function startDust(){
  const c=document.getElementById("dust"); if(!c) return;
  const dpr=Math.min(2,devicePixelRatio||1);
  function size(){ c.width=innerWidth*dpr; c.height=innerHeight*dpr; }
  size(); const ctx=c.getContext("2d"); ctx.setTransform(dpr,0,0,dpr,0,0);
  const N=Math.min(46, Math.round(innerWidth/30));
  const mote=()=>({x:Math.random()*innerWidth, y:Math.random()*innerHeight*0.9,
    r:Math.random()*1.3+0.4, vx:(Math.random()-0.5)*0.08, vy:-(Math.random()*0.12+0.03),
    a:Math.random()*0.35+0.08, tw:Math.random()*6.28});
  let motes=Array.from({length:N},mote);
  if(REDUCED){
    ctx.clearRect(0,0,innerWidth,innerHeight);
    for(const m of motes){ ctx.fillStyle=`rgba(212,180,110,${m.a})`;
      ctx.beginPath(); ctx.arc(m.x,m.y,m.r,0,7); ctx.fill(); } return; }
  function frame(){
    ctx.clearRect(0,0,innerWidth,innerHeight);
    for(const m of motes){ m.x+=m.vx; m.y+=m.vy; m.tw+=0.01;
      if(m.y<-4){ Object.assign(m,mote(),{y:innerHeight+4}); }
      const tw=0.6+0.4*Math.sin(m.tw);
      const g=ctx.createRadialGradient(m.x,m.y,0,m.x,m.y,m.r*3);
      g.addColorStop(0,`rgba(224,196,130,${m.a*tw})`); g.addColorStop(1,"rgba(224,196,130,0)");
      ctx.fillStyle=g; ctx.beginPath(); ctx.arc(m.x,m.y,m.r*3,0,7); ctx.fill(); }
    dustRAF=requestAnimationFrame(frame);
  }
  cancelAnimationFrame(dustRAF); frame();
  addEventListener("resize",()=>{size();ctx.setTransform(dpr,0,0,dpr,0,0);},{passive:true});
}

/* faint guilloche rosette behind the document — security-print texture, NOT the motif */
function drawWatermark(canvas){
  const {ctx,cssW,cssH}=setupCanvas(canvas,canvas.parentElement.clientHeight||600);
  ctx.clearRect(0,0,cssW,cssH);
  const cx=cssW*0.78, cy=cssH*0.26, R=Math.min(cssW,cssH)*0.36;
  ctx.strokeStyle="rgba(212,160,23,0.028)"; ctx.lineWidth=1;
  for(let i=0;i<80;i++){ const a=i/80*Math.PI;
    ctx.save(); ctx.translate(cx,cy); ctx.rotate(a);
    ctx.beginPath(); ctx.ellipse(0,0,R,R*0.3,0,0,6.2832); ctx.stroke(); ctx.restore(); }
  const cx2=cssW*0.18, cy2=cssH*0.85, R2=Math.min(cssW,cssH)*0.22;
  ctx.strokeStyle="rgba(212,160,23,0.02)";
  for(let i=0;i<52;i++){ const a=i/52*Math.PI;
    ctx.save(); ctx.translate(cx2,cy2); ctx.rotate(a);
    ctx.beginPath(); ctx.ellipse(0,0,R2,R2*0.3,0,0,6.2832); ctx.stroke(); ctx.restore(); }
}

function sealSVG(mode){
  const c=(mode==="alive"||mode==="pivoted")?"#8FB339":"#D4A017";
  return `<svg width="60" height="60" viewBox="0 0 60 60">
    <circle cx="30" cy="30" r="28" fill="none" stroke="${c}" stroke-opacity=".5" stroke-width="1"/>
    <circle cx="30" cy="30" r="23" fill="none" stroke="${c}" stroke-opacity=".22" stroke-width="1" stroke-dasharray="2 3"/>
    <path d="M14 31 h7 l2 -7 l3 13 l3 -9 l2 3 h12" fill="none" stroke="${c}" stroke-width="1.6"
      stroke-linejoin="round" stroke-linecap="round"/>
    <text x="30" y="52" text-anchor="middle" fill="${c}" fill-opacity=".6"
      font-family="IBM Plex Mono,monospace" font-size="5" letter-spacing="1">SEALED</text></svg>`;
}

/* ---------- render the certificate from a real /autopsy result ---------- */
function pct(x){ return Math.round((x||0)*100); }
function esc(s){ return String(s).replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c])); }
function todayStr(){ const t=new Date();
  return `${t.getFullYear()}-${String(t.getMonth()+1).padStart(2,"0")}-${String(t.getDate()).padStart(2,"0")}`; }

function render(d){
  LAST = d;
  const v = d.verdict || {};
  const mode = v.mode || "insufficient_history";
  const conf = typeof v.confidence === "number" ? v.confidence : 0;
  const engine = ENGLABEL[v.engine] ? v.engine : "rules";
  const probs = v.probs || {};
  const f = d.features || null;
  const born = (d.meta && d.meta.created_at) || null;
  const last = (d.meta && d.meta.last_commit_at) || null;
  const isTemplated = /without the language model/i.test(d.narration || "");

  const modeTitle = mode==="alive" ? "CERTIFICATE OF LIFE"
    : mode==="insufficient_history" ? "PRELIMINARY FINDING" : "CERTIFICATE OF DEATH";
  const subjectLabel = (mode==="alive" || mode==="insufficient_history") ? "Subject" : "Deceased";

  // differential — a real posterior (TabPFN) becomes a diagnosis list; rules yields one cause, said honestly
  const pe = Object.entries(probs).filter(([,x]) => x > 0).sort((a,b) => b[1]-a[1]);
  let diffHTML;
  if(pe.length >= 2){
    diffHTML = `<div class="ddx">` + pe.filter(([,x]) => x >= 0.01).map(([k,x],i) => {
      const c = MODE_COLOR[k] || "#D4A017";
      return `<div class="drow ${i===0?'lead':''}">
         <span class="dmark"${i===0?` style="background:${c};box-shadow:0 0 7px ${c}"`:''}></span>
         <span class="dname">${esc(k.replace(/_/g," "))}</span><span class="dleader"></span>
         <span class="dpct"${i===0?` style="color:${c}"`:''}>${pct(x)}%</span></div>`;
    }).join("") + `</div>`;
  } else {
    diffHTML = `<div class="ddx-note">A single determination. The forensic-rules estimate yields one
      cause, not a probability distribution over causes; a live TabPFN run returns the full differential.</div>`;
  }

  const drivers = DRIVERS[mode] || [];
  const fmt = (k,val) => { if(val == null) return "—";
    if(k==="commit_cadence_decay" || k==="velocity_ratio") return Number(val).toFixed(2);
    return "" + Math.round(Number(val)); };
  const rows = f ? FEAT.map(([k,label,u]) => {
      const drv = drivers.includes(k) ? ' class="driver"' : '';
      return `<tr${drv}><th>${label}</th><td>${fmt(k,f[k])}${u?`<span class="u">${u}</span>`:""}</td></tr>`;
    }).join("") : `<tr><th>Evidence</th><td>unavailable</td></tr>`;
  const bornLast = (born || last) ? `${born || "—"} → ${last || "—"}` : "unknown";

  const engClass = ENGCLASS[engine] || "eng-rules";
  const narLabel = isTemplated ? "templated coroner · LLM offline" : ("narrated by " + (d.narration_engine || "Gemma") + " (open weights)");
  const narClass = isTemplated ? "nar-fallback" : "nar-live";
  const certNo = d.certificate_id ? esc(d.certificate_id).toUpperCase() : "—";

  // the deceased's OWN last words — a recovered quote, distinct from the coroner's eulogy.
  // Only a deceased subject has "last words": never frame a living project's text this way.
  const isDeceased = mode !== "alive" && mode !== "insufficient_history";
  const lastWordsHTML = (d.death_note && isDeceased) ? `
     <div class="last-words">
       <div class="lw-kicker">Last words &middot; recovered from the record</div>
       <p class="lw-quote">&ldquo;${esc(d.death_note)}&rdquo;</p>
     </div>` : "";

  // project summary — "What this project was" (only when project_summary present; null-safe for old-shape results)
  const summaryHTML = d.project_summary ? `
     <div class="project-summary">
       <div class="ps-kicker">What this project was</div>
       <p class="ps-text">${esc(d.project_summary)}</p>
     </div>` : "";

  // content-read badge — shown only when the adjudicator actually ran (not templated/offline)
  // d.narration_engine may already contain "· 0G Compute"; extract model name only to avoid doubling the suffix
  const readModel = (d.narration_engine || "LLM").split("·")[0].trim();
  const contentBadgeHTML = (!isTemplated && d.llm_hint && !d.llm_hint.llm_offline) ? `
     <span class="badge nar-live"><span class="d"></span>evidence read by ${esc(readModel)} &middot; 0G Compute</span>` : "";

  // cohort — forensic context: how this fate compares to its nearest neighbours (mode-aware verb, null-safe)
  let cohortHTML = "";
  if(d.cohort && d.cohort.cohort_size){
    const co = d.cohort;
    const verb = mode==="alive" ? "Resembles" : mode==="insufficient_history" ? "Grouped with" : "Died like";
    const self = `${d.owner}/${d.repo}`.toLowerCase();
    const others = (co.neighbors||[]).filter(n => String(n).toLowerCase() !== self);
    const tip = others.length ? ` title="nearest neighbours · ${esc(others.join(" · "))}"` : "";
    cohortHTML = `<div class="cohort-line"${tip}>${verb} <b>${co.matching}</b> of <b>${co.cohort_size}</b> similar repos${others.length?`<span class="co-hint"> — hover to see the cohort</span>`:""}</div>`;
  }

  cert.innerHTML = `
   <div class="cert-watermark"><canvas id="certWm"></canvas></div>
   <div class="cert-strip"><canvas id="certHeart"></canvas>
     <span class="tod" id="todLabel"></span></div>
   <div class="cert-pad">
     <div class="cert-top">
       <div class="seal" id="seal">${sealSVG(mode)}</div>
       <div class="cert-title"><div class="kicker">Office of the Repository Coroner</div>
         <h2>${modeTitle}</h2></div>
       <div class="cert-no">No. ${certNo}<br>filed ${todayStr()}</div>
     </div>

     <div class="determination"><div class="det-row">
       <div class="det-main">
         <div class="label">${subjectLabel}</div>
         <div class="deceased">${esc(d.owner)}/${esc(d.repo)}</div>
         <div class="cause m-${mode} reveal" id="causeWord">${esc(mode.replace(/_/g," "))}</div>
       </div>
       <div class="certainty"><div class="num">${pct(conf)}<span class="pctsign">%</span></div>
         <div class="cap">certainty</div></div>
     </div></div>

     <div class="differential"><div class="ptitle">Differential &middot; the other deaths considered</div>
       ${diffHTML}</div>
     ${cohortHTML}

     <table class="evidence"><caption>Forensic evidence</caption>${rows}
       <tr><th>Born / last seen</th><td>${esc(bornLast)}</td></tr></table>

     ${lastWordsHTML}

     ${summaryHTML}

     <blockquote class="coroner" id="coroner"></blockquote>

     <div class="cert-foot">
       <span class="badge ${engClass}"><span class="d"></span>${ENGLABEL[engine]}</span>
       <span class="badge ${narClass}"><span class="d"></span>${narLabel}</span>
       ${contentBadgeHTML}
       <span class="spacer"></span>
       <span class="cid">specimen ${certNo}</span>
     </div>
   </div>`;
  cert.hidden = false;

  // time-of-death label on the strip
  const b = beats(mode);
  const lbl = document.getElementById("todLabel");
  const stripW = cert.querySelector(".cert-strip").clientWidth; const padX=12, W=stripW-padX*2;
  if(mode==="alive"){ lbl.textContent = "still beating · " + (last || "recently");
    lbl.style.left="auto"; lbl.style.right="14px"; lbl.style.transform="none"; }
  else { lbl.textContent = "time of death · " + (last || "unknown");
    lbl.style.left = (padX + b.todX*W) + "px"; }

  // layers + choreography
  const seal = document.getElementById("seal");
  const causeW = document.getElementById("causeWord");
  drawWatermark(document.getElementById("certWm"));
  drawTrace(document.getElementById("certHeart"), mode, {static:REDUCED,
    onDone:()=>{ seal.classList.add(REDUCED?"shown":"stamped"); causeW.classList.add("shown"); }});
  if(REDUCED){ seal.classList.add("shown"); causeW.classList.add("shown");
    document.getElementById("coroner").textContent = d.narration || ""; }
  else typeOut(document.getElementById("coroner"), d.narration || "", 420);
}

function typeOut(el,text,delay){
  if(REDUCED){ el.textContent=text; return; }
  el.textContent=""; let i=0;
  const step=()=>{ el.textContent=text.slice(0,i); i+=2; if(i<=text.length) setTimeout(step,10); };
  setTimeout(step, delay||0);
}

/* ---------- wiring: the live autopsy ---------- */
async function runAutopsy(repo){
  errEl.hidden = true; cert.hidden = true; loadingEl.hidden = false;
  submitBtn.disabled = true;
  try{
    const r = await fetch("/autopsy", { method:"POST",
      headers:{ "Content-Type":"application/json" },
      body: JSON.stringify({ repo_url: repo }) });
    const d = await r.json();
    loadingEl.hidden = true; submitBtn.disabled = false;
    if(!r.ok){ errEl.textContent = d.detail || "The exhumation failed."; errEl.hidden = false; return; }
    render(d);
    cert.scrollIntoView({ behavior: REDUCED?"auto":"smooth", block:"start" });
  }catch(_){
    loadingEl.hidden = true; submitBtn.disabled = false;
    errEl.textContent = "Network error — the crypt is unreachable. Try again."; errEl.hidden = false;
  }
}

form.addEventListener("submit", e => { e.preventDefault();
  const repo = repoInput.value.trim(); if(repo) runAutopsy(repo); });

async function loadExamples(){
  try{
    const r = await fetch("/examples"); const ex = await r.json();
    examplesEl.innerHTML = "try: " + ex.map(e =>
      `<button type="button" data-repo="${esc(e.repo)}">${esc(e.repo)}</button>`).join(" · ");
    examplesEl.querySelectorAll("button").forEach(b =>
      b.addEventListener("click", () => { repoInput.value = b.dataset.repo; runAutopsy(b.dataset.repo); }));
  }catch(_){}
}

function heroBeat(){ drawTrace(document.getElementById("heroHeart"), "abandoned", {dur:2100, color:"#D4A017"}); }

addEventListener("load", () => { startDust(); heroBeat(); loadExamples(); });
addEventListener("resize", () => { heroBeat();
  if(!cert.hidden && LAST){ const mode = (LAST.verdict && LAST.verdict.mode) || "abandoned";
    const w = document.getElementById("certWm"); if(w) drawWatermark(w);
    const c = document.getElementById("certHeart"); if(c) drawTrace(c, mode, {static:true}); } });
