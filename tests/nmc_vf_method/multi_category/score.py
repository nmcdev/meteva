import nmc_verification.nmc_vf_method.multi_category.score as score
import numpy as np
if __name__ == '__main__':
    ob = np.random.rand(10, 2)
    fo = np.random.rand(10, 2)
    ob10 = ob * 10
    fo10 = fo * 10
    ob_int = ob10.astype(np.int8)
    fo_int = fo10.astype(np.int8)
    grade_list = [3, 5]

    accuracy = score.accuracy(ob_int,fo_int,grade_list)
    print('accuracy评分',accuracy)
    accuracy = score.accuracy(ob_int, fo_int)
    print('accuracy评分',accuracy)

    hss = score.hss(ob,fo)
    print('hss评分：', hss)
    hss = score.hss(ob,fo,grade_list)
    print('hss评分：', hss)

    hk = score.hk(ob, fo,[0.1,10,25])
    print('hk评分：', hk)






