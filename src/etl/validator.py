import pandas as pd
from src.etl.loader import load_core_datasets

# Expected columns for each dataset
EXPECTED_COLUMNS = {
    "companies": [
        "id",
        "company_name",
    ],

    "profitandloss": [
        "company_id",
        "year",
    ],

    "balancesheet": [
        "company_id",
        "year",
    ],

    "cashflow": [
        "company_id",
        "year",
    ],

    "analysis": [
        "company_id",
    ],

    "documents": [
        "company_id",
    ],

    "prosandcons": [
        "company_id",
    ],

    "sectors": [
        "company_id",
    ],

    "stock_prices": [
        "company_id",
    ],

    "market_cap": [
        "company_id",
    ],

    "financial_ratios": [
        "company_id",
    ],

    "peer_groups": [
        "company_id",
    ],
}


def validate_required_columns(datasets):
    """
    Check whether all required columns exist.
    """
    failures = []

    for table_name, required_columns in EXPECTED_COLUMNS.items():

        if table_name not in datasets:
            failures.append({
                "table": table_name,
                "column": "-",
                "issue": "Dataset not loaded",
                "severity": "CRITICAL"
            })
            continue

        df = datasets[table_name]

        for column in required_columns:

            if column not in df.columns:
                failures.append({
                    "table": table_name,
                    "column": column,
                    "issue": "Missing required column",
                    "severity": "CRITICAL"
                })

    return failures


def validate_duplicates(datasets):
    """
    Check duplicate (company_id, year) records.
    """

    failures = []

    year_tables = [
        "profitandloss",
        "balancesheet",
        "cashflow",
        "stock_prices",
        "financial_ratios",
    ]

    for table in year_tables:

        if table not in datasets:
            continue

        df = datasets[table]

        if "company_id" not in df.columns or "year" not in df.columns:
            continue

        duplicates = df[df.duplicated(
            subset=["company_id", "year"],
            keep=False
        )]

        for _, row in duplicates.iterrows():

            failures.append({
                "table": table,
                "company_id": row["company_id"],
                "year": row["year"],
                "issue": "Duplicate record",
                "severity": "WARNING"
            })

    return failures


def validate_missing_company_id(datasets):
    """
    Check missing company IDs.
    """

    failures = []

    for table_name, df in datasets.items():

        if "company_id" in df.columns:

            missing = df[df["company_id"].isna()]

            for _, row in missing.iterrows():

                failures.append({
                    "table": table_name,
                    "company_id": None,
                    "year": row["year"] if "year" in row else None,
                    "issue": "Missing company_id",
                    "severity": "CRITICAL"
                })

    return failures


def validate_missing_year(datasets):
    """
    Check missing years.
    """

    failures = []

    for table_name, df in datasets.items():

        if "year" in df.columns:

            missing = df[df["year"].isna()]

            for _, row in missing.iterrows():

                failures.append({
                    "table": table_name,
                    "company_id": row["company_id"] if "company_id" in row else None,
                    "year": None,
                    "issue": "Missing year",
                    "severity": "WARNING"
                })

    return failures


if __name__ == "__main__":

    datasets = load_core_datasets()

    failures = []

    failures.extend(validate_required_columns(datasets))
    failures.extend(validate_duplicates(datasets))
    failures.extend(validate_missing_company_id(datasets))
    failures.extend(validate_missing_year(datasets))

    if failures:

        df = pd.DataFrame(failures)

        print(df)

        df.to_csv(
            "validation_failures.csv",
            index=False
        )

        print("\nValidation failures saved.")

    else:

        print("\nNo validation failures found.")