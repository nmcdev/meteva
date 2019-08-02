import nmc_verification
import datetime


def accuracy_muti_model(ob_sta, fo_sta_list, grade_list):
    intersection_of_data = fo_sta_list[0]
    for i in range(1, len(fo_sta_list) - 1):
        intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
            intersection_of_data, fo_sta_list[i])
    intersection_of_data['dtime'] = intersection_of_data['dtime'].map(lambda x: datetime.timedelta(hours=x))
    intersection_of_data['time'] = intersection_of_data['time'] + intersection_of_data['dtime']
    intersection_of_data['dtime'] = 0
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
        intersection_of_data, ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
        intersection_of_data, ob_sta)
    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    accuracy_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        accuracy_score = nmc_verification.nmc_vf_method.multi_category.score.accuracy(ob_data, fo_of_data, grade_list)
        accuracy_list.append(accuracy_score)

    return accuracy_list


def hss_muti_model(ob_sta, fo_sta_list, grade_list):
    intersection_of_data = fo_sta_list[0]
    for i in range(1, len(fo_sta_list) - 1):
        intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
            intersection_of_data, fo_sta_list[i])
    intersection_of_data['dtime'] = intersection_of_data['dtime'].map(lambda x: datetime.timedelta(hours=x))
    intersection_of_data['time'] = intersection_of_data['time'] + intersection_of_data['dtime']
    intersection_of_data['dtime'] = 0
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
        intersection_of_data, ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
        intersection_of_data, ob_sta)
    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    hss_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        hss_score = nmc_verification.nmc_vf_method.multi_category.score.hss(ob_data, fo_of_data, grade_list)
        hss_list.append(hss_score)
    return hss_list


def hk_muti_model(ob_sta, fo_sta_list, grade_list):
    intersection_of_data = fo_sta_list[0]
    for i in range(1, len(fo_sta_list) - 1):
        intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
            intersection_of_data, fo_sta_list[i])
    intersection_of_data['dtime'] = intersection_of_data['dtime'].map(lambda x: datetime.timedelta(hours=x))
    intersection_of_data['time'] = intersection_of_data['time'] + intersection_of_data['dtime']
    intersection_of_data['dtime'] = 0
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
        intersection_of_data, ob_sta)
    intersection_of_data = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(
        intersection_of_data, ob_sta)
    ob_data = intersection_of_data.iloc[:, -1]
    ob_data = ob_data.values
    hk_list = []
    for fo_of_data in intersection_of_data.iloc[:, 7:-1]:
        fo_of_data = fo_of_data.values
        hk_score = nmc_verification.nmc_vf_method.multi_category.score.hk(ob_data, fo_of_data, grade_list)
        hk_list.append(hk_score)

    return hk_list
