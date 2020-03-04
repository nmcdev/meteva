import meteva
import numpy as np
import pandas as pd

#格点转换为站点
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
    member = grd['member'][0]
    df = pd.DataFrame(dat,columns=['id','lon','lat',member])
    sta = meteva.base.basicdata.sta_data(df)
    grid = meteva.base.basicdata.get_grid_of_data(grd)
    sta['time'] = grid.stime
    sta['dtime'] = grid.sdtimedelta
    sta['level'] = grid.levels[0]
    sta['alt'] = 9999
    return sta

#格点到站点的插值
def interpolation_nearest(grd,sta,other_info='left'):
    grid = meteva.base.basicdata.get_grid_of_data(grd)
    sta1 = meteva.base.function.get_from_sta_data.sta_in_grid_xy(sta, grid)
    dat0 = grd.values
    dat = np.squeeze(dat0)

    ig = np.round((sta1['lon'] - grid.slon) // grid.dlon).astype(dtype = 'int16')
    jg = np.round((sta1['lat'] - grid.slat) // grid.dlat).astype(dtype = 'int16')

    dat_sta= dat[jg,ig]
    data_name = meteva.base.basicdata.get_data_names(sta)[0]
    sta1.loc[:, data_name] = dat_sta[:]
    if other_info == 'left':
        sta1['time'] = grid.stime
        sta1['dtime'] = grid.dtimes[0]
        sta1['level'] = grid.levels[0]
        meteva.base.basicdata.set_data_names(sta1,grid.members)
    return sta1

#双线性格点到站点的插值
def interpolation_linear(grd,sta,other_info='left'):
    grid = meteva.base.basicdata.get_grid_of_data(grd)
    sta1 = meteva.base.function.get_from_sta_data.sta_in_grid_xy(sta, grid)
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
    data_name = meteva.base.get_stadata_names(sta)[0]
    sta1.loc[:, data_name] = dat_sta[:]
    if other_info == 'left':
        sta1['time'] = grid.stime
        sta1['dtime'] = grid.dtimes[0]
        sta1['level'] = grid.levels[0]
        meteva.base.set_stadata_names(sta1,grid.members)
    return sta1


#三维格点到站点的插值
def interpolation_cubic(grd,sta,other_info = 'left'):
    grid = meteva.base.basicdata.get_grid_of_data(grd)
    sta1 = meteva.base.function.get_from_sta_data.sta_in_grid_xy(sta, grid)
    dat0 = grd.values
    dat = np.squeeze(dat0)
    ig = ((sta1['lon'] - grid.slon) // grid.dlon).astype(dtype = 'int16')
    jg = ((sta1['lat'] - grid.slat) // grid.dlat).astype(dtype = 'int16')
    dx = (sta1['lon'] - grid.slon) / grid.dlon - ig
    dy = (sta1['lat'] - grid.slat) / grid.dlat - jg
    data_name = meteva.base.basicdata.get_data_names(sta1)[0]
    for p in range(-1,3,1):
        iip = np.minimum(np.maximum(ig+p,0),grid.nlon-1)
        fdx = cubic_f(p, dx)
        for q in range(-1,3,1):
            jjq = np.minimum(np.maximum(jg+q,0),grid.nlat-1)
            fdy = cubic_f(q,dy)
            fdxy = fdx * fdy
            sta1[data_name] +=  fdxy * dat[jjq,iip]
    if other_info == 'left':
        sta1['time'] = grid.stime
        sta1['dtime'] = grid.dtimes[0]
        sta1['level'] = grid.levels[0]
        meteva.base.basicdata.set_data_names(sta1,grid.members)
    return sta1

def cubic_f(n, dx):
    if (n == -1):
        return -dx * (dx - 1) * (dx - 2) / 6
    elif (n == 0):
        return (dx + 1) * (dx - 1) * (dx - 2) / 2
    elif (n == 1):
        return -(dx + 1) * dx * (dx - 2) / 2
    else:
        return (dx + 1) * dx * (dx - 1) / 6
