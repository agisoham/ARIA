"""Leakage-free validation splits for time-series strategies.

A backtest that trains and tests on overlapping or shuffled time is worthless — it leaks
the future into the past. This module provides:

- `walk_forward_splits`: expanding (or rolling) train windows, each tested on the *next*
  out-of-sample block. This is the honest way to evaluate a strategy over time.
- `purged_kfold_splits`: López de Prado's purged K-fold with an embargo, which drops the
  training samples adjacent to each test fold so overlapping labels can't leak.

Both yield `(train_idx, test_idx)` numpy arrays and never let a test index precede its
train set improperly.
"""
from __future__ import annotations

from collections.abc import Iterator

import numpy as np


def walk_forward_splits(
    n_samples: int, n_splits: int = 5, expanding: bool = True,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """Yield `(train_idx, test_idx)` where every test block strictly follows its train set.

    The timeline is cut into `n_splits + 1` equal blocks; block *i* trains on everything
    before it and tests on block *i*. `expanding=True` grows the train window each step;
    `False` uses a fixed-size rolling window.
    """
    if n_splits < 1:
        raise ValueError("n_splits must be >= 1")
    fold = n_samples // (n_splits + 1)
    if fold == 0:
        raise ValueError("too few samples for the requested number of splits")

    for i in range(1, n_splits + 1):
        test_start = i * fold
        test_end = (i + 1) * fold if i < n_splits else n_samples
        train_start = 0 if expanding else (i - 1) * fold
        train_idx = np.arange(train_start, test_start)
        test_idx = np.arange(test_start, test_end)
        yield train_idx, test_idx


def purged_kfold_splits(
    n_samples: int, n_splits: int = 5, embargo: float = 0.01,
) -> Iterator[tuple[np.ndarray, np.ndarray]]:
    """Purged K-fold with an embargo (López de Prado).

    Each contiguous fold is the test set; the training set is every other index EXCEPT a
    band of width `embargo * n_samples` around the test fold (purge + embargo), which
    prevents overlapping-label leakage between adjacent train/test samples.
    """
    if n_splits < 2:
        raise ValueError("n_splits must be >= 2")
    indices = np.arange(n_samples)
    emb = round(n_samples * embargo)
    bounds = np.linspace(0, n_samples, n_splits + 1, dtype=int)

    for k in range(n_splits):
        start, end = bounds[k], bounds[k + 1]
        test_idx = indices[start:end]
        lo, hi = max(0, start - emb), min(n_samples, end + emb)
        mask = np.ones(n_samples, dtype=bool)
        mask[lo:hi] = False  # drop the test fold + embargo band on both sides
        train_idx = indices[mask]
        yield train_idx, test_idx
