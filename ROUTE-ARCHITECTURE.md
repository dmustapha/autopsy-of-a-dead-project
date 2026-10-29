# ROUTE-ARCHITECTURE — Autopsy of a Dead Project (LAW#11)

Routes derived from the user-model (USER-ONBOARDING.md). The product presents as one visual page but
exposes four real routes; no single-page cram. Dependency + flow detail is in ARCHITECTURE §4/§8.

## ROUTES
- `/` — landing. The money shot: title + one-line hook + paste field + three pre-warmed example graves. Serves BOTH user classes (judge skims + clicks an example; reader-dev pastes their own). Server-rendered (Jinja2), warm.
- `/autopsy` — POST (the one loop). Accepts `{repo_url}`, returns the full `AutopsyResult` JSON the card binds to. This is the product's value action for every user.
- `/examples` — GET. Returns the three pre-warmed demo repos (one per death-mode) that power the landing chips — the zero-setup first-value path for the cold stranger.
- `/healthz` — GET. Liveness + model-reachability (`{ok, seed_rows, tabpfn_reachable}`); consumed by Render's health check and the external warm-ping.

Route count = 4 (> 1), satisfying the two-user-class model without a multi-page cram; the single
visual surface is a deliberate product decision (PRD §34 scope), not a cram.

## FIRST-CONTACT
- **30-sec legibility:** within 30 seconds a judge understands the whole product — the title states it, and one click on an example chip renders a death-certificate card (verdict + confidence + evidence table + eulogy + engine badge). No reading required to "get it."
- **Money-shot-on-landing:** the landing route's hero IS the death-certificate card (shown on the first example click); it is also the post's cover image. The money shot is one interaction from the landing, never buried.
- **E0 presentation fix-axes:**
  - **liveness / cold-start:** Render Starter + numInstances=1 + warm-ping → first byte <2s; a judge never meets a cold/dead page.
  - **honesty-placement:** the `engine` badge ("classified by TabPFN" vs "forensic-rules estimate") sits in the card footer, in-frame on every screenshot — honesty is visible at first contact, not hidden.
  - **money-shot:** the certificate card (above).
  - **entry-funnel:** live post link / README → landing → one-click example → value; the cold stranger needs zero setup, no account, no keys.
