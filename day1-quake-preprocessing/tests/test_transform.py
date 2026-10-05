import numpy as np
import pandas as pd

from quakes import config
from quakes.transform import build_preprocessor, split_data


def make_df(n=200):
    rng = np.random.default_rng(0)
    d = {c: rng.normal(size=n) for c in config.NUMERIC}
    for c in config.NOMINAL:
        d[c] = rng.choice(["a", "b", "c"], n)
    d["mag"] = rng.uniform(0, 7, n)
    d["big_quake"] = (rng.random(n) < 0.3).astype(int)
    df = pd.DataFrame(d)
    df.loc[:10, config.NUMERIC[0]] = np.nan
    return df


def test_split_excludes_targets_and_stratifies():
    X_train, X_test, y_train, y_test = split_data(make_df())
    assert "mag" not in X_train.columns and "big_quake" not in X_train.columns
    assert abs(y_train.mean() - y_test.mean()) < 0.05


def test_preprocessor_outputs_clean_matrix():
    X_train, X_test, _, _ = split_data(make_df())
    pre = build_preprocessor()
    Xtr, Xte = pre.fit_transform(X_train), pre.transform(X_test)
    assert not np.isnan(Xtr).any() and not np.isnan(Xte).any()
    assert Xtr.shape[0] == len(X_train) and Xte.shape[0] == len(X_test)
