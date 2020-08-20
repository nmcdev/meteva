import math
import meteva
from meteva.base.tool.math_tools import lon_lat_to_cartesian
from scipy.spatial import cKDTree
import numpy as np
import copy
import pandas as pd
import datetime


def accumulate_time(sta_ob,step,keep_all = True):
    '''
    观测数据累加
    :param sta_ob:
    :param step:
    :param keep_all:
    :return:
    '''

    times= sta_ob.loc[:,'time'].values
    times = list(set(times))
    times.sort()
    times = np.array(times)
    dtimes = times[1:] - times[0:-1]
    min_dtime = np.min(dtimes)
    rain_ac = None
    for i in range(step):
        rain1 = sta_ob.copy()
        rain1["time"] = rain1["time"] + min_dtime * i
        rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac,rain1,how="inner")
    if not keep_all:
        dtimes = times[:] - times[-1]
        dh = (dtimes/min_dtime).astype(np.int32)
        new_times = times[dh%step ==0]
        rain_ac = meteva.base.in_time_list(rain_ac,new_times)
    print("warning: accumulate_time函数将在后续升级中不再支持，请重新使用sum_of_sta函数满足相关需求")
    return rain_ac

def accumulate_dtime(sta,step,keep_all = True):
    '''观测数据累加'''

    dtimes= sta.loc[:,'dtime'].values
    dtimes = list(set(dtimes))
    dtimes.sort()
    dtimes = np.array(dtimes)
    dhour_unit = dtimes[0]
    if dhour_unit ==0:
        dhour_unit = dtimes[1]
    rain_ac = None
    for i in range(step):
        rain1 = sta.copy()
        rain1["dtime"] = rain1["dtime"] + dhour_unit * i
        #print(dhour_unit * i)
        rain_ac = meteva.base.add_on_level_time_dtime_id(rain_ac,rain1,how="inner")
    if not keep_all:
        dh =((dtimes - dtimes[-1])/dhour_unit).astype(np.int32)
        new_dtimes = dtimes[dh%step ==0]
        rain_ac = meteva.base.in_dtime_list(rain_ac,new_dtimes)
    return rain_ac

def change(sta,delta = 24,used_coords = "time"):

    if used_coords == "time":
        names_0 = meteva.base.get_stadata_names(sta)
        names_1 = []
        for name in names_0:
            names_1.append(name + "_new")
        sta1 = sta.copy()
        meteva.base.set_stadata_names(sta1, names_1)
        sta1["time"] = sta1["time"] + datetime.timedelta(hours= delta)
        sta01 = meteva.base.combine_on_all_coords(sta1, sta)
        fn = len(names_1)
        dvalue = sta01.iloc[:, (-fn):].values - sta01.iloc[:, (-fn * 2):(-fn)].values
        sta01.iloc[:, (-fn):] = dvalue
        sta01 = sta01.drop(names_1, axis=1)
        return sta01
    else:
        names_0 = meteva.base.get_stadata_names(sta)
        names_1 = []
        for name in names_0:
            names_1.append(name+"_new")
        sta1 = sta.copy()
        meteva.base.set_stadata_names(sta1,names_1)
        sta1["dtime"] = sta1["dtime"] + delta
        sta01 = meteva.base.combine_on_all_coords(sta1,sta)
        fn= len(names_1)
        dvalue = sta01.iloc[:,(-fn):].values - sta01.iloc[:,(-fn * 2):(-fn)].values
        sta01.iloc[:,(-fn):] = dvalue
        sta01 = sta01.drop(names_1,axis=1)
        return sta01

