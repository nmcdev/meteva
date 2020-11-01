import meteva
from meteva.base.tool.math_tools import lon_lat_to_cartesian
from scipy.spatial import cKDTree
import copy
import numpy as np
import pandas as pd

def sta_index_ensemble_near_by_sta(sta_to,nearNum = 100,sta_from = None,drop_frist = False):
    if(sta_to is None):
        return None
    if(sta_from is None):
        sta_from = copy.deepcopy(sta_to)
    xyz_sta0 = lon_lat_to_cartesian(sta_to['lon'].values[:], sta_to['lat'].values[:],R = meteva.base.basicdata.ER)
    xyz_sta1 = lon_lat_to_cartesian(sta_from['lon'].values[:], sta_from['lat'].values[:],R = meteva.base.basicdata.ER)
    tree = cKDTree(xyz_sta1)
    _,indexs = tree.query(xyz_sta0, k=nearNum)
    sta_ensemble = sta_to[meteva.base.get_coord_names()]
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
    xyz_sta0 = lon_lat_to_cartesian(sta_to['lon'].values[:], sta_to['lat'].values[:],R = meteva.base.basicdata.ER)
    xyz_sta1 = lon_lat_to_cartesian(sta_from['lon'].values[:], sta_from['lat'].values[:],R = meteva.base.basicdata.ER)
    tree = cKDTree(xyz_sta1)
    _,indexs = tree.query(xyz_sta0, k=nearNum)
    input_dat = sta_from.loc[:, 'id'].values
    sta_ensemble = sta_to[meteva.base.get_coord_names()]
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
    xyz_sta0 = lon_lat_to_cartesian(sta_to['lon'].values[:], sta_to['lat'].values[:],R = meteva.base.basicdata.ER)
    xyz_sta1 = lon_lat_to_cartesian(sta_from['lon'].values[:], sta_from['lat'].values[:],R = meteva.base.basicdata.ER)
    tree = cKDTree(xyz_sta1)
    _,indexs = tree.query(xyz_sta0, k=nearNum)
    data_name = meteva.base.get_stadata_names(sta_from)[0]
    input_dat = sta_from[data_name].values
    sta_ensemble = sta_to[meteva.base.get_coord_names()]
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
    xyz_sta0 = lon_lat_to_cartesian(sta_to['lon'].values[:], sta_to['lat'].values[:],R = meteva.base.basicdata.ER)
    xyz_sta1 = lon_lat_to_cartesian(sta_from['lon'].values[:], sta_from['lat'].values[:],R = meteva.base.basicdata.ER)
    tree = cKDTree(xyz_sta1)
    d,_ = tree.query(xyz_sta0, k=nearNum)
    sta_ensemble = sta_to[meteva.base.get_coord_names()]
    for i in range(nearNum):
        data_name = "data" + str(i)
        sta_ensemble[data_name] = d[:,i]
    if drop_frist:
        sta_ensemble = sta_ensemble.drop(columns=['data0'])
    return sta_ensemble

def sta_index_ensemble_near_by_grid(sta, grid,nearNum = 1):
    ER = meteva.base.ER
    members = np.arange(nearNum).tolist()
    grid1 = meteva.base.grid(grid.glon,grid.glat,member_list=members)
    grd_en = meteva.base.grid_data(grid1)
    xyz_sta =  meteva.base.tool.math_tools.lon_lat_to_cartesian(sta.loc[:,"lon"], sta.loc[:,"lat"],R = ER)
    lon = np.arange(grid1.nlon) * grid1.dlon + grid1.slon
    lat = np.arange(grid1.nlat) * grid1.dlat + grid1.slat
    grid_lon,grid_lat = np.meshgrid(lon,lat)
    xyz_grid = meteva.base.tool.math_tools.lon_lat_to_cartesian(grid_lon.flatten(), grid_lat.flatten(),R = ER)
    tree = cKDTree(xyz_sta)
    value, inds = tree.query(xyz_grid, k=nearNum)
    grd_en.values = inds.reshape((nearNum,1,1,1,grid1.nlat,grid1.nlon))
    return grd_en

