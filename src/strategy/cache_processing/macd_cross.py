from ...signal import *


def add_macd_cross(df, new_data_int_idx):
    for i in range(
        1 if new_data_int_idx == -1 else new_data_int_idx,
        len(df)
    ):
        if df.MACD_Histogram[i - 1] < 0 and df.MACD_Histogram[i] > 0:
            df.loc[df.index[i], 'MACD_Cross'] = MACD_CROSS_UP
        elif df.MACD_Histogram[i - 1] > 0 and df.MACD_Histogram[i] < 0:
            df.loc[df.index[i], 'MACD_Cross'] = MACD_CROSS_DOWN

        if df.MACD_Line[i - 1] < 0 and df.MACD_Line[i] > 0:
            df.loc[df.index[i], 'MACD_Zero_Cross'] = MACD_CROSS_UP
        elif df.MACD_Line[i - 1] > 0 and df.MACD_Line[i] < 0:
            df.loc[df.index[i], 'MACD_Zero_Cross'] = MACD_CROSS_DOWN
