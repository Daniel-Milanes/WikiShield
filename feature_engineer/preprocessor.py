import pandas as pd

from .account_age import account_age
from .comment_empty import comment_empty
from .is_ip import is_IP
from .word_count import word_count


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
