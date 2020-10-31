# -*- coding:UTF-8 -*-
import copy
import numpy as np
import pandas as pd
import meteva


def sta_data(df,columns = None):
    '''
    sta_data() 对数据进行格式化成为固定格式
    :param df: dataframe的站点数据
    :param columns: 文件内包含的数据的列名
    :return: 包含‘level', 'time', 'dtime', 'id', 'lon', 'lat',  列的一个dataframe
    '''
    #提取dframe0 列名称
    if columns is None:
        columns = df.columns

    # 将列名变为小写
    columns_1 = []
    for column in columns:
        #column = column.lower()
        columns_1.append(column)
    columns = columns_1

    new_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat']

    # 提取数据列名称,扩展到新df的列名称中
    for column in columns:
        if column not in new_columns:
            new_columns.append(column)
    sta = copy.deepcopy(df)

    sta.columns = columns
    if "id" not in columns:
        sta["id"] = meteva.base.IV
    reset_id(sta)
    sta.reset_index(inplace=True)

    # 更改列名
    sta = sta.reindex(columns = new_columns)
    #dframe1 = dframe1[new_columns]

    # 排序
    sta.sort_values(by=new_columns[:4],inplace=False)

    if len(sta.columns) == 6:
        sta["data0"] =0
    else:
        #for i in range(6,len(sta.columns)):
        #    sta.iloc[:,i] = (sta.values[:,i]).astype(np.float32)
        pass

    return sta


def get_undim_data_names(sta):
    '''

    :param sta:
    :return:
    '''
    coor_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat']
    columns = sta.columns
    data_columns = []
    for column in columns:
        if column not in coor_columns:
            if column.find("dim_type")!=0:
                data_columns.append(column)
    return data_columns

def get_stadata_names(sta):
    '''
    get_data_names() 获取站点数据的要素名
    :param sta: 站点数据
    :return: 要素名列表
    '''
    coor_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat']
    columns = sta.columns
    data_columns = []
    for column in columns:
        if column not in coor_columns:
            data_columns.append(column)
    return data_columns

def get_coord_names():
    '''

    :return: 站点数据基本信息列名['level', 'time', 'dtime', 'id', 'lon', 'lat']列表
    '''
    return ['level', 'time', 'dtime', 'id', 'lon', 'lat']

def set_stadata_names(sta,data_name_list):
    '''
    更改 要素名，和添加缺省列
    :param sta: 站点数据
    :param data_name: 站点数据 要素名
    :return: 更改要素名名后的站点数据
    '''
    if not isinstance(data_name_list,list):
        data_name_list = [data_name_list]
    #if isinstance(data_name_list,list):
    coor_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat']
    for data_name in data_name_list:
        coor_columns.append(data_name)
    sta.columns = coor_columns
    #else:
    #    print("输出名称设置不成功，数据名称列表参数需为list形式")
    return

def set_stadata_coords(sta,level = None,time = None,dtime = None,id = None,lat = None,lon = None):
    '''
    set_time_dtime_level_name 设置time_dtime_level 的值  并且设置要素名
    :param sta: 站点数据
    :param time: 起报时
    :param dtime: 时效
    :param level: 层次
    :param data_name: 要素名
    :return:  站点数据
    '''
    if time is not None:
        time1 = meteva.base.all_type_time_to_time64(time)
        sta.loc[:,'time'] = time1
    if dtime is not None:
        sta.loc[:,'dtime'] = dtime
    if level is not None:
        sta.loc[:,'level'] = level
    if id is not None:
        sta.loc[:,"id"] = id
    if lat is not None:
        sta.loc[:,"lat"] = lat
    if lon is not None:
        sta.loc[:,"lon"] = lon


def reset_id(sta):
    '''
    输入的sta的站号中可能有些站号包含a-z,A-Z的字母，对此将这些字母转换为对应的ASCII数字，再将整个字符串格式的站号转换为数值形式
    返回sta站号为整型
    '''
    #print(sta)

    id_type = str(sta["id"].dtype)
    if id_type.find("int32") <0:
        values = sta['id'].values
        if id_type.find("int") >=0 or id_type.find("float") >=0:
            int_id = values.astype(np.int32)
            sta['id'] = int_id
        else:
            int_id = np.zeros(len(values))
            for i in range(len(values)):
                if isinstance(values[i],str):
                    strs = values[i]
                    strs_int = ""
                    for s in strs:
                        if s.isdigit():
                            strs_int += s
                        else:
                            strs_int += str(ord(s))
                    int_id[i] = int(strs_int)
                else:
                    int_id[i] = values[i]
            int_id = int_id.astype(np.int32)
            sta['id'] = int_id
    return


