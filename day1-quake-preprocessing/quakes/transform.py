"""Task 5: split and preprocess."""
import pandas as pd
from sklearn.compose import ColumnTransformer

from . import config


def split_data(df: pd.DataFrame, test_size: float = 0.2):
    """Return X_train, X_test, y_train, y_test.

    Stratified on config.TARGET, seeded with config.SEED.
    Neither the target nor 'mag' may remain in X.
    """
    from sklearn.model_selection import train_test_split

    y = df[config.TARGET]
    X = df.drop(columns=[config.TARGET, "mag"], errors="ignore")
    return train_test_split(
        X, y, test_size=test_size, stratify=y, random_state=config.SEED
    )


def build_preprocessor(scaler: str = "robust") -> ColumnTransformer:
    """ColumnTransformer over config.NUMERIC and config.NOMINAL.

    numeric: median imputation, then a scaler chosen by name
             ('standard', 'minmax', 'robust')
    nominal: most-frequent imputation, then one-hot (handle_unknown='ignore')
    """
    from sklearn.impute import SimpleImputer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import (
        MinMaxScaler,
        OneHotEncoder,
        RobustScaler,
        StandardScaler,
    )

    scalers = {
        "standard": StandardScaler,
        "minmax": MinMaxScaler,
        "robust": RobustScaler,
    }
    if scaler not in scalers:
        raise ValueError(f"Unknown scaler '{scaler}'. Choose from {list(scalers)}")

    numeric = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", scalers[scaler]()),
    ])
    nominal = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("num", numeric, config.NUMERIC),
        ("nom", nominal, config.NOMINAL),
    ])