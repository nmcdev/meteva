import pandas as pd
import numpy as np
import copy
import meteva
import datetime
import time
import math

# 两个站点信息合并为一个，在原有的dataframe的基础上增加行数
def combine_join(sta, sta1):
    if (sta is None):
        return sta1
    elif (sta1 is None):
        return sta
    else:
        data_name1 = meteva.base.basicdata.get_stadata_names(sta)
        data_name2 = meteva.base.basicdata.get_stadata_names(sta1)
        if data_name1 == data_name2:
            sta = pd.concat([sta, sta1])
        else:
            sta2 = copy.deepcopy(sta1)
            meteva.base.basicdata.set_stadata_names(sta2,data_name1)
            sta = pd.concat([sta, sta2])
    sta = sta.reset_index(drop=True)
    return sta

# 两个站点信息合并为一个，以站号为公共部分，在原有的dataframe的基础上增加列数
def combine_on_id(sta, sta1):
    if sta is None:
        return sta1
    elif sta1 is None:
        return sta
    else:
        df = pd.merge(sta, sta1, on='id', how='inner')
        columns = list(sta.columns)
        len_sta = len(columns)
        # 删除合并后第二组时空坐标信息
        drop_col = list(df.columns[len_sta:len_sta + 5])
        df.drop(drop_col, axis=1, inplace=True)
        columns_dim = list(sta.columns)[0:6]
        columns_data = list(df.columns)[6:]
        columns = columns_dim + columns_data
        df.columns = columns
        return df

def that_the_name_exists(list, value):
    '''
    that_the_name_exists判断value是否在list中  如果存在改value直到不在list中为止
    :param list: 一个要素名列表
    :param value:  要素名
    :return:
    '''
    value = str(value)
    list = [str(i) for i in list]
    if value in list:
        value = str(value) + 'x'
        return that_the_name_exists(list, value)
    else:
        return value

#  两个站点信息合并为一个，以站号为公共部分，在原有的dataframe的基础上增加列数
def combine_on_all_coords(sta, sta1,how = "inner"):
    '''
    merge_on_all_dim 合并两个sta_dataframe并且使要素名不重复
    :param sta: 一个站点dataframe
    :param sta1: 一个站点dataframe
    :return:
    '''
    if (sta is None):
        return sta1
    elif sta1 is None:
        return sta
    else:
        columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat']
        sta_value_columns = sta.iloc[:, 6:].columns.values.tolist()
        sta1_value_columns = sta1.iloc[:, 6:].columns.values.tolist()
        if len(sta_value_columns) >= len(sta1_value_columns):

            for sta1_value_column in sta1_value_columns:
                ago_name = copy.deepcopy(sta1_value_column)
                sta1_value_column = that_the_name_exists(sta_value_columns, sta1_value_column)
                sta1.rename(columns={ago_name: sta1_value_column},inplace=True)
        else:
            for sta_value_column in sta_value_columns:
                ago_name = copy.deepcopy(sta_value_column)
                sta_value_column = that_the_name_exists(sta1_value_columns, sta_value_column)
                sta.rename(columns={ago_name: sta_value_column})
        df = pd.merge(sta, sta1, on=columns, how=how)
        return df

def combine_on_leve_time_id(sta,sta1):
    '''
    merge_on_all_dim 合并两个sta_dataframe并且使要素名不重复
    :param sta: 一个站点dataframe
    :param sta1: 一个站点dataframe
    :return:
    '''
    if (sta is None):
        return sta1
    elif sta1 is None:
        return sta
    else:
        columns = ['level', 'time',  'id']
        sta_value_columns = sta.iloc[:, 6:].columns.values.tolist()
        sta2 = copy.deepcopy(sta1)
        sta2_value_columns = sta2.iloc[:, 6:].columns.values.tolist()

        if len(sta_value_columns) >= len(sta2_value_columns):
            for sta2_value_column in sta2_value_columns:
                ago_name = copy.deepcopy(sta2_value_column)
                sta2_value_column = that_the_name_exists(sta_value_columns, sta2_value_column)
                sta2.rename(columns={ago_name: sta2_value_column},inplace=True)
        else:
            for sta_value_column in sta_value_columns:
                ago_name = copy.deepcopy(sta_value_column)
                sta_value_column = that_the_name_exists(sta2_value_columns, sta_value_column)
                sta.rename(columns={ago_name: sta_value_column})
        sta2.drop(['dtime',"lon","lat"], axis=1, inplace=True)
        df = pd.merge(sta, sta2, on=columns, how='inner')
        return df

