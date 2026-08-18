import streamlit as st
import pandas as pd

from src.dashboard.utils.db import (
    get_peers,
    get_ratios,
)

st.title("Peer Comparison")
st.caption("Compare companies within the same peer group using key financial metrics.")


# --------------------------------------------------
# Load peer groups
# --------------------------------------------------

peer_data = get_peers.__wrapped__ if hasattr(get_peers, "__wrapped__") else None

from src.etl.loader import load_core_datasets

datasets = load_core_datasets()
peers = datasets["peer_groups"].copy()


if peers.empty:
    st.warning("Peer group data is unavailable.")
    st.stop()


# --------------------------------------------------
# Peer group selection
# --------------------------------------------------

peer_groups = sorted(
    peers["peer_group_name"]
    .dropna()
    .astype(str)
    .unique()
)

selected_group = st.selectbox(
    "Select Peer Group",
    peer_groups,
)


# --------------------------------------------------
# Companies in selected peer group
# --------------------------------------------------

group_peers = peers[
    peers["peer_group_name"].astype(str) == selected_group
].copy()


if group_peers.empty:
    st.warning("No companies found in this peer group.")
    st.stop()


benchmark_rows = group_peers[
    group_peers["is_benchmark"] == True
]

if not benchmark_rows.empty:
    benchmark = benchmark_rows.iloc[0]["company_id"]
else:
    benchmark = None


# --------------------------------------------------
# Header information
# --------------------------------------------------

st.subheader(selected_group)

if benchmark:
    st.info(f"Benchmark Company: **{benchmark}**")

st.write(
    f"{len(group_peers)} companies in this peer group."
)


# --------------------------------------------------
# Build comparison dataset
# --------------------------------------------------

records = []

for _, peer in group_peers.iterrows():

    ticker = str(peer["company_id"])

    ratios = get_ratios(ticker)

    if ratios.empty:
        continue

    ratios = ratios.copy()
    ratios["year"] = ratios["year"].astype(str)

    # Remove duplicate company-year records
    ratios = ratios.drop_duplicates(
        subset=["company_id", "year"],
        keep="first",
    )

    # Latest available record
    latest = ratios.iloc[-1]

    records.append(
        {
            "Company": ticker,
            "Benchmark": "Yes" if ticker == benchmark else "",
            "Year": latest.get("year"),

            "ROE (%)": latest.get(
                "return_on_equity_pct"
            ),

            "D/E": latest.get(
                "debt_to_equity"
            ),

            "OPM (%)": latest.get(
                "operating_profit_margin_pct"
            ),

            "NPM (%)": latest.get(
                "net_profit_margin_pct"
            ),

            "Interest Coverage": latest.get(
                "interest_coverage"
            ),

            "FCF (₹ Cr)": latest.get(
                "free_cash_flow_cr"
            ),
        }
    )


comparison = pd.DataFrame(records)


if comparison.empty:
    st.warning(
        "No financial ratio data available for this peer group."
    )
    st.stop()


# --------------------------------------------------
# Numeric conversion
# --------------------------------------------------

numeric_columns = [
    "ROE (%)",
    "D/E",
    "OPM (%)",
    "NPM (%)",
    "Interest Coverage",
    "FCF (₹ Cr)",
]

for column in numeric_columns:
    comparison[column] = pd.to_numeric(
        comparison[column],
        errors="coerce",
    )


# --------------------------------------------------
# Sort benchmark first
# --------------------------------------------------

comparison["_benchmark_sort"] = (
    comparison["Benchmark"] != "Yes"
)

comparison = comparison.sort_values(
    "_benchmark_sort"
).drop(
    columns="_benchmark_sort"
)


# --------------------------------------------------
# KPI summary
# --------------------------------------------------

st.subheader("Peer Group Summary")

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Companies",
    len(comparison),
)

c2.metric(
    "Average ROE",
    f"{comparison['ROE (%)'].mean():.2f}%",
)

c3.metric(
    "Average D/E",
    f"{comparison['D/E'].mean():.2f}",
)

c4.metric(
    "Average OPM",
    f"{comparison['OPM (%)'].mean():.2f}%",
)


st.divider()


# --------------------------------------------------
# Comparison table
# --------------------------------------------------

st.subheader("Financial Comparison")

st.dataframe(
    comparison,
    use_container_width=True,
    hide_index=True,
)


# --------------------------------------------------
# Visual comparison
# --------------------------------------------------

st.subheader("ROE Comparison")

roe_chart = comparison[
    ["Company", "ROE (%)"]
].dropna()

roe_chart = roe_chart.set_index("Company")

st.bar_chart(
    roe_chart,
    use_container_width=True,
)


st.subheader("Debt / Equity Comparison")

de_chart = comparison[
    ["Company", "D/E"]
].dropna()

de_chart = de_chart.set_index("Company")

st.bar_chart(
    de_chart,
    use_container_width=True,
)


# --------------------------------------------------
# Benchmark analysis
# --------------------------------------------------

if benchmark and benchmark in comparison["Company"].values:

    benchmark_row = comparison[
        comparison["Company"] == benchmark
    ].iloc[0]

    st.subheader("Benchmark Company")

    b1, b2, b3, b4 = st.columns(4)

    b1.metric(
        "ROE",
        f"{benchmark_row['ROE (%)']:.2f}%"
        if pd.notna(benchmark_row["ROE (%)"])
        else "N/A",
    )

    b2.metric(
        "D/E",
        f"{benchmark_row['D/E']:.2f}"
        if pd.notna(benchmark_row["D/E"])
        else "N/A",
    )

    b3.metric(
        "OPM",
        f"{benchmark_row['OPM (%)']:.2f}%"
        if pd.notna(benchmark_row["OPM (%)"])
        else "N/A",
    )

    b4.metric(
        "FCF",
        f"₹{benchmark_row['FCF (₹ Cr)']:.2f} Cr"
        if pd.notna(benchmark_row["FCF (₹ Cr)"])
        else "N/A",
    )