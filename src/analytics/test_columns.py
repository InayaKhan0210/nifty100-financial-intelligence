from src.etl.loader import load_core_datasets

datasets = load_core_datasets()

print(datasets["profitandloss"].columns.tolist())