from pathlib import Path
from src.etl.loader import load_core_datasets

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


def calculate_operating_profit_margin():
    """
    Calculate Operating Profit Margin (OPM)
    and compare it with the dataset value.
    """

    datasets = load_core_datasets()

    pnl = datasets["profitandloss"].copy()

    # Calculate OPM
    pnl["opm_calculated"] = (
        pnl["operating_profit"] / pnl["sales"]
    ) * 100

    # Round to 2 decimal places
    pnl["opm_calculated"] = pnl["opm_calculated"].round(2)

    # Compare with dataset value
    pnl["opm_match"] = (
        pnl["opm_percentage"].round(2)
        == pnl["opm_calculated"]
    )

    return pnl


if __name__ == "__main__":

    result = calculate_operating_profit_margin()

    # Save results
    result.to_csv(
        OUTPUT_PATH / "operating_profit_margin.csv",
        index=False
    )

    # Display comparison
    print(
        result[
            [
                "company_id",
                "year",
                "sales",
                "operating_profit",
                "opm_percentage",
                "opm_calculated",
                "opm_match",
            ]
        ].head(10)
    )

    # Summary
    total_rows = len(result)
    matched_rows = result["opm_match"].sum()
    unmatched_rows = total_rows - matched_rows

    print("\n========== Summary ==========")
    print(f"Total Records     : {total_rows}")
    print(f"Matched Records   : {matched_rows}")
    print(f"Unmatched Records : {unmatched_rows}")

    print("\noperating_profit_margin.csv created successfully!")