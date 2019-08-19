import nmc_verification.nmc_vf_method.continuous as continuous
import numpy as np

if __name__ == '__main__':
    ob = np.array([1, 3, 4, 6, 8, 9, 15, 14, 13, 14, 16, 9, 8, 10, 11])
    fo = np.array([2, 3, 5, 5, 7, 10, 14, 13, 14, 14, 15, 10, 8, 11, 12])
    continuous.plot.scatter_regress(ob, fo)
    print('scatter_regress执行成功')
    continuous.plot.sorted_ob_fo(ob, fo)
    print('sorted_ob_fo执行成功')
    continuous.plot.box_plot(ob,fo)
    print('box_plot执行成功')

