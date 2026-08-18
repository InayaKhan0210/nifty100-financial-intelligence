import streamlit as st
import pandas as pd
import plotly.express as px

from src.dashboard.utils.db import (
    get_companies,
    get_sectors,
    get_ratios,
)


st.title("Sector Analysis")
st.caption("Analyze financial performance across Nifty 100 sectors.")


# --------------------------------------------------
# Load data
# --------------------------------------------------

sectors = get_sectors()
companies = get_companies()


if sectors.empty:
    st.warning("Sector data is unavailable.")
    st.stop()


# --------------------------------------------------
# Prepare sector data
# --------------------------------------------------

sectors = sectors.copy()

sectors["company_id"] = (
    sectors["company_id"]
    .astype(str)
)

sectors["broad_sector"] = (
    sectors["broad_sector"]
    .astype(str)
)

sectors["index_weight_pct"] = pd.to_numeric(
    sectors["index_weight_pct"],
    errors="coerce",
)


# --------------------------------------------------
# Sector selector
# --------------------------------------------------

sector_list = sorted(
    sectors["broad_sector"]
    .dropna()
    .unique()
)

selected_sector = st.selectbox(
    "Select Sector",
    sector_list,
)


sector_companies = sectors[
    sectors["broad_sector"] == selected_sector
].copy()


if sector_companies.empty:
    st.warning("No companies found in this sector.")
    st.stop()


# --------------------------------------------------
# Build financial dataset
# --------------------------------------------------

records = []

for ticker in sector_companies["company_id"]:

    ratios = get_ratios(ticker)

    if ratios.empty:
        continue

    ratios = ratios.copy()

    ratios["year"] = ratios["year"].astype(str)

    ratios = ratios.drop_duplicates(
        subset=["company_id", "year"],
        keep="first",
    )

    ratios = ratios[
        ratios["year"].str.upper() != "TTM"
    ]

    if ratios.empty:
        continue

    ratios["_year_num"] = pd.to_numeric(
        ratios["year"].str.extract(r"(\d{4})")[0],
        errors="coerce",
    )

    ratios = ratios.sort_values("_year_num")

    latest = ratios.iloc[-1]

    records.append(
        {
            "company_id": ticker,
            "roe": latest.get(
                "return_on_equity_pct"
            ),
            "de": latest.get(
                "debt_to_equity"
            ),
            "opm": latest.get(
                "operating_profit_margin_pct"
            ),
            "npm": latest.get(
                "net_profit_margin_pct"
            ),
            "fcf": latest.get(
                "free_cash_flow_cr"
            ),
        }
    )


financials = pd.DataFrame(records)


# --------------------------------------------------
# Merge sector + financial data
# --------------------------------------------------

analysis = sector_companies.merge(
    financials,
    on="company_id",
    how="left",
)


for column in [
    "roe",
    "de",
    "opm",
    "npm",
    "fcf",
]:

    analysis[column] = pd.to_numeric(
        analysis[column],
        errors="coerce",
    )


# --------------------------------------------------
# Header
# --------------------------------------------------

st.subheader(selected_sector)

st.write(
    f"{len(sector_companies)} companies in this sector."
)


# --------------------------------------------------
# Sector KPIs
# --------------------------------------------------

c1, c2, c3, c4 = st.columns(4)


c1.metric(
    "Companies",
    len(sector_companies),
)


c2.metric(
    "Index Weight",
    f"{sector_companies['index_weight_pct'].sum():.2f}%",
)


c3.metric(
    "Average ROE",
    (
        f"{analysis['roe'].mean():.2f}%"
        if analysis["roe"].notna().any()
        else "N/A"
    ),
)


c4.metric(
    "Average D/E",
    (
        f"{analysis['de'].mean():.2f}"
        if analysis["de"].notna().any()
        else "N/A"
    ),
)


st.divider()


# --------------------------------------------------
# Financial summary
# --------------------------------------------------

st.subheader("Sector Financial Summary")


summary_columns = [
    "company_id",
    "sub_sector",
    "index_weight_pct",
    "roe",
    "de",
    "opm",
    "npm",
    "fcf",
]


summary = analysis[
    [
        column
        for column in summary_columns
        if column in analysis.columns
    ]
].copy()


summary = summary.rename(
    columns={
        "company_id": "Company",
        "sub_sector": "Sub-sector",
        "index_weight_pct": "Index Weight (%)",
        "roe": "ROE (%)",
        "de": "D/E",
        "opm": "OPM (%)",
        "npm": "NPM (%)",
        "fcf": "FCF (₹ Cr)",
    }
)


summary = summary.sort_values(
    "ROE (%)",
    ascending=False,
    na_position="last",
)


st.dataframe(
    summary,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Top companies
# --------------------------------------------------

st.subheader("Top Companies by ROE")


top_roe = analysis[
    [
        "company_id",
        "roe",
    ]
].dropna()


top_roe = top_roe.sort_values(
    "roe",
    ascending=False,
).head(10)


if not top_roe.empty:

    top_roe = top_roe.rename(
        columns={
            "company_id": "Company",
            "roe": "ROE (%)",
        }
    )

    st.dataframe(
        top_roe,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info("ROE data unavailable.")


# --------------------------------------------------
# ROE chart
# --------------------------------------------------

st.subheader("ROE Comparison")


if not top_roe.empty:

    fig = px.bar(
        top_roe,
        x="Company",
        y="ROE (%)",
        title=f"Top ROE Companies — {selected_sector}",
    )

    fig.update_layout(
        height=450,
        xaxis_title="Company",
        yaxis_title="ROE (%)",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# --------------------------------------------------
# Sub-sector breakdown
# --------------------------------------------------

st.subheader("Sub-sector Breakdown")


subsector = (
    sector_companies
    .groupby("sub_sector")
    .agg(
        Companies=("company_id", "count"),
        Index_Weight=("index_weight_pct", "sum"),
    )
    .reset_index()
)


subsector = subsector.rename(
    columns={
        "sub_sector": "Sub-sector",
        "Index_Weight": "Index Weight (%)",
    }
)


st.dataframe(
    subsector,
    use_container_width=True,
    hide_index=True,
)