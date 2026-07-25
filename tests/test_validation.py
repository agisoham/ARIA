import numpy as np

from aria import validation as v


def test_walk_forward_no_leakage_and_growth():
    prev_train = -1
    for train, test in v.walk_forward_splits(100, n_splits=4, expanding=True):
        assert train.size > 0 and test.size > 0
        assert train.max() < test.min()          # test is strictly in the future of train
        assert np.intersect1d(train, test).size == 0  # no overlap
        assert train.size > prev_train            # expanding window grows
        prev_train = train.size


def test_walk_forward_rolling_is_fixed_width():
    widths = {len(train) for train, _ in v.walk_forward_splits(100, n_splits=4, expanding=False)}
    assert len(widths) == 1  # rolling window keeps a constant train size


def test_purged_kfold_embargo_removes_adjacent_train():
    n, emb = 100, 0.05
    for train, test in v.purged_kfold_splits(n, n_splits=5, embargo=emb):
        assert np.intersect1d(train, test).size == 0
        band = round(n * emb)
        # no training index may fall inside the embargo band around the test fold
        lo, hi = test.min() - band, test.max() + band
        assert not np.any((train >= lo) & (train <= hi))


def test_purged_kfold_covers_all_test_indices():
    n = 100
    seen = np.concatenate([test for _, test in v.purged_kfold_splits(n, n_splits=5)])
    assert np.array_equal(np.sort(seen), np.arange(n))  # folds partition the data
