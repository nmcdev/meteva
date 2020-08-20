import math
import meteva
from meteva.base.tool.math_tools import lon_lat_to_cartesian
from scipy.spatial import cKDTree
import numpy as np
import copy
import pandas as pd


def mean_of_sta(sta,used_coords = ["member"]):
    sta_mean = sta.loc[:,meteva.base.get_coord_names()]
    sta_data = sta[meteva.base.get_stadata_names(sta)]
    value = sta_data.values
    mean = np.mean(value,axis=1)
    sta_mean['mean'] = mean
    return sta_mean

def std_of_sta(sta,used_coords = ["member"]):
    sta_std = sta.loc[:,meteva.base.get_coord_names()]
    sta_data = sta[meteva.base.get_stadata_names(sta)]
    value = sta_data.values
    std = np.std(value, axis=1)
    sta_std['std'] = std
    return sta_std

def var_of_sta(sta,used_coords = ["member"]):
    sta_var = sta.loc[:,meteva.base.get_coord_names()]
    sta_data = sta[meteva.base.get_stadata_names(sta)]
    value = sta_data.values
    var = np.var(value, axis=1)
    sta_var['var'] = var
    return sta_var

def max_of_sta(sta,used_coords = ["member"]):
    sta_max = sta.loc[:,meteva.base.get_coord_names()]
    sta_data = sta[meteva.base.get_stadata_names(sta)]
    value = sta_data.values
    max1 = np.max(value, axis=1)
    sta_max['max'] = max1
    return sta_max

def min_of_sta(sta,used_coords = ["member"]):
    sta_min = sta.loc[:,meteva.base.get_coord_names()]
    sta_data = sta[meteva.base.get_stadata_names(sta)]
    value = sta_data.values
    min1 = np.min(value, axis=1)
    sta_min['min'] = min1
    return sta_min

def sum_of_sta(sta,used_coords = ["member"],span = None,keep_all = True):
    if not isinstance(used_coords,list):
        used_coords = [used_coords]

    if used_coords == ["member"]:
        sta_sum = sta.loc[:,meteva.base.get_coord_names()]
        sta_data = sta[meteva.base.get_stadata_names(sta)]
        value = sta_data.values
        min1 = np.sum(value, axis=1)
        sta_sum['min'] = min1
        return sta_sum
    elif used_coords == ["time"]:
        if span is None:
            print("if used_coords == [time], span must be int of float bigger than 0 ")
        times = sta.loc[:, 'time'].values
        times = list(set(times))
        times.sort()
        times = np.array(times)
        dtimes = times[1:] - times[0:-1]
        min_dtime = np.min(dtimes)
        min_dhour = min_dtime / np.timedelta64(1, 'h')
        rain_ac = None
        step = int(round(span/min_dhour))
        for i in range(step):
            rain1 = sta.copy()
            rain1["time"] = rain1["time"] + min_dtime * i
            rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac, rain1, how="inner")
        if not keep_all:
            dtimes = times[:] - times[-1]
            dh = (dtimes / min_dtime).astype(np.int32)
            new_times = times[dh % step == 0]
            rain_ac = meteva.base.in_time_list(rain_ac, new_times)
        return rain_ac
    elif used_coords ==["dtime"]:
        if span is None:
            print("if used_coords == [dtime], span must be int of float bigger than 0 ")

        dtimes = sta.loc[:, 'dtime'].values
        dtimes = list(set(dtimes))
        dtimes.sort()
        dtimes = np.array(dtimes)
        dhour_unit = dtimes[0]
        if dhour_unit == 0:
            dhour_unit = dtimes[1]
        rain_ac = sta.copy()
        step = int(round(span/dhour_unit))
        print(step)
        for i in range(1,step):
            rain1 = sta.copy()
            rain1["dtime"] = rain1["dtime"] + dhour_unit * i
            # print(dhour_unit * i)
            rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac, rain1, default=0)

        rain_ac = meteva.base.between_dtime_range(rain_ac,span,dtimes[-1])  # 删除时效小于range的部分
        if not keep_all:
            dh = ((dtimes - dtimes[-1]) / dhour_unit).astype(np.int32)
            new_dtimes = dtimes[dh % step == 0]
            rain_ac = meteva.base.in_dtime_list(rain_ac, new_dtimes)
        return rain_ac



#获取网格数据的平均值
def mean_of_grd(grd,used_coords = ["member"]):
    grid0 = meteva.base.basicdata.get_grid_of_data(grd)
    grid1 = meteva.base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,member_list=["mean"])
    dat = np.squeeze(grd.values)
    dat = np.mean(dat,axis = 0)
    grd1 = meteva.base.basicdata.grid_data(grid1,dat)
    return grd1

#获取网格数据的方差
def var_of_grd(grd,used_coords = ["member"]):
    grid0 = meteva.base.basicdata.get_grid_of_data(grd)
    grid1 = meteva.base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,member_list=["var"])
    dat = np.squeeze(grd.values)
    dat = np.var(dat,axis = 0)
    grd1 = meteva.base.basicdata.grid_data(grid1,dat)
    return grd1

#获取网格数据的标准差
def std_of_grd(grd,used_coords = ["member"]):
    grid0 = meteva.base.basicdata.get_grid_of_data(grd)
    grid1 = meteva.base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,member_list=["std"])
    dat = np.squeeze(grd.values)
    dat = np.std(dat,axis = 0)
    grd1 = meteva.base.basicdata.grid_data(grid1,dat)
    return grd1

#获取网格数据的最小值
def min_of_grd(grd,used_coords = ["member"]):
    grid0 = meteva.base.basicdata.get_grid_of_data(grd)
    grid1 = meteva.base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,member_list=["min"])
    dat = np.squeeze(grd.values)
    dat = np.min(dat,axis = 0)
    grd1 = meteva.base.basicdata.grid_data(grid1,dat)
    return grd1

#获取网格数据的最大值
def max_of_grd(grd,used_coords = ["member"]):
    grid0 = meteva.base.basicdata.get_grid_of_data(grd)
    grid1 = meteva.base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,member_list=["max"])
    dat = np.squeeze(grd.values)
    dat = np.max(dat,axis = 0)
    grd1 = meteva.base.basicdata.grid_data(grid1,dat)
    return grd1

#获取网格数据的求和
def sum_of_grd(grd,used_coords = ["member"]):
    grid0 = meteva.base.basicdata.get_grid_of_data(grd)
    grid1 = meteva.base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,member_list=["max"])
    dat = np.squeeze(grd.values)
    dat = np.sum(dat,axis = 0)
    grd1 = meteva.base.basicdata.grid_data(grid1,dat)
    return grd1
