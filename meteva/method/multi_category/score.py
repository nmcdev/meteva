import meteva
import numpy as np
from meteva.base import IV
from meteva.method.yes_or_no.score import ts_hfmc, ets_hfmc, bias_hfmc, far_hfmc, mr_hfmc,pod_hfmc,sr_hfmc,pofd_hfmc
import math


def tc(ob, fo, grade_list=None):
    '''
    accuracy 求多分类预报准确率
    :param ob: 实况数据 不确定维numpy
    :param fo:  预测数据 不确定维numpy
    :param grade_list:等级，如果grade_list= None则ob和fo里的值代表类别，否则，根据grade_list来进行分类
    :return: 返回一维数组，包括（总样本数，正确数）
    '''
    tc_array_list = []
    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])

    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    for line in range(new_Fo_shape[0]):
        # 多分类预报准确率
        if grade_list is None:
            # ob 和fo是不确定维的numpy数组，其中每个值是代表分类的类别
            ob1 = ob.reshape((-1))
            fo1 = new_Fo[line, :].reshape((-1))
        else:
            ob1 = np.zeros_like(ob)
            fo1 = np.zeros_like(new_Fo[line, :])
            # ob 和fo 是连续的变量，通过 threshold_list 将ob 和fo划分成连续的等级之后再计算等级准确性
            for index in range(len(grade_list) - 1):
                ob_index_list = np.where((grade_list[index] <= ob) & (ob < grade_list[index + 1]))
                ob1[ob_index_list] = index + 1
                fo_index_list = np.where(
                    (grade_list[index] <= new_Fo[line, :]) & (new_Fo[line, :] < grade_list[index + 1]))
                fo1[fo_index_list] = index + 1
            ob_index_list = np.where(grade_list[-1] <= ob)
            ob1[ob_index_list] = len(grade_list)
            fo_index_list = np.where(grade_list[-1] <= new_Fo[line, :])
            fo1[fo_index_list] = len(grade_list)
        correct_num = np.sum(fo1 == ob1)

        tc_array_list.append(np.array([ob.size, correct_num]))
    tc_array = np.array(tc_array_list)
    shape = list(Fo_shape[:ind])
    shape.append(2)
    tc_array = tc_array.reshape(shape)
    return tc_array


def tcof(ob, fo, grade_list=None):
    '''
    多分类评分中间统计量
    :param ob: 实况数据 任意维numpy数组
    :param fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 一个从小到大排列的实数列表，以其中列出的数值划分出的多个区间作为分类标签。
    :return: 一维数组，包括（总样本数，正确样本数，观测的样本数、预报的样本数）
    '''
    tcof_list = []
    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])

    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    if (grade_list is None):
        fo_list = list(set(fo.reshape((-1)).tolist()))
        ob_list = list(set(fo.reshape((-1)).tolist()))
        fo_list.extend(ob_list)
        grade_list = list(set(fo_list))
        grade_list.sort()
        if len(grade_list) > 30:
            print("自动识别的样本类别超过30种，判断样本为连续型变量，grade_list不能缺省")
            return
    for line in range(new_Fo_shape[0]):
        tc1 = tc(ob, new_Fo[line, :],grade_list=grade_list)
        ft = meteva.method.multi_category.table.frequency_table(ob, new_Fo[line, :], grade_list=grade_list)
        tcof1 = np.zeros((len(grade_list) + 2, 2))
        tcof1[0, :] = tc1
        tcof1[1:, :] = ft.T
        tcof_list.append(tcof1)

    tcof_array = np.array(tcof_list)

    shape = list(Fo_shape[:ind])
    shape_list = [len(grade_list) + 2, 2]
    shape.extend(shape_list)
    tcof_array = tcof_array.reshape(shape)

    return tcof_array


