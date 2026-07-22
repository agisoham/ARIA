import numpy as np

from aria import metrics as m


def test_max_drawdown_known_series():
    # equity: 1.0 -> 1.1 -> 0.88 ; trough is 0.88/1.1 - 1 = -0.2
    md = m.max_drawdown([0.10, -0.20])
    assert abs(md - (-0.2)) < 1e-12


def test_sharpe_sign_and_zero_variance():
    up = np.full(300, 0.001)  # constant -> zero variance -> undefined -> 0.0
    assert m.sharpe_ratio(up) == 0.0
    rng = np.random.default_rng(0)
    good = rng.normal(0.001, 0.01, 2000)   # positive drift
    bad = rng.normal(-0.001, 0.01, 2000)   # negative drift
    assert m.sharpe_ratio(good) > 0
    assert m.sharpe_ratio(bad) < 0


def test_psr_bounds_and_monotonicity():
    # zero observed vs zero benchmark -> exactly 0.5
    assert abs(m.probabilistic_sharpe_ratio(0.0, 1000) - 0.5) < 1e-9
    # a strong per-period Sharpe over a long record -> near-certain
    strong = m.probabilistic_sharpe_ratio(0.15, 2000)
    weak = m.probabilistic_sharpe_ratio(0.02, 50)
    assert strong > 0.99
    assert 0.0 <= weak <= 1.0
    assert strong > weak  # more evidence -> higher confidence


def test_deflation_is_stricter_than_psr():
    # deflating for many trials must never make the strategy look *better*
    sr, n = 0.10, 1500
    psr = m.probabilistic_sharpe_ratio(sr, n)
    dsr = m.deflated_sharpe_ratio(sr, n, sr_variance=0.0025, n_trials=50)
    assert 0.0 <= dsr <= 1.0
    assert dsr <= psr + 1e-12


def test_summary_keys():
    rng = np.random.default_rng(1)
    r = rng.normal(0.0005, 0.01, 500)
    s = m.summary(r)
    for k in ("cagr", "ann_vol", "sharpe", "sortino", "max_drawdown", "calmar", "psr_vs_zero"):
        assert k in s
