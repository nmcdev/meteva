import copy
import datetime
import numpy as np
import copy
import nmc_verification
import nmc_verification.nmc_vf_report.perspective as perspective
import collections
import os
import xarray as xr
import pandas as pd
import xarray


# 将参数数组转换为列表
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


# 将所有评分分为两类  hmfn   和 abcd 改变字典的method 的值
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
            mpara['method'] = ['tase']
            break

    return mpara


def middle_veri_result_add(middle_already, middle_part, sample_same):
    if sample_same:
        total_num = middle_part[:, :, 0]
        shape = list(middle_part.shape)
        model_num = shape[1]
        shape.append(model_num)
        shape = tuple(shape)
        middle_part_4d = np.zeros(shape)
        num_0 = np.zeros(total_num.shape)
        num_0[total_num == 0] = 1
        sum_num_0 = np.sum(num_0, axis=1)  # sum_num_0 记录时空维度中有几个模式为全部缺省
        # print('lllllllllllllllllllllllllllllllstart')
        # print(sum_num_0)
        # print('llllllllllllllllllllllllllllllllend')
        # 广播
        for i in range(model_num):
            middle_part_4d[:, :, :, i] = middle_part[:, :, :]
            # print('middle_part_4d[index_has0, :, :, i]middle_part_4d[index_has0, :, :, i]middle_part_4d[index_has0, :, :, i]start',i)
            # print(middle_part_4d)
            # print('middle_part_4d[index_has0, :, :, i]middle_part_4d[index_has0, :, :, i]middle_part_4d[index_has0, :, :, i]end',i)

            #
            index_has0 = np.where(sum_num_0 > i)[0]  # 找到模式缺省的i个对应的时空的下标
            middle_part_4d[index_has0, :, :, i] = 0

            # print('middle_part_4d[index_has0, :, :, i]middle_part_4d[index_has0, :, :, i]middle_part_4d[index_has0, :, :, i]start',i)
            # print(middle_part_4d)
            # print('middle_part_4d[index_has0, :, :, i]middle_part_4d[index_has0, :, :, i]middle_part_4d[index_has0, :, :, i]end',i)

        # end
        if middle_already is not None:
            middle_part_4d += middle_already
        return middle_part_4d
    else:
        middle_part_3d = middle_part
        if middle_already is not None:
            middle_part_3d += middle_already
        return middle_part_3d


def cut_sta_not_after(sta, time):
    if sta is None:
        return None, None
    else:
        not_after_part = sta.loc[sta["time"] <= time]
        after_part = sta.drop(not_after_part.index)
        return not_after_part, after_part


