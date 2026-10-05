from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FALLBACK_PATH = ROOT / "data" / "fallback" / "all_week.geojson"
STREAM_DIR = ROOT / "data" / "stream"
PROCESSED_DIR = ROOT / "data" / "processed"

SEED = 42
TARGET = "big_quake"

NUMERIC: list[str] = [
    "depth_km", "lon", "lat", "abs_lat", "is_shallow",
    "nst", "nst_missing", "gap", "dmin", "rms",
    "hour", "dayofweek", "update_lag_hours", "is_reviewed",
]
NOMINAL: list[str] = ["region", "net"]
LEAKY: list[str] = [
    "title", "sig", "mmi", "cdi", "felt", "alert",   # required by the tests
    "tsunami", "magType", "types",
]