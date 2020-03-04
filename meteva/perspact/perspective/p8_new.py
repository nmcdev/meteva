para = {
    "fo_time_range": ["2019010108", "2019020108", "12h"],
    "dtime": [1, 2, 3, "h"],
    "station": {
        "path": r"F:\ppt\sta_alt_1w.txt"
    },
    "sample_must_be_same": True,
    "dim_type": [
        {
            "name": "dim_type_region",
            "type": "grid_data",
            "path": r"F:\ppt\sr.nc"
        },

    ],
    "observation": {
        "path": r"F:\ppt\ob\sta\rain01\BTYYMMDDHH.000",
        "valid": [0, 300],
    },
    "forecasts": [
        {
            "name": "持续预报",
            "type": "sta_data",
            "path": r"F:\ppt\ob\sta\rain01\BTYYMMDDHH.000",
            "fo_time_move_back": [0, 0.5, 1],
            "ob_time_need_be_same": False,
        },
        {
            "name": "定时预报",
            "type": "grid_data",
            "path": r"F:\ppt\nmczhidao\grid\RAIN01\YYMMDD\YYMMDDHH.TTT.nc",
            "fo_time_move_back": [0, 12.5, 1],
            "ob_time_need_be_same": True,
        },
        {
            "name": "Grapes_3km",
            "type": "grid_data",
            "path": r"F:\ppt\grapes_3km\grid\rain01\BTYYMMDDHH.TTT.nc",
            "fo_time_move_back": [0, 12.5, 1],
            "ob_time_need_be_same": True,
        },
        {
            "name": "华东中尺度",
            "type": "grid_data",
            "path": r"F:\ppt\shanghai\grid\rain01\BTYYMMDDHH.TTT.nc",
            "fo_time_move_back": [0, 12.5, 1],
            "ob_time_need_be_same": True,
        },
        {
            "name": "临近外推",
            "type": "grid_data",
            "path": r"F:\ppt\nowcast\grid\rain01\BTYYMMDDHH.TTT.nc",
            "fo_time_move_back": [0, 0.5, 1],
            "ob_time_need_be_same": True,
        },
        {
            "name": "滚动更新",
            "type": "grid_data",
            "path": r"F:\ppt\nmcgundong\grid\rain01\BTYYMMDDHH.TTT.nc",
            "fo_time_move_back": [0, 0.5, 1],
            "ob_time_need_be_same": True,
        }

    ],
    "group_set": {
        "level": "fold",
        "time": "fold",
        "year": 'unfold',
        "month": {'group': [[1]],
                  'group_name': [['1月']]},
        "xun": 'fold',
        "hou": 'fold',
        "day": {'group': [[1, 2, 3, 4, 5, 6], [7, 8, 9, 10, 11, 12, 13]],
                'group_name': [['1d', '2d', '3d', '4d', '5d', '6d'], ['7d', '8d', '9d', '10d', '11d', '12d', '13d']]},
        "hour": "fold",
        "dtime": {'group': [[1, 2], [3]],
                  'group_name': [['1h', '2h'], ['3h']]
                  },
        "id": "fold",
        "dim_type_region": {
            "group": [[1], [2], [3], [4], [5], [6], [7]],
            "group_name": [["新疆"], ["西北中东部"], ["华北"], ["东北"], ["黄淮江淮江南"], ["华南"], ["西南"]],
        },

    },
    "veri_set": [
        {
            "name": "ts_bias",
            "method": ["ts", "bias"],
            "para1": [0.1, 5, 10, 20],
            "para1Name": ["小雨", ">=5毫米", ">=10毫米", ">=20毫米"],
            "plot_type": "bar"
        },

        {
            "name": "pc_sun_rain",
            "method": ["pc"],
            "plot_type": "bar"
        },
        {
            "name": "me_mae_mse_rmse",
            "method": ["me", 'mae', 'mse', 'rmse'],
            "plot_type": "bar"
        }
    ],
    "plot_set": {
        "subplot": "vmethod",
        "legend": "member",
        "axis": "dim_type_region"
    },
    "save_dir": r"F:\veri_result\p8new"

}

