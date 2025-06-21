import re
import pandas as pd


def word_count(row: pd.Series) -> tuple[int, int]:
    """
    Count the number of words in the 'added_line' and
    'deleted_line' fields of a DataFrame row.

    This function:
    - Removes punctuation
    - Converts text to lowercase
    - Splits text into words
    - Counts all words

    Parameters:
        row (pandas.Series): A row from a DataFrame containing
        'added_line' and 'deleted_line' keys.

    Returns:
        tuple: A pair (added_count, deleted_count) representing the number of words
               in the added and deleted lines, respectively.
    """
    added = len(re.sub(r"[^\w\s]", " ", str(row["added_lines"])).lower().split())
    deleted = len(re.sub(r"[^\w\s]", " ", str(row["deleted_lines"])).lower().split())
    return added, deleted
