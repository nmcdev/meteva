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
