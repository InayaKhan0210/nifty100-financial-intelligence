from src.etl.normalize import normalize_ticker, normalize_year
import pandas as pd

tickers = pd.Series([" tcs ", "Infy", " RELIANCE "])
years = pd.Series(["Mar-24", "Dec-23", "Mar-15"])

print(normalize_ticker(tickers))
print()
print(normalize_year(years))