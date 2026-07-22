# Methodology — the LLM Council & Two-Layer Screening

ARIA's core discipline is **debate before build, prove before risk.** Every significant
architectural decision is pressure-tested by an automated council of AI agents *before* any
code is written, and no verdict is trusted on a single pass.

## Why conflicting incentives
A single AI advisor tends to agree with you. Give each agent an opposing mandate and weak ideas
are attacked from several directions at once. An idea survives only if it withstands the quant's
demand for evidence, the risk manager's fear of ruin, the engineer's buildability test, and the
pragmatist's "why not just buy it?" challenge — while an **Advocate** ensures the strongest case
*for* the idea is also on the table, so the board never rejects by default.

## The seats
| Seat | Mandate | Core question |
|---|---|---|
| Quant Purist | Statistical-edge zealot | Measured out-of-sample evidence, or just a story? |
| Risk Manager | Survival-obsessed permabear | What's the worst case — does it end the game? |
| Systems Engineer | Buildability realist | Can one person build & maintain this in time? |
| Pragmatist | Build-vs-buy challenger | Why build what already exists? |
| Advocate | Steelman | What's the strongest honest case FOR? |
| Data-Signal Specialist | NLP / quant-data expert | Is there a real, extractable signal? |
| Compliance & Data-Rights | Regulation & ToS | Is this legal and licence-clean? |

Panels are configurable per decision, and each seat can be cast to a specific model so the
strongest reasoner sits in the pivotal seat.

## Layer 1 — the debate
1. The decision is submitted to the panel.
2. Each agent argues in turn over N rounds, seeing and rebutting the prior agents.
3. A non-voting **Critic** reviews the debate for groupthink and blind spots (a reflection pass).
4. A **Chair** synthesises a verdict — **BUILD / BUY / DEFER / DROP** + one concrete next action —
   under a **calibration rule**: it may not be more cautious than the most cautious individual seat
   without stating a justification (this prevents a survivability-biased panel from over-rejecting).

## Layer 2 — re-screening
A single debate can share a systemic bias across all seats. Layer 2 stress-tests the Layer-1
verdict itself:
1. **Bias Auditor** — names the systemic bias most likely to have skewed *this* panel
   (survivability-bias, status-quo bias, novelty-aversion…) and the consideration the whole panel
   under-weighted.
2. **Red Team** — argues the verdict is *wrong*, using the audited bias and the Critic's missed
   points, and names the alternative verdict.
3. **Chair** — issues a second-layer ruling: **CONFIRM** or **REVISE**.

A decision is only "settled" once it survives Layer 2. Both layers are logged verbatim.

## Design principles learned in practice
- **Steelman everything.** A board without an Advocate drifts toward reflexive caution.
- **Calibrate the Chair.** Synthesis should reflect the debate, not amplify one bias.
- **Diversity is real only across model *families*.** Route seats across providers where possible.
- **Free-tier realism.** Reasoning models have the tightest quotas — reserve them for single-shot
  roles. Pace calls; keep prompts within input caps.
