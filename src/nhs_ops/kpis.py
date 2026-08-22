from __future__ import annotations

import numpy as np
import pandas as pd


def provider_monthly_kpis(frame: pd.DataFrame) -> pd.DataFrame:
    """Aggregate canonical records to one row per provider/month."""
    aggregations = {
        "provider_name": "last",
        "attendances": "sum",
        "within_4h": "sum",
        "breaches_4h": "sum",
    }
    if "emergency_admissions" in frame.columns:
        aggregations["emergency_admissions"] = "sum"

    grouped = (
        frame.groupby(["provider_code", "month"], as_index=False)
        .agg(aggregations)
        .sort_values(["provider_code", "month"])
    )
    grouped["four_hour_rate"] = np.where(
        grouped["attendances"] > 0,
        grouped["within_4h"] / grouped["attendances"],
        np.nan,
    )
    grouped["breach_rate"] = 1 - grouped["four_hour_rate"]
    grouped["attendance_mom_pct"] = (
        grouped.groupby("provider_code")["attendances"].pct_change(fill_method=None)
    )
    grouped["breach_rate_mom_pp"] = (
        grouped.groupby("provider_code")["breach_rate"].diff() * 100
    )
    return grouped.reset_index(drop=True)


def add_peer_anomaly_flags(frame: pd.DataFrame, threshold: float = 3.5) -> pd.DataFrame:
    """Flag unusually high breach rates using a monthly robust z-score (MAD)."""
    result = frame.copy()

    def score_month(group: pd.DataFrame) -> pd.DataFrame:
        median = group["breach_rate"].median()
        mad = (group["breach_rate"] - median).abs().median()
        if pd.isna(mad) or mad == 0:
            group["breach_rate_robust_z"] = 0.0
        else:
            group["breach_rate_robust_z"] = 0.6745 * (group["breach_rate"] - median) / mad
        return group

    result = result.groupby("month", group_keys=False).apply(score_month, include_groups=False)
    result = result.reset_index(drop=False)
    if "month" not in result.columns:
        # pandas versions differ in how grouping columns are retained when include_groups=False.
        raise RuntimeError("Month grouping column was not retained during anomaly scoring")
    result["high_breach_anomaly"] = result["breach_rate_robust_z"] >= threshold
    return result


def executive_snapshot(frame: pd.DataFrame) -> dict[str, float | int | str]:
    """Return top-line metrics for the latest available month."""
    latest_month = frame["month"].max()
    latest = frame[frame["month"] == latest_month]
    attendances = float(latest["attendances"].sum())
    within_4h = float(latest["within_4h"].sum())
    return {
        "month": latest_month.strftime("%Y-%m"),
        "providers": int(latest["provider_code"].nunique()),
        "attendances": int(attendances),
        "four_hour_rate": within_4h / attendances if attendances else float("nan"),
        "breaches_4h": int(latest["breaches_4h"].sum()),
    }
