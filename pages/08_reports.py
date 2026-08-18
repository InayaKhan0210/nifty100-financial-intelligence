import streamlit as st
import pandas as pd

from src.dashboard.utils.db import get_companies
from src.etl.loader import load_core_datasets


st.title("Annual Reports")
st.caption("Access annual reports for Nifty 100 companies.")


# --------------------------------------------------
# Load documents
# --------------------------------------------------

datasets = load_core_datasets()
documents = datasets["documents"].copy()

companies = get_companies()


# --------------------------------------------------
# Company selector
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
# Filter reports
# --------------------------------------------------

reports = documents[
    documents["company_id"].astype(str) == selected_ticker
].copy()


if reports.empty:
    st.warning(
        "No annual reports available for this company."
    )
    st.stop()


# --------------------------------------------------
# Clean data
# --------------------------------------------------

reports["Year"] = pd.to_numeric(
    reports["Year"],
    errors="coerce"
)

reports = reports.dropna(
    subset=["Year"]
)

reports["Year"] = reports["Year"].astype(int)

reports = reports.sort_values(
    "Year",
    ascending=False
)


# --------------------------------------------------
# Summary
# --------------------------------------------------

latest_year = reports["Year"].max()

c1, c2, c3 = st.columns(3)

c1.metric(
    "Reports Available",
    len(reports)
)

c2.metric(
    "Latest Report",
    latest_year
)

c3.metric(
    "Company",
    selected_ticker
)


st.divider()


# --------------------------------------------------
# Latest annual report
# --------------------------------------------------

st.subheader("Latest Annual Report")

latest = reports.iloc[0]

st.write(
    f"**Annual Report {latest['Year']}**"
)

st.link_button(
    "Open Latest Annual Report",
    str(latest["Annual_Report"])
)


st.divider()


# --------------------------------------------------
# Historical reports
# --------------------------------------------------

st.subheader("Historical Annual Reports")

for _, row in reports.iterrows():

    year = row["Year"]
    url = row["Annual_Report"]

    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(
            f"Annual Report {year}"
        )

    with col2:
        st.link_button(
            "Open Report",
            str(url)
        )


st.divider()


# --------------------------------------------------
# Table
# --------------------------------------------------

st.subheader("Report Archive")

table = reports[
    ["Year", "Annual_Report"]
].copy()

table = table.rename(
    columns={
        "Year": "Year",
        "Annual_Report": "Annual Report URL",
    }
)

st.dataframe(
    table,
    use_container_width=True,
    hide_index=True,
)