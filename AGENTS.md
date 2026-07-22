# ARIA core — agent rules

## Absolute guardrails (never violate)
- NEVER place live orders, move money, or call a live broker trading endpoint.
- All trading is simulated / paper. Live-execution code lives behind a disabled flag that
  requires an explicit, manual human step the agent cannot perform.
- Never hardcode API keys. Read from the environment / a gitignored `.env`.
- No look-ahead bias: a backtest must never use data from the future of the bar being decided.
  Use the split helpers in `aria.validation`; never shuffle time series.

## Conventions
- Python 3.11+, type hints, docstrings on public functions.
- Format + lint with `ruff`. Tests with `pytest`. Every public function ships a unit test.
- A strategy is not "validated" until it passes walk-forward + a deflated-Sharpe check
  (`aria.metrics.deflated_sharpe_ratio`).

## Commands
- Install: `pip install -r requirements.txt`
- Test: `pytest -q`
- Lint/format: `ruff check . && ruff format .`

## Definition of done
Green tests, no look-ahead, and metrics reported honestly (deflated for the number of trials).