def t_rh_to_tw(temp,rh,rh_unit = "%"):
    '''根据温度和相对湿度计算湿球温度'''
    if isinstance(temp,pd.DataFrame):
        sta1 = meteva.base.combine_on_all_coords(temp, rh)
        meteva.base.set_stadata_names(sta1, ["t", "rh"])
        sta2 = meteva.base.not_IV(sta1)
        T = sta2.loc[:,"t"].values
        RH = sta2["rh"].values
        if(T[0]>120):
            T -= 273.16

        if rh_unit == "%":
            pass
        else:
            RH = RH * 100
        max_rh = np.max(RH)
        min_rh = np.min(RH)
        if max_rh>100 or min_rh <0:
            print("相对湿度取值不能超过100%或小于0%")
            return
        if max_rh < 1:
            print("警告：最大的相对湿度小于1%，请确认rh的单位是否为%，如果不是,请设置rh_unit = 1")

        Tw = T * np.arctan(0.151977 * np.sqrt(RH + 8.313659)) + np.arctan(T + RH) - np.arctan(
            RH - 1.676331) + 0.00391838 * np.power(RH, 1.5) * np.arctan(0.023101 * RH) - 4.686035

        sta2["tw"] = Tw
        sta = sta2.drop(["t", "rh"], axis=1)
        return sta
    else:
        grid0 = meteva.base.get_grid_of_data(temp)
        if temp.values[0,0,0,0,0,0] >120:
            T = temp.values - 273.16
        else:
            T = temp.values

        RH = rh.values
        if rh_unit == "%":
            RH /= 100
        else:
            pass
        max_rh = np.max(RH)
        min_rh = np.min(RH)
        if max_rh>1 or min_rh <0:
            print("相对湿度取值不能超过100%或小于0%")
            return
        if max_rh < 0.01:
            print("警告：最大的相对湿度小于1%，请确认rh的单位是否为%，如果不是,请设置rh_unit = 1")

        Tw = T * np.arctan(0.151977 * np.sqrt(RH + 8.313659)) + np.arctan(T + RH) - np.arctan(
            RH - 1.676331) + 0.00391838 * np.power(RH, 1.5) * np.arctan(0.023101 * RH) - 4.686035

        grd = meteva.base.grid_data(grid0,Tw)
        return grd



def u_v_to_wind(u,v):
    if isinstance(u,pd.DataFrame):
        sta = meteva.base.combine_on_all_coords(u, v)
        meteva.base.set_stadata_names(sta, ["u", "v"])
        return  sta

    else:
        grid0 = meteva.base.get_grid_of_data(u)
        grid1 = meteva.base.grid(grid0.glon,grid0.glat,grid0.gtime,
                                                  dtime_list= grid0.dtimes,level_list=grid0.levels,member_list=["u","v"])
        wind = meteva.base.grid_data(grid1)
        wind.name = "wind"
        wind.values[0, :, :, :, :, :] = u.values[0, :, :, :, :, :]
        wind.values[1, :, :, :, :, :] = v.values[0, :, :, :, :, :]
        return wind

def speed_angle_to_wind(speed,angle = None):
    if isinstance(speed, pd.DataFrame):
        if angle is not None:
            sta = meteva.base.combine_on_all_coords(speed, angle)
        else:
            sta = speed.copy()
        meteva.base.set_stadata_names(sta, ["speed", "angle"])
        #speed = sta["speed"].values.astype(np.float32)
        #angle = sta["angle"].values.astype(np.float32)
        speed = sta["speed"].values.astype(np.float32)
        angle = sta["angle"].values.astype(np.float32)
        u = -speed * np.sin(angle  * 3.14 / 180)
        v = -speed * np.cos(angle * 3.14 / 180)
        sta["u"] = u
        sta["v"] = v
        sta = sta.drop(["speed", "angle"], axis=1)
        return sta



    else:
        speed_v = speed.values.squeeze()
        angle_v = angle.values.squeeze()

        grid0 = meteva.base.get_grid_of_data(speed)
        grid1 = meteva.base.grid(grid0.glon,grid0.glat,grid0.gtime,
                                                  dtime_list=grid0.dtimes,level_list=grid0.levels,member_list=["u","v"])
        wind = meteva.base.grid_data(grid1)
        wind.name = "wind"
        wind.values[0, :, :, :, :, :] = speed_v[:, :] * np.cos(angle_v[:, :] * math.pi /180)
        wind.values[1, :, :, :, :, :] = speed_v[:, :] * np.sin(angle_v[:, :] * math.pi /180)
        return wind

