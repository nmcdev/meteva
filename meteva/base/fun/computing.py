import pandas as pd
import numpy as np
import meteva
from scipy.ndimage import convolve
from scipy.ndimage.filters import uniform_filter
import math
import copy
#将两个站点数据信息进行合并，并去重。

def put_stadata_on_station(sta,station):
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
    for i in range(len_c1+5,len_m):
        name1 = columns_m[i]
        name2 = columns_m[6]
        df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]


    #删除合并后多余的时空信息列
    len_s = len(list(station.columns))
    drop_col = list(df.columns[6:len_s+5])
    #print(drop_col)
    df.drop(drop_col, axis=1, inplace=True)
    #重新命名列名称
    df.columns = sta1.columns
    return df


def smooth(grd,smooth_times = 1,used_coords = "xy"):
    if (grd is None):
        return None
    levels = grd["level"].values
    times = grd["time"].values
    dtimes = grd["dtime"].values
    members = grd["member"].values
    lons = grd['lon'].values
    lats = grd['lat'].values
    grid0 = meteva.base.basicdata.get_grid_of_data(grd)
    grd_new = meteva.base.grid_data(grid0)
    for i in range(len(levels)):
        for j in range(len(times)):
            for k in range(len(dtimes)):
                for m in range(len(members)):
                    dat = grd.values[m,i,j,k,:,:]
                    print(dat.shape)
                    kernel = np.array([[0.0625, 0.125, 0.0625],
                                       [0.125, 0.25, 0.125],
                                       [0.0625, 0.125, 0.0625]])
                    for s in range(smooth_times):
                        dat = convolve(dat, kernel)

                    grd_new.values[m,i,j,k,:,:] = dat[:,:]
    return grd_new




def moving_avarage(grd, half_window_size):
    # 该函数计算网格点附近矩形方框内的平均值
    # 使用同规格的场，确保网格范围和分辨率一致
    # window_size 窗口尺度

    levels = copy.deepcopy(grd["level"].values)
    times = copy.deepcopy(grd["time"].values)
    dtimes = copy.deepcopy(grd["dtime"].values)
    members = copy.deepcopy(grd["member"].values)
    grd1 = copy.deepcopy(grd)
    '''
    nlon = len(grd["lon"])
    nlat = len(grd["lat"])
    

    i0 = np.arange(nlon)
    i_s = i0 - half_window_size
    i_s[i_s < 0] = 0
    i_e = i0 + half_window_size+1
    i_e[i_e > nlon] = nlon

    j0 = np.arange(nlat)
    j_s = j0 - half_window_size
    j_s[j_s < 0] = 0
    j_e = j0 + half_window_size+1
    j_e[j_e > nlat] = nlat


    IS,J = np.meshgrid(i_s,j0)
    IE,_ = np.meshgrid(i_e,j0)

    I,JS = np.meshgrid(i0,j_s)
    _,JE = np.meshgrid(i0,j_e)

    #计算每个网格点上的累计格点数
    accu_num = (IE - IS ) * (JE - JS)
    dat_accumulate_x = np.zeros((nlat,nlon+1))
    dat_accumulate_y = np.zeros((nlat+1, nlon))
    '''
    size = half_window_size* 2 + 1
    for i in range(len(levels)):
        for j in range(len(times)):
            for k in range(len(dtimes)):
                for m in range(len(members)):
                    dat = grd1.values[m, i, j, k, :, :]
                    dat1 = uniform_filter(dat,size=size)
                    grd1.values[m, i, j, k, :, :] = np.round(dat1[:,:],10)
                    '''
                    dat = grd1.values[m,i,j,k,:,:]
                    # 首先在x方向做累加
                    dat_accumulate_x[:,1:] = dat[:,:]
                    for ii in range(nlon):
                        dat_accumulate_x[:,ii+1] = dat_accumulate_x[:,ii] + dat[:,ii]

                    #计算x方向左右累积量的差，即得到格点附近东西向滑动累加
                    dat = dat_accumulate_x[J,IE] - dat_accumulate_x[J,IS]

                    # 然后在y方向做累加
                    dat_accumulate_y[1:,:] = dat[:,:]
                    for jj in range(nlat):
                        dat_accumulate_y[jj+1,:] = dat_accumulate_y[jj,:] + dat[jj,:]

                    #计算y方向上下累计量的差，即得到格点附近东西向滑动累加
                    dat = dat_accumulate_y[JE, I] - dat_accumulate_y[JS, I]

                    # 计算平均
                    grd1.values[m,i,j,k,:,:] = dat/accu_num

                    '''
    return grd1




