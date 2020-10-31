import math
import meteva
from meteva.base.tool.math_tools import lon_lat_to_cartesian
from scipy.spatial import cKDTree
import numpy as np
import copy
import pandas as pd
import datetime


def mean_of_sta(sta,used_coords = ["member"],span = 24,equal_weight = False,keep_all = True):
    if not isinstance(used_coords,list):
        used_coords = [used_coords]

    sta1 = meteva.base.not_IV(sta)

    if used_coords == ["member"]:
        sta_mean = sta1.loc[:,meteva.base.get_coord_names()]
        sta_data = sta1[meteva.base.get_stadata_names(sta1)]
        value = sta_data.values
        mean = np.mean(value,axis=1)
        sta_mean['mean'] = mean
        return sta_mean
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

        step = int(round(span/min_dhour))

        sta1["count_for_add"] = 1

        if not equal_weight:
            names = meteva.base.get_stadata_names(sta1)
            rain_ac = sta1.copy()
            for name in names:
                rain_ac[name] *= 0.5

            for i in range(1,step):
                rain1 = sta1.copy()
                rain1["time"] = rain1["time"] + min_dtime * i
                rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac, rain1, how="outer",default=0)
            rain1 = sta1.copy()
            rain1["time"] = rain1["time"] + min_dtime * step
            for name in names:
                rain1[name] *= 0.5
            rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac, rain1, how="outer", default=0)

        else:
            rain_ac = None
            for i in range(step):
                rain1 = sta1.copy()
                rain1["time"] = rain1["time"] + min_dtime * i
                rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac, rain1, how="outer",default=0)

        names = meteva.base.get_stadata_names(rain_ac)
        for n in range(len(names)-1):
            rain_ac[names[n]] /= rain_ac[names[-1]]
        rain_ac = meteva.base.in_member_list(rain_ac,names[:-1])
        rain_ac = meteva.base.between_time_range(rain_ac, times[0], times[-1])  # 删除时效小于range的部分

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
        step = int(round(span/dhour_unit))

        if equal_weight:
            sta1["count_for_add"] = 1
            names = meteva.base.get_stadata_names(sta1)
            rain_ac = sta1.copy()
            for i in range(1,step):
                rain1 = sta1.copy()
                rain1["dtime"] = rain1["dtime"] + dhour_unit * i
                rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac, rain1,how="outer",default=0)
        else:
            pass
            dtimes_delta = (dtimes[1:] - dtimes[:-1])
            names = meteva.base.get_stadata_names(sta1)
            sta1["weight_pre"] =0
            sta1["weight_later"] = 0
            for i in range(len(dtimes)-1):
                sta1.loc[sta1["dtime"] == dtimes[i+1],"weight_pre"] = dtimes_delta[i]
                sta1.loc[sta1["dtime"] == dtimes[i], "weight_later"] = dtimes_delta[i]

            sta2 = sta1.iloc[:,:-2]
            sta2.loc[:,"count_for_add"] = sta1.loc[:,"weight_pre"]
            rain_ac = sta2.copy()


            for n in range(len(names)):
                rain_ac.loc[:,names[n]] *= sta2.loc[:,"count_for_add"]

            sta2.loc[:,"count_for_add"] = sta1.loc[:,"weight_pre"] + sta1.loc[:,"weight_later"]
            for i in range(1,step-1):
                rain1 = sta2.copy()
                for n in range(len(names)):
                    rain1.loc[:,names[n]] *= sta2.loc[:,"count_for_add"]
                rain1["dtime"] = rain1["dtime"] + dhour_unit * i
                rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac, rain1,how="outer",default=0)

            sta2.loc[:,"count_for_add"] = sta1.loc[:,"weight_later"]
            rain1 = sta2.copy()
            for n in range(len(names)):
                rain1.loc[:,names[n]] *= sta2.loc[:,"count_for_add"]
            rain1["dtime"] = rain1["dtime"] + dhour_unit * step
            rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac, rain1, how="outer", default=0)

        names = meteva.base.get_stadata_names(rain_ac)
        for n in range(len(names)-1):
            rain_ac[names[n]] /= rain_ac[names[-1]]

        rain_ac = meteva.base.in_member_list(rain_ac,names[:-1])
        rain_ac = meteva.base.in_dtime_list(rain_ac,dtimes[1:])  # 删除时效小于range的部分
        if not keep_all:
            dh = ((dtimes - dtimes[-1]) / dhour_unit).astype(np.int32)
            new_dtimes = dtimes[dh % step == 0]
            rain_ac = meteva.base.in_dtime_list(rain_ac, new_dtimes)
        return rain_ac


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

