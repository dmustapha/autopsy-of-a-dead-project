/* card.design.test.cjs — design-system invariants for the frozen death-certificate card.
   Asserts DESIGN_SYSTEM.md / brand.json stay in sync with app/static/card.css and that the
   load-bearing honesty + craft rules hold. Run: node design-tests/card.design.test.cjs */
const fs = require('fs');
const css = fs.readFileSync(__dirname + '/../app/static/card.css', 'utf8');
const brand = JSON.parse(fs.readFileSync(__dirname + '/../brand.json', 'utf8'));
let fails = 0;
const ok = (cond, msg) => { if (!cond) { console.error('FAIL:', msg); fails++; } else console.log('ok:', msg); };

// 1. Accent token present + one-hue discipline
ok(css.includes('--amber:#D4A017'), 'amber accent token #D4A017 in card.css');
ok(brand.brandColor === '#D4A017' && brand.accent === '#D4A017', 'brand.json single accent = amber');

// 2. Warm near-black ground, never flat #000
ok(css.includes('--ground:#0c0b09'), 'ground is warm near-black #0c0b09');
ok(!/background:\s*#000(\b|;|})/.test(css), 'no flat #000 panel fill');

// 3. Three fonts, three jobs
ok(css.includes('"IBM Plex Mono"') && css.includes('"Spectral"'), 'mono + serif fonts declared');

// 4. Per-mode color truth (all 5 modes mapped distinctly)
['#c9623f','#d98324','#6fa8c9','#6f9f7a','#8FB339'].forEach(h =>
  ok(css.includes(h), `mode hue ${h} present (color carries truth)`));

// 5. Status legend covers 5 death-modes + 4 engine/narration states
const toks = brand.statusLegend.map(r => r.token);
['alive','abandoned','burned_out','pivoted','completed'].forEach(t =>
  ok(toks.includes(t), `statusLegend has death-mode ${t}`));
['engine=tabpfn','engine=rules','narration=gemma','narration=templated'].forEach(t =>
  ok(toks.includes(t), `statusLegend has engine/narration state ${t}`));

// 6. Invariant phrase present (the thesis)
ok(/honest engine badge/i.test(brand.invariantPhrase), 'invariantPhrase encodes honest-engine-badge thesis');

// 7. Glow-only elevation (no decorative black drop-shadow outside the one certificate document-lift)
const blackShadows = (css.match(/box-shadow:[^;]*rgba\(0,0,0/g) || []);
ok(blackShadows.length <= 1, `at most one soft document-lift black shadow (found ${blackShadows.length})`);

console.log(fails === 0 ? '\nDESIGN TESTS PASS' : `\n${fails} DESIGN TEST FAILURE(S)`);
process.exit(fails === 0 ? 0 : 1);
