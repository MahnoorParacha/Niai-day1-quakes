# Day 1 Lab: Answers

Name: Mahnoor

## 1. Leakage
Which columns did you drop and why? Is `tsunami` leaky? Is `magType`?


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

