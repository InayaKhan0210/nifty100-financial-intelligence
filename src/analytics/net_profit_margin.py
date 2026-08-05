from pathlib import Path
from src.etl.loader import load_core_datasets

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


def calculate_net_profit_margin():
    """
    Calculate Net Profit Margin (NPM)
    and compare it with the dataset values.
    """

    datasets = load_core_datasets()

    pnl = datasets["profitandloss"].copy()

    # Calculate Net Profit Margin
    pnl["net_profit_margin_calculated"] = (
        pnl["net_profit"] / pnl["sales"]
    ) * 100

    # Round for comparison
    pnl["net_profit_margin_calculated"] = (
        pnl["net_profit_margin_calculated"].round(2)
    )

    # If dataset already contains Net Profit Margin, compare it
    if "net_profit_margin" in pnl.columns:
        pnl["net_profit_margin_match"] = (
            pnl["net_profit_margin"].round(2)
            == pnl["net_profit_margin_calculated"]
        )
    else:
        pnl["net_profit_margin_match"] = "Not Available"

    return pnl


if __name__ == "__main__":

    result = calculate_net_profit_margin()

    result.to_csv(
        OUTPUT_PATH / "net_profit_margin.csv",
        index=False
    )

    print(
        result[
            [
                "company_id",
                "year",
                "sales",
                "net_profit",
                "net_profit_margin_calculated",
                "net_profit_margin_match",
            ]
        ].head(10)
    )

    print("\n========== Summary ==========")
    print(f"Total Records : {len(result)}")

    print("\nnet_profit_margin.csv created successfully!")