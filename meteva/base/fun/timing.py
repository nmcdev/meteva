import pandas as pd
import copy
import meteva
import datetime
import math
import numpy as np


def rain_to_01process(rain01h_ob_fos,used_coords = "time"):
    '''
    降水过程必须被完整包含在时间（时效）序列内，否则起止时间会有偏差
    :param rain01h_ob_fos:
    :param used_coords:
    :return:
    '''

    if used_coords=="time":
        step = datetime.timedelta(hours=1)
    else:
        step = 1
    rain01h_ob_fos_hap = rain01h_ob_fos.copy()
    values = rain01h_ob_fos_hap.iloc[:,6:].values
    values[values<0.1] = 0
    values[values>0] = 1
    rain01h_ob_fos_hap.iloc[:,6:] = values[...]
    rain01h_ob_fos_hap_move01 = rain01h_ob_fos_hap.copy()
    rain01h_ob_fos_hap_move01[used_coords] -= step
    rain01h_ob_fos_hap.iloc[:,6:] += 10
    rain01h_ob_fos_hap = meteva.base.max_on_level_time_dtime_id(rain01h_ob_fos_hap,rain01h_ob_fos_hap_move01,how = "outer",default=0)
    rain01h_ob_fos_hap_move01[used_coords] += 2 * step
    rain01h_ob_fos_hap = meteva.base.max_on_level_time_dtime_id(rain01h_ob_fos_hap, rain01h_ob_fos_hap_move01,how = "outer",default=0)
    values2 = rain01h_ob_fos_hap.iloc[:, 6:].values
    values2[values2>=10] -=10
    rain01h_ob_fos_hap.iloc[:, 6:] =values2[...]
    rain02h_ob_fos_hap = meteva.base.sum_of_sta(rain01h_ob_fos_hap,used_coords=[used_coords],span = 2)
    values3 = rain02h_ob_fos_hap.iloc[:,6:].values
    values3[values3>0] = 1
    rain02h_ob_fos_hap.iloc[:,6:] = values3[...]
    rain02h_ob_fos_hap_back01 = rain02h_ob_fos_hap.copy()
    rain02h_ob_fos_hap_back01[used_coords] -= step
    rain02h_ob_fos_hap_sprate02 =meteva.base.min_on_level_time_dtime_id(rain02h_ob_fos_hap,rain02h_ob_fos_hap_back01,how = "outer",default=0)

    rain02h_ob_fos_hap_sprate02.sort_values(by = ["level","time","dtime","id"],inplace=True)
    return  rain02h_ob_fos_hap_sprate02

def rain_process_start(rain01h_ob_fos,used_coords = "time"):
    '''
    在时间维度，统计降水的开始时间
    :param rain01h_ob_fos:
    :return:
    '''
    rain02h_ob_fos_hap_sprate02 = rain_to_01process(rain01h_ob_fos,used_coords=used_coords)
    delta = meteva.base.change(rain02h_ob_fos_hap_sprate02,used_coords=used_coords,delta=1)
    # if used_coords =="time":
    #     delta[used_coords] -= datetime.timedelta(hours=1)
    # else:
    #     delta[used_coords] -= 1
    values = delta.iloc[:, 6:].values
    values[values <=0] = 0
    rain_start_01 = delta.copy()
    rain_start_01.iloc[:, 6:] = values[...]
    return rain_start_01


def rain_process_end(rain01h_ob_fos,used_coords = "time"):
    '''
    在时间维度，统计降水的开始时间
    :param rain01h_ob_fos:
    :return:
    '''
    rain02h_ob_fos_hap_sprate02 = rain_to_01process(rain01h_ob_fos,used_coords=used_coords)
    delta = meteva.base.change(rain02h_ob_fos_hap_sprate02,used_coords=used_coords,delta=1)
    if used_coords =="time":
        delta[used_coords] -= datetime.timedelta(hours=1)
    else:
        delta[used_coords] -= 1

    values = delta.iloc[:, 6:].values
    values[values >=0] = 0
    values *= -1
    rain_end_01 = delta.copy()
    rain_end_01.iloc[:, 6:] = values[...]
    return rain_end_01


