import pandas as pd
import pytest

from nhs_ops.transform import canonicalise_ae


def test_canonicalise_ae_derives_rates_and_caps_within_four_hours():
    source = pd.DataFrame(
        {
            "Organisation Code": ["R01", "R02"],
            "Organisation Name": ["North Trust", "South Trust"],
            "Reporting Month": ["2026-07-01", "2026-07-01"],
            "Total Attendances": [100, 50],
            "Attendances Within 4 Hours": [80, 60],
            "Emergency Admissions": [20, 10],
        }
    )

    result = canonicalise_ae(source)

    assert list(result["provider_code"]) == ["R01", "R02"]
    assert result.loc[0, "four_hour_rate"] == pytest.approx(0.8)
    assert result.loc[0, "breaches_4h"] == 20
    assert result.loc[1, "within_4h"] == 50
    assert result.loc[1, "breaches_4h"] == 0


def test_canonicalise_ae_fails_on_missing_contract_fields():
    with pytest.raises(ValueError, match="Missing required analytical fields"):
        canonicalise_ae(pd.DataFrame({"provider_code": ["R01"]}))
