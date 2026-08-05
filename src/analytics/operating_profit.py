from pathlib import Path
from src.etl.loader import load_core_datasets

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


def calculate_operating_profit():
    """
    Calculate Operating Profit and compare it with
    the value available in the dataset.
    """

    datasets = load_core_datasets()

    pnl = datasets["profitandloss"].copy()

    # Calculate Operating Profit
    pnl["operating_profit_calculated"] = (
        pnl["sales"] - pnl["expenses"]
    )

    # Compare with dataset value
    pnl["operating_profit_match"] = (
        pnl["operating_profit"]
        == pnl["operating_profit_calculated"]
    )

    return pnl


if __name__ == "__main__":

    result = calculate_operating_profit()

    # Save results
    result.to_csv(
        OUTPUT_PATH / "operating_profit.csv",
        index=False
    )

    # Display comparison
    print(
        result[
            [
                "company_id",
                "year",
                "sales",
                "expenses",
                "operating_profit",
                "operating_profit_calculated",
                "operating_profit_match",
            ]
        ].head(10)
    )

    # Summary
    total_rows = len(result)
    matched_rows = result["operating_profit_match"].sum()
    unmatched_rows = total_rows - matched_rows

    print("\n========== Summary ==========")
    print(f"Total Records     : {total_rows}")
    print(f"Matched Records   : {matched_rows}")
    print(f"Unmatched Records : {unmatched_rows}")

    print("\noperating_profit.csv created successfully!")