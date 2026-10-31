# A11y Report — death-certificate card (design_forge refine)

Run via local Playwright `getComputedStyle` on the live `:3300` instance (real measurements, not delegated).

## Contrast (WCAG)
| Pair | Ratio | AA (4.5) | AAA (7) |
|---|---|---|---|
| paper `#ece5d6` on ground `#0c0b09` | **15.69:1** | ✅ | ✅ |
| amber eyebrow `#D4A017` on ground | **8.28:1** | ✅ | ✅ |

All body/evidence text sits on the warm near-black ground at ≥15:1. No contrast failures.

## Keyboard / focus
- `a/button/input/[tabindex]:focus-visible` → 2px amber outline + 2px offset (added this phase, CF-4).
- `input:focus` retains the amber border + 3px glow ring.
- Single-path flow: Tab → input → CTA → example buttons, all reachable; no focus trap.

## Motion / reduced-motion
- `prefers-reduced-motion: reduce` disables all animation (`animation:none!important`) — the flatline,
  lamp, dust, and seal stamp all freeze; the card stays fully legible and functional.

## Semantics
- `#cert` is `aria-live="polite"` — the verdict is announced when the certificate renders.
- `.field` decorative layer is `aria-hidden="true"`.
- Images carry alt/label (logo SVG `role="img" aria-label`).

## State coverage (all reachable + handled)
loading (`#loading` "exhuming…" + animated dot = the wait/timer indicator) · error (`#error` friendly
422s) · empty (initial landing, no result) · abstain (`insufficient_history` → "No body to examine") ·
abort/failure-recovery (`catch` → re-enables submit + "the crypt is unreachable. Try again.").

Verdict: **a11y PASS** — contrast AAA, keyboard focus affordance present, reduced-motion honored, live region on the verdict.
