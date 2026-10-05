"""Task 5: run the whole pipeline end to end.

Steps (see LAB_GUIDE.md):
 1. fetch all_week (fall back to config.FALLBACK_PATH if the network fails)
 2. merge any data/stream/*.jsonl rows, then dedupe_latest
 3. clean, engineer features, drop leaky columns
 4. split, fit_transform on train only, transform test
 5. print the report, save train.csv, test.csv, preprocessor.joblib
"""
import argparse
import json

import joblib
import pandas as pd

from . import config
from .cleaning import clean, dedupe_latest
from .features import (
    add_location_features,
    add_quality_features,
    add_target,
    add_time_features,
    drop_leaky_columns,
    group_rare,
)
from .fetch import fetch_feed, geojson_to_df
from .transform import build_preprocessor, split_data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scaler", default="robust",
                        choices=["standard", "minmax", "robust"])
    args = parser.parse_args()

    # 1. fetch (fall back to the saved file if the network fails)
    try:
        payload = fetch_feed("all_week")
    except Exception as e:
        print(f"Fetch failed ({e}); using fallback file")
        with open(config.FALLBACK_PATH, encoding="utf-8") as f:
            payload = json.load(f)
    raw = geojson_to_df(payload)

    # 2. merge stream rows, then keep the latest version of each event
    stream_files = sorted(config.STREAM_DIR.glob("*.jsonl"))
    stream_rows = 0
    combined = raw
    if stream_files:
        stream = pd.concat(
            [pd.read_json(p, lines=True, convert_dates=False, dtype=False)
             for p in stream_files],
            ignore_index=True,
        )
        stream_rows = len(stream)
        combined = pd.concat([raw, stream], ignore_index=True)

    versions = combined.groupby("id")["updated"].nunique()
    events_changed = int((versions > 1).sum())
    combined = dedupe_latest(combined)

    # 3. clean, engineer features, drop leaky columns
    df = clean(combined)
    rows_after_cleaning = len(df)
    df = add_time_features(df)
    df = add_quality_features(df)
    df = add_location_features(df)
    df = add_target(df)
    df["region"] = group_rare(df["region"], top_k=15)
    df = drop_leaky_columns(df)

    # 4. split, then fit the preprocessor on train only
    X_train, X_test, y_train, y_test = split_data(df)
    pre = build_preprocessor(args.scaler)
    Xt_train = pre.fit_transform(X_train)
    Xt_test = pre.transform(X_test)
    if hasattr(Xt_train, "toarray"):
        Xt_train, Xt_test = Xt_train.toarray(), Xt_test.toarray()

    # 5. report and save
    print("---- Report ----")
    print(f"Raw rows (API):              {len(raw)}")
    print(f"Stream rows merged:          {stream_rows}")
    print(f"Events whose updated changed: {events_changed}")
    print(f"Rows after cleaning:         {rows_after_cleaning}")
    print(f"Train shape: {Xt_train.shape}   Test shape: {Xt_test.shape}")
    print(f"Positive rate  train: {y_train.mean():.3f}   test: {y_test.mean():.3f}")

    cols = pre.get_feature_names_out()
    train = pd.DataFrame(Xt_train, columns=cols, index=X_train.index)
    train[config.TARGET] = y_train
    test = pd.DataFrame(Xt_test, columns=cols, index=X_test.index)
    test[config.TARGET] = y_test

    config.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    train.to_csv(config.PROCESSED_DIR / "train.csv", index=False)
    test.to_csv(config.PROCESSED_DIR / "test.csv", index=False)
    joblib.dump(pre, config.PROCESSED_DIR / "preprocessor.joblib")
    print(f"Saved train.csv, test.csv, preprocessor.joblib to {config.PROCESSED_DIR}")


if __name__ == "__main__":
    main()