#将两个站点dataframe相加在一起
def add_on_level_time_dtime_id(sta1,sta2,how = "left",default = None):
    if sta1 is None:
        return sta2
    elif sta2 is None:
        return sta1
    else:
        # 删除重复行
        df = pd.merge(sta1, sta2, on=["level","time","dtime","id"], how=how)
        #print(len(sta1.index))
        #print(len(sta2.index))
        #print(len(df.index))
        #时间，时效和层次，采用df1的

        #站点取df1，df2中非缺省的
        columns = list(sta1.columns)
        len_c1 = len(columns)
        columns_m = list(df.columns)
        #print(columns_m)
        for i in range(4,6):
            name1 = columns_m[i]
            name2 = columns_m[i+len_c1-4]
            df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]


        #删除合并后第二组时空坐标信
        drop_col = list(df.columns[len_c1:len_c1+2])
        df.drop(drop_col, axis=1, inplace=True)

        #print(df)
        #相加前是否要先设定缺省值
        columns_m = list(df.columns)
        len_m = len(columns_m)
        if default is not None:
            for i in range(6, len_m):
                df.iloc[:, i].fillna(default, inplace=True)

        #对数据列进行相加
        len_d = len_m - len_c1
        for i in range(6,len_c1):
            df[df.columns.values[i]] = df.iloc[:, i] + df.iloc[:, i+len_d]

        #print(df)
        #删除df2对应的数据列
        columns_drop = list(df.columns[len_c1:len_m])
        df.drop(columns_drop, axis=1, inplace=True)

        #重新命名列名称
        df.columns = columns
        return df


#将两个站点dataframe相乘在一起
def mutiply_on_level_time_dtime_id(sta1,sta2,how = "left",default = None):
    if sta1 is None:
        return sta2
    elif sta2 is None:
        return sta1
    else:
        # 删除重复行
        df = pd.merge(sta1, sta2, on=["level","time","dtime","id"], how=how)
        #print(len(sta1.index))
        #print(len(sta2.index))
        #print(len(df.index))
        #时间，时效和层次，采用df1的

        #站点取df1，df2中非缺省的
        columns = list(sta1.columns)
        len_c1 = len(columns)
        columns_m = list(df.columns)
        #print(columns_m)
        for i in range(4,6):
            name1 = columns_m[i]
            name2 = columns_m[i+len_c1-4]
            df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]


        #删除合并后第二组时空坐标信
        drop_col = list(df.columns[len_c1:len_c1+2])
        df.drop(drop_col, axis=1, inplace=True)

        #print(df)
        #相加前是否要先设定缺省值
        columns_m = list(df.columns)
        len_m = len(columns_m)
        if default is not None:
            for i in range(6, len_m):
                df.iloc[:, i].fillna(default, inplace=True)

        #对数据列进行相乘
        len_d = len_m - len_c1
        for i in range(6,len_c1):
            df[df.columns.values[i]] = df.iloc[:, i] * df.iloc[:, i+len_d]

        #print(df)
        #删除df2对应的数据列
        columns_drop = list(df.columns[len_c1:len_m])
        df.drop(columns_drop, axis=1, inplace=True)

        #重新命名列名称
        df.columns = columns
        return df


def max_on_level_time_dtime_id(sta1,sta2,how = "left",default = None):
    if sta1 is None:
        return sta2
    elif sta2 is None:
        return sta1
    else:
        # 删除重复行
        df = pd.merge(sta1, sta2, on=["level","time","dtime","id"], how=how)
        #print(len(sta1.index))
        #print(len(sta2.index))
        #print(len(df.index))
        #时间，时效和层次，采用df1的

        #站点取df1，df2中非缺省的
        columns = list(sta1.columns)
        len_c1 = len(columns)
        columns_m = list(df.columns)
        #print(columns_m)
        for i in range(4,6):
            name1 = columns_m[i]
            name2 = columns_m[i+len_c1-4]
            df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]


        #删除合并后第二组时空坐标信
        drop_col = list(df.columns[len_c1:len_c1+2])
        df.drop(drop_col, axis=1, inplace=True)

        #print(df)
        #相加前是否要先设定缺省值
        columns_m = list(df.columns)
        len_m = len(columns_m)
        if default is not None:
            for i in range(6, len_m):
                df.iloc[:, i].fillna(default, inplace=True)

        #对数据列进行相加
        len_d = len_m - len_c1
        for i in range(6,len_c1):

            values = df[[df.columns[i],df.columns[i+len_d]]].values
            max_value = values.max(axis = 1)
            df[df.columns.values[i]] = max_value

        #print(df)
        #删除df2对应的数据列
        columns_drop = list(df.columns[len_c1:len_m])
        df.drop(columns_drop, axis=1, inplace=True)

        #重新命名列名称
        df.columns = columns
        return df


