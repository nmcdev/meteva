import numpy as np
import nmc_verification.nmc_vf_base.basicdata as bd

def get_member(grd,num):
    dat = grd.values[num,0,0,0,:,:]
    grid0 = bd.get_grid_of_data(grd)
    grid1 = bd.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.gdtime,grid0.levels)
    grd1= bd.grid_data(grid1,dat)
    return grd1

def get_mean(grd):
    grid0 = bd.get_grid_of_data(grd)
    grid1 = bd.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.gdtime,grid0.levels)
    dat = np.squeeze(grd.values)
    dat = np.mean(dat,axis = 0)
    grd1 = bd.grid_data(grid1,dat)
    return grd
