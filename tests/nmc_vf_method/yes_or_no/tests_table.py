import nmc_verification.nmc_vf_method.yes_or_no as yoa
import numpy as np

if __name__ == '__main__':
    ob = np.array([0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1])
    fo = np.array([0, 1, 1, 0, 0, 0, 1, 0, 1, 0, 1])
    yoa.table.contingency_table(ob,fo)