def get_veri_from_middle_result(para_whole, middle_veri):
    nead_hmfc_methods = ["ts", "bias", "ets", "fal_rate", "hit_rate", "mis_rate"]
    nead_abcd_methods = ["pc", "spc"]

    # 得到预报模式列表
    data_name_list = ["ob"]
    for model in para_whole["forecasts"]:
        data_name_list.append(model["name"])
    model_num = len(para_whole["forecasts"])

    veri_paras = para_whole["veri_set"]
    veri_result = {}
    group_set = para_whole["group_set"]
    for key in middle_veri.keys():
        data_array = middle_veri[key]["result"]
        shape = data_array.shape
        if len(shape) == 4:
            middle_veri_3d = np.zeros(shape[0:3])
            data_4d = data_array
            total_num = data_4d[:, :, 0, -1]
            num_0 = np.zeros(total_num.shape)
            num_0[total_num == 0] = 1
            sum_num_0 = np.sum(num_0, axis=1)
            # print(sum_num_0)

            for i in range(model_num):
                # 如果一个分类sta，它有i个模式中存在一个模式总和为0，即这些模式一直缺省
                # 则每个time的中间结果中，>i 个模式样本数为0的那个时次的结果会被全部置0
                index_has0 = np.where(sum_num_0 == i)[0]
                middle_veri_3d[index_has0, :, :] = data_4d[index_has0, :, :, i]
        else:
            middle_veri_3d = data_array

        dims = []
        coords = {}
        shape = []
        # group_set 的维度
        for coord in group_set.keys():
            if group_set[coord] != "fold":
                dims.append(coord)
                coords[coord] = group_set[coord]["group_name"]
                shape.append(len(coords[coord]))

        # 模式维度
        dims.append("member")
        coords["member"] = data_name_list[1:]
        shape.append(model_num)

        # 检验方法维度
        methods = veri_paras[key]["method"]
        dims.append("vmethod")
        coords["vmethod"] = methods
        shape.append(len(methods))

        # 检验方法维度
        one_veri_para = veri_paras[key]
        if ("para1" in one_veri_para.keys()):
            para1 = one_veri_para["para1"]
            if (para1 is not None):
                shape.append(len(para1))
                coords["para1"] = para1
                dims.append("para1")
        if ("para2" in one_veri_para.keys()):
            para2 = one_veri_para["para2"]
            if (para1 is not None):
                shape.append(len(para2))
                coords["para2"] = para2
                dims.append("para2")

        shape = tuple(shape)
        result0 = np.zeros(shape)
        result_f = xr.DataArray(result0, coords=coords, dims=dims)
        if methods[0] in nead_hmfc_methods:
            ngrade = len(one_veri_para["para1"])

            hit = middle_veri_3d[:, :, 1:(1 + ngrade)]
            mis = middle_veri_3d[:, :, (1 + ngrade):(1 + 2 * ngrade)]
            fal = middle_veri_3d[:, :, (1 + 2 * ngrade):(1 + 3 * ngrade)]
            cn = middle_veri_3d[:, :, (1 + 3 * ngrade):(1 + 4 * ngrade)]
        elif methods[0] in nead_abcd_methods:
            tn = middle_veri_3d[:, :, 0]
            na = middle_veri_3d[:, :, 1]
            nd = middle_veri_3d[:, :, 4]

        for method in methods:
            shape_xr = result_f.loc[dict(vmethod=method)].shape
            # print(shape_xr)
            if method.lower() == "ts":
                ts = hit / (mis + fal + hit + 1e-6)
                result_f.loc[dict(vmethod=method)] = ts.reshape(shape_xr)
            elif method.lower() == "bias":
                bias = (hit + fal) / (mis + hit + 1e-6)
                result_f.loc[dict(vmethod=method)] = bias.reshape(shape_xr)
            elif method.lower() == "pc":
                pc = (na + nd) / (tn + 1e-6)
                result_f.loc[dict(vmethod=method)] = pc.reshape(shape_xr)
            else:
                pass
        veri_result[key] = result_f
    return veri_result


# 通过指定参数获取站点信息
def get_sta_by_para(sta, para):
    sta1 = copy.deepcopy(sta)
    for key in para.keys():
        if key == "level":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_level_list(sta1, para[key])
        elif key == "time":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_time_list(sta1, para[key])
        elif key == "year":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_year_list(sta1, para[key])
        elif key == "month":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_month_list(sta1, para[key])
        elif key == "xun":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_xun_list(sta1, para[key])
        elif key == "hou":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_hou_list(sta1, para[key])
        elif key == "day":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_day_list(sta1, para[key])
        elif key == "hour":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_hour_list(sta1, para[key])
        elif key == "dtime":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dtime_list(sta1, para[key])
        elif key == "dday":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dday_list(sta1, para[key])
        elif key == "dhour":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dhour_list(sta1, para[key])
        elif key == "dminute":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dminute_list(sta1, para[key])
        elif key == "id":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_id_list(sta1, para[key])
        elif key == 'lon':
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_lon_range(sta1, para[key][0],
                                                                                                 para[key][1])
        elif key == 'lat':
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_lat_range(sta1, para[key][0],
                                                                                                 para[key][1])
        elif key == "alt":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_alt_range(sta1, para[key][0],
                                                                                                 para[key][1])
        else:

            if key in sta1.columns:
                # print(para[key])
                sta1 = sta1.loc[sta1[key].isin(para[key])]
            else:
                print("参数关键词不支持")
    return sta1


