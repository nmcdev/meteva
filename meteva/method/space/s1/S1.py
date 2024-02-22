#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 22 23:16:25 2022

@author: tangbuxing
"""
import numpy as np
import pandas as pd
#import sys
#sys.path.append(r'F:\Work\MODE')
from meteva.method.space.fuzzy_logic.lib import kernel2dsmooth
import meteva


def S1(grd_ob,grd_fo,nx = 10,ny = 10,sigma = 1, gradFUN = "KernelGradFUN"):
    out = {}
    x = grd_ob.values.squeeze()
    xhat = grd_fo.values.squeeze()
    Xgrad = kernel2dsmooth.kernel2dsmooth(x, kernel_type="LoG", nx=nx, ny=ny, sigma=sigma)
    Ygrad = kernel2dsmooth.kernel2dsmooth(xhat, kernel_type="LoG", nx=nx, ny=ny, sigma=sigma)

    denom = sum(np.sum(np.maximum(abs(Xgrad), abs(Ygrad)), axis=0))
    numer = sum(np.sum(abs(Ygrad - Xgrad), axis=0))

    grid1 = meteva.base.get_grid_of_data(grd_ob)
    ob_grad = meteva.base.grid_data(grid1,Xgrad)
    grid2 = meteva.base.get_grid_of_data(grd_fo)
    fo_grad = meteva.base.grid_data(grid2, Ygrad)
    out = {"s1":100 * numer / denom,"ob_grad":ob_grad,"fo_grad":fo_grad}


    return out

def S1_original(x, xhat, gradFUN = "KernelGradFUN"):
    out = {}
    
    Xgrad = kernel2dsmooth.kernel2dsmooth(x, kernel_type = "LoG", nx = 10, ny = 12, sigma = 1)
    Ygrad = kernel2dsmooth.kernel2dsmooth(xhat, kernel_type = "LoG", nx = 10, ny = 12, sigma = 1)
    
    denom = sum(np.sum(np.maximum(abs(Xgrad),abs(Ygrad)), axis = 0))
    numer = sum(np.sum(abs(Ygrad - Xgrad),axis = 0))
        
    out = 100 * numer/denom
    return out

if __name__ == '__main__':
    # x = pd.read_csv(r"H:\test_data\input\mem\s1\UKfcst6.csv")
    # xhat = pd.read_csv(r"H:\test_data\input\mem\s1\UKobs6.csv")
    # look=S1(x, xhat)
    import meteva.base as meb
    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    path_fo = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo = meb.read_griddata_from_nc(path_fo, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")

    #obs_array = grd_ob.values.squeeze()
    #fst_array = grd_fo.values.squeeze()
    look=S1(grd_ob, grd_fo)
    print(look)

    meb.smooth()