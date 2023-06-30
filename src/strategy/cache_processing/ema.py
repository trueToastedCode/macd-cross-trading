import pandas as pd
import numpy as np


def add_ema(df, new_data_int_idx, new_data_dt_idx, src, length, trg):
    k = 2 / (length + 1)
    if new_data_int_idx == -1:
        start_index = df[pd.notnull(df[src])].index.min()
        assert pd.notnull(start_index)
        start_index = df.index.get_loc(start_index)
        result = [np.nan] * (length - 1 + start_index)
        ema = df[src][start_index:start_index + length].sum() / length
        result.append(ema)
        for i in range(length + start_index, len(df)):
            ema = df[src][i] * k + ema * (1 - k)
            result.append(ema)
        df[trg] = result
    else:
        ema = df[trg][new_data_int_idx - 1]
        assert pd.notnull(ema)
        result = []
        for i in range(new_data_int_idx, len(df)):
            ema = df[src][i] * k + ema * (1 - k)
            result.append(ema)
        df.loc[df.index >= new_data_dt_idx, trg] = result
