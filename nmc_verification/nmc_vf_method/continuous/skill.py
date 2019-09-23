def mre_skill(mre, mre_base):
    if mre_base == 0:
        if mre > 0:
            return -999
        else:
            return 0
    else:
        smre1 = (mre_base - mre) / mre_base
        return smre1