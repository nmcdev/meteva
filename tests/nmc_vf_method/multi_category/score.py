import nmc_verification.nmc_vf_method.multi_category.score as score
import numpy as np
if __name__ == '__main__':

    ob = np.random.randint(1, 10, 10)
    of = np.random.randint(1, 10, 10)


    hk = score.hk(ob, of,grade_list=[3,5])
    print('hk评分：', hk)

    hss = score.hss(ob,of)
    print('hss评分：', hss)


    accuracy = score.accuracy(ob,of,[5,8])
    print('accuracy评分',accuracy)

