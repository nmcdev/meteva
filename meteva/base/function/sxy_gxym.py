#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import meteva
from scipy.spatial import cKDTree
import numpy as np

ER = 6371
def get_nearby_sta_index_ensemble(sta, grid,nearNum = 1):
    members = np.arange(nearNum).tolist()
    grid1 = meteva.base.grid(grid.glon,grid.glat,members=members)
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
