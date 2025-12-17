# Copyright (c) 2025, Iulia Kriuchkova

"""Gradio interface for visualizing historical return rates and purchase delays.

This script loads and preprocesses marketplace data, calculates delay days
and historical return rates, and provides interactive visualizations
with Gradio.
"""
import gradio as gr  # noqa: I001
from matplotlib.figure import Figure

from preprocessing.data_cleaning import load_and_clean_data
from preprocessing.delay_calc import add_delay_days
from preprocessing.hist_return_rate_calc import add_hist_return_rate
from preprocessing.create_pivot_hist_delay import create_fig, cohort_order


# 1. Загрузка и обработка данных
df = load_and_clean_data()
df = add_delay_days(df)
df = add_hist_return_rate(df)

# Получаем дефолтные значения для фильтров
delay_cohorts = cohort_order
return_buckets = df["hist_return_bucket"].cat.categories.tolist()

# Функция обновления графика


def update_chart(
    selected_cohorts: list[str], selected_buckets: list[str]
) -> Figure:
    """Update the stacked bar chart based on selected cohorts and return buckets.

    Args:
        selected_cohorts: List of delay cohorts to display.
        selected_buckets: List of historical return buckets to display.

    Returns:
        matplotlib.figure.Figure: Figure object with the updated chart.
    """
    return create_fig(
        df,
        selected_cohorts=selected_cohorts,
        selected_buckets=selected_buckets,
    )


# 2. Создаём Gradio интерфейс
with gr.Blocks() as demo:
    gr.Markdown("## Гистограмма исторического коэффициента возвратов")
    gr.BarPlot(df, x="hist_return_bucket", y="count", y_aggregate="count")
    gr.Markdown("## Гистограмма задержек между регистрацией и покупкой")
    gr.BarPlot(df, x="delay_days_cohort", y="count", y_aggregate="count")
    gr.Markdown("## Фильтры по когортам и историческим возвратам")
    with gr.Row():
        cohort_input = gr.Dropdown(
            choices=delay_cohorts,
            value=delay_cohorts,
            label="Выберите когорты",
            multiselect=True,
        )
        bucket_input = gr.CheckboxGroup(
            choices=return_buckets,
            value=return_buckets,
            label="Выберите бакеты возвратов",
        )

    output_plot = gr.Plot(value=update_chart(delay_cohorts, return_buckets))

    # Привязываем интерактивность
    cohort_input.change(
        fn=update_chart,
        inputs=[cohort_input, bucket_input],
        outputs=output_plot,
    )
    bucket_input.change(
        fn=update_chart,
        inputs=[cohort_input, bucket_input],
        outputs=output_plot,
    )


# 3. Запускаем Gradio
demo.launch()
