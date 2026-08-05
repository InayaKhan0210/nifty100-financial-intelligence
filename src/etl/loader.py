from pathlib import Path
import pandas as pd

from src.etl.normalize import normalize_ticker, normalize_year

# Path to raw data
RAW_DATA_PATH = Path("data/raw")

# Core datasets (header=1)
CORE_FILES = [
    "companies.xlsx",
    "profitandloss.xlsx",
    "balancesheet.xlsx",
    "cashflow.xlsx",
    "analysis.xlsx",
    "documents.xlsx",
    "prosandcons.xlsx",
]

# Supplementary datasets (header=0)
SUPPLEMENTARY_FILES = [
    "sectors.xlsx",
    "stock_prices.xlsx",
    "market_cap.xlsx",
    "financial_ratios.xlsx",
    "peer_groups.xlsx",
]


def load_core_datasets():
    """
    Load all Excel datasets.
    Returns a dictionary of DataFrames.
    """

    datasets = {}

    # Load core datasets (header=1)
    for file_name in CORE_FILES:

        file_path = RAW_DATA_PATH / file_name

        print(f"Loading {file_name}...")

        df = pd.read_excel(file_path, header=1)

        if "company_id" in df.columns:
            df["company_id"] = normalize_ticker(df["company_id"])

        if "id" in df.columns and file_name == "companies.xlsx":
            df["id"] = normalize_ticker(df["id"])

        if "year" in df.columns:
            df["year"] = normalize_year(df["year"])

        datasets[file_name.replace(".xlsx", "")] = df

        print(f"Loaded {len(df)} rows and {len(df.columns)} columns")

    # Load supplementary datasets (header=0)
    for file_name in SUPPLEMENTARY_FILES:

        file_path = RAW_DATA_PATH / file_name

        print(f"Loading {file_name}...")

        df = pd.read_excel(file_path, header=0)

        if "company_id" in df.columns:
            df["company_id"] = normalize_ticker(df["company_id"])

        datasets[file_name.replace(".xlsx", "")] = df

        print(f"Loaded {len(df)} rows and {len(df.columns)} columns")

    return datasets


if __name__ == "__main__":
    data = load_core_datasets()

    print("\nDatasets Loaded Successfully\n")

    for name, df in data.items():
        print(f"{name:<20} {df.shape}")