import pandas as pd


def normalize_ticker(series: pd.Series) -> pd.Series:
    """
    Standardize company ticker symbols.

    Example:
        " tcs " -> "TCS"
        "infy"  -> "INFY"
    """
    return (
        series.astype(str)
        .str.strip()
        .str.upper()
    )


def normalize_year(series: pd.Series) -> pd.Series:
    """
    Convert year labels like:
        Mar-24 -> 2024-03
        Dec-23 -> 2023-12
    """

    month_map = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12",
    }

    def convert(value):
        if pd.isna(value):
            return None

        value = str(value).strip()

        if "-" not in value:
            return value

        month, year = value.split("-")

        month = month.title()

        if month not in month_map:
            return value

        year = int(year)

        if year <= 30:
            year += 2000
        else:
            year += 1900

        return f"{year}-{month_map[month]}"

    return series.apply(convert)