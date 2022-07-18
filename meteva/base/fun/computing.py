import pandas as pd
import numpy as np
import meteva
from scipy.ndimage import convolve
from scipy.ndimage.filters import uniform_filter
import copy
#将两个站点数据信息进行合并，并去重。

def put_stadata_on_station(sta,station):
    sta_list = meteva.base.split(sta)
    sta1_list = []
    for sta0 in sta_list:
        #删除重复行
        sta1 = sta0.drop_duplicates(['id'])
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
        df.attrs = copy.deepcopy(sta.attrs)
        sta1_list.append(df)
    sta_new = pd.concat(sta1_list,axis=0)
    return sta_new


def smooth(grd,smooth_times = 1,used_coords = "xy"):
    if (grd is None):
        return None
    levels = grd["level"].values
    times = grd["time"].values
    dtimes = grd["dtime"].values
    members = grd["member"].values
    grid0 = meteva.base.basicdata.get_grid_of_data(grd)
    grd_new = meteva.base.grid_data(grid0)
    for i in range(len(levels)):
        for j in range(len(times)):
            for k in range(len(dtimes)):
                for m in range(len(members)):
                    dat = grd.values[m,i,j,k,:,:]
                    #print(dat.shape)
                    kernel = np.array([[0.0625, 0.125, 0.0625],
                                       [0.125, 0.25, 0.125],
                                       [0.0625, 0.125, 0.0625]])
                    for s in range(smooth_times):
                        dat = convolve(dat, kernel)

                    grd_new.values[m,i,j,k,:,:] = dat[:,:]
    return grd_new




def moving_avarage(grd, half_window_size):
    return moving_ave(grd,half_window_size)


def moving_ave(grd,half_window_size):
    # 该函数计算网格点附近矩形方框内的平均值
    # 使用同规格的场，确保网格范围和分辨率一致
    # window_size 窗口尺度

    levels = copy.deepcopy(grd["level"].values)
    times = copy.deepcopy(grd["time"].values)
    dtimes = copy.deepcopy(grd["dtime"].values)
    members = copy.deepcopy(grd["member"].values)
    grd1 = copy.deepcopy(grd)
    size = half_window_size * 2 + 1
    for i in range(len(levels)):
        for j in range(len(times)):
            for k in range(len(dtimes)):
                for m in range(len(members)):
                    dat = grd1.values[m, i, j, k, :, :]
                    # print(type(dat[0,0]))
                    dat1 = uniform_filter(dat, size=size)
                    grd1.values[m, i, j, k, :, :] = np.round(dat1[:, :], 10)
    return grd1


def moving_max(grd, half_window_size):
    # 该函数计算网格点附近矩形方框内的最大值
    # 使用同规格的场，确保网格范围和分辨率一致
    # window_size 窗口尺度
    levels = copy.deepcopy(grd["level"].values)
    times = copy.deepcopy(grd["time"].values)
    dtimes = copy.deepcopy(grd["dtime"].values)
    members = copy.deepcopy(grd["member"].values)
    grd1 = copy.deepcopy(grd)
    nlon = len(grd["lon"])
    nlat = len(grd["lat"])


    size = half_window_size * 2 + 1
    for i in range(len(levels)):
        for j in range(len(times)):
            for k in range(len(dtimes)):
                for m in range(len(members)):

                    dat = grd1.values[m,i,j,k,:,:]
                    vmin = np.min(dat)
                    dat_3d_lon = np.ones((size,nlat,nlon))*vmin
                    for p in range(-half_window_size,half_window_size+1):
                        ps0 = max(0,p)
                        pe0 = min(nlon,nlon + p)
                        dat_3d_lon[p,:,ps0 : pe0] = dat[:,(ps0 - p):(pe0-p)]
                    dat_max_lon = np.max(dat_3d_lon,axis=0)

                    dat_3d_lat = np.ones((size,nlat,nlon))*vmin
                    for p in range(-half_window_size,half_window_size+1):
                        ps0 = max(0,p)
                        pe0 = min(nlat,nlat + p)
                        dat_3d_lat[p,ps0 : pe0,:] = dat_max_lon[(ps0 - p):(pe0-p),:]
                    dat_max_lat = np.max(dat_3d_lat,axis=0)

                    grd1.values[m, i, j, k, :, :] = dat_max_lat[:, :]
                    # 首先在x方向做求最大
    return grd1



