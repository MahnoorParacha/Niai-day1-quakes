import numpy as np
import pandas as pd

from quakes.cleaning import (dedupe_latest, drop_missing_target,
                             epoch_ms_to_datetime, extract_region,
                             iqr_outlier_mask, keep_earthquakes)


def test_epoch_ms_to_datetime():
    df = pd.DataFrame({"time": [1700000000000], "updated": [1700000100000]})
    out = epoch_ms_to_datetime(df)
    assert pd.api.types.is_datetime64_any_dtype(out["time"])
    assert out["time"].dt.year.iloc[0] == 2023


def test_dedupe_latest():
    df = pd.DataFrame({"id": ["a", "a", "b"], "updated": [1, 2, 1],
                       "mag": [1.0, 2.0, 3.0]})
    out = dedupe_latest(df)
    assert len(out) == 2
    assert out.loc[out["id"] == "a", "mag"].iloc[0] == 2.0


def test_keep_earthquakes():
    df = pd.DataFrame({"type": [" Earthquake", "explosion", "earthquake"]})
    assert len(keep_earthquakes(df)) == 2


def test_extract_region():
    s = pd.Series(["10 km SW of Ridgecrest, CA", "Mid-Atlantic Ridge", "Tonga"])
    assert extract_region(s).tolist() == ["CA", "Mid-Atlantic Ridge", "Tonga"]


def test_iqr_outlier_mask():
    mask = iqr_outlier_mask(pd.Series([1, 2, 3, 4, 5, 100]))
    assert mask.sum() == 1 and mask.iloc[-1]


def test_drop_missing_target():
    out = drop_missing_target(pd.DataFrame({"mag": [1.0, np.nan]}))
    assert len(out) == 1
