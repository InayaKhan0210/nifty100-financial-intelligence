from src.etl.loader import load_core_datasets

datasets = load_core_datasets()

print("\nBalance Sheet Columns\n")
print(datasets["balancesheet"].columns.tolist())

print("\nFinancial Ratios Columns\n")
print(datasets["financial_ratios"].columns.tolist())