def close_time_grouping(group_dict):
    time_name_list = ['time', 'year', "month", "xun", "hou", "day", "hour", "dtime"]
    for key in group_dict:
        if key in time_name_list:
            group_dict[key] = 'fold'
    return group_dict


# 将数据按照规定的分组规则进行分成一个个小数据   并放到一个列表中
def group_sta(sta, para_group_set):
    para_dict_list_list = {}
    for key in para_group_set:
        if para_group_set[key] != "fold":
            para_dict_list_list[key] = para_group_set[key]["group"]
            # para_dict_list_list ={dtime:[[],[],[]],dim_type_region:[[],[],[]]}

    para_list_dict_list = para_array_to_list(0, para_dict_list_list)
    sta_list = []
    for para_dict_list in para_list_dict_list:
        sta1 = get_sta_by_para(sta, para_dict_list)
        sta_list.append(sta1)
        # print(len(sta_list))
    return sta_list, para_list_dict_list


def verification_with_complite_para(para):
    # 1#首先根据预报时效范围计算观测时效的范围,并且建立每个观测时间对应的多个起报时间和预报时效
    fo_start_time = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(para["fo_time_range"][0])
    fo_end_time = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(para["fo_time_range"][1])
    time_step = int(para["fo_time_range"][2][0:-1])
    time_type = para["fo_time_range"][2][-1]
    ob_time_dict = {}
    time1 = fo_start_time
    dtime_list = para["dtime"][0:-1]
    # 将观测时间与 （起报时+时效）通过字典 联系在一起   观测时间作为键  （起报时+时效）作为值
    # 放到ob_time_dict
    ob_time_and_fo_time_link(time1, fo_end_time, dtime_list, ob_time_dict, time_step)
    # ob_time_dict 结构 {实况时间：[[起报时间，dtime]]}
    # 设置中间检验结果
    # 2# 将检验标准分为两大类hmnf 与 pc_hmnf
    veri_group_num = len(para["veri_set"])  # 有几中检验标准 ，hmnf和 pc_hmnf#等
    middle_veri = {}
    for i in range(veri_group_num):
        middle_veri[i] = {}
        middle_veri[i]["para"] = get_middle_veri_para(para["veri_set"][i])
        middle_veri[i]["result"] = None  # 将改变后的字典赋值为 middle_veri
        # middle 结构为{i：{para：{name：veri_name，method:hfn/abcd,para1:grade_list,para1_Name:grade_name_list,plot_type:plot_type},result:value},,...........}
    # 3#划分区域 比如"新疆", "西北中东部", "华北", "东北", "黄淮江淮江南", "华南", "西南"
    # 区域之间对比   比如 实况新疆的数据 与预测新疆进行评分
    # 读取站点信息：
    station = nmc_verification.nmc_vf_base.io.read_stadata.read_from_micaps3(para["station"]["path"])
    station["data0"] = 9999
    ob_sta_all = None
    # 判断每个维度类型文件是否为固定文件
    para_dim_type = para["dim_type"]
    dim_type_num = 0
    dim_type_sta_all_dict = collections.OrderedDict()
    dim_type_sta1_list, dim_type_num = get_dim_type_info(para_dim_type, dim_type_sta_all_dict)


    fo_type_num = len(para["forecasts"])
    fo_sta_all_dict = collections.OrderedDict()
    for i in range(fo_type_num):
        # 存储所有预报站点数据的字典
        fo_sta_all_dict[i] = None
    # 筛选数据的阈值
    value_s = para["observation"]["valid"][0]  # 阈值开始值
    value_e = para["observation"]["valid"][1]  # 阈值结束值

    # 获取group_set 中hour的集合
    hour_list = get_time_set_in_group_set(para, 'hour')
    month_list = get_time_set_in_group_set(para, 'month')
    # 得到预报模式列表
    data_name_list = ["ob"]
    for model in para["forecasts"]:
        data_name_list.append(model["name"])
    time1 = fo_start_time - datetime.timedelta(hours=time_step)
    area_coords, area_shape = get_area_dims(para, is_fold_time=True)
    new_area_coords = copy.deepcopy(area_coords)
    area_coords['dim_type_region'] = ['、'.join(area_coord) for area_coord in new_area_coords['dim_type_region']]

    model_coords, model_shape = get_model_dims(data_name_list)
    wbl = 0
    # print(time1)
    while time1 <= fo_end_time:
        wbl += 1
        if (time_type == "h"):
            time1 = time1 + datetime.timedelta(hours=time_step)
        else:
            time1 = time1 + datetime.timedelta(minutes=time_step)
        # 判断时间是否在分析列表里
        if not time1.hour in hour_list:
            continue
        read_dim_type_data(dim_type_num, para_dim_type, dim_type_sta1_list, station, dtime_list, time1,
                           dim_type_sta_all_dict)
        # 读取观测
        # print(ob_time_dict)
        ob_sta_one_time_all, copy_ob_time_dict = read_ob_data(dtime_list, time1, ob_time_dict, para, station, value_s,
                                                              value_e)

        ob_time_dict = copy_ob_time_dict
        ob_sta_all = nmc_verification.nmc_vf_base.function.put_into_sta_data.join(ob_sta_all, ob_sta_one_time_all)
        # print(ob_sta_all)
        merge = None
        # 提取dim_type中数据
        for key in dim_type_sta_all_dict.keys():
            merge = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(merge,
                                                                                             dim_type_sta_all_dict[key])

        # 通过和dim数据merger来提取观测数据
        sta_before, sta_after = cut_sta_not_after(ob_sta_all, time1)
        ob_sta_all = sta_after

        if sta_before is None:
            continue
        merge = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(merge, sta_before)

        # 读取预报
        # print(merge)
        for dtime in dtime_list:
            new_merge = copy.deepcopy(merge)
            for i in range(fo_type_num):
                read_fo_data_on_one_time_and_one_dtime(para, i, time1, dtime, station, value_s, value_e,
                                                       fo_sta_all_dict)
            # print(fo_sta_all_dict)
            # 同一观测时间的数据
            # 通过和dim数据merger  来提取预报数据 # 将几种模式数据合并一起

            for key in fo_sta_all_dict.keys():
                new_merge = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(new_merge,
                                                                                                     fo_sta_all_dict[
                                                                                                         key])
            group_set = copy.deepcopy(para["group_set"])
            group_set = close_time_grouping(group_set)
            # print(group_set)
            sta_list, para_list_dict_list = group_sta(new_merge, group_set)

            total_and_hmfn_and_abcd_dataset = xr.Dataset()

            for key in middle_veri.keys():
                mpara = middle_veri[key]["para"]

                one_veri_set_para_coords, one_veri_set_para_shape = get_one_veri_set_para_dims(mpara)
                confusion_matrix_coords, confusion_matrix_shape = get_confusion_matrix_dims(mpara)

                mpara["sample_must_be_same"] = para["sample_must_be_same"]
                methods = mpara["method"]
                para1 = None
                if "para1" in mpara.keys():
                    para1 = mpara["para1"]
                para2 = None
                if "para2" in mpara.keys():
                    para2 = mpara["para2"]

                total_and_hmfn_or_abcd_data_set = get_middle_veri_result(sta_list, mpara, area_coords, area_shape,
                                                                         model_coords, model_shape,
                                                                         one_veri_set_para_coords,
                                                                         one_veri_set_para_shape,
                                                                         confusion_matrix_coords,
                                                                         confusion_matrix_shape)
                # print(total_and_hmfn_or_abcd_data_set)
                total_and_hmfn_and_abcd_dataset.update(total_and_hmfn_or_abcd_data_set)
            dtime = str(dtime)
            dtime = dtime.zfill(3)
            path = time1.strftime("%Y%m%d%H") + '.' + str(dtime) + '.nc'
            total_and_hmfn_and_abcd_dataset.to_netcdf(path)
            # total_and_hmfn_and_abcd_dataset.close()

            print('已经写入完毕')


