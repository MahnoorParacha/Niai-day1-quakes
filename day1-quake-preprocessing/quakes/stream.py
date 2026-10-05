"""Task 2: simulate streaming by polling a feed on a timer."""
import argparse
import os
import time

import pandas as pd

from quakes.fetch import fetch_feed, geojson_to_df


def filter_unseen(df: pd.DataFrame, seen: set) -> pd.DataFrame:
    """Return only rows whose (id, updated) pair is not in `seen`.

    Add the new pairs to `seen` (modify the set in place).
    """
    if df.empty:
        return df.copy()

    mask = []
    for key in zip(df["id"], df["updated"]):
        if key in seen:
            mask.append(False)
        else:
            seen.add(key)
            mask.append(True)
    return df[mask]


def run_stream(feed: str, interval_s: int, duration_s: int, out_path: str) -> None:
    """Poll `feed` every `interval_s` seconds for `duration_s` seconds.

    Each poll: fetch, parse, keep unseen rows, append them to `out_path`
    as JSON lines, and print e.g. "[14:02:11] 3 new / 12 fetched".
    A failed poll must not stop the loop.
    """
    out_dir = os.path.dirname(out_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    seen = set()
    end_time = time.monotonic() + duration_s

    while True:
        stamp = time.strftime("%H:%M:%S")
        try:
            df = geojson_to_df(fetch_feed(feed))
            new = filter_unseen(df, seen)
            if not new.empty:
                text = new.to_json(orient="records", lines=True)
                with open(out_path, "a", encoding="utf-8") as f:
                    f.write(text)
                    if not text.endswith("\n"):
                        f.write("\n")
            print(f"[{stamp}] {len(new)} new / {len(df)} fetched", flush=True)
        except Exception as e:
            print(f"[{stamp}] poll failed: {e}", flush=True)

        remaining = end_time - time.monotonic()
        if remaining <= 0:
            break
        time.sleep(min(interval_s, remaining))


def main() -> None:
    """argparse: --feed (default all_hour), --interval (60), --duration (2400),
    --out (data/stream/stream.jsonl), then call run_stream."""
    parser = argparse.ArgumentParser(description="Poll the USGS feed and save new events.")
    parser.add_argument("--feed", default="all_hour")
    parser.add_argument("--interval", type=int, default=60)
    parser.add_argument("--duration", type=int, default=2400)
    parser.add_argument("--out", default="data/stream/stream.jsonl")
    args = parser.parse_args()
    run_stream(args.feed, args.interval, args.duration, args.out)


if __name__ == "__main__":
    main()