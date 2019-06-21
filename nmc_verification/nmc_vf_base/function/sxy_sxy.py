import pandas as pd
import numpy as np
import copy
from scipy.spatial import cKDTree
import nmc_verification


def set_data_to(sta,station):
    #删除重复行
    sta1 = sta.drop_duplicates(['id'])
    #先将数据合并
    df = pd.merge(station,sta1, on='id', how='left')
    #时间，时效和层次，采用sta的
    df.iloc[:, 0] = sta1.iloc[0, 0]
    df.iloc[:, 1] = sta1.iloc[0, 1]
    df.iloc[:, 2] = sta1.iloc[0, 2]

    #如果合并后sta对应的数据是缺省，则用station里的data0列补充
    columns = list(sta1.columns)
    len_c1 = len(columns)
    columns_m = list(df.columns)
    len_m = len(columns_m)
    for i in range(len_c1+6,len_m):
        name1 = columns_m[i]
        name2 = columns_m[7]
        df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]


    #删除合并后多余的时空信息列
    len_s = len(list(station.columns))
    drop_col = list(df.columns[7:len_s+6])
    df.drop(drop_col, axis=1, inplace=True)
    #重新命名列名称
    df.columns = sta1.columns

    return df

def set_default_value(sta,default):
    columns = list(sta.columns)
    len_c = len(columns)
    for i in range(7,len_c):
        name1 = columns[i]
        sta.loc[sta[name1].isnull(), name1] = default


def drop_nan(sta):
    columns = list(sta.columns)
    columns_data = columns[7:]
    df = sta.dropna(subset = columns_data)
    return df

def add_on_id(sta1_0, sta2_0, how="left", default=None):
    if sta1_0 is None:
        return sta2_0
    elif sta2_0 is None:
        return sta1_0
    else:
        #将两个df1 合并在一起
        # 删除重复行
        sta2 = sta2_0.drop_duplicates(['id'])
        sta1 = sta1_0.drop_duplicates(['id'])

        df = pd.merge(sta1, sta2, on='id', how=how)
        #print(len(sta1.index))
        #print(len(sta2.index))
        #print(len(df.index))
        #时间，时效和层次，采用df1的
        df.iloc[:, 0] = df.iloc[0, 0]
        df.iloc[:, 1] = df.iloc[0, 1]
        df.iloc[:, 2] = df.iloc[0, 2]

        #站点取df1，df2中非缺省的
        columns = list(sta1.columns)
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
def minus_on_id(sta1_0, sta2_0, how="left", default=None):

    # 删除重复行
    sta2 = sta2_0.drop_duplicates(['id'])
    sta1 = sta1_0.drop_duplicates(['id'])
    #将两个df1 合并在一起
    df = pd.merge(sta1, sta2, on='id', how=how)

    #时间，时效和层次，采用df1的
    df.iloc[:, 0] = df.iloc[0, 0]
    df.iloc[:, 1] = df.iloc[0, 1]
    df.iloc[:, 2] = df.iloc[0, 2]

    #站点取df1，df2中非缺省的
    columns = list(sta1.columns)
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

def multiply_on_id(sta1_0, sta2_0, how="left", default=None):
    # 删除重复行
    sta2 = sta2_0.drop_duplicates(['id'])
    sta1 = sta1_0.drop_duplicates(['id'])

    #将两个df1 合并在一起
    df = pd.merge(sta1, sta2, on='id', how=how)

    #时间，时效和层次，采用df1的
    df.iloc[:, 0] = df.iloc[0, 0]
    df.iloc[:, 1] = df.iloc[0, 1]
    df.iloc[:, 2] = df.iloc[0, 2]

    #站点取df1，df2中非缺省的
    columns = list(sta1.columns)
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


def idw_sta_to_sta(sta0, station,effectR = 1000,nearNum = 16):
    sta1 = station.copy()
    xyz_sta0 = nmc_verification.nmc_vf_base.method.math_tools.lon_lat_to_cartesian(sta0.ix[:, 'lon'], sta0.ix[:, 'lat'], R = nmc_verification.nmc_vf_base.basicdata.const.ER)
    xyz_sta1 = nmc_verification.nmc_vf_base.method.math_tools.lon_lat_to_cartesian(sta1.ix[:, 'lon'], sta1.ix[:, 'lat'], R = nmc_verification.nmc_vf_base.basicdata.const.ER)
    tree = cKDTree(xyz_sta0)
    d, inds = tree.query(xyz_sta1, k=nearNum)
    d += 1e-6
    w = 1.0 / d ** 2
    data_name0 = nmc_verification.nmc_vf_base.basicdata.get_data_names(sta0)[0]
    input_dat = sta0.ix[:,data_name0]
    dat = np.sum(w * input_dat[inds], axis=1) / np.sum(w, axis=1)
    dat[:] = np.where(d[:,0] > effectR,0,dat[:])
    data_name0 = nmc_verification.nmc_vf_base.basicdata.get_data_names(sta1)[0]
    sta1.ix[:,data_name0] = dat
    return sta1

