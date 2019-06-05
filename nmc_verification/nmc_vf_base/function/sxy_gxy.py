import numpy as np
import math
from nmc_verification.nmc_vf_base.method.math import lon_lat_to_cartesian
from scipy.spatial import cKDTree
import nmc_verification.nmc_vf_base.basicdata as bd
import nmc_verification.nmc_vf_base.function as fun
from nmc_verification.nmc_vf_base.method.frprmn2 import frprmn2


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
    grid0 = bd.grid([slon,elon,dlon],[slat,elat,dlat])
    dat = np.zeros((grid0.nlat,grid0.nlon))
    data_name = bd.get_data_names(sta)[0]
    dat[jg,ig] = sta.ix[:,data_name]
    grd = bd.grid_data(grid0,dat)
    return grd



def sta_to_grid_idw(sta, grid0,background = None,effectR = 1000,nearNum = 16,other_info='left'):
    data_name = bd.get_data_names(sta)
    if other_info=='left':
        grid = bd.grid(grid0.glon,grid0.glat,[sta.ix[0,'time']],[sta.ix[0,'dtime']],[sta.ix[0,'level']],data_name)
    else:
        grid = grid0
    xyz_sta =  lon_lat_to_cartesian(sta.ix[:,'lon'], sta.ix[:,'lat'],R = bd.const.ER)
    lon = np.arange(grid.nlon) * grid.dlon + grid.slon
    lat = np.arange(grid.nlat) * grid.dlat + grid.slat
    grid_lon,grid_lat = np.meshgrid(lon,lat)
    xyz_grid = lon_lat_to_cartesian(grid_lon.flatten(), grid_lat.flatten(),R = bd.const.ER)
    tree = cKDTree(xyz_sta)
    d, inds = tree.query(xyz_grid, k=nearNum)
    d += 1e-6
    w = 1.0 / d ** 2
    input_dat = sta.ix[:,'data0'].values
    dat = np.sum(w * input_dat[inds], axis=1) / np.sum(w, axis=1)
    bg = bd.grid_data(grid)
    if(background is not None):
        bg = fun.gxy_gxy.linearInterpolation(background,grid)
    bg_dat = bg.values.flatten()
    dat = np.where(d[:,0] > effectR,bg_dat,dat)
    grd = bd.grid_data(grid,dat)
    return grd



def sta_to_grid_oa2(sta0,background,sm = 1,effect_R = 1000,rate_of_model = 0,other_info='left'):
    sta = fun.sxy_sxy.drop_nan(sta0)
    grid = bd.get_grid_of_data(background)
    sta = fun.sxy_sxy.get_sta_in_grid(sta, grid)
    grd = background.copy()
    dat = np.squeeze(grd.values)
    ig = ((sta.ix[:,'lon'] - grid.slon) // grid.dlon).astype(dtype = 'int16')
    jg = ((sta.ix[:,'lat'] - grid.slat) // grid.dlat).astype(dtype = 'int16')
    dx = (sta.ix[:,'lon'] - grid.slon) / grid.dlon - ig
    dy = (sta.ix[:,'lat'] - grid.slat) / grid.dlat - jg
    c00 = (1 - dx) * (1 - dy)
    c01 = dx * (1 - dy)
    c10 = (1-dx) * dy
    c11 = dx * dy
    lat = np.arange(grid.nlat) * grid.dlat + grid.slat
    sr = 1/np.power(np.cos(lat*math.pi/180),4)

    def targe(x):
        grdv =  x.reshape(grid.nlat,grid.nlon)
        dx = grdv[:,:-2] + grdv[:,2:] - 2 * grdv[:,1:-1]
        cost1 = np.sum(dx * dx)
        dy = grdv[:-2,:] + grdv[2:,:] - 2 * grdv[1:-1,:]
        dy2 = dy * dy
        sum_dy = np.sum(dy2,axis=1)
        cost1 = cost1 + np.dot(sum_dy,sr[1:-1])

        sta_g = c00 * dat[jg, ig] + c01 * dat[jg, ig + 1] + c10 * dat[jg + 1, ig] + c11 * dat[
            jg + 1, ig + 1]
        error = sta.ix[:,'data0'] - sta_g
        cost2 = np.sum(error * error)
        cost = sm * cost1 + cost2
        return cost

    def grads(x):
        grdv = x.reshape(grid.nlat,grid.nlon)
        g1 = np.zeros(grdv.shape)
        dx = 2 * (grdv[:,:-2] + grdv[:,2:] - 2 * grdv[:,1:-1])
        g1[:,:-2] = dx
        g1[:,2:] += dx
        g1[:,1:-1] -= 2*dx

        sr_expend = np.tile(sr[1:-1],[grid.nlon,1]).T
        dy = 2 *(grdv[:-2,:] + grdv[2:,:] - 2 * grdv[1:-1,:])
        dy_sr = dy * sr_expend
        g1[:-2,:] += dy_sr
        g1[2:,:] += dy_sr
        g1[1:-1,:] -= 2 * dy_sr

        g2 = np.zeros(grdv.shape)
        sta_g = c00 * dat[jg, ig] + c01 * dat[jg, ig + 1] + c10 * dat[jg + 1, ig] + c11 * dat[jg + 1, ig + 1]
        d = 2 * (sta_g - sta.ix[:,'data0'])
        g2[jg,ig] += d * c00
        g2[jg,ig + 1]  += d * c01
        g2[jg+1,ig] += d * c10
        g2[jg+1,ig+1] += d * c11
        g = sm * g1 + g2
        return g.reshape(-1)

    x = dat.reshape(-1)
    x_oa = frprmn2(x, targe, grads)
    dat = x_oa.reshape(grid.nlat,grid.nlon)
    grd = bd.grid_data(grid,dat)
    bd.set_coords(grd,time = sta.ix[0,'time'],dtime=sta.ix[0,'dtime'],level = sta.ix[0,'level'])

    return grd
