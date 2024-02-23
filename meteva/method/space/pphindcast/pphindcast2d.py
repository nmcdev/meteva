# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 23:34:45 2022

@author: 1
"""
import numpy as npy
import pandas as pd
import copy
#import pyreadr
import sys
from scipy import optimize as optimize
from meteva.method.space.pphindcast.lib import hoods2dPrep, im, datagrabber, vxstats, thresholder
from meteva.method.space.pphindcast.lib import kernel2dsmooth, make_spatialVx
#sys.path.append(r'F:\Work\MODE')
#from tra_PracticallyPerfectHindcast.lib import hoods2dPrep
#from Submit2.baddeley_binary_image_metric.lib.im import im
#from Submit2.fuzzy_logic.lib import datagrabber, vxstats, thresholder, kernel2dsmooth
#from Submit2.baddeley_binary_image_metric.lib.make_spatialVx import make_spatialVx




def findthresh (p, Ix, sPx, binmat, which_score, subset = None):
    sIx = npy.zeros(binmat.shape)
    sIx[sPx >= p] = 1
    res = -vxstats.vxstats(sIx, Ix, which_stats=[which_score], subset=subset)[which_score]
    #print(res)
    return res

def Practically_Perfect_Hindcast(grd_ob,grd_fo,thresholds,compare = ">=",which_score = "ets",level = [1,3,5],
                                 smooth_fun ="hoods2dsmooth",show = False ):
    obs_array = grd_ob.values.squeeze()
    fst_array = grd_fo.values.squeeze()

    hold = make_spatialVx.make_spatialVx(obs_array, fst_array, loc=None,
                          fieldtype="Geometric Objects Pretending to be Precipitation",
                          units="mm/h", thresholds=thresholds,
                          dataname="ICP Geometric Cases", obsname="geom000", modelname="geom001")
    look_pphindcast2d = pphindcast2d(Object = hold,which_score=which_score,levels = level,verbose = show,rule= compare,
                                     smooth_fun = smooth_fun)
    return look_pphindcast2d


def pphindcast2d (Object, which_score = 'ets', time_point = 1, obs = 1, model = 1,
                  levels = None, max_n = None, smooth_fun = "hoods2dsmooth", 
                  smooth_params = None, rule = ">=", verbose = False):
    out = {}
    Object = hoods2dPrep.hoods2dPrep(input_object = Object, pe=None, levels=levels, max_n=max_n, 
                        smooth_fun="hoods2dsmooth", smooth_params=None)
    dat = datagrabber.datagrabber(Object)
    X = npy.array(dat['X'])
    Xhat = npy.array(dat['Xhat'])
    xdim = Object['xdim']
    Nxy = npy.prod(xdim)
    subset = Object['subset']
    thresholds = Object['thresholds'][1]
    levels = Object['levels']
    #q = npy.shape(thresholds[1])[0]
    q = npy.shape(thresholds)[0]
    l = len(levels)
    outmat = npy.zeros((l, q))
    Pthresh = npy.zeros((l, q))
    #out = {'attribute': Object, 'which_score': which_score}
    out = { 'which_score': which_score}
    binmat = npy.zeros((xdim[0], xdim[1]))
    for threshold in range(q):
        #print(threshold)
        dat2_X = thresholder.thresholder(x=X, th=thresholds[threshold], func_type='binary', rule=">=", replace_with=0)
        dat2_Xhat = thresholder.thresholder(x=Xhat, th=thresholds[threshold], func_type='binary', rule=">", replace_with=0)
        Ix = dat2_X
        Iy = dat2_Xhat
        for level in range(l):
            #print(level)
            Wlvl = kernel2dsmooth.kernel2dsmooth(Ix, kernel_type='boxcar', n = levels[level], setup=True)
            sPy = kernel2dsmooth.kernel2dsmooth(Iy, kernel_type='boxcar', n = levels[level],
                                 W = Wlvl, xdim = xdim, Nxy = Nxy)
            sPx = kernel2dsmooth.kernel2dsmooth(Ix, kernel_type='boxcar', n = levels[level],
                                 W = Wlvl, xdim = xdim, Nxy = Nxy)
            Pthresh[level, threshold] = optimize.minimize_scalar(findthresh, 
                                                                 args=(Ix, sPx, binmat, which_score),
                                                                 bounds = (0,1), 
                                                                 method = "bounded")['x']

            #Pthresh[level, threshold] = optimize.minimize(findthresh,0,(Ix, sPx, binmat, which_score),"L-BFGS-B")
           
            
            
            if verbose:
                print("Pthresh = ", Pthresh[level, threshold],
                      "for obs threshold no. = ", threshold , "and level = ",
                      levels[level], "\n")
            sIy = thresholder.thresholder(x = sPy, th = Pthresh[level, threshold], 
                                          func_type = "binary", rule = rule)
            outmat[level, threshold] = vxstats.vxstats(x = sIy, xhat = Ix, 
                                                       which_stats = [which_score])[which_score]
    out['value'] = outmat
    out['Pthresh'] = Pthresh
    out['time_point'] = time_point
    out['model_num'] = model
    out['class'] = "pphindcast"
    
    
    return out


if __name__ == '__main__':
    # geom000 = pyreadr.read_r(r'F:\Work\MODE\Submit2\baddeley_binary_image_metric\data\geom000.Rdata')['geom000']
    # geom001 = pyreadr.read_r(r'F:\Work\MODE\Submit2\baddeley_binary_image_metric\data\geom001.Rdata')['geom001']
    # ICPg240Locs = pyreadr.read_r(r'F:\Work\MODE\Submit2\baddeley_binary_image_metric\data\ICPg240Locs.Rdata')['ICPg240Locs']

    import meteva.base as meb
    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    path_fo = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo = meb.read_griddata_from_nc(path_fo, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")

    res = Practically_Perfect_Hindcast(grd_ob,grd_fo,thresholds=[0.01, 50.01])


    '''
    Object = hold
    which_score = 'ets'
    time_point = 1
    obs = 1
    model = 1
    levels = npy.array([1,3,65])
    max_n = None
    smooth_fun = "hoods2dsmooth"
    smooth_params = None
    rule = ">="
    verbose = False
    '''
    
    

    
    
    