import time
import meteva
import meteva.perspact.perspective.veri_excel_set as veri_excel_set
import datetime
import pandas as pd
import xarray as xr
import copy
import math
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
import numpy as np
import meteva


# 参数数组转换为列表
def para_array_to_list(key_num, para_array):
    key_list = []
    for key in para_array.keys():
        key_list.append(key)
    key_count = len(key_list)

    if (key_num == key_count - 1):
        key = key_list[key_num]
        para_list = []
        list1 = para_array[key]
        for para in list1:
            dict1 = {}
            dict1[key] = para
            para_list.append(dict1)
    else:
        key = key_list[key_num]
        list1 = para_array[key]
        para_list0 = para_array_to_list(key_num + 1, para_array)
        para_list = []
        for para in list1:
            for dict0 in para_list0:
                dict1 = {}
                dict1[key] = para
                for key0 in dict0.keys():
                    dict1[key0] = copy.deepcopy(dict0[key0])
                # print(dict1)
                para_list.append(dict1)
    return para_list


def get_time_dims(para, is_fold_area=True):  # mpara, data_name_list,
    '''
    获取区域维度的名字和维度
    :param para: 最初的字典
    :param is_fold_time: 是否关闭time维度
    :return:
    '''
    group_set = copy.deepcopy(para['group_set'])
    # 获取维度信息
    if is_fold_area == True:
        group_set = close_area_grouping(group_set)
    coords = {}
    shape = []
    for coord in group_set.keys():
        if group_set[coord] != "fold":
            coords[coord] = ['、'.join(lable) for lable in group_set[coord]["group_name"]]
            shape.append(len(coords[coord]))
    return coords, shape


def close_area_grouping(group_dict):
    time_name_list = ['time', 'year', "month", "xun", "hou", "day", "hour", 'dtime']
    for key in group_dict:
        if key not in time_name_list:
            group_dict[key] = 'fold'
    return group_dict


def get_middle_veri_para(veri_para):
    nead_hmfc_methods = ["ts", "bias", "ets", "fal_rate", "hit_rate", "mis_rate"]
    nead_abcd_methods = ["pc", "spc"]
    nead_tase_methods = ['me', 'mae', 'mse', 'rmse']
    mpara = copy.deepcopy(veri_para)
    methods = veri_para["method"]
    for method in methods:
        if method in nead_hmfc_methods:
            mpara["method"] = ["hmfn"]
            break
        if method in nead_abcd_methods:
            mpara["method"] = ["abcd"]
            break
        if method in nead_tase_methods:
            mpara["method"] = ["tase"]

    return mpara


def para_array_to_list(key_num, para_array):
    key_list = []
    for key in para_array.keys():
        key_list.append(key)
    key_count = len(key_list)

    if (key_num == key_count - 1):
        key = key_list[key_num]
        para_list = []
        list1 = para_array[key]
        for para in list1:
            dict1 = {}
            dict1[key] = para
            para_list.append(dict1)
    else:
        key = key_list[key_num]
        list1 = para_array[key]
        para_list0 = para_array_to_list(key_num + 1, para_array)
        para_list = []
        for para in list1:
            for dict0 in para_list0:
                dict1 = {}
                dict1[key] = para
                for key0 in dict0.keys():
                    dict1[key0] = copy.deepcopy(dict0[key0])
                para_list.append(dict1)
    return para_list


