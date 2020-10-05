
import numpy as np
from sklearn.metrics import roc_auc_score
#from sklearn.metrics import brier_score_loss
from meteva.base.tool.math_tools import ss_iteration
from meteva.base import IV
from meteva.method.yes_or_no.score import pofd_hfmc,pod_hfmc



def tems(Ob, Fo):
    '''
    计算bs评分的中间结果
    :param Ob:
    :param Fo:
    :return:
    '''
    Ob_shape = Ob.shape
    Fo_shape = Fo.shape
    tems_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    for line in range(new_Fo_shape[0]):
        count = Ob.size
        mx = np.mean(Ob)
        sxx = np.mean(np.power(Ob - mx, 2))
        error2 = np.sum(np.power(new_Fo[line,:] - Ob, 2))
        tems_list.append(np.array([count, error2, mx, sxx]))
    tems_array = np.array(tems_list)
    shape = list(Fo_shape[:ind])
    shape.append(4)
    tems_array = tems_array.reshape(shape)
    return tems_array

def tems_merge(tems0, tems1):
    '''
    :param tems0:
    :param tems1:
    :return:
    '''
    tems_array_list = []
    tems0_shape = list(tems0.shape)
    tems1_shape = list(tems1.shape)
    if tems0_shape != tems1_shape:
        print('tems0和tems0维度不匹配')
        return
    tems0 = tems0.reshape((-1, 4))
    tems1 = tems1.reshape((-1, 4))
    new_tmmsss1_shape = tems1.shape
    for line in range(new_tmmsss1_shape[0]):
        tems1_piece = tems1[line, :]
        tems0_piece = tems0[line, :]

        count_total, mx_total, sxx_total = ss_iteration(tems0_piece[0], tems0_piece[2], tems0_piece[3], tems1_piece[0],
                                                        tems1_piece[2], tems1_piece[3])
        error_total = tems0_piece[1] + tems1_piece[1]
        tems_array_list.append(np.array([count_total, error_total, mx_total, sxx_total]))
    tems_array = np.array(tems_array_list)
    tems_array = tems_array.reshape(tems0_shape)
    return tems_array
def bs(Ob, Fo):
    '''
    brier_score 评分
    :param Ob: 输入的概率化实况，多维的numpy，发生了则取值为1，未发生则取值为0
    :param Fo: 预报的概率值，多维的numpy
    :return: 实数形式的评分值
    '''
    '''
    Ob_shape = Ob.shape
    Fo_shape = Fo.shape
    bs_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')

        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    for line in range(new_Fo_shape[0]):
        #bs0 = brier_score_loss(Ob.flatten(), new_Fo[line, :].flatten())
        bs0 = np.mean((Ob-new_Fo[line, :])**2)
        bs_list.append(bs0)
    if len(bs_list) == 1:
        bs_array = bs_list[0]
    else:
        bs_array = np.array(bs_list)
        shape = list(Fo_shape[:ind])
        bs_array = bs_array.reshape(shape)
        
    '''
    tems_array = tems(Ob,Fo)
    bs_array = bs_tems(tems_array)
    return bs_array

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

def roc_auc(Ob, Fo):
    '''
    :param Ob: 输入的概率化实况，多维的numpy，发生了则取值为1，未发生则取值为0
    :param Fo: 预报的概率值，多维的numpy
    :return: 实数形式的评分值
    '''
    ob = Ob.flatten()
    Ob_shape = Ob.shape
    Fo_shape = Fo.shape
    roc_auc_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')

        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    for line in range(new_Fo_shape[0]):
        roc_auc_list.append(roc_auc_score(ob, new_Fo[line, :].flatten()))
    if len(roc_auc_list) == 1:
        roc_auc_array = roc_auc_list[0]
    else:
        roc_auc_array = np.array(roc_auc_list)
        shape = list(Fo_shape[:ind])
        roc_auc_array = roc_auc_array.reshape(shape)
    return roc_auc_array

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