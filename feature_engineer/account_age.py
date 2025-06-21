from datetime import (
    datetime,
    timezone,
)  # Used for converting timestamps to datetime objects in UTC
import pandas as pd


def account_age(row: pd.Series) -> int:
    """
    Calculate the age of a user's account in days
      at the time of the current edit.

    Parameters:
        row (pandas.Series): A row from a DataFrame containing:
            - 'user_reg_time': User registration time as a
            Unix timestamp (int or string).
            - 'current_timestamp': Timestamp of the current
            edit as a Unix timestamp.

    Returns:
        int: The number of days between the user's
        registration and the current edit. If 'user_reg_time'
        is not a standard Unix timestamp (likely anonymous user),
        returns a default value of 1 day.

    Notes:
        - Handles cases where 'user_reg_time' may be a string
        longer than 10 digits, which might indicate an anonymous
        or malformed timestamp.
        - Assumes all timestamps are in UTC.
    """
    user_reg_time = row[
        "user_reg_time"
    ]  # Registration timestamp of the user (Unix format, possibly string)
    current_time = row["current_timestamp"]  # Timestamp of the current edit

    if len(str(user_reg_time)) > 10:
        return 1  # Default age for anonymous or malformed registration times
    else:
        reg_time = datetime.fromtimestamp(int(user_reg_time), tz=timezone.utc)
        edit_time = datetime.fromtimestamp(int(current_time), tz=timezone.utc)
        return (edit_time - reg_time).days
