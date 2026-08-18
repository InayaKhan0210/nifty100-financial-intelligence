import streamlit as st
import pandas as pd

from src.dashboard.utils.db import get_companies, get_ratios


st.title("Company Screener")
st.caption("Screen Nifty 100 companies using financial quality and balance-sheet metrics.")


# =========================================================
# LOAD COMPANIES
# =========================================================

companies = get_companies()

if companies.empty:
    st.warning("Company data unavailable.")
    st.stop()


# =========================================================
# BUILD LATEST FINANCIAL DATASET
# =========================================================

rows = []

for ticker in companies["id"].dropna().astype(str).unique():

    data = get_ratios(ticker)

    if data.empty:
        continue

    data = data.copy()

    data["year"] = data["year"].astype(str)

    # Remove duplicate company-year records
    data = data.drop_duplicates(
        subset=["company_id", "year"],
        keep="first"
    )

    # Use the latest available financial period
    latest = data.iloc[-1].copy()

    latest["company_id"] = ticker

    rows.append(latest)


df = pd.DataFrame(rows)

if df.empty:
    st.warning("No financial ratio data available.")
    st.stop()


# =========================================================
# NUMERIC CONVERSION
# =========================================================

numeric_columns = [
    "return_on_equity_pct",
    "debt_to_equity",
    "free_cash_flow_cr",
    "operating_profit_margin_pct",
    "interest_coverage",
    "dividend_payout_ratio_pct",
    "net_profit_margin_pct",
    "asset_turnover",
    "earnings_per_share",
    "book_value_per_share",
    "total_debt_cr",
    "cash_from_operations_cr",
]

for column in numeric_columns:

    if column in df.columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )


# =========================================================
# ADD COMPANY NAME
# =========================================================

df = df.merge(
    companies[["id", "company_name"]],
    left_on="company_id",
    right_on="id",
    how="left"
)

df["company_name"] = (
    df["company_name"]
    .fillna(df["company_id"])
)


# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.header("Screening Filters")


preset = st.sidebar.selectbox(
    "Preset",
    [
        "Custom",
        "Quality",
        "Growth",
        "Debt-Free",
        "Dividend",
    ]
)


# =========================================================
# PRESETS
# =========================================================

presets = {

    "Custom": {
        "roe": 0,
        "de": 10,
        "opm": -100,
        "nmp": -100,
        "fcf": -100000,
        "icr": 0,
    },

    "Quality": {
        "roe": 15,
        "de": 1,
        "opm": 15,
        "nmp": 10,
        "fcf": 0,
        "icr": 3,
    },

    "Growth": {
        "roe": 15,
        "de": 2,
        "opm": 10,
        "nmp": 8,
        "fcf": 0,
        "icr": 2,
    },

    "Debt-Free": {
        "roe": 10,
        "de": 0.1,
        "opm": -100,
        "nmp": -100,
        "fcf": 0,
        "icr": 3,
    },

    "Dividend": {
        "roe": 8,
        "de": 2,
        "opm": -100,
        "nmp": -100,
        "fcf": 0,
        "icr": 0,
    },
}


p = presets[preset]


# =========================================================
# FILTER CONTROLS
# =========================================================

roe_min = st.sidebar.slider(
    "ROE Minimum (%)",
    0.0,
    100.0,
    float(p["roe"])
)


de_max = st.sidebar.slider(
    "D/E Maximum",
    0.0,
    10.0,
    float(p["de"])
)


opm_min = st.sidebar.slider(
    "Operating Margin Minimum (%)",
    -100.0,
    100.0,
    float(p["opm"])
)


npm_min = st.sidebar.slider(
    "Net Profit Margin Minimum (%)",
    -100.0,
    100.0,
    float(p["nmp"])
)


fcf_min = st.sidebar.slider(
    "Free Cash Flow Minimum (₹ Cr)",
    -100000.0,
    100000.0,
    float(p["fcf"])
)


