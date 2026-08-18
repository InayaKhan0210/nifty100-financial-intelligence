from pathlib import Path

from src.etl.loader import load_core_datasets

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

datasets = load_core_datasets()

pnl = datasets["profitandloss"]
balance = datasets["balancesheet"]

# Calculate Capital Employed
merged = pnl.merge(
    balance[
        [
            "company_id",
            "year",
            "equity_capital",
            "reserves",
            "borrowings",
        ]
    ],
    on=["company_id", "year"],
    how="inner",
)

merged["capital_employed"] = (
    merged["equity_capital"]
    + merged["reserves"]
    + merged["borrowings"]
)

# Calculate ROCE
merged["roce_calculated"] = (
    merged["operating_profit"]
    / merged["capital_employed"]
) * 100

merged["roce_calculated"] = (
    merged["roce_calculated"].round(2)
)

print("\nMissing ROCE values:")
print(merged["roce_calculated"].isna().sum())

print("\nInfinite ROCE values:")
print(merged["roce_calculated"].isin([float("inf"), float("-inf")]).sum())


print("\nPreview:")

print(
    merged[
        [
            "company_id",
            "year",
            "operating_profit",
            "capital_employed",
            "roce_calculated",
        ]
    ].head(10)
)

print("\nROCE Statistics:")

print(
    merged["roce_calculated"].describe()
)


# Save results
merged.to_csv(
    OUTPUT_PATH / "roce.csv",
    index=False
)

print("\nROCE Statistics:")
print(merged["roce_calculated"].describe())

print("\nroce.csv created successfully!")