def hfmc_grade(ob, fo, grade_list):
    '''
    多分类评分中间统计量
    :param ob: 实况数据 任意维numpy数组
    :param fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 一个从小到大排列的实数列表，以其中列出的数值划分出的多个区间作为分类标签。
    :return: 一维数组，包括（总样本数，正确样本数，观测的样本数、预报的样本数）
    '''
    hfmc_multi_list = []
    Ob_shape = ob.shape
    Fo_shape = fo.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return

    total_count = ob.size
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    new_grade_list = None
    for line in range(new_Fo_shape[0]):

        new_grade_list = grade_list
        hfmc_m = np.zeros((len(grade_list) + 1, 4))
        gle = [-1e300]
        gle.extend(grade_list)
        gle.append(1e300)
        for i in range(len(gle) - 1):
            #命中样本
            hit_index_list = np.where(
                (ob >= gle[i]) & (ob < gle[i + 1]) & (new_Fo[line, :] >= gle[i]) & (new_Fo[line, :] < gle[i + 1]))
            hfmc_m[i, 0] = len(hit_index_list[0])

            #空报样本，预报处于某个区间，而观测低于该区间
            fal_index_list = np.where(
                (ob < gle[i]) & (new_Fo[line, :] >= gle[i]) & (new_Fo[line, :] < gle[i + 1]))
            hfmc_m[i, 1] = len(fal_index_list[0])

            # 漏报样本，观测处于某个区间，而预测低于该区间
            mis_index_list = np.where(
                (ob >= gle[i]) & (ob < gle[i + 1]) & (new_Fo[line, :] < gle[i]))
            hfmc_m[i, 2] = len(mis_index_list[0])

            #正确无
            nd_list = np.where((ob < gle[i]) & (new_Fo[line, :] < gle[i]))
            hfmc_m[i, 3] = len(nd_list[0])
        hfmc_multi_list.append(hfmc_m)
    hfmc_multi_array = np.array(hfmc_multi_list)
    shape = list(Fo_shape[:ind])
    a = len(new_grade_list)
    if (grade_list is not None):
        a+=1
    shape.append(a)
    shape.append(4)
    hfmc_multi_array = hfmc_multi_array.reshape(shape)
    return hfmc_multi_array


def hfmc_multi(ob, fo, grade_list=None):
    '''
    多分类评分中间统计量
    :param ob: 实况数据 任意维numpy数组
    :param fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 一个从小到大排列的实数列表，以其中列出的数值划分出的多个区间作为分类标签。
    :return: 一维数组，包括（总样本数，正确样本数，观测的样本数、预报的样本数）
    '''
    hfmc_multi_list = []
    Ob_shape = ob.shape
    Fo_shape = fo.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return

    total_count = ob.size
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    new_grade_list = None
    for line in range(new_Fo_shape[0]):

        if (grade_list is None):
            grade_list1 = list(set(ob.flatten()))
            grade_list2 = list(set(fo.flatten()))
            grade_list1.extend(grade_list2)
            new_grade_list = list(set(grade_list1))
            new_grade_list.sort()
            if len(new_grade_list) > 30:
                print("自动识别的样本类别超过30种，判断样本为连续型变量，grade_list不能缺省")
                return
            hfmc_m = np.zeros((len(new_grade_list), 4))
            for i in range(len(new_grade_list)):
                grade = new_grade_list[i]
                hit_index_list = np.where((ob == grade) & (new_Fo[line, :] == grade))

                hfmc_m[i, 0] = len(hit_index_list[0])
                fal_index_list = np.where((ob != grade) & (new_Fo[line, :] == grade))
                hfmc_m[i, 1] = len(fal_index_list[0])
                mis_index_list = np.where((ob == grade) & (new_Fo[line, :] != grade))
                hfmc_m[i, 2] = len(mis_index_list[0])
                hfmc_m[i, 3] = total_count - hfmc_m[i, 0] - hfmc_m[i, 1] - hfmc_m[i, 2]
        else:
            new_grade_list = grade_list
            hfmc_m = np.zeros((len(grade_list) + 1, 4))
            gle = [-1e300]
            gle.extend(grade_list)
            gle.append(1e300)
            for i in range(len(gle) - 1):

                #命中样本
                hit_index_list = np.where(
                    (ob >= gle[i]) & (ob < gle[i + 1]) & (new_Fo[line, :] >= gle[i]) & (new_Fo[line, :] < gle[i + 1]))
                hfmc_m[i, 0] = len(hit_index_list[0])

                #空报样本，预报处于某个区间，而观测低于该区间
                fal_index_list = np.where(((ob < gle[i]) | (ob >= gle[i + 1])) & (new_Fo[line, :] >= gle[i]) & (new_Fo[line, :] < gle[i + 1]))
                hfmc_m[i, 1] = len(fal_index_list[0])
                # 漏报样本，观测处于某个区间，而预测低于该区间
                mis_index_list = np.where((ob >= gle[i]) & (ob < gle[i + 1]) & ((new_Fo[line, :] < gle[i]) | (new_Fo[line, :] >= gle[i + 1])))
                hfmc_m[i, 2] = len(mis_index_list[0])

                #正确无
                hfmc_m[i, 3] = total_count - hfmc_m[i, 0] - hfmc_m[i, 1] - hfmc_m[i, 2]
        hfmc_multi_list.append(hfmc_m)
    hfmc_multi_array = np.array(hfmc_multi_list)
    shape = list(Fo_shape[:ind])
    a = len(new_grade_list)
    if (grade_list is not None):
        a+=1
    shape.append(a)
    shape.append(4)
    hfmc_multi_array = hfmc_multi_array.reshape(shape)

    return hfmc_multi_array


