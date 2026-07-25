# Roadmap

Six gated phases. Capital is never deployed before the thing that protects it is proven on paper.
The early phases extract full learning value at essentially zero financial risk; the US leg rides
along at zero cost via free paper-trading APIs.

| Phase | Focus | Capital at risk |
|---|---|---|
| 0 | Research & automated architecture council | Zero |
| 1 | Validate edge on existing platforms (India) + Alpaca paper (US) | Zero (paper) |
| 2 | Build the foundation — Core only, with anti-overfit rigor (walk-forward, purged CV, deflated Sharpe) and cost modelling | Zero (paper) |
| 3 | Differentiators — regime detection; grounded Q&A layer over ARIA's own data | Zero (paper) |
| 4 | Tiny live capital, treated as tuition (India first; US only at scale) | Small, optional |
| 5 | Aggressive Alpha sleeve | Capped, optional |

**Gating logic.** Each phase has an explicit exit gate — e.g. Phase 1: *if there is no edge on a
free platform, no custom build will create one*; Phase 2: *your code must reproduce the platform's
paper-trading results*. Phase 4 (live capital) is optional — staying on paper indefinitely is a
valid end state given the capital-preservation rule.

**Long-run architecture (planned).** Beyond trading, ARIA is being built to reason about its own
history: a **Knowledge & Decision Graph** (decisions ↔ debates ↔ evidence ↔ strategies ↔ experiments,
enabling GraphRAG for the council) and **experiment tracking** (MLflow, self-hosted) so every run —
and the trial count the deflated Sharpe needs — is logged honestly. Free/local tooling only; built when
the corpus justifies it, never on the near-term critical path. A **grounded Q&A layer** will sit on top —
an English interface to ask ARIA about its own signals, metrics, and decisions, answered only from real
data via read-only tool-calls with citations (never a price prediction, never a trade), shown beside a
provenance panel of the exact sources each answer draws on. It is placed in **Phase 3** — it needs the
Phase 2 signals and logged results to talk about — and its design is settled in council at the Phase 2→3
gate, once there is real data to reason over rather than speculation.

**Markets.** India (NSE/BSE) and US. US access for the builder runs through official remittance
rules with treaty tax treatment; US paper trading (free, API-first) is the path for Phases 1–3,
with real US capital deferred until it is justified at scale.
