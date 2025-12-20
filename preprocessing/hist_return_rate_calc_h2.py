# Copyright (c) 2025, Iulia Kriuchkova

"""Module for calculating users' historical return rates.

Provides functions to add columns with historical return rates
and categorize them into buckets.
"""

import numpy as np
import pandas as pd


def add_hist_return_rate(df: pd.DataFrame) -> pd.DataFrame:
    # Специальные маски по покупкам/возвратам
    mask_no_buys = (df["total_buy"] == 0) & (df["total_return"] == 0)
    mask_only_returns = (df["total_buy"] == 0) & (df["total_return"] > 0)
    mask_zero_returns = (df["total_buy"] > 0) & (df["total_return"] == 0)
    mask_pos_both = (df["total_buy"] > 0) & (df["total_return"] > 0)

    # Исторический коэффициент возвратов
    df["hist_return_rate"] = np.nan
    df.loc[mask_pos_both, "hist_return_rate"] = (
        df.loc[mask_pos_both, "total_return"] / df.loc[mask_pos_both, "total_buy"]
    )


    return df