def combine_on_level_time_dtime_id(sta, sta1,how = 'inner'):
    '''
    merge_on_all_dim 合并两个sta_dataframe并且使要素名不重复
    :param sta: 一个站点dataframe
    :param sta1: 一个站点dataframe
    :return:
    '''
    if (sta is None):
        return sta1
    elif sta1 is None:
        return sta
    else:
        columns = ['level', 'time', 'dtime', 'id']
        sta_value_columns = sta.iloc[:, 6:].columns.values.tolist()
        sta2 = copy.deepcopy(sta1)
        sta2_value_columns = sta2.iloc[:, 6:].columns.values.tolist()

        if len(sta_value_columns) >= len(sta2_value_columns):
            for sta2_value_column in sta2_value_columns:
                ago_name = copy.deepcopy(sta2_value_column)
                sta2_value_column = that_the_name_exists(sta_value_columns, sta2_value_column)
                sta2.rename(columns={ago_name: sta2_value_column},inplace=True)
        else:
            for sta_value_column in sta_value_columns:
                ago_name = copy.deepcopy(sta_value_column)
                sta_value_column = that_the_name_exists(sta2_value_columns, sta_value_column)
                sta.rename(columns={ago_name: sta_value_column})
        if(how == "inner"):
            sta2.drop(["lon","lat"], axis=1, inplace=True)
            df = pd.merge(sta, sta2, on=columns, how=how)
        else:
            sta3 = sta.copy()
            sta3.drop(["lon","lat"], axis=1, inplace=True)
            df = pd.merge(sta3, sta2, on=columns, how=how)
            if(len(df.index) == 0):
                print("no matched line")
                return None
            df = meteva.base.sta_data(df)
        return df



def combine_on_level_time_dtime(sta, sta1,how = 'inner'):
    '''
    merge_on_all_dim 合并两个sta_dataframe并且使要素名不重复
    :param sta: 一个站点dataframe
    :param sta1: 一个站点dataframe
    :return:
    '''
    if (sta is None):
        return sta1
    elif sta1 is None:
        return sta
    else:
        columns = ['level', 'time', 'dtime']
        sta_value_columns = sta.iloc[:, 6:].columns.values.tolist()
        sta2 = copy.deepcopy(sta1)
        sta2_value_columns = sta2.iloc[:, 6:].columns.values.tolist()

        if len(sta_value_columns) >= len(sta2_value_columns):
            for sta2_value_column in sta2_value_columns:
                ago_name = copy.deepcopy(sta2_value_column)
                sta2_value_column = that_the_name_exists(sta_value_columns, sta2_value_column)
                sta2.rename(columns={ago_name: sta2_value_column},inplace=True)
        else:
            for sta_value_column in sta_value_columns:
                ago_name = copy.deepcopy(sta_value_column)
                sta_value_column = that_the_name_exists(sta2_value_columns, sta_value_column)
                sta.rename(columns={ago_name: sta_value_column})
        if(how == "inner"):
            sta2.drop(["id","lon","lat"], axis=1, inplace=True)
            df = pd.merge(sta, sta2, on=columns, how=how)
        else:
            sta3 = sta.copy()
            sta3.drop(["id","lon","lat"], axis=1, inplace=True)
            df = pd.merge(sta3, sta2, on=columns, how=how)
            if(len(df.index) == 0):
                print("no matched line")
                return None
            df = meteva.base.sta_data(df)
        return df


def combine_on_obTime_id(sta_ob,sta_fo_list,need_match_ob = False):
    '''
    将观测
    :param sta_ob:
    :param sta_fo_list:
    :return:
    '''
    if not isinstance(sta_fo_list, list):
        sta_fo_list = [sta_fo_list]
    dtime_list = list(set(sta_fo_list[0]['dtime'].values.tolist()))
    nsta_ob = len(sta_ob.index)
    if(nsta_ob * len(dtime_list) >= 10000000):
        if nsta_ob >= 10000000:
            print("请注意，在大规模数据匹配合并时，need_match_ob 参数将自动切换为True")
            return combine_on_obTime_id_bigData(sta_ob,sta_fo_list)
        else:
            return combine_on_obTime_id_bigData(sta_ob, sta_fo_list,need_match_ob=need_match_ob,g = "dtime")
    else:
        if sta_ob is None:
            sta_combine = None
        else:
            #print(dtime_list)
            sta_combine = []
            for dtime in dtime_list:
                sta = copy.deepcopy(sta_ob)
                sta["time"] = sta["time"] - datetime.timedelta(hours= dtime)
                sta["dtime"] = dtime
                sta_combine.append(sta)
            sta_combine = pd.concat(sta_combine, axis=0)

        sta_combine_fo = None
        for sta_fo in sta_fo_list:
            sta_combine_fo = combine_on_level_time_dtime_id(sta_combine_fo, sta_fo)

        if need_match_ob:
            sta_combine = meteva.base.not_IV(sta_combine)
            sta_combine = combine_on_level_time_dtime_id(sta_combine, sta_combine_fo, how="inner")
        else:
            sta_combine = combine_on_level_time_dtime_id(sta_combine,sta_combine_fo,how="right")
            if sta_combine is not None:
                sta_combine = sta_combine.fillna(meteva.base.IV)

        return sta_combine



