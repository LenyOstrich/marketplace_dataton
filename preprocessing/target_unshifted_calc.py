
import numpy as np
import pandas as pd


def add_target_params(df : pd.DataFrame):
    # Обогащаем датасет признаком target_unshifted
    df['target_unshifted'] = 0.3 - df['target']

    # Обогащаем датасет признаком is_bad_target
    df['is_bad_target'] = df['target_unshifted'] >= 0.3

    return df