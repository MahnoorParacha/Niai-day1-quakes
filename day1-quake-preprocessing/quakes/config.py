from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FALLBACK_PATH = ROOT / "data" / "fallback" / "all_week.geojson"
STREAM_DIR = ROOT / "data" / "stream"
PROCESSED_DIR = ROOT / "data" / "processed"

SEED = 42
TARGET = "big_quake"

# TODO (Task 4 and 5): fill these in after you have explored the data.
NUMERIC: list[str] = []   # numeric feature columns
NOMINAL: list[str] = []   # categorical feature columns (one-hot encoded)
LEAKY: list[str] = []     # columns that encode the magnitude: must be dropped