def accuracy(ob, fo, grade_list=None):
    '''
    accuracy 求多分类预报准确率
    :param ob: 实况数据 任意维numpy数组
    :param fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 如果该参数为None，观测或预报值出现过的值都作为分类标记.
    如果该参数不为None，它必须是一个从小到大排列的实数，以其中列出的数值划分出的多个区间作为分类标签。
    对于预报和观测值不为整数的情况，grade_list 不能设置为None。
    :return: 0-1的实数，0代表无技巧，最优预报为1
    '''
    tc1 = tc(ob,fo,grade_list)
    total_count = tc1[...,0]
    correct_count = tc1[...,1]
    accuracy_score = correct_count / total_count
    return accuracy_score


def accuracy_tc(tc_array):
    '''
    :param tc_array:
    :return:
    '''
    total_count = tc_array[..., 0]
    correct_count = tc_array[..., 1]
    accuracy_score = correct_count / total_count
    return accuracy_score


def accuracy_tcof(tcof_array):
    '''

    :param tcof_array:
    :return:
    '''
    total_count = tcof_array[..., 0, 0]
    correct_count = tcof_array[..., 0, 1]
    accuracy_score = correct_count / total_count
    return accuracy_score


def ts_grade(ob,fo,grade_list):
    '''
    分级ts评分
    :param ob:
    :param fo:
    :param grade_list:
    :return:
    '''
    hfmc_array = hfmc_grade(ob, fo, grade_list)
    ts_array = ts_hfmc(hfmc_array)
    return ts_array


def ets_grade(ob, fo, grade_list):
    hfmc_array = hfmc_grade(ob, fo, grade_list)
    ets_array = ets_hfmc(hfmc_array)
    return ets_array


def bias_grade(ob, fo, grade_list):
    hfmc_array = hfmc_grade(ob, fo, grade_list)
    bias_array = bias_hfmc(hfmc_array)
    return bias_array


def mr_grade(ob, fo, grade_list):
    hfmc_array = hfmc_grade(ob, fo, grade_list)
    mr_array = mr_hfmc(hfmc_array)
    return mr_array


def far_grade(ob, fo, grade_list):
    hfmc_array = hfmc_grade(ob, fo, grade_list)
    far_array = far_hfmc(hfmc_array)
    return far_array

def pod_grade(ob,fo,grade_list):
    hfmc_array = hfmc_grade(ob, fo, grade_list)
    pod_array = pod_hfmc(hfmc_array)
    return pod_array

def pofd_grade(ob,fo,grade_list):
    hfmc_array = hfmc_grade(ob, fo, grade_list)
    pofd_array = pofd_hfmc(hfmc_array)
    return pofd_array

