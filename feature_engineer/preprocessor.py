import pandas as pd
from feature_engineer import (
    VandalismScorer,
    is_IP,
    account_age,
    comment_empty,
    word_count,
)
from sklearn.model_selection import StratifiedKFold
import numpy as np


def preprocessor(df: pd.DataFrame) -> None:
    """
    Preprocess the DataFrame by applying various feature engineering techniques.
    Modifies the DataFrame in place.

    Args:
        df (pd.DataFrame): The input DataFrame to be processed.
    """

    df.drop(
        df[
            (df["added_lines"] == "BAD REQUEST")
            | (df["deleted_lines"] == "BAD REQUEST")
        ].index,
        inplace=True,
    )

    df["comment_empty"] = df.apply(comment_empty, axis=1)
    df["account_age"] = df.apply(account_age, axis=1)
    df["is_IP"] = df.apply(is_IP, axis=1)
    df["word_count_added"], df["word_count_deleted"] = zip(
        *df.apply(word_count, axis=1)
    )

