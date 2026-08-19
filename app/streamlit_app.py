"""Streamlit dashboard for European banking churn segmentation analytics."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from churn_analytics.data import (  # noqa: E402
    AGE_BAND_ORDER,
    BALANCE_SEGMENT_ORDER,
    CREDIT_BAND_ORDER,
    TENURE_GROUP_ORDER,
    prepare_customers,
)
from churn_analytics.kpis import compute_kpis, profile_comparison, segment_churn_table  # noqa: E402

NAVY = "#0B1F3A"
GOLD = "#C4A35A"
TEAL = "#1F7A8C"
CRIMSON = "#B23A48"
SLATE = "#4A5568"
PLOTLY_TEMPLATE = "plotly_white"
COLORWAY = [TEAL, GOLD, CRIMSON, "#2E6F40", "#5C4B8A", "#D9763A"]


def _inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.4rem; max-width: 1280px;}
        h1, h2, h3 {color: #0B1F3A;}
        .hero {
            background: linear-gradient(135deg, #0B1F3A 0%, #1F7A8C 100%);
            color: #F8F4EA;
            padding: 1.4rem 1.6rem;
            border-radius: 16px;
            margin-bottom: 1.1rem;
        }
        .hero h1 {color: #F8F4EA; font-size: 1.7rem; margin-bottom: 0.35rem;}
        .hero p {color: #E6EDF5; margin: 0; font-size: 0.95rem;}
        .kpi-card {
            background: #ffffff;
            border: 1px solid #E6E2D6;
            border-left: 5px solid #C4A35A;
            border-radius: 12px;
            padding: 0.85rem 1rem;
            min-height: 108px;
        }
        .kpi-label {font-size: 0.78rem; color: #4A5568; letter-spacing: 0.04em; text-transform: uppercase;}
        .kpi-value {font-size: 1.55rem; font-weight: 700; color: #0B1F3A; margin: 0.15rem 0;}
        .kpi-hint {font-size: 0.78rem; color: #1F7A8C;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _kpi_card(label: str, value: str, hint: str) -> None:
    st.markdown(
        f'<div class="kpi-card"><div class="kpi-label">{label}</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-hint">{hint}</div></div>',
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def _load_prepared() -> pd.DataFrame:
    prepared, _report = prepare_customers()
    return prepared


def _apply_filters(df: pd.DataFrame, filters: dict) -> pd.DataFrame:
    out = df
    if filters["geographies"]:
        out = out[out["Geography"].isin(filters["geographies"])]
    if filters["genders"]:
        out = out[out["Gender"].isin(filters["genders"])]
    if filters["age_bands"]:
        out = out[out["AgeBand"].isin(filters["age_bands"])]
    if filters["credit_bands"]:
        out = out[out["CreditBand"].isin(filters["credit_bands"])]
    if filters["tenure_groups"]:
        out = out[out["TenureGroup"].isin(filters["tenure_groups"])]
    if filters["balance_segments"]:
        out = out[out["BalanceSegment"].isin(filters["balance_segments"])]
    if filters["products"]:
        out = out[out["NumOfProducts"].isin(filters["products"])]
    if filters["activity"] != "All":
        flag = 1 if filters["activity"] == "Active" else 0
        out = out[out["IsActiveMember"] == flag]
    if filters["high_value_only"]:
        out = out[out["HighValueFlag"] == 1]
    return out


def _bar_rate(table: pd.DataFrame, title: str, x_title: str) -> go.Figure:
    fig = px.bar(
        table,
        x="segment",
        y="churn_rate",
        color="churn_rate",
        color_continuous_scale=["#D6E8E4", TEAL, CRIMSON],
        title=title,
        labels={"segment": x_title, "churn_rate": "Churn rate"},
        hover_data={"customers": True, "churned": True, "share_of_churn": ":.1%", "churn_rate": ":.1%"},
    )
    fig.update_layout(template=PLOTLY_TEMPLATE, coloraxis_showscale=False, yaxis_tickformat=".0%")
    fig.update_traces(text=table["churn_rate"].map(lambda v: f"{v:.1%}"), textposition="outside")
    return fig


def main() -> None:
    st.set_page_config(
        page_title="European Banking Churn Analytics",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_css()
    data = _load_prepared()

    st.sidebar.header("Segment filters")
    st.sidebar.caption("KPIs and charts update from the filtered customer set.")
    geographies = st.sidebar.multiselect("Geography", sorted(data["Geography"].unique()), default=sorted(data["Geography"].unique()))
    genders = st.sidebar.multiselect("Gender", sorted(data["Gender"].unique()), default=sorted(data["Gender"].unique()))
    age_bands = st.sidebar.multiselect("Age band", list(AGE_BAND_ORDER), default=list(AGE_BAND_ORDER))
    credit_bands = st.sidebar.multiselect("Credit score band", list(CREDIT_BAND_ORDER), default=list(CREDIT_BAND_ORDER))
    tenure_groups = st.sidebar.multiselect("Tenure group", list(TENURE_GROUP_ORDER), default=list(TENURE_GROUP_ORDER))
    balance_segments = st.sidebar.multiselect(
        "Balance segment", list(BALANCE_SEGMENT_ORDER), default=list(BALANCE_SEGMENT_ORDER)
    )
    products = st.sidebar.multiselect(
        "Number of products", sorted(data["NumOfProducts"].unique()), default=sorted(data["NumOfProducts"].unique())
    )
    activity = st.sidebar.radio("Engagement", ["All", "Active", "Inactive"], horizontal=True)
    high_value_only = st.sidebar.checkbox("High-value customers only (top-quartile balance or salary)")

    filtered = _apply_filters(
        data,
        {
            "geographies": geographies,
            "genders": genders,
            "age_bands": age_bands,
            "credit_bands": credit_bands,
            "tenure_groups": tenure_groups,
            "balance_segments": balance_segments,
            "products": products,
            "activity": activity,
            "high_value_only": high_value_only,
        },
    )

    if filtered.empty:
        st.warning("No customers match the current filters. Broaden the selection to restore the view.")
        return

    kpis = compute_kpis(filtered)
    engagement = kpis["engagement"]

    st.markdown(
        """
        <div class="hero">
            <h1>Customer Segmentation &amp; Churn Pattern Analytics</h1>
            <p>European retail banking · France, Spain, Germany · segmentation-driven retention intelligence</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        _kpi_card("Overall churn rate", f"{kpis['overall_churn_rate']:.1%}", f"{kpis['churned']:,} of {kpis['customers']:,} customers")
    with c2:
        _kpi_card("High-value churn ratio", f"{kpis['high_value_churn_ratio']:.1%}", f"{kpis['high_value_customers']:,} premium customers")
    with c3:
        _kpi_card("Geographic risk index", f"{kpis['peak_geographic_risk']:.2f}×", f"Peak exposure: {kpis['peak_geography']}")
    with c4:
        _kpi_card("Engagement drop", f"{engagement['drop_ratio']:.2f}×", f"Inactive {engagement['inactive_churn_rate']:.1%} vs active {engagement['active_churn_rate']:.1%}")
    with c5:
        _kpi_card("Balance at risk", f"€{kpis['churned_balance']/1e6:.1f}m", "Aggregate balance of churned accounts")

    overview, geography, age_tenure, high_value, drilldown = st.tabs(
        [
            "Overall churn summary",
            "Geography-wise churn",
            "Age & tenure",
            "High-value explorer",
            "Drill-down",
        ]
    )

    with overview:
        left, right = st.columns((1.15, 1))
        with left:
            status = filtered["ChurnStatus"].value_counts().rename_axis("status").reset_index(name="customers")
            fig = px.pie(
                status,
                names="status",
                values="customers",
                color="status",
                color_discrete_map={"Churned": CRIMSON, "Retained": TEAL},
                hole=0.55,
                title="Churned vs retained",
            )
            fig.update_layout(template=PLOTLY_TEMPLATE)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.subheader("Churned vs retained profiles")
            profiles = profile_comparison(filtered)
            profiles_display = profiles.copy()
            if "Balance" in profiles_display.index:
                profiles_display.loc["Balance"] = profiles_display.loc["Balance"].map(lambda v: round(v, 0))
            if "EstimatedSalary" in profiles_display.index:
                profiles_display.loc["EstimatedSalary"] = profiles_display.loc["EstimatedSalary"].map(lambda v: round(v, 0))
            st.dataframe(profiles.round(2), use_container_width=True)
            st.caption("Churned customers are older on average and hold higher balances than retained customers.")

        st.subheader("Segment-wise churn rates")
        cols = st.columns(3)
        specs = [
            ("Gender", "Gender"),
            ("CreditBand", "Credit score band"),
            ("BalanceSegment", "Balance segment"),
        ]
        for col, (field, label) in zip(cols, specs):
            table = segment_churn_table(filtered, field)
            col.plotly_chart(_bar_rate(table, label, label), use_container_width=True)

        st.subheader("Product holding vs churn")
        products_table = segment_churn_table(filtered, "NumOfProducts")
        fig = px.bar(
            products_table,
            x="segment",
            y="churn_rate",
            text=products_table["churn_rate"].map(lambda v: f"{v:.1%}"),
            title="Churn rate by number of products",
            color_discrete_sequence=[CRIMSON],
        )
        fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_tickformat=".0%", xaxis_title="Products")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Single-product customers and 3–4 product holders drive a disproportionate share of exits.")

        activity_table = segment_churn_table(filtered, "ActivityStatus")
        st.plotly_chart(_bar_rate(activity_table, "Engagement vs churn", "Activity"), use_container_width=True)

    with geography:
        geo_table = kpis["geographic_risk_index"]
        left, right = st.columns(2)
        with left:
            fig = px.bar(
                geo_table,
                x="segment",
                y="churn_rate",
                color="risk_index",
                color_continuous_scale=["#D6E8E4", GOLD, CRIMSON],
                title="Churn rate by country",
                labels={"segment": "Geography", "churn_rate": "Churn rate", "risk_index": "Risk index"},
                hover_data={"customers": True, "churned": True, "risk_index": ":.2f"},
            )
            fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)
        with right:
            fig = px.bar(
                geo_table,
                x="segment",
                y="share_of_churn",
                color="segment",
                color_discrete_sequence=COLORWAY,
                title="Share of all churn events",
                labels={"segment": "Geography", "share_of_churn": "Share of churn"},
            )
            fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_tickformat=".0%", showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Geography × age interaction")
        heat = (
            filtered.groupby(["Geography", "AgeBand"], observed=True)["Exited"]
            .mean()
            .reset_index()
            .pivot(index="Geography", columns="AgeBand", values="Exited")
        )
        fig = px.imshow(
            heat,
            color_continuous_scale=["#F4EBD0", GOLD, CRIMSON],
            aspect="auto",
            title="Churn rate: country by age band",
            text_auto=".1%",
        )
        fig.update_layout(template=PLOTLY_TEMPLATE)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Geography × gender")
        gender_geo = (
            filtered.groupby(["Geography", "Gender"], observed=True)["Exited"]
            .mean()
            .reset_index()
            .rename(columns={"Exited": "churn_rate"})
        )
        fig = px.bar(
            gender_geo,
            x="Geography",
            y="churn_rate",
            color="Gender",
            barmode="group",
            color_discrete_map={"Female": GOLD, "Male": TEAL},
            title="Gender-based churn differences by country",
        )
        fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)
        st.dataframe(geo_table.round(3), use_container_width=True)

    with age_tenure:
        a1, a2 = st.columns(2)
        with a1:
            age_table = segment_churn_table(filtered, "AgeBand")
            st.plotly_chart(_bar_rate(age_table, "Churn by age band", "Age band"), use_container_width=True)
        with a2:
            tenure_table = segment_churn_table(filtered, "TenureGroup")
            st.plotly_chart(_bar_rate(tenure_table, "Churn by tenure group", "Tenure"), use_container_width=True)

        fig = px.histogram(
            filtered,
            x="Age",
            color="ChurnStatus",
            barmode="overlay",
            nbins=30,
            color_discrete_map={"Churned": CRIMSON, "Retained": TEAL},
            opacity=0.7,
            title="Age distribution: churned vs retained",
        )
        fig.update_layout(template=PLOTLY_TEMPLATE)
        st.plotly_chart(fig, use_container_width=True)

        tenure_age = (
            filtered.groupby(["TenureGroup", "AgeBand"], observed=True)["Exited"]
            .mean()
            .reset_index()
            .rename(columns={"Exited": "churn_rate"})
        )
        fig = px.bar(
            tenure_age,
            x="AgeBand",
            y="churn_rate",
            color="TenureGroup",
            barmode="group",
            color_discrete_sequence=COLORWAY,
            title="Age and tenure combined",
        )
        fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    with high_value:
        st.markdown(
            f"High-value customers are those in the **top quartile of balance** "
            f"(≥ €{kpis['balance_q75']:,.0f}) **or salary** (≥ €{kpis['salary_q75']:,.0f})."
        )
        hv = filtered[filtered["HighValueFlag"] == 1]
        h1, h2, h3 = st.columns(3)
        h1.metric("High-value customers", f"{len(hv):,}")
        h2.metric("High-value churn ratio", f"{kpis['high_value_churn_ratio']:.1%}")
        h3.metric("Premium balance at risk", f"€{kpis['high_value_balance_at_risk']/1e6:.1f}m")

        scatter = filtered.sample(min(len(filtered), 2500), random_state=7)
        fig = px.scatter(
            scatter,
            x="EstimatedSalary",
            y="Balance",
            color="ChurnStatus",
            symbol="HighValueFlag",
            opacity=0.65,
            color_discrete_map={"Churned": CRIMSON, "Retained": TEAL},
            title="Salary vs balance (sample of filtered customers)",
            labels={"EstimatedSalary": "Estimated salary (€)", "Balance": "Account balance (€)"},
        )
        fig.update_layout(template=PLOTLY_TEMPLATE)
        st.plotly_chart(fig, use_container_width=True)

        combo = (
            filtered.assign(
                SalaryBand=filtered["HighSalaryFlag"].map({1: "High salary", 0: "Other salary"}),
                BalBand=filtered["HighBalanceFlag"].map({1: "High balance", 0: "Other balance"}),
            )
            .groupby(["SalaryBand", "BalBand"])["Exited"]
            .agg(customers="count", churn_rate="mean")
            .reset_index()
        )
        fig = px.bar(
            combo,
            x="BalBand",
            y="churn_rate",
            color="SalaryBand",
            barmode="group",
            color_discrete_sequence=[TEAL, GOLD],
            title="Salary vs balance churn patterns",
        )
        fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

        hv_geo = segment_churn_table(hv, "Geography") if not hv.empty else pd.DataFrame()
        if not hv_geo.empty:
            st.plotly_chart(_bar_rate(hv_geo, "High-value churn by geography", "Geography"), use_container_width=True)

        st.caption(
            "High-balance churners concentrate revenue risk: exits are not confined to low-value, "
            "zero-balance accounts."
        )

    with drilldown:
        st.subheader("Customer-level drill-down")
        st.caption("Inspect the filtered rows that underpin the KPIs above.")
        show_churned = st.toggle("Show churned customers only", value=False)
        view = filtered[filtered["Exited"] == 1] if show_churned else filtered
        display_cols = [
            "CustomerId",
            "Geography",
            "Gender",
            "Age",
            "AgeBand",
            "CreditScore",
            "CreditBand",
            "Tenure",
            "TenureGroup",
            "Balance",
            "BalanceSegment",
            "NumOfProducts",
            "IsActiveMember",
            "EstimatedSalary",
            "HighValueFlag",
            "Exited",
        ]
        st.dataframe(view[display_cols].sort_values(["Exited", "Balance"], ascending=[False, False]), use_container_width=True, height=420)
        st.download_button(
            "Download filtered CSV",
            view.to_csv(index=False).encode("utf-8"),
            file_name="filtered_churn_segment.csv",
            mime="text/csv",
        )

        st.subheader("Contribution of each segment to total churn")
        contrib_dim = st.selectbox(
            "Contribution dimension",
            ["Geography", "AgeBand", "TenureGroup", "BalanceSegment", "CreditBand", "Gender", "NumOfProducts"],
        )
        contrib = segment_churn_table(filtered, contrib_dim)
        fig = px.bar(
            contrib,
            x="segment",
            y="share_of_churn",
            color="churn_rate",
            color_continuous_scale=["#D6E8E4", GOLD, CRIMSON],
            title=f"Share of churn events by {contrib_dim}",
            hover_data={"customers": True, "churn_rate": ":.1%"},
        )
        fig.update_layout(template=PLOTLY_TEMPLATE, yaxis_tickformat=".0%")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown(
        "Sources: Unified Mentor project brief · "
        "[European Central Bank](https://www.ecb.europa.eu/home/html/index.en.html) context on retail banking stability."
    )


if __name__ == "__main__":
    main()
