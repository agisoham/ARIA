# Example council debate (synthetic)

> **This is a fully synthetic, anonymized example** — no real strategy, no real market view.
> Its only purpose is to show the *shape* of an ARIA council debate and the two-layer screening.
> Real strategy debates are kept private (see `.gitignore`); the public repo ships this example
> and the neutral `topics/_template.md`.
>
> Generated shape only — the model text below is illustrative, not a real run.

**Topic:** Should ARIA cache downloaded market data to Parquet, or reload it from the data API on every run?
**Seats:** quant · systems · pragmatist · advocate · futureproof
**Rounds:** 2 · non-voting Critic · calibrated Chair

---

## Layer 1 — debate

### Round 1
- **Systems** — Reloading from the API every run is slow and burns free-tier rate limits; a local Parquet cache keyed by (symbol, timeframe, date-range) makes backtests reproducible and fast. Standard practice.
- **Quant** — Caching is fine *only if* it can't introduce look-ahead. A cache that silently serves survivorship-adjusted or forward-revised data would corrupt every backtest. The cache must store raw, as-of data with the fetch date.
- **Pragmatist** — Do we need this now? Phase 1 runs are small and daily. A cache is ~30 lines, but it's another moving part that can go stale. Cheapest correct thing first.
- **Advocate (steelman)** — The cache pays for itself the first time you re-run a walk-forward: identical inputs, no network flakiness, and it's the foundation the Phase-2 backtester needs anyway. Build the small version now.
- **Future-Proofer** — Will this matter in 2 years? Yes — Parquet + a partition scheme is exactly what scales to minute/second data later. Choosing it now avoids a rewrite. Low regret.

### Round 2 (seats respond)
- **Quant** — Concede the value if invalidation is explicit: cache entries carry a `fetched_at` and are immutable; corrections write a *new* row, never overwrite. Then no look-ahead.
- **Pragmatist** — Agreed if it stays ~30 lines and the cache path is gitignored (data isn't committed). No custom cache server, no DB.
- **Systems** — Parquet on disk, one file per (symbol, timeframe); no service. Fine.

### Critic (reflection, non-voting)
The panel converged fast — watch for consensus bias. The one unaddressed risk is *cache poisoning by a bad fetch*: if the API returns a partial day, it could be cached as truth. Recommend a validation check on write (row count, monotonic dates) before a fetch is cached.

### Chair verdict
**BUILD (minimal)** — add a small Parquet cache with immutable, timestamped entries and a validate-on-write check; keep the data gitignored.
**Next action:** implement `data/cache.py` with `(symbol, timeframe, range) → Parquet`, `fetched_at` column, and a write-time validation; unit-test the no-overwrite + validation behavior.

---

## Layer 2 — re-screening

- **Bias Auditor** — Systemic lean: *pro-build / novelty toward tooling.* A builder-heavy panel enjoys building infrastructure; the Pragmatist's "do we need it now?" was conceded quickly. The bias would push toward building sooner/bigger than needed.
- **Red Team** — The verdict could be wrong if Phase 1 never actually re-runs the same range enough to amortize the cache — then it's premature infrastructure. Alternative verdict: **DEFER** until a backtest is re-run ≥3 times.
- **Chair (2nd ruling): CONFIRM (BUILD, minimal).** The cache is a *Phase-2 prerequisite* regardless, and the "minimal + validate-on-write" scope already answers the over-building bias. But the ruling adopts the Red Team's guardrail: **keep it ~30 lines; if it grows a service or a DB, that's scope creep to re-debate.**

**Settled:** BUILD the minimal, immutable, validated Parquet cache. Re-debate only if it outgrows a single-file-per-series design.
