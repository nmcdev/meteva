import numpy as np
from meteva.base.tool.math_tools import mean_iteration,sxy_iteration,ss_iteration
from meteva.base import IV

def sample_count(Ob,Fo  = None):
    '''
    计算检验的样本数
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 整数，Ob.size
    '''
    return Ob.size

def ob_mean(Ob,Fo = None):
    '''
    计算观测样本的平均
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: None或任意数据，它的存在是为了使得参数规范化，方便更高级的封装
    :return: 实数
    '''
    return np.mean(Ob)

def fo_mean(Ob,Fo):
    '''
    计算观测样本的平均
    -----------------------------
    :param Ob: None或任意数据，它的存在是为了使得参数规范化，方便更高级的封装
    :param Fo: 预报数据  任意维numpy数组
    :return: 实数
    '''
    return np.mean(Fo)

def tc_count(Ob,Fo,threshold):
    '''
    计算准确率的中间结果
    :param Ob:
    :param Fo:
    :param threshold:
    :return:
    '''
    total_count = Ob.size
    error = np.abs(Fo - Ob)
    index = np.where(error<= threshold)
    correct_count = len(index[0])
    return np.array([total_count,correct_count])

def correct_rate(Ob,Fo,threshold):
    '''
    计算准确率
    :param Ob:
    :param Fo:
    :param threshold:
    :return:
    '''
    tc_array = tc_count(Ob,Fo,threshold)
    return tc_array[1]/tc_array[0]

def correct_rate_tc(tc_count_array):
    '''

    :param tc_count_array:
    :return:
    '''
    cr1 = tc_count_array[...,1]/tc_count_array[...,0]
    return cr1


def tase(Ob,Fo):
    '''
    计算平均误差、平均绝对误差、均方误差、均方根误差的中间结果
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 一维numpy数组，其内容依次为总样本数、误差总和、绝对误差总和、误差平方总和
    '''
    total_count = Ob.size
    e_sum = np.sum(Fo - Ob)
    ae_sum = np.sum(np.abs(Fo - Ob))
    se_sum = np.sum(np.square(Fo - Ob))
    return np.array([total_count,e_sum,ae_sum,se_sum])

def me(Ob, Fo):
    '''
    me 求两组数据的误差平均值
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 负无穷到正无穷的实数，最优值为0
    '''
    mean_error = np.mean(Fo - Ob)
    return mean_error

def me_tase(tase_array):
    '''
    me 求两组数据的误差平均值
    :param tase_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（total_count,e_sum,ae_sum,se_sum）
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 负无穷到正无穷的实数，最优值为0
    '''
    mean_error = tase_array[...,1]/tase_array[...,0]
    return mean_error

def mae(Ob, Fo):
    '''
    mean_abs_error,对两组数据求平均绝对值误差
    -----------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 0到无穷大，最优值为0
    '''
    mean_abs_error = np.mean(np.abs(Ob - Fo))
    return mean_abs_error
def mae_tase(tase_array):
    '''
    mean_abs_error,求两组数据的平均绝对误差
    :param tase_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（total_count,e_sum,ae_sum,se_sum）
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到无穷大，最优值为0
    '''
    mean_abs_error = tase_array[...,2]/tase_array[...,0]
    return mean_abs_error

def mse(Ob, Fo):
    '''
    mean_sqrt_error, 求两组数据的均方误差
    ----------------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 0到无穷大，最优值为0
    '''

    mean_squre_error = np.mean(np.square(Ob - Fo))
    return mean_squre_error
def mse_tase(tase_array):
    '''
    mse 求两组数据的均方误差
    :param tase_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（total_count,e_sum,ae_sum,se_sum）
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到无穷大，最优值为0
    '''
    mean_squre_error = tase_array[...,3]/tase_array[...,0]
    return mean_squre_error

def rmse(Ob, Fo):
    '''
    root_mean_square_error 求两组数据的均方根误差
    ------------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 0到无穷大，最优值为0
    '''
    mean_sqrt_error = np.sqrt(np.mean(np.square(Ob - Fo)))
    return mean_sqrt_error
def rmse_tase(tase_array):
    '''
    mse 求两组数据的均方根误差
    :param tase_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（total_count,e_sum,ae_sum,se_sum）
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到无穷大，最优值为0
    '''
    root_mean_sqrt_error = np.sqrt(tase_array[...,3]/tase_array[...,0])
    return root_mean_sqrt_error

