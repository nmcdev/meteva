import math
import nmc_verification
from nmc_verification.nmc_vf_base.tool.math_tools import lon_lat_to_cartesian
from scipy.spatial import cKDTree
import numpy as np
import copy

def u_v_to_wind(u,v):
    grid0 = nmc_verification.nmc_vf_base.get_grid_of_data(u)
    grid1 = nmc_verification.nmc_vf_base.grid(grid0.glon,grid0.glat,grid0.gtime,
                                              dtime_list= grid0.dtimes,level_list=grid0.levels,member_list=["u","v"])
    wind = nmc_verification.nmc_vf_base.grid_data(grid1)
    wind.name = "wind"
    wind.values[0, :, :, :, :, :] = u.values[0, :, :, :, :, :]
    wind.values[1, :, :, :, :, :] = v.values[0, :, :, :, :, :]
    return wind

def speed_angle_to_wind(speed,angle):

    speed_v = speed.values.squeeze()
    angle_v = angle.values.squeeze()

    grid0 = nmc_verification.nmc_vf_base.get_grid_of_data(speed)
    grid1 = nmc_verification.nmc_vf_base.grid(grid0.glon,grid0.glat,grid0.gtime,
                                              dtime_list=grid0.dtimes,level_list=grid0.levels,member_list=["u","v"])
    wind = nmc_verification.nmc_vf_base.grid_data(grid1)
    wind.name = "wind"
    wind.values[0, :, :, :, :, :] = speed_v[:, :] * np.cos(angle_v[:, :] * math.pi /180)
    wind.values[1, :, :, :, :, :] = speed_v[:, :] * np.sin(angle_v[:, :] * math.pi /180)
    return wind



def sta_index_ensemble_near_by_sta(sta_to,nearNum = 100,sta_from = None,drop_frist = False):
    if(sta_to is None):
        return None
    if(sta_from is None):
        sta_from = copy.deepcopy(sta_to)
    xyz_sta0 = lon_lat_to_cartesian(sta_to['lon'].values[:], sta_to['lat'].values[:],R = nmc_verification.nmc_vf_base.basicdata.ER)
    xyz_sta1 = lon_lat_to_cartesian(sta_from['lon'].values[:], sta_from['lat'].values[:],R = nmc_verification.nmc_vf_base.basicdata.ER)
    tree = cKDTree(xyz_sta0)
    _,indexs = tree.query(xyz_sta1, k=nearNum)
    sta_ensemble = sta_to[nmc_verification.nmc_vf_base.get_coord_names()]
    for i in range(nearNum):
        data_name = "data" + str(i)
        sta_ensemble[data_name] = indexs[:,i]
    if drop_frist:
        sta_ensemble = sta_ensemble.drop(columns=['data0'])
    return sta_ensemble

def sta_id_ensemble_near_by_sta(sta_to,nearNum = 100,sta_from = None,drop_frist = False):
    if(sta_to is None):
        return None
    if(sta_from is None):
        sta_from = copy.deepcopy(sta_to)
    xyz_sta0 = lon_lat_to_cartesian(sta_to['lon'].values[:], sta_to['lat'].values[:],R = nmc_verification.nmc_vf_base.basicdata.ER)
    xyz_sta1 = lon_lat_to_cartesian(sta_from['lon'].values[:], sta_from['lat'].values[:],R = nmc_verification.nmc_vf_base.basicdata.ER)
    tree = cKDTree(xyz_sta0)
    _,indexs = tree.query(xyz_sta1, k=nearNum)
    input_dat = sta_from.ix[:, 'id'].values
    sta_ensemble = sta_to[nmc_verification.nmc_vf_base.get_coord_names()]
    for i in range(nearNum):
        data_name = "data" + str(i)
        sta_ensemble[data_name] = input_dat[indexs[:,i]]
    if drop_frist:
        sta_ensemble = sta_ensemble.drop(columns=['data0'])
    return sta_ensemble

def sta_value_ensemble_near_by_sta(sta_to,nearNum = 100,sta_from = None,drop_frist = False):
    if(sta_to is None):
        return None
    if(sta_from is None):
        sta_from = copy.deepcopy(sta_to)
    xyz_sta0 = lon_lat_to_cartesian(sta_to['lon'].values[:], sta_to['lat'].values[:],R = nmc_verification.nmc_vf_base.basicdata.ER)
    xyz_sta1 = lon_lat_to_cartesian(sta_from['lon'].values[:], sta_from['lat'].values[:],R = nmc_verification.nmc_vf_base.basicdata.ER)
    tree = cKDTree(xyz_sta0)
    _,indexs = tree.query(xyz_sta1, k=nearNum)
    data_name = nmc_verification.nmc_vf_base.get_data_names(sta_from)[0]
    input_dat = sta_from[data_name].values
    sta_ensemble = sta_to[nmc_verification.nmc_vf_base.get_coord_names()]
    for i in range(nearNum):
        data_name = "data" + str(i)
        sta_ensemble[data_name] = input_dat[indexs[:,i]]
    if drop_frist:
        sta_ensemble = sta_ensemble.drop(columns=['data0'])
    return sta_ensemble

