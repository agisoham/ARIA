"""Does the anti-overfit harness actually work? A 40-line proof you can run.

The claim ARIA makes everywhere is: *a good-looking backtest is usually luck, and the deflated
Sharpe ratio catches it.* This script demonstrates that claim instead of asserting it.

The setup is the classic backtest trap, in miniature:

1. Generate `N_TRIALS` strategies that are **pure noise** — random returns with *zero* true edge.
   By construction, none of them can predict anything.
2. Do what an overfitting researcher does: keep **the best one** by Sharpe ratio.
3. Report the naive Sharpe (looks impressive!) next to the **deflated** Sharpe, which knows you
   tried `N_TRIALS` times and raises the bar to the Sharpe you'd expect from luck alone.

The honest metric should conclude: *no skill here.* Run it:

    python examples/overfitting_demo.py
"""
from __future__ import annotations

import numpy as np

from aria import metrics as m
from aria.experiment_log import ExperimentLog, Run

N_TRIALS = 200        # how many strategies we "tried"
N_DAYS = 1000         # length of each track record (~4 years of daily bars)
TRUE_EDGE = 0.0       # zero. none of these strategies has any real edge.
SEED = 7


def main() -> None:
    rng = np.random.default_rng(SEED)

    # 1. N_TRIALS strategies of pure noise — zero true edge, by construction.
    trials = rng.normal(TRUE_EDGE, 0.01, size=(N_TRIALS, N_DAYS))

    # Log every single one, winners and losers alike — this is what makes the trial count honest.
    log = ExperimentLog("examples/_demo_runs.csv")
    per_period = []
    for i, returns in enumerate(trials):
        sr = float(returns.mean() / returns.std(ddof=1))
        per_period.append(sr)
        log.record(Run(strategy=f"noise_{i:03d}", per_period_sharpe=sr, n_obs=N_DAYS,
                       outcome="dropped", notes="synthetic; no true edge"))

    # 2. Keep the best-looking one — exactly what overfitting looks like in practice.
    best = int(np.argmax(per_period))
    best_returns = trials[best]

    # 3. Judge it honestly.
    naive_sharpe = m.sharpe_ratio(best_returns)                 # annualised — the headline number
    psr = m.probabilistic_sharpe_ratio(per_period[best], N_DAYS)  # vs a zero benchmark
    n_trials, sr_var = log.deflation_inputs()                   # the honest trial count
    dsr = m.deflated_sharpe_ratio(per_period[best], N_DAYS, sr_var, n_trials)

    print(f"Tried {N_TRIALS} strategies of pure noise (true edge = {TRUE_EDGE}).\n")
    print(f"  Best annualised Sharpe   : {naive_sharpe: .2f}   <- looks like a real strategy")
    print(f"  PSR (ignores trial count): {psr: .3f}   <- 'significant!' if you forget you cherry-picked")
    print(f"  Trials actually run      : {n_trials}")
    print(f"  DEFLATED Sharpe (honest) : {dsr: .3f}   <- accounts for {n_trials} tries\n")

    verdict = "correctly refuses to call it skill" if dsr < 0.95 else "FAILED to catch the overfit"
    print(f"Verdict: the deflated Sharpe {verdict}.")
    print("The naive number is luck dressed up as edge. That gap is the whole point of the harness.")


if __name__ == "__main__":
    main()
