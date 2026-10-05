# Day 1 Lab: Live Earthquake Data → Model-Ready Dataset

**NIAI AI/ML Program · Module 3 · Data Preprocessing and Feature Engineering**
**Trainer:** Anique Atique Alam

## Goal
Turn the live USGS earthquake feed into a model-ready dataset for predicting `big_quake` (magnitude ≥ 4.5), with no leakage. You write the code. The tests tell you when each piece works.

Your output (`data/processed/`) is reused on Day 3 (regression on `mag`) and Day 4 (classification of `big_quake`).

## Setup (10 min)
```bash
conda env create -f environment.yml
conda activate niai-ml
pytest            # everything fails: that's your to-do list
```

Open this in a browser and inspect the JSON before writing code:
`https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_week.geojson`

### API facts you need
- Feed URL pattern: `.../summary/{magnitude}_{window}.geojson`, for example `all_hour`, `all_day`, `all_week`, `2.5_day`.
- The response is GeoJSON with a `features` list.
- Each feature has a top-level `id`, a `properties` dict, and `geometry.coordinates` as `[lon, lat, depth_km]`.
- `time` and `updated` are **epoch milliseconds**.
- A misspelled feed name returns HTTP 200 with a plain-text "404 File Not Found" body, so the status code alone is not a safe check.
- The feed files refresh about once a minute. The same event can appear again with a newer `updated`.

**No network?** Use the instructor-provided `data/fallback/all_week.geojson` (`run.py` falls back to it automatically).

## Project map
| File | Task |
|---|---|
| `quakes/fetch.py` | 1: fetch and parse |
| `quakes/stream.py` | 2: stream collector |
| `quakes/cleaning.py` | 3: cleaning |
| `quakes/features.py` | 4: feature engineering |
| `quakes/config.py`, `transform.py`, `run.py` | 5: transform and run |

Each stub has a docstring that states exactly what the function must do. Run one test file at a time, for example `pytest tests/test_fetch.py`.

---

## Task 1: Fetch and parse (`fetch.py`, 15 min)
**Write**
- `fetch_feed(feed="all_week") -> dict`
- `geojson_to_df(payload) -> DataFrame`, one row per event, with columns `id`, every key in `properties`, plus `lon`, `lat`, `depth_km`.

**Hints**
- `requests.get(..., timeout=15)`, then `raise_for_status()`.
- Wrap the `.json()` call so a bad feed name gives a clear error.
- Build a list of dicts, then `pd.DataFrame(rows)`.

**Checkpoint:** `pytest tests/test_fetch.py`. Then pull the real feed and run `df.info()` and `df.isna().mean().sort_values()`. Note which columns are mostly empty.

---

## Task 2: Stream collector (`stream.py`, 10 min)
Simulate streaming by polling `all_hour` every 60 s.

**Write**
- `filter_unseen(df, seen)`: keep only rows whose `(id, updated)` pair is new, and add those pairs to `seen`.
- `run_stream(feed, interval_s, duration_s, out_path)`: loop, fetch, filter, append to a `.jsonl` file, print `[hh:mm:ss] 3 new / 12 fetched`.
- `main()` with argparse, so it runs as `python -m quakes.stream --interval 60 --duration 2400`.

**Hints**
- `time.sleep`, and `df.to_json(path_or_buf, orient="records", lines=True)`. Open the file in append mode (`"a"`) and write a trailing newline.
- Catch network errors inside the loop so one failed poll does not kill the run.

**Checkpoint:** `pytest tests/test_stream.py`. Then **launch it in a second terminal and leave it running.** You merge its output in Task 5.

---

