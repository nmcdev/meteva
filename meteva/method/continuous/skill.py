
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
