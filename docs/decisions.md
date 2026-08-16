# Decision log

Every architectural decision, debated by the council and logged. Verdicts are BUILD / BUY /
DEFER / DROP; a decision is "settled" only after it survives two-layer screening (a bias audit +
red-team pass that can confirm or overturn the first verdict).

## Currently open questions
Kept here so the process is legible — each is debated when evidence exists, not before:
- **Grounded Q&A layer / GraphRAG — the *how*** (plain tool-calls vs vector-RAG vs GraphRAG). Debated at the Phase 2→3 gate, once real signals + results exist. *(design accepted; build in Phase 3)*
- **US-market expansion phasing** — when/whether to extend the US paper leg beyond research. *(topic ready, not yet run)*
- **Experiment-tracking depth** — a CSV runs-log now (built); MLflow when experiments scale. *(provisional — re-run with model diversity)*
- **RL self-learning core** — drop-leaning; not yet formally debated.
- **Backtester architecture — event-driven vs vectorised.** Event-driven makes look-ahead bias structurally impossible; vectorised is far cheaper to build and adequate on daily bars. Includes a prerequisite audit of whether free tick data exists at all, which caps the useful ambition either way. *(Debated at the Phase 2→3 gate.)*
- **Under what conditions, if any, may a learned component participate in the decision path?** Regime detection and Bayesian sizing are already planned, so the question is not "AI or no AI" but where the line sits. The working rule is an **admission test — history and determinism**: a component may inform a decision only if it can be replayed over past data and returns the same output for the same input, so the whole pipeline stays measurable by a deflated Sharpe. Non-deterministic components fail that test on instrumentation grounds, not ideological ones. *(Debated at the Phase 2→3 gate; the current invariant — no agent places or decides a trade — stands until then.)*

| Decision | Verdict | One-line rationale |
|---|---|---|
| Dual Barbell split (as foundational structure) | **DEFER** | Prototype Core/Alpha isolation in paper trading before committing (re-screen confirmed). |
| Barbell ratio & position sizing | **Model agreed; deployment DEFERRED** | Council accepted a cap + fractional-Kelly design (hard Alpha cap, Kelly-sized from deflated out-of-sample edge) and rejected fixed ratios. Actual Alpha allocation deferred to 0 until the Core is proven in isolation. |
| Crisis Scenario Library (stress-replay gate) | **DEFER** | Re-screening reversed an earlier BUILD: without free, realistic crisis-era data, automated stress-tests give false assurance. Audit data availability first. |
| Custom market-event sentiment/news engine | **DEFER** | No proven retail out-of-sample edge; costly/ToS-risky data. Research and paper-trade only, legal sources. **Cost basis refreshed 2026-07:** X/Twitter no longer has a free tier (now metered per post read), while free ticker-tagged news+sentiment does exist (Alpha Vantage, Marketaux, Finnhub, RSS) — so the deciding argument is *frequency, not price*: X's edge is latency, which a daily-frequency system never consumes. Any revisit should be a ₹0 experiment (news as a filter, gated on out-of-sample deflated Sharpe), not a build. |
| Statistical arbitrage / pairs trading | **DEFER** | Defensible edge, but validate on a free platform with walk-forward + structural-break tests before any custom build. |
| Options / derivatives pricing module | **DEFER** | Build as a separate, sandboxed learning module — not on the survivability-first core path. |
| Limit order book simulator | **DEFER** | Not justified for a solo, daily-horizon system until a strategy demands sub-close execution modelling; audit free L2/L3 data first. |
| ML models trained on crisis data | **DROP** | ~10-event sample — near-certain overfitting. |
| Trading frequency | **Intraday direction; HFT out of scope** | Daily/swing near-term, intraday as the sanctioned direction; true HFT ruled out for a solo/free build. Built **frequency-agnostic** so it can be dialled to minutes/seconds later without a rewrite. |
| LLM-summarised social digest as a signal | **DROP as signal; fine as reading** | No history (untestable out-of-sample) and non-deterministic (irreproducible); an LLM producing a number the system trusts is the same failure class as an LLM placing a trade. Ranking by engagement also samples the outcome, since the loudest posts follow the move. |
| Experiment tracking (trial log) | **BUILD (minimal) now → MLflow later** | A CSV runs-log (`aria.experiment_log`) records every trial — kept or dropped — so the deflated Sharpe's trial count is honest; MLflow when experiments scale. |
| Grounded Q&A layer ("ARIA Chat") | **Design accepted; build in Phase 3** | Read-only, cited, forecast-refusing English layer over ARIA's own data; the *how* (tool-calls vs GraphRAG) folds into the vector-search debate at the Phase 2→3 gate. |

**Reading the pattern:** the council is skeptical of narratives and scope creep — most ideas are
deferred until evidence exists, not adopted on a story. The two-layer screening even *reversed its
own earlier BUILD* (the crisis library) once a data-sourcing problem surfaced on the second pass —
which is exactly what a second layer is for. Rejected approaches stay rejected, with reasons
attached, so no decision is ever re-argued from scratch.
