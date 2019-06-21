import numpy as np
import nmc_verification

#获取num层的网格数据
def get_member(grd,num):
    dat = grd.values[num,0,0,0,:,:]
    grid0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd)
    grid1 = nmc_verification.nmc_vf_base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.gdtime,grid0.levels)
    grd1= nmc_verification.nmc_vf_base.basicdata.grid_data(grid1,dat)
    return grd1

#获取网格数据的平均值
def get_mean(grd,member_name):
    grid0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd)
    grid1 = nmc_verification.nmc_vf_base.basicdata.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.gdtime,grid0.levels,members=[member_name])
    dat = np.squeeze(grd.values)
    dat = np.mean(dat,axis = 0)
    grd1 = nmc_verification.nmc_vf_base.basicdata.grid_data(grid1,dat)
    return grd
