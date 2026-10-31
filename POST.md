---
title: I built a coroner for dead software. It issues death certificates — and refuses to lie.
published: false
tags: devchallenge, hf26challenge, ai, opensource
cover_image: [image: hero]
---

Every developer has a graveyard.

Mine is a GitHub account full of repos that stopped one day and never started again. A linter I was *sure* would take off. A "weekend" game engine. Three different note-taking apps, because the first two apparently didn't teach me anything. They're not deleted — that would be admitting something — they just sit there with a last commit from some Tuesday, going quietly green to grey.

So for the "Ghost in the Machine" challenge I built the thing those repos deserve: a coroner.

**Autopsy of a Dead Project** is a forensic pathology tool for software. You paste a GitHub URL. A machine examines the body, determines *how* the project died, and issues a death certificate — cause of death, time since last sign of life, a differential diagnosis, and the project's recovered last words. If the repo turns out to be alive, you get a certificate of **LIFE** instead, flatline still beating green.

It's spooky, and it's a little sad, which felt right for a Halloween / Día de los Muertos build. Día de los Muertos isn't about fear — it's about remembering the dead by name. That's the whole frame here. The Repository Coroner doesn't mock your abandoned projects. It memorializes them.

[image: cert-bower]

## What's actually under the sheet

Two open-weight models do the forensics, and — this is the part I care about most — **both of them run locally, on my own box, with no hosted inference anywhere in the loop.**

**TabPFN** is a tabular foundation model. Instead of training a classifier on my data, it does *in-context learning*: you hand it a small labelled corpus and a new row, and in one forward pass it returns a posterior — an actual probability distribution over the possible outcomes, not a single confident guess. For me the "row" is a 10-feature vector I pull from the GitHub API for any repo:

- days since last commit
- commit-cadence decay (the slope of how fast the heartbeat slowed)
- lifespan in days
- contributor count
- bus factor
- velocity ratio (recent activity ÷ lifetime activity)
- is-archived
- release recency
- has-releases
- open-issue ratio

Those ten numbers go in; a distribution over six **death modes** comes out: `abandoned`, `burned_out`, `pivoted`, `completed`, `alive`, and `insufficient_history`.

The second model is **Gemma** (`gemma2:2b`), served locally through **Ollama**. It has two jobs. First, it's a tie-zone **adjudicator**: when TabPFN's top two causes are too close to call, Gemma reads the actual commit messages and README and can break the tie — but only on a high-confidence read. Second, it's the coroner's voice: it writes the eulogy on the certificate, grounded in the evidence.

### Why "local open weights" is the whole point, not a footnote

Early in the build I was running TabPFN through Prior Labs' hosted API. It worked. Then one day it returned `503 Service is disabled`, and my coroner had no brain. That was the moment the architecture decision made itself: **I switched the hosted client off and ran the open TabPFN weights on-device.** `from tabpfn import TabPFNClassifier`, model loads once per process, predicts in about four seconds. No key, no bill, no external dependency that can go dark mid-autopsy.

Pair that with Gemma on Ollama (`LLM_BASE_URL=http://localhost:11434/v1`) and the entire pipeline — classification *and* narration — has zero closed dependencies. It runs offline. You can read every weight and every line. For a tool whose entire pitch is *honesty about death*, "you can inspect exactly what judged you" isn't a nice-to-have. It's the point. Open weights are what let me make this promise and keep it.

And I'm honest on the certificate itself about which brain actually fired. Every result carries an engine label:

- `tabpfn` — the foundation model called it clean
- `tabpfn + llm · adjudicated` — Gemma broke a tie
- `rules` — TabPFN was offline, so a transparent forensic-rules fallback took over (labeled, never disguised as the model)
- `rules + llm` — rules verdict, LLM adjudicated

Nothing is hidden behind a generic "AI says."

[image: cert-tabpfn-differential]

## The honesty engine (the part I'm proudest of)

Here's the design decision that I think actually makes this tool worth shipping.

