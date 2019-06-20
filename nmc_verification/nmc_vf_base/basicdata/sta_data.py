# -*- coding:UTF-8 -*-
import copy


def sta_data(df, columns=None):
    '''
    sta_data是一个用来将Demo3格式的数据，进行格式化的函数，
    将column全部变为小写。并且将column统一为
    'level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt'，data0，data1.......。
    ------------------------------

    :param df: Demo3类型的DateFrame
    :param columns: DateFrame列名
    :return: sta:一个格式化之后的DateFrame

    '''

    # 提取dframe0 列名称
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

    # 将缺省的列填充
    # for corr_column in new_columns:
    #    if corr_column not in columns:
    #        columns_num = new_columns.index(corr_column)
    #        dframe1.insert(columns_num, corr_column,9999)
    sta = sta.reindex(columns=new_columns)
    # dframe1 = dframe1[new_columns]

    # 更改列名
    # data = 'data'
    # num = sta.shape[1]
    # for i in range(8,num):
    #    new_name = data+str(i)
    #    sta.rename(columns={i: new_name}, inplace=True)

    # 排序
    sta.sort_values(by=new_columns[:4], inplace=False)

    # 单层索引
    return sta


def get_data_names(sta):
    '''
    get_data_naems  获取要素的column
    ---------
    :param sta:
    :return: data_columns
    '''
    coor_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt']
    columns = sta.columns
    data_columns = []
    for column in columns:
        if column not in coor_columns:
            data_columns.append(column)
    return data_columns


def set_data_name(sta, data_name):
    '''
    set_data_name 设置要素column
    -----------------
    :param sta: DateFrame
    :param data_name: list类型，里面包含column
    :return:
    '''
    coor_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt', data_name]
    sta.columns = coor_columns
    return


def set_time_dtime_level(sta, time=None, dtime=None, level=None):
    '''
    set_time_dtime_level  设置time，dtime，level
    -------------
    :param sta: DateFrame
    :param time: 设置后的时间
    :param dtime: 设置后的时效
    :param level: 设置后的层
    :return:
    '''
    if time is not None:
        sta['time'] = time
    if dtime is not None:
        sta['dtime'] = dtime
    if level is not None:
        sta['level'] = level
