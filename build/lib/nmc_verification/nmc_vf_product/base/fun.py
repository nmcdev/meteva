import nmc_verification
import copy
import datetime
import math
import time
import pandas as pd
import numpy as np


def get_time_str_list(time_list):
    str1 = nmc_verification.nmc_vf_base.tool.time_tools.get_time_str_one_by_one(time_list[0])
    time_str_list = [str1]
    for i in range(1,len(time_list)):
        time_str_list.append(nmc_verification.nmc_vf_base.tool.time_tools.get_time_str_one_by_one(time_list[i],time_list[i-1]))
    return time_str_list

def get_save_path(save_dir,method,group_by,group_list,model_name,type,discription = None):

    if discription is None:
        discription = ""
    else:
        discription ="_"+discription
    if save_dir is None:
        save_path = None
    else:
        save_dir = save_dir.replace("\\", "/")
        if group_by is None:
            save_path = save_dir + "/"+method.__name__+"_" +model_name+discription+type
        else:
            save_path = save_dir + "/" +method.__name__+"_" + model_name + "_"+ group_by + str(group_list)+discription+type
    return save_path



def get_title(method,group_by,group_list,model_name,title = None,discription_uni = ""):

    if group_by is None:
        if(title is None):
            title1 = method.__defaults__[-1] + "(" + model_name  + ")" + discription_uni
        else:
            title1 = title+ "(" + model_name  + ")"
    else:
        group_name = group_by + "="
        g_num = len(group_list)
        if group_by in ["time","ob_time","day","ob_day"]:
            #判断是否等间距
            if g_num == 1:
                time_str = nmc_verification.nmc_vf_base.tool.time_tools.get_time_str_one_by_one(group_list[0])
                group_name += time_str
            elif g_num == 2:
                time_str1 = nmc_verification.nmc_vf_base.tool.time_tools.get_time_str_one_by_one(group_list[0])
                time_str2 = nmc_verification.nmc_vf_base.tool.time_tools.get_time_str_one_by_one(group_list[1],group_list[0])
                group_name += time_str1+"|"+time_str2
            elif g_num == 3:
                time_str1 = nmc_verification.nmc_vf_base.tool.time_tools.get_time_str_one_by_one(group_list[0])
                time_str2 = nmc_verification.nmc_vf_base.tool.time_tools.get_time_str_one_by_one(group_list[1],group_list[0])
                time_str3 = nmc_verification.nmc_vf_base.tool.time_tools.get_time_str_one_by_one(group_list[2], group_list[1])
                group_name += time_str1+"|"+time_str2 +"|"+time_str3
            else:
                #判断时间是否等间距
                time_str1 = nmc_verification.nmc_vf_base.tool.time_tools.get_time_str_one_by_one(group_list[0])
                time_str2 = nmc_verification.nmc_vf_base.tool.time_tools.get_time_str_one_by_one(group_list[-1],group_list[0])
                group_name += time_str1 + "至" + time_str2
        else:

            if g_num < 5:
                for i in range(g_num):
                    loc = group_list[i]
                    if type(loc) == str:
                        group_name += loc
                    else:
                        group_name += str(loc)

                    if i < len(group_list) - 1:
                        group_name += "|"
            else:
                loc = group_list[0]
                if type(loc) == str:
                    group_name += loc +"|"+ group_list[1]+"|...|"+group_list[-1]
                else:
                    group_name += str(loc)+"|"+ str(group_list[1])+"|...|"+str(group_list[-1])

        if title is not None:
            title1 = title + discription_uni
        else:
            title1 = method.__defaults__[-1] + "(" + model_name + ")" + discription_uni +"\n("+group_name+")"
    return title1


def get_unique_coods(sta):
    begin = time.time()
    nline = len(sta.index)
    #print(nline)
    discription = ""
    if sta["level"].values[0] == sta["level"].values[-1]:
        repete = len(sta["level"].drop_duplicates().index)
        if repete == 1:
            discription += "level=" + str(sta["level"].values[0]) +" "
    #print("level")
    #print(time.time() - begin)
    #判断空间的一致性
    not_unique = True
    if sta["id"].values[0] == sta["id"].values[-1]:
        repete = len(sta["time"].drop_duplicates().index)
        if repete == 1:
            discription += "id=" + str(sta["id"].values[0])+" "
            not_unique = False
    #print("id")
    #print(time.time() - begin)

    time0 = nmc_verification.nmc_vf_base.time_tools.all_type_time_to_datetime(sta["time"].values[0])
    time_1 =  nmc_verification.nmc_vf_base.time_tools.all_type_time_to_datetime(sta["time"].values[-1])

    #判断时间的一致性
    not_unique = True
    if time0 == time_1:
        repete = len(sta["time"].drop_duplicates().index)
        if repete == 1:
            print(sta["time"].values[0])
            discription += "time=" + nmc_verification.nmc_vf_base.tool.time_tools.get_time_str_one_by_one(sta["time"].values[0])+" "
            not_unique = False
    #print("time")
    #print(time.time() - begin)
    if not_unique:
        #判断是否是同一fo_hour
        if time0.hour == time_1.hour:

            times = pd.Series(0, sta["time"])
            if len(times.index.hour.drop_duplicates()) == 1:
                discription += "hour=" + str(times.index.hour[0])+" "
                not_unique = False

        #print("hour")
        #print(time.time() - begin)

        day_unique = False
        if not_unique:
            #判断是否是同一fo_dayofyear
            #dayofyears = sta['time'].map(lambda x: x.dayofyear)
            if time0.timetuple().tm_yday == time_1.timetuple().tm_yday:
                times = pd.Series(0, sta["time"])
                if len(times.index.dayofyear.drop_duplicates())==1:
                    discription += "dayofyear=" + str(times.index.dayofyear[0])+" "
                    day_unique = True

        #print("day")
        #print(time.time() - begin)
        #如果日期是一致的，就不用判断年月了
        month_unique = False
        if not day_unique:
            #判断是否是同一fo_month
            if time0.month == time_1.month:
                times =  pd.Series(0,sta["time"])
                if len(times.index.month.drop_duplicates())==1:
                    discription += "month=" + str(times.index.month[0])+" "
                    month_unique = True
        #print("month")
        #print(time.time() - begin)
        if not month_unique:
            #判断是否是同一fo_year
            if time0.year == time_1.year:
                times  = pd.Series(0,sta["time"])
                if len(times.index.year.drop_duplicates()) == 1:
                    discription += "year=" + str(times.index.year[0])+" "
    #print(time.time() - begin)
    if discription != "":
        discription = "\n("+discription[0:-1]+")"
    return discription


