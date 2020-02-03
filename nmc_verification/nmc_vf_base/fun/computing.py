import pandas as pd
import numpy as np
import copy
from scipy.spatial import cKDTree
import nmc_verification
from scipy.ndimage import convolve
import math

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
    grid0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd)
    grd_new = nmc_verification.nmc_vf_base.grid_data(grid0)
    for i in range(len(levels)):
        for j in range(len(times)):
            for k in range(len(dtimes)):
                for m in range(len(members)):
                    dat = grd.values[m,i,j,k,:,:]
                    kernel = np.array([[0.0625, 0.125, 0.0625],
                                       [0.125, 0.25, 0.125],
                                       [0.0625, 0.125, 0.0625]])
                    for s in range(smooth_times):
                        dat = convolve(dat, kernel)

                    grd_new.values[m,i,j,k,:,:] = dat[:,:]
    return grd_new



def moving_avarage(grd, half_window_size, skip=1):
    # 该函数计算网格点附近矩形方框内的平均值
    # 使用同规格的场，确保网格范围和分辨率一致
    # window_size 窗口尺度，为了避免窗口较大时计算太慢，可选择跳点取平均，再插值回到原始分辨率
    if (skip > half_window_size):
        print("pdf_skip is larger than half pdf_window_size")
        return None
    grid0 = nmc_verification.nmc_vf_base.get_grid_of_data(grd)
    step_num_lon = int(math.ceil((grid0.nlon - 1) / skip)) + 1
    dlon_skip = grid0.dlon * skip
    elon_skip = grid0.slon + dlon_skip * (step_num_lon - 1)
    step_num_lat = int(math.ceil((grid0.nlat - 1) / skip)) + 1
    dlat_skip = grid0.dlat * skip
    elat_skip = grid0.slat + dlat_skip * (step_num_lat - 1)
    grid_skip = nmc_verification.nmc_vf_base.grid([grid0.slon, elon_skip, dlon_skip],
                                                  [grid0.slat, elat_skip, dlat_skip])
    dat0 = grd.values.squeeze()
    dat = np.zeros((step_num_lat, step_num_lon))