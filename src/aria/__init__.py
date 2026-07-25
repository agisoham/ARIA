"""ARIA core — survivability-first quant tooling.

Built prover-first: the validation harness and honest metrics come before any strategy.

    from aria import sharpe_ratio, deflated_sharpe_ratio, walk_forward_splits
"""
from aria.experiment_log import ExperimentLog, Run
from aria.metrics import (
    annualized_volatility,
    cagr,
    calmar_ratio,
    deflated_sharpe_ratio,
    expected_max_sharpe,
    max_drawdown,
    probabilistic_sharpe_ratio,
    sharpe_ratio,
    sortino_ratio,
    summary,
)
from aria.validation import purged_kfold_splits, walk_forward_splits

__version__ = "0.1.0"

__all__ = [
    "ExperimentLog",
    "Run",
    "annualized_volatility",
    "cagr",
    "calmar_ratio",
    "deflated_sharpe_ratio",
    "expected_max_sharpe",
    "max_drawdown",
    "probabilistic_sharpe_ratio",
    "purged_kfold_splits",
    "sharpe_ratio",
    "sortino_ratio",
    "summary",
    "walk_forward_splits",
]