def get_dims_and_coords_and_shape(para, shape, dims, indexes_dict, coords_dict, final_result_dict_list_array):
    new_coords_dict = {}
    new_indexes_dict = {}
    new_shape_dict = {}
    for i in range(len(para['veri_set'])):
        overall_shape = copy.deepcopy(shape)
        new_coords = []
        new_indexes = []
        for key in dims.keys():
            new_coords.append(dims[key])
            new_indexes.append(key)
        new_indexes.append('vmethod')
        new_indexes.extend(indexes_dict[i])
        new_coords.append(para['veri_set'][i]['method'])
        new_coords.extend(coords_dict[i])
        new_coords_dict[i] = new_coords
        new_indexes_dict[i] = new_indexes
        final_result_dict_list_array[i] = np.array(final_result_dict_list_array[i])
        area_shape = final_result_dict_list_array[i].shape[1:]
        overall_shape.extend(area_shape)
        new_shape_dict[i] = overall_shape
    return new_indexes_dict, new_coords_dict, new_shape_dict


def group_sta(para_group_set):
    para_dict_list_list = {}
    for key in para_group_set:
        if para_group_set[key] != "fold" and para_group_set[key] != 'unfold':
            para_dict_list_list[key] = para_group_set[key]["group"]
            # para_dict_list_list ={dtime:[[],[],[]],dim_type_region:[[],[],[]]}
    if len(para_dict_list_list) < 1:
        para_list_dict_list = None
    else:
        para_list_dict_list = para_array_to_list(0, para_dict_list_list)
    return para_list_dict_list


def ob_time_and_fo_time_link(fo_start_time, fo_end_time, dtime_list, ob_time_dict, time_step):
    '''
    将实况时间==（预报时间+dtime) 的时间通过字典联系在一起如：
    {实况时间：[预报时间,dtime]}
    :param fo_start_time: 开始的预报时间
    :param fo_end_time: 结束预报时间
    :param dtime_list:  dtime的列表
    :param ob_time_dict: 实况时间的字典
    :param time_step: time跳跃的时间
    :return:
    '''
    time1 = copy.deepcopy(fo_start_time)
    while time1 <= fo_end_time:
        for dh in dtime_list:
            ob_time = time1 + datetime.timedelta(hours=dh)
            if ob_time not in ob_time_dict.keys():
                ob_time_dict[ob_time] = [[time1, dh]]
            else:
                ob_time_dict[ob_time].append([time1, dh])
        time1 = time1 + datetime.timedelta(hours=time_step)


