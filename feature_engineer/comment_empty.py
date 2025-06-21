import pandas as pd


def comment_empty(row: pd.Series) -> bool:
    """
    Check whether the 'comment' field in a DataFrame row is empty (NaN or blank).

    Parameters:
        row (pandas.Series): A row from a DataFrame containing a 'comment' field.

    Returns:
        bool: True if the comment is missing (NaN), False otherwise.
    """
    return pd.isna(row["comment"])
