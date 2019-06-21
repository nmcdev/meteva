import numpy as np
import math
import nmc_verification
from scipy.spatial import cKDTree
def transform(sta,dlon = None,dlat = None):
    """
    将站点形式的规则网格的数据转化为格点数据
    :param sta:站点数据
    :param dlon 经度精度
    :param dlat 纬度经度
    :return:返回格点网格数据
    """
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
    grid0 = nmc_verification.nmc_vf_base.basicdata.grid([slon,elon,dlon],[slat,elat,dlat])
    dat = np.zeros((grid0.nlat,grid0.nlon))
    data_name = nmc_verification.nmc_vf_base.basicdata.get_data_names(sta)[0]
    dat[jg,ig] = sta.ix[:,data_name]
    grd = nmc_verification.nmc_vf_base.basicdata.grid_data(grid0,dat)
    return grd

#站点到格点的反距离插值，对每个格点，获取其最近的几个站点编号、距离, 然后计算权重和。
def sta_to_grid_idw(sta, grid0,background = None,effectR = 1000,nearNum = 16,other_info='left'):
    data_name = nmc_verification.nmc_vf_base.basicdata.get_data_names(sta)
    if other_info=='left':
        grid = nmc_verification.nmc_vf_base.basicdata.grid(grid0.glon,grid0.glat,[sta.ix[0,'time']],[sta.ix[0,'dtime']],[sta.ix[0,'level']],data_name)
    else:
        grid = grid0
    xyz_sta =  nmc_verification.nmc_vf_base.method.math_tools.lon_lat_to_cartesian(sta.ix[:, 'lon'], sta.ix[:, 'lat'], R = nmc_verification.nmc_vf_base.basicdata.const.ER)
    lon = np.arange(grid.nlon) * grid.dlon + grid.slon
    lat = np.arange(grid.nlat) * grid.dlat + grid.slat
    grid_lon,grid_lat = np.meshgrid(lon,lat)
    xyz_grid = nmc_verification.nmc_vf_base.method.math_tools.lon_lat_to_cartesian(grid_lon.flatten(), grid_lat.flatten(), R = nmc_verification.nmc_vf_base.basicdata.const.ER)
    tree = cKDTree(xyz_sta)
    #d,inds 分别是站点到格点的距离和id
    d, inds = tree.query(xyz_grid, k=nearNum)
    d += 1e-6
    w = 1.0 / d ** 2
    input_dat = sta.ix[:,'data0'].values
    dat = np.sum(w * input_dat[inds], axis=1) / np.sum(w, axis=1)
    bg = nmc_verification.nmc_vf_base.basicdata.grid_data(grid)
    if(background is not None):
        bg = nmc_verification.nmc_vf_base.function.gxy_gxy.linearInterpolation(background,grid)
    bg_dat = bg.values.flatten()
    dat = np.where(d[:,0] > effectR,bg_dat,dat)
    grd = nmc_verification.nmc_vf_base.basicdata.grid_data(grid,dat)
    return grd

#站点到格点转换
def sta_to_grid_oa2(sta0,background,sm = 1,effect_R = 1000,rate_of_model = 0):

    sta = nmc_verification.nmc_vf_base.function.sxy_sxy.drop_nan(sta0)
    data_name = nmc_verification.nmc_vf_base.basicdata.get_data_names(sta)[0]
    grid = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(background)
    sta = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_grid_xy(sta, grid)
    #print(sta)
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

        error = sta.ix[:,7] - sta_g

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

        d = 2 * (sta_g - sta.ix[:,7])

        g2[jg,ig] += d * c00

        g2[jg,ig + 1]  += d * c01

        g2[jg+1,ig] += d * c10

        g2[jg+1,ig+1] += d * c11

        g = sm * g1 + g2

        return g.reshape(-1)



    x = grd.values.reshape(-1)

    x_oa = nmc_verification.nmc_vf_base.method.frprmn2(x, targe, grads)

    grd.values = x_oa.reshape(1,1,1,1,grid.nlat,grid.nlon)

    return grd
