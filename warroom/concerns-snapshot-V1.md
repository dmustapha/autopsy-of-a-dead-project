# Hackathon Warroom Concerns
**Last updated:** 2026-03-01
**Source:** Refined across Seeker/MONOLITH, Ethereum Lagos, Chainlink Convergence
**Version:** 2.0 — Added severity weights, conflict resolution, negative examples

---

## Severity Levels

Each concern carries a severity weight that determines how it is handled during deliberation:

| Severity | Label | Meaning | Deliberation Impact |
|:---:|---|---|---|
| **C** | Critical | Violation = idea is eliminated | Cannot proceed to Round 4 if any Critical concern is unaddressed |
| **I** | Important | Violation = significant score penalty | Deduct 1-2 points from relevant criterion per unaddressed Important concern |
| **A** | Advisory | Violation = noted but not disqualifying | Flagged in concerns compliance table, no automatic penalty |

---

## UNIVERSAL (Always included in every warroom — non-negotiable)

1. **[C] Time NOT a constraint.** Claude Code = 10x dev speed. Do NOT penalize ideas for complexity. Do NOT kill good ideas because "9 days isn't enough." With Claude Code, MCP servers, subagents, skills, and hooks, ambitious projects are achievable.
   - *BAD:* "This idea requires a smart contract AND a frontend AND an API — too complex for one person in 7 days." (Wrong — Claude Code handles this.)
   - *GOOD:* Evaluate on merit, not perceived build time.

2. **[I] Everything is devnet/testnet.** Mocks are fine. No real money, no real infrastructure needed for hackathon demos. Judge ideas on whether the concept and demo are compelling, not whether they have production infrastructure.
   - *BAD:* "We need real liquidity pools with $10K TVL for the demo to work."
   - *GOOD:* "We'll pre-seed testnet with mock data that makes the demo feel real."

3. **[C] Uniqueness is non-negotiable.** If competitors exist in the hackathon's ecosystem for the same idea, that's a SERIOUS strike. Zero competitors in the target space is strongly preferred. Verify competition for EACH idea explicitly.
   - *BAD:* "There are 3 other DEX aggregators but ours will be better." (Unlikely to win.)
   - *GOOD:* "No one in the hackathon is building oracle-based insurance. Zero competitors confirmed via Discord intel and Devpost search."

4. **[A] Fresh ideas allowed.** Not limited to any previous list or predefined set. Agents can and should invent completely new ideas. The research exists to inform, not constrain.

5. **[C] "Does this help real humans?" test.** Every idea must pass it. If you can't point to real people whose lives improve because this exists, the idea fails.
   - *BAD:* "This is a really cool technical experiment with blockchain oracles."
   - *GOOD:* "500M smallholder farmers have zero crop insurance. This gives them coverage for $2/month."

6. **[I] Read ALL research data.** Discord intel, Twitter/Grok intel, Telegram intel, web research, competitor analysis, winning patterns, judge preferences — use EVERYTHING. Do not cherry-pick.
   - *BAD:* Agent proposes idea without citing any research files.
   - *GOOD:* Agent cites discord-intelligence-report.md Section 4, deep-research.md Section 10, and master-research.md finding #7.

7. **[I] Take your time, be extensive.** No rushing through deliberation. Each agent's proposals should be 200-400 words with specific citations from research. Cross-examination should be thorough, not surface-level. The warroom produces 800+ lines of genuine debate.

8. **[C] Cumulative corrections (nothing dropped).** Every correction from every warroom version (V1, V2, V3...) carries forward. If a concern was raised, it persists. Nothing is silently dropped between iterations.
   - *BAD:* V2 ignores a correction made in V1 because it doesn't fit the new direction.
   - *GOOD:* V2 explicitly addresses the V1 correction: "V1 correction about [X] is addressed by [Y]."

9. **[C] Must solve a SIGNIFICANT, real problem.** The builder must BELIEVE in what the idea does, not just believe it can win. "Would I still build this if there were no prize?" is the test.
   - *BAD:* "This idea maximizes hackathon-gaming strategy but I wouldn't use it myself."
   - *GOOD:* "I would build this anyway because [specific problem] affects [specific people] and no solution exists."

10. **[I] Focused product, BROAD problem.** Niche scope for the hackathon MVP is fine. Niche AUDIENCE is NOT. The problem should affect MILLIONS of real people. The solution should be one clean, focused thing that addresses a piece of that broad problem.
    - *BAD:* "This tool helps 200 NFT traders on one specific chain."
    - *GOOD:* "This tool addresses a piece of the $50B wage theft problem, starting with gig workers."

11. **[I] Winning AND real impact are not mutually exclusive.** The goal is to find ideas where both align. Never sacrifice real-world value for hackathon-gaming strategy, and never sacrifice winnability for pure idealism. Find BOTH.

12. **[A] Reframing is on the table.** The same technology stack can be applied to different problems. Don't just pick from a list of ideas — find the best problem-technology fit. If the hackathon's core tech has an obvious application nobody is pursuing, that's a signal.