def sr_grade(ob,fo,grade_list):
    hfmc_array = hfmc_grade(ob, fo, grade_list)
    sr_array = sr_hfmc(hfmc_array)
    return sr_array


def ts_multi(ob, fo, grade_list=None):
    hfmc_array = hfmc_multi(ob, fo, grade_list)
    ts_array = ts_hfmc(hfmc_array)
    return ts_array


def ets_multi(ob, fo, grade_list=None):
    hfmc_array = hfmc_multi(ob, fo, grade_list)
    ets_array = ets_hfmc(hfmc_array)
    return ets_array


def bias_multi(ob, fo, grade_list=None):
    hfmc_array = hfmc_multi(ob, fo, grade_list)
    bias_array = bias_hfmc(hfmc_array)
    return bias_array


def mr_multi(ob, fo, grade_list=None):
    hfmc_array = hfmc_multi(ob, fo, grade_list)
    mr_array = mr_hfmc(hfmc_array)
    return mr_array


def far_multi(ob, fo, grade_list=None):
    hfmc_array = hfmc_multi(ob, fo, grade_list)
    far_array = far_hfmc(hfmc_array)
    return far_array


def pod_multi(ob,fo,grade_list):
    hfmc_array = hfmc_multi(ob, fo, grade_list)
    pod_array = pod_hfmc(hfmc_array)
    return pod_array

def pofd_multi(ob,fo,grade_list):
    hfmc_array = hfmc_multi(ob, fo, grade_list)
    pofd_array = pofd_hfmc(hfmc_array)
    return pofd_array

def sr_multi(ob,fo,grade_list):
    hfmc_array = hfmc_multi(ob, fo, grade_list)
    sr_array = sr_hfmc(hfmc_array)
    return sr_array


def hss(ob, fo, grade_list=None):
    '''
    hss heidke技能得分,它表现实际的预报的分类准确性相对于随机分类达到的准确性的技巧
    :param ob: 实况数据 任意维numpy数组
    :param fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 如果该参数为None，观测或预报值出现过的值都作为分类标记.
    如果该参数不为None，它必须是一个从小到大排列的实数，以其中列出的数值划分出的多个区间作为分类标签。
    对于预报和观测值不为整数的情况，grade_list 不能设置为None。
    :return:
    '''
    Ob_shape = ob.shape
    Fo_shape = fo.shape
    hss_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')

        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    for line in range(new_Fo_shape[0]):

        conf_mx = meteva.method.multi_category.table.contingency_table_multicategory(ob, new_Fo[line, :], grade_list)

        accuracy_score = accuracy(ob, new_Fo[line, :], grade_list)
        total_num = ob.size
        NF_array = conf_mx[0:-1, -1]
        NO_array = conf_mx[-1, 0:-1]
        random_score = np.dot(NF_array, NO_array) / (total_num * total_num)
        if (random_score == 1):
            HSS = IV
        else:
            HSS = (accuracy_score - random_score) / (1 - random_score)
        hss_list.append(HSS)
    if len(hss_list)==1:
        hss_array = hss_list[0]
    else:
        hss_array = np.array(hss_list)
        shape = list(Fo_shape[:ind])
        hss_array = hss_array.reshape(shape)

    return hss_array


def hk(ob, fo, grade_list=None):
    '''
    hk Hanssen和Kuipers判别
    :param ob: 实况数据 任意维numpy数组
    :param fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 如果该参数为None，观测或预报值出现过的值都作为分类标记.
    如果该参数不为None，它必须是一个从小到大排列的实数，以其中列出的数值划分出的多个区间作为分类标签。
    对于预报和观测值不为整数的情况，grade_list 不能设置为None。
    :return:
    '''
    # 多分类预报hk技巧评分
    Ob_shape = ob.shape
    Fo_shape = fo.shape
    hk_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')

        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    for line in range(new_Fo_shape[0]):
        conf_mx = meteva.method.multi_category.table.contingency_table_multicategory(ob, new_Fo[line, :], grade_list)
        accuracy_score = accuracy(ob, new_Fo[line, :], grade_list)
        total_num = ob.size
        NF_array = conf_mx[0:-1, -1]
        NO_array = conf_mx[-1, 0:-1]
        random_score = np.dot(NF_array, NO_array) / (total_num * total_num)
        ob_rate = np.dot(NO_array, NO_array) / (total_num * total_num)
        HK = (accuracy_score - random_score) / (1 - ob_rate)
        hk_list.append(HK)
    if len(hk_list)==1:
        hk_array = hk_list[0]
    else:
        hk_array = np.array(hk_list)
        shape = list(Fo_shape[:ind])
        hk_array = hk_array.reshape(shape)

    return hk_array


