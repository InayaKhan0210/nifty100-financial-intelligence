from pathlib import Path

from src.etl.loader import load_core_datasets

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

datasets = load_core_datasets()

pnl = datasets["profitandloss"]
ratios = datasets["financial_ratios"]

# Select required columns
pnl = pnl[
    [
        "company_id",
        "year",
        "operating_profit",
        "interest",
    ]
].copy()

ratios = ratios[
    [
        "company_id",
        "year",
        "interest_coverage",
    ]
].copy()

# Remove duplicate company/year records
pnl = pnl.drop_duplicates(
    subset=["company_id", "year"]
)

ratios = ratios.drop_duplicates(
    subset=["company_id", "year"]
)

# Merge datasets
merged = pnl.merge(
    ratios,
    on=["company_id", "year"],
    how="left",
)

# Calculate Interest Coverage Ratio
merged["interest_coverage_calculated"] = (
    merged["operating_profit"]
    / merged["interest"].replace(0, float("nan"))
).round(2)

# Validate against source
merged["interest_coverage_match"] = (
    merged["interest_coverage_calculated"].round(2)
    == merged["interest_coverage"].round(2)
)

# Check whether source is available
merged["source_available"] = (
    merged["interest_coverage"].notna()
)

# Validation status
merged["validation_status"] = "Source unavailable"

merged.loc[
    merged["source_available"]
    & merged["interest_coverage_match"],
    "validation_status"
] = "Match"

merged.loc[
    merged["source_available"]
    & ~merged["interest_coverage_match"],
    "validation_status"
] = "Mismatch"

# Preview
print("\nInterest Coverage Validation:")

print(
    merged[
        [
            "company_id",
            "year",
            "operating_profit",
            "interest",
            "interest_coverage_calculated",
            "interest_coverage",
            "validation_status",
        ]
    ].head(20)
)

# Validation summary
print("\nValidation Summary:")

print(
    merged["validation_status"].value_counts()
)

# Actual mismatches
mismatches = merged[
    merged["validation_status"] == "Mismatch"
]

print("\nActual Mismatches:")
print("Mismatch Count:", len(mismatches))

if len(mismatches) > 0:
    print(
        mismatches[
            [
                "company_id",
                "year",
                "interest_coverage_calculated",
                "interest_coverage",
            ]
        ].head(20)
    )

# Save results
output_file = (
    OUTPUT_PATH / "interest_coverage.csv"
)

merged.to_csv(
    output_file,
    index=False
)

print(f"\nSaved: {output_file}")

# Summary statistics
print("\nInterest Coverage Summary:")

print(
    merged["interest_coverage_calculated"].describe()
)