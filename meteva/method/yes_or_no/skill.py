from meteva.base import  IV
#计算晴雨预报相对技巧
def pc_skill(pc,pc_base):
    '''

    :param pc:
    :param pc_base:
    :return:
    '''
    if pc_base == 1:
        if pc <1:
            return IV
        else:
            return 0
    else:
        spc1 = (pc - pc_base) / (1 - pc_base)
        return spc1

def spc(pc,pc_base):
    '''

    :param pc: 省台的正确率
    :param pc_base: 中央台的正确率
    :return: 省台相对中央台的预报技巧
    '''
    if pc_base == 1:
        if pc <1:
            return IV
        else:
            return 0
    else:
        skill = (pc - pc_base) / (1 - pc_base)
        return round(skill,3)

#计算Ts评分相对技巧
def ts_skill(ts,ts_base):
    '''

    :param ts:
    :param ts_base:
    :return:
    '''
    if ts_base == 1:
        if ts < 1:
            return IV
        else:
            return 0
    else:
        sts1 = (ts - ts_base) / (1 - ts_base)
        return sts1

def sts(ts,ts_base):
    '''

    :param ts: 省台的ts评分
    :param ts_base: 中央台的ts评分
    :return: 省台相对中央台的预报技巧
    '''
    if ts_base == 1:
        if ts < 1:
            return IV
        else:
            return 0
    else:
        skill = (ts - ts_base) / (1 - ts_base)
        return round(skill,3)

def bias_extend_skill(be,be_base):
    '''

    :param be:
    :param be_base:
    :return:
    '''
    if be_base ==0:
        if be == 0:
            return 0
        else:
            return IV
    else:
        sbi1 = (be_base - be) / be_base
        return sbi1

def sbi(be,be_base):
    '''

    :param be: 省台的偏差幅度
    :param be_base: 中央台的偏差幅度
    :return: 省台相对于中央台的预报技巧
    '''
    if be_base ==0:
        if be == 0:
            return 0
        else:
            return IV
    else:
        skill = (be_base - be) / be_base
        round(skill,3)

def sfa(far,far_base):
    '''

    :param far: 省台空报率
    :param far_base: 中央台空报率
    :return: 省台相对于中央台的预报技巧
    '''
    if far == 0:
        if far_base ==0:
            return 0
        else:
            return IV
    elif far_base == IV:
        if far == IV:
            return 0
        else:
            return -1
    else:
        skill = (far_base - far)/far
        return round(skill,3)


def spo(pod,pod_base):
    '''

    :param far: 省台空报率
    :param far_base: 中央台空报率
    :return: 省台相对于中央台的预报技巧
    '''
    if pod_base == 1:
        if pod ==1:
            return 0
        else:
            return -IV
    else:
        skill= (pod - pod_base) / (1 - pod_base)
        return round(skill,3)
