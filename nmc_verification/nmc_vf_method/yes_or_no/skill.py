
#计算晴雨预报相对技巧
def spc(pc,pc_base):
    if pc_base == 1:
        return 9999
    else:
        spc1 = 100 * (pc - pc_base) / (1 - pc_base)
        return spc1

#计算Ts评分相对技巧
def sts(ts,ts_base):
    if ts_base == 1:
        return 9999
    else:
        sts1 = 100 * (ts - ts_base) / (1 - ts_base)
        return sts1

def sbi(be,be_base):
    if be_base ==0:
        return 9999
    else:
        sbi1 = (be_base - be) / be_base
        return sbi1
