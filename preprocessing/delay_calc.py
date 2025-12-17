# Copyright (c) 2025, Iulia Kriuchkova

"""Module for calculating delay between registration/login and first purchase.

Categorizes users into cohorts based on delay days.
"""

from typing import Literal

import numpy as np
import pandas as pd


def add_delay_days(df: pd.DataFrame) -> pd.DataFrame:
    """Add 'delay_days' and 'delay_days_cohort' columns to the DataFrame.

    Fills missing registration and first purchase dates, calculates
    the number of days between registration/login and first purchase,
    and assigns users to cohorts based on quantiles.

    Args:
        df (pd.DataFrame): DataFrame with 'reg_dt', 'first_login', 'first_buy' columns.

    Returns:
        pd.DataFrame: DataFrame with added 'delay_days' and 'delay_days_cohort' columns.
    """
    # заполняем пропуски
    df["reg_dt"] = df["reg_dt"].fillna(df["first_login"])
    min_first_buy_date = df["first_buy"].min() - pd.Timedelta(days=1)
    df["first_buy"] = df["first_buy"].fillna(min_first_buy_date)

    def calculate_days_delay(row: pd.Series) -> int | float:
        if row["reg_dt"] < row["first_buy"]:
            return (row["first_buy"] - row["reg_dt"]).days
        if row["first_login"] < row["first_buy"]:
            return (row["first_buy"] - row["first_login"]).days
        return np.nan

    df["delay_days"] = df.apply(calculate_days_delay, axis=1)

    # разбиваем по когортам

    q1 = df["delay_days"].quantile(0.25)
    q2 = df["delay_days"].quantile(0.50)
    q3 = df["delay_days"].quantile(0.75)

    def delay_days_cohort(
        dt: float,
    ) -> Literal[
        "Невозможно исследовать",
        "Очень быстрая покупка (Q1)",
        "Быстрая покупка (Q2)",
        "Медленная покупка (Q3)",
        "Очень медленная покупка (Q4)",
    ]:
        if pd.isna(dt):
            return "Невозможно исследовать"
        if dt <= q1:
            return "Очень быстрая покупка (Q1)"
        if dt <= q2:
            return "Быстрая покупка (Q2)"
        if dt <= q3:
            return "Медленная покупка (Q3)"
        return "Очень медленная покупка (Q4)"

    df["delay_days_cohort"] = df["delay_days"].map(delay_days_cohort)

    return df