def rain_process_lenght(rain01h_ob_fos,used_coords = "time",record_on = "end"):
    rain02h_ob_fos_hap_sprate02 = rain_to_01process(rain01h_ob_fos,used_coords=used_coords)
    rain02h_ob_fos_hap_sprate02_m = rain02h_ob_fos_hap_sprate02.copy()
    lenght = rain02h_ob_fos_hap_sprate02.copy()


    if record_on =="end":
        move_step = 1
    else:
        move_step  = -1

    if used_coords =="time":
        max_move = 72
        step =  datetime.timedelta(hours=move_step)
    else:
        dtime_list = list(set(rain02h_ob_fos_hap_sprate02["dtime"].values))
        dtime_max = np.max(np.array(dtime_list))
        max_move = min(dtime_max, 72)
        step = move_step

    for dh in range(max_move):
        rain02h_ob_fos_hap_sprate02_m[used_coords] += step
        rain02h_ob_fos_hap_sprate02_m = meteva.base.mutiply_on_level_time_dtime_id(rain02h_ob_fos_hap_sprate02_m,
                                                                                   rain02h_ob_fos_hap_sprate02)
        lenght = meteva.base.add_on_level_time_dtime_id(lenght, rain02h_ob_fos_hap_sprate02_m,how="left",default=0)
    delta = meteva.base.change(rain02h_ob_fos_hap_sprate02, used_coords=used_coords, delta=1)

    if record_on=="end":
        if used_coords == "time":
            delta[used_coords] -= datetime.timedelta(hours=1)
        else:
            delta[used_coords] -= 1

    values = -move_step *delta.iloc[:, 6:].values
    values[values <=0] = 0
    rain_end_01 = delta.copy()
    rain_end_01.iloc[:, 6:] = values[...]
    lenght = meteva.base.mutiply_on_level_time_dtime_id(lenght,rain_end_01,how="left",default=0)
    return lenght


def rain_process_peak(rain01h_ob_fos,used_coords = "time"):

    process01 = rain_to_01process(rain01h_ob_fos,used_coords=used_coords)
    rain01h_ob_fos_sprate02 = meteva.base.mutiply_on_level_time_dtime_id(rain01h_ob_fos,process01,how="right",default=0)
    values0 = rain01h_ob_fos_sprate02.iloc[:,6:].values
    if(len(values0.shape) ==2):
        rand = 0.001*np.random.rand(values0.shape[0],values0.shape[1])
    else:
        rand = 0.001 * np.random.rand(values0.shape[0])
    values0[values0>=0.1] += rand[values0>=0.1]  # 在原值上增加微量的随机增量，以避免一个过程中完全相同的两个峰值导致峰值时间的频次不合理。

    rain01h_ob_fos_sprate02.iloc[:,6:]  = values0[...]
    rain01h_ob_fos_move = rain01h_ob_fos_sprate02.copy()
    max_value = rain01h_ob_fos_sprate02.copy()
    if used_coords =="time":
        max_move = 72
        step =  datetime.timedelta(hours=1)
    else:
        dtime_list = list(set(process01["dtime"].values))
        dtime_max = np.max(np.array(dtime_list))
        max_move = min(dtime_max, 72)
        step = 1

    for dh in range(1,max_move):
        rain01h_ob_fos_move[used_coords] += step
        rain01h_ob_fos_move = meteva.base.mutiply_on_level_time_dtime_id(rain01h_ob_fos_move,
                                                                                   process01,how="right",default=0)
        max_value = meteva.base.max_on_level_time_dtime_id(max_value, rain01h_ob_fos_move)
        print("已完成"+ str(int(100*dh/(2*max_move+1)))+"%")

    rain01h_ob_fos_move = rain01h_ob_fos_sprate02.copy()
    for dh in range(1,max_move):
        rain01h_ob_fos_move[used_coords] -= step
        rain01h_ob_fos_move = meteva.base.mutiply_on_level_time_dtime_id(rain01h_ob_fos_move,
                                                                          process01,how="right",default=0)
        max_value = meteva.base.max_on_level_time_dtime_id(max_value, rain01h_ob_fos_move)
        print("已完成" + str(int(100*(dh+max_move) / (2 * max_move + 1)))+"%")
    values = rain01h_ob_fos_sprate02.iloc[:, 6:].values
    values[values==0] = -1
    rain01h_ob_fos_sprate02.iloc[:, 6:] = values[...]
    peak = meteva.base.minus_on_level_time_dtime_id(rain01h_ob_fos_sprate02,max_value,how="left",default=0)
    values2 = peak.iloc[:, 6:].values
    values2[values2<0] =-1
    values2 +=1
    peak.iloc[:, 6:] = values2[...]

    peak_time = rain01h_ob_fos.copy()
    peak_time.iloc[:,6:] = 0
    peak_time = meteva.base.max_on_level_time_dtime_id(peak_time,peak,how = "left",default=0)
    peak_value = meteva.base.mutiply_on_level_time_dtime_id(rain01h_ob_fos,peak_time)

    return peak_time,peak_value