def min_on_level_time_dtime_id(sta1,sta2,how = "left",default = None):
    if sta1 is None:
        return sta2
    elif sta2 is None:
        return sta1
    else:
        # 删除重复行
        df = pd.merge(sta1, sta2, on=["level","time","dtime","id"], how=how)
        #print(len(sta1.index))
        #print(len(sta2.index))
        #print(len(df.index))
        #时间，时效和层次，采用df1的

        #站点取df1，df2中非缺省的
        columns = list(sta1.columns)
        len_c1 = len(columns)
        columns_m = list(df.columns)
        #print(columns_m)
        for i in range(4,6):
            name1 = columns_m[i]
            name2 = columns_m[i+len_c1-4]
            df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]


        #删除合并后第二组时空坐标信
        drop_col = list(df.columns[len_c1:len_c1+2])
        df.drop(drop_col, axis=1, inplace=True)

        #print(df)
        #相加前是否要先设定缺省值
        columns_m = list(df.columns)
        len_m = len(columns_m)
        if default is not None:
            for i in range(6, len_m):
                df.iloc[:, i].fillna(default, inplace=True)

        #对数据列进行相加
        len_d = len_m - len_c1
        for i in range(6,len_c1):

            values = df[[df.columns[i],df.columns[i+len_d]]].values
            min_value = values.min(axis = 1)
            df[df.columns.values[i]] = min_value

        #print(df)
        #删除df2对应的数据列
        columns_drop = list(df.columns[len_c1:len_m])
        df.drop(columns_drop, axis=1, inplace=True)

        #重新命名列名称
        df.columns = columns
        return df


def add_on_id(sta1_0, sta2_0, how="left", default=None):
    if sta1_0 is None:
        return sta2_0
    elif sta2_0 is None:
        return sta1_0
    else:
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
        for i in range(4,6):
            name1 = columns_m[i]
            name2 = columns_m[i+len_c1-1]
            df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]


        #删除合并后第二组时空坐标信
        drop_col = list(df.columns[len_c1:len_c1+5])
        df.drop(drop_col, axis=1, inplace=True)

        #print(df)
        #相加前是否要先设定缺省值
        columns_m = list(df.columns)
        len_m = len(columns_m)
        if default is not None:
            for i in range(6, len_m):
                df.iloc[:, i].fillna(default, inplace=True)

        #对数据列进行相加
        len_d = len_m - len_c1
        for i in range(6,len_c1):
            df[df.columns.values[i]] = df.iloc[:, i] + df.iloc[:, i+len_d]

        #print(df)
        #删除df2对应的数据列
        columns_drop = list(df.columns[len_c1:len_m])
        df.drop(columns_drop, axis=1, inplace=True)

        #重新命名列名称
        df.columns = columns
        return df

def max_on_id(sta1_0, sta2_0, how="left"):
    if sta1_0 is None:
        return sta2_0
    elif sta2_0 is None:
        return sta1_0
    else:
        # 删除重复行
        sta2 = sta2_0.drop_duplicates(['id'])
        sta1 = sta1_0.drop_duplicates(['id'])


        df = pd.merge(sta1, sta2, on='id', how=how)
        df.iloc[:, 0] = df.iloc[0, 0]
        df.iloc[:, 1] = df.iloc[0, 1]
        df.iloc[:, 2] = df.iloc[0, 2]
        #站点取df1，df2中非缺省的
        columns = list(sta1.columns)
        len_c1 = len(columns)
        columns_m = list(df.columns)
        for i in range(4,6):
            name1 = columns_m[i]
            name2 = columns_m[i+len_c1]
            df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]

        #删除合并后第二组时空坐标信息
        drop_col = list(df.columns[len_c1:len_c1+5])
        df.drop(drop_col, axis=1, inplace=True)

        #对数据列判断最大
        datas = df.iloc[:,6:].values
        datas[datas == meteva.base.IV] = -meteva.base.IV
        maxdata = np.max(datas,axis=1)
        df.iloc[:,6] = maxdata
        #print(df)
        #删除df2对应的数据列
        len_m = len(df.columns)
        columns_drop = list(df.columns[7:len_m])
        df.drop(columns_drop, axis=1, inplace=True)
        #重新命名列名称
        df.columns = columns

        return df