13. **[C] Must serve actual target users who exist TODAY.** The idea's primary users should be identifiable, reachable people. "Future users after the ecosystem matures" is not sufficient. Who uses this on day 1?
    - *BAD:* "Once the blockchain ecosystem matures, millions will use this."
    - *GOOD:* "Freelancers on Upwork who lose 10% to transfer fees — reachable via Upwork forums and freelancer Discords."

14. **[I] Demo must feel like the real product.** The gap between the hackathon demo and what the actual product would be should be as small as possible. Judges should see a product, not a prototype. Pre-seed with realistic data if needed.
    - *BAD:* "The demo just shows a form that says 'transaction submitted' with lorem ipsum data."
    - *GOOD:* "Pre-seeded with 50 realistic user profiles, real transaction history, and live oracle price feeds on testnet."

15. **[C] No self-duplication — must not rebuild the builder's shipped OR in-flight projects.** An idea whose CORE problem + primary mechanism matches a project the builder has shipped or is actively building is eliminated — **regardless of chain**. "Same mechanism" is the load-bearing primitive, not the surface name: a commit-then-resolve-on-chain reputation/track-record system is ONE shape whether branded "accountability ledger," "falsifiable alpha," or "verifiable resume." **In-flight/concurrent projects (active build, overlapping deadline) are the highest risk** — they are freshest in mind so they dominate generation, and re-skinning one onto a new chain is self-plagiarism, not translation. The warroom builds this forbidden-shapes list at Step 0B.2 (shipped from built-projects.md; in-flight from memory + sibling working dirs + TASTE.md) and injects it into the generator kill-list.
    - *BAD:* "Port our currently-building AlphaAttest accountability layer onto Mantle with a 'falsifiable alpha' reskin." (Two near-identical submissions to two live hackathons in the same week.)
    - *GOOD:* "AlphaAttest is the commit-resolve-attest shape — banned. This idea is an AI negotiating counterparty: a different load-bearing primitive entirely."

---

## Conflict Resolution

When concerns conflict with each other, use this priority order:

1. **Critical concerns always win over Important and Advisory.**
2. **Between Critical concerns:** Concern #5 (real humans) and #9 (significant problem) take precedence over #3 (uniqueness). An idea that solves a real problem with some competition is better than a unique idea that helps nobody.
3. **Between Important concerns:** #6 (use all research) and #7 (be extensive) support each other and cannot be traded off.
4. **When a user correction contradicts a universal concern:** The user correction wins. Document the override explicitly: "User override: [concern #X] relaxed because [reason]."
5. **When an advisory concern conflicts with a Critical one:** Drop the advisory concern entirely.

---

## CONTEXTUAL (Included when relevant — skill prompts you about each one)

- **[A] AI/Agents should be considered when appropriate.** [Relevant when: AI is a PRIMARY track with >20% judging weight, OR the hackathon's core platform is an AI infrastructure (Gensyn, ElizaOS, Virtuals, etc.). NOT relevant when: AI is one of many tracks, AI integration is optional, or the hackathon is primarily DeFi/gaming/infrastructure. This concern should activate rarely — most hackathons do not require AI to win. When it does activate, it means "consider whether AI adds genuine value here," not "push ideas toward AI."]
  - *BAD:* "There's an AI track so all ideas should involve AI agents." (Activating too broadly — a small track does not justify domain-wide bias.)
  - *GOOD (activating):* "The hackathon's only track is AI infrastructure and all judges are AI researchers — AI integration is mandatory, not optional."
  - *GOOD (not activating):* "There's a small AI bounty but main tracks are DeFi and tooling — this concern does not apply."

- **[I] Hardware utilization matters.** [Relevant when: hardware-specific hackathon like Seeker/Solana Mobile, where the judging criteria include hardware leverage or "only possible on this device" differentiation.]

- **[I] Mobile-native UX required.** [Relevant when: mobile-first hackathon where UX/stickiness is a major judging criterion and the platform is mobile devices.]

- **[I] Cross-chain capability valued.** [Relevant when: hackathon involves interoperability technology like CCIP, bridges, or multi-chain messaging, and judges specifically evaluate cross-chain integration.]

- **[I] Confidential compute / privacy angle.** [Relevant when: hackathon has a privacy track or the ecosystem is pushing confidential compute, zero-knowledge, or selective disclosure narratives.]

- **[A] Sponsor bounty stacking strategy.** [Relevant when: hackathon has sponsor-specific bounties (e.g., Worldcoin, Tenderly, thirdweb) that can be stacked on top of track prizes for maximum prize potential.]
  - *BAD:* "Bolt on 3 sponsor SDKs superficially to qualify for all bounties."
  - *GOOD:* "Our core architecture naturally uses CCIP + Functions. Adding Worldcoin identity verification deepens the product and qualifies for their bounty."

---

## PER-HACKATHON (Added during warroom setup — one-time, specific to current hackathon)

<!-- This section is populated per hackathon run. Examples from past hackathons:
- "TRUSTTAP must be included and deeply evaluated" (Seeker V5)
- "Crypto-native Seeker owners are the actual target users, not hypothetical future users" (Seeker V5)
- "The project must meaningfully use CRE, not just wrap it superficially" (Chainlink)
-->