def bias_m(Ob, Fo):
    '''
    均值偏差 求预测数据和实况数据的平均值的比
    ------------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return:  0到正无穷，最优值为1
    '''
    mean_ob = np.mean(Ob)
    if mean_ob == 0:
        bias0 = IV
    else:
        bias0 = np.mean(Fo) / mean_ob
    return bias0

def bias_tmmsss(tmmsss_array):
    '''
    均值偏差 求预测数据和实况数据的平均值的比
    :param tmmsss_array: 包含命中空报和漏报的多维数组，其中最后一维长度为6，分别记录了（count,mx,my,sxx,syy,sxy）
    :return:
    '''
    mean_ob = tmmsss_array[...,1] + 0
    mean_fo = tmmsss_array[...,2]
    if mean_ob.size ==1:
        if mean_ob == 0:
            bias0 = IV
        else:
            bias0 = mean_fo/mean_ob
    else:
        mean_ob[mean_ob == 0] = IV
        bias0 = mean_ob/mean_fo
        bias0[mean_ob == IV] = IV
    return bias0

def corr(Ob, Fo):
    '''
    相关系数，求实况数据还和预测数据之间的相关系数
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: corr0
    '''
    ob_f = Ob.flatten()
    fo_f = Fo.flatten()
    corr0 = np.corrcoef(ob_f, fo_f)[0, 1]
    return corr0

def corr_tmmsss(tmmsss_array):
    '''
    相关系数，求实况数据还和预测数据之间的相关系数
    :param tmmsss_array: 包含命中空报和漏报的多维数组，其中最后一维长度为6，分别记录了（count,mx,my,sxx,syy,sxy）
    :return:
    '''
    sxx = tmmsss_array[...,3]
    syy = tmmsss_array[...,4]
    sxy = tmmsss_array[...,5]
    sxxsyy = np.sqrt(sxx * syy)
    if sxxsyy.size == 1:
        if sxxsyy == 0:
            sxxsyy = 1e-10
    else:
        sxxsyy[sxxsyy == 0] = 1e-10
    corr = sxy/sxxsyy
    return corr

def tmmsss(Ob,Fo):
    '''
    统计相关系数等检验量所需的中间变量
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: numpy 一维数组，其元素为根据Ob和Fo
    计算出的（样本数，观测平均值，预报平均值，观测方差，预报方差，协方差
    '''
    ob_f = Ob.flatten()
    fo_f = Fo.flatten()
    count = Ob.size
    mx = np.mean(ob_f)
    my = np.mean(fo_f)
    dx = ob_f - mx
    dy = fo_f - my
    sxx = np.mean(np.power(dx,2))
    syy = np.mean(np.power(dy,2))
    sxy = np.mean(dx * dy)
    return np.array([count,mx,my,sxx,syy,sxy])

def tmmsss_merge(tmmsss0,tmmsss1):
    '''
    将两份包含样本数、平均值和方差、协方差的中间结果合并
    :param tmmsss0: 长度6的一维数组，分别记录了（count,mx,my,sxx,syy,sxy）
    :param tmmsss1: 长度6的一维数组，分别记录了（count,mx,my,sxx,syy,sxy）
    :return: 长度6的一维数组，分别记录了（count,mx,my,sxx,syy,sxy）
    '''
    count_0 = tmmsss0[0]
    mx_0 = tmmsss0[1]
    my_0 = tmmsss0[2]
    sxx_0 = tmmsss0[3]
    syy_0 = tmmsss0[4]
    sxy_0 = tmmsss0[5]
    count_1 = tmmsss1[0]
    mx_1 = tmmsss1[1]
    my_1 = tmmsss1[2]
    sxx_1 = tmmsss1[3]
    syy_1 = tmmsss1[4]
    sxy_1 = tmmsss1[5]
    _, _, sxx_total = ss_iteration(count_0, mx_0, sxx_0, count_1, mx_1, sxx_1)
    _, _, syy_total = ss_iteration(count_0, my_0, syy_0, count_1, my_1, syy_1)
    count_total, mx_total, my_total, sxy_total = sxy_iteration(count_0, mx_0, my_0, sxy_0,
                                                               count_1, mx_1, my_1, sxy_1)
    return np.array([count_total,mx_total,my_total,sxx_total,syy_total,sxy_total])