def min_on_id(sta1_0, sta2_0, how="left"):
    if sta1_0 is None:
        return sta2_0
    elif sta2_0 is None:
        return sta1_0
    else:
        # 删除重复行
        sta2 = sta2_0.drop_duplicates(['id'])
        sta1 = sta1_0.drop_duplicates(['id'])
        df = pd.merge(sta1, sta2, on='id', how=how)
        df.iloc[:, 0] = df.iloc[0, 0]
        df.iloc[:, 1] = df.iloc[0, 1]
        df.iloc[:, 2] = df.iloc[0, 2]
        #站点取df1，df2中非缺省的
        columns = list(sta1.columns)
        len_c1 = len(columns)
        columns_m = list(df.columns)
        for i in range(4,6):
            name1 = columns_m[i]
            name2 = columns_m[i+len_c1]
            df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]

        #删除合并后第二组时空坐标信息
        drop_col = list(df.columns[len_c1:len_c1+5])
        df.drop(drop_col, axis=1, inplace=True)

        #对数据列判断最大
        datas = df.iloc[:,6:].values
        mindata = np.min(datas,axis=1)
        df.iloc[:,6] = mindata
        #print(df)
        #删除df2对应的数据列
        len_m = len(df.columns)
        columns_drop = list(df.columns[7:len_m])
        df.drop(columns_drop, axis=1, inplace=True)
        #重新命名列名称
        df.columns = columns

        return df


#两个站点dataframe相减
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
    for i in range(4,6):
        name1 = columns_m[i]
        name2 = columns_m[i+len_c1]
        df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]

    #删除合并后第二组时空坐标信息
    drop_col = list(df.columns[len_c1:len_c1+5])
    df.drop(drop_col, axis=1, inplace=True)

    #相加前是否要先设定缺省值
    columns_m = list(df.columns)
    len_m = len(columns_m)
    if default is not None:
        for i in range(6, len_m):
            df.iloc[:, i].fillna(default, inplace=True)

    #对数据列进行相加
    len_d = len_m - len_c1
    for i in range(6,len_c1):
        df[df.columns.values[i]] = df.iloc[:, i] - df.iloc[:, i+len_d]

    #删除df2对应的数据列
    columns_drop = list(df.columns[len_c1:len_m])
    df.drop(columns_drop, axis=1, inplace=True)

    #重新命名列名称
    df.columns = columns

    return df



#两个dataframe相乘
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
    for i in range(4,6):
        name1 = columns_m[i]
        name2 = columns_m[i+len_c1]
        df.loc[df[name1].isnull(), name1] = df[df[name1].isnull()][name2]

    #删除合并后第二组时空坐标信息
    drop_col = list(df.columns[len_c1:len_c1+5])
    df.drop(drop_col, axis=1, inplace=True)

    #相加前是否要先设定缺省值
    columns_m = list(df.columns)
    len_m = len(columns_m)
    if default is not None:
        for i in range(6, len_m):
            df.iloc[:, i].fillna(default, inplace=True)

    #对数据列进行相加
    len_d = len_m - len_c1
    for i in range(6,len_c1):
        df[df.columns.values[i]] = df.iloc[:, i] * df.iloc[:, i+len_d]

    #删除df2对应的数据列
    columns_drop = list(df.columns[len_c1:len_m])
    df.drop(columns_drop, axis=1, inplace=True)

    #重新命名列名称
    df.columns = columns

    return df

def reset_value_as_IV(sta,iv_value):
    sta1 = sta.copy()
    data_names = meteva.base.get_stadata_names(sta1)
    for name in data_names:
        sta1.loc[sta1.loc[:,name] == iv_value,name] = meteva.base.IV
    return sta1

def move_fo_time(sta,dtime):
    sta1 = sta.copy()
    sta1["time"] = sta["time"] + dtime* np.timedelta64(1, 'h')
    sta1["dtime"] = sta["dtime"] - dtime
    return sta1