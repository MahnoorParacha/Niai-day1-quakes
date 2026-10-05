import numpy as np
import pandas as pd

from quakes.features import (add_quality_features, add_target, add_time_features,
                             drop_leaky_columns, group_rare)


def test_time_features():
    df = pd.DataFrame({"time": pd.to_datetime([1700000000000], unit="ms", utc=True)})
    out = add_time_features(df)
    assert out["hour"].iloc[0] == 22 and out["dayofweek"].iloc[0] == 1


def test_quality_features():
    t = pd.Timestamp("2023-11-14", tz="UTC")
    df = pd.DataFrame({"time": [t], "updated": [t + pd.Timedelta(hours=2)],
                       "status": ["reviewed"], "nst": [np.nan]})
    out = add_quality_features(df)
    assert out["update_lag_hours"].iloc[0] == 2.0
    assert out["is_reviewed"].iloc[0] == 1 and out["nst_missing"].iloc[0] == 1


def test_group_rare():
    s = pd.Series(["a"] * 5 + ["b"] * 2 + ["c"])
    assert set(group_rare(s, top_k=1)) == {"a", "Other"}


def test_add_target():
    out = add_target(pd.DataFrame({"mag": [4.4, 4.5, 6.0]}))
    assert out["big_quake"].tolist() == [0, 1, 1]


def test_drop_leaky_columns():
    cols = ["title", "sig", "mmi", "cdi", "felt", "alert", "depth_km"]
    out = drop_leaky_columns(pd.DataFrame({c: [1] for c in cols}))
    assert list(out.columns) == ["depth_km"]
