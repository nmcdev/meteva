import numpy as np
import copy

def pc_hmfn(hmfn_list):
    '''
    晴雨准确率
    -------------------------
    :param hit: 命中数
    :param mis: 空报数
    :param fal: 漏报数
    -------------------------
    :return:
    '''
    hmfn_array = np.array(hmfn_list)
    hmfn_array_sum = np.sum(hmfn_array,axis=0)
    hit = hmfn_array_sum[0]
    mis = hmfn_array_sum[1]
    fal = hmfn_array_sum[2]
    cn = hmfn_array_sum[3]
    cr = (hit + cn) / (hit + mis + fal + cn)
    return cr

def pc_of_sunny_rainy(Ob, Fo):
    '''
    晴雨准确率
    :param Ob: 一个一维得numpy.ndarray   实况数据
    :param Fo: 一个一维得numpy.ndarray   预测数据
    :return:
    '''
    # 晴雨准确率
    hmfn_list = hmfn_of_sunny_rainy(Ob, Fo)
    cr = pc_hmfn(hmfn_list)
    return cr

def hmfn_of_sunny_rainy(Ob, Fo):
    '''
    晴雨准确率列联表
    :param Ob: 一个一维得numpy.ndarray   实况数据
    :param Fo: 一个一维得numpy.ndarray   预测数据
    :return:
    '''
    # 晴雨准确率
    fo1 = copy.deepcopy(Fo)
    fo1[fo1 < 0.099] = 0
    shape = Ob.shape
    obhap = np.zeros(shape)
    obhap[Ob > 0] = 1
    fohap = np.zeros(shape)
    fohap[fo1 > 0] = 1
    obhap01 = np.zeros(shape)
    obhap01[Ob >= 0.1] = 1

    hit_threshold = (obhap * fohap)
    mis_threshold = (obhap01 * (1 - fohap))
    fal_threshold = ((1 - obhap) * fohap)
    cn_threshold = 1 - hit_threshold - mis_threshold - fal_threshold

    hit = hit_threshold.sum()
    mis = mis_threshold.sum()
    fal = fal_threshold.sum()
    cn = cn_threshold.sum()
    return hit.tolist(), mis.tolist(), fal.tolist(), cn.tolist()

def hit_rate(Ob, Fo, grade_list=[1e-30]):
    hit, mis, fal, _ = hmfn(Ob, Fo, grade_list)
    return hit / (hit + mis + 0.0000001)

def hit_rate_hmfn(hmfn_list):
    hmfn_array = np.array(hmfn_list)
    hmfn_array_sum = np.sum(hmfn_array,axis=0)
    hit = hmfn_array_sum[0]
    mis = hmfn_array_sum[1]
    return hit / (hit + mis + 0.0000001)

def fal_rate(Ob, Fo, grade_list=[1e-30]):
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
    # 如果threshold_list ==None，则说明Ob,Fo是0或1组成的数组

    hit, mis, fal, _ = hmfn(Ob, Fo, grade_list)
    return fal / (hit + fal + 0.0000001)

def fal_rate_hmfn(hmfn_list):
    hmfn_array = np.array(hmfn_list)
    hmfn_array_sum = np.sum(hmfn_array,axis=0)
    hit = hmfn_array_sum[0]
    fal = hmfn_array_sum[2]
    return fal / (hit + fal + 0.0000001)

def mis_rate(Ob, Fo, grade_list=[1e-30]):

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
    # 如果threshold_list ==None，则说明Ob,Fo是0或1组成的数组

    hit, mis, fal, _ = hmfn(Ob, Fo, grade_list)
    return mis / (hit + mis + 0.0000001)

def mis_rate_hmfn(hmfn_list):
    hmfn_array = np.array(hmfn_list)
    hmfn_array_sum = np.sum(hmfn_array,axis=0)
    mis = hmfn_array_sum[1]
    hit = hmfn_array_sum[0]
    return mis / (hit + mis + 0.0000001)

