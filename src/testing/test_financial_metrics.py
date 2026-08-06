from src.etl.loader import load_core_datasets


TEST_COMPANIES = [
    "TCS",
    "INFY",
    "RELIANCE"
]


def test_financial_metrics():

    datasets = load_core_datasets()

    pnl = datasets["profitandloss"].copy()

    for company in TEST_COMPANIES:

        print("\n" + "=" * 70)
        print(f"Company: {company}")
        print("=" * 70)

        company_data = pnl[pnl["company_id"] == company].copy()

        company_data["Operating Profit (Calculated)"] = (
            company_data["sales"] - company_data["expenses"]
        )

        company_data["OPM (Calculated)"] = (
            company_data["Operating Profit (Calculated)"]
            / company_data["sales"]
        ) * 100

        company_data["Net Profit Margin"] = (
            company_data["net_profit"]
            / company_data["sales"]
        ) * 100

        print(
            company_data[
                [
                    "year",
                    "sales",
                    "expenses",
                    "operating_profit",
                    "Operating Profit (Calculated)",
                    "opm_percentage",
                    "OPM (Calculated)",
                    "net_profit",
                    "Net Profit Margin",
                ]
            ]
        )


if __name__ == "__main__":
    test_financial_metrics()