def moving_min(grd, half_window_size):
    # 该函数计算网格点附近矩形方框内的最小值
    # 使用同规格的场，确保网格范围和分辨率一致
    # window_size 窗口尺度
    levels = copy.deepcopy(grd["level"].values)
    times = copy.deepcopy(grd["time"].values)
    dtimes = copy.deepcopy(grd["dtime"].values)
    members = copy.deepcopy(grd["member"].values)
    grd1 = copy.deepcopy(grd)
    nlon = len(grd["lon"])
    nlat = len(grd["lat"])


    size = half_window_size * 2 + 1
    for i in range(len(levels)):
        for j in range(len(times)):
            for k in range(len(dtimes)):
                for m in range(len(members)):

                    dat = grd1.values[m,i,j,k,:,:]
                    vmax = np.max(dat)
                    dat_3d_lon = np.ones((size,nlat,nlon))*vmax
                    for p in range(-half_window_size,half_window_size+1):
                        ps0 = max(0,p)
                        pe0 = min(nlon,nlon + p)
                        dat_3d_lon[p,:,ps0 : pe0] = dat[:,(ps0 - p):(pe0-p)]
                    dat_max_lon = np.min(dat_3d_lon,axis=0)

                    dat_3d_lat = np.ones((size,nlat,nlon))*vmax
                    for p in range(-half_window_size,half_window_size+1):
                        ps0 = max(0,p)
                        pe0 = min(nlat,nlat + p)
                        dat_3d_lat[p,ps0 : pe0,:] = dat_max_lon[(ps0 - p):(pe0-p),:]
                    dat_max_lat = np.min(dat_3d_lat,axis=0)

                    grd1.values[m, i, j, k, :, :] = dat_max_lat[:, :]
                    # 首先在x方向做求最大
    return grd1


def moving_std(grd,half_window_size):
    # 该函数计算网格点附近矩形方框内的标准差
    # 使用同规格的场，确保网格范围和分辨率一致
    # window_size 窗口尺度
    grd_move_mean = moving_avarage(grd,half_window_size)
    delta = copy.deepcopy(grd)
    delta.values[:] = np.power(grd.values[:] - grd_move_mean.values[:],2)
    delta =moving_avarage(delta,half_window_size)
    delta.values = np.sqrt(delta.values)

    return delta



#将两个站点dataframe相加在一起
def add_on_level_time_dtime_id(sta1,sta2,how = "left",default = None):
    if sta1 is None or len(sta1.index)==0:
        return sta2
    elif sta2 is None or len(sta2.index)==0:
        return sta1
    else:
        # 删除重复行
        dtime_type = str(sta1["dtime"].dtype)
        if dtime_type.find("int") < 0:
            print("警告：站点数据的dtime坐标不是整数，可能导致数据后续数据匹配失败，请检查输入数据，将站点数据的dtime坐标设置为整数类型")
            # return None
        df = pd.merge(sta1, sta2, on=["level","time","dtime","id"], how=how)
        # print(len(df.index))
        # df.drop_duplicates(subset=["level","time","dtime","id"],inplace=True)
        # print(len(df.index))

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
        df.attrs = copy.deepcopy(sta1.attrs)
        return df


#将两个站点dataframe相乘
def mutiply_on_level_time_dtime_id(sta1,sta2,how = "left",default = None):
    if sta1 is None:
        return sta2
    elif sta2 is None:
        return sta1
    else:
        # 删除重复行
        dtime_type = str(sta1["dtime"].dtype)
        if dtime_type.find("int") < 0:
            print("警告：站点数据的dtime坐标不是整数，可能导致数据后续数据匹配失败，请检查输入数据，将站点数据的dtime坐标设置为整数类型")
            # return None
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
        df.attrs = copy.deepcopy(sta1.attrs)
        return df


#将两个站点dataframe相减
def minus_on_level_time_dtime_id(sta1,sta2,how = "left",default = None):
    if sta1 is None:
        return sta2
    elif sta2 is None:
        return sta1
    else:
        # 删除重复行
        dtime_type = str(sta1["dtime"].dtype)
        if dtime_type.find("int") < 0:
            print("警告：站点数据的dtime坐标不是整数，可能导致数据后续数据匹配失败，请检查输入数据，将站点数据的dtime坐标设置为整数类型")
            # return None
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

        #对数据列进行相减
        len_d = len_m - len_c1
        for i in range(6,len_c1):
            df[df.columns.values[i]] = df.iloc[:, i] - df.iloc[:, i+len_d]

        #print(df)
        #删除df2对应的数据列
        columns_drop = list(df.columns[len_c1:len_m])
        df.drop(columns_drop, axis=1, inplace=True)

        #重新命名列名称
        df.columns = columns
        df.attrs = copy.deepcopy(sta1.attrs)
        return df

def max_on_level_time_dtime_id(sta1,sta2,how = "left",default = None):
    if sta1 is None:
        return sta2
    elif sta2 is None:
        return sta1
    else:
        # 删除重复行
        dtime_type = str(sta1["dtime"].dtype)
        if dtime_type.find("int") < 0:
            print("警告：站点数据的dtime坐标不是整数，可能导致数据后续数据匹配失败，请检查输入数据，将站点数据的dtime坐标设置为整数类型")
            # return None
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
        df.attrs = copy.deepcopy(sta1.attrs)
        return df


