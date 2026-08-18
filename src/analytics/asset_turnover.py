from pathlib import Path

from src.etl.loader import load_core_datasets

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

datasets = load_core_datasets()

pnl = datasets["profitandloss"]
balance = datasets["balancesheet"]
ratios = datasets["financial_ratios"]

merged = pnl.merge(
    balance[
        [
            "company_id",
            "year",
            "total_assets",
        ]
    ],
    on=["company_id", "year"],
    how="inner",
)

merged = merged.merge(
    ratios[
        [
            "company_id",
            "year",
            "asset_turnover",
        ]
    ],
    on=["company_id", "year"],
    how="left",
)

print("\nPreview:")

print(
    merged[
        [
            "company_id",
            "year",
            "sales",
            "total_assets",
            "asset_turnover",
        ]
    ].head(10)
)

# Calculate Asset Turnover
merged["asset_turnover_calculated"] = (
    merged["sales"] /
    merged["total_assets"]
)

merged["asset_turnover_calculated"] = (
    merged["asset_turnover_calculated"].round(2)
)

# Validate calculated Asset Turnover against source data
merged["asset_turnover_match"] = (
    merged["asset_turnover_calculated"].round(2)
    == merged["asset_turnover"].round(2)
)

print("\nPreview:")

print(
    merged[
        [
            "company_id",
            "year",
            "sales",
            "total_assets",
            "asset_turnover_calculated",
            "asset_turnover",
        ]
    ].head(10)
)


print("\nValidation Preview:")

print(
    merged[
        [
            "company_id",
            "year",
            "asset_turnover_calculated",
            "asset_turnover",
            "asset_turnover_match",
        ]
    ].head(20)
)

merged.to_csv(OUTPUT_PATH / "asset_turnover.csv", index=False)

print("\nAsset Turnover Summary:")
print(merged["asset_turnover_calculated"].describe())