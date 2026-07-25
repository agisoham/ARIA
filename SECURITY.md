# Security policy

ARIA is a personal research project, but it touches API keys and (eventually) brokerage accounts, so
secret hygiene and execution safety are treated as engineering requirements rather than good intentions.

## Reporting a vulnerability

Found a leaked credential, an unsafe default, or a way to make the system place an order it shouldn't?
Please **open a GitHub issue** describing the problem — or, if it involves an exposed secret, avoid
posting the value itself and say only where it appears so it can be rotated first.

There's no bounty; this is a solo learning project. Reports are still very welcome.

## How secrets are handled

- **Nothing real is committed.** `.env` files are gitignored (`.env`, `*.env`, with only
  `.env.example` allowed through), and private strategy topics are excluded by default —
  `llm-council/topics/*` is ignored except the neutral template.
- **A pre-commit hook runs [gitleaks](https://github.com/gitleaks/gitleaks)** (entropy + heuristics) so a
  key can't be committed by accident. See `.pre-commit-config.yaml`.
- **A second scanner runs before publishing.** The publish/sync tooling refuses to proceed if anything
  key-shaped appears in the staged files.
- **Keys are per-provider, free-tier, and rotatable.** Any credential that has ever appeared outside a
  local `.env` — including in a chat window or a screenshot — is treated as compromised and rotated.

If you fork this repo: copy `llm-council/.env.example` to `.env` and fill in your own keys. Never commit
that file.

## Execution safety (why this repo can't lose your money)

These are enforced constraints, not aspirations — the full list lives in [`AGENTS.md`](AGENTS.md):

- **No live trading by default**, ever. Live execution is opt-in, human-gated, and only reachable after
  the paper-trading gates pass.
- **LLMs never place trades.** The AI council debates *design*; deterministic, tested code produces
  signals. No agent has an order-placement path.
- **No agent may write to a broker API.** An AI coding agent working on this repo is blocked from
  money-moving commands by hook-level guardrails, not by prompt instructions alone.
- **Kill-switch first.** The Risk Guardian (drawdown limits, VaR/CVaR, stop-loss, kill-switch) is a
  Phase-2 prerequisite — it is built *before* any capital is deployed, not after.

## Scope

This project trades only its author's own capital. It does not manage third-party money, and nothing in
this repository is financial advice.
