"""Customer segmentation and churn analytics for European retail banking."""

from .data import (
    REQUIRED_COLUMNS,
    load_dataset,
    prepare_customers,
    validate_raw_frame,
)
from .kpis import compute_kpis, geographic_risk_index, segment_churn_table

__all__ = [
    "REQUIRED_COLUMNS",
    "load_dataset",
    "prepare_customers",
    "validate_raw_frame",
    "compute_kpis",
    "geographic_risk_index",
    "segment_churn_table",
]
