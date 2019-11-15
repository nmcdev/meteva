import nmc_verification
from nmc_verification.nmc_vf_base.tool.math_tools import lon_lat_to_cartesian
from scipy.spatial import cKDTree
import numpy as np
import copy

def get_nearby_sta_index_ensemble(sta_to,nearNum = 100,sta_from = None,drop_frist = False):
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

def get_nearby_sta_id_ensemble(sta_to,nearNum = 100,sta_from = None,drop_frist = False):
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

def get_nearby_sta_value_ensemble(sta_to,nearNum = 100,sta_from = None,drop_frist = False):
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

def get_nearby_sta_dis_ensemble(sta_to,nearNum = 100,sta_from = None,drop_frist = False):
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



