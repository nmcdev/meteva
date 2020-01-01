import nmc_verification
import datetime


def me_muti_model(ob_sta, fo_sta_list):
    '''
    me_muti_model 求多模式  me——误差平均值评分
    --------------------------------------------
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :return:
    '''
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)
    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    me_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = intersection_of_data[fo_of_data].values
        me_score = nmc_verification.nmc_vf_method.continuous.score.me(ob_data, fo_of_data)
        me_list.append(me_score)

    return me_list


def mae_muti_model(ob_sta, fo_sta_list):
    '''
    mae_muti_model 求多模式  mae——平均绝对值误差
    ---------------------------------------------
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :return:
    '''
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    mae_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = intersection_of_data[fo_of_data].values
        mae_score = nmc_verification.nmc_vf_method.continuous.score.mae(ob_data, fo_of_data)
        mae_list.append(mae_score)

    return mae_list


def mse_muti_model(ob_sta, fo_sta_list):
    '''
    mae_muti_model 求多模式  mae——平均绝对值误差
    ------------------------------------------------
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :return:
    '''
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    mse_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = intersection_of_data[fo_of_data].values
        mse_score = nmc_verification.nmc_vf_method.continuous.score.mse(ob_data, fo_of_data)
        mse_list.append(mse_score)

    return mse_list


def rmse_muti_model(ob_sta, fo_sta_list):
    '''
    rmse_muti_model 求多模式  rmse——均方根误差
    ------------------------------------------------
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :return:
    '''
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    rmse_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = intersection_of_data[fo_of_data].values
        rmse_score = nmc_verification.nmc_vf_method.continuous.score.rmse(ob_data, fo_of_data)
        rmse_list.append(rmse_score)

    return rmse_list


def bias_muti_model(ob_sta, fo_sta_list):
    '''
    bias_muti_model 求多模式  bias——预测数据和实况数据的平均值的比
    ------------------------------------------------
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :return:
    '''
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    bias_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = intersection_of_data[fo_of_data].values
        bias_score = nmc_verification.nmc_vf_method.continuous.score.bias(ob_data, fo_of_data)
        bias_list.append(bias_score)

    return bias_list


def corr_muti_model(ob_sta, fo_sta_list):
    '''
    corr_muti_model 求多模式  corr——实况数据还和预测数据之间的相关系数
    ------------------------------------------------
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :return:
    '''
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    corr_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = intersection_of_data[fo_of_data].values
        corr_score = nmc_verification.nmc_vf_method.continuous.score.corr(ob_data, fo_of_data)
        corr_list.append(corr_score)

    return corr_list


import copy


def mre_muti_model(ob_sta, fo_sta_list):
    '''
    are_muti_model  多模式下 are——平均绝对值误差
    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :return:
    '''
    fo_sta_list.append(ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_id_and_obTime(fo_sta_list)

    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    are_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = intersection_of_data[fo_of_data].values
        are_score = nmc_verification.nmc_vf_method.continuous.score.mre(ob_data, fo_of_data)
        are_list.append(are_score)

    return are_list
