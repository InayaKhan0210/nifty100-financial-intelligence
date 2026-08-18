from pathlib import Path

from src.etl.loader import load_core_datasets

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

datasets = load_core_datasets()

ratios = datasets["financial_ratios"].copy()

# Keep required columns
fcf = ratios[
    [
        "company_id",
        "year",
        "cash_from_operations_cr",
        "capex_cr",
        "free_cash_flow_cr",
    ]
].copy()

# Remove duplicate company/year records
fcf = fcf.drop_duplicates(
    subset=["company_id", "year"]
)

# Calculate Free Cash Flow
fcf["free_cash_flow_calculated"] = (
    fcf["cash_from_operations_cr"]
    - fcf["capex_cr"]
).round(2)

# Validate against source
fcf["fcf_match"] = (
    fcf["free_cash_flow_calculated"].round(2)
    == fcf["free_cash_flow_cr"].round(2)
)

# Source availability
fcf["source_available"] = (
    fcf["free_cash_flow_cr"].notna()
)

# Validation status
fcf["validation_status"] = "Source unavailable"

fcf.loc[
    fcf["source_available"]
    & fcf["fcf_match"],
    "validation_status"
] = "Match"

fcf.loc[
    fcf["source_available"]
    & ~fcf["fcf_match"],
    "validation_status"
] = "Mismatch"

# Preview
print("\nFree Cash Flow Validation:")

print(
    fcf[
        [
            "company_id",
            "year",
            "cash_from_operations_cr",
            "capex_cr",
            "free_cash_flow_calculated",
            "free_cash_flow_cr",
            "validation_status",
        ]
    ].head(20)
)

# Validation summary
print("\nValidation Summary:")

print(
    fcf["validation_status"].value_counts()
)

# Actual mismatches
mismatches = fcf[
    fcf["validation_status"] == "Mismatch"
]

print("\nActual Mismatches:")
print("Mismatch Count:", len(mismatches))

if len(mismatches) > 0:
    print(
        mismatches[
            [
                "company_id",
                "year",
                "free_cash_flow_calculated",
                "free_cash_flow_cr",
            ]
        ].head(20)
    )

# Save
output_file = (
    OUTPUT_PATH / "free_cash_flow.csv"
)

fcf.to_csv(
    output_file,
    index=False
)

print(f"\nSaved: {output_file}")

# Summary
print("\nFree Cash Flow Summary:")

print(
    fcf["free_cash_flow_calculated"].describe()
)