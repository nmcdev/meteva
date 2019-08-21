import nmc_verification.nmc_vf_method.yes_or_no as yon
import numpy as np

if __name__ == '__main__':
    ob = np.array([1, 0, 1, 0, 1, 1, 0, 0])
    of = np.array([0, 0, 1, 0, 0, 1, 1, 0])

    rain_score = yon.score.pc_of_sunny_rainy(ob, of)
    print('晴雨准确率：', rain_score)

    abcd_s_r_score = yon.score.hmfn_of_sunny_rainy(ob, of)
    print('晴雨准确率:', abcd_s_r_score)

    hot_rate = yon.score.hit_rate(ob, of)
    print('命中率：', hot_rate)

    fal_rate = yon.score.fal_rate(ob, of)
    print('误报率:', fal_rate)

    mis_rate = yon.score.mis_rate(ob, of)
    print('漏报率：', mis_rate)

    bias = yon.score.bias(ob, of)
    print('bias评分：', bias)

    bias_extend = yon.score.bias_extend(ob, of)
    print(bias_extend)

    ts = yon.score.ts(ob, of)
    print('ts评分：', ts)

    hit, mis, fal, cn = yon.score.hmfn(ob, of)
    print('hit, mis, fal, cn:', hit, mis, fal, cn)
    # print(type(hit))

    ts_hmfn = yon.score.ts_hmfn(hit, mis, fal)
    print('ts hmfn 评分：', ts_hmfn)

    ets = yon.score.ets(ob, of)
    print('ets评分：', ets)

    ets_hmfn = yon.ets_hmfn(hit, mis, fal, cn)
    print('ets_hmfn评分：', ets_hmfn)

    ob = np.array([1, 2, 3, 13, 11, 12, 20, 21, 22])
    fo = np.array([1, 2, 3, 13, 11, 12, 20, 21, 22])
    print(np.sum([ob[0], ob[1]]))
    # fo = np.array([1, 11, 9, 11, 13, 9, 23, 18, 22])
    #     hit, mis, fal, cn = yon.score.hmfn(ob, fo, threshold_list=[10, 20])
    #
    #     merge_data = np.vstack((hit, mis, fal))
    #     # print(merge_data)
    #     print(merge_data[:,1])
    #     print(type(merge_data[:,1]))
    #     print(np.sum(merge_data[:,1]))
    #     # tss = ts_hmfn(hit, mis, fal)
    # ts = yon.score.ts(ob, fo, grade_list=[10, 20])
    # print('ts评分：', ts)
    # print(tss)
    # a = [0, 1]
    # print(len(a))
