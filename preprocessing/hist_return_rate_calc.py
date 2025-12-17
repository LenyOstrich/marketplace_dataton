# Copyright (c) 2025, Iulia Kriuchkova

"""Module for calculating users' historical return rates.

Provides functions to add columns with historical return rates
and categorize them into buckets.
"""

import numpy as np
import pandas as pd


def add_hist_return_rate(df: pd.DataFrame) -> pd.DataFrame:
    """Add a column 'hist_return_rate' to the DataFrame.

    Calculated as total_return / total_buy. If total_buy == 0, uses total_return / 1.

    Args:
        df (pd.DataFrame): Input DataFrame with 'total_return' and 'total_buy' columns.

    Returns:
        pd.DataFrame: DataFrame with added 'hist_return_rate' and 'hist_return_bucket' columns.
    """
    mask_total_buy_zero = df["total_buy"] == 0

    df["hist_return_rate"] = np.where(
        mask_total_buy_zero,
        df["total_return"],
        df["total_return"] / df["total_buy"]
    )

    bins = [0, 0.1, 0.5, 1, 5, np.inf]
    labels = ["0–10%", "10–50%", "50–100%", "100–500%", ">500%"]
    df["hist_return_bucket"] = pd.cut(
        df["hist_return_rate"],
        bins=bins,
        labels=labels,
        include_lowest=True,
    )

    return df
