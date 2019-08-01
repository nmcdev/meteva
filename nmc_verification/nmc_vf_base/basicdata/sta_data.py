# -*- coding:UTF-8 -*-
import copy
import numpy as np

def sta_data(df,columns = None):
    '''
    sta_data() 对数据进行格式化成为固定格式
    :param df: dataframe的站点数据
    :param columns: 文件内包含的数据的列名
    :return: 包含level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt 列的一个dataframe
    '''
    #提取dframe0 列名称
    if columns is None:
        columns = df.columns

    # 将列名变为小写
    columns_1 = []
    for column in columns:
        column = column.lower()
        columns_1.append(column)
    columns = columns_1

    new_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']

    # 提取数据列名称,扩展到新df的列名称中
    data_column = []
    for column in columns:
        if column not in new_columns:
            new_columns.append(column)
    sta = copy.deepcopy(df)
    sta.reset_index(inplace=True)
    reset_id(sta)
    # 将缺省的列填充
    #for corr_column in new_columns:
    #    if corr_column not in columns:
    #        columns_num = new_columns.index(corr_column)
    #        dframe1.insert(columns_num, corr_column,9999)
    sta = sta.reindex(columns = new_columns)
    #dframe1 = dframe1[new_columns]

    # 更改列名
    #data = 'data'
    #num = sta.shape[1]
    #for i in range(8,num):
    #    new_name = data+str(i)
    #    sta.rename(columns={i: new_name}, inplace=True)

    # 排序
    sta.sort_values(by=new_columns[:4],inplace=False)

    # 单层索引
    return sta

def get_undim_data_names(sta):
    '''

    :param sta:
    :return:
    '''
    coor_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']
    columns = sta.columns
    data_columns = []
    for column in columns:
        if column not in coor_columns:
            if column.find("dim_type")!=0:
                data_columns.append(column)
    return data_columns

def get_data_names(sta):
    '''
    get_data_names() 获取站点数据的要素名
    :param sta: 站点数据
    :return: 要素名列表
    '''
    coor_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']
    columns = sta.columns
    data_columns = []
    for column in columns:
        if column not in coor_columns:
            data_columns.append(column)
    return data_columns

def get_coord_names():
    '''

    :return: 站点数据基本信息列名['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']列表
    '''
    return ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']

def set_data_name(sta,data_name):
    '''
    更改 要素名，和添加缺省列
    :param sta: 站点数据
    :param data_name: 站点数据 要素名
    :return: 更改要素名名后的站点数据
    '''
    coor_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt',data_name]
    sta.columns = coor_columns
    return

def set_time_dtime_level_name(sta,time = None,dtime = None,level = None,data_name = None):
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
        sta['time'] = time
    if dtime is not None:
        sta['dtime'] = dtime
    if level is not None:
        sta['level'] = level
    if data_name is not None:
        set_data_name(sta,data_name)
        
        
def reset_id(sta):
    '''
    将带有a-z,A-Z格式的按照，通过ASCII码转换为数字，拼接完之后，再返回
    例如：sta = 'abdf' 返回：9798100102
    :param sta:站号
    :return:ASCII转码之后的int型站号。
    '''
    a_list = []
    b_list = []
    for item in sta:
        a_list.append(item)
    num = len(a_list)
    for i in range(0, num):
        num = ord(a_list[i])
        b_list.append(str(num))
    item2 = "".join(b_list)
    return int(item2)


def reset_id(sta):
    values = sta['id'].values
    if type(values[0]) == str:
        int_id = np.zeros(len(values))
        for i in range(len(values)):
            strs = values[i]
            strs_int = ""
            for s in strs:
                if s.isdigit():
                    strs_int += s
                else:
                    strs_int += str(ord(s))
            int_id[i] = int(strs_int)
        int_id = int_id.astype(np.int32)
        sta['id'] = int_id
    return