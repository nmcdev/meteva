# -*- coding:UTF-8 -*-
import copy
import pandas as pd
import numpy as np
from pandas import DataFrame
import copy
import  read


def sta_data(dframe0,columns):


    dframe1 = copy.deepcopy(dframe0)
    dframe1.reset_index(inplace=True)
    dframe1.rename(columns={0:'sta'},inplace=True)
    corr_columns = ['level', 'sta', 'time', 'dtime', 'lon', 'lat', 'alt']

    # 将列名变为小写
    columns_1 = []
    for column in columns:
        column = column.lower()
        columns_1.append(column)
    columns = columns_1

    # 将缺省的列填充  按照改变列的顺序
    for corr_column in corr_columns:
        if corr_column not in columns:
            columns_num = corr_columns.index(corr_column)
            dframe1.insert(columns_num, corr_column, 9999)

        df_n = dframe1[corr_column]
        dframe1.drop(corr_column, axis=1,inplace=True)
        dframe1.insert(corr_columns.index(corr_column),corr_column, df_n)


    # 更改data列名
    data = 'data'
    num = dframe1.shape[1]-len(corr_columns)
    for i in range(0,num):
        data1 = data+str(i)
        corr_columns.append(data1)
    print(dframe1)
    dframe1.columns = corr_columns
    print('columns：',dframe1.columns)

    # 排序
    new_columns = list(dframe1.columns.values)

    dframe1.sort_values(by=new_columns[:4],inplace=False)
    print(dframe1)
    # 单层索引
    return dframe1

def get_data_names(sta):
    coor_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']
    columns = sta.columns
    data_columns = []
    for column in columns:
        if column not in coor_columns:
            data_columns.append(column)
    return data_columns

def get_coord_names():
    return ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']

def set_data_name(sta,data_name):
    coor_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt',data_name]
    sta.columns = coor_columns
    return

def reset_id(sta):
    '''
    将带有a-z,A-Z格式的按照，通过ASCII码转换为数字，拼接完之后，再返回
    例如：sta = 'abdf' 返回：9798100102
    :param sta:站号
    :return:ASCII转码之后的int型站号。
    '''
    a_list = []
    b_list = []
    for item in sta:
        a_list.append(item)
    num = len(a_list)
    for i in range(0, num):
        num = ord(a_list[i])
        b_list.append(str(num))
    item2 = "".join(b_list)
    return int(item2)

def set_time_dtime_level(sta,time = None,dtime = None,level = None):
    if time is not None:
        sta['time'] = time
    if dtime is not None:
        sta['dtime'] = dtime
    if level is not None:
        sta['level'] = level