A eulogy is generative text. Generative text hallucinates. A coroner that invents a cause of death is not a coroner — it's a liar with nice handwriting. So between Gemma and the certificate, there's a **grounding gate**: before any eulogy reaches the card, I check that its claims trace back to the real evidence — the actual commit record, the real README. If the prose drifts into stuff the data doesn't support, the gate **refuses it**.

When the gate refuses, the certificate falls back to a templated, strictly-factual coroner, and the badge reads **"LLM OFFLINE."**

That label is a small, deliberate lie-by-omission that I decided to keep, and here's the honest version: during testing, for `Polymer/polymer` and `bower/bower`, Ollama was *up and running*. Gemma produced eulogies. But those eulogies failed the grounding check — so the certificate dropped to the templated coroner and showed "LLM OFFLINE" anyway. The model was online; its *output* was not trustworthy, so the tool treated it as if it weren't there. For `fastapi/fastapi`, Gemma's eulogy passed grounding and was shown live, bylined "narrated by Gemma (open weights)."

I went back and forth on that "LLM OFFLINE" wording. I kept it. The tool would genuinely rather say *"I couldn't ground this"* than narrate a death it can't defend. That's not a bug I'm apologizing for — it's the feature.

[image: cert-fastapi]

A couple of forensic touches that fall out of the same philosophy:

- **Differential diagnosis.** Like a real pathologist considering competing causes, the certificate shows the whole posterior, not just the winner. `Polymer/polymer` reads *pivoted 38% · completed 22% · burned_out 19% · abandoned 18% · alive 2%* — the uncertainty is on the page, in ink.
- **The death note.** Each death certificate recovers the project's "last words" — a real, confidence-gated quote lifted from the README or commit history. Polymer's is almost too on-the-nose: *"If you're starting a new project, we recommend that you consider using LitElement instead."* That's the maintainers signing their own certificate. I only show it on death certificates, and only when I'm confident it's really theirs.
- **A cohort line.** "Died like 2 of 5 similar repos," from a nearest-neighbour comparison — so a death feels situated, not isolated.

## What this is *not* (because a coroner should disclose)

If I'm going to make a whole tool about intellectual honesty, the limitations section can't be the one place I go quiet.

- The labelled corpus is **48 rows**, hand-labelled by me. There's **no held-out evaluation**, so every confidence number is *in-distribution* — calibrated to my little graveyard, not the universe of repos.
- `open_issue_ratio` is a **weak signal** on the hard cases. The genuinely hard call is `abandoned` vs `completed`, and that feature doesn't reliably separate them.
- The cohort line reuses the classifier's own k-NN neighbours. It's a **UX touch, not independent validation** — don't read it as a second opinion.
- The six death modes are **editorial judgment calls.** "Burned out" vs "abandoned" is sometimes a story I'm choosing to tell about the numbers. I believe the stories. They're still stories.

None of that makes the tool useless. It makes it a *forensic estimate that knows it's an estimate* — which, for something stamping "cause of death" on your side-projects, is exactly the posture I want.

## What it means

The stack is deliberately boring so the ideas can be loud: Python, FastAPI + uvicorn, a Jinja2 template, and vanilla JS on a `<canvas>` for the certificate — the flatline animation, the wax seal, the guilloche watermark, no framework bloat. 47 tests green. Fully local, it's TabPFN plus Gemma on Ollama and nothing else phoning home.

But the thing I actually built isn't a GitHub-stats dashboard. It's a small argument that AI tools can be made to **know the edge of what they know** — to issue a verdict *and* show their uncertainty, to recover real last words instead of inventing poignant ones, to say "offline" when their own output can't be trusted even though the lights are on.

My graveyard is still full. The difference is now every stone has a cause of death on it, and I believe every one.

Go autopsy your own graveyard. Paste your proudest dead repo and see how it died — or find out, maybe uncomfortably, that it's still breathing and you're the one who walked away.

**Code:** [INSERT repo URL]
