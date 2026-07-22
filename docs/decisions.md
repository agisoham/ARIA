# Decision log

Every architectural decision, debated by the council and logged. Verdicts are BUILD / BUY /
DEFER / DROP; a decision is "settled" only after it survives two-layer screening.

| Date | Decision | Verdict | One-line rationale |
|---|---|---|---|
| 2026-07 | Dual Barbell split (as foundational structure) | **DEFER** | Prove Core/Alpha isolation in a paper-traded prototype before committing. |
| 2026-07 | Custom market-event sentiment/news engine | **DEFER** | No proven retail out-of-sample alpha; costly/ToS-risky data. Revisit after the Core, legal sources only. |
| 2026-07 | Crisis Scenario Library (stress-replay gate) | **BUILD** | A lightweight, code-enforced replay of strategies through historical crashes — cheap, high survivability value. ML-trained-on-crises dropped as an overfitting trap. |
| 2026-07 | 75/25 ratio + explicit stress floor | **DEFER** | Not the math but the evidence timing — set the ratio from measured Core drawdown data, not before it exists. |

**Reading the pattern:** the council is skeptical of narratives (three DEFERs) and receptive to
cheap survivability instruments (one BUILD) — and the instrument it approved is exactly what
produces the evidence the deferred decisions are waiting on. Rejected approaches stay rejected,
with their reasons attached, so no decision is ever re-argued from scratch.
