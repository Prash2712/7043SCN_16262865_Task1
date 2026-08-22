import pandas as pd
import pytest

from nhs_ops.kpis import add_peer_anomaly_flags, executive_snapshot, provider_monthly_kpis


def test_provider_monthly_kpis_and_snapshot():
    frame = pd.DataFrame(
        {
            "provider_code": ["R01", "R01", "R02"],
            "provider_name": ["North", "North", "South"],
            "month": pd.to_datetime(["2026-06-01", "2026-07-01", "2026-07-01"]),
            "attendances": [100, 120, 80],
            "within_4h": [85, 90, 72],
            "breaches_4h": [15, 30, 8],
        }
    )

    kpis = provider_monthly_kpis(frame)
    snapshot = executive_snapshot(kpis)

    assert snapshot["month"] == "2026-07"
    assert snapshot["providers"] == 2
    assert snapshot["attendances"] == 200
    assert snapshot["breaches_4h"] == 38
    assert snapshot["four_hour_rate"] == pytest.approx(162 / 200)
    north_july = kpis[(kpis.provider_code == "R01") & (kpis.month == pd.Timestamp("2026-07-01"))].iloc[0]
    assert north_july["attendance_mom_pct"] == pytest.approx(0.2)


def test_peer_anomaly_flags_preserve_month_and_flag_extreme_rate():
    frame = pd.DataFrame(
        {
            "provider_code": ["R01", "R02", "R03", "R04", "R05"],
            "month": pd.to_datetime(["2026-07-01"] * 5),
            "breach_rate": [0.10, 0.11, 0.12, 0.13, 0.60],
        }
    )

    scored = add_peer_anomaly_flags(frame, threshold=3.5)

    assert "month" in scored.columns
    assert scored.loc[scored.provider_code == "R05", "high_breach_anomaly"].item()
    assert not scored.loc[scored.provider_code == "R01", "high_breach_anomaly"].item()
