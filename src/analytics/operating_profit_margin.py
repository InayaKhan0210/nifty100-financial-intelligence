from pathlib import Path

from src.etl.loader import load_core_datasets

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)


def calculate_operating_profit_margin():

    datasets = load_core_datasets()

    pnl = datasets["profitandloss"]
    ratios = datasets["financial_ratios"]

    # Required columns
    pnl = pnl[
        [
            "company_id",
            "year",
            "sales",
            "operating_profit",
        ]
    ].copy()

    ratios = ratios[
        [
            "company_id",
            "year",
            "operating_profit_margin_pct",
        ]
    ].copy()

    # Remove duplicate company/year records
    pnl = pnl.drop_duplicates(
        subset=["company_id", "year"]
    )

    ratios = ratios.drop_duplicates(
        subset=["company_id", "year"]
    )

    # Merge with financial ratios
    merged = pnl.merge(
        ratios,
        on=["company_id", "year"],
        how="left",
    )

    # Calculate OPM
    merged["opm_calculated"] = (
        (merged["operating_profit"] / merged["sales"]) * 100
    ).round(2)

    # Compare with source
    merged["opm_match"] = (
        merged["opm_calculated"].round(2)
        == merged["operating_profit_margin_pct"].round(2)
    )

    # Identify whether source exists
    merged["source_available"] = (
        merged["operating_profit_margin_pct"].notna()
    )

    # Validation status
    merged["validation_status"] = "Source unavailable"

    merged.loc[
        merged["source_available"]
        & merged["opm_match"],
        "validation_status"
    ] = "Match"

    merged.loc[
        merged["source_available"]
        & ~merged["opm_match"],
        "validation_status"
    ] = "Mismatch"

    return merged


if __name__ == "__main__":

    result = calculate_operating_profit_margin()

    print("\nOperating Profit Margin Validation:")

    print(
        result[
            [
                "company_id",
                "year",
                "sales",
                "operating_profit",
                "opm_calculated",
                "operating_profit_margin_pct",
                "validation_status",
            ]
        ].head(20)
    )

    print("\nValidation Summary:")

    print(
        result["validation_status"].value_counts()
    )

    mismatches = result[
        result["validation_status"] == "Mismatch"
    ]

    print("\nActual Mismatches:")
    print("Mismatch Count:", len(mismatches))

    if len(mismatches) > 0:
        print(
            mismatches[
                [
                    "company_id",
                    "year",
                    "opm_calculated",
                    "operating_profit_margin_pct",
                ]
            ].head(20)
        )

    # Save output
    output_file = (
        OUTPUT_PATH / "operating_profit_margin.csv"
    )

    result.to_csv(
        output_file,
        index=False
    )

    print(f"\nSaved: {output_file}")

    # Summary
    print("\nOperating Profit Margin Summary:")

    print(
        result["opm_calculated"].describe()
    )