
import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.metrics import brier_score_loss

def brier_score(Ob,Fo):
    '''

    :param Ob: 输入的概率化实况，多维的numpy，发生了则取值为1，未发生则取值为0
    :param Fo: 预报的概率值，多维的numpy
    :return: 实数形式的评分值
    '''
    bs0 =brier_score_loss(Ob,Fo)
    return bs0

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
