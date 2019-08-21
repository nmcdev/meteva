import nmc_verification.nmc_vf_method.continuous.score as score
import numpy as np

if __name__ == '__main__':
    ob = np.array([1, 3, 4, 6, 10, 9, 15, 14, 13, 14, 16, 9, 8, 15, 11])
    of = np.array([2, 3, 5, 5, 7, 10, 10, 13, 11, 14, 15, 10, 8, 11, 12])

    me_score = score.me(ob, of)
    print('误差平均值：', me_score)

    mae_score = score.mae(ob, of)
    print('平均绝对值误差：', mae_score)

    mse_score = score.mse(ob, of)
    print('均方误差：', mse_score)

    rmse_score = score.rmse(ob, of)
    print('均方根误差：', rmse_score)

    bias_score = score.bias(ob, of)
    print('均值比：', bias_score)

    corr_score = score.corr(ob, of)
    print('相关系数：', corr_score)

    are_score = score.mre(ob, of)
    print('平均相对误差：', are_score)

    ob = np.array(np.random.randint(0, 10, 20))

    of = np.array(np.random.randint(0, 10, 20))
    print(ob)
    #
    # '''功能不明'''
    # FSS_score = score.FSS(ob, of)
    # print('FSS:', FSS_score)
