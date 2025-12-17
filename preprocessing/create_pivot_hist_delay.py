# Copyright (c) 2025, Iulia Kriuchkova

"""Create pivot tables and visualizations of historical return rates.

This module provides functions to aggregate user counts by delay cohorts
and historical return buckets, and to visualize the distribution as
stacked bar charts.
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.figure import Figure

bucket_order = ["0–10%", "10–50%", "50–100%", "100–500%", ">500%"]

cohort_order = [
    "Невозможно исследовать",
    "Очень быстрая покупка (Q1)",
    "Быстрая покупка (Q2)",
    "Медленная покупка (Q3)",
    "Очень медленная покупка (Q4)",
]


def create_pivot_hist_delay(
    df: pd.DataFrame,
    selected_cohorts: list[str] | None = None,
    selected_buckets: list[str] | None = None,
) -> pd.DataFrame:
    """Create a pivot table of historical return counts by delay cohorts.

    Filters the DataFrame by selected cohorts and return buckets, aggregates
    user counts, and converts the results to percentages per cohort.

    Args:
        df: Input DataFrame with 'user_id', 'delay_days_cohort', and 'hist_return_bucket' columns.
        selected_cohorts: Optional list of cohorts to include. If None, uses all unique cohorts.
        selected_buckets: Optional list of return buckets to include. If None, uses all categories.

    Returns:
        pd.DataFrame: Pivot table with cohorts as rows, buckets as columns, and percentages as values.
    """
    # Дефолтные значения
    if selected_cohorts is None:
        selected_cohorts = df["delay_days_cohort"].unique().tolist()
    if selected_buckets is None:
        selected_buckets = df["hist_return_bucket"].cat.categories.tolist()

    # Фильтруем по выбранным значениям
    cohorts: list[str] = (
        selected_cohorts
        if selected_cohorts is not None
        else df["delay_days_cohort"].unique().tolist()
    )
    filtered_df = df[df["delay_days_cohort"].isin(cohorts)]

    filtered_df = filtered_df[
        filtered_df["hist_return_bucket"].isin(selected_buckets)
    ]

    pivot = filtered_df.pivot_table(
        index="delay_days_cohort",
        columns="hist_return_bucket",
        values="user_id",
        aggfunc="count",
        fill_value=0,
        observed=True,
    )

    # Сохраняем порядок когорты и бакетов
    return pivot.reindex(
        index=selected_cohorts,
        columns=selected_buckets,
        fill_value=0,
    )


def create_fig(
    df: pd.DataFrame,
    selected_cohorts: list[str] | None = None,
    selected_buckets: list[str] | None = None,
) -> Figure:
    """Create a stacked bar chart showing historical return percentages by cohort.

    Args:
        df: Input DataFrame with 'user_id', 'delay_days_cohort', and 'hist_return_bucket' columns.
        selected_cohorts: Optional list of cohorts to display. If None, uses all unique cohorts.
        selected_buckets: Optional list of return buckets to display. If None, uses all categories.

    Returns:
        matplotlib.figure.Figure: Figure object with the stacked bar chart.
    """
    cohort_vs_hist_bucket = create_pivot_hist_delay(
        df,
        selected_cohorts,
        selected_buckets,
    )

    # Переводим в проценты внутри каждой когорты
    cohort_vs_hist_bucket_pct = (
        cohort_vs_hist_bucket.div(cohort_vs_hist_bucket.sum(axis=1), axis=0)
        * 100
    )
    # Построение stacked bar chart
    fig, ax = plt.subplots(figsize=(12, 10))

    bottom = np.zeros(len(cohort_vs_hist_bucket_pct))
    colors = plt.cm.get_cmap("inferno")(np.linspace(0, 1, len(bucket_order)))

    for idx, bucket in enumerate(cohort_vs_hist_bucket_pct.columns):
        values = cohort_vs_hist_bucket_pct[bucket].to_numpy()
        ax.bar(
            cohort_vs_hist_bucket_pct.index,
            values,
            bottom=bottom,
            label=bucket,
            color=colors[idx],
        )
        # Добавляем подписи внутри сегмента
        for i, (val, bot) in enumerate(zip(values, bottom, strict=True)):
            if val > 0:
                abs_count = cohort_vs_hist_bucket[bucket].iloc[i]  # абсолютное число пользователей
                ax.text(
                    i,  # позиция по X
                    bot + val / 2,  # по Y – середина сегмента
                    f"{val:.1f}%\n({abs_count})",  # текст: процент + абсолютное число
                    ha="center",
                    va="center",
                    fontsize=9,
                    color="white",
                )
        bottom += values

    ax.set_ylabel("Доля пользователей, %")
    ax.set_xlabel("Когорта по количеству дней до первой покупки")
    ax.set_title(
        "Распределение исторического коэффициента возвратов по когортам",
    )
    ax.legend(
        title="Бакет исторических возвратов",
        bbox_to_anchor=(1.05, 1),
        loc="upper left",
    )
    plt.xticks(rotation=20)
    plt.tight_layout()

    return fig