def combine_on_obTime_one_id(sta_ob,sta_fo_list,how = "inner"):
    '''
    将观测
    :param sta_ob:
    :param sta_fo_list:
    :return:
    '''
    if not isinstance(sta_fo_list, list):
        sta_fo_list = [sta_fo_list]


    if sta_ob is None:
        sta_combine = None
    else:
        dtime_list = list(set(sta_fo_list[0]['dtime'].values.tolist()))
        #print(dtime_list)
        sta_combine = []
        for dtime in dtime_list:
            sta = copy.deepcopy(sta_ob)
            sta["time"] = sta["time"] - datetime.timedelta(hours= dtime)
            sta["dtime"] = dtime
            sta_combine.append(sta)
        sta_combine = pd.concat(sta_combine, axis=0)

    sta_combine_fo = None
    for sta_fo in sta_fo_list:
        sta_combine_fo = combine_on_level_time_dtime(sta_combine_fo, sta_fo,how= how)

    sta_combine = combine_on_level_time_dtime(sta_combine, sta_combine_fo)


    return sta_combine



def combine_on_obTime_id_bigData(sta_ob,sta_fo_list,need_match_ob = True,g = "id"):
    import sys,gc
    '''
    将观测
    :param sta_ob:
    :param sta_fo_list:
    :return:
    '''
    if not isinstance(sta_fo_list, list):
        print("the second args shold be a list")
        return
    sta_all = None
    if g =="id":
        grouped_ob = dict(list(sta_ob.groupby("id")))
        nfo = len(sta_fo_list)
        grouped_fo_list=[]
        for i in range(nfo):
            grouped_fo_list.append(dict(list(sta_fo_list[i].groupby("id"))))
        id_ob = list(grouped_ob.keys())
        sys._clear_type_cache()
        gc.collect()
        sta_all = []
        n_id = len(id_ob)
        if need_match_ob:
            how = "inner"
        else:
            how = "right"
        for i in range(n_id):
            rate = int((i/n_id)*100)
            if rate%5 == 0:
                if abs(i - rate * 0.01 * n_id)<1:
                    print(str(rate) + "% combined")

            key = id_ob[i]
            all_fos_have = True
            sta_ob_one_id = grouped_ob.pop(key)
            sta_fos_one_id = []
            for i in range(nfo):
                if key in grouped_fo_list[i].keys():
                   sta_fos_one_id.append(grouped_fo_list[i].pop(key))
                else:
                    all_fos_have = False
            if all_fos_have:
                combine_one = combine_on_obTime_one_id(sta_ob_one_id,sta_fos_one_id,how = how)
                sta_all.append(combine_one)
        sta_all = pd.concat(sta_all,axis=0)
    elif g == "dtime":
        nfo = len(sta_fo_list)
        grouped_fo_list = []
        for i in range(nfo):
            grouped_fo_list.append(dict(list(sta_fo_list[i].groupby("dtime"))))
        dtime_list = list(grouped_fo_list[0].keys())
        sys._clear_type_cache()
        gc.collect()
        sta_all = []
        n_dtime = len(dtime_list)

        for i in range(n_dtime):
            rate = int((i/n_dtime)*100)
            print(str(rate) + "% combined")

            key = dtime_list[i]
            all_fos_have = True
            sta_fos_one_dtime= []
            for i in range(nfo):
                if key in grouped_fo_list[i].keys():
                    sta_fos_one_dtime.append(grouped_fo_list[i].pop(key))
                else:
                    all_fos_have = False
            if all_fos_have:
                combine_one = combine_on_obTime_id(sta_ob, sta_fos_one_dtime, need_match_ob=need_match_ob)
                sta_all.append(combine_one)
        sta_all = pd.concat(sta_all, axis=0)
    if sta_all is not None:
        sta_all = sta_all.fillna(meteva.base.IV)
    return sta_all



