import nmc_verification.nmc_vf_method.multi_category as mc
import numpy as np
if __name__ == '__main__':

    ob = np.array([11, 13, 15, 12, 13, 14, 15, 13])
    fo = np.array([15, 13, 15, 12, 14, 14, 15, 13])
    mc.table.multi_category_contingency_table(ob, fo)

