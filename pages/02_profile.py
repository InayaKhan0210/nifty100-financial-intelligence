import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.dashboard.utils.db import (
    get_companies,
    get_ratios,
    get_pl,
    get_sectors,
)


st.title("Company Profile")

companies = get_companies()
sectors = get_sectors()


# ---------------------------------------------------------
# Company selection
# ---------------------------------------------------------

search_options = companies["id"].dropna().astype(str).tolist()

selected_ticker = st.selectbox(
    "Search Company / Ticker",
    search_options,
)


company_rows = companies[
    companies["id"].astype(str) == selected_ticker
]

if company_rows.empty:
    st.warning("Company not found.")
    st.stop()

company = company_rows.iloc[0]


# ---------------------------------------------------------
# Company information
# ---------------------------------------------------------

company_name = company.get(
    "company_name",
    selected_ticker
)

about = company.get("about_company", "")

sector_row = sectors[
    sectors["company_id"].astype(str) == selected_ticker
]

if sector_row.empty:
    sector_row = sectors[
        sectors["id"].astype(str) == selected_ticker
    ]

if not sector_row.empty:

    sector_info = sector_row.iloc[0]

    sector = sector_info.get(
        "broad_sector",
        "N/A"
    )

    sub_sector = sector_info.get(
        "sub_sector",
        "N/A"
    )

else:

    sector = "N/A"
    sub_sector = "N/A"


# ---------------------------------------------------------
# Company header
# ---------------------------------------------------------

st.subheader(company_name)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.write("**Ticker**")
    st.write(selected_ticker)

with c2:
    st.write("**Sector**")
    st.write(sector)

with c3:
    st.write("**Sub-sector**")
    st.write(sub_sector)

with c4:
    st.write("**Face Value**")
    st.write(
        company.get("face_value", "N/A")
    )


if pd.notna(about) and str(about).strip():

    st.markdown("### About the Company")
    st.write(about)


st.divider()


# ---------------------------------------------------------
# Financial data
# ---------------------------------------------------------

ratios = get_ratios(selected_ticker)
pnl = get_pl(selected_ticker)


if ratios.empty:

    st.warning(
        "Financial ratio data is not available for this company."
    )

