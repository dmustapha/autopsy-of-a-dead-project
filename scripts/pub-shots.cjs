// Capture live certificate screenshots from the PUBLIC deployed URL (for the post + evidence).
// Uses the cached examples (bower=death, fastapi=life). Run: node scripts/pub-shots.cjs
const { chromium } = require('/opt/homebrew/lib/node_modules/playwright');
const fs = require('fs');
const BASE = process.env.AUTOPSY_URL || 'https://autopsy.132-145-100-81.sslip.io/';
const OUT = '/Users/MAC/dev-ghost/evidence/deploy';
fs.mkdirSync(OUT, { recursive: true });

async function shot(page, repo, name) {
  await page.goto(BASE, { waitUntil: 'networkidle', timeout: 30000 });
  await page.waitForTimeout(1000);
  await page.fill('#repo', repo);
  await page.click('button.cta');
  await page.waitForSelector('#cert:not([hidden])', { timeout: 60000 });
  await page.waitForTimeout(3000); // flatline flatten + seal stamp
  const info = await page.evaluate(() => {
    const cert = document.querySelector('#cert');
    const badges = [...document.querySelectorAll('.pill,.badge,[class*="badge"]')].map(b=>b.innerText.trim()).filter(Boolean);
    return { certLen: cert ? cert.innerText.length : 0, badges };
  });
  // full-page (hero + certificate) + a tight certificate crop
  await page.screenshot({ path: `${OUT}/live-${name}-full.png`, fullPage: true });
  const cert = await page.$('#cert');
  if (cert) await cert.screenshot({ path: `${OUT}/live-${name}-cert.png` });
  return info;
}

(async () => {
  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 900 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const out = {};
  // landing hero
  await page.goto(BASE, { waitUntil:'networkidle', timeout:30000 });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: `${OUT}/live-hero.png` });
  for (const [repo, name] of [['bower/bower','bower-death'], ['fastapi/fastapi','fastapi-life']]) {
    try { out[name] = await shot(page, repo, name); }
    catch (e) { out[name] = { error: e.message }; }
  }
  await browser.close();
  fs.writeFileSync(`${OUT}/shots.json`, JSON.stringify(out, null, 2));
  console.log(JSON.stringify(out, null, 2));
  console.log('saved to', OUT);
})().catch(e => { console.error('FATAL', e.message); process.exit(1); });
