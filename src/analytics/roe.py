from pathlib import Path

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)
from src.etl.loader import load_core_datasets

datasets = load_core_datasets()

pnl = datasets["profitandloss"]
balance = datasets["balancesheet"]
ratios = datasets["financial_ratios"]

# Merge Profit & Loss with Balance Sheet
merged = pnl.merge(
    balance,
    on=["company_id", "year"],
    how="inner",
    suffixes=("_pnl", "_bs")
)

# Merge with Financial Ratios
merged = merged.merge(
    ratios[
        [
            "company_id",
            "year",
            "return_on_equity_pct"
        ]
    ],
    on=["company_id", "year"],
    how="left"
)

# Calculate Shareholders' Equity
merged["shareholders_equity"] = (
    merged["equity_capital"] +
    merged["reserves"]
)

# Calculate ROE
merged["roe_calculated"] = (
    merged["net_profit"] /
    merged["shareholders_equity"]
) * 100

# Round to 2 decimal places
merged["roe_calculated"] = (
    merged["roe_calculated"].round(2)
)

# Compare calculated ROE with dataset ROE
merged["roe_match"] = (
    merged["return_on_equity_pct"].round(2)
    ==
    merged["roe_calculated"]
)

print("\nMerged Shape:", merged.shape)

print("\nColumns:")
print(merged.columns.tolist())

print("\nPreview:")

print(
    merged[
        [
            "company_id",
            "year",
            "net_profit",
            "shareholders_equity",
            "roe_calculated",
            "return_on_equity_pct",
            "roe_match",
        ]
    ].head(10)
)

# Save results
merged.to_csv(
    OUTPUT_PATH / "return_on_equity.csv",
    index=False
)

total_rows = len(merged)
matched_rows = merged["roe_match"].sum()
unmatched_rows = total_rows - matched_rows

print("\n========== Summary ==========")
print(f"Total Records     : {total_rows}")
print(f"Matched Records   : {matched_rows}")
print(f"Unmatched Records : {unmatched_rows}")

print("\nreturn_on_equity.csv created successfully!")