import time
import logging

from .smma_up_down import add_smma_up_down
from .rsi import add_rsi
from .atr import add_atr
from .ema import add_ema
from .subtraction import add_subtraction
from .macd_cross import add_macd_cross
from .total_signal import add_total_signal


class CacheProcessing:
    def __init__(
            self,
            timeframe,
            atr_len,
            rsi_len,
            ema_short_src,
            ema_short_len,
            ema_long_src,
            ema_long_len,
            macd_line_len,
            total_signal_macd_max_candle_count,
            total_signal_max_rsi
    ):
        self.timeframe = timeframe
        self.atr_len = atr_len
        self.rsi_len = rsi_len
        self.ema_short_src = ema_short_src
        self.ema_short_len = ema_short_len
        self.ema_long_src = ema_long_src
        self.ema_long_len = ema_long_len
        self.macd_line_len = macd_line_len
        self.total_signal_macd_max_candle_count = total_signal_macd_max_candle_count
        self.total_signal_max_rsi = total_signal_max_rsi

    def process_cache(self, df, new_data_int_idx=-1):
        time_before = time.perf_counter()

        new_data_dt_idx = None if new_data_int_idx == -1 else df.index[new_data_int_idx]

        default_args = dict(df=df, new_data_int_idx=new_data_int_idx, new_data_dt_idx=new_data_dt_idx)

        add_atr(**default_args, length=self.atr_len)

        add_smma_up_down(**default_args, length=self.rsi_len)

        add_rsi(**default_args)

        add_ema(**default_args, src=self.ema_short_src, length=self.ema_short_len, trg='EMA_Short')

        add_ema(**default_args, src=self.ema_long_src, length=self.ema_long_len, trg='EMA_Long')

        add_subtraction(**default_args, src='EMA_Long', src_from='EMA_Short', trg='MACD_Line')

        add_ema(**default_args, src='MACD_Line', length=self.macd_line_len, trg='MACD_Signal')

        add_subtraction(**default_args, src='MACD_Signal', src_from='MACD_Line', trg='MACD_Histogram')

        add_macd_cross(df=df, new_data_int_idx=new_data_int_idx)

        add_total_signal(**default_args, max_candle_count=self.total_signal_macd_max_candle_count,
                         timeframe=self.timeframe, max_rsi=self.total_signal_max_rsi)

        elapsed = time.perf_counter() - time_before
        logging.debug(f'Processed cache in {round(elapsed, 2)}s')
