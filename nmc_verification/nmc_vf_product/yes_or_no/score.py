import nmc_verification
import numpy as np
import pandas as pd
import datetime


# ts_array = ts_array.reshape((len(fo_sta_list), len(grade_list)))
# TS评分
def ts_muti_model(ob_sta, fo_sta_list, grade_list):
    '''
    求多模式 ts
    :param ob_sta: 一个实况数据  类型  dataframe
    :param fo_sta_list:  多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :param grade_list: 等级  列表list
    :return:
    '''

    # 将 多个模式的预报数据合并为一个dataframe  并 将起报时和时效处理   起报时 + 时效  = 实况_起报时
    # 实况_时效 = 0
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)
    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    ts_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        ts = nmc_verification.nmc_vf_method.yes_or_no.score.ts(ob_data, fo_of_data, grade_list)
        ts_list.append(ts)
    return ts_list


# 计算偏差值
def bias_muti_model(ob_sta, fo_sta_list, grade_list):
    '''
    bias_muti_model 求多模式 bias
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :param grade_list: 等级  列表list
    :return:
    '''

    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    bias_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        bias_score = nmc_verification.nmc_vf_method.yes_or_no.score.bias(ob_data, fo_of_data, grade_list)
        bias_list.append(bias_score)

    return bias_list


def mis_rate_muti_model(ob_sta, fo_sta_list, grade_list):
    '''
    mis_rate_muti_model 求多模式 mis_rate   漏报率
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :param grade_list: 等级  列表list
    :return:
    '''
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    mis_rate_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        mis_rate_score = nmc_verification.nmc_vf_method.yes_or_no.score.mis_rate(ob_data, fo_of_data, grade_list)
        mis_rate_list.append(mis_rate_score)

    return mis_rate_list


def fal_rate_muti_model(ob_sta, fo_sta_list, grade_list):
    '''
    fal_rate_muti_model 求多模式 fal_rate   漏报率
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :param grade_list: 等级  列表list
    :return:
    '''
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    fal_rate_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        fal_rate_score = nmc_verification.nmc_vf_method.yes_or_no.score.fal_rate(ob_data, fo_of_data, grade_list)
        fal_rate_list.append(fal_rate_score)
    return fal_rate_list


# hmfc命中，漏报，空报，正确否定
# def hmfn(sta, grade_list):
#     data_names = nmc_verification.nmc_vf_base.basicdata.get_undim_data_names(sta)
#     ob = sta[data_names[0]].values
#     fo_num = len(data_names) - 1
#     re_list = []
#     for i in range(fo_num):
#         fo = sta[data_names[i + 1]].values
#         hit, mis, fal, cn = nmc_verification.nmc_vf_method.yes_or_no.score.hmfn(ob, fo, grade_list)
#         re_list.append(hit.tolist())
#         re_list.append(mis.tolist())
#         re_list.append(fal.tolist())
#         re_list.append(cn.tolist())
#     hmfn_array = np.array(re_list)
#     hmfn_array = hmfn_array.reshape(4, fo_num, len(grade_list))
#     return hmfn_array
def hmfn_muti_model(ob_sta, fo_sta_list, grade_list):
    '''
    bias_muti_model 求多模式 hmfn
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :param grade_list: 等级  列表list
    :return:
    '''
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    re_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        hit, mis, fal, cn = nmc_verification.nmc_vf_method.yes_or_no.score.hmfn(ob_data, fo_of_data, grade_list)
        re_list.append(hit.tolist())
        re_list.append(mis.tolist())
        re_list.append(fal.tolist())
        re_list.append(cn.tolist())
    return re_list


# abcd,晴雨准确率计算联立表，命中，漏报，空报，正确否定
# def abcd(sta):
#     data_names = nmc_verification.nmc_vf_base.basicdata.get_undim_data_names(sta)
#     ob = sta[data_names[0]].values
#     fo_num = len(data_names) - 1
#     re_list = []
#     for i in range(fo_num):
#         fo = sta[data_names[i + 1]].values
#         hit, mis, fal, cn = nmc_verification.nmc_vf_method.yes_or_no.score.abcd_of_sunny_rainy(ob, fo)
#         re_list.append(hit.tolist())
#         re_list.append(mis.tolist())
#         re_list.append(fal.tolist())
#         re_list.append(cn.tolist())
#     abcd_array = np.array(re_list)
#     abcd_array = abcd_array.reshape(4, fo_num)
#     return abcd_array
def abcd_muti_model(ob_sta, fo_sta_list):
    '''
    bias_muti_model 求多模式 abcd 晴雨准确率
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :return:
    '''

    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    re_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        hit, mis, fal, cn = nmc_verification.nmc_vf_method.yes_or_no.score.abcd_of_sunny_rainy(ob_data, fo_of_data)
        re_list.append(hit.tolist())
        re_list.append(mis.tolist())
        re_list.append(fal.tolist())
        re_list.append(cn.tolist())
    return re_list


def pc_of_sunny_rainy_muti_model(ob_sta, fo_sta_list):
    '''
        pc_of_sunny_rainy_muti_model 求多模式    pc晴雨准确率
        :param ob_sta:  一个实况数据  类型  dataframe
        :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
        每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
        :return:
        '''
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    re_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        hit, mis, fal, cn = nmc_verification.nmc_vf_method.yes_or_no.score.pc_of_sunny_rainy(ob_data, fo_of_data)
        re_list.append(hit.tolist())
        re_list.append(mis.tolist())
        re_list.append(fal.tolist())
        re_list.append(cn.tolist())
    return re_list


def hit_muti_model(ob_sta, fo_sta_list, grade_list):
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    mis_rate_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        mis_rate_score = nmc_verification.nmc_vf_method.yes_or_no.score.hit_rate(ob_data, fo_of_data, grade_list)
        mis_rate_list.append(mis_rate_score)

    return mis_rate_list


def bias_extend_muti_model(ob_sta, fo_sta_list, grade_list):
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    bias_extend_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        bias_extend_score = nmc_verification.nmc_vf_method.yes_or_no.score.bias_extend(ob_data, fo_of_data, grade_list)
        bias_extend_list.append(bias_extend_score)
    return bias_extend_list


def ets_muti_model(ob_sta, fo_sta_list, grade_list):
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    ets_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        ets_score = nmc_verification.nmc_vf_method.yes_or_no.score.ets(ob_data, fo_of_data, grade_list)
        ets_list.append(ets_score)
    return ets_list
