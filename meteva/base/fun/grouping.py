import meteva
import datetime
import pandas as pd
import numpy as np

def group(sta_ob_and_fos,group_by,group_list_list = None):
    valid_group_list_list = []
    sta_ob_and_fos_list = []
    if group_by is None:
        sta_ob_and_fos_list.append(sta_ob_and_fos)
    else:
        if group_list_list is not None:
            group_list_list0 = []
            for group_list in group_list_list:
                if isinstance(group_list,list):
                    group_list_list0.append(group_list)
                else:
                    group_list_list0.append([group_list])
            group_list_list = group_list_list0
        valid_group = ["level","time","year","month","day","dayofyear","hour",
                       "ob_time","ob_year","ob_month","ob_day","ob_dayofyear","ob_hour",
                       "dtime","dday","dhour","id"]
        if not group_by in valid_group:
            print("group_by 参数必须为如下列表中的选项：")
            print(str(valid_group))
            return None
        if group_by == "level":
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(group_by)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = meteva.base.in_level_list(sta_ob_and_fos,group_list)
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)
        elif group_by == "time":
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(group_by)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = meteva.base.in_time_list(sta_ob_and_fos,group_list)
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)

        elif group_by == "year":
            fo_times = pd.Series(0, index=sta_ob_and_fos['time'])
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(fo_times.index.year)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = sta_ob_and_fos.loc[fo_times.index.year.isin(group_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)

        elif group_by == "month":
            fo_times = pd.Series(0, index=sta_ob_and_fos['time'])
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(fo_times.index.month)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = sta_ob_and_fos.loc[fo_times.index.month.isin(group_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)
        elif group_by == "day":
            time0 = datetime.datetime(1900, 1, 1, 0, 0)
            seconds = 3600 * 24
            indexs = (sta_ob_and_fos['time'] - time0) // np.timedelta64(1, "D")
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(indexs)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([time0 + datetime.timedelta(days=key)])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    days_list = []
                    for day0 in group_list:
                        day = (day0 - time0).total_seconds() // seconds
                        days_list.append(day)
                    sta = sta_ob_and_fos.loc[indexs.isin(days_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)
        elif group_by == "dayofyear":
            fo_times = pd.Series(0, index=sta_ob_and_fos['time'])
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(fo_times.index.dayofyear)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = sta_ob_and_fos.loc[fo_times.index.dayofyear.isin(group_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)
        elif group_by == "hour":
            fo_times = pd.Series(0, index=sta_ob_and_fos['time'])
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(fo_times.index.hour)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = sta_ob_and_fos.loc[fo_times.index.hour.isin(group_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)

        elif group_by == "ob_time":
            dtimes = sta_ob_and_fos["dtime"] * np.timedelta64(1, 'h')
            obtimes = sta_ob_and_fos['time'] + dtimes
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(obtimes)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = sta_ob_and_fos.loc[obtimes.isin(group_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)

        elif group_by == "ob_year":
            dtimes = sta_ob_and_fos["dtime"] * np.timedelta64(1, 'h')
            obtimes = pd.Series(0, index=sta_ob_and_fos['time'] + dtimes)
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(obtimes.index.year)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = sta_ob_and_fos.loc[obtimes.index.year.isin(group_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)

        elif group_by == "ob_month":
            dtimes = sta_ob_and_fos["dtime"] * np.timedelta64(1, 'h')
            obtimes = pd.Series(0, index=sta_ob_and_fos['time'] + dtimes)
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(obtimes.index.month)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = sta_ob_and_fos.loc[obtimes.index.month.isin(group_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)
        elif group_by == "ob_day":
            dtimes = sta_ob_and_fos["dtime"] * np.timedelta64(1, 'h')
            obtimes = pd.Series(0, index=sta_ob_and_fos['time'] + dtimes)
            time0 = datetime.datetime(1900, 1, 1, 0, 0)
            seconds = 3600 * 24
            indexs = (obtimes.index - time0) // np.timedelta64(1, "D")

            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(indexs)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([time0 + datetime.timedelta(days=key)])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    days_list = []
                    for day0 in group_list:
                        day = (day0 - time0).total_seconds() // seconds
                        days_list.append(day)
                    sta = sta_ob_and_fos.loc[indexs.isin(days_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)
        elif group_by == "ob_dayofyear":
            dtimes = sta_ob_and_fos["dtime"] * np.timedelta64(1, 'h')
            obtimes = pd.Series(0, index=sta_ob_and_fos['time'] + dtimes)
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(obtimes.index.dayofyear)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = sta_ob_and_fos.loc[obtimes.index.dayofyear.isin(group_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)
        elif group_by == "ob_hour":
            dtimes = sta_ob_and_fos["dtime"] * np.timedelta64(1, 'h')
            obtimes = pd.Series(0, index=sta_ob_and_fos['time'] + dtimes)
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(obtimes.index.hour)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = sta_ob_and_fos.loc[obtimes.index.hour.isin(group_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)

        elif group_by == "dtime":
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(group_by)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = meteva.base.in_dtime_list(sta_ob_and_fos,group_list)
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)

        elif group_by == "dday":
            ddays = np.ceil(sta_ob_and_fos['dtime'] / 24)
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(ddays)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = sta_ob_and_fos.loc[ddays.isin(group_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)
        elif group_by == "dhour":
            dhours = sta_ob_and_fos['dtime'] % 24
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(dhours)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = sta_ob_and_fos.loc[dhours.isin(group_list)]
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)
        elif group_by == "id":
            if group_list_list is None:
                grouped_dict = dict(list(sta_ob_and_fos.groupby(group_by)))
                keys = grouped_dict.keys()
                for key in keys:
                    valid_group_list_list.append([key])
                    sta_ob_and_fos_list.append(grouped_dict[key])
            else:
                for group_list in group_list_list:
                    sta = meteva.base.in_id_list(sta_ob_and_fos,group_list)
                    if len(sta.index) !=0:
                        valid_group_list_list.append(group_list)
                        sta_ob_and_fos_list.append(sta)
    #返回分组结果，和实际分组方式
    if len(valid_group_list_list)==0:
        valid_group_list_list = None
    valid_group_list =  np.array(valid_group_list_list).squeeze().tolist()
    return sta_ob_and_fos_list,valid_group_list
