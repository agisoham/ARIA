"""Honest experiment tracking for ARIA — the trial counter the deflated Sharpe needs.

The deflated Sharpe ratio only tells the truth if you count *every* strategy and variant you
ever tried, including the ones that failed. Human memory undercounts trials, and undercounting
silently inflates the deflated Sharpe — you end up believing a lucky winner is skill. This module
removes the temptation: every backtest / paper run is appended to a plain CSV *as you run it*, so
the trial count and the spread of Sharpes across trials are recorded honestly and feed straight
into :func:`aria.metrics.deflated_sharpe_ratio`.

Deliberately minimal and dependency-free (stdlib ``csv`` + numpy): a git-diffable CSV now,
swappable for MLflow later without changing call sites — the same prove-first, frequency-agnostic
principle as the rest of ARIA. Start logging in Phase 1, before the backtester exists; a strategy
you tried on a free platform and abandoned is still a trial.

Example
-------
    from aria.experiment_log import ExperimentLog, Run
    from aria import metrics as m

    log = ExperimentLog("experiments/runs.csv")
    log.record(Run(strategy="S1_momentum", params="fast=20,slow=50",
                   market="NSE", n_obs=1250, per_period_sharpe=0.061, oos=True, outcome="kept"))
    # ... later, evaluating the strategy you decided to keep:
    n_trials, sr_var = log.deflation_inputs()
    dsr = m.deflated_sharpe_ratio(observed_sr=0.061, n_obs=1250,
                                  sr_variance=sr_var, n_trials=n_trials)
"""
from __future__ import annotations

import csv
import os
from dataclasses import dataclass
from datetime import datetime, timezone

import numpy as np

FIELDS = [
    "run_id", "timestamp", "strategy", "params", "market", "period",
    "n_obs", "per_period_sharpe", "oos", "outcome", "notes",
]


@dataclass
class Run:
    """One recorded attempt. ``per_period_sharpe`` is the NON-annualised Sharpe (what the
    deflated Sharpe expects). Even a dropped or in-sample-only run must be recorded — it
    still consumed a trial and must deflate the eventual winner."""
    strategy: str
    params: str = ""          # e.g. "fast=20,slow=50"
    market: str = ""          # e.g. "NSE" or "US"
    period: str = ""          # e.g. "2015-2020"
    n_obs: int = 0            # number of return observations in the test window
    per_period_sharpe: float = 0.0
    oos: bool = False         # was this out-of-sample? (in-sample runs still count as trials)
    outcome: str = ""         # "kept" | "dropped" | "inconclusive"
    notes: str = ""
    run_id: str = ""          # auto-filled if blank
    timestamp: str = ""       # auto-filled (UTC) if blank


class ExperimentLog:
    """Append-only CSV log of every strategy/variant tried.

    The file is created with a header on first use. Reads are cheap; the log is meant to be
    small (one row per experiment) and human-inspectable — open it in any editor or diff it
    in git to see exactly how many trials stand behind a deflated Sharpe.
    """

    def __init__(self, path: str):
        self.path = path
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        if not os.path.exists(path):
            with open(path, "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(FIELDS)

    def record(self, run: Run) -> Run:
        """Append one run. Fills ``run_id`` and a UTC ``timestamp`` if blank. Returns the run."""
        if not run.run_id:
            run.run_id = f"r{self.trial_count() + 1:04d}"
        if not run.timestamp:
            run.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        with open(self.path, "a", newline="", encoding="utf-8") as f:
            csv.DictWriter(f, fieldnames=FIELDS).writerow({k: getattr(run, k) for k in FIELDS})
        return run

    def rows(self) -> list[dict]:
        """Every logged run as a list of dicts (in insertion order)."""
        with open(self.path, newline="", encoding="utf-8") as f:
            return list(csv.DictReader(f))

    def trial_count(self) -> int:
        """Total trials logged — the honest ``n_trials`` for the deflated Sharpe.

        Counts every run, kept or dropped. A strategy you tried and abandoned still consumed a
        trial and must deflate the winner's Sharpe; this is the number people forget.
        """
        return len(self.rows())

    def sharpe_variance(self) -> float:
        """Sample variance of the per-period Sharpes across all trials (feeds ``sr_variance``)."""
        vals = [
            float(r["per_period_sharpe"])
            for r in self.rows()
            if r.get("per_period_sharpe") not in (None, "")
        ]
        if len(vals) < 2:
            return 0.0
        return float(np.var(np.asarray(vals, dtype=float), ddof=1))

    def deflation_inputs(self) -> tuple[int, float]:
        """Convenience: ``(n_trials, sr_variance)`` ready to hand to
        :func:`aria.metrics.deflated_sharpe_ratio`."""
        return self.trial_count(), self.sharpe_variance()
