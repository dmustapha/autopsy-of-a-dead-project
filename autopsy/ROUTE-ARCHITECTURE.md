# ROUTE-ARCHITECTURE — Autopsy of a Dead Project

A deliberately small app (one load, one paste-field) but NOT a single-page cram: the landing, the result, and a separate judge/demo route are distinct, derived from the two-class user model.

## ROUTES
- `/` (landing) — R-7 opening beat: hero line, paste field, and a pre-seeded death-certificate visible on first paint (no empty state).
- `/autopsy` (POST) — the app action: accepts the pasted URL, runs the loop, streams the result into the certificate card (HTMX/fetch-streamed partial, same page).
- `/demo` — separate judge/demo route: shows 3 pre-seeded certificates (one per interesting death-mode) side by side, the measured table, and the hold-out accuracy figure. The route a judge lands on to evaluate without pasting.
- `/healthz` — the keep-warm heartbeat endpoint (durability-tier keepWarm target).

## FIRST-CONTACT
- 30-sec legibility: "Paste a dead GitHub repo. An open-weight AI tells you how it died."
- money-shot: the death-certificate card (parchment/tombstone aesthetic) — the post hero image.
- liveness/cold-start: a seeded certificate for a famous dead repo renders immediately on `/` (no spinner on first paint).
- honesty: a footer line stating the stack (TabPFN classifies, open-weight model on Groq narrates) and a limitations link; the verdict is the model's output, not a rule.
- entry-funnel: the single hero CTA is the paste field + "Autopsy" button.
