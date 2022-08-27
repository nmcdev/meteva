import meteva
import numpy as np
import pandas as pd
import xarray as xr
import datetime
import collections
import copy


# 实现任意纬度分类的函数
def score_df(df, method, s = None,g=None,gll_dict = None,plot = None,first = True,**kwargs):
    '''

    :param df:
    :param method:
    :param g:
    :return:
    '''
    method_name = method.__name__

    method_mid = meteva.perspact.get_middle_method(method)
    column_list = meteva.perspact.get_middle_columns(method_mid)
    score_method_with_mid = meteva.perspact.get_score_method_with_mid(method)
    df0 = meteva.base.sta_data(df)

    column_df = df.columns
    if not set(column_list) <= set(column_df):
        print("input pandas.DataFrame must contains columns in list of "+ str(column_list) + " for mem." + method_name + " caculation")
        return None,None

    if s is not None:
        if "member" in s.keys():
            df0  = df0.loc[df0['member'].isin(s["member"])]
            s.pop("member")
    df1 = meteva.base.sele_by_dict(df0, s)

    if method_name.find("ob_fo_") >= 0 and first:
        df_ob = copy.deepcopy(df1)
        df_ob["member"] = "OBS"
        if method_mid.__name__ == "hfmc":
            df_ob["H"] = df1["H"] + df1["M"]
            df_ob["F"] = 0
            df_ob["M"] = 0
            df_ob["C"] = df1["F"] + df1["C"]
        df_ob.drop_duplicates(subset=None, keep='first', inplace=True)
        df1 = pd.concat([df_ob,df1],axis=0)
        if g is None:
            g = ["member"]

        if "member" not in g:
            print("统计"+method_name+"时，参数g中必须包含“member")
            return

    if g is None:
        g = [g]
        gll_dict = None
        gll0 = None
    else:

        #将g转成列表形式
        if isinstance(g,str):
            g = [g]

        #gll_dict 初始化包含所有分类维度
        if gll_dict is None:
            gll_dict = {}
            for gg in range(len(g)):
                gll_dict[g[gg]] = None

        #对每个维度的分类方式进行赋值
        for gg in range(len(g)):
            if g[gg] not in gll_dict.keys() or  gll_dict[g[gg]] is None:
                if g[gg].find("time")>=0:
                    _,gll = meteva.base.group(df1,g = g[gg])
                else:
                    #为了保持原有排序，不用group函数
                    groups = df1[g[gg]]
                    groups = groups.drop_duplicates(keep="first")
                    gll = groups.values
                gll_dict[g[gg]] = gll

        # 将分组方式统一成单层列表，或者两层列表
        gll_dict1 = {}
        for gg in range(len(g)):
            list_list = gll_dict[g[gg]]
            has_list = False
            for list1 in list_list:
                if  isinstance(list1,list):
                    has_list = True
            if has_list:
                list_list1 = []
                for list1 in list_list:
                    if isinstance(list1, list):
                        list_list1.append(list1)
                    else:
                        list_list1.append([list1])
            else:
                list_list1 = list_list
            gll_dict1[g[gg]] = list_list1
        gll_dict = gll_dict1

        #取出第一个分类维度的分类方式备用
        gll0 = gll_dict[g[0]]

    g0 = g[0]
    df1_list, gll = meteva.base.group(df1, g=g0, gll=gll0)
    if len(g) == 1:
        score_list = []
        gll_i_dict ={}
        score1 = None
        for i in range(len(df1_list)):
            if method_mid == meteva.method.tmmsss:
                tmmsss_array = df1_list[i][column_list].values
                mid_array = tmmsss_array[0, :]
                for j in range(1, tmmsss_array.shape[0]):
                    mid_array = meteva.method.tmmsss_merge(mid_array, tmmsss_array[j, :])
            else:
                mid_list = []
                for column in column_list:
                    mid = np.sum(df1_list[i][column])
                    mid_list.append(mid)
                mid_array = np.array(mid_list)
            score1 = score_method_with_mid(mid_array)
            score_list.append(score1)
            if gll is None:
                gll_str = "None"
            else:
                gll_str = str(gll[i])
            gll_i_dict[gll_str] = i

        if gll0 is None:
            score_list_with_iv = score_list
        else:
            score_list_with_iv = []
            for j in range(len(gll0)):
                gll_str = str(gll0[j])
                if gll_str in gll_i_dict.keys():
                    score2 = score_list[gll_i_dict[gll_str]]
                else:
                    score2 = score1 * 0 + meteva.base.IV
                score_list_with_iv.append(score2)
        score_array = np.array(score_list_with_iv)

        if method_name.find("ob_fo_")>=0:
             score_array = score_array[...,1,0]

        if plot is not None:meteva.base.plot_tools.plot_bar(plot,score_array,name_list_dict=gll_dict,**kwargs)

        return  score_array,gll_dict
    else:
        if len(g) == 2:
            g_left = g[1]
        else:
            g_left = g[1:]

        gll_i_dict ={}
        score_all_list = []
        score_array = None
        for i in range(len(gll)):
            score_array,gll_dict_new = score_df(df1_list[i], method,g = g_left, gll_dict = gll_dict,plot = None,first = False)
            score_all_list.append(score_array)
            gll_str = str(gll[i])
            gll_i_dict[gll_str] = i
            # if "member" in gll_dict.keys():
            #     if "OBS" not in gll_dict["member"]:
            #         gll_dict["member"] = gll_dict_new["member"]  # 为ob_fo_ 函数增加OBS列

        score_list_with_iv = []
        for j in range(len(gll0)):
            gll_str = str(gll0[j])
            if gll_str in gll_i_dict.keys():
                score2 = score_all_list[gll_i_dict[gll_str]]
            else:
                score2 = score_array * 0 + meteva.base.IV
            score_list_with_iv.append(score2)
        score_all_array = np.array(score_list_with_iv)

        if plot is not None:meteva.base.plot_tools.plot_bar(plot,score_all_array,name_list_dict=gll_dict,**kwargs)

        return score_all_array,gll_dict