def is_max_of_oneday(sta,used_coords = "time",start_hour_of_one_day = 0,keep_zeros = True):
    '''
    判断一个数据样本是否为一天中的最大值，是则记为1，否则记为0
    :param sta:
    :param used_coords:
    :param start_hour_of_one_day:
    :return:
    '''
    pass

    sta_max = meteva.base.max_of_sta(sta,used_coords=used_coords,span = 24)
    sta_max_last_time = meteva.base.sele_by_para(sta_max,ob_hour=start_hour_of_one_day)
    if len(sta_max_last_time.index) ==0:
        print("没有最大值观测时间和"+str(start_hour_of_one_day).zfill(2)+"时对应的数据样本")
    sta_max_list = [sta_max_last_time]
    for dh in range(1,24):
        sta_max_m = copy.deepcopy(sta_max_last_time)
        if used_coords =="time":
            sta_max_m["time"] -= datetime.timedelta(hours=dh)
        elif used_coords=="dtime":
            sta_max_m["dtime"] -= dh
        else:
            print("参数used_coords 只支持 time 和dtime两个选项")
            return
        sta_max_list.append(sta_max_m)
    sta_max_all = meteva.base.concat(sta_max_list)
    sta_minus = meteva.base.minus_on_level_time_dtime_id(sta,sta_max_all,how="inner")
    values = sta_minus.values[:,6:]
    values[values==0] = 1
    values[values<0] = 0
    sta_minus.iloc[:, 6:] =values[:,:]
    if not keep_zeros:
        sta0 = copy.deepcopy(sta)
        values = sta0.values[:, 6:]
        values[values != 0] = 1
        sta0.iloc[:,6:] = values
        sta_minus = meteva.base.mutiply_on_level_time_dtime_id(sta_minus,sta0,how="inner")

    return sta_minus



def is_min_of_oneday(sta,used_coords = "time",start_hour_of_one_day = 0):
    '''
    判断一个数据样本是否为一天中的最小值，是则记为1，否则记为0
    :param sta:
    :param used_coords:
    :param start_hour_of_one_day:
    :return:
    '''
    pass

    sta_min = meteva.base.min_of_sta(sta,used_coords=used_coords,span = 24)
    sta_min_last_time = meteva.base.sele_by_para(sta_min,ob_hour=start_hour_of_one_day)
    if len(sta_min_last_time.index) ==0:
        print("没有最大值观测时间和"+str(start_hour_of_one_day).zfill(2)+"时对应的数据样本")
        return
    sta_min_list = [sta_min_last_time]
    for dh in range(1,24):
        sta_min_m = copy.deepcopy(sta_min_last_time)
        if used_coords =="time":
            sta_min_m["time"] -= datetime.timedelta(hours=dh)
        elif used_coords=="dtime":
            sta_min_m["dtime"] -= dh
        else:
            print("参数used_coords 只支持 time 和dtime两个选项")
            return
        sta_min_list.append(sta_min_m)
    sta_min_all = meteva.base.concat(sta_min_list)
    sta_minus = meteva.base.minus_on_level_time_dtime_id(sta_min_all,sta,how="inner")
    values = sta_minus.values[:,6:]
    values[values==0] = 1
    values[values<0] = 0
    sta_minus.iloc[:, 6:] =values[:,:]


    return sta_minus