import pandas as pd
import numpy as np
import copy

def join(sta,sta1):
    if(sta is None):
        return sta1
    else:
        sta = pd.concat([sta,sta1])
    return sta


def merge(sta,sta1):

    df = pd.merge(sta, sta1, on='id', how='left')
    columns = list(sta.columns)
    len_sta = len(columns)
    # 删除合并后第二组时空坐标信息
    drop_col = list(df.columns[len_sta:len_sta + 6])
    df.drop(drop_col, axis=1, inplace=True)
    columns_dim = list(sta.columns)[0:7]
    columns_data = list(df.columns)[7:]
    columns = columns_dim + columns_data
    df.columns = columns
    return df