def get_middle_veri_result(sta_list, para, area_coords, area_shape, model_coords, model_shape, one_veri_set_para_coords,
                           one_veri_set_para_shape, confusion_matrix_coords, confusion_matrix_shape):
    # para 是中间量检验的参数
    '''
    获取 一个hmfn或者abcd中的一个检验结果，和total_num 并将两个指标加入Data_set中
    :param sta_list:
    :param para:
    :param area_coords:
    :param area_shape:
    :param model_coords:
    :param model_shape:
    :param one_veri_set_para_coords:
    :param one_veri_set_para_shape:
    :param confusion_matrix_coords:
    :param confusion_matrix_shape:
    :return:
    '''

    sample_same = para["sample_must_be_same"]
    model_num = len(model_coords['member'])
    # print(data_name_list)
    data_names = copy.deepcopy(model_coords['member'])
    data_names.insert(0, 'ob')
    veri_list_4d = []
    total_num_list_list = []
    for sta in sta_list:
        total_num_list = []

        # 计算总的非9999样本数
        if sta is None or len(sta.index) == 0:
            for i in range(model_num):
                total_num_list.append(0)
        else:
            for i in range(model_num):
                model_name = model_coords['member'][i]
                fo = sta[model_name].values
                fo = fo[fo != 9999]
                total_num_list.append(len(fo))
        para1 = None
        para2 = None
        if "para1" in para.keys():
            para1 = para["para1"]
        if "para2" in para.keys():
            para2 = para["para2"]

        for vmethod in para["method"]:
            result = ver_one_groupsta_one_method(sta, vmethod, para1, para2, data_names,
                                                 sample_same)
        veri_list_4d.append(result)
        total_num_list_list.append(total_num_list)
    veri_array_4d = np.array(veri_list_4d)
    total_num_array_2d = np.array(total_num_list_list)
    shape_list = []
    for shape in [area_shape, model_shape, one_veri_set_para_shape, confusion_matrix_shape]:
        shape_list.extend(shape)
    shape_array = np.array(shape_list)
    shape_array = shape_array[shape_array != None]
    shape_list = list(shape_array)
    veri_array = veri_array_4d.reshape(shape_list)
    shape_list = copy.deepcopy(area_shape)
    total_num_shape = shape_list.extend(model_shape)
    total_num_array = total_num_array_2d.reshape(total_num_shape)
    dim_label, dim_name = dim_name_and_label_splice(area_coords, model_coords)

    total_array = xr.DataArray(total_num_array,
                               coords=dim_label,
                               dims=dim_name)

    ds1 = xr.Dataset({'total_num': total_array})
    dim_label, dim_name = dim_name_and_label_splice(area_coords, model_coords, one_veri_set_para_coords,
                                                    confusion_matrix_coords)

    if para["method"] == ['hmfn']:
        hmfn_array = xr.DataArray(veri_array_4d,
                                  coords=dim_label,
                                  dims=dim_name)
        ds2 = xr.Dataset({"hmfn_array": hmfn_array})
        ds1 = ds1.update(ds2)
    if para['method'] == ['abcd']:
        abcd_array = xr.DataArray(veri_array,
                                  coords=dim_label,
                                  dims=dim_name)
        ds2 = xr.Dataset({"abcd_array": abcd_array})
        ds1 = ds1.update(ds2)
    if para['method'] == ['tase']:
        tase_array = xr.DataArray(veri_array, coords=dim_label, dims=dim_name)
        ds2 = xr.Dataset({"tase_array": tase_array})
        ds1 = ds1.update(ds2)
    return ds1