## Task 3: Cleaning (`cleaning.py`, 25 min)
| Function | Behaviour |
|---|---|
| `epoch_ms_to_datetime(df)` | `time` and `updated` become UTC datetimes |
| `dedupe_latest(df)` | One row per `id`, keeping the greatest `updated` |
| `keep_earthquakes(df)` | Normalise `type` (strip, lowercase), keep `"earthquake"` only |
| `extract_region(place)` | Text after the last comma, or the whole string if no comma |
| `iqr_outlier_mask(s, k=1.5)` | True outside Q1 − k·IQR and Q3 + k·IQR |
| `drop_missing_target(df)` | Drop rows where `mag` is NaN |
| `clean(df)` | Chain the above and add a `region` column |

**Hints**
- `sort_values("updated")` then `drop_duplicates("id", keep="last")`
- `pd.to_datetime(..., unit="ms", utc=True)`
- `Series.str.split(",").str[-1]`

**Checkpoint:** `pytest tests/test_cleaning.py`. Then print the shape before and after each step. Where did the most rows go?

**Decide, don't delete blindly.** Run `iqr_outlier_mask` on `depth_km` and `mag`. Negative depth and negative magnitude both occur in real data. Error or real? Write your call in `ANSWERS.md`.

---

## Task 4: Feature engineering (`features.py`, 15 min)
| Function | Output |
|---|---|
| `add_time_features(df)` | `hour`, `dayofweek` (UTC) |
| `add_quality_features(df)` | `update_lag_hours` (`updated − time`), `is_reviewed`, `nst_missing` |
| `add_location_features(df)` | `abs_lat`, `is_shallow` (depth_km < 70) |
| `group_rare(series, top_k=15)` | Keep the top_k most frequent values, replace the rest with `"Other"` |
| `add_target(df)` | `big_quake = 1 if mag >= 4.5 else 0` |
| `drop_leaky_columns(df)` | Remove the columns listed in `config.LEAKY` |

**Think first:** why does `region` need `group_rare` before one-hot encoding? What happens to the column count without it?

**Leakage hunt.** `sig` is computed from the magnitude and other inputs, and `title` literally contains the magnitude. Inspect your columns and fill `config.LEAKY`. The tests require at least `title`, `sig`, `mmi`, `cdi`, `felt`, `alert`. Ask of every column: *would I know this at the moment I predict?*

**Checkpoint:** `pytest tests/test_features.py`

---

## Task 5: Transform and run (`config.py`, `transform.py`, `run.py`, 15 min)
**`config.py`:** fill `NUMERIC`, `NOMINAL`, `LEAKY`.

**`transform.py`**
- `split_data(df, test_size=0.2)` returns `X_train, X_test, y_train, y_test`, stratified and seeded. **`mag` must not be in X.**
- `build_preprocessor(scaler="robust")` returns a `ColumnTransformer`.
  - Numeric: median imputation, then a scaler chosen by name (`standard`, `minmax`, `robust`).
  - Nominal: most-frequent imputation, then one-hot with `handle_unknown="ignore"`.

**`run.py`**
1. Fetch `all_week` (fall back to the file in `data/fallback/` on failure).
2. If `data/stream/*.jsonl` exists, merge it in, then apply `dedupe_latest`.
3. Clean, engineer features, drop leaky columns.
4. Split, `fit_transform` on train only, `transform` on test.
5. Print a report: raw rows, rows after cleaning, stream rows merged, events whose `updated` changed, train/test shapes, positive-class rate in each.
6. Save `train.csv`, `test.csv` and `preprocessor.joblib` to `data/processed/`.

**Checkpoint:** `pytest` all green, then `python -m quakes.run`.

---

## Questions (`ANSWERS.md`, 3–4 lines each)
1. **Leakage:** which columns did you drop and why? Is `tsunami` leaky? Is `magType`?
2. **Stream vs batch:** how many events changed (same `id`, newer `updated`) during your stream window? What does that tell you about "latest version wins"?
3. **Outliers:** your decision on negative depth and negative magnitude, with reasoning.
4. **Cardinality:** you grouped `region` to top-k. Name one alternative encoding and one risk it carries.

## Stretch
- Add `events_last_24h_in_region` (rolling count per region).
- Compare `--scaler standard` and `--scaler robust` on `depth_km`.
