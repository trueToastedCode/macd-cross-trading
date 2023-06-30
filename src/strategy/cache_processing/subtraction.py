def add_subtraction(df, new_data_int_idx, new_data_dt_idx, src, src_from, trg):
    if new_data_int_idx == -1:
        df[trg] = df[src_from] - df[src]
    else:
        _df = df[df.index >= new_data_dt_idx]
        df.loc[df.index >= new_data_dt_idx, trg] = _df[src_from] - _df[src]
