# ARIA — Adaptive Responsive Intelligence Architecture

**A solo-built algorithmic trading system for Indian and US markets, engineered survivability-first.**
Primary goal: learning ML, quantitative finance, and systems engineering deeply. Hard rule: never
lose money. Earning is a genuine goal too — strictly within SEBI regulations, exchange rules, and
broker terms.

> *Debate before you build. Prove before you risk. Protect the Core, always.*

## Philosophy
ARIA rejects the "predict the market" framing in favour of **manage uncertainty and survive**. The
architecture is a **Dual Barbell**: a conservative Core (80–90% of any deployed capital, built for
survivability and steady compounding) kept strictly separate from a small, capped Aggressive Alpha
sleeve (10–20%) that can fail without threatening the Core.

Every major architectural decision is pressure-tested *before code* by an automated
**[LLM Council](llm-council/)** — AI agents with deliberately conflicting mandates that debate the
decision across genuinely different models, with a calibrated Chair issuing a verdict
(BUILD / BUY / DEFER / DROP). Verdicts are logged to an Obsidian knowledge base so no decision is
ever re-argued from scratch.

## The roadmap (gated phases)
| Phase | Focus | Capital at risk |
|---|---|---|
| 0 *(current)* | Research & architecture council | Zero |
| 1 | Validate strategy edge on existing platforms (Streak / AlgoTest) | Zero (paper) |
| 2 | Build the foundation — data pipeline, backtester, Risk Guardian | Zero (paper) |
| 3 | Differentiators — sentiment & regime detection | Zero (paper) |
| 4 | Tiny live capital, treated as tuition | ₹10–25k, optional |
| 5 | Aggressive Alpha sleeve | Capped, optional |

Each phase is gated: capital is never deployed before the thing that protects it is proven on paper.
For the first ~18 months ARIA is not expected to out-trade off-the-shelf platforms — the value is
the learning, and the discipline of proving any edge honestly (walk-forward validation,
out-of-sample evidence, no curve-fitting).

## Council verdicts so far
- **Dual Barbell split → DEFER** — prototype Core/Alpha isolation and prove it in paper trading
  before committing (the council refused to accept the barbell as a narrative).
- **Custom sentiment/news engine → DEFER** — no proven retail-level alpha in free-tier sentiment
  for Indian markets; revisit only after the Core is proven, using strictly legal data sources.

## What's in this repo
- **[`llm-council/`](llm-council/)** — the automated multi-model debate engine (runs entirely on
  free LLM APIs). Usable for any project's architecture decisions, not just ARIA's. See its README.

The private research notes (decision logs, learning journal) live outside this repo by design.
**No API keys or `.env` files are ever committed** — see `.gitignore`.

## Compliance stance
ARIA trades only its builder's own capital, within all applicable regulations in both target markets:
- **India:** SEBI's retail algo-trading framework, exchange rules, and broker API terms.
- **US (as an Indian resident):** RBI's Liberalised Remittance Scheme (USD 250k/yr cap, TCS on
  remittances), W-8BEN filed for treaty tax treatment, and SEC/FINRA rules. US paper trading
  (e.g. Alpaca's free API) carries zero remittance/regulatory friction and is the Phase 1–3 path.

No managing others' money, no market-manipulative patterns, honest tax treatment in both jurisdictions.

## Data sources & research stack
- **Market data:** free-tier APIs (e.g. Alpha Vantage for US; broker WebSockets for NSE).
- **Research retrieval:** arXiv q-fin (via alphaXiv), Consensus, Elicit — feeding the council's
  evidence base.
- **LLM providers for the council:** GitHub Models, Google AI Studio, Groq, Cerebras — all free tiers.

## License
MIT — see [LICENSE](LICENSE).