def max_of_sta(sta,used_coords = ["member"],span = None,keep_all = True):
    if not isinstance(used_coords,list):
        used_coords = [used_coords]
    if used_coords  == ["member"]:
        sta_max = sta.loc[:,meteva.base.get_coord_names()]
        sta_data = sta[meteva.base.get_stadata_names(sta)]
        value = sta_data.values
        max1 = np.max(value, axis=1)
        sta_max['max'] = max1
        return sta_max
    elif used_coords == ["time"]:
        if span is None:
            times = sta.loc[:, 'time'].values
            times = list(set(times))
            times.sort()
            rain_ac = meteva.base.in_time_list(sta,[times[0]])
            meteva.base.set_stadata_coords(rain_ac, time=times[-1])
            for i in range(1,len(times)):
                rain01 = meteva.base.in_time_list(sta,times[i])
                meteva.base.set_stadata_coords(rain01,time=times[-1])
                rain_ac = meteva.base.max_on_level_time_dtime_id(rain_ac, rain01, how="inner")
            return rain_ac
        else:
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
                rain_ac = meteva.base.max_on_level_time_dtime_id(rain_ac, rain1, how="inner")
            time0_add_span = times[0] + np.timedelta64(int(min_dhour * (step - 1)),'h')
            rain_ac = meteva.base.sele_by_para(rain_ac,time_range=[time0_add_span,times[-1]])
            if not keep_all:
                dtimes = times[:] - times[-1]
                dh = (dtimes / min_dtime).astype(np.int32)
                new_times = times[dh % step == 0]
                rain_ac = meteva.base.in_time_list(rain_ac, new_times)
            return rain_ac
    elif used_coords ==["dtime"]:
        if span is None:
            dtimes = sta.loc[:, 'dtime'].values
            dtimes = list(set(dtimes))
            dtimes.sort()
            rain_ac = meteva.base.in_dtime_list(sta, [dtimes[0]])
            meteva.base.set_stadata_coords(rain_ac, dtime=dtimes[-1])
            for i in range(1, len(dtimes)):
                rain01 = meteva.base.in_dtime_list(sta, dtimes[i])
                meteva.base.set_stadata_coords(rain01, dtime=dtimes[-1])
                rain_ac = meteva.base.max_on_level_time_dtime_id(rain_ac, rain01, how="inner")
            return rain_ac
        else:
            dtimes = sta.loc[:, 'dtime'].values
            dtimes = list(set(dtimes))
            dtimes.sort()
            dtimes = np.array(dtimes)
            dhour_unit = dtimes[1] - dtimes[0]

            #if dhour_unit == 0:
            #    dhour_unit = dtimes[1]

            rain_ac = sta.copy()
            #print(span)
            #print(dhour_unit)
            step = int(round(span/dhour_unit))
            #print(step)
            for i in range(1,step):
                rain1 = sta.copy()
                rain1["dtime"] = rain1["dtime"] + dhour_unit * i
                # print(dhour_unit * i)
                rain_ac = meteva.base.max_on_level_time_dtime_id(rain_ac, rain1, default=0)

            begin_dtime = dtimes[0]+dhour_unit * (step - 1)
            rain_ac = meteva.base.between_dtime_range(rain_ac,begin_dtime,dtimes[-1])  # 删除时效小于range的部分
            dtimes =np.array(list(set(rain_ac.loc[:, "dtime"].values.tolist())))
            if not keep_all:
                dh = ((dtimes - dtimes[-1]) / dhour_unit).astype(np.int32)
                new_dtimes = dtimes[dh % step == 0]
                rain_ac = meteva.base.in_dtime_list(rain_ac, new_dtimes)
            return rain_ac