def one_score(param, mid_result_list_set, sum):
    score_list = []
    area_indexes = []
    coords = []

    if 'ts' in param['method']:
        hmfn_sum = np.zeros((1))
        for data in mid_result_list_set:

            hmfn_data_array = data.hmfn_array
            area_indexes = list(hmfn_data_array.coords)[:-1]
            coords = []
            for index in area_indexes:
                label = hmfn_data_array[index].values
            hmfn_array = hmfn_data_array.values
            hmfn_sum = hmfn_array + hmfn_sum

        hit = hmfn_sum[..., 0]
        mis = hmfn_sum[..., 1]
        fal = hmfn_sum[..., 2]
        ts = hit / (mis + fal + hit + 1e-6)
        score_list.append(ts)

    if 'bias' in param['method']:
        hmfn_sum = np.zeros((1))
        for data in mid_result_list_set:
            hmfn_data_array = data.hmfn_array
            area_indexes = list(hmfn_data_array.coords)[:-1]
            coords = []
            for index in area_indexes:
                label = hmfn_data_array[index].values
                coords.append(label)
            hmfn_array = hmfn_data_array.values
            hmfn_sum = hmfn_array + hmfn_sum
        hit = hmfn_sum[..., 0]
        mis = hmfn_sum[..., 1]
        fal = hmfn_sum[..., 2]
        bias = (hit + fal) / (mis + hit + 1e-6)
        score_list.append(bias)

    if 'pc' in param['method']:
        abcd_sum = np.zeros((1))

        for data in mid_result_list_set:
            abcd_data_array = data.abcd_array
            area_indexes = list(abcd_data_array.coords)[:-1]
            coords = []
            for index in area_indexes:
                label = abcd_data_array[index].values
                coords.append(label)

            abcd_array = abcd_data_array.values
            abcd_sum = abcd_array + abcd_sum
        na = abcd_sum[..., 0]
        nd = abcd_sum[..., 3]
        pc = (na + nd) / (sum + 1e-6)

        score_list.append(pc)
    if 'me' in param['method']:
        tase_sum = np.zeros((1))
        for data in mid_result_list_set:
            tase_data_array = data.tase_array
            area_indexes = list(tase_data_array.coords)[:-1]
            coords = []
            for index in area_indexes:
                label = tase_data_array[index].values
                coords.append(label)
            tase_array = tase_data_array.values
            tase_sum = tase_array + tase_sum
        me = tase_sum[..., 0] / (sum + 1e-6)
        score_list.append(me)
    if 'mae' in param['method']:
        tase_sum = np.zeros((1))
        for data in mid_result_list_set:
            tase_data_array = data.tase_array
            area_indexes = list(tase_data_array.coords)[:-1]
            coords = []
            for index in area_indexes:
                label = tase_data_array[index].values
                coords.append(label)
            tase_array = tase_data_array.values
            tase_sum = tase_array + tase_sum
        mae = tase_sum[..., 1] / (sum + 1e-6)
        score_list.append(mae)
    if 'mse' in param['method']:
        tase_sum = np.zeros((1))
        for data in mid_result_list_set:
            tase_data_array = data.tase_array
            area_indexes = list(tase_data_array.coords)[:-1]
            coords = []
            for index in area_indexes:
                label = tase_data_array[index].values
                coords.append(label)
            tase_array = tase_data_array.values
            tase_sum = tase_array + tase_sum
        mse = tase_sum[..., 2] / (sum + 1e-6)
        score_list.append(mse)
    if 'rmse' in param['method']:
        tase_sum = np.zeros((1))
        for data in mid_result_list_set:
            tase_data_array = data.tase_array
            area_indexes = list(tase_data_array.coords)[:-1]
            coords = []
            for index in area_indexes:
                label = tase_data_array[index].values
                coords.append(label)
            tase_array = tase_data_array.values
            tase_sum = tase_array + tase_sum
        mse = tase_sum[..., 2] / (sum + 1e-6)
        rmse = np.sqrt(mse)
        score_list.append(rmse)


    return score_list, area_indexes, coords


def create_DataArray_dict(para, final_result_dict_list_array, new_shape_dict, new_coords_dict, new_indexes_dict):
    # 将数据通过上文得到的indexes# coords和shape和grades转化为DataArray 并且将dataArray放到字典中

    all_catrgory_grades_data_array_dict = {}
    for i in range(len(para['veri_set'])):
        category_of_grades = final_result_dict_list_array[i]
        category_of_shape = new_shape_dict[i]
        category_of_coords = new_coords_dict[i]
        category_of_indexes = new_indexes_dict[i]
        category_of_grades = category_of_grades.reshape(category_of_shape)
        category_of_data_array = xr.DataArray(category_of_grades, coords=category_of_coords, dims=category_of_indexes)
        all_catrgory_grades_data_array_dict[i] = category_of_data_array
    return all_catrgory_grades_data_array_dict


def filter_valid_data(one_tiem_group_and_dtime_path):
    sum = np.zeros((1))
    data_list = []
    for path in one_tiem_group_and_dtime_path:
        data = xr.open_dataset(path)
        total_dataset = data['total_num']
        data_list.append(data)
        total_array = total_dataset.values
        sum = total_array + sum
    new_sum = copy.deepcopy(sum)
    new_sum[new_sum > 0] = -1
    new_sum += 1

    # 通过total 和total判断是否跳过该数据
    mid_result_list_set = []
    for data in data_list:
        total_dataset = data['total_num']
        total_array = total_dataset.values
        xx = new_sum + total_array
        if np.any(xx) == 0:
            continue
        else:
            mid_result_list_set.append(data)
    return mid_result_list_set, sum


