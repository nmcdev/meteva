import meteva
import numpy as np
from meteva.base import IV
from meteva.method.yes_or_no.score import ts_hfmc, ets_hfmc, bias_hfmc, far_hfmc, mr_hfmc


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
        print('实况数据和观测数据维度不匹配')
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
        print('实况数据和观测数据维度不匹配')
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
        print('实况数据和观测数据维度不匹配')
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
        print('实况数据和观测数据维度不匹配')
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
        print('实况数据和观测数据维度不匹配')

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
        print('实况数据和观测数据维度不匹配')

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
