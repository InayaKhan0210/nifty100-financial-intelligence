import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_companies,
    get_cf,
    get_ratios,
)

st.title("Capital Allocation")
st.caption(
    "Analyze how companies generate, invest, and distribute capital."
)

companies = get_companies()

# --------------------------------------------------
# Company selection
# --------------------------------------------------

tickers = (
    companies["id"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)

selected_ticker = st.selectbox(
    "Select Company",
    tickers,
)

if not selected_ticker:
    st.stop()

# --------------------------------------------------
# Load data
# --------------------------------------------------

cf = get_cf(selected_ticker)
ratios = get_ratios(selected_ticker)

if cf.empty:
    st.warning("Cash flow data unavailable for this company.")
    st.stop()

cf = cf.copy()
cf["year"] = cf["year"].astype(str)

for col in [
    "operating_activity",
    "investing_activity",
    "financing_activity",
    "net_cash_flow",
]:
    if col in cf.columns:
        cf[col] = pd.to_numeric(
            cf[col],
            errors="coerce"
        )

cf = cf.sort_values("year")

# --------------------------------------------------
# Latest available year
# --------------------------------------------------

latest_cf = cf.iloc[-1]

operating = latest_cf.get("operating_activity")
investing = latest_cf.get("investing_activity")
financing = latest_cf.get("financing_activity")
net_cash = latest_cf.get("net_cash_flow")

# --------------------------------------------------
# KPI cards
# --------------------------------------------------

st.subheader("Latest Capital Allocation")

k1, k2, k3, k4 = st.columns(4)

def format_cr(value):
    if pd.isna(value):
        return "N/A"
    return f"₹{value:,.0f} Cr"

k1.metric(
    "Operating Cash Flow",
    format_cr(operating)
)

k2.metric(
    "Investing Cash Flow",
    format_cr(investing)
)

k3.metric(
    "Financing Cash Flow",
    format_cr(financing)
)

k4.metric(
    "Net Cash Flow",
    format_cr(net_cash)
)

st.caption(f"Latest available period: {latest_cf['year']}")

st.divider()

# --------------------------------------------------
# Cash Flow Trend
# --------------------------------------------------

st.subheader("Cash Flow Trend")

fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=cf["year"],
        y=cf["operating_activity"],
        name="Operating",
    )
)

fig.add_trace(
    go.Bar(
        x=cf["year"],
        y=cf["investing_activity"],
        name="Investing",
    )
)

fig.add_trace(
    go.Bar(
        x=cf["year"],
        y=cf["financing_activity"],
        name="Financing",
    )
)

fig.update_layout(
    barmode="group",
    height=450,
    xaxis_title="Year",
    yaxis_title="Cash Flow (₹ Cr)",
)

st.plotly_chart(
    fig,
    use_container_width=True,
)

# --------------------------------------------------
# Free Cash Flow & Capex
# --------------------------------------------------

st.subheader("Free Cash Flow & Capital Expenditure")

if not ratios.empty:

    ratios = ratios.copy()
    ratios["year"] = ratios["year"].astype(str)

    ratios = ratios.drop_duplicates(
        subset=["company_id", "year"],
        keep="first"
    )

    ratios = ratios.sort_values("year")

    ratios["free_cash_flow_cr"] = pd.to_numeric(
        ratios["free_cash_flow_cr"],
        errors="coerce"
    )

    ratios["capex_cr"] = pd.to_numeric(
        ratios["capex_cr"],
        errors="coerce"
    )

    fig2 = go.Figure()

    fig2.add_trace(
        go.Scatter(
            x=ratios["year"],
            y=ratios["free_cash_flow_cr"],
            mode="lines+markers",
            name="Free Cash Flow",
        )
    )

    fig2.add_trace(
        go.Scatter(
            x=ratios["year"],
            y=ratios["capex_cr"],
            mode="lines+markers",
            name="Capex",
        )
    )

    fig2.update_layout(
        height=400,
        xaxis_title="Year",
        yaxis_title="₹ Cr",
    )

    st.plotly_chart(
        fig2,
        use_container_width=True,
    )

else:
    st.info("Financial ratio data unavailable.")

# --------------------------------------------------
# Capital Allocation Table
# --------------------------------------------------

st.subheader("Capital Allocation History")

display_columns = [
    "year",
    "operating_activity",
    "investing_activity",
    "financing_activity",
    "net_cash_flow",
]

display_columns = [
    col for col in display_columns
    if col in cf.columns
]

table = cf[display_columns].sort_values(
    "year",
    ascending=False
)

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True,
)

st.caption(
    "Positive investing cash flow may represent asset sales or investment proceeds; "
    "negative investing cash flow generally indicates investment or capital expenditure."
)