def hk_tcof(tcof_array):
    '''
    :param tcof_array:
    :return:
    '''

    tc_sum = tcof_array[..., 0, 0]
    cc_sum = tcof_array[..., 0, 1]
    accuracy_score = cc_sum / tc_sum
    obn_sum = tcof_array[..., 1:, 0]
    fon_sum = tcof_array[..., 1:, 1]
    dotobfo = np.zeros_like(tc_sum)
    dotobob = np.zeros_like(tc_sum)
    for g in range(obn_sum.shape[-1]):
        dotobfo += obn_sum[..., g] * fon_sum[..., g]
        dotobob += obn_sum[..., g] * obn_sum[..., g]
    random_score = dotobfo / (tc_sum * tc_sum)
    ob_rate = dotobob / (tc_sum * tc_sum)
    if ob_rate.size == 1:
        if ob_rate == 1:
            HK = IV
        else:
            HK = (accuracy_score - random_score) / (1 - ob_rate)
    else:
        ob_rate[ob_rate == 1] = -1
        HK = (accuracy_score - random_score) / (1 - ob_rate)
        HK[ob_rate == -1] = IV
    return HK


def hss_tcof(tcof_array):
    '''
    :param tcof_list:
    :return:
    '''
    tc_sum = tcof_array[..., 0, 0]
    cc_sum = tcof_array[..., 0, 1]
    accuracy_score = cc_sum / tc_sum
    obn_sum = tcof_array[..., 1:, 0]
    fon_sum = tcof_array[..., 1:, 1]
    dotobfo = np.zeros_like(tc_sum)
    dotobob = np.zeros_like(tc_sum)
    for g in range(obn_sum.shape[-1]):
        dotobfo += obn_sum[..., g] * fon_sum[..., g]
        dotobob += obn_sum[..., g] * obn_sum[..., g]
    random_score = dotobfo / (tc_sum * tc_sum)

    if random_score.size == 1:
        if random_score == 1:
            HSS = IV
        else:
            HSS = (accuracy_score - random_score) / (1 - random_score)
    else:
        random_score[random_score == 1] = -1
        HSS = (accuracy_score - random_score) / (1 - random_score)
        HSS[random_score == -1] = IV

    return HSS


def seeps_ctable(contingency_table_multicategory,p1):

    s_fv = np.array([[0, 1 / (1 - p1), 4 / (1 - p1)],
                     [1 / p1, 0, 3 / (1 - p1)],
                     [1 / p1 + 3 / (2 + p1), 3 / (2 + p1), 0]]) * 0.5

    if len(contingency_table_multicategory.shape) == 2:
        ctm_fv = contingency_table_multicategory
        p_fv = ctm_fv[0:-1, 0:-1] / ctm_fv[-1, -1]
        #print(p_fv)
        seeps_error = np.sum(s_fv * p_fv)
        return seeps_error
    else:
        seeps_error_list=[]
        for line in range(contingency_table_multicategory[0]):
            ctm_fv = contingency_table_multicategory[line,:,:]
            p_fv = ctm_fv[0:-1, 0:-1] / ctm_fv[-1, -1]
            seeps_error = np.sum(s_fv * p_fv)
            seeps_error_list.append(seeps_error)
        seeps_error_array = np.array(seeps_error_list)
        #shape = list(Fo_shape[:ind])
        #seeps_error_array = seeps_error_array.reshape(shape)
        return seeps_error_array


