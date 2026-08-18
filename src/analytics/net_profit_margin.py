from pathlib import Path

from src.etl.loader import load_core_datasets

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

datasets = load_core_datasets()

pnl = datasets["profitandloss"]
ratios = datasets["financial_ratios"]

# Keep only the required columns
pnl = pnl[
    [
        "company_id",
        "year",
        "sales",
        "net_profit",
    ]
].copy()

ratios = ratios[
    [
        "company_id",
        "year",
        "net_profit_margin_pct",
    ]
].copy()

# Remove duplicate company/year records before merging
pnl = pnl.drop_duplicates(subset=["company_id", "year"])
ratios = ratios.drop_duplicates(subset=["company_id", "year"])

# Merge datasets
merged = pnl.merge(
    ratios,
    on=["company_id", "year"],
    how="left",
)

# Calculate Net Profit Margin
merged["net_profit_margin_calculated"] = (
    (merged["net_profit"] / merged["sales"]) * 100
).round(2)

merged["net_profit_margin_match"] = (
    merged["net_profit_margin_calculated"].round(2)
    == merged["net_profit_margin_pct"].round(2)
)

# Source data availability
merged["source_available"] = merged["net_profit_margin_pct"].notna()

# True mismatch only when source data exists
merged["validation_status"] = "Source unavailable"

merged.loc[
    merged["source_available"]
    & merged["net_profit_margin_match"],
    "validation_status"
] = "Match"

merged.loc[
    merged["source_available"]
    & ~merged["net_profit_margin_match"],
    "validation_status"
] = "Mismatch"

print("\nNet Profit Margin Validation:")

print(
    merged[
        [
            "company_id",
            "year",
            "sales",
            "net_profit",
            "net_profit_margin_calculated",
            "net_profit_margin_pct",
            "net_profit_margin_match",
        ]
    ].head(20)
)

print("\nValidation Summary:")
print(
    merged["validation_status"].value_counts()
)

print("\nActual Mismatches:")

mismatches = merged[
    merged["validation_status"] == "Mismatch"
]

print("Mismatch Count:", len(mismatches))

if len(mismatches) > 0:
    print(
        mismatches[
            [
                "company_id",
                "year",
                "net_profit_margin_calculated",
                "net_profit_margin_pct",
            ]
        ].head(20)
    )

# Save output
output_file = OUTPUT_PATH / "net_profit_margin.csv"
merged.to_csv(output_file, index=False)

print(f"\nSaved: {output_file}")

# Summary
print("\nNet Profit Margin Summary:")
print(merged["net_profit_margin_calculated"].describe())