def mre_skill(mre, mre_base):
    if mre_base == 0:
        return 9999
    else:
        smre1 = (mre_base - mre) / mre_base
        return smre1