def seeps(Ob, Fo, p1=None, threshold=None):
    '''

    :param Ob:
    :param Fo:
    :param p1:
    :param significant_rain_threshold:
    :return:
    '''

    if p1 is None:
        ob1 = np.sort(Ob.flatten())
        index_p1 = np.where(ob1 <= 0.2)
        p1 = len(index_p1[0]) / ob1.size
        p3 = (1 - p1) / 3
        index_p3 = int(math.ceil((1 - p3) * ob1.size)) - 1
        threshold = ob1[index_p3]
        if threshold < 0.3:
            threshold = 0.3
    if p1 == 1: p1 -= 1e-6
    if p1 == 0: p1 = 1e-6
    ctable = meteva.method.contingency_table_multicategory(Ob, Fo,
                                                  grade_list=[0.2000001, threshold])
    seeps_error = seeps_ctable(ctable,p1)
    return seeps_error



def seeps_skill(Ob, Fo, p1=None, threshold=None):
    '''

    :param Ob:
    :param Fo:
    :param p1:
    :param significant_rain_threshold:
    :return:
    '''
    seeps_array = seeps(Ob,Fo,p1= p1,threshold=threshold)
    skill = 1- seeps_array
    return skill


def show_valid_k1_k2(p1,p2,p3):
    x = np.arange(201)*0.01-1
    y = np.arange(201)*0.01-1
    valid_index = np.zeros((201,201))
    for i in range(201):
        for j in range(201):
            k2 = x[i]
            k1 = y[j]

            s11 = (p3 + p1*(p3-p2) * k1 + p3*(p2+p3)*k2) / (p1 * (p1+p3))
            s13 = -(1+(p1+p2)*k1 + (p2+p3)*k2)/(p1+p3)
            s22 = -(p1*k1 + p3 *k2)/p2
            s33 = (p1+p1*(p1+p2)*k1 + p3*(p1-p2)*k2)/(p3*(p1+p3))

            if (i == 125 and j == 50):
                print()

            # 非顺序条件
            if k1 < s11 and k1 < s22 and k2 <s22 and k2 < s33 and s13 < s11 and s13 < s33:
                valid_index[i,j] = 1

                #顺序条件
                if s13< k1 and s13 < k2:
                    valid_index[i, j] += 1
    print(valid_index)
    import matplotlib.pyplot as plt
    plt.pcolormesh(valid_index.T)
    plt.show()

def get_s_array(p1,p2,p3,k1=-0.25,k2=-0.25):
    '''
    根据3分类预报问题的实况气候概率p1,p2和p3， 确定Murphy评分的评分权重矩阵。
    评分权重的确定原理简单叙述如下：
    3分类预报的完整检验信息可由一个3×3的列联表表示。列联表中的元素p_ij表示 观测为第i类,预报为第j类的样本数。
    总的评分等于列联表每个元素×一个权重系数后求和得到 sum(p_ij * s_ij)。 为此需要确定9个评分权重系数。
    一般来说对角线上的权重系数s_ii 应该是正的，表示奖励， 非对角线上的s_ij是负的表示惩罚。那这9个评分权重该取为多少，
    用它们做评价才是公平的？ 为此主要考虑2点，一是如果全部报对（列联表的元素全部集中在对角线上），评分应为1，另外，
    随机预报的评分应该为0，这2个条件可以构成关于权重系数的4个方程构成的方程组，这个方程组中包含3个分类的实况概率p1、p2、p3，
    构成的已知参数。如果考虑这个评分矩阵是对称的，则一共有6个待定系数，因此它是一个欠定问题。为此有两个评分权重系数必须事先指定，
    为此令 k1 = s12, k2 = s23， 在此基础上可以计算出其它4个系数 s11,s22,s33,s13.
    根据Murphy的分析，k1和k2的取值范围为(-0.5,0)时，计算出的评分权重可以满足：
    s12 < s11,s12<s22, s23<s22,s23<s33, s13<s12,s13<s23。
    关于上述内容的更详细论述可参考《预报检验-大气科学从业者指南》 4.3.2节
    :param p1: 实况第1分类的概率
    :param p2: 实况第2分类的概率
    :param p3: 实况第3分类的概率
    :param k1:权重系数s12
    :param k2:权重系数s23
    :return: 3×3的权重系数矩阵。
    '''

    s_array = np.zeros((3,3))

    s_array[0,1] = k1
    s_array[1, 0] = k1  #对称
    s_array[1,2] = k2
    s_array[2, 1] = k2  #对称

    #《预报检验-大气科学从业者指南》 4.3.2节 公式4.13
    s_array[0,0] = (p3 + p1 * (p3 - p2) * k1 + p3 * (p2 + p3) * k2) / (p1 * (p1 + p3))
    s_array[0, 2] = -(1 + (p1 + p2) * k1 + (p2 + p3) * k2) / (p1 + p3)
    s_array[1,1] = -(p1 * k1 + p3 * k2) / p2
    s_array[2,2] = (p1 + p1 * (p1 + p2) * k1 + p3 * (p1 - p2) * k2) / (p3 * (p1 + p3))

    s_array[2,0] = s_array[0,2]  #对称

    print(s_array)
    return s_array



