"""Ingestion, validation, cleaning, and segmentation for the bank churn dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

REQUIRED_COLUMNS = (
    "CustomerId",
    "Surname",
    "CreditScore",
    "Geography",
    "Gender",
    "Age",
    "Tenure",
    "Balance",
    "NumOfProducts",
    "HasCrCard",
    "IsActiveMember",
    "EstimatedSalary",
    "Exited",
)

ALLOWED_GEOGRAPHIES = frozenset({"France", "Spain", "Germany"})
BINARY_COLUMNS = ("HasCrCard", "IsActiveMember", "Exited")
DROP_COLUMNS = ("Surname",)

DEFAULT_DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "churn_modelling.csv"

AGE_BAND_ORDER = ("<30", "30–45", "46–60", "60+")
CREDIT_BAND_ORDER = ("Low", "Medium", "High")
TENURE_GROUP_ORDER = ("New", "Mid-term", "Long-term")
BALANCE_SEGMENT_ORDER = ("Zero-balance", "Low-balance", "High-balance")


class ValidationError(ValueError):
    """Raised when the source file fails structural or domain checks."""


def load_dataset(path: str | Path | None = None) -> pd.DataFrame:
    """Load the raw customer file without mutating analytics fields."""
    source = Path(path) if path is not None else DEFAULT_DATA_PATH
    if not source.exists():
        raise FileNotFoundError(f"Dataset not found: {source}")
    return pd.read_csv(source)


def validate_raw_frame(df: pd.DataFrame) -> dict[str, Any]:
    """Confirm required columns, uniqueness, binary flags, and churn labels."""
    issues: list[str] = []
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        issues.append(f"Missing required columns: {missing}")

    report: dict[str, Any] = {
        "row_count": int(len(df)),
        "column_count": int(df.shape[1]),
        "missing_columns": missing,
        "null_cells": int(df.isna().sum().sum()) if not missing else None,
        "duplicate_customer_ids": None,
        "binary_violations": {},
        "geography_values": None,
        "product_range": None,
        "churn_rate": None,
        "ok": False,
        "issues": issues,
    }

    if missing:
        return report

    if df.isna().any().any():
        nulls = df.isna().sum()
        issues.append(f"Null values present: {nulls[nulls > 0].to_dict()}")

    duplicate_ids = int(df["CustomerId"].duplicated().sum())
    report["duplicate_customer_ids"] = duplicate_ids
    if duplicate_ids:
        issues.append(f"Duplicate CustomerId values: {duplicate_ids}")

    binary_violations: dict[str, list[Any]] = {}
    for col in BINARY_COLUMNS:
        unexpected = sorted(set(df[col].dropna().unique()) - {0, 1})
        if unexpected:
            binary_violations[col] = unexpected
            issues.append(f"{col} is not strictly binary; unexpected values: {unexpected}")
    report["binary_violations"] = binary_violations

    geos = sorted(df["Geography"].dropna().astype(str).unique().tolist())
    report["geography_values"] = geos
    unknown_geo = set(geos) - ALLOWED_GEOGRAPHIES
    if unknown_geo:
        issues.append(f"Unexpected Geography values: {sorted(unknown_geo)}")

    product_min = int(df["NumOfProducts"].min())
    product_max = int(df["NumOfProducts"].max())
    report["product_range"] = (product_min, product_max)
    if product_min < 1 or product_max > 4:
        issues.append(f"NumOfProducts outside expected 1–4 range: {product_min}–{product_max}")

    if not set(df["IsActiveMember"].dropna().unique()).issubset({0, 1}):
        issues.append("IsActiveMember failed engagement-field validation")

    report["churn_rate"] = float(df["Exited"].mean()) if len(df) else None
    report["issues"] = issues
    report["ok"] = len(issues) == 0
    if not report["ok"]:
        raise ValidationError("; ".join(issues))
    return report


def _age_band(age: int | float) -> str:
    if age < 30:
        return "<30"
    if age <= 45:
        return "30–45"
    if age <= 60:
        return "46–60"
    return "60+"


def _credit_band(score: int | float) -> str:
    """FICO-aligned bands: Low < 580, Medium 580–669, High 670+."""
    if score < 580:
        return "Low"
    if score < 670:
        return "Medium"
    return "High"


def _tenure_group(tenure: int | float) -> str:
    if tenure <= 2:
        return "New"
    if tenure <= 6:
        return "Mid-term"
    return "Long-term"


def _balance_segment(balance: float) -> str:
    if balance == 0:
        return "Zero-balance"
    if balance < 100_000:
        return "Low-balance"
    return "High-balance"


def add_segmentation(df: pd.DataFrame) -> pd.DataFrame:
    """Attach derived segmentation dimensions used across analysis and the app."""
    out = df.copy()
    out["AgeBand"] = out["Age"].map(_age_band)
    out["CreditBand"] = out["CreditScore"].map(_credit_band)
    out["TenureGroup"] = out["Tenure"].map(_tenure_group)
    out["BalanceSegment"] = out["Balance"].map(_balance_segment)
    out["ActivityStatus"] = out["IsActiveMember"].map({1: "Active", 0: "Inactive"})
    out["CardStatus"] = out["HasCrCard"].map({1: "Has credit card", 0: "No credit card"})
    out["ChurnStatus"] = out["Exited"].map({1: "Churned", 0: "Retained"})

    balance_q75 = float(out["Balance"].quantile(0.75))
    salary_q75 = float(out["EstimatedSalary"].quantile(0.75))
    out["HighBalanceFlag"] = (out["Balance"] >= balance_q75).astype(int)
    out["HighSalaryFlag"] = (out["EstimatedSalary"] >= salary_q75).astype(int)
    out["HighValueFlag"] = ((out["HighBalanceFlag"] == 1) | (out["HighSalaryFlag"] == 1)).astype(int)
    out.attrs["balance_q75"] = balance_q75
    out.attrs["salary_q75"] = salary_q75

    out["AgeBand"] = pd.Categorical(out["AgeBand"], categories=AGE_BAND_ORDER, ordered=True)
    out["CreditBand"] = pd.Categorical(out["CreditBand"], categories=CREDIT_BAND_ORDER, ordered=True)
    out["TenureGroup"] = pd.Categorical(out["TenureGroup"], categories=TENURE_GROUP_ORDER, ordered=True)
    out["BalanceSegment"] = pd.Categorical(
        out["BalanceSegment"], categories=BALANCE_SEGMENT_ORDER, ordered=True
    )
    return out


def prepare_customers(path: str | Path | None = None) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Load, validate, drop non-analytical surname, and create segments."""
    raw = load_dataset(path)
    report = validate_raw_frame(raw)
    cleaned = raw.drop(columns=[col for col in DROP_COLUMNS if col in raw.columns])
    prepared = add_segmentation(cleaned)
    report["balance_q75"] = prepared.attrs.get("balance_q75")
    report["salary_q75"] = prepared.attrs.get("salary_q75")
    return prepared, report
