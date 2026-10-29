# LIMITATIONS — Autopsy of a Dead Project (honest)

- **Death-mode is an inference, not ground truth.** TabPFN classifies from ~6 git features against a ~50-repo seed set. It is a plausible forensic signal, not a verdict of fact. The UI says "likely cause of death," never "cause of death."
- **Seed dataset is small + hand-labeled.** ~50 repos, labels assigned by the builder → class boundaries are approximate; confidence is calibrated to the seed, not the universe of repos. Stated plainly in the post.
- **Commit-signal only.** We dropped Issues/PR signals for the 1-day scope, so a repo that died in its issue tracker but kept committing may read "alive."
- **GitHub unauth rate limits** (60 req/hr/IP) can throttle bursts without a token; large repos are commit-window-capped.
- **TabPFN hosted dependency.** If `tabpfn-client` is unreachable at request time the app degrades to a transparent forensic-rules verdict, clearly labeled as the fallback (never silently faked).
- **Narration is generative.** Grounded on the real features, but prose — not a precise metric report.
- **Stateless.** No saved history; each autopsy is single-shot.
