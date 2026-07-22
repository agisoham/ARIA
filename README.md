# ARIA — Adaptive Responsive Intelligence Architecture

**A solo-built algorithmic trading system for Indian and US markets, engineered survivability-first.**
Primary goal: learning ML, quantitative finance, and systems engineering deeply. Hard rule: never
lose money. Earning is a genuine goal too — strictly within SEBI regulations, exchange rules, and
broker terms.

> *Debate before you build. Prove before you risk. Protect the Core, always.*

## Philosophy
ARIA rejects the "predict the market" framing in favour of **manage uncertainty and survive**. The
architecture is a **Dual Barbell**: a conservative Core (~70% of any deployed capital, built for
survivability and steady compounding) kept strictly separate from a capped Aggressive Alpha
sleeve (~30%) that can fail without threatening the Core.

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
| 3 | Differentiators — regime detection (news/sentiment deferred pending proven edge) | Zero (paper) |
| 4 | Tiny live capital, treated as tuition | Small, optional |
| 5 | Aggressive Alpha sleeve | Capped, optional |

Each phase is gated: capital is never deployed before the thing that protects it is proven on paper.
For the first ~18 months ARIA is not expected to out-trade off-the-shelf platforms — the value is
the learning, and the discipline of proving any edge honestly (walk-forward validation,
out-of-sample evidence, no curve-fitting).

## Council verdicts so far
The council is deliberately hard to convince — most ideas are deferred until there's evidence, not
adopted on a story. Highlights (full log in [docs/decisions.md](docs/decisions.md)):
- **Dual Barbell structure → DEFER** — prove Core/Alpha isolation in a paper-traded prototype first.
- **Barbell ratio & sizing → DEFER (capped pilot)** — don't lock a number; run a small, reversible
  pilot, with the Alpha sleeve as a hard *cap* and fractional-Kelly sizing deployment within it.
- **Crisis stress-test library → DEFER** — the two-layer screening *reversed its own earlier BUILD*
  once it caught that free, realistic crisis-era data may not exist; audit the data first.
- **Sentiment/news engine, stat-arb, options-pricing, order-book simulator → DEFER**, each with a
  concrete next step; **ML-trained-on-crises → DROP** (tiny sample, overfitting trap).

The reversal is the whole point: a second screening layer exists to catch the first layer's blind spots.

## Documentation
A public wiki lives in [`docs/`](docs/):
- [Methodology](docs/methodology.md) — the LLM Council & two-layer screening (the interesting part).
- [Philosophy](docs/philosophy.md) — goals, the Dual Barbell, the survive-don't-predict stance.
- [Roadmap](docs/roadmap.md) — the gated phases and their exit gates.
- [Decision log](docs/decisions.md) — every council verdict, dated.
- [Safe agentic development](docs/agentic-safety.md) — how an AI coding agent builds this without ever being able to touch real money.

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
