import pandas as pd


def safe_divide(numerator, denominator):
    """
    Safely divide two values.
    Returns None if denominator is 0 or missing.
    """

    if pd.isna(denominator) or denominator == 0:
        return None

    return numerator / denominator


def round_percentage(value):
    """
    Round percentage values to 2 decimal places.
    """

    if pd.isna(value):
        return None

    return round(value, 2)