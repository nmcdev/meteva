# -*-coding:utf-8-*-
import math
import copy
import numpy as np
from . import data_pre
import meteva

def estimate_negatives(look):
    #根据 目标间平均距离估算negative的数量
    pass

def feature_table(look):
    #x = copy.deepcopy(look)
    out = {}
    grid0 = look["grid"]
    zeros = np.zeros((grid0.nlat,grid0.nlon))
    label_list_ob = look["label_list_ob"]
    for id in label_list_ob:
        index = look["grd_ob_features"][id]
        min_y = np.min(index[0])
        max_y = np.max(index[0])+1

        min_x = np.min(index[1])
        max_x = np.max(index[1])+1

        zeros[min_y:max_y,min_x:max_x] = 1

    area = np.sum(zeros) + 1e-6
    nob_all = int(len(label_list_ob) * grid0.nlat * grid0.nlon / area)+1

    zeros = np.zeros((grid0.nlat,grid0.nlon))
    label_list_fo = look["label_list_fo"]
    for id in label_list_fo:
        index = look["grd_fo_features"][id]
        min_y = np.min(index[0])
        max_y = np.max(index[0]) + 1

        min_x = np.min(index[1])
        max_x = np.max(index[1]) + 1

        zeros[min_y:max_y, min_x:max_x] = 1

    area = np.sum(zeros) + 1e-6
    nfo_all = int(len(label_list_fo) * grid0.nlat * grid0.nlon / area) + 1

    n_all = max(nob_all,nfo_all)
    label_list_matched = look["label_list_matched"]
    hit = len(label_list_matched)
    unmatched = look['unmatched']
    miss = len(unmatched["ob"])
    false_alarm = len(unmatched["fo"])
    correct_negetive = n_all - (hit + miss + false_alarm)
    if correct_negetive<0: correct_negetive = 0

    hfmc = np.array([hit,false_alarm,miss,correct_negetive])

    ets = meteva.method.ets_hfmc(hfmc)
    pod = meteva.method.pod_hfmc(hfmc)
    pofd = meteva.method.pofd_hfmc(hfmc)
    far = meteva.method.far_hfmc(hfmc)
    hss = meteva.method.hss_yesorno_hfmc(hfmc)

    theta = {'ets': ets, 'pod': pod, 'pofd': pofd, 'far': far, 'hss': hss}
    tab = {'Hits': hit, 'Misses': miss, 'False alarms': false_alarm, 'Correct negatives': correct_negetive}
    out['contingency_table_yesorno'] = tab
    out['score'] = theta
    return out

def feature_table_old(look, fudge=1e-08, hits_random=None, correct_negatives=None, fA=0.05):

    x = copy.deepcopy(look)
    out = {}
    #m = x["unmatched"]["matches"]
    #hits = m.shape[0]
    m = x["matches"]

    #if (x['match_type'] == 'deltamm'):
    #    hits = m['ob'].shape[0]
    if x['match_type'] in ['centmatch' ,'deltamm' ,'minboundmatch',"MergeForce","unimatch"]:
        hits = len(m[:, 0])
    miss = get_length(x['unmatched']['ob'])
    fa = get_length(x['unmatched']['fo'])
    #No = x['Xlabeled'].max()
    #Nf = x['Ylabeled'].max()
    Xfeats = data_pre.pick_labels(x['grd_ob_features'])
    Yfeats = data_pre.pick_labels(x['grd_fo_features'])
    No = len(Xfeats)
    Nf = len(Yfeats)

    if correct_negatives is None:
        bigD = (1 - fA) * No / fA - Nf
        if bigD < 0:
            print(
                "FeatureTable: attempted to estimate a value for correct.negatives," 
                "but got a negative answer.  Setting to NA.")
            bigD = None
            bigD = 1
        elif bigD == 0:
            bigD = fudge
    else:
        bigD = correct_negatives
    if hits_random is None:
        hits_random = (Nf * No) / (Nf + miss + bigD)

    #print(bigD)
    denom = Nf + miss - hits_random
    if denom == 0:
        denom = fudge
    GSS = (hits - hits_random) / denom
    s = (hits + miss) / bigD
    POD = hits / (hits + miss + fudge)
    SH2 = POD * (1 - POD) / (hits + miss + fudge)
    POD_se = math.sqrt(SH2)
    FArate = fa / (fa + bigD)
    SF2 = FArate * (1 - FArate) / (fa + bigD)
    FArate_se = math.sqrt(SF2)
    FAR = fa / (hits + fa + fudge)
    FAR_se = math.sqrt(
        (FAR ** 4) * ((1 - POD) / (hits + fudge) + (1 - POD) / (fa + fudge)) * (hits ** 2 / (fa ** 2 + fudge)))
    HSS = 2 * (hits * bigD - fa * miss) / ((hits + miss) * (miss + bigD) + (hits + fa) * (fa + bigD) + fudge)
    SHSS2 = SF2 * (HSS ** 2) * (1 / (POD - FArate + fudge) + (1 - s) * (1 - 2 * s)) ** 2 + SH2 * (HSS ** 2) * (
            1 / (POD - FArate + fudge) - s * (1 - 2 * s)) ** 2
    HSS_se = math.sqrt(SHSS2)
    if 2 - HSS == 0:
        GSS_se = math.sqrt(4 * SHSS2 / fudge)
    else:
        GSS_se = math.sqrt(4 * SHSS2 / ((2 - HSS) ** 4))
    theta = {'ets': GSS, 'pod': POD, 'pofd': FArate, 'far': FAR, 'hss': HSS}
    theta_se = {'ETS': GSS_se, 'POD': POD_se, 'POFD': FArate_se, 'FAR': FAR_se, 'HSS': HSS_se}
    #out['se'] = theta_se
    tab = {'Hits': hits, 'Misses': miss, 'False alarms': fa, 'Correct negatives': bigD}
    out['contingency_table_yesorno'] = tab
    out['score'] = theta
    return out

def get_length(x):
    data_type = type(x).__name__
    # 此处应该将调用方法中的‘None’改为None
    if data_type == "str" and x == 'NULL':
        return 0
    elif data_type == "int" or data_type == "float":
        return 1
    elif data_type == "DataFrame" or data_type == "ndarray":
        return x.size
    #添加set类型
    elif data_type == "set" or data_type == "list":
        return len(x)
    else:
        print("传入类型错误")
        raise Exception("传入类型错误")


