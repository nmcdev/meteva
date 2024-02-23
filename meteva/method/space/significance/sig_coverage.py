#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 27 18:29:57 2022

@author: tangbuxing
"""
import numpy as np


def CI_fun(CI_field, est_field, replacement=np.nan):
    test = est_field[0.5 * CI_field < abs(est_field)] = replacement
    return test


def inside(DF):
    # result = CI_fun(DF['Upper'] - DF['Lower'], DF['Estimate'])
    aa = DF['Upper'] - DF['Lower']
    bb = DF['Estimate']
    result = 0.5 * aa < abs(bb)  #满足条件代表平均值是显著偏离1的
    return result


def sig_coverage(DF):
    out = {}
    tmp = inside(DF)
    #sum(DF['Estimate'] == None) =0 表示df中的内容是误差均值，否则表示其它暂无支持的统计内容
    # out 是表示均值显著的占比。
    out = sum(tmp[tmp == 1]) / len(tmp) - sum(DF['Estimate'] == None)
    return out



