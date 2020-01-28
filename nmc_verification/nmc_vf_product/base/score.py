import nmc_verification
from nmc_verification.nmc_vf_method import *
import pandas as pd
import numpy as np
import datetime

class group_name:
    level: "level"
    time : "time"
    year : "year"
    month: "month"
    day:"day"
    hour :"hour"
    dtime:"dtime"
    dday:"dday"
    dhour:"dhour"
    id:"id"

def score(sta_ob_and_fos,method_name,group_by = None,group_list_list = None):
    data_name = nmc_verification.nmc_vf_base.get_stadata_names(sta_ob_and_fos)
    fo_num = len(data_name) -1
    group_list_list1 = None
    if group_by is None:
        ob = sta_ob_and_fos[data_name[0]].values
        result = np.zeros(fo_num)
        for i in range(fo_num):
            fo = sta_ob_and_fos[data_name[i+1]].values
            result[i] = globals().get(method_name)(ob,fo)
    else:
        sta_ob_and_fos_list = []
        if group_by == "level":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                level_list = copy.deepcopy(sta_ob_and_fos['level'].values)
                level_list = list(set(level_list))
                level_list.sort()
                group_list_list1 = []
                for level in level_list:
                    group_list_list1.append([level])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_level_list(sta_ob_and_fos,group_list)
                sta_ob_and_fos_list.append(sta)
        elif group_by == "time":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                time_list = copy.deepcopy(sta_ob_and_fos['time'].values)
                time_list = list(set(time_list))
                time_list.sort()
                group_list_list1 = []
                for time in time_list:
                    group_list_list1.append([time])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_time_list(sta_ob_and_fos,group_list)
                sta_ob_and_fos_list.append(sta)

        elif group_by == "year":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                year_list = sta_ob_and_fos['time'].map(lambda x: x.year)
                year_list = list(set(year_list))
                year_list.sort()
                group_list_list1 = []
                for year in year_list:
                    group_list_list1.append([year])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_year_list(sta_ob_and_fos,group_list)
                sta_ob_and_fos_list.append(sta)

        elif group_by == "month":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                month_list = sta_ob_and_fos['time'].map(lambda x: x.month)
                month_list = list(set(month_list))
                month_list.sort()
                group_list_list1 = []
                for month in month_list:
                    group_list_list1.append([month])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_month_list(sta_ob_and_fos,group_list)
                sta_ob_and_fos_list.append(sta)
        elif group_by == "day":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                day_list = sta_ob_and_fos['time'].map(lambda x: x.dayofyear)
                day_list = list(set(day_list))
                day_list.sort()
                group_list_list1 = []
                for month in day_list:
                    group_list_list1.append([month])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_day_list(sta_ob_and_fos,group_list)
                sta_ob_and_fos_list.append(sta)
        elif group_by == "hour":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                hour_list = sta_ob_and_fos['time'].map(lambda x: x.dayofyear)
                hour_list = list(set(hour_list))
                hour_list.sort()
                group_list_list1 = []
                for month in hour_list:
                    group_list_list1.append([month])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_day_list(sta_ob_and_fos,group_list)
                sta_ob_and_fos_list.append(sta)

        group_num = len(group_list_list1)
        result = np.zeros((fo_num,group_num))
        for i in range(group_num):
            sta = sta_ob_and_fos_list[i]
            if(len(sta.index) == 0):
                result[:,i] = nmc_verification.nmc_vf_base.IV
            else:
                ob = sta[data_name[0]].values
                for j in range(fo_num):
                    fo = sta[data_name[i+1]].values
                    result[j,i] = globals().get(method_name)(ob,fo)

    return result,data_name[1:],group_list_list1

df = pd.DataFrame({"level":[850,500],
                   "time":[datetime.datetime(2018,1,1,8,0),datetime.datetime(2019,12,31,20,0)],
                   "dtime":[12,36],
                   "id":[54511,54512],
                   "lon":[100,110],
                  "lat":[30,40],
                  "ob":[0,0],
                  "fo1":[1,1],
                  "fo2":[2,2]})
sta = nmc_verification.nmc_vf_base.sta_data(df)
veri = score(sta,"mse",group_by= "day")
print(veri)
