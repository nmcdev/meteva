# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 17:04:49 2021

@author: 1
"""
import numpy as np

def Earth(x1, x2 = 'NULL', miles = True, R = 'NULL'):
    #计算球面距离
    if (R == 'NULL'):
        if (miles):
            R = 3963.34
        else :
            R = 6378.388
    coslat1 = np.cos((x1[:, 1] * np.pi)/180)
    sinlat1 = np.sin((x1[:, 1] * np.pi)/180)
    coslon1 = np.cos((x1[:, 0] * np.pi)/180)
    sinlon1 = np.sin((x1[:, 0] * np.pi)/180)
    if (x2 == 'NULL'):
        pp1 = np.array((coslat1 * coslon1, coslat1 * sinlon1, sinlat1))
        pp2 = np.array((coslat1 * coslon1, coslat1 * sinlon1, sinlat1))
        pp = np.dot(pp1.T, pp2)
        if float('%.6f'%(np.max(pp))) > 1:
            return R * np.arccos(1 * np.sign(pp))
        else :
            return R * np.arccos(pp)
        
    else :
        coslat2 = np.cos((x2[:, 1] * np.pi)/180)
        sinlat2 = np.sin((x2[:, 1] * np.pi)/180)
        coslon2 = np.cos((x2[:, 0] * np.pi)/180)
        sinlon2 = np.sin((x2[:, 0] * np.pi)/180)
        pp1 = np.mat((coslat1 * coslon1, coslat1 * sinlon1, sinlat1))
        pp2 = np.mat((coslat2 * coslon2, coslat2 * sinlon2, sinlat2))
        pp = np.dot(pp1.T, pp2)
        if float('%.6f'%(np.max(pp))) > 1:
            return R * np.arccos(1 * np.sign(pp))
        else :
            return R * np.arccos(pp)
        
def rdist(Id, loc):
    #计算两点间欧式距离
    dd = []
    for i in range(len(Id)):
        a = Id[i, 0]
        b = Id[i, 1]
        x11 = loc[a]
        x22 = loc[b]
        dd00 = np.sqrt(np.sum(np.square(x11 - x22)))
        dd.append(dd00)
    dd = np.array(dd)
    return dd