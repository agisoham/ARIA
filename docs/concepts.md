# Concepts & methods

The quant, ML, and systems methods ARIA uses — and plans to. Marked honestly:
**✅ in use / built · ⬜ planned · ✎ considered then deferred/dropped.** The ✅ items are in the code
(`src/aria/`); the ⬜ items are an ordered runway, not a wish-list; the ✎ items show what was
weighed and set aside (judgement, not omission).

## Quantitative finance & trading
- ✅ **Sharpe / Sortino / max drawdown / Calmar / CAGR / annualised volatility** — the standard risk-adjusted return and survivability metrics (`aria.metrics`).
- ✅ **Probabilistic Sharpe Ratio (PSR)** — P(true Sharpe > benchmark), correcting for track length, skew and kurtosis (López de Prado).
- ✅ **Deflated Sharpe Ratio (DSR)** — PSR with the benchmark raised to the Sharpe expected *by luck* after N trials. The honest "is this overfit?" test.
- ✅ **Walk-forward validation** — train on the past, test on the next unseen block, roll forward (`aria.validation`).
- ✅ **Purged K-fold + embargo** — cross-validation that drops train samples adjacent to the test fold to stop label leakage (López de Prado).
- ✅ **Look-ahead bias / overfitting / in-sample vs out-of-sample** — the failure modes the above stack exists to catch.
- ✅ **Dual Barbell (Taleb)** — most capital in a survivable Core, a small capped aggressive sleeve; convex and survivable.
- ✅ **Momentum & mean-reversion** — the two classic strategy families (moving-average crossover; RSI / Bollinger reversion) used to validate edge honestly.
- ✅ **Technical indicators** — SMA, EMA, MACD, RSI, Bollinger bands.
- ✅ **Fractional Kelly sizing** — size from edge/variance (f*≈μ/σ²), scaled to tame drawdown and estimation error.
- ⬜ **Transaction-cost modelling** — spread, slippage, market impact, fees; a cost-blind backtest is a red flag. Working spec: half-spread on entry (ask) plus half-spread on exit (bid) plus a flat per-trade commission, using real bid/ask where available.
- ✎ **Kelly degeneracy** — a Kelly-derived sizer can collapse to a near-constant output regardless of conviction, at which point it is fixed sizing wearing a formula. Worth testing for explicitly before trusting fractional-Kelly deployment; conviction-tiered sizing is the fallback.
- ⬜ **One-pipeline replay** — the backtest executes the same code path as live, replayed over historical data, so simulation and production cannot silently diverge.
- ✎ **Hindsight narrative** — an after-the-fact causal story about why a trade worked or failed. It feels like understanding but is invented, and if a language model writes it into a trade journal, fabricated causality re-enters the decision loop disguised as documentation. The rule ARIA adopts: narrate what the *system* did, never why the *market* moved.

## Reliability & operations *(planned, Phase 4+)*
- ⬜ **Restartability over uptime** — design to be safe to crash rather than to never crash: state in a database rather than memory, idempotent operations, and a startup reconciliation that resolves drift between recorded and broker-actual positions before acting.
- ⬜ **Broker-side resting stops** — a stop held as a condition inside a running process protects nothing once that process dies. Protective orders rest at the exchange. Enforced as an invariant in `AGENTS.md`.
- ⬜ **Scheduled cloud execution** — free scheduled CI runners suit daily frequency; an always-on free-tier VM comes next. A machine at home shares the power and network failure domain it is meant to survive.
- ⬜ **VaR / CVaR (Expected Shortfall)** — loss at a confidence level / expected loss beyond it; the risk engine's language.
- ✎ **Statistical arbitrage / pairs (cointegration — Engle-Granger, Johansen; stationarity tests)** — deferred until validated.
- ✎ **Regime detection (Hidden Markov Models)** — latent market states; a Phase-3 differentiator.
- ✎ **Options pricing (Black-Scholes, binomial trees, Monte Carlo, the Greeks; GARCH vol)** — deferred as a separate learning module.
- ✎ **Fat tails / survivorship bias / risk compensation** — the reasoning behind treating "measured" worst-case floors with suspicion.

## Machine learning & the LLM council
- ✅ **Multi-agent LLM council** — conflicting-mandate agents debate every architecture decision before code.
- ✅ **Two-layer screening** — a bias-audit + red-team pass that re-screens and can overturn a verdict.
- ✅ **Reflection / self-correction · Chair calibration** — a non-voting Critic; a synthesis rule against over-cautious verdicts.
- ✅ **Self-healing model IDs** — validate model names against the live provider catalog and auto-correct drift.
- ⬜ **RAG · vector search (FAISS/Chroma) · knowledge graph / GraphRAG** — feed the council retrieved, connected evidence instead of priors.
- ⬜ **Grounded Q&A layer + provenance** — an optional English interface to query ARIA's own signals, metrics, and decisions, answered only via read-only tool-calls with citations and a grounding-check — never a price prediction, never a trade. A two-window UI shows each answer beside the exact sources it's built from.
- ⬜ **Bayesian decision engine / Bayesian optimisation** — probability-of-success sizing; overfit-safe tuning.
- ✎ **FinBERT sentiment · reinforcement-learning trading core** — deferred / drop-leaning (overfit traps at this scale).
- ✎ **Backtestability as the admission test** — data may inform a strategy only if it has *history* (so it can be tested out-of-sample) and is *deterministic* (same input ⇒ same number). LLM-summarised social digests fail both, so they stay reading material and never become signal — an LLM producing a number the system trusts is the same failure class as an LLM placing a trade.
- ✎ **Engagement bias** — ranking social posts by engagement samples the *outcome*: the loudest posts about a stock arrive after it has already moved. A cousin of look-ahead bias, disguised as sensible filtering.

## Software engineering & systems
- ✅ **Frequency-agnostic design** — timeframe is a parameter, never hardcoded; daily today, minute/second later without a rewrite.
- ✅ **Prover-first** — build the validator (metrics + splits) before any strategy.
- ✅ **TDD / pytest · secret management (gitleaks, gitignored `.env`) · agent invariants (`AGENTS.md`)**.
- ✅ **Rate-limit handling / backoff · OpenAI-compatible provider abstraction** — the engine's plumbing.
- ⬜ **Vectorisation (NumPy/pandas/Polars) · numba · Parquet caching · profiling** — the backtester's speed toolkit.
- ✅ **Experiment tracking (trial log)** — `aria.experiment_log` records every strategy/variant tried, kept or dropped, so the deflated Sharpe's trial count is honest (unit-tested); MLflow later when experiments scale.
- ✅ **Honest trial-counting** — the deflated Sharpe is only truthful if N counts *every* attempt including failures; log as you run.
- ⬜ **Data loader · vectorised frequency-agnostic backtester · MLflow experiment tracking**.

## What's next, by phase
- **Phase 1:** apply the metrics (incl. deflated Sharpe) to real paper-trading results; honest in-sample vs out-of-sample.
- **Phase 2:** data loader (Parquet), vectorised backtester, transaction-cost model, risk engine (VaR/CVaR, stop-loss, kill-switch), experiment tracking, Kelly sizing.
- **Phase 3:** regime detection (HMM); statistical arbitrage if validated.
- **Long-run:** RAG / GraphRAG / vector search / knowledge graph; Bayesian decision engine.
