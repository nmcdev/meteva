
import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.metrics import brier_score_loss
from nmc_verification.nmc_vf_base.tool.math_tools import mean_iteration,ss_iteration

def brier_score(Ob,Fo):
    '''

    :param Ob: 输入的概率化实况，多维的numpy，发生了则取值为1，未发生则取值为0
    :param Fo: 预报的概率值，多维的numpy
    :return: 实数形式的评分值
    '''
    bs0 =brier_score_loss(Ob,Fo)
    return bs0

def brier_score_cemmss_list(cemmss_list):
    ce_array = np.array(cemmss_list)
    ce_array_sum = np.sum(ce_array, axis=0)
    total_count = ce_array_sum[0]
    e2_sum = ce_array_sum[1]
    brier = e2_sum / total_count
    return brier

def cemmss(Ob,Fo):
    count = Ob.size
    mx= np.mean(Ob)
    sxx = np.mean(np.power(Ob - mx, 2))
    my = np.mean(Fo)
    syy = np.mean(np.power(Fo - my, 2))
    error2 = np.sum(np.power(Fo - Ob,2))
    return count,error2,mx,my,sxx,syy

def bss(Ob,Fo):
    '''
    :param Ob: 输入的概率化实况，多维的numpy，发生了则取值为1，未发生则取值为0
    :param Fo: 预报的概率值，多维的numpy
    :return: 实数形式的评分值
    '''
    p_climate = np.sum(Ob)/Ob.size
    Fo_climate = np.ones_like(Ob) * p_climate
    bs0 = brier_score(Ob,Fo)
    bs_climate = brier_score(Ob,Fo_climate)
    if bs_climate !=0:
        bss0 = 1 - bs0/bs_climate
    else:
        if bs0 ==0:
            bss0 = 1
        else:
            bss0 = -999
    return bss0

def bss_cemmss(cemmss_list):
    bs0 = brier_score_cemmss_list(cemmss_list)
    cemmss = cemmss_list[0]
    count_total = cemmss[0]
    mx_total = cemmss[1]
    my_total = cemmss[2]
    sxx_total = cemmss[3]

    for i in range(len(cemmss_list) - 1):
        cmmsss1 = cemmss_list[i + 1]
        count_new = cmmsss1[0]
        mx_new = cmmsss1[1]
        my_new = cmmsss1[2]
        sxx_new = cmmsss1[3]
        count_total,my_total = mean_iteration(count_total,my_total,count_new,my_new)
        count_total, mx_total, sxx_total = ss_iteration(count_total, mx_total, sxx_total, count_new, mx_new, sxx_new)

    bs_climate = sxx_total * count_total + (mx_total, - my_total)*(mx_total - my_total)
    if bs_climate !=0:
        bss0 = 1 - bs0/bs_climate
    else:
        if bs0 ==0:
            bss0 = 1
        else:
            bss0 = -999
    return bss0

def roc_auc(Ob,Fo):
    '''
    :param Ob: 输入的概率化实况，多维的numpy，发生了则取值为1，未发生则取值为0
    :param Fo: 预报的概率值，多维的numpy
    :return: 实数形式的评分值
    '''
    return roc_auc_score(Ob,Fo)

    return

def RPS(ob_probablility,fo_probali):
    '''
    RPS用于检验多分类的概率预报和观测的一致性
    :param ob_probablility: 二维数组，其中行数为样本数，列数为待预测的类别数
    ，第i,j个元素表示第i个观测样本预测第j个类别是否发生，是记为1，否记为0
    :param fo_probali: 二维数组，其中行数为样本数，列数为待预测的类别数，第i,j个元素表示第i个预报样本预测第j个类别的发生概率
    :return:
    '''
    pass
