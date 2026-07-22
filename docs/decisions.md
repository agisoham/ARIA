# Decision log

Every architectural decision, debated by the council and logged. Verdicts are BUILD / BUY /
DEFER / DROP; a decision is "settled" only after it survives two-layer screening (a bias audit +
red-team pass that can confirm or overturn the first verdict).

| Decision | Verdict | One-line rationale |
|---|---|---|
| Dual Barbell split (as foundational structure) | **DEFER** | Prototype Core/Alpha isolation in paper trading before committing (re-screen confirmed). |
| Barbell ratio & position sizing | **DEFER → capped pilot** | Don't lock a fixed ratio; run a small, reversible, capped pilot. Sizing to be a hard Alpha *cap* with fractional-Kelly deployment within it, set from measured data — not a chosen number. |
| Crisis Scenario Library (stress-replay gate) | **DEFER** | Re-screening reversed an earlier BUILD: without free, realistic crisis-era data, automated stress-tests give false assurance. Audit data availability first. |
| Custom market-event sentiment/news engine | **DEFER** | No proven retail out-of-sample edge; costly/ToS-risky data. Research and paper-trade only, legal sources. |
| Statistical arbitrage / pairs trading | **DEFER** | Defensible edge, but validate on a free platform with walk-forward + structural-break tests before any custom build. |
| Options / derivatives pricing module | **DEFER** | Build as a separate, sandboxed learning module — not on the survivability-first core path. |
| Limit order book simulator | **DEFER** | Not justified for a solo, daily-horizon system until a strategy demands sub-close execution modelling; audit free L2/L3 data first. |
| ML models trained on crisis data | **DROP** | ~10-event sample — near-certain overfitting. |

**Reading the pattern:** the council is skeptical of narratives and scope creep — most ideas are
deferred until evidence exists, not adopted on a story. The two-layer screening even *reversed its
own earlier BUILD* (the crisis library) once a data-sourcing problem surfaced on the second pass —
which is exactly what a second layer is for. Rejected approaches stay rejected, with reasons
attached, so no decision is ever re-argued from scratch.
