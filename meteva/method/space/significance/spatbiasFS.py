#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 10 10:54:21 2021

"""
import numpy as np
import pandas as pd
#import pyreadr
import sys

#sys.path.append(r'/Users/tangbuxing/Desktop/tra_test-SAL/fieldSignficance/lib')
from meteva.method.space.field_significance import LocSig, is_sig

# import matplotlib.pyplot as plt

def spatbiasFS(X, Y, loc='NULL', block_length='NULL', alpha_boot=0.05,
               field_sig=0.05, bootR=1000, ntrials=1000, show=False):
    out = {}
    '''
    if (!is.null(loc)) {
        data.name <- c(as.character(substitute(X)), as.character(substitute(Y)), 
                   as.character(substitute(loc)))
        names(data.name) <- c("verification", "forecast", "locations")
        }
    else {
        data.name <- c(as.character(substitute(X)), as.character(substitute(Y)))
        names(data.name) <- c("verification", "forecast")
        }
    out$data.name <- data.name
    '''
    errfield = Y - X
    hold = LocSig.LocSig(Z=errfield, numrep=bootR, block_length=block_length,
                         alpha=alpha_boot)
    res = is_sig.is_sig(errfield, hold, n=ntrials, fld_sig=field_sig, show=show)
    out['block_boot_results'] = hold
    out['sig_results'] = res
    out['field_significance'] = field_sig
    out['alpha_boot'] = alpha_boot
    out['bootR'] = bootR
    out['ntrials'] = ntrials
    out['class'] = "spatbiasFS"

    return out


if __name__ == '__main__':
    # 导入数据，并裁切一部分
    # obsData = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/fieldSignficance/data/GFSNAMobsEx.rda')[
    #     'GFSNAMobsEx']
    # fcstData = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/fieldSignficance/data/GFSNAMfcstEx.rda')[
    #     'GFSNAMfcstEx']
    # locData = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/fieldSignficance/data/GFSNAMlocEx.rda')[
    #     'GFSNAMlocEx']
    # locId = (locData["Lon"] >= -90) & (locData["Lon"] <= -75) & (locData["Lat"] <= 40)
    # locSub = locData[locId]
    # GFSobsSub = obsData.T[locId].T
    # GFSfcstSub = fcstData.T[locId].T

    ob = np.random.randn(100,400)
    fo = np.random.randn(100,400) + 0.1
    # 调用示例
    lookFS = spatbiasFS(X=ob, Y=fo)

    '''
    #参数赋值
    X = GFSobsSub
    Y = GFSfcstSub
    loc=locSub
    block_length = 'NULL'
    alpha_boot = 0.05
    field_sig = 0.05
    bootR = 500
    ntrials=500
    show = True
    '''