def calculate_score(para, all_path, final_result_dict_list_array, indexes_dict, coords_dict):
    for one_time_group_path in all_path:
        for one_tiem_group_and_dtime_path in one_time_group_path:
            # 获取评分

            # 计算total_sum
            mid_result_list_set, sum = filter_valid_data(one_tiem_group_and_dtime_path)

            # 获取area的indexes 和coords
            for i in range(len(para["veri_set"])):
                score_list, area_indexes, coords = one_score(para["veri_set"][i], mid_result_list_set, sum)
                final_result_dict_list_array[i].append(score_list)
                indexes_dict[i] = area_indexes
                coords_dict[i] = coords
    return final_result_dict_list_array, coords_dict, indexes_dict


def filter_time_series(par_dict, time_Series2):
    if par_dict != 0:
        for key in par_dict.keys():
            if key == "year":
                time_series1 = pd.Series()
                for year in par_dict[key]:
                    time_Series0 = time_Series2.loc[time_Series2.dt.year == year]
                    time_series1 = time_series1.append(time_Series0)
                time_Series2 = time_series1
            if key == "month":
                time_series1 = pd.Series()
                for month in par_dict[key]:
                    time_Series0 = time_Series2.loc[time_Series2.dt.month == month]
                    time_series1 = time_series1.append(time_Series0)
                time_Series2 = time_series1
            if key == "xun":
                time_series1 = pd.Series()
                for xun in par_dict[key]:
                    mons = time_Series2.map(lambda x: x.month).values.astype(np.int16)
                    days = time_Series2.map(lambda y: y.day).values.astype(np.int16)
                    xuns = np.ceil(days / 10).astype(np.int16)
                    xuns[xuns > 3] = 3
                    xuns += (mons - 1) * 3
                    time_Series0 = time_Series2.loc[xuns == xun]
                    time_series1 = time_series1.append(time_Series0)
                time_Series2 = time_series1
            if key == "hou":
                time_series1 = pd.Series()
                for hou in par_dict[key]:
                    mons = time_Series2.map(lambda x: x.month).values.astype(np.int16)
                    days = time_Series2.map(lambda y: y.day).values.astype(np.int16)
                    hous = np.ceil(days / 5).astype(np.int16)
                    hous[hous > 6] = 6
                    hous += (mons - 1) * 6
                    time_Series0 = time_Series2.loc[hous == hou]
                    time_series1 = time_series1.append(time_Series0)
                time_Series2 = time_series1

            if key == "day":
                time_series1 = pd.Series()
                # print(time_Series2)
                for day in par_dict[key]:
                    # print(time_Series2.dt.day==day)
                    time_Series0 = time_Series2.loc[time_Series2.dt.day == day]
                    time_series1 = time_series1.append(time_Series0)

                time_Series2 = time_series1

            if key == "hour":
                time_series1 = pd.Series()
                for hour in par_dict[key]:
                    time_Series0 = time_Series2.loc[time_Series2.dt.hour == hour]
                    time_series1 = time_series1.append(time_Series0)
                time_Series2 = time_series1
    return time_Series2


def join_time_dtime_nc_path(dtime_group_list_list, time_df):
    one_time_group_path = []
    for dtime_group_list in dtime_group_list_list:
        dtime_group_list = ['%03d' % dtime for dtime in dtime_group_list]
        dtime_df = pd.DataFrame({'dtime': dtime_group_list})
        dtime_df['value'] = 1
        # 通过merge进行笛卡尔积运算
        one_tiem_group_and_dtime_df = pd.merge(time_df, dtime_df, on='value')
        one_tiem_group_and_dtime_df['time'] = one_tiem_group_and_dtime_df['time'].apply(
            lambda x: x.strftime('%Y%m%d%H'))
        one_tiem_group_and_dtime_df['nc'] = 'nc'
        one_tiem_group_and_dtime_df = one_tiem_group_and_dtime_df.drop(['value'], axis=1)
        one_tiem_group_and_dtime_list_list = one_tiem_group_and_dtime_df.values.tolist()
        # 将笛卡尔积得到的df转化为的列表进行join 从而拼接成path
        one_tiem_group_and_dtime_path = ['.'.join(one_tiem_group_and_dtime_list) for
                                         one_tiem_group_and_dtime_list in
                                         one_tiem_group_and_dtime_list_list]
        one_time_group_path.append(one_tiem_group_and_dtime_path)
    return one_time_group_path
    pass


