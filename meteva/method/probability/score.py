
import numpy as np
from sklearn.metrics import roc_auc_score
from sklearn.metrics import brier_score_loss
from meteva.base.tool.math_tools import ss_iteration
from meteva.base import IV
from meteva.method.yes_or_no.score import pofd_hfmc,pod_hfmc



def tems(Ob, Fo):
    '''

    :param Ob:
    :param Fo:
    :return:
    '''
    count = Ob.size
    mx = np.mean(Ob)
    sxx = np.mean(np.power(Ob - mx, 2))
    error2 = np.sum(np.power(Fo - Ob, 2))
    return np.array([count, error2, mx,sxx])

def tems_merge(tems0,tems1):
    '''

    :param tems0:
    :param tems1:
    :return:
    '''
    count_total, mx_total, sxx_total = ss_iteration(tems0[0], tems0[2],tems0[3], tems1[0], tems1[2],tems1[3])
    error_total = tems0[1] + tems1[1]
    return np.array([count_total,error_total,mx_total,sxx_total])

def bs(Ob,Fo):
    '''
    brier_score 评分
    :param Ob: 输入的概率化实况，多维的numpy，发生了则取值为1，未发生则取值为0
    :param Fo: 预报的概率值，多维的numpy
    :return: 实数形式的评分值
    '''
    bs0 =brier_score_loss(Ob.flatten(),Fo.flatten())
    return bs0

def bs_tems(tems_array):
    '''

    :param tems_array:
    :return:
    '''
    total_count = tems_array[...,0]
    e2_sum = tems_array[...,1]
    brier = e2_sum / total_count
    return brier



def bss(Ob,Fo):
    '''
    :param Ob: 输入的概率化实况，多维的numpy，发生了则取值为1，未发生则取值为0
    :param Fo: 预报的概率值，多维的numpy
    :return: 实数形式的评分值
    '''
    p_climate = np.sum(Ob)/Ob.size
    Fo_climate = np.ones_like(Ob) * p_climate
    bs0 = bs(Ob,Fo)
    bs_climate = bs(Ob,Fo_climate)
    if bs_climate !=0:
        bss0 = 1 - bs0/bs_climate
    else:
        if bs0 ==0:
            bss0 = 1
        else:
            bss0 = IV
    return bss0

def bss_tems(tems_array):
    bs0 = bs_tems(tems_array)
    sxx_total = tems_array[...,3]

    bs_climate = sxx_total
    if bs_climate.size == 1:
        if bs_climate !=0:
            bss0 = 1 - bs0/bs_climate
        else:
            if bs0 ==0:
                bss0 = 1
            else:
                bss0 = IV
    else:
        under = np.zeros_like(bs_climate)
        under[...] = bs_climate[...]
        under[bs_climate == 0] = 1
        bss0 = 1 - bs0 / under
        bss0[bs_climate ==0] = IV
    return bss0

def roc_auc(Ob,Fo):
    '''
    :param Ob: 输入的概率化实况，多维的numpy，发生了则取值为1，未发生则取值为0
    :param Fo: 预报的概率值，多维的numpy
    :return: 实数形式的评分值
    '''
    return roc_auc_score(Ob,Fo)

def roc_auc_hnh(hnh_array):
    '''

    :param hnh_array:
    :return:
    '''
    ngrade = hnh_array.shape[-2]
    total_grade_num = hnh_array[...,:,0]
    observed_grade_num = hnh_array[...,:,1]
    shape = list(total_grade_num.shape)
    shape.append(4)
    shape = tuple(shape)
    hfmc = np.zeros(shape)
    total_hap = np.sum(observed_grade_num,axis= -1)
    total_num = np.sum(total_grade_num,axis= -1)
    sum_axis = len(observed_grade_num.shape) - 1
    for i in range(ngrade):
        hfmc[...,i, 0] = np.sum(observed_grade_num[...,i:],axis=sum_axis)
        hfmc[...,i, 1] = np.sum(total_grade_num[...,i:],axis=sum_axis) - hfmc[...,i, 0]
        hfmc[...,i, 2] = total_hap - hfmc[...,i, 0]
        hfmc[...,i, 3]= total_num - (hfmc[...,i, 0] + hfmc[...,i, 1]+ hfmc[...,i, 2])

    far = pofd_hfmc(hfmc)
    pod = pod_hfmc(hfmc)

    start1 = np.ones_like(total_num)
    end0 = np.zeros_like(total_num)
    auc = (start1 - far[...,0]) * (start1 + pod[...,0])
    for i in range(1,ngrade):
        auc += (far[...,i-1] - far[...,i]) * (pod[...,i-1] + pod[...,i])
    auc += (far[...,-1] - end0) * (pod[...,-1])
    auc /= 2

    return auc