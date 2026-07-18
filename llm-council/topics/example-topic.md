seats: quant, risk, systems, pragmatist, advocate, nlp, compliance

Should ARIA build a custom market-event sentiment & news engine as a Phase 3 differentiator?

Scope: ingest X/Twitter, Truth Social, and general financial news to detect market-moving
events (macro shocks, policy/tariff headlines, major-company news) and feed them as signals
or filters into Core ARIA's strategies.

Weigh specifically:
- Free-tier data reality: X/Twitter and Truth Social API access costs and Terms-of-Service
  limits; which sources are actually free/legal to pull (official news APIs, RSS).
- Build-vs-buy: FinBERT and off-the-shelf sentiment vs a custom pipeline; do Streak/AlgoTest
  already cover any of this?
- Evidence: can we measure whether sentiment/news signals materially beat plain Core ARIA on
  paper results — and how would we avoid overfitting to noise?
- Solo-builder feasibility on free tooling, and the "never lose money" + SEBI constraints.
- Given the Dual Barbell was just DEFERRED pending a prototype, does this belong before or
  after that proof?
