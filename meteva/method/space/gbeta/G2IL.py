#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 17:48:39 2023

@author: tangbuxing
"""
import copy

#import pyreadr
import numpy as np
import pandas as pd
#import statsmodels.api as sm

import meteva.base
from  meteva.method.space.gbeta import Gbeta_score
import matplotlib.pyplot as plt
from sklearn.preprocessing import Binarizer
from meteva.method.space.qq_plot import get_qqplot_2samples_data

def ubalancer(x, alpha, beta):
    res = np.maximum(1 - (x - alpha)/(beta - alpha), 0)    #pmax -> np.maximum(np.arange(1,6), 3)
    return res

def G2IL_score(ob, fo, threshold, beta = None, alpha = 0):
    out = {}
    binarizer=Binarizer(threshold=threshold)
    Z = binarizer.transform(ob)
    Zhat = binarizer.transform(fo)
    G = Gbeta_score(Z,  Zhat, threshold = 0.5, beta = beta, alpha = alpha)
    
    IA = Z == 1
    IB = Zhat == 1
    nA = np.sum(IA)
    nB = np.sum(IB)
    nAB = np.sum(IA & IB)
    N = np.prod(ob.shape) +0.0
    if beta is None:
        beta = N*N  #/2.0
    
    if nA > 0 and nB > 0:
        x_data, y_data = get_qqplot_2samples_data(ob[IA], fo[IB], count=100)
        #tmp = sm.qqplot_2samples(X[IA],X[IB],line='45')    #sm.qqplot_2samples 未测
        #mae = np.mean(abs(tmp[x] - tmp[y]))
        #rmse = np.sqrt(np.mean((tmp[x] - tmp[y]), 2))
        
        #fig = sm.qqplot_2samples(ob[IA],ob[IB])    #sm.qqplot_2samples 未测
        #xx_qqplot = np.sort(X[IB])
        #yy_qqplot = np.sort(X[IA])
        # 获取 Q-Q 图中的数据
        #ax = fig.axes[0]
        #line = ax.get_lines()[0]  # 获取第一条线，即对角线
        #x_data, y_data = line.get_data()
        #rho = np.corrcoef(x_data, y_data)[0, 1]
        mae = np.mean(abs(x_data - y_data))
        rmse = np.sqrt(np.mean(np.power((x_data - y_data),2)))
        #print(mae,rmse)
            
    elif nA == nB:
        mae = rmse = 0
    elif nA > 0 :
        mae = rmse = np.max(abs(ob))
    elif nB > 0 :
        mae = rmse = np.max(abs(fo))
    else:
        mae = meteva.base.IV
        rmse = meteva.base.IV
    #x = (nA + nB - 2 * nAB) * (1 + mae)    
    #out = np.maximum(1 - (x - alpha)/(beta - alpha), 0)    #pmax -> np.maximum(np.arange(1,6), 3)

    out_G2IL = ubalancer(x = (nA + nB - 2 * nAB) * (1 + mae), alpha = alpha, 
                   beta = beta)  
  
    comps = copy.deepcopy(G)
    comps["rmse_sorted"] = rmse
    comps['G2IL']= out_G2IL
    
    return comps
    
if __name__ == '__main__':
    # fcst = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/Gbeta/data/wrf4ncar0531.RData')['wrf4ncar0531']
    # obs = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/Gbeta/data/obs0601.RData')['obs0601']
    # res_G2IL = G2IL(X = obs.values, Xhat = fcst.values, threshold = 2.1,beta = 601 * 501 )

    import meteva.base as meb
    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    path_fo_03 = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo = meb.read_griddata_from_nc(path_fo_03, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")
    res_Gbeta = G2IL_score(grd_ob.values.squeeze(), grd_fo.values.squeeze(), threshold = 0.1)
    print(res_Gbeta)

'''
    X = fcst.values
    Xhat = obs.values
    threshold = 2.1
    alpha = 0
    rule = ">"
    w = 0.5
'''

    
    
    