def murphy_ctable(ctable_array,s_array):
    '''
    根据3×3的列联表，和评分权重矩阵 计算 Murphy 矩阵
    评分公式参考《预报检验-大气科学从业者指南》 4.3.2节，公式 4.8
    :param ctable_array:  3×3的观测预报列联表
    :param s_array:  评分权重矩阵
    :return:  Murphy评分
    '''

    score = np.sum(ctable_array * s_array)
    return score



def murphy_score(ob,fo,grade_list = None,p1 = None,p2 = None,p3 = None,k1 = -0.25,k2 = 0.25):
    '''
    计算Murphy 评分。
    步骤包括：
    1. 根据实况和预报数据，以及等级划分阈值，统计列联表
    2. 根据3分类预报问题的实况气候概率p1,p2和p3，确定Murphy评分的评分权重矩阵（函数 get_s_array）
    3. 根据列联表和权重矩阵，计算Murphy 评分。

    :param ob: 实况数据，
    :param fo: 预报数据
    :param grade_list:实况和预报分类的阈值，如果实况和预报已经是离散的等级，则不需要该参数
    :param p1: 实况为第1分类的气候概率
    :param p2:实况为第2分类的气候概率
    :param p3:实况为第2分类的气候概率
    :param k1: 评分权重系数 s12
    :param k2:评分权重系数 s23
    :return: Murphy评分。
    '''

    #根据实况获取观测预报的列联表
    ctable = meteva.method.multi_category.table.contingency_table_multicategory(ob,fo,grade_list)
    if len(ctable.shape)==2:
        ctable = ctable.reshape(1,ctable.shape[0],ctable.shape[1])


    if p1 is not None and p2 is not None and p3 is not None:
        # 如果用户从外部指定实况的概率，就用用户指定的概率来生成权重矩阵s_array
        s_array = get_s_array(p1,p2,p3,k1,k2)
    else:
        #如果用户未指定实况概率，则根据传入的实况数据来获取每个等级的概率，再计算权重矩阵
        p_ob = ctable[0, :-1, -1] / ctable[0, -1, -1]  # 返回的列联表实际上是4×4的，其中最后一行是实况的概率分布
        s_array = get_s_array(p_ob[0], p_ob[1], p_ob[2], k1, k2)


    score_list = []
    for i in range(ctable.shape[0]):
        ct_array = ctable[i, :-1, :-1]
        score1 =murphy_ctable(ct_array,s_array)  #已知列联表和权重系数矩阵，计算Murphy 评分
        score_list.append(score1)

    if len(score_list)==1:
        return score_list[0]  #单个预报返回实数
    else:
        return np.array(score_list)  #多个预报返回数组





if __name__ == "__main__":


    s_array = get_s_array(-0.5,-0.25,0.2,0.5,0.3)
    print(s_array*60)