icr_min = st.sidebar.slider(
    "Interest Coverage Minimum",
    0.0,
    150.0,
    float(p["icr"])
)


# =========================================================
# APPLY FILTERS
# =========================================================

filtered = df.copy()


filtered = filtered[
    filtered["return_on_equity_pct"].fillna(-999)
    >= roe_min
]


filtered = filtered[
    filtered["debt_to_equity"].fillna(999)
    <= de_max
]


filtered = filtered[
    filtered["operating_profit_margin_pct"].fillna(-999)
    >= opm_min
]


filtered = filtered[
    filtered["net_profit_margin_pct"].fillna(-999)
    >= npm_min
]


filtered = filtered[
    filtered["free_cash_flow_cr"].fillna(-999999)
    >= fcf_min
]


filtered = filtered[
    filtered["interest_coverage"].fillna(-999)
    >= icr_min
]


# =========================================================
# COMPOSITE SCORE
# =========================================================

score_columns = [
    "return_on_equity_pct",
    "net_profit_margin_pct",
    "operating_profit_margin_pct",
    "interest_coverage",
]


available_scores = [
    column
    for column in score_columns
    if column in filtered.columns
]


if not filtered.empty and available_scores:

    ranks = filtered[available_scores].rank(
        pct=True
    )

    filtered["composite_score"] = (
        ranks.mean(axis=1) * 100
    ).round(2)

else:

    filtered["composite_score"] = 0.0


# =========================================================
# RESULTS
# =========================================================

st.subheader(
    f"{len(filtered)} companies match your filters"
)


# =========================================================
# KPI SUMMARY
# =========================================================

k1, k2, k3, k4 = st.columns(4)

with k1:
    st.metric(
        "Companies",
        len(filtered)
    )

with k2:

    if not filtered.empty:
        st.metric(
            "Average ROE",
            f"{filtered['return_on_equity_pct'].mean():.2f}%"
        )
    else:
        st.metric("Average ROE", "N/A")


with k3:

    if not filtered.empty:
        st.metric(
            "Average D/E",
            f"{filtered['debt_to_equity'].mean():.2f}"
        )
    else:
        st.metric("Average D/E", "N/A")


with k4:

    if not filtered.empty:
        st.metric(
            "Average FCF",
            f"{filtered['free_cash_flow_cr'].mean():,.0f} Cr"
        )
    else:
        st.metric("Average FCF", "N/A")


# =========================================================
# DISPLAY TABLE
# =========================================================

if filtered.empty:

    st.warning(
        "No companies match the selected filters. "
        "Try relaxing the filters."
    )

else:

    display_columns = [
        "company_id",
        "company_name",
        "year",
        "composite_score",
        "return_on_equity_pct",
        "debt_to_equity",
        "net_profit_margin_pct",
        "operating_profit_margin_pct",
        "interest_coverage",
        "free_cash_flow_cr",
    ]

    display_columns = [
        column
        for column in display_columns
        if column in filtered.columns
    ]

    result = (
        filtered[display_columns]
        .sort_values(
            "composite_score",
            ascending=False
        )
        .copy()
    )

    result.columns = [
        "Ticker",
        "Company",
        "Year",
        "Score",
        "ROE (%)",
        "D/E",
        "Net Profit Margin (%)",
        "Operating Margin (%)",
        "Interest Coverage",
        "FCF (Cr)",
    ]

    st.dataframe(
        result,
        use_container_width=True,
        hide_index=True
    )


    # =====================================================
    # TOP 10
    # =====================================================

    st.subheader("Top 10 Companies")

    top10 = result.head(10)

    st.bar_chart(
        top10.set_index("Ticker")["Score"]
    )


# =========================================================
# CSV EXPORT
# =========================================================

if not filtered.empty:

    csv_data = result.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        "Download Results as CSV",
        data=csv_data,
        file_name="nifty100_screener_results.csv",
        mime="text/csv"
    )