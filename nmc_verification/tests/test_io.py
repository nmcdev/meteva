
import nmc_verification.nmc_vf_base as nmb
import numpy as np
import datetime
import pandas as pd

def test_read_write_micaps4():
    path = r"H:\task\develop\python\git\nmc_met_class\nmc_met_class\tests\test_data\grid_fo.txt"
    grd = nmb.io.rg.read_from_micaps4(path)
    nmb.io.wg.write_to_micaps4(grd)
    sta = nmb.fun.gxy_sta.transform(grd)
    grd1 = nmb.fun.sta_gxy.transform(sta)
    nmb.io.wg.write_to_micaps4(grd1)
    #print(sta)

def test_read_nc():
    path = r"K:\paper13\m8\18010100.003.nc"
    #path = r"H:\task\develop\python\git\nmc_met_class\nmc_met_class\tests\a.txt"
    #from nmc_met_class.io.read_DataArray import read_from_nc
    grd = nmb.io.rg.read_from_nc(path)
    grd = nmb.bd.set_coords(grd,level=850,time='2019051901',dtime="4d")
    #nmc.io.wg.write_to_nc(grd,scale_factor=1)
    grid0 = nmb.bd.get_grid_of_data(grd)

    grd0 = nmb.bd.grid_data(grid0)

    nmb.io.wg.write_to_micaps4(grd0)
    print(grd)


def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'red' if val < 2 else 'black'
    return 'color: %s' % color

def interpolation():
    path = r"H:\task\develop\python\git\nmc_met_class\nmc_met_class\tests\test_data\grid_fo.txt"
    grd = nmb.io.rg.read_from_micaps4(path)
    #grid0 = nmc.bd.get_grid_of_data(grd)
    print(grd)
    grid0 = nmb.bd.grid.grid([80,130,0.125],[20,40,0.125])
    print(grid0.tostring())
    grd1 = nmb.fun.gxy_gxy.interpolation_linear(grd,grid0,reserve_other_dim=True)
    print(grd1)
    nmb.io.wg.write_to_micaps4(grd1)

    path = r"H:\task\develop\python\git\nmc_met_class\nmc_met_class\tests\test_data\评分站点.txt"
    station = nmb.io.rs.read_from_micaps3(path)
    print(station)
    sta1 = nmb.fun.gxy_sta.interpolation_linear(grd1,station)
    nmb.io.ws.write_to_micaps3(sta1)
    print(sta1.style.applymap(color_negative_red))

    pass

#interpolation()

def test_read_m3():
    path = r"H:\task\develop\python\git\nmc_met_class\nmc_met_class\tests\test_data\评分站点.txt"
    station = nmb.io.rs.read_from_micaps3(path)
    print(station)
    station['data0'] = 0
    path = r"H:\task\develop\python\git\nmc_met_class\nmc_met_class\tests\test_data\rain_without0.txt"
    sta = nmb.io.rs.read_from_micaps3(path,station= station,reserve_time_dtime_level=True)
    print(sta)
    grid0 = nmb.bd.grid([70,140,0.5],[10,60,0.5])
    background = nmb.bd.grid_data(grid0)
    grd = nmb.fun.sta_gxy.sta_to_grid_oa2(sta,background=background)

    nmb.io.wg.write_to_micaps4(grd)
    print(grd)

test_read_m3()

#test_read_write_micaps4()