def min_on_level_time_dtime_id(sta1,sta2,how = "left",default = None):
    if sta1 is None:
        return sta2
    elif sta2 is None:
        return sta1
    else:
        # 删除重复行
        dtime_type = str(sta1["dtime"].dtype)
        if dtime_type.find("int") < 0:
            print("警告：站点数据的dtime坐标不是整数，可能导致数据后续数据匹配失败，请检查输入数据，将站点数据的dtime坐标设置为整数类型")
            # return None
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
        df.attrs = copy.deepcopy(sta1.attrs)
        return df


def add_on_id(sta1_0, sta2_0, how="left", default=None):
    if sta1_0 is None:
        return sta2_0
    elif sta2_0 is None:
        return sta1_0
    else:
        # 删除重复行
        dtime_type = str(sta1_0["dtime"].dtype)
        if dtime_type.find("int") < 0:
            print("警告：站点数据的dtime坐标不是整数，可能导致数据后续数据匹配失败，请检查输入数据，将站点数据的dtime坐标设置为整数类型")
            # return None
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
        df.attrs = copy.deepcopy(sta1_0.attrs)
        return df

def max_on_id(sta1_0, sta2_0, how="left"):
    if sta1_0 is None:
        return sta2_0
    elif sta2_0 is None:
        return sta1_0
    else:
        # 删除重复行
        dtime_type = str(sta1_0["dtime"].dtype)
        if dtime_type.find("int") < 0:
            print("警告：站点数据的dtime坐标不是整数，可能导致数据后续数据匹配失败，请检查输入数据，将站点数据的dtime坐标设置为整数类型")
            # return None
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
        df.attrs = copy.deepcopy(sta1_0.attrs)
        return df

def min_on_id(sta1_0, sta2_0, how="left"):
    if sta1_0 is None:
        return sta2_0
    elif sta2_0 is None:
        return sta1_0
    else:
        # 删除重复行
        dtime_type = str(sta1_0["dtime"].dtype)
        if dtime_type.find("int") < 0:
            print("警告：站点数据的dtime坐标不是整数，可能导致数据后续数据匹配失败，请检查输入数据，将站点数据的dtime坐标设置为整数类型")
            # return None
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
        df.attrs = copy.deepcopy(sta1_0.attrs)
        return df


#两个站点dataframe相减
def minus_on_id(sta1_0, sta2_0, how="left", default=None):

    # 删除重复行
    dtime_type = str(sta1_0["dtime"].dtype)
    if dtime_type.find("int") < 0:
        print("警告：站点数据的dtime坐标不是整数，可能导致数据后续数据匹配失败，请检查输入数据，将站点数据的dtime坐标设置为整数类型")
        #return None
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
    df.attrs = copy.deepcopy(sta1_0.attrs)
    return df



#两个dataframe相乘
def multiply_on_id(sta1_0, sta2_0, how="left", default=None):

    dtime_type = str(sta1_0["dtime"].dtype)
    if dtime_type.find("int") < 0:
        print("警告：站点数据的dtime坐标不是整数，可能导致数据后续数据匹配失败，请检查输入数据，将站点数据的dtime坐标设置为整数类型")
        #return None
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
    df.attrs = copy.deepcopy(sta1_0.attrs)
    return df

def reset_value_as_IV(sta,iv_value):
    sta1 = sta.copy()
    data_names = meteva.base.get_stadata_names(sta1)
    for name in data_names:
        sta1.loc[sta1.loc[:,name] == iv_value,name] = meteva.base.IV
    return sta1

def move_fo_time(data,dtime,keep_minus_dtime = True):
    if isinstance(data, pd.DataFrame):
        sta1 = data.copy()
        sta1["time"] = data["time"] + dtime* np.timedelta64(1, 'h')
        sta1["dtime"] = data["dtime"] - dtime
        if not keep_minus_dtime: sta1 = meteva.base.between_dtime_range(sta1,0,10000)
        return sta1
    else:
        grd1 = data.copy()
        grd1.coords["time"]= grd1.coords["time"].values[:] + dtime* np.timedelta64(1, 'h')

        grd1.coords["dtime"] =grd1.coords["dtime"].values[:] -  dtime
        if not keep_minus_dtime:grd1 = meteva.base.between_dtime_range(grd1,0,10000)
        return grd1

def get_ob_from_combined_data(sta_all):
    data_names = meteva.base.get_stadata_names(sta_all)
    sta_ob = meteva.base.sele_by_para(sta_all,member=[data_names[0]])
    dtime = sta_ob["dtime"].values[:]
    sta_ob["time"] = sta_ob["time"] + dtime * np.timedelta64(1, 'h')
    sta_ob["dtime"] = 0
    sta_ob = sta_ob.drop_duplicates(keep="first")
    return sta_ob