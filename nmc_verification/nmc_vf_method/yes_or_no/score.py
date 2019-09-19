import numpy as np

def pc_of_sunny_rainy(Ob, Fo):
    '''
    晴雨准确率
    :param Ob: 一个一维得numpy.ndarray   实况数据
    :param Fo: 一个一维得numpy.ndarray   预测数据
    :return:
    '''
    # 晴雨准确率
    hit, mis, fal, cn = hmfn_of_sunny_rainy(Ob, Fo)
    cr = (hit + cn) / (hit + mis + fal + cn)
    return cr


def hmfn_of_sunny_rainy(Ob, Fo):
    '''
    晴雨准确率列联表
    :param Ob: 一个一维得numpy.ndarray   实况数据
    :param Fo: 一个一维得numpy.ndarray   预测数据
    :return:
    '''
    # 晴雨准确率
    Fo[Fo < 0.1] = 0
    num = np.size(Ob)
    obhap = np.zeros(num)
    obhap[Ob > 0] = 1
    fohap = np.zeros(num)
    fohap[Fo > 0] = 1
    obhap01 = np.zeros(num)
    obhap01[Ob >= 0.1] = 1

    hit_threshold = (obhap * fohap)
    mis_threshold = (obhap01 * (1 - fohap))
    fal_threshold = ((1 - obhap) * fohap)
    cn_threshold = 1 - hit_threshold - mis_threshold - fal_threshold

    hit = hit_threshold.sum()
    mis = mis_threshold.sum()
    fal = fal_threshold.sum()
    cn = cn_threshold.sum()
    return hit, mis, fal, cn


def hit_rate(Ob, Fo, grade_list=None):
    '''
    hit_rate 求出命中率
    ----------------------
    :param Ob: 实况数据 一维numpy
    :param Fo: 预测数据 一维numpy
    :param grade_list: 等级
    :return:
    '''
    # 输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一维命中率评分值数组，数组中的每个值对应一个等级
    # 如果grade_list ==None，则说明Ob,Fo是0或1组成的数组

    hit, mis, fal, _ = hmfn(Ob, Fo, grade_list)
    return hit / (hit + mis + 0.0000001)


def fal_rate(Ob, Fo, grade_list=None):
    '''
    fal-rate  求出误报率
    ------------------
    :param Ob: 实况数据 一维numpy
    :param Fo: 预测数据 一维numpy
    :param grade_list: 等级
    :return:
    '''
    # 输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一维空报率评分值数组，数组中的每个值对应一个等级
    # 如果grade_list ==None，则说明Ob,Fo是0或1组成的数组

    hit, mis, fal, _ = hmfn(Ob, Fo, grade_list)
    return fal / (hit + fal + 0.0000001)


def mis_rate(Ob, Fo, grade_list=None):

    '''
    mis_rate 漏报率评分
    --------------------------
    :param Ob: 实况数据 一维numpy
    :param Fo: 预测数据 一维numpy
    :param grade_list: 等级
    :return:
    '''
    # 输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一维漏报率评分值数组，数组中的每个值对应一个等级
    # 如果grade_list ==None，则说明Ob,Fo是0或1组成的数组

    hit, mis, fal, _ = hmfn(Ob, Fo, grade_list)
    return mis / (hit + mis + 0.0000001)


def bias(Ob, Fo, grade_list=None):
    '''
    bias   bias评分
    ----------------
    :param Ob: 实况数据 一维numpy
    :param Fo: 预测数据 一维numpy
    :param grade_list: 等级
    :return: '''
    # 输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一维bias评分值数组，数组中的每个值对应一个等级
    # 如果grade_list ==None，则说明Ob,Fo是0或1组成的数组

    hit, mis, fal, _ = hmfn(Ob, Fo, grade_list)
    return (hit + fal) / (hit + mis + 0.0000001)



def bias_extend(Ob, Fo, grade_list=None):
    bias0 = bias(Ob, Fo, grade_list)

    bias_extend0 = np.abs(bias0 - 1)
    return bias_extend0