def mre(Ob, Fo):
    '''
    mre  精细化网格预报竞赛检验办法中的降水量定量相对误差检验指标
    :param Ob: 实况数据 不定长维度的numpy
    :param Fo: 测试数据 不定长维度的numpy
    :return: mre
    '''
    s = Ob + Fo
    if np.sum(s) == 0:
        return 0
    else:
        d = Ob - Fo
        s1 = s[s > 0]
        d1 = d[s > 0]
        are0 = np.mean(np.abs(d1 / s1))
        return are0

def mre_toar(toar_array):
    '''
    mre  精细化网格预报竞赛检验办法中的降水量定量相对误差检验指标
    :param toar_array: 包含命中空报和漏报的多维数组，其中最后一维长度为2，分别记录了（预报和观测值之和大于0样本数,各点相对误差绝对值总和）
    （预报和观测值之和大于0样本数、各点相对误差绝对值总和），它由toar返回
    :return:
    '''
    count = toar_array[...,0] + 0
    if count.size ==1:
        if count == 0:
            mre0 = IV
        else:
            mre0 = toar_array[...,1] / count
    else:
        count[count<0] = 1e-10
        ar = toar_array[...,1]
        mre0 = ar/count
        mre0[count<1] = IV
    return mre0

def toar(Ob,Fo):
    '''
    相对误差检验指标的中间结果量
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 一维numpy数组，其内容依次为预报和观测值之和大于0样本数、各点相对误差绝对值总和
    '''
    s = Ob + Fo
    d = Ob - Fo
    s1 = s[s > 0]
    d1 = d[s > 0]
    ar = np.sum(np.abs(d1 / s1))
    return np.array([s1.size,ar])


def nse(Ob,Fo):
    '''
    nse纳什系数, 常用于计算两个非正态序列的相对误差情况，
    :param Ob:实况数据 不定长维度的numpy
    :param Fo:测试数据 不定长维度的numpy
    :return:负无穷至1，最优值为1
    '''
    mob = np.mean(Ob)
    qdob = np.mean(np.power(Ob - mob,2))
    if qdob ==0:
        return IV
    else:
        return 1-np.mean(np.power(Ob - Fo,2))/qdob

def nse_tase_tmmsss(tase_array,tmmsss_array):
    '''

    :param tase_array:
    :param tmmsss_array:
    :return:
    '''
    sxx = tmmsss_array[...,3] + 0
    if sxx.size == 1:
        if sxx == 0:
            nse0 = IV
        else:
            nse0 = 1 - tase_array[...,3]/tase_array[...,0]/sxx
    else:
        sum = sxx + 0
        sum[sxx ==0] = 1e-10
        mse0 = tase_array[...,3]/tase_array[...,0]
        nse0 = 1 - mse0/sum
        nse0[sxx == 0] = IV
    return nse0

# FSS
def FSS(Ob, Fo, window_sizes_list=[3], threshold_list=[50], Masker=None):
    '''

    :param Ob: 实况数据 2维的numpy
    :param Fo: 实况数据 2维的numpy
    :param window_sizes_list: 卷积窗口宽度的列表，以格点数为单位
    :param threshold_list:  事件发生的阈值
    :param Masker:  2维的numpy检验的关注区域，在Masker网格值取值为0或1，函数只对网格值等于1的区域的数据进行计算。
    :return:
    '''
    shape = Ob.shape
    nw = len(window_sizes_list)
    # print(nw)
    nt = len(threshold_list)
    fss = np.zeros((nw, nt))
    for i in range(nw):
        kernel = np.ones((nw, nw))
        # print(kernel)
        ws = np.sum(kernel)
        if Masker is not None:
            masker_sum = np.convolve(Masker, kernel, mode="same") + 1e-10
        else:
            masker_sum = np.ones(shape) * ws + 1e-10
        for j in range(nt):
            ob_hap = np.zeros(shape)
            ob_hap[Ob > threshold_list[j]] = 1
            fo_hap = np.zeros(shape)
            fo_hap[Fo > threshold_list[j]] = 1
            ob_hap_sum = np.convolve(ob_hap, kernel, mode="same")
            fo_hap_sum = np.convolve(fo_hap, kernel, mode="same")
            ob_hap_p = ob_hap_sum / masker_sum
            fo_hap_p = fo_hap_sum / masker_sum
            a1 = np.sum(np.power(ob_hap_p - fo_hap_p, 2))
            a2 = np.sum(np.power(ob_hap_p, 2)) + np.sum(np.power(fo_hap_p, 2))
            fss[i, j] = 1 - a1 / (a2 + 1e-10)
    return fss