def get_all_path(para_dict_list_list, time_Series, dtime_list, shape):
    all_path = []
    for par_dict in para_dict_list_list:
        time_Series2 = copy.deepcopy(time_Series)

        # 通过time分组来进行对time进行筛选，挑选出符合当前分组的time
        time_Series2 = filter_time_series(par_dict, time_Series2)

        # 对分组dtime和上文筛选出的time进行笛卡尔积
        time_df = pd.DataFrame({'time': time_Series2})  # 将时间series转化为df是为了下一步笛卡尔积运算
        time_df['value'] = 1
        if para['group_set']['dtime'] == 'fold':
            dtime_group_list_list = [dtime_list]
            shape.append(len(dtime_group_list_list))
        elif para['group_set']['dtime'] == 'unfold':
            dtime_array = np.array(dtime_list)
            dtime_array = dtime_array.reshape([-1, 1])
            dtime_group_list_list = dtime_array.tolist()
            shape.append(len(dtime_group_list_list))
        else:
            dtime_group_list_list = para['group_set']['dtime']['group']

        one_time_group_path = join_time_dtime_nc_path(dtime_group_list_list, time_df)

        all_path.append(one_time_group_path)
    return all_path, shape


def create_empty_data_and_coords_and_indexes_dict(para):
    final_result_dict_list_array = {}
    coords_dict = {}
    indexes_dict = {}
    for i in range(len(para["veri_set"])):
        final_result_dict_list_array[i] = []
        coords_dict[i] = None
        indexes_dict[i] = None

    return final_result_dict_list_array, coords_dict, indexes_dict


def get_time_Series(time1, fo_end_time, time_type, time_step):
    time_list = []
    # 对时间序列进行处理
    time_Series = None
    while time1 <= fo_end_time:
        if (time_type == "h"):
            time1 = time1 + datetime.timedelta(hours=time_step)
        else:
            time1 = time1 + datetime.timedelta(minutes=time_step)
        time_list.append(time1)
        time_Series = pd.Series(time_list)
    return time_Series