def ts(Ob, Fo, grade_list=None):
    '''
    ts ts评分
    -----------------------------
    :param Ob: 实况数据 一维numpy
    :param Fo: 预测数据 一维numpy
    :param grade_list: 等级
    -----------------------------
    :return:
    '''
    # 输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值value，
    # 返回一维ts评分值数组，数组中的每个值对应一个等级
    # 如果grade_list ==None，则说明Ob,Fo是0或1组成的数组

    hit, mis, fal, _ = hmfn(Ob, Fo, grade_list)
    return ts_hmfn(hit, mis, fal)


def ts_hmfn(hit, mis, fal):
    '''
    ts  hmfn评分
    -------------------------
    :param hit: 命中数
    :param mis: 空报数
    :param fal: 漏报数
    -------------------------
    :return:
    '''
    # 输入命中、空报、漏报数
    # 返回一维ts评分值数组，数组中的每个值对应一个等级
    return hit / (hit + mis + fal + 0.000001)


def ets(Ob, Fo, grade_list=None):
    '''
    ets ets评分
    ----------------------------
    :param Ob: 实况数据 一维numpy
    :param Fo: 预测数据 一维numpy
    :param grade_list: 等级
    -----------------------------
    :return:
    '''
    # 输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值value，
    # 返回一维ets评分值数组，数组中的每个值对应一个等级
    # 如果grade_list ==None，则说明Ob,Fo是0或1组成的数组

    hit, mis, fal, cn = hmfn(Ob, Fo, grade_list)
    return ets_hmfn(hit, mis, fal, cn)


def ets_hmfn(hit, mis, fal, cn):
    '''
    ets_hmfn ets_hmfn评分# 输入命中数、空报数、漏报数、正确否定数
    # 返回一维ets评分值数组，数组中的每个值对应一个等级
    -------------------------
    :param hit: 命中数
    :param mis: 空报数
    :param fal: 漏报数
    :param cn: 正确否定数
    -------------------------
    :return:
    '''

    total = hit + mis + fal + cn + 0.000001  # 加0.0000001 为防止出现除0情况
    hit_random = (hit + mis) * (hit + fal) / total
    return (hit - hit_random) / (hit + mis + fal - hit_random + 0.000001)


def hmfn(Ob, Fo, grade_list=None):
    '''
    hmfn  列联表
    -------------------------------
    :param Ob: 实况数据  一维numpy
    :param Fo: 预测数据  一维numpy
    :param grade_list:阈值列表
    -------------------------------
    :return:
    '''
    # 输入观测Ob和预报Fo的预报数据（1维的numpy数组）
    # 返回命中数、空报数、漏报数、正确否定数共4个数组，数组中的每个值对应一个等级
    # 如果grade_list ==None，则说明Ob,Fo是0或1组成的数组
    if grade_list is None:

        hit_threshold = (Ob * Fo)
        mis_threshold = (Ob * (1 - Fo))
        fal_threshold = ((1 - Ob) * Fo)
        cn_threshold = ((1 - Ob) * (1 - Fo))
        hit = hit_threshold.sum()
        mis = mis_threshold.sum()
        fal = fal_threshold.sum()
        cn = cn_threshold.sum()
        return hit, mis, fal, cn
    else:
        hit = np.zeros(len(grade_list))
        mis = np.zeros(len(grade_list))
        fal = np.zeros(len(grade_list))
        cn = np.zeros(len(grade_list))
        for i in range(len(grade_list)):
            threshold = grade_list[i]
            num = np.size(Ob)
            obhap = np.zeros(num)
            obhap[Ob >= threshold] = 1
            fohap = np.zeros(num)
            fohap[Fo >= threshold] = 1

            hit_threshold = (obhap * fohap)
            mis_threshold = (obhap * (1 - fohap))
            fal_threshold = ((1 - obhap) * fohap)
            cn_threshold = ((1 - obhap) * (1 - fohap))
            hit[i] = hit_threshold.sum()
            mis[i] = mis_threshold.sum()
            fal[i] = fal_threshold.sum()
            cn[i] = cn_threshold.sum()
        return hit, mis, fal, cn
