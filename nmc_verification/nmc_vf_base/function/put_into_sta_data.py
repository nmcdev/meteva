import pandas as pd
import numpy as np
import copy
import nmc_verification
import datetime
import time


# 两个站点信息合并为一个，在原有的dataframe的基础上增加行数
def join(sta, sta1):
    if (sta is None):
        return sta1
    else:
        sta = pd.concat([sta, sta1])
    sta = sta.drop_duplicates(['id'])
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


def that_the_name_exists(list, value):
    '''
    that_the_name_exists判断value是否在list中  如果存在改value直到不在list中为止
    :param list: 一个要素名列表
    :param value:  要素名
    :return:
    '''
    value = str(value)
    list = [str(i) for i in list]
    if value in list:
        value = str(value) + 'x'
        return that_the_name_exists(list, value)
    else:
        return value


#  两个站点信息合并为一个，以站号为公共部分，在原有的dataframe的基础上增加列数
def merge_on_all_dim(sta, sta1):
    '''
    merge_on_all_dim 合并两个sta_dataframe并且使要素名不重复
    :param sta: 一个站点dataframe
    :param sta1: 一个站点dataframe
    :return:
    '''
    if (sta is None):
        return sta1
    elif sta1 is None:
        return sta
    else:
        columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']
        sta_value_columns = sta.iloc[:, 7:].columns.values.tolist()
        sta1_value_columns = sta1.iloc[:, 7:].columns.values.tolist()
        if len(sta_value_columns) >= len(sta1_value_columns):

            for sta1_value_column in sta1_value_columns:
                ago_name = copy.deepcopy(sta1_value_column)
                sta1_value_column = that_the_name_exists(sta_value_columns, sta1_value_column)
                sta1.rename(columns={ago_name: sta1_value_column},inplace=True)
        else:
            for sta_value_column in sta_value_columns:
                ago_name = copy.deepcopy(sta_value_column)
                sta_value_column = that_the_name_exists(sta1_value_columns, sta_value_column)
                sta.rename(columns={ago_name: sta_value_column})

        df = pd.merge(sta, sta1, on=columns, how='inner')
        return df


def merge_on_id_and_obTime(sta_list):
    '''
    merge_on_id_and_obTime  合并多个sta——dataframe  并且保证合并后的dataframe要素名不重复
    :param sta_list:   含有多个sta_dataframe的列表
    :return:
    '''
    intersection_of_data = None
    for sta in sta_list:
        sta['dtime'] = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
        sta['time'] = sta['time'] + sta['dtime']
        sta['dtime'] = 0

        intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
            intersection_of_data, sta)
    return intersection_of_data
# def merge_on_all_dim(sta, sta1):
#     if (sta is None):
#         return sta1
#     elif sta1 is None:
#         return sta
#     else:
#         columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']
#         df = pd.merge(sta, sta1, on=columns, how='inner')
#         return df
#
#
# def merge_on_id_and_obTime(sta_list):
#     intersection_of_data = None
#     for sta in sta_list:
#         sta['dtime'] = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
#         sta['time'] = sta['time'] + sta['dtime']
#         sta['dtime'] = 0
#         intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
#             intersection_of_data, sta)
#     sta_value_columns_list = intersection_of_data.iloc[:, 7:].columns.values.tolist()
#     sta_value_columns_list = [str(sta_value) for sta_value in sta_value_columns_list]
#     sta_value_columns_set = set(sta_value_columns_list)
#
#     for sta_value in sta_value_columns_set:
#         num = sta_value_columns_list.count(sta_value)
#         if num > 1:
#             for i in range(num - 1):
#                 t = time.time()
#                 sta_value_columns_list[sta_value_columns_list.index(sta_value)] = sta_value + str(round(t * 1000))
#     sta_value_columns_list = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt'] + sta_value_columns_list
#     intersection_of_data.columns = sta_value_columns_list
#     return  intersection_of_data

    # lenght = len(sta_list)
    #     # corr_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']
    #     # data = 'data'
    #     # for i in range(0, lenght):
    #     #     data1 = data + str(i)
    #     #     corr_columns.append(data1)
    #     # intersection_of_data.columns = corr_columns
    #     #
    #     # nmc_verification.nmc_vf_base.sta_data(intersection_of_data)
    #     # return intersection_of_data
