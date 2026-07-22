"""Honest performance metrics for ARIA.

The point of this module is not to make a strategy look good — it's to make it hard to
fool yourself. Alongside the usual Sharpe/drawdown numbers it implements the
**Probabilistic** and **Deflated** Sharpe ratios (López de Prado), which answer the
question every quant review asks: *given how many strategies you tried, is this Sharpe
actually distinguishable from luck?*

All inputs are simple period returns (e.g. daily), as a sequence or numpy array.
No look-ahead, no external data — pure functions, fully unit-tested.
"""
from __future__ import annotations

from statistics import NormalDist

import numpy as np

_N = NormalDist()  # standard normal; stdlib, no scipy dependency
_EULER = 0.5772156649015329  # Euler–Mascheroni constant
_EPS = 1e-12  # treat a standard deviation below this as effectively zero (constant series)


def _arr(returns) -> np.ndarray:
    return np.asarray(returns, dtype=float).ravel()


# --------------------------------------------------------------------------- #
# Core metrics
# --------------------------------------------------------------------------- #

def cagr(returns, periods_per_year: int = 252) -> float:
    """Compound annual growth rate from period returns."""
    r = _arr(returns)
    if r.size == 0:
        return 0.0
    growth = float(np.prod(1.0 + r))
    years = r.size / periods_per_year
    if years <= 0 or growth <= 0:
        return 0.0
    return growth ** (1.0 / years) - 1.0


def annualized_volatility(returns, periods_per_year: int = 252) -> float:
    r = _arr(returns)
    if r.size < 2:
        return 0.0
    return float(r.std(ddof=1) * np.sqrt(periods_per_year))


def sharpe_ratio(returns, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    """Annualised Sharpe ratio. `risk_free` is an annual rate."""
    r = _arr(returns)
    if r.size < 2:
        return 0.0
    excess = r - risk_free / periods_per_year
    sd = excess.std(ddof=1)
    if not np.isfinite(sd) or sd < _EPS:
        return 0.0
    return float(np.sqrt(periods_per_year) * excess.mean() / sd)


def sortino_ratio(returns, risk_free: float = 0.0, periods_per_year: int = 252) -> float:
    """Like Sharpe but penalises only downside deviation."""
    r = _arr(returns)
    if r.size < 2:
        return 0.0
    excess = r - risk_free / periods_per_year
    downside = excess[excess < 0]
    dd = np.sqrt(np.mean(downside ** 2)) if downside.size else 0.0
    if not np.isfinite(dd) or dd < _EPS:
        return 0.0
    return float(np.sqrt(periods_per_year) * excess.mean() / dd)


def max_drawdown(returns) -> float:
    """Largest peak-to-trough decline of the equity curve. Returned as a negative fraction."""
    r = _arr(returns)
    if r.size == 0:
        return 0.0
    equity = np.cumprod(1.0 + r)
    peak = np.maximum.accumulate(equity)
    drawdown = equity / peak - 1.0
    return float(drawdown.min())


def calmar_ratio(returns, periods_per_year: int = 252) -> float:
    """CAGR divided by the magnitude of the max drawdown."""
    mdd = abs(max_drawdown(returns))
    if mdd == 0:
        return 0.0
    return cagr(returns, periods_per_year) / mdd


# --------------------------------------------------------------------------- #
# Overfit-aware Sharpe (López de Prado)
# --------------------------------------------------------------------------- #

def _per_period_sharpe(returns) -> float:
    """Non-annualised Sharpe (per observation) — the input PSR/DSR expect."""
    r = _arr(returns)
    if r.size < 2:
        return 0.0
    sd = r.std(ddof=1)
    return 0.0 if (not np.isfinite(sd) or sd < _EPS) else float(r.mean() / sd)


def probabilistic_sharpe_ratio(
    observed_sr: float, n_obs: int, benchmark_sr: float = 0.0,
    skew: float = 0.0, kurtosis: float = 3.0,
) -> float:
    """P(true Sharpe > benchmark). `observed_sr`/`benchmark_sr` are PER-PERIOD Sharpes.

    Corrects the Sharpe estimate for track-record length, skew and (excess) kurtosis.
    Returns a probability in [0, 1]. > 0.95 is the usual bar for "real".
    """
    if n_obs < 2:
        return 0.0
    denom = np.sqrt(1.0 - skew * observed_sr + (kurtosis - 1.0) / 4.0 * observed_sr ** 2)
    if denom <= 0:
        return 0.0
    z = (observed_sr - benchmark_sr) * np.sqrt(n_obs - 1) / denom
    return float(_N.cdf(z))


def expected_max_sharpe(sr_variance: float, n_trials: int) -> float:
    """Expected maximum PER-PERIOD Sharpe from `n_trials` independent strategies under the
    null of zero true skill — the deflation benchmark. `sr_variance` is the variance of the
    Sharpe estimates across those trials."""
    if n_trials < 2 or sr_variance <= 0:
        return 0.0
    e = np.e
    q1 = _N.inv_cdf(1.0 - 1.0 / n_trials)
    q2 = _N.inv_cdf(1.0 - 1.0 / (n_trials * e))
    return float(np.sqrt(sr_variance) * ((1.0 - _EULER) * q1 + _EULER * q2))


def deflated_sharpe_ratio(
    observed_sr: float, n_obs: int, sr_variance: float, n_trials: int,
    skew: float = 0.0, kurtosis: float = 3.0,
) -> float:
    """Probabilistic Sharpe deflated by the number of strategies tried.

    This is the honest answer to "is this backtest overfit?": it raises the benchmark to
    the Sharpe you'd expect to see *by luck* after trying `n_trials` strategies.
    `observed_sr` is the PER-PERIOD Sharpe of the chosen strategy.
    """
    sr0 = expected_max_sharpe(sr_variance, n_trials)
    return probabilistic_sharpe_ratio(observed_sr, n_obs, sr0, skew, kurtosis)


def summary(returns, periods_per_year: int = 252) -> dict:
    """One honest performance snapshot."""
    return {
        "cagr": cagr(returns, periods_per_year),
        "ann_vol": annualized_volatility(returns, periods_per_year),
        "sharpe": sharpe_ratio(returns, periods_per_year=periods_per_year),
        "sortino": sortino_ratio(returns, periods_per_year=periods_per_year),
        "max_drawdown": max_drawdown(returns),
        "calmar": calmar_ratio(returns, periods_per_year),
        "psr_vs_zero": probabilistic_sharpe_ratio(_per_period_sharpe(returns), _arr(returns).size),
    }
