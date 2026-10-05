"""Task 4: feature engineering."""
import pandas as pd


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add 'hour' and 'dayofweek' (UTC) from 'time'."""
    ...


def add_quality_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add:
    update_lag_hours = hours between 'time' and 'updated'
    is_reviewed      = 1 if status == 'reviewed' else 0
    nst_missing      = 1 if 'nst' is missing else 0
    """
    ...


def add_location_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add 'abs_lat' and 'is_shallow' (1 if depth_km < 70 else 0)."""
    ...


def group_rare(s: pd.Series, top_k: int = 15) -> pd.Series:
    """Keep the top_k most frequent values; replace all others with 'Other'."""
    ...


def add_target(df: pd.DataFrame) -> pd.DataFrame:
    """Add 'big_quake' = 1 if mag >= 4.5 else 0."""
    ...


def drop_leaky_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop every column listed in config.LEAKY (ignore ones that are absent)."""
    ...