def combine_on_obTime(sta_ob,sta_fo_list,need_match_ob = False):
    if not isinstance(sta_fo_list, list):
        sta_fo_list = [sta_fo_list]

    dtime_list = list(set(sta_fo_list[0]['dtime'].values.tolist()))
    sta_combine = []
    for dtime in dtime_list:
        sta = sta_ob.copy()
        sta["time"] = sta["time"] - datetime.timedelta(hours= dtime)
        sta["dtime"] = dtime
        sta_combine.append(sta)
    sta_combine = pd.concat(sta_combine,axis=0)

    sta_combine_fo = None
    for sta_fo in sta_fo_list:
        sta_combine_fo = combine_on_all_coords(sta_combine_fo, sta_fo)


    if need_match_ob:
        sta_combine = combine_on_all_coords(sta_combine, sta_combine_fo, how="inner")
    else:
        sta_combine = combine_on_all_coords(sta_combine,sta_combine_fo,how="right")
        sta_combine = sta_combine.fillna(meteva.base.IV)



    return sta_combine

def combine_on_bak_idandobTime1(sta_list):
    '''
    merge_on_id_and_obTime  合并多个sta——dataframe  并且保证合并后的dataframe要素名不重复
    :param sta_list:   含有多个sta_dataframe的列表
    :return:
    '''
    intersection_of_data = None
    for sta in sta_list:
        sta['dtime'] = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
        sta['time'] = sta['time'] + sta['dtime']
        sta['dtime'] = 0

        intersection_of_data = combine_on_all_coords(intersection_of_data, sta)
    return intersection_of_data


def combine_expand_IV(sta,sta_with_IV):
    '''
        将观测
        :param sta_ob:
        :param sta_fo_list:
        :return:
        '''

    sta_with_IV1 = copy.deepcopy(sta_with_IV)
    columns = ["level","time","dtime","id"]
    for i in range(4):
        sta_expand = []
        if sta_with_IV.iloc[0,i] == meteva.base.IV or pd.isnull(sta_with_IV.iloc[0,i]):
            value_list = list(set(sta.iloc[:,i].values.tolist()))
            if i == 1:
                for j in range(len(value_list)):
                    value_list[j] = meteva.base.tool.all_type_time_to_time64(value_list[j])
            for value in value_list:
                sta1 = copy.deepcopy(sta_with_IV1)
                sta1.iloc[:,i] = value
                sta_expand.append(sta1)
            sta_with_IV1 = pd.concat(sta_expand, axis=0)
    #sta_with_IV1 = sta_with_IV1.dropna()
    sta_combine = combine_on_level_time_dtime_id(sta, sta_with_IV1)
    return sta_combine

def get_inner_grid(grid0,grid1,used_coords = "xy"):
    si = 0
    sj = 0
    ei = 0
    ej = 0
    if(grid1.slon > grid0.slon):
        si = int(math.ceil((grid1.slon - grid0.slon)/grid0.dlon))
    if(grid1.slat > grid0.slat):
        sj = int(math.ceil((grid1.slat - grid0.slat)/grid0.dlat))
    if(grid1.elon < grid0.elon):
        ei = int(math.ceil((grid0.elon - grid1.elon)/grid0.dlon))
    if(grid1.elat < grid0.elat):
        ej = int(math.ceil((grid0.elat - grid1.elat)/grid0.dlat))
    slon = grid0.slon + si * grid0.dlon
    slat = grid0.slat + sj * grid0.dlat
    elon = grid0.elon - ei * grid0.dlon
    elat = grid0.elat - ej * grid0.dlat
    grid_inner = meteva.base.grid([slon,elon,grid0.dlon],[slat,elat,grid0.dlat],grid0.gtime,grid0.dtimes,grid0.levels,grid0.members)
    return grid_inner

def get_outer_grid(grid0,grid1,used_coords = "xy"):

    slon = min(grid0.slon,grid1.slon)
    slat = min(grid0.slat,grid1.slat)
    elon = max(grid0.elon,grid1.elon)
    elat = max(grid0.elat,grid1.elat)
    grid_outer = meteva.base.grid([slon,elon,grid0.dlon],[slat,elat,grid0.dlat],grid0.gtime,grid0.dtimes,grid0.levels,grid0.members)
    return grid_outer

def expand_to_contain_another_grid(grd0,grid1,used_coords = "xy",outer_value = 0):
    grid0 = meteva.base.get_grid_of_data(grd0)
    grid_outer = get_outer_grid(grid0,grid1,used_coords = used_coords)
    grd1 = meteva.base.grid_data(grid_outer)
    grd1.values[...] = outer_value

    si = 0
    sj = 0
    if (grid1.slon < grid0.slon):
        si = int(round((grid0.slon - grid1.slon) / grid0.dlon))
    if (grid1.slat < grid0.slat):
        sj = int(round((grid0.slat - grid1.slat) / grid0.dlat))
    grd1.values[:,:,:,:,sj:(sj + grid0.nlat), si:(si + grid0.nlon)] = grd0.values[...]
    return grd1

