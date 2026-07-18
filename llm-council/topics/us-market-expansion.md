seats: quant, risk, systems, pragmatist, advocate, compliance

Should ARIA target US markets alongside Indian markets — and if so, in which phase?

Context researched 2026-07-19 (verify before relying):
- Access for an Indian resident: RBI LRS caps outward remittance at USD 250k/yr; ~20% TCS
  applies on large remittances (threshold ~₹7-10L, reclaimable via ITR). Money must actually
  leave India to fund a US broker — this is real friction and cost for small capital.
- Tax: with W-8BEN filed, US capital gains for Indian residents are taxed 0% in the US
  (taxed in India instead); dividends face 25% treaty withholding.
- Regulation: SEC approved eliminating the Pattern Day Trader rule (effective June 2026,
  brokers have until Oct 2027 to implement) — the old $25k day-trading floor is going away.
- Tooling: Alpaca offers commission-free US equities trading with an API-first design and
  UNLIMITED FREE PAPER TRADING (no funding needed, available internationally) — arguably
  better free algo infrastructure than anything available for NSE. IBKR has the most complete
  API but more friction.
- ARIA's Phase 1 platforms (Streak/AlgoTest) are India-only; a US leg would validate on
  Alpaca paper instead.

Weigh specifically:
- Does a US paper-trading leg (zero capital, zero LRS/TCS friction) belong in Phases 1-3,
  with real-money US deployment deferred to Phase 4+ when capital justifies remittance costs?
- Diversification value of two uncorrelated markets vs. doubled complexity for a solo builder
  (two data pipelines, two brokers, two regulatory regimes, currency risk).
- Does US-market data quality/tooling (free, API-first) actually accelerate the LEARNING goal
  faster than India-only?
- Currency/remittance drag on small capital: does real-money US trading ever make sense below
  a few lakh of deployable capital?
- What does this do to the deferred Dual Barbell prototype — one barbell across markets, or
  one per market?
