import nmc_verification
import copy
import datetime
import math
import time
import pandas as pd


def group_data(sta_ob_and_fos,group_by,group_list_list = None):

    group_list_list1 = None
    valid_group_list_list = []
    sta_ob_and_fos_list = []
    if group_by is None:
        sta_ob_and_fos_list.append(sta_ob_and_fos)
    else:
        valid_group = ["level","time","year","month","day","dayofyear","hour",
                       "ob_time","ob_year","ob_month","ob_day","ob_dayofyear","ob_hour",
                       "dtime","dday","dhour","id"]
        if not group_by in valid_group:
            print("group_by 参数必须为如下列表中的选项：")
            print(str(valid_group))
            return None

        direct_group = ["level","time","dtime","dday","dhour","id"]

        if group_by in  direct_group:
            grouped_dict = dict(list(sta_ob_and_fos.groupby(group_by)))
            keys = grouped_dict.keys()
            if group_list_list is None:
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                key_set = set(keys)
                for group_list0 in group_list_list:
                    group_list1 = list(set(group_list0)^key_set)
                    if len(group_list1)>0:
                        valid_group_list_list.append(group_list1)
                        if len(group_list1) ==1:
                            sta_ob_and_fos_list.append(grouped_dict[group_list1[0]])
                        else:
                            sta_list = []
                            for key in group_list1:
                                sta_list.append(grouped_dict[key])
                            sta_con = pd.concat(sta_list)
                            sta_con.reset_index(drop=True)
                            sta_ob_and_fos_list.append(sta_con)

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
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
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
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
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
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "day":
            if group_list_list is not None:
                group_list_list1 = []
                for group_list in group_list_list:
                    group_list1 = []
                    for time0 in group_list:
                        time1 = datetime.datetime(time0.year,time0.month,time0.day,0,0)
                        group_list1.append(time1)
                    group_list_list1.append(group_list1)

            else:
                day_list = sta_ob_and_fos['time'].map(lambda x: datetime.datetime(x.year,x.month,x.day,0,0))
                day_list = list(set(day_list))
                day_list.sort()
                group_list_list1 = []
                for hour in day_list:
                    group_list_list1.append([hour])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_day_list(sta_ob_and_fos,group_list)
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "dayofyear":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                day_list = sta_ob_and_fos['time'].map(lambda x: x.dayofyear)
                day_list = list(set(day_list))
                day_list.sort()
                group_list_list1 = []
                for hour in day_list:
                    group_list_list1.append([hour])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_dayofyear_list(sta_ob_and_fos,group_list)
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "hour":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                hour_list = sta_ob_and_fos['time'].map(lambda x: x.hour)
                hour_list = list(set(hour_list))
                hour_list.sort()
                group_list_list1 = []
                for hour in hour_list:
                    group_list_list1.append([hour])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_hour_list(sta_ob_and_fos,group_list)
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)

        elif group_by == "ob_time":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                time_list = list(set(obtimes))
                time_list.sort()
                group_list_list1 = []
                for time in time_list:
                    group_list_list1.append([time])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obtimes.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)

        elif group_by == "ob_year":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            obyears = obtimes.map(lambda x: x.year)
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                year_list = list(set(obyears))
                year_list.sort()
                group_list_list1 = []
                for year in year_list:
                    group_list_list1.append([year])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obyears.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)

        elif group_by == "ob_month":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            obmonths = obtimes.map(lambda x: x.month)
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                month_list = list(set(obmonths))
                month_list.sort()
                group_list_list1 = []
                for month in month_list:
                    group_list_list1.append([month])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obmonths.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "ob_day":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            obdays = obtimes.map(lambda  x:datetime.datetime(x.year,x.month,x.day,0,0))
            if group_list_list is not None:
                group_list_list1 = []
                for group_list in group_list_list:
                    group_list1 = []
                    for time0 in group_list:
                        time1 = datetime.datetime(time0.year, time0.month, time0.day, 0, 0)
                        group_list1.append(time1)
                    group_list_list1.append(group_list1)
            else:
                day_list = list(set(obdays))
                day_list.sort()
                group_list_list1 = []
                for day in day_list:
                    group_list_list1.append([day])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obdays.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "ob_dayofyear":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            obdays = obtimes.map(lambda  x:x.dayofyear)
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                day_list = list(set(obdays))
                day_list.sort()
                group_list_list1 = []
                for day in day_list:
                    group_list_list1.append([day])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obdays.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "ob_hour":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            obhours = obtimes.map(lambda  x:x.hour)
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                hour_list = list(set(obhours))
                hour_list.sort()
                group_list_list1 = []
                for hour in hour_list:
                    group_list_list1.append([hour])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obhours.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)


        elif group_by == "dtime":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                dtime_list = copy.deepcopy(sta_ob_and_fos['dtime'].values)
                dtime_list = list(set(dtime_list))
                dtime_list.sort()
                group_list_list1 = []
                for dtime in dtime_list:
                    group_list_list1.append([dtime])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_dtime_list(sta_ob_and_fos,group_list)
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)

        elif group_by == "dday":
            ddays = sta_ob_and_fos['dtime'].map(lambda x: math.ceil(x/24))
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                dday_list = list(set(ddays))
                dday_list.sort()
                group_list_list1 = []
                for dday in dday_list:
                    group_list_list1.append([dday])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[ddays.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "dhour":
            dhours = sta_ob_and_fos['dtime'].map(lambda x: x%24)
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                dhour_list = list(set(dhours))
                dhour_list.sort()
                group_list_list1 = []
                for dhour in dhour_list:
                    group_list_list1.append([dhour])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[dhours.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "id":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                id_list = copy.deepcopy(sta_ob_and_fos['id'].values)
                id_list = list(set(id_list))
                id_list.sort()
                group_list_list1 = []
                for id in id_list:
                    group_list_list1.append([id])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_id_list(sta_ob_and_fos,group_list)
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
    #返回分组结果，和实际分组方式

    if len(valid_group_list_list)==0:
        valid_group_list_list = None
    return sta_ob_and_fos_list,valid_group_list_list


def group_data1(sta_ob_and_fos,group_by,group_list_list = None):

    group_list_list1 = None
    valid_group_list_list = []
    sta_ob_and_fos_list = []
    if group_by is None:
        sta_ob_and_fos_list.append(sta_ob_and_fos)
    else:
        valid_group = ["level","time","year","month","day","dayofyear","hour",
                       "ob_time","ob_year","ob_month","ob_day","ob_dayofyear","ob_hour",
                       "dtime","dday","dhour","id"]
        if not group_by in valid_group:
            print("group_by 参数必须为如下列表中的选项：")
            print(str(valid_group))
            return None
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
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
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
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
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
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
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
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "day":
            if group_list_list is not None:
                group_list_list1 = []
                for group_list in group_list_list:
                    group_list1 = []
                    for time0 in group_list:
                        time1 = datetime.datetime(time0.year,time0.month,time0.day,0,0)
                        group_list1.append(time1)
                    group_list_list1.append(group_list1)

            else:
                day_list = sta_ob_and_fos['time'].map(lambda x: datetime.datetime(x.year,x.month,x.day,0,0))
                day_list = list(set(day_list))
                day_list.sort()
                group_list_list1 = []
                for hour in day_list:
                    group_list_list1.append([hour])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_day_list(sta_ob_and_fos,group_list)
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "dayofyear":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                day_list = sta_ob_and_fos['time'].map(lambda x: x.dayofyear)
                day_list = list(set(day_list))
                day_list.sort()
                group_list_list1 = []
                for hour in day_list:
                    group_list_list1.append([hour])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_dayofyear_list(sta_ob_and_fos,group_list)
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "hour":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                hour_list = sta_ob_and_fos['time'].map(lambda x: x.hour)
                hour_list = list(set(hour_list))
                hour_list.sort()
                group_list_list1 = []
                for hour in hour_list:
                    group_list_list1.append([hour])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_hour_list(sta_ob_and_fos,group_list)
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)

        elif group_by == "ob_time":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                time_list = list(set(obtimes))
                time_list.sort()
                group_list_list1 = []
                for time in time_list:
                    group_list_list1.append([time])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obtimes.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)

        elif group_by == "ob_year":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            obyears = obtimes.map(lambda x: x.year)
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                year_list = list(set(obyears))
                year_list.sort()
                group_list_list1 = []
                for year in year_list:
                    group_list_list1.append([year])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obyears.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)

        elif group_by == "ob_month":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            obmonths = obtimes.map(lambda x: x.month)
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                month_list = list(set(obmonths))
                month_list.sort()
                group_list_list1 = []
                for month in month_list:
                    group_list_list1.append([month])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obmonths.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "ob_day":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            obdays = obtimes.map(lambda  x:datetime.datetime(x.year,x.month,x.day,0,0))
            if group_list_list is not None:
                group_list_list1 = []
                for group_list in group_list_list:
                    group_list1 = []
                    for time0 in group_list:
                        time1 = datetime.datetime(time0.year, time0.month, time0.day, 0, 0)
                        group_list1.append(time1)
                    group_list_list1.append(group_list1)
            else:
                day_list = list(set(obdays))
                day_list.sort()
                group_list_list1 = []
                for day in day_list:
                    group_list_list1.append([day])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obdays.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "ob_dayofyear":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            obdays = obtimes.map(lambda  x:x.dayofyear)
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                day_list = list(set(obdays))
                day_list.sort()
                group_list_list1 = []
                for day in day_list:
                    group_list_list1.append([day])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obdays.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "ob_hour":
            dtimes = sta_ob_and_fos['dtime'].map(lambda x: datetime.timedelta(hours=x))
            obtimes = sta_ob_and_fos['time'] + dtimes
            obhours = obtimes.map(lambda  x:x.hour)
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                hour_list = list(set(obhours))
                hour_list.sort()
                group_list_list1 = []
                for hour in hour_list:
                    group_list_list1.append([hour])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[obhours.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)


        elif group_by == "dtime":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                dtime_list = copy.deepcopy(sta_ob_and_fos['dtime'].values)
                dtime_list = list(set(dtime_list))
                dtime_list.sort()
                group_list_list1 = []
                for dtime in dtime_list:
                    group_list_list1.append([dtime])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_dtime_list(sta_ob_and_fos,group_list)
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)

        elif group_by == "dday":
            ddays = sta_ob_and_fos['dtime'].map(lambda x: math.ceil(x/24))
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                dday_list = list(set(ddays))
                dday_list.sort()
                group_list_list1 = []
                for dday in dday_list:
                    group_list_list1.append([dday])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[ddays.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "dhour":
            dhours = sta_ob_and_fos['dtime'].map(lambda x: x%24)
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                dhour_list = list(set(dhours))
                dhour_list.sort()
                group_list_list1 = []
                for dhour in dhour_list:
                    group_list_list1.append([dhour])
            for group_list in group_list_list1:
                sta = sta_ob_and_fos.loc[dhours.isin(group_list)]
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
        elif group_by == "id":
            if group_list_list is not None:
                group_list_list1 = group_list_list
            else:
                id_list = copy.deepcopy(sta_ob_and_fos['id'].values)
                id_list = list(set(id_list))
                id_list.sort()
                group_list_list1 = []
                for id in id_list:
                    group_list_list1.append([id])
            for group_list in group_list_list1:
                sta = nmc_verification.nmc_vf_base.in_id_list(sta_ob_and_fos,group_list)
                if len(sta.index) !=0:
                    valid_group_list_list.append(group_list)
                    sta_ob_and_fos_list.append(sta)
    #返回分组结果，和实际分组方式

    if len(valid_group_list_list)==0:
        valid_group_list_list = None
    return sta_ob_and_fos_list,valid_group_list_list


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


def get_time_str_one_by_one(time1,time0 = None):
    if time0 is None:
        time2 = nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_datetime(time1)
        if time2.hour == 0 and time2.minute == 0:
            time_str = time2.strftime("%Y年%m月%d日")
        elif time2.minute == 0:
            time_str = time2.strftime("%Y年%m月%d日%H时")
        else:
            time_str = time2.strftime("%Y年%m月%d日%H时%M分")
    else:
        time00 = nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_datetime(time0)
        time2 = nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_datetime(time1)
        if time2.year != time00.year:
            if time2.hour == 0 and time2.minute == 0:
                time_str = time1.strftime("%Y年%m月%d日")
            elif time1.minute == 0:
                time_str = time1.strftime("%Y年%m月%d日%H时")
            else:
                time_str = time1.strftime("%Y年%m月%d日%H时%M分")
        elif time2.month != time00.month:
            if time2.hour == 0 and time2.minute == 0:
                time_str = time2.strftime("%m月%d日")
            elif time2.minute == 0:
                time_str = time2.strftime("%m月%d日%H时")
            else:
                time_str = time2.strftime("%m月%d日%H时%M分")
        elif time2.day != time00.day:
            if time2.hour == 0 and time2.minute == 0:
                time_str = time2.strftime("%d日")
            elif time2.minute == 0:
                time_str = time2.strftime("%d日%H时")
            else:
                time_str = time2.strftime("%d日%H时%M分")
        elif time2.hour != time00.hour:
            if time2.minute == 0:
                time_str = time2.strftime("%H时")
            else:
                time_str = time2.strftime("%H时%M分")
        else:
            time_str = time2.strftime("%M分")
    return time_str

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
                time_str = get_time_str_one_by_one(group_list[0])
                group_name += time_str
            elif g_num == 2:
                time_str1 = get_time_str_one_by_one(group_list[0])
                time_str2 = get_time_str_one_by_one(group_list[1],group_list[0])
                group_name += time_str1+"|"+time_str2
            elif g_num == 3:
                time_str1 = get_time_str_one_by_one(group_list[0])
                time_str2 = get_time_str_one_by_one(group_list[1],group_list[0])
                time_str3 = get_time_str_one_by_one(group_list[2], group_list[1])
                group_name += time_str1+"|"+time_str2 +"|"+time_str3
            else:
                #判断时间是否等间距
                time_str1 = get_time_str_one_by_one(group_list[0])
                time_str2 = get_time_str_one_by_one(group_list[-1],group_list[0])
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
    #begin = time.time()
    nline = len(sta.index)
    #print(nline)
    discription = ""
    if sta["level"].values[0] == sta["level"].values[-1]:
        repete = sum(sta["level"].duplicated().values) + 1
        if repete == nline:
            discription += "level=" + str(sta["level"].values[0]) +" "

    #判断空间的一致性
    not_unique = True
    if sta["id"].values[0] == sta["id"].values[-1]:
        repete = sum(sta["id"].duplicated().values) + 1
        if repete == nline:
            discription += "id=" + str(sta["id"].values[0])+" "
            not_unique = False
    if not_unique:
        if sta["lon"].values[0] == sta["lon"].values[-1]:
            repete = sum(sta["lon"].duplicated().values) + 1
            if repete == nline:
                discription += "lon=" + str(sta["lon"].values[0])+" "
                not_unique = False
    if not_unique:
        if sta["lat"].values[0] == sta["lat"].values[-1]:
            repete = sum(sta["lat"].duplicated().values) + 1
            if repete == nline:
                discription += "lat=" + str(sta["lat"].values[0])+" "

    time0 = nmc_verification.nmc_vf_base.time_tools.all_type_time_to_datetime(sta["time"].values[0])
    time_1 =  nmc_verification.nmc_vf_base.time_tools.all_type_time_to_datetime(sta["time"].values[0])
    #判断时间的一致性
    not_unique = True
    if time0 == time_1:
        repete = sum(sta["time"].duplicated().values) + 1
        if repete == nline:
            discription += "time=" + get_time_str_one_by_one(sta["time"].values[0])+" "
            not_unique = False

    if not_unique:
        #判断是否是同一fo_hour
        if time0.hour == time_1.hour:
            hours = sta['time'].map(lambda x: x.hour)
            repete = sum(hours.duplicated().values) + 1
            if repete == nline:
                discription += "hour=" + str(hours.values[0])+" "
                not_unique = False

    day_unique = False
    if not_unique:
        #判断是否是同一fo_dayofyear
        dayofyears = sta['time'].map(lambda x: x.dayofyear)
        if dayofyears.values[0] == dayofyears.values[-1]:
            repete = sum(dayofyears.duplicated().values) + 1
            if repete == nline:
                discription += "dayofyear=" + str(dayofyears.values[0])+" "
                day_unique = True

    #如果日期是一致的，就不用判断年月了
    month_unique = False
    if not day_unique:
        #判断是否是同一fo_month
        if time0.month == time_1.month:
            months = sta['time'].map(lambda x: x.month)
            repete = sum(months.duplicated().values) + 1
            if repete == nline:
                discription += "month=" + str(months.values[0])+" "
                month_unique = True
    if not month_unique:
        #判断是否是同一fo_year
        if time0.year == time_1.year:
            years = sta['time'].map(lambda x: x.year)
            repete = sum(years.duplicated().values) + 1
            if repete == nline:
                discription += "year=" + str(years.values[0])+" "
    #print(time.time() - begin)
    if discription != "":
        discription = "\n("+discription[0:-1]+")"
    return discription

class group_by:
    level: "level"
    time : "time"
    year : "year"
    month: "month"
    day:"day"
    dayofyear:"dayofyear"
    hour :"hour"
    ob_time:"ob_time"
    ob_year:"ob_year"
    ob_month:"ob_month"
    ob_day:"ob_day"
    ob_dayofyear:"ob_dayofyear"
    ob_hour:"ob_hour"
    dtime:"dtime"
    dday:"dday"
    dhour:"dhour"
    id:"id"

