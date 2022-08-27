from meteva.base import IV
import numpy as np


def mre_skill(mre, mre_base):
    '''
    mre_skill 相对误差技巧，其中mre是精细化网格预报竞赛检验办法中的水量定量相对误差检验指标，
    :param mre:
    :param mre_base:
    :return: 相对技巧值，取值范围为负无穷到1，但负无穷记为-999返回
    '''
    if mre_base == 0:
        if mre > 0:
            return -999
        else:
            return 0
    else:
        smre1 = (mre_base - mre) / mre_base
        return smre1

def sme(mre, mre_base):
    '''
    :param mre: 省台的定量降水相对误差
    :param mre_base: 中央台的定量降水相对误差
    :return: 省台相对于中央台的技巧
    '''
    if mre_base == 0:
        if mre > 0:
            return -IV
        else:
            return 0
    else:
        skill = (mre_base - mre) / mre_base
        return round(skill,3)

def sst(mae,mae_base):
    '''

    :param mae: 省台的平均绝对误差
    :param mae_base: 中央台的平均绝对误差
    :return: 省台相对于中央台的技巧
    '''


    if mae_base == 0:
        skill = 1.01
    else:
        skill = (mae_base - mae)/(mae_base)

    return round(skill,3)


def tbask(ob,fo):

    '''
    根据输入的观测和预报数据计算预报员的基本评分
    ob: 观测数据序列
    fo: 预报数据序列，包含客观预报和预报员预报供两列
    '''
    fo_forecaster = fo[0, :]  # 提取预报员的预报
    error_forecaster = np.abs(fo_forecaster - ob)  # 计算绝对误差
    score_forecaster = np.zeros(error_forecaster.shape)  # 初始化一个基本评分数组
    index = np.where(error_forecaster <= 2)
    score_forecaster[index] = 0.6 # 将误差符合条件站次设为0.6分，其它继续为0

    # 提取模式的预报#############技巧评分
    fo_model = fo[1, :]
    error_model = np.abs(fo_model - ob)  # 计算绝对误差
    skill = np.zeros(ob.shape)  # 初始化一个基本评分数组

    index = np.where((error_model <= 2) & (error_forecaster <= 2))
    skill[index] = 0.6
    index = np.where((error_model >= 2) & (error_forecaster >= 2))
    skill[index] = 0.3
    index = np.where((error_model > 2) & (error_forecaster <= 2))
    skill[index] = 1

    score = score_forecaster + skill

    score_sum = np.sum(score)  # 计算总样本的平均分

    tbask = np.array([ob.size,score_sum])
    return tbask  # 返回总得分

def temp_forecaster_score(ob,fo):


    '''
    根据输入的观测和预报数据计算预报员的基本评分
    ob: 观测数据序列
    fo: 预报数据序列，包含客观预报和预报员预报供两列
    '''

    tbask_array = tbask(ob,fo)
    score = tbask_array[1]/tbask_array[0]
    return score  # 返回总得分


def temp_forecaster_score_tbask(tbask_array):


    score = tbask_array[1]/tbask_array[0]
    return score  # 返回总得分