else:

    ratios = ratios.copy()

    ratios["year"] = ratios["year"].astype(str)

    ratios = ratios.drop_duplicates(
        subset=["year"],
        keep="first"
    )

    ratios = ratios.sort_values("year")

    latest = ratios.iloc[-1]

    latest_year = latest["year"]


    # -----------------------------------------------------
    # KPI calculations
    # -----------------------------------------------------

    roe = latest.get(
        "return_on_equity_pct"
    )

    nmp = latest.get(
        "net_profit_margin_pct"
    )

    de = latest.get(
        "debt_to_equity"
    )

    fcf = latest.get(
        "free_cash_flow_cr"
    )


    # ROCE comes directly from companies dataset
    roce = company.get(
        "roce_percentage"
    )


    # Revenue CAGR
    revenue_cagr = None

    if not pnl.empty:

        pnl_cagr = pnl.copy()

        pnl_cagr["year"] = (
            pnl_cagr["year"]
            .astype(str)
        )

        pnl_cagr["sales"] = pd.to_numeric(
            pnl_cagr["sales"],
            errors="coerce"
        )

        pnl_cagr = pnl_cagr.dropna(
            subset=["sales"]
        )

        # Remove duplicate years
        pnl_cagr = pnl_cagr.drop_duplicates(
            subset=["year"],
            keep="last"
        )

        if len(pnl_cagr) >= 6:

            first_revenue = pnl_cagr.iloc[-6]["sales"]
            latest_revenue = pnl_cagr.iloc[-1]["sales"]

            if (
                first_revenue > 0
                and latest_revenue > 0
            ):

                revenue_cagr = (
                    (latest_revenue / first_revenue)
                    ** (1 / 5)
                    - 1
                ) * 100


    # -----------------------------------------------------
    # Formatting
    # -----------------------------------------------------

    def format_value(value, suffix=""):

        value = pd.to_numeric(
            pd.Series([value]),
            errors="coerce"
        ).iloc[0]

        if pd.isna(value):
            return "N/A"

        return f"{value:.2f}{suffix}"


    # -----------------------------------------------------
    # KPI cards
    # -----------------------------------------------------

    st.subheader(
        f"Key Financial Metrics — {latest_year}"
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    with k1:
        st.metric(
            "ROE",
            format_value(roe, "%")
        )

    with k2:
        st.metric(
            "ROCE",
            format_value(roce, "%")
        )

    with k3:
        st.metric(
            "Net Profit Margin",
            format_value(nmp, "%")
        )

    with k4:
        st.metric(
            "Debt / Equity",
            format_value(de)
        )

    with k5:
        st.metric(
            "Revenue CAGR 5Y",
            format_value(
                revenue_cagr,
                "%"
            )
        )

    with k6:
        st.metric(
            "Free Cash Flow",
            format_value(
                fcf,
                " Cr"
            )
        )


    st.divider()


    # -----------------------------------------------------
    # Financial Ratio Table
    # -----------------------------------------------------

    st.subheader("Financial Ratios")

    ratio_display = ratios[
        [
            "year",
            "net_profit_margin_pct",
            "operating_profit_margin_pct",
            "return_on_equity_pct",
            "debt_to_equity",
            "interest_coverage",
            "asset_turnover",
            "free_cash_flow_cr",
        ]
    ].copy()

    ratio_display.columns = [
        "Year",
        "Net Profit Margin (%)",
        "Operating Margin (%)",
        "ROE (%)",
        "Debt / Equity",
        "Interest Coverage",
        "Asset Turnover",
        "FCF (Cr)",
    ]

    st.dataframe(
        ratio_display,
        use_container_width=True,
        hide_index=True
    )


    # -----------------------------------------------------
    # Revenue & Net Profit Trend
    # -----------------------------------------------------

    st.subheader(
        "Revenue and Net Profit — 10 Year Trend"
    )

    if not pnl.empty:

        chart_df = pnl.copy()

        chart_df["year"] = (
            chart_df["year"]
            .astype(str)
        )

        chart_df["sales"] = pd.to_numeric(
            chart_df["sales"],
            errors="coerce"
        )

        chart_df["net_profit"] = pd.to_numeric(
            chart_df["net_profit"],
            errors="coerce"
        )

        chart_df = chart_df.drop_duplicates(
            subset=["year"],
            keep="last"
        )

        chart_df = (
            chart_df
            .sort_values("year")
            .tail(10)
        )

        fig = go.Figure()

        fig.add_trace(
            go.Bar(
                x=chart_df["year"],
                y=chart_df["sales"],
                name="Revenue"
            )
        )

        fig.add_trace(
            go.Bar(
                x=chart_df["year"],
                y=chart_df["net_profit"],
                name="Net Profit"
            )
        )

        fig.update_layout(
            barmode="group",
            height=450,
            xaxis_title="Year",
            yaxis_title="Amount (₹ Cr)"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "Profit & Loss data unavailable."
        )


    # -----------------------------------------------------
    # ROE / ROCE Trend
    # -----------------------------------------------------

    st.subheader("ROE & ROCE Trend")

    chart_ratios = ratios.copy()

    chart_ratios["roe"] = pd.to_numeric(
        chart_ratios[
            "return_on_equity_pct"
        ],
        errors="coerce"
    )

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_ratios["year"],
            y=chart_ratios["roe"],
            mode="lines+markers",
            name="ROE"
        )
    )

    # ROCE is a company-level value rather than
    # a historical ratio series in the current dataset.
    if pd.notna(roce):

        fig.add_hline(
            y=float(roce),
            annotation_text=f"ROCE: {float(roce):.2f}%",
            annotation_position="top right"
        )

    fig.update_layout(
        height=400,
        xaxis_title="Year",
        yaxis_title="Percentage (%)"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ---------------------------------------------------------
# Company links
# ---------------------------------------------------------

st.subheader("Company Resources")

website = company.get("website")
nse = company.get("nse_profile")
bse = company.get("bse_profile")

links = []

if pd.notna(website) and str(website).strip():
    links.append(("Company Website", website))

if pd.notna(nse) and str(nse).strip():
    links.append(("NSE Profile", nse))

if pd.notna(bse) and str(bse).strip():
    links.append(("BSE Profile", bse))

if links:

    for label, url in links:

        st.markdown(
            f"**{label}:** {url}"
        )

else:

    st.info(
        "Company links unavailable."
    )