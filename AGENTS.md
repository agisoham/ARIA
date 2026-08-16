# AGENTS.md — ARIA

Repository-wide instructions for autonomous and AI-assisted development.

These guidelines apply to any coding agent (Claude Code, Codex, Gemini CLI, Cursor, Aider,
Continue, etc.) as well as human contributors where applicable.

## Non-negotiable invariants
Valuable whether the code is written by a human or an AI — these are never traded away:

- **Never introduce look-ahead bias.** Use the split helpers in `aria.validation`; never shuffle a
  time series or let a test see data from the future of the bar being decided.
- **Never expose secrets.** No keys or tokens in code or commits; read them from a gitignored
  `.env`. A gitleaks pre-commit hook enforces this.
- **Never enable live trading by default.** Live-execution code stays behind a disabled flag that
  requires an explicit, manual human step an agent cannot perform.
- **Never suppress failing tests.** Fix the code or the test — do not skip, `xfail`, or delete a
  test to make the suite green.
- **Never report backtest metrics without specifying the validation methodology** — walk-forward
  vs. purged CV, sample size, and whether the Sharpe is *deflated* for the number of trials.
- **Every new strategy requires accompanying tests and documentation** before it counts as done.
- **Never hold a stop-loss only in process memory.** Any live protective order must rest with the broker
  as a real order. A stop implemented as `if price < stop` inside a running program protects nothing the
  moment that program dies — and eventually it will. *(Blocks live execution; applies from Phase 4.)*

## Conventions
- Python 3.11+, type hints, docstrings on public functions.
- Format + lint with `ruff`. Tests with `pytest`. Every public function ships a unit test.
- A strategy is "validated" only after it passes walk-forward **and** a deflated-Sharpe check
  (`aria.metrics.deflated_sharpe_ratio`).
- **Frequency-agnostic:** never hardcode a bar frequency. Data loaders, backtester, strategy
  interfaces, and metrics take the timeframe as a parameter (e.g. `periods_per_year`), so the same
  code runs on daily bars now and minute/second bars later without a rewrite.

## Commands
- Install: `pip install -r requirements.txt`
- Test: `pytest -q`
- Lint/format: `ruff check . && ruff format .`

## Definition of done
Green tests, no look-ahead, and metrics reported honestly (deflated for the number of trials).
