import numpy as np
from nmc_verification.nmc_vf_base.tool.math_tools import mean_iteration,sxy_iteration,ss_iteration

def tase(Ob,Fo):
    '''
    计算平均误差、平均绝对误差、均方误差、均方根误差的中间结果
    -----------------------------
    :param Ob: 实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return: python 元组
    '''
    total_count = Ob.size
    e_sum = np.sum(Ob - Fo)
    ae_sum = np.sum(np.abs(Ob - Fo))
    se_sum = np.sum(np.square(Ob - Fo))
    return total_count,e_sum,ae_sum,se_sum
def me(Ob, Fo):
    '''
    me 求两组数据的误差平均值
    -----------------------------
    :param Ob: 实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return: 实数，最优值为0
    '''
    mean_error = np.mean(Fo - Ob)
    return mean_error
def me_tase(tase_list):
    '''
    me 求两组数据的误差平均值
    :param tase_list,一个组元的列表，其中每个组元为(total_count,e_sum,ae_sum,se_sum),分别代表由部分数据计算得到的
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到1的实数，完美值为1
    '''
    tase_array = np.array(tase_list)
    tase_array_sum = np.sum(tase_array, axis=0)
    total_count = tase_array_sum[0]
    e_sum = tase_array_sum[1]
    mean_error = e_sum/total_count
    return mean_error
def mae(Ob, Fo):
    '''
    mae对两组数据求平均绝对值误差
    -----------------------
    :param Ob:实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return: mean_abs_error
    '''
    mean_abs_error = np.mean(np.abs(Ob - Fo))
    return mean_abs_error
def mae_tase(tase_list):
    '''
    mae 求两组数据的平均绝对误差
    :param tase_list,一个组元的列表，其中每个组元为(total_count,e_sum,ae_sum,se_sum),分别代表由部分数据计算得到的
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到1的实数，完美值为1
    '''
    tase_array = np.array(tase_list)
    tase_array_sum = np.sum(tase_array, axis=0)
    total_count = tase_array_sum[0]
    ae_sum = tase_array_sum[2]
    mean_abs_error = ae_sum/total_count
    return mean_abs_error
def mse(Ob, Fo):
    '''
    mse  求两组数据的均方误差
    ----------------------------------
    :param Ob:实况数据 多维numpy
    :param Fo:预测数据 多维numpy
    :return: mean_sqrt_error
    '''
    mean_sqrt_error = np.mean(np.square(Ob - Fo))
    return mean_sqrt_error
def mse_tase(tase_list):
    '''
    mse 求两组数据的均方误差
    :param tase_list,一个组元的列表，其中每个组元为(total_count,e_sum,ae_sum,se_sum),分别代表由部分数据计算得到的
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到1的实数，完美值为1
    '''
    tase_array = np.array(tase_list)
    tase_array_sum = np.sum(tase_array, axis=0)
    total_count = tase_array_sum[0]
    se_sum = tase_array_sum[3]
    mean_squre_error = se_sum/total_count
    return mean_squre_error
def rmse(Ob, Fo):
    '''
    rmse 求两组数据的均方根误差
    ------------------------------
    :param Ob:实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return:mean_sqrt_error
    '''
    mean_sqrt_error = np.sqrt(np.mean(np.square(Ob - Fo)))
    return mean_sqrt_error
def rmse_tase(tase_list):
    '''
    mse 求两组数据的均方根误差
    :param tase_list,一个组元的列表，其中每个组元为(total_count,e_sum,ae_sum,se_sum),分别代表由部分数据计算得到的
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到1的实数，完美值为1
    '''
    tase_array = np.array(tase_list)
    tase_array_sum = np.sum(tase_array, axis=0)
    total_count = tase_array_sum[0]
    se_sum = tase_array_sum[3]
    mean_squre_error = se_sum/total_count
    rmse = np.sqrt(mean_squre_error)
    return rmse
