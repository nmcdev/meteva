#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Dec 13 17:50:26 2021

"""
import numpy as np
import pandas as pd
import meteva.method as mem
from sklearn.utils import resample


def LocSig(Z, numrep=1000, block_length='NULL', bootfun="mean",
           alpha=0.05, bca=False):
    booted = {}
    if bootfun == 'mean':
        Z = np.ma.masked_array(Z, np.isnan(Z))
        bootfun = np.mean(Z, axis=0)
        booted_t0 = bootfun
    Z = np.array(Z)
    zdim = Z.shape
    n = zdim[0]
    m = zdim[1]
    out = pd.DataFrame(np.zeros(shape=(m, 3)), columns=['Lower', 'Estimate', 'Upper'])
    if block_length is 'NULL':
        block_length = np.floor(np.sqrt(n))
    if block_length == 1:
        # 判断为假，不执行
        # booted = boot(Z, bootfun, R = numrep)    #未翻译
        for i in range(Z.shape[1]):
            booted_list = [np.mean(resample(Z[:, i], n_samples=Z.shape[0])) for _ in
                           range(numrep)]  # n_samples是受tseries控制
            booted_0 = np.array(booted_list)
            booted = np.append(booted, booted_0)
    else:
        # booted = tsboot(Z, bootfun, l = block.length, R = numrep, sim = "fixed")
        booted = np.array(())
        for i in range(Z.shape[1]):
            booted_list = [np.mean(resample(Z[:, i], n_samples=Z.shape[0])) for _ in
                           range(numrep)]  # n_samples是受tseries控制
            booted_0 = np.array(booted_list)
            booted = np.append(booted, booted_0)
            # booted = np.stack((booted, booted_0), axis = 1)
    booted_t = booted.reshape(numrep, Z.shape[1], order='F')
    booted = {'t0': booted_t0, 't': booted_t, 'R': numrep}
    out['Estimate'] = booted['t0']
    #print(booted_t)
    if block_length == 1 and bca:
        # 判断为假,不执行
        conf = 1 - alpha
        tmp_Lower = np.percentile(a=booted_t, q=100*(1 + conf) / 2, axis=0)
        tmp_Upper = np.percentile(a=booted_t, q=100*(1 - conf) / 2, axis=0)
        out['Lower'] = tmp_Lower
        out['Upper'] = tmp_Upper

        '''
        #原本R的逻辑
        for i in range(1, m):
            tmp = boot_CI(booted, conf = 1-alpha, Type = "bac", index = i)
            out['Lower'][i] = tmp["bca"][:, 4]
            out['Upper'][i] = tmp["bca"][:, 5]
        '''
    else:
        if bca:
            print(
                "LocSig: You chose to use the BCa method, but block.length != 1.  Using percentile method with circular block bootstrap instead.")

        conf = 1 - alpha
        tmp_Lower = np.percentile(a=booted_t, q=100*(1 - conf) / 2, axis=0)
        tmp_Upper = np.percentile(a=booted_t, q=100*(1 + conf) / 2, axis=0)
        out['Lower'] = tmp_Lower
        out['Upper'] = tmp_Upper

        '''
        #原本R的逻辑
        for i in range(1, m):
            #计算置信度区间（分位数:np.percentile）
            #可信度=0.90,置信区间宽度=0.05, 置信区间上限=0.07,置信区间下限=0.02,表示:发生在区间(0.02,0.07)这个范围内的可能性为0.90
            tmp = boot_CI(booted, conf = 1-alpha, Type = "perc", index = i)
            out['Lower'[i]] = tmp["prec"][:, 4]
            out['Upper'][i] = tmp["prec"][:, 5]
        '''

    # out['class'] = "LocSig"
    return out


'''    
if __name__ == '__main__':
    obsData = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/fieldSignficance/data/GFSNAMobsEx.rda')['GFSNAMobsEx']
    fcstData = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/fieldSignficance/data/GFSNAMfcstEx.rda')['GFSNAMfcstEx']
    locData = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/fieldSignficance/data/GFSNAMlocEx.rda')['GFSNAMlocEx']
    locId = (locData["Lon"] >= -90) & (locData["Lon"] <= -75) & (locData["Lat"] <= 40)
    locSub = locData[locId]
    GFSobsSub = obsData.T[locId].T
    GFSfcstSub = fcstData.T[locId].T

    Z = GFSobsSub - GFSfcstSub
    numrep = 500
    block_length = 'NULL'
    alpha = 0.05
'''

