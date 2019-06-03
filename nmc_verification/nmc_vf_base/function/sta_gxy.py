import numpy as np
import math
from nmc_met_class.tools.math import lon_lat_to_cartesian
from scipy.spatial import cKDTree
import nmc_verification.nmc_vf_base.basicdata as bd

def transform(sta,dlon = None,dlat = None):
    #将站点形式的规则网格的数据转化为格点数据

    slon = np.min(sta['lon'])
    elon = np.max(sta['lon'])
    slat = np.min(sta['lat'])
    elat = np.max(sta['lat'])
    nsta = len(sta.index)
    if(dlon is None):
        for i in range(nsta-1):
            dlon = sta.ix[i,'lon'] - sta.ix[i+1,'lon']
            if dlon != 0:
                dlon = math.fabs(dlon)
                break
    if(dlat is None):
        for i in range(nsta-1):
            dlat = sta.ix[i,'lat'] - sta.ix[i+1,'lat']
            if dlat != 0:
                dlat = math.fabs(dlat)
                break

    ig = ((sta.ix[:,'lon'] - slon) // dlon).astype(dtype = 'int16')
    jg = ((sta.ix[:,'lat'] - slat) // dlat).astype(dtype = 'int16')
    grid0 = bd.grid.grid([slon,elon,dlon],[slat,elat,dlat])
    dat = np.zeros((grid0.nlat,grid0.nlon))
    #print(sta.ix[:,'data0'])
    dat[jg,ig] = sta.ix[:,'data0']
    grd = bd.grid_data.grid_data(grid0,dat)
    return grd


