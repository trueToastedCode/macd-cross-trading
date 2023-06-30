import logging
import pandas as pd
import numpy as np

from ...signal import *
from .candles_since import candles_since


def add_total_signal(df, new_data_int_idx, new_data_dt_idx, max_candle_count, timeframe, max_rsi):
    if new_data_int_idx == -1:
        macd_all_cross_down_rows = df[
            (df.MACD_Zero_Cross == MACD_CROSS_DOWN) |
            (df.MACD_Cross == MACD_CROSS_DOWN)
        ]
        macd_all_cross_up_rows = df[
            (df.MACD_Zero_Cross == MACD_CROSS_UP) |
            (df.MACD_Cross == MACD_CROSS_UP)
        ]
        df['TotalSignal'] = np.nan
    else:
        start_all_cross_down_idx = df[
            (new_data_dt_idx - df.index) / timeframe <= max_candle_count
        ].index.min()
        if pd.isnull(start_all_cross_down_idx) or start_all_cross_down_idx >= new_data_dt_idx:
            logging.warning('MACD cross down min index not found')
            return
        macd_all_cross_down_rows = df[
            (df.index >= start_all_cross_down_idx) &
            (
                (df.MACD_Zero_Cross == MACD_CROSS_DOWN) |
                (df.MACD_Cross == MACD_CROSS_DOWN)
            )
        ]
        macd_all_cross_up_rows = df[
            (df.index >= start_all_cross_down_idx) &
            (
                (df.MACD_Zero_Cross == MACD_CROSS_UP) |
                (df.MACD_Cross == MACD_CROSS_UP)
            )
        ]

    for i in range(len(macd_all_cross_down_rows)):
        macd_cross_down_row = macd_all_cross_down_rows.iloc[i]

        macd_cross_up_idx = macd_all_cross_up_rows[
            macd_all_cross_up_rows.index > macd_cross_down_row.name
        ].index.min()
        if pd.isnull(macd_cross_up_idx):
            continue

        candle_count = candles_since(macd_cross_down_row.name, macd_cross_up_idx, timeframe)
        if candle_count > max_candle_count:
            continue

        macd_cross_up_row = macd_all_cross_up_rows.loc[macd_cross_up_idx]
        if macd_cross_up_row.RSI > max_rsi:
            continue

        df.loc[macd_cross_up_row.name, 'TotalSignal'] = LONG_SIGNAL
