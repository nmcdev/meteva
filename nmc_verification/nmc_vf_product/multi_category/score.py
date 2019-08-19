import nmc_verification
import datetime


# 准确率
def accuracy_muti_model(ob_sta, fo_sta_list, grade_list):
    '''
    accuracy_muti_model  多模式下 准确率
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
    accuracy_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = intersection_of_data[fo_of_data].values
        accuracy_score = nmc_verification.nmc_vf_method.multi_category.score.accuracy(ob_data, fo_of_data, grade_list)
        accuracy_list.append(accuracy_score)

    return accuracy_list


def hss_muti_model(ob_sta, fo_sta_list, grade_list):
    '''
    accuracy_muti_model  多模式下 hss 评分
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
    hss_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = intersection_of_data[fo_of_data].values
        hss_score = nmc_verification.nmc_vf_method.multi_category.score.hss(ob_data, fo_of_data, grade_list)
        hss_list.append(hss_score)
    return hss_list


def hk_muti_model(ob_sta, fo_sta_list, grade_list):
    '''
    accuracy_muti_model  多模式下 hk评分
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
    hk_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = intersection_of_data[fo_of_data].values
        hk_score = nmc_verification.nmc_vf_method.multi_category.score.hk(ob_data, fo_of_data, grade_list)
        hk_list.append(hk_score)

    return hk_list