def time_unfold(para, time_series):
    new_time_series = copy.deepcopy(time_series)
    for key in para['group_set'].keys():
        if key == 'year' and para['group_set'][key] == 'unfold':
            year_series = new_time_series.dt.year
            year_list = list(set(year_series))
            year_np = np.array(year_list)

            year_np = year_np.reshape([-1, 1])
            year_list_list = year_np.tolist()
            para['group_set'][key] = {}
            para['group_set'][key]['group'] = year_list_list
            new_year_list_list = copy.deepcopy(year_list_list)
            group_name_list_list = []
            for year_list in new_year_list_list:
                group_name_list = []
                for year in year_list:
                    year_name = str(year) + 'year'

                    group_name_list.append(year_name)
                group_name_list_list.append(group_name_list)
            para['group_set'][key]['group_name'] = group_name_list_list

        if key == 'month' and para['group_set'][key] == 'unfold':
            month_series = new_time_series.dt.day
            month_list = list(set(month_series))
            month_np = np.array(month_list)

            month_np = month_np.reshape([-1, 1])
            month_list_list = month_np.tolist()
            para['group_set'][key] = {}
            para['group_set'][key]['group'] = month_list_list
            new_month_list_list = copy.deepcopy(month_list_list)
            group_name_list_list = []
            for month_list in new_month_list_list:
                group_name_list = []
                for month in month_list:
                    month_name = str(month) + 'month'

                    group_name_list.append(month_name)
                group_name_list_list.append(group_name_list)
            para['group_set'][key]['group_name'] = group_name_list_list

        if key == 'xun' and para['group_set'][key] == 'unfold':
            mons = new_time_series.map(lambda x: x.month).values.astype(np.int16)
            days = new_time_series.map(lambda y: y.day).values.astype(np.int16)
            xuns = np.ceil(days / 10).astype(np.int16)
            xuns[xuns > 3] = 3
            xuns += (mons - 1) * 3
            xun_list = list(set(xuns))
            xun_np = np.array(xun_list)

            xun_np = xun_np.reshape([-1, 1])
            xun_list_list = xun_np.tolist()
            para['group_set'][key] = {}
            para['group_set'][key]['group'] = xun_list_list
            new_xun_list_list = copy.deepcopy(xun_list_list)
            group_name_list_list = []
            for xun_list in new_xun_list_list:
                group_name_list = []
                for xun in xun_list:
                    xun_name = str(xun) + 'xun'

                    group_name_list.append(xun_name)
                group_name_list_list.append(group_name_list)
            para['group_set'][key]['group_name'] = group_name_list_list

        if key == 'hou' and para['group_set'][key] == 'unfold':
            mons = new_time_series.map(lambda x: x.month).values.astype(np.int16)
            days = new_time_series.map(lambda y: y.day).values.astype(np.int16)
            hous = np.ceil(days / 5).astype(np.int16)
            hous[hous > 6] = 6
            hous += (mons - 1) * 6
            hous_list = list(set(hous))
            hous_np = np.array(hous_list)

            hous_np = hous_np.reshape([-1, 1])
            hous_list_list = hous_np.tolist()
            para['group_set'][key] = {}
            para['group_set'][key]['group'] = hous_list_list
            new_hous_list_list = copy.deepcopy(hous_list_list)
            group_name_list_list = []
            for hous_list in new_hous_list_list:
                group_name_list = []
                for hous in hous_list:
                    hous_name = str(hous) + 'hous'

                    group_name_list.append(hous_name)
                group_name_list_list.append(group_name_list)
            para['group_set'][key]['group_name'] = group_name_list_list

        if key == 'day' and para['group_set'][key] == 'unfold':
            day_series = new_time_series.dt.day
            day_list = list(set(day_series))
            day_np = np.array(day_list)

            day_np = day_np.reshape([-1, 1])
            day_list_list = day_np.tolist()
            para['group_set'][key] = {}
            para['group_set'][key]['group'] = day_list_list
            new_day_list_list = copy.deepcopy(day_list_list)
            group_name_list_list = []
            for day_list in new_day_list_list:
                group_name_list = []
                for day in day_list:
                    day_name = str(day) + 'day'

                    group_name_list.append(day_name)
                group_name_list_list.append(group_name_list)
            para['group_set'][key]['group_name'] = group_name_list_list

        if key == 'hour' and para['group_set'][key] == 'unfold':
            hour_series = new_time_series.dt.hour
            hour_list = list(set(hour_series))
            hour_np = np.array(hour_list)

            hour_np = hour_np.reshape([-1, 1])
            hour_list_list = hour_np.tolist()
            para['group_set'][key] = {}
            para['group_set'][key]['group'] = hour_list_list
            new_hour_list_list = copy.deepcopy(hour_list_list)
            group_name_list_list = []
            for hour_list in new_hour_list_list:
                group_name_list = []
                for hour in hour_list:
                    hour_name = str(hour) + 'hour'

                    group_name_list.append(hour_name)
                group_name_list_list.append(group_name_list)
            para['group_set'][key]['group_name'] = group_name_list_list
    return para