def sele_by_dict(ds0,s):
    if s is None:
        return ds0
    else:
        ob_keys =[]
        not_ob_keys = []
        for key in s.keys():
            if key.find("ob_")>=0:
                ob_keys.append(key)
            else:
                not_ob_keys.append(key)

        #收集非观测时间相关的时间选取参数
        s_not_ob = {}
        #收集和dtime维度相关的选取参数
        dtime_s = ds0.dtime.values
        for key in not_ob_keys:
            list0 = s[key]
            if not isinstance(list0, list):
                list0 = [list0]
            if key =="dtime":
                dtime_s = list(set(dtime_s) & set(list0))
                if len(dtime_s) ==0:
                    return None
                dtime_s.sort()
                not_ob_keys.remove(key)
            elif key =="dtime_range":
                list1 = []
                for value in dtime_s:
                    if value>=s[key][0] and value<= s[key][1]:
                        list1.append(value)
                if len(list1) == 0:
                    return None
                else:
                    list1.sort()
                    dtime_s = list1
                not_ob_keys.remove(key)


        #收集和time维度相关的选取参数
        time_s = ds0.time.values
        for key in not_ob_keys:
            list0 = s[key]
            if not isinstance(list0, list):
                list0 = [list0]
            if key =="time":
                values_s1 = []
                for value in list0:
                    values_s1.append(meteva.base.all_type_time_to_time64(value))
                fo_times = pd.Series(0, index=time_s)
                time_s = time_s[fo_times.index.isin(values_s1)]
                if len(time_s) == 0:
                    return None
                not_ob_keys.remove(key)
            elif key =="year":
                fo_times = pd.Series(0, index=time_s)
                time_s = time_s[fo_times.index.year.isin(list0)]
                if len(time_s) == 0:
                    return None
                not_ob_keys.remove(key)
            elif key =="month":
                fo_times = pd.Series(0, index=time_s)
                time_s = time_s[fo_times.index.month.isin(list0)]
                if len(time_s) == 0:
                    return None
                not_ob_keys.remove(key)
            elif key =="xun":
                fo_times = pd.Series(0, index=time_s)
                mons = fo_times.index.month.astype(np.int16)
                days = fo_times.index.day.astype(np.int16)
                xuns = np.ceil(days / 10).values.astype(np.int16)
                xuns[xuns > 3] = 3
                xuns += (mons - 1) * 3
                xuns = pd.Series(xuns)
                time_s = time_s[xuns.isin(list0)]
                if len(time_s) == 0:
                    return None
                not_ob_keys.remove(key)
            elif key =="hou":
                fo_times = pd.Series(0, index=time_s)
                mons = fo_times.index.month.astype(np.int16)
                days = fo_times.index.day.astype(np.int16)
                hous = np.ceil(days / 5).values.astype(np.int16)
                hous[hous > 6] = 6
                hous += (mons - 1) * 6
                hous = pd.Series(hous)
                time_s = time_s[hous.isin(list0)]
                if len(time_s) == 0:
                    return None
                not_ob_keys.remove(key)
            elif key =="day":
                days_list = []
                time0 = datetime.datetime(1900, 1, 1, 0, 0)
                seconds = 3600 * 24
                for day0 in list0:
                    day0 = meteva.base.tool.time_tools.all_type_time_to_datetime(day0)
                    day = int((day0 - time0).total_seconds() // seconds)
                    days_list.append(day)
                days = (time_s - meteva.base.all_type_time_to_time64(time0)) // np.timedelta64(1, "D")
                days = pd.Series(days)
                time_s = time_s[days.isin(days_list)]
                if len(time_s) == 0:
                    return None
                not_ob_keys.remove(key)
            elif key =="dayofyear":
                fo_times = pd.Series(0, index=time_s)
                time_s = time_s[fo_times.index.dayofyear.isin(list0)]
                if len(time_s) == 0:
                    return None
                not_ob_keys.remove(key)
            elif key =="hour":
                fo_times = pd.Series(0, index=time_s)
                time_s = time_s[fo_times.index.hour.isin(list0)]
                if len(time_s) == 0:
                    return None
                not_ob_keys.remove(key)
            elif key =="minute":
                fo_times = pd.Series(0, index=time_s)
                time_s = time_s[fo_times.index.minute.isin(list0)]
                if len(time_s) == 0:
                    return None
                not_ob_keys.remove(key)
            elif key =="time_range":
                start_time = meteva.base.all_type_time_to_time64(list0[0])
                end_time = meteva.base.all_type_time_to_time64(list0[1])
                list1 = []
                for value in time_s:
                    if value>=start_time and value<= end_time:
                        list1.append(value)
                if len(list1) == 0:
                    return None
                else:
                    dtime_s = np.array(list1)
                not_ob_keys.remove(key)

        #根据观测时间参和可用时效确定实际可用的起报时间
        time_exp = None
        dtime_exp = None
        if len(ob_keys)>0:
            time_exp,dtime_exp = np.meshgrid(time_s,dtime_s)
            time_exp = time_exp.flatten()
            dtime_exp = dtime_exp.flatten()
            dtime_exp_64 = dtime_exp * np.timedelta64(1, 'h')
            obtimes_exp = time_exp + dtime_exp_64
            for key in ob_keys:
                list0 = s[key]
                if not isinstance(list0, list):
                    list0 = [list0]
                if key =="ob_time":
                    values_s1 = []
                    for value in list0:
                        values_s1.append(meteva.base.all_type_time_to_time64(value))
                    ob_times = pd.Series(0, index=obtimes_exp)
                    index = ob_times.index.isin(values_s1)
                    time_exp = time_exp[index]
                    obtimes_exp = obtimes_exp[index]
                    dtime_exp = dtime_exp[index]
                    if len(obtimes_exp) == 0:
                        return None
                elif key =="ob_year":
                    fo_times = pd.Series(0, index=time_s)
                    time_s = time_s[fo_times.index.year.isin(list0)]
                    if len(dtime_s) == 0:
                        return None

                elif key =="ob_month":
                    fo_times = pd.Series(0, index=time_s)
                    time_s = time_s[fo_times.index.month.isin(list0)]
                    if len(time_s) == 0:
                        return None

                elif key =="ob_xun":
                    fo_times = pd.Series(0, index=time_s)
                    mons = fo_times.index.month.astype(np.int16)
                    days = fo_times.index.day.astype(np.int16)
                    xuns = np.ceil(days / 10).values.astype(np.int16)
                    xuns[xuns > 3] = 3
                    xuns += (mons - 1) * 3
                    xuns = pd.Series(xuns)
                    time_s = time_s[xuns.isin(list0)]
                    if len(time_s) == 0:
                        return None

                elif key =="ob_hou":
                    fo_times = pd.Series(0, index=time_s)
                    mons = fo_times.index.month.astype(np.int16)
                    days = fo_times.index.day.astype(np.int16)
                    hous = np.ceil(days / 5).values.astype(np.int16)
                    hous[hous > 6] = 6
                    hous += (mons - 1) * 6
                    hous = pd.Series(hous)
                    time_s = time_s[hous.isin(list0)]
                    if len(time_s) == 0:
                        return None
                elif key =="ob_day":
                    days_list = []
                    time0 = datetime.datetime(1900, 1, 1, 0, 0)
                    seconds = 3600 * 24
                    for day0 in list0:
                        day0 = meteva.base.tool.time_tools.all_type_time_to_datetime(day0)
                        day = int((day0 - time0).total_seconds() // seconds)
                        days_list.append(day)
                    days = (time_s - meteva.base.all_type_time_to_time64(time0)) // np.timedelta64(1, "D")
                    days = pd.Series(days)
                    time_s = time_s[days.isin(days_list)]
                    if len(time_s) == 0:
                        return None
                elif key =="ob_dayofyear":
                    fo_times = pd.Series(0, index=time_s)
                    time_s = time_s[fo_times.index.dayofyear.isin(list0)]
                    if len(time_s) == 0:
                        return None
                    not_ob_keys.remove(key)
                elif key =="ob_hour":
                    fo_times = pd.Series(0, index=time_s)
                    time_s = time_s[fo_times.index.hour.isin(list0)]
                    if len(time_s) == 0:
                        return None
                elif key =="ob_minute":
                    fo_times = pd.Series(0, index=time_s)
                    time_s = time_s[fo_times.index.minute.isin(list0)]
                    if len(time_s) == 0:
                        return None

                elif key =="ob_time_range":
                    start_time = meteva.base.all_type_time_to_time64(list0[0])
                    end_time = meteva.base.all_type_time_to_time64(list0[1])
                    list1 = []
                    for value in time_s:
                        if value>=start_time and value<= end_time:
                            list1.append(value)
                    if len(list1) == 0:
                        return None
                    else:
                        dtime_s = np.array(list1)

            time_s = list(set(time_exp))
            time_s.sort()
            dtime_s = list(set(dtime_exp))
            dtime_s.sort()
        s_not_ob["dtime"] = dtime_s
        s_not_ob["time"] = time_s

        #收集其它维度相关的参数
        for key in not_ob_keys:
            list0 = s[key]
            if not isinstance(list0, list):
                list0 = [list0]
            s_not_ob[key] =list0
        ds1 = ds0.sel(s_not_ob)

        #将和观测时间不对应的部分重置为nan
        if time_exp is not None:
            df = pd.DataFrame({"time":time_exp,"dtime":dtime_exp,"data0":1})
            df.sort_values(by=["time","dtime"],inplace=True)
            df_new = pd.DataFrame(df["data0"].values, index=[df["time"].values,df["dtime"].values],columns=["data0"])
            df_new.index.names = ["time","dtime"]
            s_xr =  df_new.to_xarray()
            ds2 = ds1.where(s_xr.data0==1)  # 通过s_xr中的nan将ds1中的相应维度重置为0。
        else:
            ds2 = ds1

        return ds2

def get_gll(ds0,g):

    if g in ds0.coords:
        return ds0[g].values
    elif g.find("ob_")>=0:
        time_s = ds0["time"].values
        dtime_s = ds0["dtime"].values

        time_exp, dtime_exp = np.meshgrid(time_s, dtime_s)
        time_exp = time_exp.flatten()
        dtime_exp = dtime_exp.flatten()
        dtime_exp_64 = dtime_exp * np.timedelta64(1, 'h')
        obtimes_exp = time_exp + dtime_exp_64
        obtime_s = list(set(obtimes_exp))
        obtime_s.sort()
        if g =="ob_time":
            return obtime_s
        elif g == "ob_year":
            obtimes = pd.Series(0, index=obtime_s)
            grouped_dict = dict(list(obtimes.groupby(obtimes.index.year)))
            keys = list(grouped_dict.keys())
            return keys
        elif g == "ob_month":
            obtimes = pd.Series(0, index=obtime_s)
            grouped_dict = dict(list(obtimes.groupby(obtimes.index.month)))
            keys = list(grouped_dict.keys())
            return keys
        elif g == "ob_dayofyear":
            obtimes = pd.Series(0, index=obtime_s)
            grouped_dict = dict(list(obtimes.groupby(obtimes.index.dayofyear)))
            keys = list(grouped_dict.keys())
            return keys
        elif g == "ob_day":
            obtimes = pd.Series(0, index=obtime_s)
            time0 = datetime.datetime(1900, 1, 1, 0, 0)
            indexs = (obtimes.index - time0) // np.timedelta64(1, "D")
            grouped_dict = dict(list(obtimes.groupby(indexs)))
            keys = list(grouped_dict.keys())
            gll = []
            for key in keys:
                gll.append([time0 + datetime.timedelta(days=key)])
            return gll
        elif g == "ob_hour":
            obtimes = pd.Series(0, index=obtime_s)
            grouped_dict = dict(list(obtimes.groupby(obtimes.index.hour)))
            keys = list(grouped_dict.keys())
            return keys
        elif g == "ob_minute":
            obtimes = pd.Series(0, index=obtime_s)
            grouped_dict = dict(list(obtimes.groupby(obtimes.index.minute)))
            keys = list(grouped_dict.keys())
            return keys
    else:
        time_s = ds0["time"].values

        if g == "year":
            times = pd.Series(0, index=time_s)
            grouped_dict = dict(list(times.groupby(times.index.year)))
            keys = list(grouped_dict.keys())
            return keys
        elif g == "month":
            times = pd.Series(0, index=time_s)
            grouped_dict = dict(list(times.groupby(times.index.month)))
            keys = list(grouped_dict.keys())
            return keys
        elif g == "dayofyear":
            times = pd.Series(0, index=time_s)
            grouped_dict = dict(list(times.groupby(times.index.dayofyear)))
            keys = list(grouped_dict.keys())
            return keys
        elif g == "day":
            times = pd.Series(0, index=time_s)
            time0 = datetime.datetime(1900, 1, 1, 0, 0)
            indexs = (times.index - time0) // np.timedelta64(1, "D")
            grouped_dict = dict(list(times.groupby(indexs)))
            keys = list(grouped_dict.keys())
            gll = []
            for key in keys:
                gll.append([time0 + datetime.timedelta(days=key)])
            return gll
        elif g == "hour":
            times = pd.Series(0, index=time_s)
            grouped_dict = dict(list(times.groupby(times.index.hour)))
            keys = list(grouped_dict.keys())
            return keys
        elif g == "minute":
            times = pd.Series(0, index=time_s)
            grouped_dict = dict(list(times.groupby(times.index.minute)))
            keys = list(grouped_dict.keys())
            return keys


def sele_ob_time(ds0,ob_time):

    ob_time = meteva.base.all_type_time_to_time64(ob_time)
    time_s = ds0.time.values
    dtime_s = ds0.dtime.values
    ds_merge = None
    for dtime in dtime_s:
        time1 = ob_time -dtime * np.timedelta64(1, 'h')
        if time1 in time_s:
            ds1 = ds0.sel({"time":time1,"dtime":dtime})
            ds1 = ds1.drop("time")
            ds1.coords["ob_time"] = ob_time
            ds1 = ds1.expand_dims("dtime")
            ds1 = ds1.expand_dims("ob_time")
            if ds_merge is None:
                ds_merge = ds1
            else:
                ds_merge = ds_merge.merge(ds1)
    return ds_merge


def group(ds0,g = None,gll = None):

    if g is None:
        return [ds0],None
    elif g =="ob_time":
        gll = get_gll(ds0,g)
        ds_list = []
        for i in range(len(gll)):
            ds1 = sele_ob_time(ds0, ob_time = gll[i])
            ds_list.append(ds1)
        return ds_list, gll
    else:

        if gll is not None:
            ds_list = []
            for i in range(len(gll)):
                ds1 = sele_by_dict(ds0, s={g: gll[i]})
                ds_list.append(ds1)
            return ds_list, gll
        else:
            if g in ds0.coords:
                groups = list(ds0.groupby(g))
                valid_gll = []
                ds_list = []
                for i in range(len(groups)):
                    valid_gll.append(groups[i][0])
                    ds_list.append(groups[i][1])

                return ds_list,valid_gll
            else:
                gll = get_gll(ds0,g)
                ds_list = []
                for i in range(len(gll)):
                    ds1 = sele_by_dict(ds0, s={g: gll[i]})
                    ds_list.append(ds1)
                return ds_list, gll


def score_ds(ds,method,s = None,g = None,gll_dict = None,plot = None,first = True,**kwargs):
    method_name = method.__name__
    if method_name.find("ob_fo_") >= 0 and first:
        df1 = meteva.perspact.tran_middle_ds_to_df(ds)
        return score_df(df1,method,s = s,g = g,gll_dict=gll_dict,plot=plot,first = first,**kwargs)

    method_mid = meteva.perspact.get_middle_method(method)
    value_list = meteva.perspact.get_middle_columns(method_mid)
    score_method_with_mid = meteva.perspact.get_score_method_with_mid(method)

    for value in value_list:
        if not value in ds:
            print("input xarray.DataSet must contains columns in list of " + str(
            value_list) + " for mem." + method_name + " caculation")
            return None, None


    ds1 = sele_by_dict(ds, s)

    if g is None:
        g = [g]
        gll_dict = None
        gll0 = None
    else:

        # 将g转成列表形式
        if isinstance(g, str):
            g = [g]

        #gll_dict 初始化包含所有分类维度
        if gll_dict is None:
            gll_dict = {}
            for gg in range(len(g)):
                gll_dict[g[gg]] = None

        # 对每个维度的分类方式进行赋值
        for gg in range(len(g)):
            if g[gg] not in gll_dict.keys() or gll_dict[g[gg]] is None:
                gll_dict[g[gg]] = get_gll(ds1,g[gg])

        # 将分组方式统一成单层列表，或者两层列表
        gll_dict1 = {}
        for gg in range(len(g)):
            list_list = gll_dict[g[gg]]
            has_list = False
            for list1 in list_list:
                if isinstance(list1, list):
                    has_list = True
            if has_list:
                list_list1 = []
                for list1 in list_list:
                    if isinstance(list1, list):
                        list_list1.append(list1)
                    else:
                        list_list1.append([list1])
            else:
                list_list1 = list_list
            gll_dict1[g[gg]] = list_list1
        gll_dict = gll_dict1
        # 取出第一个分类维度的分类方式备用
        gll0 = gll_dict[g[0]]

    g0 = g[0]
    ds1_list, gll = group(ds1, g=g0,gll = gll0)

    if len(g) == 1:
        score_list = []
        gll_i_dict = {}
        score1 = None
        for i in range(len(ds1_list)):
            if method_mid == meteva.method.tmmsss:

                mid_values_list = []
                for column in value_list:
                    mid_values = ds1_list[i][column].values.flatten()
                    mid_values_list.append(mid_values)

                mid_all = np.array(mid_values_list)
                tmmsss_array = mid_all.T
                mid_array = tmmsss_array[0, :]
                for j in range(1, tmmsss_array.shape[0]):
                    mid_array = meteva.method.tmmsss_merge(mid_array, tmmsss_array[j, :])
            else:
                mid_list = []
                for column in value_list:
                    mid = np.nansum(ds1_list[i][column])
                    mid_list.append(mid)
                mid_array = np.array(mid_list)
            score1 = score_method_with_mid(mid_array)
            score_list.append(score1)
            if gll is None:
                gll_str = "None"
            else:
                gll_str = str(gll[i])
            gll_i_dict[gll_str] = i

        if gll0 is None:
            score_list_with_iv = score_list
        else:
            score_list_with_iv = []
            for j in range(len(gll0)):
                gll_str = str(gll0[j])
                if gll_str in gll_i_dict.keys():
                    score2 = score_list[gll_i_dict[gll_str]]
                else:
                    score2 = score1 * 0 + meteva.base.IV
                score_list_with_iv.append(score2)

        score_array = np.array(score_list_with_iv)

        if plot is not None: meteva.base.plot_tools.plot_bar(plot, score_array, name_list_dict=gll_dict, **kwargs)
        return score_array, gll_dict
    else:
        if len(g) == 2:
            g_left = g[1]
        else:
            g_left = g[1:]

        gll_i_dict = {}
        score_all_list = []
        score_array = None
        for i in range(len(gll)):
            score_array, _ = score_ds(ds1_list[i], method, g=g_left, gll_dict=gll_dict, plot=None)
            score_all_list.append(score_array)
            gll_str = str(gll[i])
            gll_i_dict[gll_str] = i

        score_list_with_iv = []
        for j in range(len(gll0)):
            gll_str = str(gll0[j])
            if gll_str in gll_i_dict.keys():
                score2 = score_all_list[gll_i_dict[gll_str]]
            else:
                score2 = score_array * 0 + meteva.base.IV
            score_list_with_iv.append(score2)
        score_all_array = np.array(score_list_with_iv)
        score_all_array[np.isnan(score_all_array)] = meteva.base.IV
        if plot is not None: meteva.base.plot_tools.plot_bar(plot, score_all_array, name_list_dict=gll_dict, **kwargs)

        return score_all_array, gll_dict




def score_xy_df(df_mid,method,s = None,g = None,gll_dict = None,save_path = None,**kwargs):

    g_list = []
    if isinstance(g,list):
        if len(g)>1:
            print("score_xy_df函数暂时不支持多维分类功能")
            return
    else:
        if g is not None:
            g_list = [g]
    g_list.append("id")

    if s is not None:
        if "member" in s.keys():
            df_mid  = df_mid.loc[df_mid['member'].isin(s["member"])]
            s.pop("member")
    df_mid = meteva.base.sele_by_dict(df_mid, s)
    score_array,g_dict =score_df(df_mid,method,g = g_list,gll_dict = gll_dict)
    grd_list = []

    region_ids = g_dict["id"]
    max_id = np.max(region_ids)
    min_id = np.min(region_ids)

    max_ = max(max_id,abs(min_id))
    if max_ <1000000:
        lat = np.round(region_ids  / 1000)
        lon = region_ids - lat * 1000
    else:
        lat = np.round(region_ids / 10000)
        lon = region_ids - lat * 10000
        lon /=10
        lat /=10
    score_grd = None
    if len(g_list) == 1:
        dict1 = {"level":df_mid["level"].values[0],"time":df_mid["time"].values[0],"dtime":df_mid["dtime"].values[0],
            "id": region_ids, "lon": lon, "lat": lat,  "score": score_array}
        df = pd.DataFrame(dict1)
        score_sta = meteva.base.sta_data(df)
        score_grd = meteva.base.trans_sta_to_grd(score_sta)
        meteva.base.plot_tools.contourf_2d_grid(score_grd, save_path,**kwargs)
    elif len(g_list) == 2:
        gnames0 = g_dict[g_list[0]]
        ng0 = len(gnames0)
        for i in range(ng0):
            name = gnames0[i]
            value = score_array[i,:]
            if g_list[0] =="member":
                df = pd.DataFrame({"level":df_mid["level"].values[0],"time":df_mid["time"].values[0],"dtime":df_mid["dtime"].values[0],"id":region_ids,
                                   "lon": lon, "lat": lat, name: value})
            else:
                dict1 = {"id":region_ids,"lon":lon,"lat":lat,g_list[0]:name,"score":value}
                if "level" not in dict1:
                    dict1["level"] = df_mid["level"].values[0]
                if "time" not in dict1:
                    dict1["time"] = df_mid["time"].values[0]
                if "dtime" not in dict1:
                    dict1["dtime"] = df_mid["dtime"].values[0]
                df = pd.DataFrame(dict1)
            score_sta = meteva.base.sta_data(df)
            score_grd = meteva.base.trans_sta_to_grd(score_sta)
            grd_list.append(score_grd)
        score_grd = meteva.base.concat(grd_list)
        title = score_grd.coords[g_list[0]].values.tolist()
        kwargs["title"]  = title
        meteva.base.plot_tools.contourf_2d_grid(score_grd,save_path,subplot=g_list[0],**kwargs)
    return score_grd


if __name__ =="__main__":
    import pandas as pd
    #path = r"O:\data\hdf\gongbao\wind3h_update12h_station2k\wind3h_update12h_station2k.h5"
    path = r"H:/a.txt"
    uv = pd.read_hdf(path)
    uv = meteva.base.sele_by_para(uv,time_range = ["2022081408","2022081720"],dtime = [12,24,36,48])
    uv = meteva.base.in_member_list(uv,member_list=[0,1,2,3,4,5],name_or_index="index")
    #uv.to_hdf(r"H:\test_data\input\mps\wind.h5","df")

    speed,_ = meteva.base.wind_to_speed_angle(uv)
    df = meteva.perspact.middle_df_sta(speed,meteva.method.nasws_s)
    score = meteva.perspact.score_df(df,meteva.method.acs,g = "member")
    print(score)
    score = meteva.product.score(speed,meteva.method.acs)
    print(score)
    pass


