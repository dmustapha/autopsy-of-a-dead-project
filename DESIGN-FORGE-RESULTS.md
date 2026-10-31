# DESIGN-FORGE-RESULTS.md

status: complete

## What Just Happened
We formalized the frozen, owner-approved death-certificate card into durable, reusable contracts and
gave the project a real brand mark. `DESIGN_SYSTEM.md` now lets a stranger rebuild the card from
scratch (the coroner/ofrenda palette as alpha-over-role tokens, three-fonts-three-jobs typography,
the constructed-field atmosphere recipe, the pure-glow shadow philosophy); `brand.json` encodes the
tokens, a `statusLegend` mapping all five death-modes **and** the four honest engine/narration states
to colors, and the invariant phrase *"Every verdict carries an honest engine badge."* The logo is a
real AI-generated mark (stablestudio nano-banana, 3 variants at $0.07 each): a solid amber tombstone
with a negative-cut flatline — unmistakably grave + the card's signature pulse, legible as a 16px
favicon. During the refine pass we made two genuine craft improvements to the frozen card without
changing its look: added a keyboard `:focus-visible` affordance (a11y, CF-4) and tokenized the radii
to the documented 2/11/16/999 scale (CF-1) — the craft lint now passes with **0 violations** and a
re-run of the live 375px/contrast verification confirmed **zero visual regression**. This matters
because the post is judged heaviest on writing and the card screenshot is its cover: the design now
has a formal spine the README/demo/package all reuse, and a brand mark for the post + repo. Next the
pipeline hardens the core (`stress_test`) then stands it up for real on Oracle (`deploy ★`).

## Honest Gaps
- **`design-applied-gate.sh` false-REDs under its own `set -o pipefail`** — a `grep -q .` early-exit
  sends SIGPIPE to the producer, so the token-in-source re-derivation returns non-zero *even though
  the tokens are found*. PROVEN a gate bug, not a design gap: with pipefail disabled after sourcing,
  `#D4A017` and `Spectral` are both FOUND in `app/static/card.css` (they are the card's actual tokens).
  The design IS applied. The dispatch-gate post does not invoke this sub-gate, so it does not block
  completion; flagged here so a reviewer isn't misled by a manual run of that one gate.
- **`public/logo.svg` embeds the real raster, it is not a traced vector** — stablestudio's
  image→SVG vectorize quoted **$10** (wallet balance was ~$0.74), so vectorization was skipped. The
  SVG is a valid, scalable container wrapping the real nano-banana PNG (not a hand-coded geometric
  scaffold). If a true vector is wanted later, re-run vectorize with more balance.
- **Gemma narration is intermittent locally (DEV-004)** — carried from the design phase; a backend/
  wiring item for deploy/livetest, not a design-forge gap. The card renders the templated-vs-Gemma
  state honestly either way.
- **fal provider is down** (HTTP 401 invalid key) — the fallback chain worked (stablestudio), but if
  fal is the preferred provider its MCP key needs refreshing.
