# Copyright (c) 2025, Iulia Kriuchkova

"""Gradio interface for visualizing historical return rates and purchase delays.

This script loads and preprocesses marketplace data, calculates delay days
and historical return rates, and provides interactive visualizations
with Gradio.
"""
import gradio as gr  # noqa: I001
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import numpy as np


from preprocessing.data_cleaning import load_and_clean_data
from preprocessing.delay_calc import add_delay_days
from preprocessing.hist_return_rate_calc_h2 import add_hist_return_rate
from preprocessing.create_pivot_hist_delay import create_fig, cohort_order
from preprocessing.target_unshifted_calc import add_target_params

# 1. Загрузка и обработка данных
df = load_and_clean_data()
df = add_target_params(df)
df = add_hist_return_rate(df)
df_hist_return_exists = df.dropna(subset='hist_return_rate')
df_strange_hist_return = (
    df_hist_return_exists[df_hist_return_exists['hist_return_rate'] >= 0.63])['platform_num']
df_ok_hist_return = (
    df_hist_return_exists[df_hist_return_exists['hist_return_rate'] < 0.63])['platform_num']


# 2. Рендеринг графиков

def h2_build_distrib_histogram():
    """Создаёт гистограмму распределения hist_return_rate."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    bin_edges = np.linspace(0, 30, num=101)
    ax.hist(
        df_hist_return_exists['hist_return_rate'],
        bins=bin_edges,
        color='skyblue',
        edgecolor='black',
        alpha=0.7
    )

    ax.set_xlabel('hist_return_rate')
    ax.set_ylabel('Частота')
    ax.set_xlim(0, 30)
    ax.set_ylim(bottom=0)
    ax.set_title('Гистограмма распределения hist_return_rate')
    ax.grid(True, alpha=0.3)
    
    plt.close()  # Важно: не выводим фигуру сразу, а возвращаем объект
    return fig

def h2_build_boxplot():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.boxplot([df_strange_hist_return, df_ok_hist_return], labels=[
            'К. истор. возвратов >=0.63', 'К. истор. возвратов <0.63'])
    ax.set_title('Диаграмма "ящик с усами" для двух групп')
    ax.set_ylim(0, 30)
    ax.set_ylabel('platform_num')
    plt.close()
    return fig

def h2_build_corr():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df_hist_return_exists['platform_num'],
            df_hist_return_exists['hist_return_rate'], alpha=0.6)

    # Оформляем график
    ax.set_xlabel('platform_num')
    ax.set_ylabel('hist_return_rate')
    ax.set_xlim(0, 300)
    ax.set_ylim(0, 400)
    ax.set_title('Взаимосвязь коэффициента исторических возвратов с количеством устройств')
    ax.grid(True, alpha=0.3)
    plt.close()
    return fig


def h4_build_boxplot():
    # разбиваем на группы
    fig, ax = plt.subplots(figsize=(10, 6))
    bad_target = df[df['is_bad_target'] == True]
    good_target = df[df['is_bad_target'] == False]
    ax.boxplot([bad_target['platform_num'], good_target['platform_num']],
                labels=['target_unshifted>=0.3', 'target_unshifted<0.3'])
    ax.set_title('Диаграмма "ящик с усами" для двух групп')
    ax.set_ylim(0, 23.5)
    ax.set_ylabel('количество устройств')
    plt.close()
    return fig

def h4_build_scatter():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.scatter(df['platform_num'], df['target_unshifted'], alpha=0.6)
    # Оформляем график
    ax.set_xlabel('platform_num')
    ax.set_ylabel('target_unshifted')
    ax.set_title('Взаимосвязь target_unshifted c количеством устройств')
    ax.grid(True, alpha=0.3)
    plt.close()
    return fig
# Создание интерфейса Gradio
with gr.Blocks() as demo:

    with gr.Row():
        btn_update = gr.Button("Нарисовать дашборд")
    with gr.Row():
        gr.Markdown("## Гипотеза 2")
    with gr.Row():
        with gr.Column(): 
            gr.Markdown("### Анализ распределения hist_return_rate")
            h2_output_hist = gr.Plot(label="Гистограмма", format='png')
        with gr.Column(): 
            gr.Markdown("### Различия количества устройств по к. истор. возвратов")
            h2_output_box = gr.Plot(label="Ящик с усами", format='png')
    with gr.Row():
        with gr.Column(): 
            gr.Markdown("### Анализ взаимосвязи к. истор. возвратов с кол-вом устройств")
            h2_output_scatter = gr.Plot(label='Диаграмма рассеяния', format='png')
    with gr.Row():
        gr.Markdown("## Гипотеза 4")
    with gr.Row():
            with gr.Column(): 
                gr.Markdown("### Анализ различий в количестве устройств по target_unshifted")
                h4_output_boxplot = gr.Plot(label="Ящик с усами", format='png')
            with gr.Column(): 
                gr.Markdown("### Анализ взаимосвязи target_unshifted с кол-вом устройств")
                h4_output_scatter = gr.Plot(label="Диаграмма рассеяния", format='png')
    ##Апдейтеры
    btn_update.click(
        fn=h2_build_distrib_histogram,
        inputs=[],
        outputs=[h2_output_hist]
    )
    btn_update.click(
        fn=h2_build_boxplot,
        inputs=[],
        outputs=[h2_output_box]
    )
    btn_update.click(
        fn=h2_build_corr,
        inputs=[],
        outputs=[h2_output_scatter]
    )
    btn_update.click(
        fn=h4_build_boxplot,
        inputs=[],
        outputs=[h4_output_boxplot]
    )
    btn_update.click(
        fn=h4_build_scatter,
        inputs=[],
        outputs=[h4_output_scatter]
    )



# 3. Запускаем Gradio
demo.launch()
