import streamlit as st
import pandas as pd

from src.dashboard.utils.db import get_companies, get_ratios, get_sectors


st.title("Nifty 100 Financial Intelligence Overview")

selected_year = "Mar 2024"

companies = get_companies()
sectors = get_sectors()


# ---------------------------------------------------------
# Build company financial metrics
# ---------------------------------------------------------

records = []

for ticker in companies["id"].dropna().unique():

    ratios = get_ratios(ticker, selected_year)

    if ratios.empty:
        continue

    row = ratios.iloc[0]

    records.append(
        {
            "company_id": ticker,
            "roe": row.get("return_on_equity_pct"),
            "de": row.get("debt_to_equity"),
            "fcf": row.get("free_cash_flow_cr"),
        }
    )


metrics = pd.DataFrame(records)


# ---------------------------------------------------------
# Market Overview
# ---------------------------------------------------------

st.subheader(f"Market Overview — {selected_year}")

if not metrics.empty:

    avg_roe = metrics["roe"].dropna().mean()
    median_de = metrics["de"].dropna().median()
    debt_free = (metrics["de"].fillna(0) == 0).sum()

else:

    avg_roe = None
    median_de = None
    debt_free = 0


col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Average ROE",
        f"{avg_roe:.2f}%" if avg_roe is not None else "N/A"
    )

with col2:
    st.metric(
        "Median D/E",
        f"{median_de:.2f}" if median_de is not None else "N/A"
    )

with col3:
    st.metric(
        "Total Companies",
        len(companies)
    )

with col4:
    st.metric(
        "Debt-Free Companies",
        debt_free
    )


# ---------------------------------------------------------
# Sector Breakdown
# ---------------------------------------------------------

st.subheader("Sector Breakdown")

if not sectors.empty:

    sector_counts = (
        sectors.groupby("broad_sector")
        .size()
        .reset_index(name="companies")
        .sort_values("companies", ascending=False)
    )

    st.bar_chart(
        sector_counts.set_index("broad_sector")["companies"]
    )

else:
    st.info("Sector data unavailable.")


# ---------------------------------------------------------
# Top 5 Companies by ROE
# ---------------------------------------------------------

st.subheader("Top 5 Companies by ROE")

if not metrics.empty:

    top_roe = (
        metrics
        .dropna(subset=["roe"])
        .sort_values("roe", ascending=False)
        .head(5)
        .copy()
    )

    top_roe = top_roe.merge(
        companies[["id", "company_name"]],
        left_on="company_id",
        right_on="id",
        how="left"
    )

    top_roe = top_roe[
        ["company_id", "company_name", "roe", "de", "fcf"]
    ]

    top_roe.columns = [
        "Ticker",
        "Company",
        "ROE (%)",
        "D/E",
        "FCF (Cr)"
    ]

    st.dataframe(
        top_roe,
        use_container_width=True,
        hide_index=True
    )

else:
    st.info("No ratio data available for this year.")