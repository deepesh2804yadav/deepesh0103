"""KPI and segment-rate calculations for churn analytics."""

from __future__ import annotations

from typing import Any

import pandas as pd


def overall_churn_rate(df: pd.DataFrame) -> float:
    if df.empty:
        return 0.0
    return float(df["Exited"].mean())


def segment_churn_table(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """Churn rate, size, and contribution of each level of a segment column."""
    if df.empty:
        return pd.DataFrame(columns=["segment", "customers", "churned", "churn_rate", "share_of_churn", "share_of_base"])
    total_churn = int(df["Exited"].sum())
    grouped = (
        df.groupby(column, observed=True)["Exited"]
        .agg(customers="count", churned="sum", churn_rate="mean")
        .reset_index()
        .rename(columns={column: "segment"})
    )
    grouped["share_of_churn"] = grouped["churned"] / total_churn if total_churn else 0.0
    grouped["share_of_base"] = grouped["customers"] / len(df)
    return grouped


def geographic_risk_index(df: pd.DataFrame) -> pd.DataFrame:
    """Regional churn exposure relative to the filtered population baseline."""
    baseline = overall_churn_rate(df)
    table = segment_churn_table(df, "Geography")
    table["risk_index"] = table["churn_rate"] / baseline if baseline else 0.0
    return table.sort_values("risk_index", ascending=False)


def high_value_churn_ratio(df: pd.DataFrame) -> float:
    premium = df[df["HighValueFlag"] == 1]
    if premium.empty:
        return 0.0
    return float(premium["Exited"].mean())


def engagement_drop_indicator(df: pd.DataFrame) -> dict[str, float]:
    """Inactivity versus activity churn gap used as the engagement drop KPI."""
    inactive = df[df["IsActiveMember"] == 0]
    active = df[df["IsActiveMember"] == 1]
    inactive_rate = float(inactive["Exited"].mean()) if not inactive.empty else 0.0
    active_rate = float(active["Exited"].mean()) if not active.empty else 0.0
    return {
        "inactive_churn_rate": inactive_rate,
        "active_churn_rate": active_rate,
        "drop_ratio": (inactive_rate / active_rate) if active_rate else 0.0,
        "drop_gap_pp": (inactive_rate - active_rate) * 100,
    }


def profile_comparison(df: pd.DataFrame) -> pd.DataFrame:
    metrics = ["CreditScore", "Age", "Tenure", "Balance", "NumOfProducts", "EstimatedSalary"]
    if df.empty:
        return pd.DataFrame()
    summary = df.groupby("ChurnStatus")[metrics].mean().T
    summary.columns.name = None
    return summary


def compute_kpis(df: pd.DataFrame) -> dict[str, Any]:
    """Core dashboard KPIs, always computed on the currently filtered frame."""
    churned = df[df["Exited"] == 1]
    retained = df[df["Exited"] == 0]
    engagement = engagement_drop_indicator(df)
    geo = geographic_risk_index(df)
    peak_geo = geo.iloc[0] if not geo.empty else None
    return {
        "customers": int(len(df)),
        "churned": int(df["Exited"].sum()) if not df.empty else 0,
        "retained": int((df["Exited"] == 0).sum()) if not df.empty else 0,
        "overall_churn_rate": overall_churn_rate(df),
        "high_value_churn_ratio": high_value_churn_ratio(df),
        "high_value_customers": int((df["HighValueFlag"] == 1).sum()) if not df.empty else 0,
        "high_value_balance_at_risk": float(churned.loc[churned["HighValueFlag"] == 1, "Balance"].sum())
        if not churned.empty
        else 0.0,
        "churned_balance": float(churned["Balance"].sum()) if not churned.empty else 0.0,
        "retained_balance": float(retained["Balance"].sum()) if not retained.empty else 0.0,
        "geographic_risk_index": geo,
        "peak_geography": None if peak_geo is None else str(peak_geo["segment"]),
        "peak_geographic_risk": 0.0 if peak_geo is None else float(peak_geo["risk_index"]),
        "engagement": engagement,
        "balance_q75": float(df.attrs.get("balance_q75") or (df["Balance"].quantile(0.75) if not df.empty else 0)),
        "salary_q75": float(df.attrs.get("salary_q75") or (df["EstimatedSalary"].quantile(0.75) if not df.empty else 0)),
    }