def verification_with_complite_para(para):
    fo_start_time = meteva.base.tool.time_tools.str_to_time(para["fo_time_range"][0])
    fo_end_time = meteva.base.tool.time_tools.str_to_time(para["fo_time_range"][1])
    time_step = int(para["fo_time_range"][2][0:-1])
    time_type = para["fo_time_range"][2][-1]

    ob_time_dict = {}
    time1 = fo_start_time
    dtime_list = para["dtime"][0:-1]
    ob_time_and_fo_time_link(time1, fo_end_time, dtime_list, ob_time_dict, time_step)
    time1 = fo_start_time - datetime.timedelta(hours=time_step)
    # 获取时间维度的信息
    veri_group_num = len(para["veri_set"])
    # print(veri_group_num)# 有几中检验标准 ，hmnf和 pc_hmnf#等
    middle_veri = {}
    for i in range(veri_group_num):
        middle_veri[i] = {}
        middle_veri[i]["para"] = get_middle_veri_para(para["veri_set"][i])

    time_series = get_time_Series(time1, fo_end_time, time_type, time_step)
    para = time_unfold(para, time_series)
    dims, shape = get_time_dims(para, is_fold_area=True)

    # 获取时间分组
    group_dict = copy.deepcopy(para['group_set'])
    time_name_list = ['time', 'year', "month", "xun", "hou", "day", "hour"]
    for key in group_dict:
        if key not in time_name_list:
            group_dict[key] = 'fold'

    para_dict_list_list = group_sta(group_dict)

    if para_dict_list_list is None:
        para_dict_list_list = [0]
    final_result_dict_list_array, coords_dict, indexes_dict = create_empty_data_and_coords_and_indexes_dict(para)
    # print(final_result_dict_list_array)
    # print(coords_dict)
    # print(indexes_dict)

    all_path, shape = get_all_path(para_dict_list_list, time_series, dtime_list, shape)

    final_result_dict_list_array, coords_dict, indexes_dict = calculate_score(para, all_path,
                                                                              final_result_dict_list_array,
                                                                              indexes_dict, coords_dict)

    # 读取数据，计算出评分 并且将对应的数据按照vari_set的长度组成字典。 获取区域的dim和indexes

    # 得到转化DataArray所需要的coords和indexes和shape
    new_indexes_dict, new_coords_dict, new_shape_dict = get_dims_and_coords_and_shape(para, shape, dims, indexes_dict,
                                                                                      coords_dict,
                                                                                      final_result_dict_list_array)
    # 将数据通过上文得到的indexes 和coords和shape和grades转化为DataArray
    all_catrgory_grades_data_array_dict = create_DataArray_dict(para, final_result_dict_list_array, new_shape_dict,
                                                                new_coords_dict, new_indexes_dict)

    # 画图，将检验结果保存到excel中
    for key in all_catrgory_grades_data_array_dict.keys():
        veri_name = para["veri_set"][key]["name"]
        save_dir = para["save_dir"] + "/" + veri_name + "/"
        path = para["save_dir"] + "/" + veri_name + ".nc"
        result = all_catrgory_grades_data_array_dict[key]
        result.to_netcdf(path)
        plot_set = meteva.perspact.perspective.veri_plot_set(subplot=para["plot_set"]["subplot"],
                                                                            legend=para["plot_set"]["legend"],
                                                                            axis=para["plot_set"]["axis"],
                                                                            save_dir=save_dir)
        plot_set.bar(all_catrgory_grades_data_array_dict[key])
        excel_set = meteva.perspact.perspective.veri_excel_set.veri_excel_set(
            sheet=para["plot_set"]["subplot"], row=para["plot_set"]["legend"],
            column=para["plot_set"]["axis"], save_dir=save_dir)
        excel_set.excel(all_catrgory_grades_data_array_dict[key])


import meteva.perspact.perspective.veri_task1wbl as veri_task1wbl
start = time.time()
verification_with_complite_para(para)

end = time.time()
print(end - start)