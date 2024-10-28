#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 13:41:16 2023

@author: tangbuxing
"""
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from sklearn.preprocessing import Binarizer
from scipy.spatial import cKDTree
from meteva.method.space.mode.deltametric import cv2_distanceTransform



def Gbeta_score(ob, fo, threshold, beta = None, alpha = 0):
    out = {}
  
    binarizer=Binarizer(threshold=threshold)
    Z = binarizer.transform(ob)
    Zhat = binarizer.transform(fo)

    #dA = distmap(Z)    #未翻译distmap函数
    #dB = distmap(Zhat)    #未翻译distmap函数
    #dA = cv2.distanceTransform(np.array(~(Z == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
    am = np.array(~(Z == 1) + 0, np.uint8)
    dA = cv2_distanceTransform(am)

    #plt.imshow(dA)
    #dB = cv2.distanceTransform(np.array(~(Zhat == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
    #plt.imshow(dB)
    bm = np.array(~(Zhat == 1) + 0, np.uint8)
    dB = cv2_distanceTransform(bm)

    IA = Z
    IB = Zhat
    if IA.shape != IB.shape:
        print("beta: X and Xhat have different dimensions.")
    N = np.prod(IA.shape) +0.0   # + 0.0 转换成float计算所有元素的乘积
  
    if beta is None:
        beta = N*N   #/4.0
    nA = np.sum(IA)
    nB = np.sum(IB)
    IA_0 = IA ==1
    IB_0 = IB ==1
    nAB = np.sum(IA_0 & IB_0)    #重叠区域
  
    term1 = (nA + nB - 2 * nAB)    #不重叠区域
    term1b = term1/np.sqrt(beta - alpha)   
    term1c = (nB - nAB)/np.sqrt(beta - alpha)
    term1d = (nA - nAB)/np.sqrt(beta - alpha)
    
    medAB = np.sum(dA * IB)/max(1, nB)
    medBA = np.sum(dB * IA)/max(1, nA)
    
    term2 = medAB * nB    
    #term2 = medAB * nB
    term2b = term2/np.sqrt(beta - alpha)
    
    term3 = medBA * nA
    term3b = term3/np.sqrt(beta - alpha)
    
    term4 = (term2 + term3)/np.sqrt(beta - alpha)
    x = term1b * term4
    outAB = np.maximum(1 - (term1c * term2b - alpha), 0)    #pmax -> np.maximum(np.arange(1,6), 3)
    outBA = np.maximum(1 - (term1d * term3b - alpha), 0)
    out = np.maximum(1 - (x - alpha), 0)

    res_data = np.array([[nA, nB, nAB, term1, medAB, medBA, term2, term3, outAB, outBA]])
    # res = pd.DataFrame(res_data, columns=["nA", "nB", "nAB", "nA + nB - 2nAB", "medAB",
    #                                       "medBA", "medAB * nB", "medBA * nA",
    #                                       "GbetaAB", "GbetaBA"])

    out = {'nA':nA, 'nB':nB, 'nAB':nAB, '"nAnB_2nAB':term1, 'medAB':medAB, 'medBA':medBA,
           'medAB_multiply_nB':term2, 'medBA_multiply_nA':term3,
            "GbetaAB":outAB,"GbetaBA":outBA,
           'beta':beta, 'alpha':alpha, 'threshold':threshold}
       
    return out 


if __name__ == '__main__':

    import meteva.base as meb
    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    path_fo_03 = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo = meb.read_griddata_from_nc(path_fo_03, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")
    res_Gbeta = Gbeta_score(grd_ob.values.squeeze(), grd_fo.values.squeeze(), threshold = 0.1)
    print(res_Gbeta)

    # fcst = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/Gbeta/data/wrf4ncar0531.RData')['wrf4ncar0531']
    # obs = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/Gbeta/data/obs0601.RData')['obs0601']
    # res_Gbeta = Gbeta( X = obs.values, Xhat = fcst.values, threshold = 2.1 )
'''
    X = obs.values
    Xhat = fcst.values
    threshold = 2.1
    alpha = 0
    beta = None
    rule = ">"
'''    


    
    
  