def get_area_dims(para, is_fold_time=True):  # mpara, data_name_list,
    '''
    获取区域维度的名字和维度
    :param para: 最初的字典
    :param is_fold_time: 是否关闭time维度
    :return:
    '''
    group_set = copy.deepcopy(para['group_set'])
    # 获取维度信息
    if is_fold_time == True:
        group_set = close_time_grouping(group_set)
    coords = {}
    shape = []
    for coord in group_set.keys():
        if group_set[coord] != "fold":
            coords[coord] = group_set[coord]["group_name"]
            shape.append(len(coords[coord]))
    return coords, shape


def get_model_dims(data_name_list):
    # 获取模式维度的名字和形状
    '''

    :param data_name_list: 所有模式名字的list
    :return:
    '''
    shape = []
    coords = {}
    coords["member"] = data_name_list[1:]
    shape.append(len(coords['member']))
    return coords, shape


def get_one_veri_set_para_dims(one_veri_set_dict):
    '''
    获取一种veri_set的等级的name  和shape
    :param one_veri_set_dict:   一个veri_set 的字典比如   {
            "name": "ts_bias",
            "method": ["ts", "bias"],
            "para1": [0.1, 5, 10, 20],
            "para1Name": ["小雨", ">=5毫米", ">=10毫米", ">=20毫米"],
            "plot_type": "bar"
        }
    :return:
    '''
    shape = []
    coords = {}
    para1 = None
    if ("para1" in one_veri_set_dict.keys()):
        para1 = one_veri_set_dict["para1"]
        if (para1 is not None):
            shape.append(len(para1))
            coords["para1"] = para1
    if ("para2" in one_veri_set_dict.keys()):
        para2 = one_veri_set_dict["para2"]
        if (para1 is not None):
            shape.append(len(para2))
            coords["para2"] = para2

    return coords, shape


