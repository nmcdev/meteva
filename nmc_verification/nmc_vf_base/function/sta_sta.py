import pandas as pd
import numpy as np
import copy

def set_data_to(df1,station):
    #先将数据合并
    df = pd.merge(station,df1, on='id', how='left')

    #如果合并后df1对应的数据是缺省，则用station里的data0列补充
    columns = list(df1.columns)
    len_c1 = len(columns)
    columns_m = list(df.columns)
    len_m = len(columns_m)
    for i in range(len_c1+6,len_m):
        name1 = columns_m[i]
        name2 = columns_m[7]
        df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]

    #时间，时效和层次，采用df1的
    columns = list(station.columns)
    len_s = len(columns)
    df.iloc[:, 0] = df.iloc[0, len_s]
    df.iloc[:, 1] = df.iloc[0, len_s+1]
    df.iloc[:, 2] = df.iloc[0, len_s+2]


    #删除合并后多余的时空信息列
    drop_col = list(df.columns[7:len_s+6])
    df.drop(drop_col, axis=1, inplace=True)

    #重新命名列名称
    df.columns = df1.columns

    return df

def set_default_value(df1,default):
    columns = list(df1.columns)
    len_c = len(columns)
    for i in range(7,len_c):
        name1 = columns[i]
        df1.loc[df1[name1].isnull(), name1] = default


def drop_nan(df1):
    columns = list(df1.columns)
    columns_data = columns[7:]
    df = df1.dropna(subset = columns_data)
    return df

def add_on_id(df1, df2, how="left", default=None):

    #将两个df1 合并在一起
    df = pd.merge(df1, df2, on='id', how=how)

    #时间，时效和层次，采用df1的
    df.iloc[:, 0] = df.iloc[0, 0]
    df.iloc[:, 1] = df.iloc[0, 1]
    df.iloc[:, 2] = df.iloc[0, 2]

    #站点取df1，df2中非缺省的
    columns = list(df1.columns)
    len_c1 = len(columns)
    columns_m = list(df.columns)
    for i in range(4,7):
        name1 = columns_m[i]
        name2 = columns_m[i+len_c1]
        df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]

    #删除合并后第二组时空坐标信息
    drop_col = list(df.columns[len_c1:len_c1+6])
    df.drop(drop_col, axis=1, inplace=True)

    #相加前是否要先设定缺省值
    columns_m = list(df.columns)
    len_m = len(columns_m)
    if default is not None:
        for i in range(7, len_m):
            df.iloc[:, i].fillna(default, inplace=True)

    #对数据列进行相加
    len_d = len_m - len_c1
    for i in range(7,len_c1):
        df[df.columns.values[i]] = df.iloc[:, i] + df.iloc[:, i+len_d]

    #删除df2对应的数据列
    columns_drop = list(df.columns[len_c1:len_m])
    df.drop(columns_drop, axis=1, inplace=True)

    #重新命名列名称
    df.columns = columns

    return df

def minus_on_id(df1, df2, how="left", default=None):

    #将两个df1 合并在一起
    df = pd.merge(df1, df2, on='id', how=how)

    #时间，时效和层次，采用df1的
    df.iloc[:, 0] = df.iloc[0, 0]
    df.iloc[:, 1] = df.iloc[0, 1]
    df.iloc[:, 2] = df.iloc[0, 2]

    #站点取df1，df2中非缺省的
    columns = list(df1.columns)
    len_c1 = len(columns)
    columns_m = list(df.columns)
    for i in range(4,7):
        name1 = columns_m[i]
        name2 = columns_m[i+len_c1]
        df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]

    #删除合并后第二组时空坐标信息
    drop_col = list(df.columns[len_c1:len_c1+6])
    df.drop(drop_col, axis=1, inplace=True)

    #相加前是否要先设定缺省值
    columns_m = list(df.columns)
    len_m = len(columns_m)
    if default is not None:
        for i in range(7, len_m):
            df.iloc[:, i].fillna(default, inplace=True)

    #对数据列进行相加
    len_d = len_m - len_c1
    for i in range(7,len_c1):
        df[df.columns.values[i]] = df.iloc[:, i] - df.iloc[:, i+len_d]

    #删除df2对应的数据列
    columns_drop = list(df.columns[len_c1:len_m])
    df.drop(columns_drop, axis=1, inplace=True)

    #重新命名列名称
    df.columns = columns

    return df

def multiply_on_id(df1, df2, how="left", default=None):

    #将两个df1 合并在一起
    df = pd.merge(df1, df2, on='id', how=how)

    #时间，时效和层次，采用df1的
    df.iloc[:, 0] = df.iloc[0, 0]
    df.iloc[:, 1] = df.iloc[0, 1]
    df.iloc[:, 2] = df.iloc[0, 2]

    #站点取df1，df2中非缺省的
    columns = list(df1.columns)
    len_c1 = len(columns)
    columns_m = list(df.columns)
    for i in range(4,7):
        name1 = columns_m[i]
        name2 = columns_m[i+len_c1]
        df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]

    #删除合并后第二组时空坐标信息
    drop_col = list(df.columns[len_c1:len_c1+6])
    df.drop(drop_col, axis=1, inplace=True)

    #相加前是否要先设定缺省值
    columns_m = list(df.columns)
    len_m = len(columns_m)
    if default is not None:
        for i in range(7, len_m):
            df.iloc[:, i].fillna(default, inplace=True)

    #对数据列进行相加
    len_d = len_m - len_c1
    for i in range(7,len_c1):
        df[df.columns.values[i]] = df.iloc[:, i] * df.iloc[:, i+len_d]

    #删除df2对应的数据列
    columns_drop = list(df.columns[len_c1:len_m])
    df.drop(columns_drop, axis=1, inplace=True)

    #重新命名列名称
    df.columns = columns

    return df

def get_sta_in_grid(df0,grid):

    df1 = copy.deepcopy(df0)
    df1.loc[df1['lon'] > grid.elon, 'data0'] = np.NaN
    df1.loc[df1['lon'] < grid.slon, 'data0'] = np.NaN
    df1.loc[df1['lat'] > grid.elat, 'data0'] = np.NaN
    df1.loc[df1['lat'] < grid.slat, 'data0'] = np.NaN
    df1 = drop_nan(df1)

    return df1