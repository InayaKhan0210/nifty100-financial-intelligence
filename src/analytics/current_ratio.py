from pathlib import Path

from src.etl.loader import load_core_datasets

OUTPUT_PATH = Path("data/processed")
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

# Load datasets
datasets = load_core_datasets()

balance = datasets["balancesheet"]

# Show available columns
print("\nBalance Sheet Columns:")
print(balance.columns.tolist())

print("\nBalance Sheet Preview:")
print(balance.head(10).to_string())

# Check for current asset/current liability columns
current_asset_candidates = [
    "current_assets",
    "current_asset",
    "other_current_assets",
]

current_liability_candidates = [
    "current_liabilities",
    "current_liability",
]

available_current_assets = [
    col for col in current_asset_candidates if col in balance.columns
]

available_current_liabilities = [
    col for col in current_liability_candidates if col in balance.columns
]

print("\nCurrent Asset Columns Found:")
print(available_current_assets)

print("\nCurrent Liability Columns Found:")
print(available_current_liabilities)

# Calculate only if the required columns exist
if available_current_assets and available_current_liabilities:

    current_assets_col = available_current_assets[0]
    current_liabilities_col = available_current_liabilities[0]

    current_ratio = balance[
        [
            "company_id",
            "year",
            current_assets_col,
            current_liabilities_col,
        ]
    ].copy()

    current_ratio["current_ratio_calculated"] = (
        current_ratio[current_assets_col]
        / current_ratio[current_liabilities_col]
    ).round(2)

    print("\nCurrent Ratio Preview:")
    print(current_ratio.head(20).to_string(index=False))

    # Save result
    output_file = OUTPUT_PATH / "current_ratio.csv"
    current_ratio.to_csv(output_file, index=False)

    print(f"\nSaved: {output_file}")

    # Summary
    print("\nCurrent Ratio Summary:")
    print(current_ratio["current_ratio_calculated"].describe())

else:
    print(
        "\nCurrent Ratio cannot be calculated yet because "
        "current assets/current liabilities columns were not found."
    )