def get_confusion_matrix_dims(one_veri_set_dict):
    '''
    获取混淆矩阵的维度的名字  与hmfn   和 abcd 有关维度名字 和shape
    :param one_veri_set_dict: 一个veri_set 的字典比如   {
            "name": "ts_bias",
            "method": ["ts", "bias"],
            "para1": [0.1, 5, 10, 20],
            "para1Name": ["小雨", ">=5毫米", ">=10毫米", ">=20毫米"],
            "plot_type": "bar"
        }
    :return:
    '''
    coodrs = {}
    shape = []
    if one_veri_set_dict['method'] == ['hmfn']:
        coodrs = {'hmfn': ['hit', 'mis', 'fla', 'cn']}
        shape = [4]
    if one_veri_set_dict['method'] == ['abcd']:
        coodrs = {'abcd': ["na", "nb", "nc", "nd"]}
        shape = [4]
    if one_veri_set_dict['method'] == ['tase']:
        coodrs = {'tase': ['error_sum', 'total_absolute_error', 'sum_error_squares']}  # 总样本数、误差总和、绝对误差总和、误差平方总和
        shape = [3]
    return coodrs, shape


def ver_one_groupsta_one_method(sta, vmethod, para1, para2, data_names, sample_same):
    fo_num = len(data_names) - 1
    result = []
    if sta is not None and len(sta.index) > 0:
        # print(len(sta.index))
        data = copy.deepcopy(sta[data_names].values)  # 取出数据
        # print(data.shape)
        # print(data)
        if sample_same:
            # 首先判断全为9999的模式个数
            all_9999_num = 0
            for i in range(fo_num):
                fo = data[:, i + 1]
                index = np.where(fo != 9999)
                # 当一列全为9999时 all_9999_num +1
                if len(fo[fo != 9999]) == 0:
                    all_9999_num += 1

            # 判断每一行为9999的数目是否等于 all_9999_num
            is_9999 = np.zeros(data.shape)
            is_9999[data != 9999] = 0
            is_9999[data == 9999] = 1
            # 对于那些非全为9999的行

            sum_is_9999 = np.sum(is_9999, axis=1)
            # 每一行为9999的数目等于all_9999_num的数据取出
            index = np.where(sum_is_9999 == all_9999_num)[0]
            data = data[index, :]  # 每行为缺省的模式与全部缺省的列数一致。相当于把缺省模式大于 全部缺省的列的数据删除

    for i in range(fo_num):
        result_one_model = None
        if sta is not None and len(sta.index) > 0:

            ob = data[:, 0]
            fo = data[:, i + 1]
            if not sample_same:
                ob = ob[fo != 9999]
                fo = fo[fo != 9999]

            if len(fo) > 0 and fo[0] != 9999:
                # print(fo[fo>1])
                if vmethod == "hmfn":
                    result_one_model = np.array(list(nmc_verification.nmc_vf_method.yes_or_no.score.hmfn
                                                     (ob, fo, para1)))
                    result_one_model = result_one_model.T
                elif vmethod == 'abcd':
                    result_one_model = np.array(list(nmc_verification.nmc_vf_method.yes_or_no.score.hmfn_of_sunny_rainy
                                                     (ob, fo)))
                    result_one_model = result_one_model.T

                elif vmethod == 'tase':
                    e_sum = np.sum(fo - ob)
                    ae_sum = np.sum(np.abs(fo - ob))
                    se_sum = np.sum(np.square(fo - ob))
                    result_one_model = np.array([e_sum, ae_sum, se_sum])
                elif vmethod == 'toar':
                    pass

        if result_one_model is None:
            if vmethod == "hmfn":
                result_one_model = np.zeros((len(para1), 4))
            elif vmethod == 'abcd':
                result_one_model = np.zeros(4)
            elif vmethod == 'tase':
                result_one_model = np.zeros(3)

        re_list = result_one_model.tolist()
        result.append(re_list)

    return result


