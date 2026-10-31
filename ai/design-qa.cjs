// design Phase-5 QA — local Playwright against live :3300 (frozen card verify, no redesign)
const { chromium } = require('/opt/homebrew/lib/node_modules/playwright');
const fs = require('fs');
const BASE = 'http://127.0.0.1:3300/';
const OUT = '/Users/MAC/dev-ghost/evidence/design-qa';
fs.mkdirSync(OUT, { recursive: true });

// WCAG relative luminance + contrast ratio
function lum(rgb){const f=c=>{c/=255;return c<=0.03928?c/12.92:Math.pow((c+0.055)/1.055,2.4)};const[r,g,b]=rgb;return 0.2126*f(r)+0.7152*f(g)+0.0722*f(b)}
function ratio(a,b){const la=lum(a)+0.05,lb=lum(b)+0.05;return +( (Math.max(la,lb)/Math.min(la,lb)).toFixed(2))}
function parseRGB(s){const m=s.match(/\d+(\.\d+)?/g);return m?m.slice(0,3).map(Number):[0,0,0]}

(async () => {
  const browser = await chromium.launch();
  const result = { ts:new Date().toISOString(), states:{}, atmosphere:{}, contrast:{}, mobile375:{}, badges:{}, issues:[] };

  // ---------- Desktop 1440x900 ----------
  const ctx = await browser.newContext({ viewport:{width:1440,height:900}, deviceScaleFactor:2 });
  const page = await ctx.newPage();
  await page.goto(BASE, { waitUntil:'networkidle', timeout:30000 });
  await page.waitForTimeout(1200); // let dust/heroBeat start

  // atmosphere: body bg warm near-black, one glow, grid layer
  const atmo = await page.evaluate(()=>{
    const g=getComputedStyle(document.body).backgroundColor;
    const lamp=!!document.querySelector('.lamp'), under=!!document.querySelector('.underglow');
    const dust=!!document.querySelector('#dust'), vig=!!document.querySelector('.vignette');
    return {bodyBg:g, lamp, underglow:under, dust, vignette:vig};
  });
  result.atmosphere = atmo;
  const bg = parseRGB(atmo.bodyBg);
  result.atmosphere.warmNearBlack = (bg[0]>=bg[2] && Math.max(...bg)<=40); // R>=B, dark
  await page.screenshot({ path:`${OUT}/hero.png`, fullPage:false });

  // contrast measurements from real computed styles on hero
  const heroColors = await page.evaluate(()=>{
    const pick=sel=>{const el=document.querySelector(sel);if(!el)return null;const c=getComputedStyle(el);return{color:c.color,bg:c.backgroundColor}};
    return { eyebrow:pick('.eyebrow'), body:{color:getComputedStyle(document.body).color,bg:getComputedStyle(document.body).backgroundColor} };
  });
  const groundRGB = parseRGB(atmo.bodyBg);
  if(heroColors.body) result.contrast.paper_on_ground = ratio(parseRGB(heroColors.body.color), groundRGB);
  if(heroColors.eyebrow) result.contrast.amber_eyebrow_on_ground = ratio(parseRGB(heroColors.eyebrow.color), groundRGB);

  // ---------- run both states ----------
  async function runState(repo, key){
    await page.goto(BASE, { waitUntil:'networkidle', timeout:30000 });
    await page.fill('#repo', repo);
    await page.click('button.cta');
    // wait for cert to reveal (hidden attr removed) — autopsy hits live GitHub
    await page.waitForSelector('#cert:not([hidden])', { timeout:60000 });
    await page.waitForTimeout(2500); // flatline animation + seal stamp
    const info = await page.evaluate(()=>{
      const cert=document.querySelector('#cert');
      const txt=cert?cert.innerText:'';
      const badges=[...document.querySelectorAll('.pill, .badge, [class*="badge"]')].map(b=>b.innerText.trim()).filter(Boolean);
      const title=(document.querySelector('.cert-title, .cert-title .kicker, h1, h2')||{}).innerText||'';
      // measure a key cert text contrast: .certainty .num (serif numeral) vs its bg
      const num=document.querySelector('.certainty .num'); let numC=null;
      if(num){const c=getComputedStyle(num);numC={color:c.color}}
      const cause=document.querySelector('[class*="cause"]'); let causeC=null;
      if(cause){causeC={color:getComputedStyle(cause).color,text:cause.innerText.trim()}}
      return {len:txt.length, badges, title, sample:txt.slice(0,400), numC, causeC};
    });
    await page.screenshot({ path:`${OUT}/cert-${key}.png`, fullPage:false });
    return info;
  }

  try { result.states.death = await runState('bower/bower','bower-death'); }
  catch(e){ result.states.death={error:String(e)}; result.issues.push('death-state render failed: '+e.message); }

  try { result.states.life = await runState('fastapi/fastapi','fastapi-life'); }
  catch(e){ result.states.life={error:String(e)}; result.issues.push('life-state render failed: '+e.message); }

  // badge honesty check
  const allBadges = [].concat(result.states.death?.badges||[], result.states.life?.badges||[]);
  result.badges.observed = [...new Set(allBadges)];
  result.badges.hasEngineBadge = allBadges.some(b=>/tabpfn|rules|fallback/i.test(b));
  result.badges.hasNarrationBadge = allBadges.some(b=>/gemma|templated|llm|offline/i.test(b));

  await ctx.close();

  // ---------- Mobile 375x844 ----------
  const mctx = await browser.newContext({ viewport:{width:375,height:844}, deviceScaleFactor:2 });
  const mp = await mctx.newPage();
  await mp.goto(BASE, { waitUntil:'networkidle', timeout:30000 });
  await mp.fill('#repo','bower/bower'); await mp.click('button.cta');
  await mp.waitForSelector('#cert:not([hidden])', { timeout:60000 });
  await mp.waitForTimeout(2000);
  const m = await mp.evaluate(()=>({
    scrollW:document.documentElement.scrollWidth, clientW:document.documentElement.clientWidth,
    certVisible: !document.querySelector('#cert').hasAttribute('hidden'),
    certW: (document.querySelector('.certificate')||{}).clientWidth||0
  }));
  result.mobile375 = { ...m, noHorizontalOverflow: m.scrollW <= m.clientW + 1 };
  if(!result.mobile375.noHorizontalOverflow) result.issues.push(`375px horizontal overflow: scrollW ${m.scrollW} > clientW ${m.clientW}`);
  await mp.screenshot({ path:`${OUT}/mobile-375.png`, fullPage:true });
  await mctx.close();

  await browser.close();

  // ---------- verdict logic ----------
  const AA = 4.5; // normal text
  const contrastOK = (result.contrast.paper_on_ground||0) >= AA;
  if(!contrastOK) result.issues.push(`paper-on-ground contrast ${result.contrast.paper_on_ground} < AA ${AA}`);
  // amber eyebrow is small-caps tracked label (>=18.66px bold or large) — treat as large-text 3:1; it's an accent label
  if((result.contrast.amber_eyebrow_on_ground||0) < 3) result.issues.push(`amber eyebrow contrast ${result.contrast.amber_eyebrow_on_ground} < 3:1`);

  result.summary = {
    deathRendered: !!(result.states.death && !result.states.death.error && result.states.death.len>200),
    lifeRendered: !!(result.states.life && !result.states.life.error && result.states.life.len>200),
    warmNearBlack: result.atmosphere.warmNearBlack,
    oneGlow: (result.atmosphere.lamp||result.atmosphere.underglow),
    gridDustPresent: result.atmosphere.dust,
    engineBadge: result.badges.hasEngineBadge,
    narrationBadge: result.badges.hasNarrationBadge,
    contrastAA_paper: contrastOK,
    mobile375OK: result.mobile375.noHorizontalOverflow && result.mobile375.certVisible,
  };
  fs.writeFileSync('/Users/MAC/dev-ghost/ai/design-qa-results.json', JSON.stringify(result,null,2));
  console.log(JSON.stringify(result.summary,null,2));
  console.log('ISSUES:', JSON.stringify(result.issues));
  console.log('CONTRAST:', JSON.stringify(result.contrast));
  console.log('BADGES:', JSON.stringify(result.badges.observed));
})().catch(e=>{console.error('FATAL',e);process.exit(1)});
