
from pathlib import Path

from src.etl.loader import load_core_datasets

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

datasets = load_core_datasets()

balance = datasets["balancesheet"]
ratios = datasets["financial_ratios"]

merged = balance.merge(
    ratios[
        [
            "company_id",
            "year",
            "debt_to_equity"
        ]
    ],
    on=["company_id", "year"],
    how="left"
)

print(merged.shape)



# Calculate Shareholders' Equity
merged["shareholders_equity"] = (
    merged["equity_capital"] +
    merged["reserves"]
)

# Calculate Debt-to-Equity Ratio
merged["debt_to_equity_calculated"] = (
    merged["borrowings"] /
    merged["shareholders_equity"]
)

# Round to 2 decimal places
merged["debt_to_equity_calculated"] = (
    merged["debt_to_equity_calculated"].round(2)
)

print("\nPreview:")

print(
    merged[
        [
            "company_id",
            "year",
            "borrowings",
            "equity_capital",
            "reserves",
            "shareholders_equity",
            "debt_to_equity_calculated",
        ]
    ].head(10)
)



print("\nBorrowings Statistics:")
print(merged["borrowings"].describe())

print("\nNon-zero Borrowings:")
print(
    merged[merged["borrowings"] != 0][
        [
            "company_id",
            "year",
            "borrowings",
            "equity_capital",
            "reserves",
            "debt_to_equity_calculated"
        ]
    ].head(20)
)

print("\nFinancial Ratios Debt-to-Equity:")
print(
    merged[
        [
            "company_id",
            "year",
            "debt_to_equity"
        ]
    ].head(20)
)

# Validate calculated ratio against the source dataset
merged["debt_to_equity_match"] = (
    merged["debt_to_equity_calculated"].round(2)
    == merged["debt_to_equity"].round(2)
)

print("\nValidation Preview:")

print(
    merged[
        [
            "company_id",
            "year",
            "debt_to_equity_calculated",
            "debt_to_equity",
            "debt_to_equity_match",
        ]
    ].head(20)
)

# Save results
merged.to_csv(
    OUTPUT_PATH / "debt_to_equity.csv",
    index=False
)

total_rows = len(merged)
matched_rows = merged["debt_to_equity_match"].sum()
unmatched_rows = total_rows - matched_rows

print("\n========== Summary ==========")
print(f"Total Records     : {total_rows}")
print(f"Matched Records   : {matched_rows}")
print(f"Unmatched Records : {unmatched_rows}")

print("\ndebt_to_equity.csv created successfully!")