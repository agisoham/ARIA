# Contributing to ARIA

ARIA is a solo, survivability-first research project — but it's built to be legible to
outsiders, and clarity for a hypothetical contributor is clarity for the author too. This
file is that forcing function. External PRs aren't expected yet; issues and questions are
welcome.

## Ground rules (non-negotiable)

These are the invariants from [`AGENTS.md`](AGENTS.md). Any change — human or AI-authored —
must hold them:

- Never introduce look-ahead bias.
- Never expose secrets (`.env`, keys, tokens).
- Never enable live trading by default.
- Never suppress failing tests.
- Never report a backtest metric without stating the validation methodology.
- Every new strategy needs accompanying tests and documentation.

If a change can't satisfy these, it doesn't go in.

## Run the tests

```bash
pip install -e .            # or: pip install numpy pytest
pytest -q
```

Everything in `src/aria/` is pure and unit-tested; a green suite is the bar for any change to it.

## Run the council on a new topic

The council debates a *design decision* — it never trades. To pose a new one:

1. Copy the template:
   ```bash
   cp llm-council/topics/_template.md llm-council/topics/my-question.md
   ```
   (Files under `topics/` are gitignored except the template — real strategy topics stay
   private. See [`examples/example-debate.md`](llm-council/examples/example-debate.md) for the
   shape a finished debate takes.)
2. Write the decision and, optionally, a `seats:` line to pick the panel
   (`quant, risk, systems, pragmatist, advocate, nlp, compliance, futureproof`).
3. Run it:
   ```bash
   cd llm-council
   export GITHUB_TOKEN=...          # a free GitHub Models token is enough
   python council.py --topic-file topics/my-question.md --rounds 2
   ```
   The verdict — Layer 1 (debate → Critic → calibrated Chair) plus Layer 2 (bias audit → red
   team → confirm/revise) — is written to your Codex. Add `--layer1-only` to skip Layer 2 on
   quota-tight days.

See [`llm-council/README.md`](llm-council/README.md) for the full flag list and the free keys.

## Experiment logging (please, always)

If you add or evaluate a strategy variant, record it with `aria.experiment_log` **as you run
it** — including the ones that don't work. The deflated Sharpe is only honest if the trial
count is complete; an unlogged failed variant is a lie of omission that inflates the winner.

## Style

- Python ≥ 3.11, `ruff` line-length 100, standard-library-first (numpy is the only runtime dep).
- Pure functions where possible; no network or file I/O inside metric/validation code.
- Docstrings explain *why*, not just *what* — this is a learning project.