def dim_name_and_label_splice(*coords):
    '''
    拼接shape  和name
    :param coords:  多个维度的coords
    :return:
    '''
    dim_label = []
    dim_name = []
    for dim in coords:
        for key in dim.keys():
            dim_label.append(dim[key])
            dim_name.append(key)
    return dim_label, dim_name


def read_ob_data(dtime_list, time1, ob_time_dict, para, station, value_s, value_e):
    ob_sta_all = None
    copy_ob_time_dict = copy.deepcopy(ob_time_dict)
    for dtime in dtime_list:
        ob_time = time1 + datetime.timedelta(hours=dtime)
        # print(ob_time)
        # print(ob_time_dict.keys())
        if ob_time in ob_time_dict.keys():
            path = nmc_verification.nmc_vf_base.tool.path_tools.get_path(para["observation"]["path"], ob_time)
            ob_sta = nmc_verification.nmc_vf_base.io.read_stadata.read_from_micaps3(path, station=station)

            if ob_sta is not None:
                ob_sta = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_value_range(ob_sta,
                                                                                                         value_s,
                                                                                                         value_e)
                time_dtime_list = copy_ob_time_dict[ob_time]
                for time_dtime in time_dtime_list:
                    # print(time_dtime)
                    ob_sta1 = copy.deepcopy(ob_sta)
                    time_p = time_dtime[0]
                    dtime = time_dtime[1]
                    nmc_verification.nmc_vf_base.set_time_dtime_level_name(ob_sta1, time=time_p, dtime=dtime,
                                                                           level=0, data_name="ob")
                    ob_sta_all = nmc_verification.nmc_vf_base.function.put_into_sta_data.join(ob_sta_all, ob_sta1)
            copy_ob_time_dict.pop(ob_time)

    return ob_sta_all, copy_ob_time_dict


def read_dim_type_data(dim_type_num, para_dim_type, dim_type_sta1_list, station, dtime_list, time1,
                       dim_type_sta_all_dict):
    for i in range(dim_type_num):

        sta = None
        if para_dim_type[i]["fix"]:

            if len(dim_type_sta1_list) > i:
                path = para_dim_type[i]["path"]
                if para_dim_type[i]["type"] == "grid_data":
                    grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_nc(path)
                    if grd is not None:
                        # 将格点插值到站点上
                        sta = nmc_verification.nmc_vf_base.function.gxy_sxy.interpolation_nearest(grd, station)
                else:
                    sta = nmc_verification.nmc_vf_base.io.read_stadata.read_from_micaps3(path, station)
            else:
                sta = copy.deepcopy(dim_type_sta1_list[i])
                dim_type_sta1_list.append(sta)
        else:
            dir = para_dim_type[i]["path"]
            path = nmc_verification.nmc_vf_base.tool.path_tools.get_path(dir, time1)
            if para_dim_type[i]["type"] == "grid_data":
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_nc(path)
                sta = nmc_verification.nmc_vf_base.function.gxy_sxy.interpolation_nearest(grd, station)
            else:
                sta = nmc_verification.nmc_vf_base.io.read_stadata.read_from_micaps3(path, station)

        for dtime in dtime_list:
            sta1 = copy.deepcopy(sta)

            nmc_verification.nmc_vf_base.set_time_dtime_level_name(sta1, time=time1, dtime=dtime, level=0,
                                                                   data_name=para_dim_type[i]["name"])
            dim_type_sta_all_dict[i] = nmc_verification.nmc_vf_base.function.put_into_sta_data.join(
                dim_type_sta_all_dict[i], sta1)


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


