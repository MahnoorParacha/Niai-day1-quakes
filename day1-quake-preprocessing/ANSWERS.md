# Day 1 Lab: Answers

Name: Mahnoor

## 1. Leakage
Which columns did you drop and why? Is `tsunami` leaky? Is `magType`?
I dropped `title`, `sig`, `mmi`, `cdi`, `felt`, `alert`, `tsunami`, `magType` and `types`. `title` literally contains the magnitude, and `sig` is computed from the magnitude and other inputs. `mmi`, `cdi`, `felt` and `alert` describe the shaking and its impact, which are consequences of a large quake that I wouldn't know at prediction time. I also kept `mag` out of X, since `big_quake` is defined directly from it.

`tsunami` is leaky: it is a flag set after an event is assessed, and it mostly fires for large offshore quakes, so it encodes size. `magType` is leaky too: it records which method was used to calculate the magnitude, so it is only known once the magnitude exists, and different methods are used for different size ranges. I kept `depth_km`, location, `nst`, `gap`, `dmin` and `rms`, which are available from the sensors and the location solution. The `is_reviewed` and `update_lag_hours` features are borderline, since review timing may depend on event size, and I'd check them if the model looked too good.



## 2. Stream vs batch
How many events changed (same `id`, newer `updated`) during your stream window? What does that tell you about "latest version wins"?
During my ~40 minute stream window, 1 event changed: `ci41343367` appeared with 3 different `updated` values (same `id`). The file had 22 rows for 12 unique events, mostly because my short test run and the real run wrote the same events twice.

This shows that one `id` can have several versions as USGS revises it (magnitude, location or review status). "Latest version wins" is the right rule: `dedupe_latest` sorts by `updated` and keeps the last row per `id`, so the final dataset has the most recent, reviewed values. The `(id, updated)` pair is the right key for spotting new versions, because `id` alone would miss the revisions.

## 3. Outliers
**Negative depth (72 events): real, so I keep them.** USGS measures depth relative to a reference level (roughly sea level), so an event near the surface at high elevation, like a shallow volcanic quake, can have a negative depth. A depth of -1 km is small and plausible, not a sensor error.

**Negative magnitude (89 events): real, so I keep them.** Magnitude is a logarithmic scale with no lower bound, and dense local networks detect micro-quakes below 0 (the minimum in this week's data is -1.22).

**Why I don't drop IQR outliers:** the flagged depths (35 to 638 km) are just deep earthquakes, and the flagged magnitudes are mostly 4.5+ quakes, which are my positive class for `big_quake`. Deleting them would remove the events I want to predict. Instead I use a robust scaler so extreme values don't distort the model.


## 4. Cardinality
You grouped `region` to top-k. Name one alternative encoding and one risk it carries.
`region` has many distinct values, so one-hot encoding would add one column per place. I grouped it to the top 15 plus "Other".

An alternative is target encoding (replace each region with the average `big_quake` rate for that region). The risk is target leakage and overfitting: if the averages are computed on the same rows the model trains on, rare regions get an almost perfect encoding of their own labels. It has to be fitted inside cross-validation folds, or on the train split only.

