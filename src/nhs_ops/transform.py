from __future__ import annotations

import re

import numpy as np
import pandas as pd


ALIASES = {
    "provider_code": {
        "provider_code", "org_code", "organisation_code", "organisationcode", "orgcode"
    },
    "provider_name": {
        "provider_name", "org_name", "organisation_name", "organisationname", "orgname"
    },
    "month": {"month", "reporting_month", "period", "reporting_period", "date"},
    "attendances": {
        "attendances", "total_attendances", "ae_attendances", "a_e_attendances", "total"
    },
    "within_4h": {
        "within_4h", "within_four_hours", "attendances_within_4_hours", "four_hour"
    },
    "emergency_admissions": {
        "emergency_admissions", "emergency_admission", "admissions", "emergencyadmissions"
    },
}


def _normalise(name: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "_", str(name).strip().lower()).strip("_")
    return text.replace("a_e", "ae")


def _resolve_columns(columns: list[str]) -> dict[str, str]:
    normalised = {_normalise(column): column for column in columns}
    resolved: dict[str, str] = {}
    for canonical, aliases in ALIASES.items():
        for alias in aliases:
            if alias in normalised:
                resolved[normalised[alias]] = canonical
                break
    return resolved


def canonicalise_ae(frame: pd.DataFrame) -> pd.DataFrame:
    """Map common NHS A&E CSV variants into a stable analytical contract."""
    result = frame.rename(columns=_resolve_columns(list(frame.columns))).copy()
    required = {"provider_code", "provider_name", "month", "attendances", "within_4h"}
    missing = required - set(result.columns)
    if missing:
        raise ValueError(f"Missing required analytical fields: {sorted(missing)}")

    keep = [column for column in ALIASES if column in result.columns]
    result = result[keep].copy()
    result["month"] = pd.to_datetime(result["month"], errors="coerce").dt.to_period("M").dt.to_timestamp()

    for column in ["attendances", "within_4h", "emergency_admissions"]:
        if column in result.columns:
            result[column] = pd.to_numeric(result[column], errors="coerce")

    result = result.dropna(subset=["provider_code", "month", "attendances", "within_4h"])
    result = result[result["attendances"] >= 0].copy()
    result["within_4h"] = result[["within_4h", "attendances"]].min(axis=1)
    result["four_hour_rate"] = np.where(
        result["attendances"] > 0,
        result["within_4h"] / result["attendances"],
        np.nan,
    )
    result["breaches_4h"] = (result["attendances"] - result["within_4h"]).clip(lower=0)
    result["breach_rate"] = 1 - result["four_hour_rate"]
    return result.sort_values(["provider_code", "month"]).reset_index(drop=True)
