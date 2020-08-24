from meteva.base import IV

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