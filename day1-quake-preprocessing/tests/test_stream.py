import pandas as pd

from quakes.stream import filter_unseen


def test_filter_unseen():
    df = pd.DataFrame({"id": ["a", "b"], "updated": [1, 1]})
    seen = {("a", 1)}
    out = filter_unseen(df, seen)
    assert out["id"].tolist() == ["b"]
    assert seen == {("a", 1), ("b", 1)}
