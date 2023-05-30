#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 23 11:29:25 2022

@author: tangbuxing
"""
import numpy as np
import pandas as pd
from sklearn import utils
from sklearn.utils import resample
from sklearn import metrics
from scipy import stats

# boot_CI(booted, conf = 1-alpha, Type = "bac", index = i)
def bootstrap_CI(actual_list, predict_list, num_repeats=1000, stat='roc_auc',
                 confident_lvl=0.95, side='two', random_state=0):
    assert len(actual_list) == len(predict_list)
    try:
        all_stats = []
        for i in range(num_repeats):
            actual_list_resampled, predict_list_resampled = resample(actual_list, predict_list)
            if stat == 'roc_auc':
                #计算二分类
                cur_roc_auc = metrics.roc_auc_score(actual_list_resampled, predict_list_resampled)
                all_stats.append(cur_roc_auc)
        roc_auc_left = np.percentile(all_stats, (1 - confident_lvl) / 2. * 100)
        roc_auc_right = np.percentile(all_stats, (1 + confident_lvl) / 2. * 100)

    except Exception as e:
        # print e
        roc_auc_left, roc_auc_right = float('nan'), float('nan')

    return roc_auc_left, roc_auc_right

if __name__ == '__main__':
    aa = [9, 8, 7, 6, 5, 11, 12, 13, 14, 15, 16]
    bb = [1, 3, 5, 7, 9, 2, 4, 6, 8, 9, 22]
    cc = bootstrap_CI(actual_list = aa, predict_list = bb)

    #data = pd.read_csv(r"/Users/tangbuxing/Desktop/tra_test-SAL/field signficance/data/booted001.csv")
    data = Z
    df = len(data) - 1
    ci = stats.t.interval(alpha = 0.95, df = data, loc=np.mean(data), scale=stats.sem(data))



