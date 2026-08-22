from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error


@dataclass(frozen=True)
class ForecastResult:
    provider_code: str
    holdout_mae: float
    forecast: pd.DataFrame


def _features(series: pd.Series) -> pd.DataFrame:
    values = pd.DataFrame({"target": series.astype(float)})
    for lag in (1, 2, 3, 6, 12):
        values[f"lag_{lag}"] = values["target"].shift(lag)
    values["rolling_mean_3"] = values["target"].shift(1).rolling(3).mean()
    values["rolling_mean_6"] = values["target"].shift(1).rolling(6).mean()
    values["month_sin"] = np.sin(2 * np.pi * values.index.month / 12)
    values["month_cos"] = np.cos(2 * np.pi * values.index.month / 12)
    return values


def forecast_metric(
    frame: pd.DataFrame,
    provider_code: str,
    metric: str = "attendances",
    horizon: int = 3,
) -> ForecastResult:
    """Forecast a provider metric using only lagged history and a chronological hold-out."""
    provider = frame[frame["provider_code"] == provider_code].sort_values("month")
    series = provider.set_index("month")[metric].asfreq("MS")
    if series.notna().sum() < 18:
        raise ValueError("At least 18 monthly observations are required for this forecasting workflow")

    feature_frame = _features(series).dropna()
    if len(feature_frame) < 6:
        raise ValueError("Insufficient complete lag history after feature construction")

    holdout_size = max(3, min(6, len(feature_frame) // 4))
    train = feature_frame.iloc[:-holdout_size]
    test = feature_frame.iloc[-holdout_size:]
    X_columns = [column for column in feature_frame.columns if column != "target"]

    model = HistGradientBoostingRegressor(
        learning_rate=0.05,
        max_iter=250,
        l2_regularization=1.0,
        random_state=42,
    )
    model.fit(train[X_columns], train["target"])
    holdout_predictions = model.predict(test[X_columns])
    mae = float(mean_absolute_error(test["target"], holdout_predictions))

    # Refit after evaluation, then forecast recursively so future target values are never read.
    model.fit(feature_frame[X_columns], feature_frame["target"])
    history = series.copy()
    future_rows: list[dict[str, float | pd.Timestamp]] = []
    for _ in range(horizon):
        future_month = history.index.max() + pd.offsets.MonthBegin(1)
        history.loc[future_month] = np.nan
        row = _features(history).loc[future_month, X_columns]
        prediction = max(0.0, float(model.predict(row.to_frame().T)[0]))
        history.loc[future_month] = prediction
        future_rows.append({"month": future_month, "prediction": prediction})

    return ForecastResult(
        provider_code=provider_code,
        holdout_mae=mae,
        forecast=pd.DataFrame(future_rows),
    )
