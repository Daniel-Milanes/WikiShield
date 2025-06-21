#!/usr/bin/env python

"""Provides feature engineering functions for features other than edit text:
currently, whether user is an IP."""

import pandas as pd
import re

dumbIPRegex = re.compile(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")
# Compiles a regex object matching any string of the form "xxx.xxx.xxx.xxx",
# where "xxx" is a set of between 1 and 3 decimal digits.
# No need to do any more validation, since the dataset only contains valid IPs
# (registered users on Wikipedia are not allowed to have IP-like usernames)


def _is_IP(data: pd.DataFrame) -> pd.DataFrame:
    """Helper function for FunctionTransformer. Checks if user is an IP."""
    return pd.concat(
        [
            data,
            data[["user"]]
            .map(lambda str: bool(dumbIPRegex.fullmatch(str)))
            .rename(columns={"user": "is_IP"}),
        ],
        axis=1,
    )
