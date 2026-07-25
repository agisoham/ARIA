import numpy as np

from aria.experiment_log import ExperimentLog, Run
from aria import metrics as m


def test_counts_every_trial_kept_or_dropped(tmp_path):
    log = ExperimentLog(str(tmp_path / "runs.csv"))
    log.record(Run(strategy="S1", params="fast=20,slow=50", per_period_sharpe=0.06, outcome="kept"))
    log.record(Run(strategy="S1", params="fast=10,slow=30", per_period_sharpe=0.01, outcome="dropped"))
    log.record(Run(strategy="S2", params="rsi=14", per_period_sharpe=0.03, outcome="dropped"))
    # a dropped trial still counts — this is the number people forget
    assert log.trial_count() == 3


def test_auto_ids_and_persistence(tmp_path):
    path = str(tmp_path / "runs.csv")
    log = ExperimentLog(path)
    r1 = log.record(Run(strategy="S1", per_period_sharpe=0.05))
    r2 = log.record(Run(strategy="S2", per_period_sharpe=0.02))
    assert (r1.run_id, r2.run_id) == ("r0001", "r0002")
    assert r1.timestamp.endswith("Z")
    # a fresh handle on the same file sees the same history (append-only, durable)
    assert ExperimentLog(path).trial_count() == 2


def test_header_written_once(tmp_path):
    path = str(tmp_path / "runs.csv")
    ExperimentLog(path)
    ExperimentLog(path).record(Run(strategy="S1", per_period_sharpe=0.04))
    with open(path, encoding="utf-8") as f:
        lines = [ln for ln in f.read().splitlines() if ln.strip()]
    assert lines[0].startswith("run_id,")
    assert sum(ln.startswith("run_id,") for ln in lines) == 1  # header not duplicated


def test_deflation_inputs_feed_metrics(tmp_path):
    log = ExperimentLog(str(tmp_path / "runs.csv"))
    for sr in (0.06, 0.01, 0.03, -0.02):
        log.record(Run(strategy="v", per_period_sharpe=sr))
    n_trials, sr_var = log.deflation_inputs()
    assert n_trials == 4
    assert abs(sr_var - float(np.var([0.06, 0.01, 0.03, -0.02], ddof=1))) < 1e-12
    # the honest wiring: more trials -> higher deflation benchmark -> lower deflated Sharpe
    dsr_many = m.deflated_sharpe_ratio(0.06, 1500, sr_var, n_trials=50)
    dsr_few = m.deflated_sharpe_ratio(0.06, 1500, sr_var, n_trials=2)
    assert dsr_few > dsr_many


def test_variance_needs_two_points(tmp_path):
    log = ExperimentLog(str(tmp_path / "runs.csv"))
    log.record(Run(strategy="only-one", per_period_sharpe=0.05))
    assert log.sharpe_variance() == 0.0