def bias(Ob, Fo, grade_list=[1e-30]):
    '''
    bias   bias评分
    ----------------
    :param Ob: 实况数据 一维numpy
    :param Fo: 预测数据 一维numpy
    :param grade_list: 等级
    :return: '''
    # 输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一维bias评分值数组，数组中的每个值对应一个等级
    # 如果threshold_list ==None，则说明Ob,Fo是0或1组成的数组

    hit, mis, fal, _ = hmfn(Ob, Fo, grade_list)
    bias0 = (hit + fal) / (hit + mis + 0.0000001)
    sum = hit +mis +fal
    bias0[sum == 0] = 1
    delta = fal - mis
    bias0[delta ==0] = 1
    return bias0

def bias_hmfn(hmfn_list):
    hmfn_array = np.array(hmfn_list)
    hmfn_array_sum = np.sum(hmfn_array,axis=0)
    mis = hmfn_array_sum[1]
    hit = hmfn_array_sum[0]
    fal = hmfn_array_sum[2]
    bias0 = (hit + fal) / (hit + mis + 0.0000001)
    sum = hit +mis +fal
    bias0[sum == 0] = 1
    delta = fal - mis
    bias0[delta ==0] = 1
    return bias0

def bias_extend(Ob, Fo, grade_list=[1e-30]):
    bias0 = bias(Ob, Fo,grade_list)
    bias_extend0 = np.abs(bias0 - 1)
    return bias_extend0

def bias_extend_hmfn(hmfn_list):
    bias0 = bias_hmfn(hmfn_list)
    bias_extend0 = np.abs(bias0 - 1)
    return bias_extend0

def ts(Ob, Fo, grade_list=[1e-30]):
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
    # 如果threshold_list ==None，则说明Ob,Fo是0或1组成的数组
    hmfn_list = [hmfn(Ob, Fo, grade_list)]
    return ts_hmfn(hmfn_list)

def ts_hmfn(hmfn_list):
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
    hmfn_array = np.array(hmfn_list)
    hmfn_array_sum = np.sum(hmfn_array,axis=0)
    hit = hmfn_array_sum[0]
    mis = hmfn_array_sum[1]
    fal = hmfn_array_sum[2]
    ts_array =hit / (hit + mis + fal + 1e-30)
    return ts_array

def ets(Ob, Fo, grade_list=[1e-30]):
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
    # 如果threshold_list ==None，则说明Ob,Fo是0或1组成的数组
    hmfn_list = [hmfn(Ob, Fo, grade_list)]
    return ets_hmfn(hmfn_list)

def ets_hmfn(hmfn_list):
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
    hmfn_array = np.array(hmfn_list)
    hmfn_array_sum = np.sum(hmfn_array,axis=0)
    hit = hmfn_array_sum[0]
    mis = hmfn_array_sum[1]
    fal = hmfn_array_sum[2]
    cn = hmfn_array_sum[3]

    total = hit + mis + fal + cn + 0.000001  # 加0.0000001 为防止出现除0情况
    hit_random = (hit + mis) * (hit + fal) / total
    return (hit - hit_random) / (hit + mis + fal - hit_random + 0.000001)

def hmfn(Ob, Fo, grade_list=[1e-300]):
    '''
    hmfn  列联表
    -------------------------------
    :param Ob: 实况数据  一维numpy
    :param Fo: 预测数据  一维numpy
    :param threshold_list:阈值列表
    -------------------------------
    :return:
    '''
    # 输入观测Ob和预报Fo的预报数据（1维的numpy数组）
    # 返回命中数、空报数、漏报数、正确否定数共4个数组，数组中的每个值对应一个等级
    # 如果threshold_list ==None，则说明Ob,Fo是0或1组成的数组

    hit = np.zeros(len(grade_list))
    mis = np.zeros(len(grade_list))
    fal = np.zeros(len(grade_list))
    cn = np.zeros(len(grade_list))
    for i in range(len(grade_list)):
        threshold = grade_list[i]
        num = np.size(Ob)
        obhap = np.zeros_like(Ob)
        obhap[Ob >= threshold] = 1
        fohap = np.zeros_like(Fo)
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


