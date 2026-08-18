import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_companies,
    get_pl,
    get_ratios,
)


st.title("Trend Analysis")
st.caption("Historical financial trends for Nifty 100 companies.")


# --------------------------------------------------
# Company selection
# --------------------------------------------------

companies = get_companies()

tickers = (
    companies["id"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_ticker = st.selectbox(
    "Select Company",
    sorted(tickers),
)


if not selected_ticker:
    st.stop()


# --------------------------------------------------
# Load data
# --------------------------------------------------

pnl = get_pl(selected_ticker)
ratios = get_ratios(selected_ticker)


if pnl.empty and ratios.empty:
    st.warning("No financial data available for this company.")
    st.stop()


# --------------------------------------------------
# Prepare P&L
# --------------------------------------------------

if not pnl.empty:

    pnl = pnl.copy()

    pnl["year"] = pnl["year"].astype(str)

    # Keep one record per year
    pnl = pnl.drop_duplicates(
        subset=["company_id", "year"],
        keep="first",
    )

    # Remove TTM from historical trend
    pnl = pnl[
        pnl["year"].str.upper() != "TTM"
    ]

    # Extract numeric year for sorting
    pnl["_year_num"] = pd.to_numeric(
        pnl["year"].str.extract(r"(\d{4})")[0],
        errors="coerce",
    )

    pnl = pnl.sort_values("_year_num")


# --------------------------------------------------
# Prepare ratios
# --------------------------------------------------

if not ratios.empty:

    ratios = ratios.copy()

    ratios["year"] = ratios["year"].astype(str)

    ratios = ratios.drop_duplicates(
        subset=["company_id", "year"],
        keep="first",
    )

    ratios = ratios[
        ratios["year"].str.upper() != "TTM"
    ]

    ratios["_year_num"] = pd.to_numeric(
        ratios["year"].str.extract(r"(\d{4})")[0],
        errors="coerce",
    )

    ratios = ratios.sort_values("_year_num")


# --------------------------------------------------
# Helper
# --------------------------------------------------

def numeric(series):
    return pd.to_numeric(
        series,
        errors="coerce",
    )


def make_line_chart(
    dataframe,
    y_column,
    title,
    y_title,
):

    if dataframe.empty or y_column not in dataframe.columns:
        st.info(f"{title} data unavailable.")
        return

    chart_data = dataframe[
        ["year", y_column]
    ].copy()

    chart_data[y_column] = numeric(
        chart_data[y_column]
    )

    chart_data = chart_data.dropna(
        subset=[y_column]
    )

    if chart_data.empty:
        st.info(f"{title} data unavailable.")
        return

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_data["year"],
            y=chart_data[y_column],
            mode="lines+markers",
            name=title,
        )
    )

    fig.update_layout(
        height=400,
        xaxis_title="Year",
        yaxis_title=y_title,
        hovermode="x unified",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )


# --------------------------------------------------
# Page header
# --------------------------------------------------

st.subheader(
    f"{selected_ticker} — Historical Trends"
)


# --------------------------------------------------
# Revenue and Profit Trends
# --------------------------------------------------

st.subheader("Revenue Trend")

if not pnl.empty:
    make_line_chart(
        pnl,
        "sales",
        "Revenue",
        "₹ Cr",
    )
else:
    st.info("Revenue data unavailable.")


st.subheader("Net Profit Trend")

if not pnl.empty:
    make_line_chart(
        pnl,
        "net_profit",
        "Net Profit",
        "₹ Cr",
    )
else:
    st.info("Net profit data unavailable.")


st.subheader("Operating Profit Trend")

if not pnl.empty:
    make_line_chart(
        pnl,
        "operating_profit",
        "Operating Profit",
        "₹ Cr",
    )
else:
    st.info("Operating profit data unavailable.")


# --------------------------------------------------
# Profitability Ratios
# --------------------------------------------------

st.subheader("ROE Trend")

if not ratios.empty:
    make_line_chart(
        ratios,
        "return_on_equity_pct",
        "ROE",
        "%",
    )
else:
    st.info("ROE data unavailable.")


st.subheader("Net Profit Margin Trend")

if not ratios.empty:
    make_line_chart(
        ratios,
        "net_profit_margin_pct",
        "Net Profit Margin",
        "%",
    )
else:
    st.info("Net profit margin data unavailable.")


st.subheader("Operating Profit Margin Trend")

if not ratios.empty:
    make_line_chart(
        ratios,
        "operating_profit_margin_pct",
        "Operating Profit Margin",
        "%",
    )
else:
    st.info("Operating profit margin data unavailable.")


# --------------------------------------------------
# Leverage
# --------------------------------------------------

st.subheader("Debt / Equity Trend")

if not ratios.empty:
    make_line_chart(
        ratios,
        "debt_to_equity",
        "Debt / Equity",
        "Ratio",
    )
else:
    st.info("Debt / Equity data unavailable.")


# --------------------------------------------------
# Cash Flow
# --------------------------------------------------

st.subheader("Free Cash Flow Trend")

if not ratios.empty:
    make_line_chart(
        ratios,
        "free_cash_flow_cr",
        "Free Cash Flow",
        "₹ Cr",
    )
else:
    st.info("Free cash flow data unavailable.")


# --------------------------------------------------
# Historical Financial Table
# --------------------------------------------------

st.subheader("Historical Financial Data")


if not pnl.empty:

    table_columns = [
        "year",
        "sales",
        "operating_profit",
        "net_profit",
        "eps",
        "dividend_payout",
    ]

    available = [
        column
        for column in table_columns
        if column in pnl.columns
    ]

    table = pnl[available].copy()

    rename_map = {
        "year": "Year",
        "sales": "Revenue (₹ Cr)",
        "operating_profit": "Operating Profit (₹ Cr)",
        "net_profit": "Net Profit (₹ Cr)",
        "eps": "EPS",
        "dividend_payout": "Dividend Payout (%)",
    }

    table = table.rename(
        columns=rename_map
    )

    st.dataframe(
        table,
        use_container_width=True,
        hide_index=True,
    )