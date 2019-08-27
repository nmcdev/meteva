import pandas as pd
import numpy as np
import copy
import nmc_verification
import datetime


# 两个站点信息合并为一个，在原有的dataframe的基础上增加行数
def join(sta, sta1):
    if (sta is None):
        return sta1
    else:
        sta = pd.concat([sta, sta1])
    sta = sta.reset_index(drop=True)
    return sta


# 两个站点信息合并为一个，以站号为公共部分，在原有的dataframe的基础上增加列数
def merge(sta, sta1):
    if sta is None:
        return sta1
    elif sta1 is None:
        return sta
    else:
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


# 两个站点信息合并为一个，以站号为公共部分，在原有的dataframe的基础上增加列数
def merge_on_all_dim(sta, sta1):
    if (sta is None):
        return sta1
    elif sta1 is None:
        return sta
    else:
        columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']
        df = pd.merge(sta, sta1, on=columns, how='inner')
        return df


def merge_on_id_and_obTime(sta_list):
    intersection_of_data = None
    for sta in sta_list:
        sta['dtime'] = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
        sta['time'] = sta['time'] + sta['dtime']
        sta['dtime'] = 0
        intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
            intersection_of_data, sta)
    data = 'data'
    new_name = []
    num = len(sta_list)
    for i in range(0, num):
        name = data + str(i)
        new_name.append(name)

    new_name = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']+new_name

    intersection_of_data.columns=new_name
    return intersection_of_data