def me_mae_rmse(Ob,Fo):
    '''
    同时计算平均误差、平均绝对误差、均方根误差
    :param Ob: 实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return: python 元组
    '''
    mean_error = me(Ob,Fo)
    mean_abs_error = mae(Ob,Fo)
    rmse1 = rmse(Ob,Fo)
    return mean_error,mean_abs_error,rmse1
def me_mae_rmse_tase(tase_list):
    '''
    同时计算平均误差、平均绝对误差、均方根误差
    :param tase_list,一个组元的列表，其中每个组元为(total_count,e_sum,ae_sum,se_sum),分别代表由部分数据计算得到的
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: python 元组
    '''
    tase_array = np.array(tase_list)
    tase_array_sum = np.sum(tase_array, axis=0)
    total_count = tase_array_sum[0]
    e_sum = tase_array_sum[1]
    mean_error = e_sum/total_count
    ae_sum = tase_array_sum[2]
    mean_abs_error = ae_sum/total_count
    se_sum = tase_array_sum[3]
    mean_squre_error = se_sum/total_count
    rmse = np.sqrt(mean_squre_error)
    return mean_error,mean_abs_error,rmse
def bias(Ob, Fo):
    '''
    bias 求预测数据和实况数据的平均值的比
    ------------------------------
    :param Ob:实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return:  bias0
    '''
    bias0 = np.mean(Fo) / (np.mean(Ob) + 1e-6)
    return bias0
def corr(Ob, Fo):
    '''
    corr 求实况数据还和预测数据之间的相关系数
    -----------------------------
    :param Ob: 实况数据 不定长维度的numpy
    :param Fo: 测试数据 不定长维度的numpy
    :return: corr0
    '''
    ob_f = Ob.flatten()
    fo_f = Fo.flatten()
    corr0 = np.corrcoef(ob_f, fo_f)[0, 1]
    return corr0
def corr_cmmsss(cmmsss_list):
    '''
    根据中间结果列表，计算相关系数
    :param cmmsss_list:
    :return: -1到1的实数
    '''
    cmmsss = cmmsss_list[0]
    count_total = cmmsss[0]
    mx_total = cmmsss[1]
    my_total = cmmsss[2]
    sxx_total = cmmsss[3]
    syy_total = cmmsss[4]
    sxy_total = cmmsss[5]
    for i in range(len(cmmsss_list)-1):
        cmmsss1 = cmmsss_list[i+1]
        count_new = cmmsss1[0]
        mx_new = cmmsss1[1]
        my_new = cmmsss1[2]
        sxx_new = cmmsss1[3]
        syy_new = cmmsss1[4]
        sxy_new = cmmsss1[5]
        _, _, sxx_total = ss_iteration(count_total,mx_total,sxx_total,count_new,mx_new,sxx_new)
        _, _, syy_total = ss_iteration(count_total,my_total,syy_total,count_new,my_new,syy_new)
        count_total,mx_total,my_total,sxy_total = sxy_iteration(count_total,mx_total,my_total,sxy_total,
                                                                count_new,mx_new,my_new,sxy_new)
    corr = sxy_total/np.sqrt(sxx_total * syy_total)
    return corr
def cmmsss(Ob,Fo):
    '''
    统计相关系数等检验量所需的中间变量
    :param Ob: 实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return: python 元组，其元素为根据Ob和Fo
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
    return count,mx,my,sxx,syy,sxy
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
def nse(Ob,Fo):
    '''
    nse纳什系数, 常用于计算两个非正态序列的相对误差情况，取值范围为负无穷至1，其取值越接近1代表越准确
    :param Ob:实况数据 不定长维度的numpy
    :param Fo:测试数据 不定长维度的numpy
    :return:
    '''
    mob = np.mean(Ob)
    qdob = np.mean(np.power(Ob - mob,2))
    if qdob ==0:
        return -9999
    else:
        return 1-np.mean(np.power(Ob - Fo,2))/qdob
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


