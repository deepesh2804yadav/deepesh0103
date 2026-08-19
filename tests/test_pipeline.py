from pathlib import Path

import pandas as pd
import pytest

from churn_analytics.data import ValidationError, add_segmentation, prepare_customers, validate_raw_frame
from churn_analytics.kpis import compute_kpis, geographic_risk_index, segment_churn_table

DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "churn_modelling.csv"


def test_prepare_customers_validates_and_segments():
    df, report = prepare_customers(DATA_PATH)
    assert report["ok"] is True
    assert report["row_count"] == 10000
    assert report["duplicate_customer_ids"] == 0
    assert "Surname" not in df.columns
    assert {"AgeBand", "CreditBand", "TenureGroup", "BalanceSegment", "HighValueFlag"} <= set(df.columns)
    assert set(df["Exited"].unique()) <= {0, 1}
    assert set(df["HasCrCard"].unique()) <= {0, 1}
    assert set(df["IsActiveMember"].unique()) <= {0, 1}


def test_overall_churn_rate_matches_dataset():
    df, _ = prepare_customers(DATA_PATH)
    kpis = compute_kpis(df)
    assert kpis["customers"] == 10000
    assert kpis["churned"] == 2037
    assert pytest.approx(kpis["overall_churn_rate"], abs=1e-6) == 0.2037


def test_germany_has_elevated_geographic_risk():
    df, _ = prepare_customers(DATA_PATH)
    geo = geographic_risk_index(df).set_index("segment")
    assert geo.loc["Germany", "risk_index"] > 1.5
    assert geo.loc["France", "risk_index"] < 1.0
    assert geo.loc["Spain", "risk_index"] < 1.0


def test_age_band_46_60_is_highest_churn():
    df, _ = prepare_customers(DATA_PATH)
    table = segment_churn_table(df, "AgeBand").set_index("segment")
    assert table["churn_rate"].idxmax() == "46–60"
    assert table.loc["46–60", "churn_rate"] > 0.45


def test_inactive_members_churn_more():
    df, _ = prepare_customers(DATA_PATH)
    kpis = compute_kpis(df)
    assert kpis["engagement"]["inactive_churn_rate"] > kpis["engagement"]["active_churn_rate"]
    assert kpis["engagement"]["drop_ratio"] > 1.5


def test_high_value_churn_is_material():
    df, _ = prepare_customers(DATA_PATH)
    kpis = compute_kpis(df)
    assert kpis["high_value_customers"] > 0
    assert kpis["high_value_churn_ratio"] > 0.15
    assert kpis["churned_balance"] > 0


def test_validation_rejects_non_binary_exited():
    raw = pd.read_csv(DATA_PATH)
    raw.loc[0, "Exited"] = 2
    with pytest.raises(ValidationError, match="Exited"):
        validate_raw_frame(raw)


def test_segmentation_labels_cover_expected_bands():
    raw = pd.DataFrame(
        {
            "CustomerId": [1, 2, 3, 4],
            "CreditScore": [500, 600, 720, 800],
            "Age": [22, 40, 50, 70],
            "Tenure": [1, 4, 9, 0],
            "Balance": [0.0, 50_000.0, 150_000.0, 200_000.0],
            "IsActiveMember": [0, 1, 0, 1],
            "HasCrCard": [1, 0, 1, 1],
            "EstimatedSalary": [10_000, 40_000, 90_000, 180_000],
            "Exited": [0, 1, 0, 1],
        }
    )
    out = add_segmentation(raw)
    assert list(out["AgeBand"].astype(str)) == ["<30", "30–45", "46–60", "60+"]
    assert list(out["CreditBand"].astype(str)) == ["Low", "Medium", "High", "High"]
    assert list(out["TenureGroup"].astype(str)) == ["New", "Mid-term", "Long-term", "New"]
    assert list(out["BalanceSegment"].astype(str)) == [
        "Zero-balance",
        "Low-balance",
        "High-balance",
        "High-balance",
    ]
