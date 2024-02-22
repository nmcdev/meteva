# -*- coding: utf-8 -*-
"""
Created on Tue Mar  2 11:31:55 2021

@author: 1
"""
from pynverse import inversefunc  # 求逆函数的包
import numpy as np
import pandas as pd
import math


def vxstats(x, xhat, which_stats=None, subset=None):
    if which_stats is None:
        which_stats = ["bias", "ts", "ets", "pod", "far", "f", "hk", "bcts", "bcets"]
    out = {}
    xdim = xhat.shape
    # 将缺省值填为0
    if type(x) == pd.DataFrame:
        x = x.fillna(0)
    if type(xhat) == pd.DataFrame:
        xhat = xhat.fillna(0)

    if "mse" in which_stats:
        if subset is None:
            Nxy = np.sum(np.sum((xhat != np.nan) & (x != np.nan), axis=0))
            out['mse'] = np.sum(np.sum((xhat - x) ** 2, axis=0)) / Nxy
        else:
            out['mse'] = np.mean((xhat[subset] - x[subset]) ** 2)
    elementExist = []
    for i, value in enumerate(which_stats):
        elementExist.append(value in ['bias', 'ts', 'ets', 'pod', 'far', 'f', "hk", "bcts", "bcets"])
    if any(elementExist):
        if xhat is not bool:
            xhat = xhat != 0
        if x is not bool:
            x = x != 0
        if subset is None:
            hits = np.sum(np.sum(xhat & x))
            miss = np.sum(np.sum((~xhat) & x))
            fa = np.sum(np.sum(xhat & (~x)))
            elementExist2 = []
            for i, value in enumerate(["ets", "f", "hk"]):
                elementExist2.append(value in which_stats)
            if any(elementExist2):
                cn = np.sum(np.sum((~xhat) & (~x)))
        else:
            # hits <- sum(c(Xhat)[subset] & c(X)[subset], na.rm = TRUE)
            hits = np.sum(np.sum(xhat[subset] & x[subset]))
            # miss <- sum(!c(Xhat)[subset] & c(X)[subset], na.rm = TRUE)
            miss = np.sum(np.sum((~xhat[subset]) & x[subset]))
            # fa <- sum(c(Xhat)[subset] & !c(X)[subset], na.rm = TRUE)
            fa = np.sum(np.sum(xhat[subset] & (~x[subset])))
            elementExist2 = []
            for i, value in enumerate(["ets", "f", "hk"]):
                elementExist2.append(value in which_stats)
            if any(elementExist2):
                cn = np.sum(np.sum((~xhat[subset]) & (~x[subset])))
        if "bias" in which_stats:
            if (hits + fa == 0) and (hits + miss == 0):
                out['bias'] = 1
            else:
                out['bias'] = (hits + fa) / (hits + miss)
        if "ts" in which_stats:
            if hits == 0:
                out['ts'] = 0
            else:
                out['ts'] = hits / (hits + miss + fa)
        if "ets" in which_stats:
            if ((hits + miss == 0) or (hits + fa == 0)):
                hits_random = 0
            else:
                hits_random = float(hits + miss) * float(hits + fa) / float(hits + miss + fa + cn)
            if (hits + miss + fa == 0):
                out['ets'] = 0
            else:
                out['ets'] = (hits - hits_random) / (hits + miss + fa - hits_random)
        elementExist3 = []
        for i, value in enumerate(["pod", "hk"]):
            elementExist3.append(value in which_stats)
        if any(elementExist3):
            if (hits + miss == 0):
                pod = 0
            else:
                pod = hits / (hits + miss)
            if "pod" in which_stats:
                out['pod'] = pod
        if "far" in which_stats:
            if (hits + fa == 0):
                out['far'] = 0
            else:
                out['far'] = fa / (hits + fa)
        elementExist4 = []
        for i, value in enumerate(["f", "hk"]):
            elementExist4.append(value in which_stats)
        if any(elementExist4):
            if (cn + fa == 0):
                f = 0
                out['f'] = f
            else:
                f = fa / (cn + fa)
                out['f'] = fa / (cn + fa)
            if "hk" in which_stats:
                f = pod - f
                out['hk'] = f
        elementExist5 = []
        for i, value in enumerate(["bcts", "bcets"]):
            elementExist5.append(value in which_stats)
        if any(elementExist5):
            nF = hits + fa
            nO = hits + miss
            lf = math.log(nO / miss)
            LambertW = (lambda y: y * math.exp(y))
            # Ha = nO - (fa/lf) * LambertW((nO/fa) * lf)
            Ha = nO - (fa / lf) * inversefunc(LambertW, y_values=((nO / fa) * lf))
            if "bcts" in which_stats:
                out['bcts'] = Ha / (2 * nO - hits)
            if "bcets" in which_stats:
                out['bcets'] = (Ha - (nO ** 2) / (hits + miss + fa +
                                                  cn)) / (2 * nO - Ha - (nO ** 2) / (hits + miss + fa + cn))
    out['class'] = "vxstats"
    return out
