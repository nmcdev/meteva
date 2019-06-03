import nmc_met_class as nmc
import numpy as np
import pandas as pd

def transform(grd):
    x = grd['lon']
    y = grd['lat']
    grid_x,grid_y = np.meshgrid(x,y)
    grid_num = len(x) * len(y)
    dat = np.empty((grid_num,4))
    dat[:,0] = np.arange(grid_num)
    dat[:,1] = grid_x.reshape(-1)
    dat[:,2] = grid_y.reshape(-1)
    dat[:,3] = grd.values.reshape(-1)
    df = pd.DataFrame(dat,columns=['id','lon','lat','data0'])
    sta = nmc.bd.sta_data.sta_data(df)
    grid = nmc.bd.grid.get_grid_of_data(grd)
    sta['time'] = grid.stime
    sta['dtime'] = grid.sdtimedelta
    sta['level'] = grid.levels[0]
    sta['alt'] = 9999
    return sta


def interpolation_linear(grd,sta):
    grid = nmc.bd.grid.get_grid_of_data(grd)
    sta1 = nmc.fun.sta_sta.get_sta_in_grid(sta,grid)
    dat0 = grd.values
    dat = np.squeeze(dat0)

    ig = ((sta1['lon'] - grid.slon) // grid.dlon).astype(dtype = 'int16')
    jg = ((sta1['lat'] - grid.slat) // grid.dlat).astype(dtype = 'int16')
    dx = (sta1['lon'] - grid.slon) / grid.dlon - ig
    dy = (sta1['lat'] - grid.slat) / grid.dlat - jg
    c00 = (1 - dx) * (1 - dy)
    c01 = dx * (1 - dy)
    c10 = (1-dx) * dy
    c11 = dx * dy

    ig1 = np.minimum(ig + 1, grid.nlon - 1)
    jg1 = np.minimum(jg + 1, grid.nlat - 1)
    dat_sta= c00 * dat[jg,ig] + c01 * dat[jg,ig1] + c10 * dat[jg1,ig] + c11 * dat[jg1,ig1]
    sta1.loc[:,'data0'] =dat_sta[:]
    sta1['time'] = grid.stime
    sta1['dtime'] = grid.sdtimedelta
    sta1['level'] = grid.levels[0]

    return sta1