def values_list_list_in_r_of_sta(sta_to, r = 40, sta_from = None,drop_first = False):
    '''

    :param sta_to:
    :param r:
    :param sta_from:
    :param drop_first:
    :return: 返回的站点将会和sta_to 一致
    '''
    if(sta_to is None):
        return None
    if(sta_from is None):
        sta_from = copy.deepcopy(sta_to)
    sta_from = meteva.base.not_IV(sta_from)
    #print(sta_from)
    xyz_sta0 = lon_lat_to_cartesian(sta_to['lon'].values[:], sta_to['lat'].values[:],R = meteva.base.basicdata.ER)
    xyz_sta1 = lon_lat_to_cartesian(sta_from['lon'].values[:], sta_from['lat'].values[:],R = meteva.base.basicdata.ER)
    tree = cKDTree(xyz_sta1)
    data_name = meteva.base.get_stadata_names(sta_from)[0]
    input_dat = sta_from[data_name].values
    indexs_list = tree.query_ball_point(xyz_sta0,r=r)

    values_list = []
    if drop_first:
        for indexs in indexs_list:
            if len(indexs) >1:
                values = input_dat[indexs[1:]]
                values_list.append(values)
            else:
                values_list.append([meteva.base.IV])
    else:
        for indexs in indexs_list:
            values = input_dat[indexs]
            values_list.append(values)

    return values_list

def statistic_in_r_of_sta(sta_to,operation, r = 40, sta_from = None,drop_first = False):
    '''
    :param sta_to:
    :param r:
    :param sta_from:
    :param drop_first:
    :return: 返回的站点将会和sta_to 一致
    '''
    sta_result = sta_to[meteva.base.get_coord_names()]
    values_list_list = values_list_list_in_r_of_sta(sta_to, r = r, sta_from = sta_from,drop_first = drop_first)
    statistic_value = []
    #print(values_list_list)
    nsta = len(values_list_list)
    for n in  range(nsta):
        values_list = values_list_list[n]
        if(len(values_list)==0):
            statistic_value.append(meteva.base.IV)
        else:
            statistic_value.append(operation(values_list))
    statistic_value = np.array(statistic_value)
    sta_result[operation.__name__] = statistic_value
    return sta_result

def max_in_r_of_sta(sta_to, r = 40, sta_from = None,drop_first = False):
    '''
    :param sta_to:
    :param r:
    :param sta_from:
    :param drop_first:
    :return: 返回的站点将会和sta_to 一致
    '''

    return statistic_in_r_of_sta(sta_to,np.max, r = r, sta_from = sta_from,drop_first = drop_first)

def min_in_r_of_sta(sta_to, r = 40, sta_from = None,drop_first = False):
    '''
    :param sta_to:
    :param r:
    :param sta_from:
    :param drop_first:
    :return: 返回的站点将会和sta_to 一致
    '''

    return statistic_in_r_of_sta(sta_to,np.min, r = r, sta_from = sta_from,drop_first = drop_first)

def mean_in_r_of_sta(sta_to, r = 40, sta_from = None,drop_first = False):
    '''
    :param sta_to:
    :param r:
    :param sta_from:
    :param drop_first:
    :return: 返回的站点将会和sta_to 一致
    '''

    return statistic_in_r_of_sta(sta_to,np.mean, r = r, sta_from = sta_from,drop_first = drop_first)


def add_stavalue_to_nearest_grid(sta,grid):
    '''

    :param sta:
    :param grid:
    :return:
    '''
    grd = meteva.base.grid_data(meteva.base.grid(grid.glon,grid.glat,gtime=[sta.iloc[0,1]],dtime_list=[sta.iloc[0,2]],level_list=[sta.iloc[0,0]]))
    sta1 = meteva.base.sele.in_grid_xy(sta, grid)
    data_names = meteva.base.get_stadata_names(sta1)
    ig = np.round((sta1.loc[:,'lon'].values - grid.slon) // grid.dlon).astype(dtype = 'int16')
    jg = np.round((sta1.loc[:,'lat'].values - grid.slat) // grid.dlat).astype(dtype = 'int16')
    df = pd.DataFrame({"jg":jg,"ig":ig,"value":sta1.iloc[:,-1]})
    duplicate_data_sum = df.groupby(by=['jg','ig'],as_index=False)["value"].sum()
    ig_d = duplicate_data_sum["ig"].values
    jg_d = duplicate_data_sum["jg"].values
    value = duplicate_data_sum["value"].values
    grd.values[0, 0, 0, 0, jg_d, ig_d] = value[:]

    meteva.base.set_griddata_coords(grd, member_list=data_names)
    return grd

def add_stacount_to_nearest_grid(sta,grid):
    sta1 = sta.copy()
    data_names = meteva.base.get_stadata_names(sta)
    sta1 = meteva.base.sele_by_para(sta1,member=data_names[0])
    sta1.iloc[:,-1] = 1
    return add_stavalue_to_nearest_grid(sta1,grid)