def read_fo_data_on_one_time_and_one_dtime(para, model_id, time1, dtime, station, value_s, value_e,
                                           fo_sta_on_one_time_and_onedtime_all_dict):
    '''

    :param para:
    :param model_id:
    :param time1:
    :param dtime:
    :param station:
    :param value_s:
    :param value_e:
    :param fo_sta_on_one_time_and_onedtime_all_dict:
    :return:
    '''
    i = model_id
    one_fo_para = para["forecasts"][i]
    data_name = one_fo_para["name"]

    range_b = one_fo_para["fo_time_move_back"]
    # 读取回退时间
    fo_time_move_backs = np.arange(range_b[0], range_b[1], range_b[2]).tolist()
    find_file = False
    path = None
    for move_back in fo_time_move_backs:
        time_model = time1 - datetime.timedelta(hours=move_back)
        dtime_model_max = dtime + move_back
        if one_fo_para["ob_time_need_be_same"]:
            dtime_model_try = [dtime_model_max]
        else:
            dtime_model_try = np.arange(dtime_model_max, -1, -1).tolist()
        for dtime_model in dtime_model_try:
            dtime_model_int = int(dtime_model)
            path = nmc_verification.nmc_vf_base.tool.path_tools.get_path(one_fo_para["path"], time_model,
                                                                         dtime_model_int)
            if os.path.exists(path):
                find_file = True
                break
        if find_file:
            break
    fo_sta = None
    if find_file:
        if one_fo_para["type"] == "sta_data":
            fo_sta = nmc_verification.nmc_vf_base.io.read_stadata.read_from_micaps3(path, station)
        else:
            grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_nc(path)
            if grd is not None:
                fo_sta = nmc_verification.nmc_vf_base.function.gxy_sxy.interpolation_nearest(grd, station)
                fo_sta = nmc_verification.nmc_vf_base.function.sxy_sxy.set_data_to(fo_sta, station)
    if fo_sta is None:
        fo_sta = copy.deepcopy(station)
    fo_sta = nmc_verification.nmc_vf_base.function.sxy_sxy.set_value_out_9999(fo_sta, value_s, value_e)
    nmc_verification.nmc_vf_base.set_time_dtime_level_name(fo_sta, level=0, time=time1, dtime=dtime,
                                                           data_name=data_name)
    fo_sta_on_one_time_and_onedtime_all_dict[i] = fo_sta


def get_dim_type_info(para_dim_type, dim_type_sta_all_dict):
    if para_dim_type is not None:
        dim_type_num = len(para_dim_type)
        dim_type_sta1_list = []
        for i in range(dim_type_num):
            dim_type_sta1_list.append(None)
            path = para_dim_type[i]["path"]
            fix = True
            if path.find("YY") > 0:
                fix = False
            if path.find("MM") > 0:
                fix = False
            if path.find("DD") > 0:
                fix = False
            if path.find("HH") > 0:
                fix = False
            para_dim_type[i]["fix"] = fix

        # print(para_dim_type)
        for i in range(dim_type_num):
            dim_type_sta_all_dict[i] = None
        return dim_type_sta1_list, dim_type_num
    # fo_type_num ：预报数据模式个数


def get_time_set_in_group_set(para, time_name):
    if para["group_set"][time_name] != "fold":
        list_list = para["group_set"][time_name]["group"]
        list1 = []
        for list0 in list_list:
            list1.extend(list0)
        time_list = list(set(list1))
    else:
        if time_name == 'hour':
            time_list = np.arange(24).tolist()
        else:
            time_list = np.arange(1, 13).tolist()

    return time_list