def t_dtp_to_rh(temp,dtp):
    if isinstance(temp,pd.DataFrame):
        sta = meteva.base.combine_on_all_coords(temp, dtp)
        meteva.base.set_stadata_names(sta, ["t", "dtp"])
        T = sta.loc[:,"t"].values
        if(T[0]>120):
            T -= 273.16

        D = sta["dtp"].values
        if D[0] >120:
            D -= 273.16
        e0 = 6.11 * np.exp(17.15 * T/(235 + T))
        e1 = 6.11 * np.exp(17.15 * D / (235 + D))

        rh = 100 * e1/e0
        sta["rh"] = rh
        sta = sta.drop(["t", "dtp"], axis=1)
        return sta
    else:
        grid0 = meteva.base.get_grid_of_data(temp)

        if temp.values[0,0,0,0,0,0] >120:
            T = temp.values - 273.16
        else:
            T = temp.values
        if dtp.values[0,0,0,0,0,0] >120:
            D = dtp.values - 273.16
        else:
            D = dtp.values

        e0 = 6.11 * np.exp(17.15 * T/(235 + T))
        e1 = 6.11 * np.exp(17.15 * D / (235 + D))

        rh = e0/e1
        grd = meteva.base.grid_data(grid0,rh)

        return grd

def t_rh_p_to_q(temp,rh,pressure,rh_unit = "%"):
    '''
    根据温度、相对湿度和气压计算比湿
    :param temp: 温度，可以是摄氏度，也可以是绝对温度
    :param rh:  相对湿度，可以是0-100，也可以是0-1
    :param level: 气压，单位百帕,可以是整数，站点数据或网格数据
    :return:
    '''
    if isinstance(temp,pd.DataFrame):
        if not isinstance(pressure,pd.DataFrame):
            level_s = temp.copy()
            level_s.iloc[:,-1] = pressure
        else:
            level_s = pressure
        sta1 = meteva.base.combine_on_all_coords(temp, rh)
        sta2 = meteva.base.combine_on_all_coords(sta1, level_s)
        meteva.base.set_stadata_names(sta2, ["t", "rh","p"])
        sta2 = meteva.base.not_IV(sta2)
        T = sta2.loc[:,"t"].values
        R = sta2.loc[:,"rh"].values
        P = sta2.loc[:,"p"].values
        if(T[0]>120):
            T -= 273.16
        e0 = 6.11 * np.exp(5420 * (1.0 / 273.15 - 1 / (T + 273.15))) * 622

        if rh_unit == "%":
            R /= 100
        else:
            pass

        max_rh = np.max(R)
        min_rh = np.min(R)
        if max_rh>1 or min_rh <0:
            print("相对湿度取值不能超过100%或小于0%")
            return
        if max_rh < 0.01:
            print("警告：最大的相对湿度小于1%，请确认rh的单位是否为%，如果不是,请设置rh_unit = 1")

        q = e0 * R/P
        sta2["q"] = q
        sta = sta2.drop(["t", "rh","p"], axis=1)
        return sta
    else:
        grid0 = meteva.base.get_grid_of_data(temp)
        if temp.values[0,0,0,0,0,0] >120:
            T = temp.values - 273.16
        else:
            T = temp.values


        R = rh.values
        if rh_unit == "%":
            R /= 100
        else:
            pass

        max_rh = np.max(R)
        min_rh = np.min(R)
        if max_rh>1 or min_rh <0:
            print("相对湿度取值不能超过100%或小于0%")
            return

        e0 = 6.11 * np.exp(5420 * (1.0 / 273.15 - 1 / (T + 273.15))) * 622

        if isinstance(pressure,float) or isinstance(pressure,float):
            P = pressure
        else:
            P = pressure.values
        q = e0 * R/P
        grd = meteva.base.grid_data(grid0,q)
        return grd



