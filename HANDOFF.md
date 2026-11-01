# HANDOFF

One page to reproduce "Autopsy of a Dead Project" from a cold clone.

## Target commit
`git checkout 5a4942fd6d86374cc3bd278f20c1c39b2b3c958e`
Branch `depth-upgrade-ui-surfacing` is the repo's default branch (a plain `git clone` lands on it), so the checkout is optional. There is no `main` to go stale.

## Fresh-clone verify (the headline claim, re-derivable)
```
git clone https://github.com/dmustapha/autopsy-of-a-dead-project && cd autopsy-of-a-dead-project
pip install -r requirements.txt
python scripts/eval_loo.py
```
Expected: TabPFN leave-one-out ≈ 58.1%, 1-nearest-neighbour baseline ≈ 43.6% (a ~14.5 point gap) over the 117-repo corpus. This re-derives the single load-bearing claim of the submission.

Run the suite:
```
pytest
```
Expected: green (68 tests per the build/verify records; 60+ test functions under `tests/`).

## Demo walkthrough
See `submission/HACKATHON-README.md` "Try it". Short version: open https://autopsy.132-145-100-81.sslip.io and click the `bower`, `caprine`, or `fastapi` example chips for an instant cached verdict. Never type a fresh repo on camera (cold path is slow by design).

## Do-not-modify (freeze list)
Load-bearing for the recorded proof; changing them invalidates the numbers:
- `app/classifier.py` — TabPFN verdict (the headline model)
- `app/narrator.py` — the grounding gate (the honesty invariant)
- `scripts/eval_loo.py` — the held-out eval that produces 58.1 vs 43.6
- the 117-row labelled corpus that eval reads

## Notes
- Live service uses 0G Compute (a network call) for narration; cold autopsies on unseen repos take a couple of minutes, cached examples return under 2 seconds.
- Open-weight end to end is true; "fully offline / nothing phones home" is NOT claimed for the live service. See `submission/HONESTY-LEDGER.md`.
