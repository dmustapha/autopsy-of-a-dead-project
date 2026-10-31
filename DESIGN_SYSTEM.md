# DESIGN_SYSTEM.md — Autopsy of a Dead Project

Formalized from the FROZEN, owner-approved card (`app/static/card.css`, `app/templates/index.html`,
`app/static/app.js`). A stranger can rebuild the card from this doc. Nothing invented — every value
is extracted from `card.css :root` and the built markup.

## Identity
- **World statement:** a coroner's bench in a dark, warm-lit morgue for dead code — a dignified
  autopsy and remembrance (Día de los Muertos: memorial, never mockery) where a repository's death
  is certified honestly, with the evidence shown and nothing faked.
- **Accent color:** autopsy-amber `#D4A017` — candlelight at midnight / aged specimen jar / coroner's
  lamp. Chosen over toe-tag green so color carries truth: amber = the lamp over the dead, green =
  still alive.
- **Signature element:** **the flatline** — a per-mode pulse trace (canvas) that runs, decays,
  flattens, and gets a seal stamp; alive everywhere (logo → favicon → hero → certificate → dead
  states). It performs the verb "classify how it died"; a fresh critic must NOT call it a chart.
- **Invariant phrase (reuse verbatim ≥3 docs):** *"Every verdict carries an honest engine badge."*

## Tokens
Warm near-black ground; ONE accent (amber) at multiple alphas; paper-cream ink; alive=green; per-mode hues.

```css
@theme {
  /* ground + surfaces (elevation = lightness step, warm) */
  --color-ground: #0c0b09;  --color-surface1: #15120e;  --color-surface2: #1b1711;  --color-surface3: #221c14;
  /* accent (one hue, three stops) */
  --color-amber: #D4A017;   --color-amber-hi: #E8B733;  --color-amber-deep: #6b5210;
  /* ink + alive */
  --color-paper: #ece5d6;   --color-ink: #13110d;       --color-green: #8FB339;
  /* per-death-mode hues */
  --color-abandoned: #c9623f; --color-burned_out: #d98324; --color-pivoted: #6fa8c9;
  --color-completed: #6f9f7a; --color-alive: #8FB339;
  /* hairlines (paper at low alpha — never a solid border) */
  --hair: rgba(236,229,214,.09); --hair-2: rgba(236,229,214,.14);
  /* type */
  --font-mono: "IBM Plex Mono", ui-monospace, monospace;   /* evidence data + eyebrows */
  --font-serif: "Spectral", Georgia, serif;                /* eulogy prose + numerals + titles */
  /* radii */
  --radius-sm: 2px; --radius-md: 11px; --radius-lg: 16px; --radius-pill: 999px;
}
```
Fluid hero: `font-size: clamp(33px, 5.2vw, 54px)`. Eyebrow mono 11px / +0.26em / uppercase / amber.

**Do's:** one accent hue (amber) at alphas for every "shade"; borders are always 1px paper at ≤15%;
elevation = surface-lightness step + hairline + ONE amber glow.
**Don'ts:** no flat `#000` panels; no hard black drop-shadows as decoration (glow-only — the single
exception is the certificate's soft document-lift, below); no hex-zoo (≤6 role hues); no neon verdict.

## Status Legend
Color carries truth. Five death-modes + the honest engine/narration badges.

| Color | Token | Meaning |
|---|---|---|
| `#8FB339` green | `alive` | repo still breathing — CERTIFICATE OF LIFE |
| `#c9623f` red-clay | `abandoned` | development stopped, no graceful end |
| `#d98324` amber-burnt | `burned_out` | maintainer fatigue / slowing to a halt |
| `#6fa8c9` blue | `pivoted` | project changed identity / superseded |
| `#6f9f7a` sage | `completed` | finished its job, intentional rest |
| `rgba(236,229,214,.72)` | `insufficient_history` | too little to examine — "no body" |
| `#D4A017` amber | `engine=tabpfn` | verdict from the real TabPFN posterior ("CLASSIFIED BY TABPFN") |
| `rgba(236,229,214,.6)` | `engine=rules` | labeled forensic-rules fallback ("rules (fallback)") |
| `#8FB339` green | `narration=gemma` | real Gemma-via-Ollama eulogy ("NARRATED BY GEMMA") |
| `rgba(236,229,214,.5)` | `narration=templated` | labeled template ("TEMPLATED CORONER · LLM OFFLINE") |

## Craft
- **Radius scale:** 2 / 11 / 16 / 999px — all tokenized, no ad-hoc values.
- **Elevation ladder:** ground `#0c0b09` → surface1 `#15120e` → surface2 `#1b1711` → surface3 `#221c14`
  (warm lightness steps), each lifted by a 1px hairline, never a hue change.
- **Shadow philosophy: pure-glow**, one documented exception. Interactive/live elements use amber or
  green glow (`0 0 7–10px var(--amber|--green)`); focus ring `0 0 0 3px rgba(212,160,23,.1)`. The
  **certificate** alone uses a soft document-lift: `0 1px 0 rgba(236,229,214,.05) inset, 0 40px 90px
  -40px rgba(0,0,0,.8)` — a lifted paper, not a decorative black shadow.
- **Constructed-field recipe (the atmosphere):** fixed `.field` z0 with: a 28px graph grid at 4% paper
  + a 140px fine grid at 2.5%, both radial-masked top-center; one amber **lamp** (two stacked radial
  gradients, `blur(6px)`, `@keyframes lamp` opacity .74↔1 over 7s); a bottom-left underglow; a dust
  canvas (`#dust`); a vignette (radial, transparent→`rgba(0,0,0,.6)`). Exactly ONE colored glow family.
- **Focus-visible:** 3px amber ring at 10% alpha, consistent.
- **Signature placement:** the flatline stays visible logo→favicon→hero→certificate→dead states.

## Primitives
- **pill** (status/badge): mono 10.5px, +0.16em, uppercase, 1px hair border, radius 999px, `rgba(21,18,14,.6)` bg; a 6px glowing dot.
- **button.cta:** amber bg, ink text, mono; hover → `--amber-hi`.
- **input:** surface1 bg, 1px hair-2 border, paper text, mono 14px, radius 11px.
- **certificate:** max-width 620px document, radius 16px, the document-lift shadow; contains the
  verdict, confidence numeral (serif), the ghost-differential, the evidence table (mono tabular,
  right-aligned), the coroner's narration (serif).

## Motion
- `@keyframes lamp` (7s breathing glow), `@keyframes lpulse` (1.1s loading dot), `@keyframes stamp`
  (.55s cubic-bezier(.2,1.5,.4,1) seal stamp).
- Default reveal: `opacity .55s ease, transform .55s cubic-bezier(.16,1,.3,1)`.
- `prefers-reduced-motion`: all animation disabled (`animation:none!important`).
- The flatline itself is canvas-driven in `app/static/app.js` (per-mode trace → flatten → seal).
