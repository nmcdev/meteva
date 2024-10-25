#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 12 14:05:22 2023

@author: tangbuxing
"""
import copy

#import pyreadr
import numpy as np
import pandas as pd

import meteva.base
#import statsmodels.api as sm
from  meteva.method.space.gbeta import Gbeta_score
import matplotlib.pyplot as plt
from sklearn.preprocessing import Binarizer
from meteva.method.space.qq_plot import get_qqplot_2samples_data


def GbetaIL_score(ob, fo, threshold, beta= None, alpha = 0,  w = 0.5):

    out = {}
    binarizer=Binarizer(threshold=threshold)
    Z = binarizer.transform(ob)
    Zhat = binarizer.transform(fo)
    G = Gbeta_score(Z, Zhat, threshold = 0.5, beta = beta, alpha = alpha)
    
    IA = Z == 1
    IB = Zhat == 1
    nA = np.sum(IA)
    nB = np.sum(IB)
    nAB = np.sum(IA & IB)
    N = np.prod(ob.shape) +0.0
    if beta is None:
        beta = N*N  #/2.0


    if nA > 0 and nB > 0:
        x_data,y_data = get_qqplot_2samples_data(ob[IA],fo[IB],count=100)
        #fig = sm.qqplot_2samples(X[IA],X[IB])    #sm.qqplot_2samples 未测
        #xx_qqplot = np.sort(ob[IB])
        #yy_qqplot = np.sort(fo[IA])
        # 获取 Q-Q 图中的数据
        #ax = fig.axes[0]
        #line = ax.get_lines()[0]  # 获取第一条线，即对角线
        #x_data, y_data = line.get_data()
        #cor计算相关性系数 —>np.corrcoef(data)[0,1]

        rho = np.corrcoef(x_data, y_data)[0, 1]
        
    elif nA == nB:
        rho = 1
    elif nA > 0 :
        rho = 1 - (nA/N)
    elif nB > 0 :
        rho = 1 - (nB/N)
    else:
        rho = meteva.base.IV

    rho = max(rho, 0)
    #out = w * G + (1 - w) * rho
    out_GbetaIL = w * 0 + (1 - w) * rho    #G为Gbeta(A,B)的值，暂不明确Gbeta函数中从哪得到
    comps = copy.deepcopy(G)
    comps['corrcoef_sorted'] = rho
    
    comps['GbetaIL']= out_GbetaIL
    comps["weights"]=[w, 1 - w]
    
    return comps
    

if __name__ == '__main__':
    #fcst = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/Gbeta/data/wrf4ncar0531.RData')['wrf4ncar0531']
    #obs = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/Gbeta/data/obs0601.RData')['obs0601']

    #res_GbetaIL = GbetaIL( X = obs.values, Xhat = fcst.values, threshold = 2.1,beta = 601 * 501 )

    import meteva.base as meb
    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    path_fo_03 = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo = meb.read_griddata_from_nc(path_fo_03, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")
    res_Gbeta = GbetaIL_score( grd_ob.values.squeeze(), grd_fo.values.squeeze(), threshold = 0.1)
    print(res_Gbeta)



    