def min_of_sta(sta,used_coords = ["member"],span = None,keep_all = True):
    if not isinstance(used_coords,list):
        used_coords = [used_coords]
    if used_coords  == ["member"]:
        sta_min = sta.loc[:,meteva.base.get_coord_names()]
        sta_data = sta[meteva.base.get_stadata_names(sta)]
        value = sta_data.values
        min1 = np.min(value, axis=1)
        sta_min['min'] = min1
        return sta_min
    elif used_coords == ["time"]:
        if span is None:
            times = sta.loc[:, 'time'].values
            times = list(set(times))
            times.sort()
            rain_ac = meteva.base.in_time_list(sta,[times[0]])
            meteva.base.set_stadata_coords(rain_ac, time=times[-1])
            for i in range(1,len(times)):
                rain01 = meteva.base.in_time_list(sta,times[i])
                meteva.base.set_stadata_coords(rain01,time=times[-1])
                rain_ac = meteva.base.min_on_level_time_dtime_id(rain_ac, rain01, how="inner")
            return rain_ac
        else:
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
                rain_ac = meteva.base.min_on_level_time_dtime_id(rain_ac, rain1, how="inner")
            time0_add_span = times[0] + np.timedelta64(int(min_dhour * (step - 1)),'h')
            rain_ac = meteva.base.sele_by_para(rain_ac,time_range=[time0_add_span,times[-1]])
            if not keep_all:
                dtimes = times[:] - times[-1]
                dh = (dtimes / min_dtime).astype(np.int32)
                new_times = times[dh % step == 0]
                rain_ac = meteva.base.in_time_list(rain_ac, new_times)
            return rain_ac
    elif used_coords ==["dtime"]:
        if span is None:
            dtimes = sta.loc[:, 'dtime'].values
            dtimes = list(set(dtimes))
            dtimes.sort()
            rain_ac = meteva.base.in_dtime_list(sta, [dtimes[0]])
            meteva.base.set_stadata_coords(rain_ac, dtime=dtimes[-1])
            for i in range(1, len(dtimes)):
                rain01 = meteva.base.in_dtime_list(sta, dtimes[i])
                meteva.base.set_stadata_coords(rain01, dtime=dtimes[-1])
                rain_ac = meteva.base.min_on_level_time_dtime_id(rain_ac, rain01, how="inner")
            return rain_ac
        else:
            dtimes = sta.loc[:, 'dtime'].values
            dtimes = list(set(dtimes))
            dtimes.sort()
            dtimes = np.array(dtimes)
            dhour_unit = dtimes[1] - dtimes[0]

            #if dhour_unit == 0:
            #    dhour_unit = dtimes[1]

            rain_ac = sta.copy()
            #print(span)
            #print(dhour_unit)
            step = int(round(span/dhour_unit))
            #print(step)
            for i in range(1,step):
                rain1 = sta.copy()
                rain1["dtime"] = rain1["dtime"] + dhour_unit * i
                # print(dhour_unit * i)
                rain_ac = meteva.base.min_on_level_time_dtime_id(rain_ac, rain1, default=0)

            begin_dtime = dtimes[0]+dhour_unit * (step - 1)
            rain_ac = meteva.base.between_dtime_range(rain_ac,begin_dtime,dtimes[-1])  # 删除时效小于range的部分
            dtimes =np.array(list(set(rain_ac.loc[:, "dtime"].values.tolist())))
            if not keep_all:
                dh = ((dtimes - dtimes[-1]) / dhour_unit).astype(np.int32)
                new_dtimes = dtimes[dh % step == 0]
                rain_ac = meteva.base.in_dtime_list(rain_ac, new_dtimes)
            return rain_ac




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
            times = sta.loc[:, 'time'].values
            times = list(set(times))
            times.sort()
            rain_ac = meteva.base.in_time_list(sta,[times[0]])
            meteva.base.set_stadata_coords(rain_ac, time=times[-1])
            for i in range(1,len(times)):
                rain01 = meteva.base.in_time_list(sta,times[i])
                meteva.base.set_stadata_coords(rain01,time=times[-1])
                rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac, rain01, how="inner")
            return rain_ac
        else:
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

            time0_add_span = times[0] + np.timedelta64(int(min_dhour * (step - 1)),'h')
            rain_ac = meteva.base.sele_by_para(rain_ac,time_range=[time0_add_span,times[-1]])
            if not keep_all:
                dtimes = times[:] - times[-1]
                dh = (dtimes / min_dtime).astype(np.int32)
                new_times = times[dh % step == 0]
                rain_ac = meteva.base.in_time_list(rain_ac, new_times)
            return rain_ac
    elif used_coords ==["dtime"]:
        if span is None:
            dtimes = sta.loc[:, 'dtime'].values
            dtimes = list(set(dtimes))
            dtimes.sort()
            rain_ac = meteva.base.in_dtime_list(sta, [dtimes[0]])
            meteva.base.set_stadata_coords(rain_ac, dtime=dtimes[-1])
            for i in range(1, len(dtimes)):
                rain01 = meteva.base.in_dtime_list(sta, dtimes[i])
                meteva.base.set_stadata_coords(rain01, dtime=dtimes[-1])
                rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac, rain01, how="inner")
            return rain_ac
        else:
            dtimes = sta.loc[:, 'dtime'].values
            dtimes = list(set(dtimes))
            dtimes.sort()
            dtimes = np.array(dtimes)
            dhour_unit = dtimes[1] - dtimes[0]

            #if dhour_unit == 0:
            #    dhour_unit = dtimes[1]

            rain_ac = sta.copy()
            #print(span)
            #print(dhour_unit)
            step = int(round(span/dhour_unit))
            #print(step)
            for i in range(1,step):
                rain1 = sta.copy()
                rain1["dtime"] = rain1["dtime"] + dhour_unit * i
                # print(dhour_unit * i)
                rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac, rain1, default=0)

            begin_dtime = dtimes[0]+dhour_unit * (step - 1)
            rain_ac = meteva.base.between_dtime_range(rain_ac,begin_dtime,dtimes[-1])  # 删除时效小于range的部分
            dtimes =set(rain_ac.loc[:, "dtime"].values.tolist())
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



def time_ceilling(sta,step = 1, time_unit = "h",begin_hour= 8):
    '''
    将不规则时间观测数据累计到固定步长的整点时刻
    :param sta: 站点数据，例如原始的闪电观测数据
    :param step:  累计的步长
    :param time_unit: 累计的时间单位，可选项包括 “H"和”M"，分别代表小时和分钟。
    :param begin_hour: 时间类型，当累计步长超过1小时,例如3小时，起步累计的时间是从08时还是00时，通常对北京时数据来说以08时起步，世界时则以00时起步
    :return:
    '''
    sta1 = sta.copy()
    time0 = datetime.datetime(2000,1,1,begin_hour,0)
    if time_unit.lower() == "h":
        step *= 3600
    else:
        step *= 60
    delta = ((sta["time"] - time0)/np.timedelta64(1,"s")).values
    delta =np.ceil(delta/step) * step
    sta1["time"] = time0
    sta1["time"] += delta * np.timedelta64(1, "s")
    return sta1


