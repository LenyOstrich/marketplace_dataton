# Copyright (c) 2025, Iulia Kriuchkova
"""Module for loading and cleaning marketplace data.

Loads data from CSV, converts date columns to datetime,
and removes duplicate users.
"""
from pathlib import Path

import pandas as pd


def load_and_clean_data() -> pd.DataFrame:
    """Load marketplace data, convert date columns, and remove duplicate users.

    Reads the CSV file, converts 'first_login', 'reg_dt', and 'first_buy' columns
    to datetime, keeps the latest record per user, and resets the index.

    Returns:
        pd.DataFrame: Cleaned DataFrame with unique users and proper date columns.
    """
    project_root = Path(__file__).resolve().parent.parent

    data_path = project_root / "data" / "marketplace.csv"
    df = pd.read_csv(data_path)

    # Приведение дат
    date_cols = ["first_login", "reg_dt", "first_buy"]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # Очистка
    return (
        df.sort_values(["user_id", "first_login"])
          .drop_duplicates(subset="user_id", keep="last")
          .reset_index(drop=True)
    )