def sta_dis_ensemble_near_by_sta(sta_to,nearNum = 100,sta_from = None,drop_frist = False):
    if(sta_to is None):
        return None
    if(sta_from is None):
        sta_from = copy.deepcopy(sta_to)
    xyz_sta0 = lon_lat_to_cartesian(sta_to['lon'].values[:], sta_to['lat'].values[:],R = nmc_verification.nmc_vf_base.basicdata.ER)
    xyz_sta1 = lon_lat_to_cartesian(sta_from['lon'].values[:], sta_from['lat'].values[:],R = nmc_verification.nmc_vf_base.basicdata.ER)
    tree = cKDTree(xyz_sta0)
    d,_ = tree.query(xyz_sta1, k=nearNum)
    sta_ensemble = sta_to[nmc_verification.nmc_vf_base.get_coord_names()]
    for i in range(nearNum):
        data_name = "data" + str(i)
        sta_ensemble[data_name] = d[:,i]
    if drop_frist:
        sta_ensemble = sta_ensemble.drop(columns=['data0'])
    return sta_ensemble

def sta_index_ensemble_near_by_grid(sta, grid,nearNum = 1):
    ER = nmc_verification.nmc_vf_base.ER
    members = np.arange(nearNum).tolist()
    grid1 = nmc_verification.nmc_vf_base.grid(grid.glon,grid.glat,members=members)
    grd_en = nmc_verification.nmc_vf_base.grid_data(grid1)
    xyz_sta =  nmc_verification.nmc_vf_base.tool.math_tools.lon_lat_to_cartesian(sta.loc[:,"lon"], sta.loc[:,"lat"],R = ER)
    lon = np.arange(grid1.nlon) * grid1.dlon + grid1.slon
    lat = np.arange(grid1.nlat) * grid1.dlat + grid1.slat
    grid_lon,grid_lat = np.meshgrid(lon,lat)
    xyz_grid = nmc_verification.nmc_vf_base.tool.math_tools.lon_lat_to_cartesian(grid_lon.flatten(), grid_lat.flatten(),R = ER)
    tree = cKDTree(xyz_sta)
    value, inds = tree.query(xyz_grid, k=nearNum)
    grd_en.values = inds.reshape((nearNum,1,1,1,grid1.nlat,grid1.nlon))
    return grd_en


def mean_of_sta(sta,used_coords = ["member"]):
    sta_mean = sta[nmc_verification.nmc_vf_base.get_coord_names()]
    sta_data = sta[nmc_verification.nmc_vf_base.get_stadata_names(sta)]
    value = sta_data.values
    mean = np.mean(value,axis=1)
    sta_mean['mean'] =mean
    return sta_mean

def std_of_sta(sta,used_coords = ["member"]):
    sta_std = sta[nmc_verification.nmc_vf_base.get_coord_names()]
    sta_data = sta[nmc_verification.nmc_vf_base.get_stadata_names(sta)]
    value = sta_data.values
    std = np.std(value, axis=1)
    sta_std['std'] = std
    return sta_std

def var_of_sta(sta,used_coords = ["member"]):
    sta_var = sta[nmc_verification.nmc_vf_base.get_coord_names()]
    sta_data = sta[nmc_verification.nmc_vf_base.get_stadata_names(sta)]
    value = sta_data.values
    var = np.var(value, axis=1)
    sta_var['var'] = var
    return sta_var

def max_of_sta(sta,used_coords = ["member"]):
    sta_max = sta[nmc_verification.nmc_vf_base.get_coord_names()]
    sta_data = sta[nmc_verification.nmc_vf_base.get_stadata_names(sta)]
    value = sta_data.values
    max1 = np.max(value, axis=1)
    sta_max['max'] = max1
    return sta_max

def min_of_sta(sta,used_coords = ["member"]):
    sta_min = sta[nmc_verification.nmc_vf_base.get_coord_names()]
    sta_data = sta[nmc_verification.nmc_vf_base.get_stadata_names(sta)]
    value = sta_data.values
    min1 = np.min(value, axis=1)
    sta_min['min'] = min1
    return sta_min


#获取网格数据的平均值
def mean_of_grd(grd,used_coords = ["member"]):
    grid0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd)
    grid1 = nmc_verification.nmc_vf_base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,member_list=["mean"])
    dat = np.squeeze(grd.values)
    dat = np.mean(dat,axis = 0)
    grd1 = nmc_verification.nmc_vf_base.basicdata.grid_data(grid1,dat)
    return grd1

#获取网格数据的方差
def var_of_grd(grd,used_coords = ["member"]):
    grid0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd)
    grid1 = nmc_verification.nmc_vf_base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,member_list=["var"])
    dat = np.squeeze(grd.values)
    dat = np.var(dat,axis = 0)
    grd1 = nmc_verification.nmc_vf_base.basicdata.grid_data(grid1,dat)
    return grd1

#获取网格数据的标准差
def std_of_grd(grd,used_coords = ["member"]):
    grid0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd)
    grid1 = nmc_verification.nmc_vf_base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,member_list=["std"])
    dat = np.squeeze(grd.values)
    dat = np.std(dat,axis = 0)
    grd1 = nmc_verification.nmc_vf_base.basicdata.grid_data(grid1,dat)
    return grd1

#获取网格数据的最小值
def min_of_grd(grd,used_coords = ["member"]):
    grid0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd)
    grid1 = nmc_verification.nmc_vf_base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,member_list=["min"])
    dat = np.squeeze(grd.values)
    dat = np.min(dat,axis = 0)
    grd1 = nmc_verification.nmc_vf_base.basicdata.grid_data(grid1,dat)
    return grd1

#获取网格数据的最大值
def max_of_grd(grd,used_coords = ["member"]):
    grid0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd)
    grid1 = nmc_verification.nmc_vf_base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,member_list=["max"])
    dat = np.squeeze(grd.values)
    dat = np.max(dat,axis = 0)
    grd1 = nmc_verification.nmc_vf_base.basicdata.grid_data(grid1,dat)
    return grd1