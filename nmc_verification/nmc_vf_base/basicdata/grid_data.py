#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import xarray as xr
import numpy as np
import pandas as pd
import datetime
import re

def set_coords(grd,level = None,time = None,dtime = None, member = None):
    #如果level 不为None，并且grd0 的level维度上size = 1，则将level方向的坐标统一设置为传入的参数level
    #其它参数类似处理
    nmember = int(len(grd.coords.variables.get(grd.coords.dims[0])))
    nlevel = int(len(grd.coords.variables.get(grd.coords.dims[1])))
    ntime = int(len(grd.coords.variables.get(grd.coords.dims[2])))
    ndt = int(len(grd.coords.variables.get(grd.coords.dims[3])))
    if (level != None) and (nlevel == 1):
        grd.coords["level"] = [level]
    #time和dtime的时候兼容一下datetime 和str两种格式
    if (time != None) and (ntime == 1):
        time1 = []
        if type(time) == str:
            if len(time) == 4:
                time1.append(time + "0101000000")
            elif len(time) == 6:
                time1.append(time + "01000000")
            elif len(time) == 8:
                time1.append(time + "000000")
            elif len(time) == 10:
                time1.append(time + "0000")
            elif len(time) == 12:
                time1.append(time + "00")
            elif len(time) == 14:
                time1.append(time)
            else:
                print("输入日期有误，请检查！")
            ttime = datetime.datetime.strptime(time1[0], '%Y%m%d%H%M%S')
        else:
            ttime = time
        grd.coords["time"] = [ttime]
    if (dtime != None) and (ndt == 1):
        if type(dtime) == str:
            gdt_num = ''.join([x for x in dtime if x.isdigit()])
            dt_int = int(gdt_num)
            TIME_type = re.findall(r"\D+", dtime)[0]
            if(TIME_type == "d"):TIME_type = "D"
            ddtime = np.timedelta64(dt_int, TIME_type)
        else:
            ddtime = dtime
        grd.coords["dtime"] = [ddtime]
    if (member != None) and (nmember == 1):
        grd.coords["member"] = [member]
    return grd

#返回一个DataArray，其维度信息和grid描述一致，数组里面的值为0.
def grid_data(grid,data=None):
    slon = grid.slon
    dlon = grid.dlon
    slat = grid.slat
    dlat = grid.dlat
    nlon = grid.nlon
    nlat = grid.nlat
    # 通过起始经纬度和格距计算经纬度格点数
    lon = np.arange(nlon) * dlon + slon
    lat = np.arange(nlat) * dlat + slat

    times = pd.date_range(grid.stime, grid.etime, freq=grid.gdtime[2])
    ntime = len(times)
    # 根据timedelta的格式，算出ndt次数和gds时效列表
    edtimedelta = grid.edtimedelta
    sdtimedelta = grid.sdtimedelta
    ddtimedelta = grid.ddtimedelta
    ndt = int((edtimedelta - sdtimedelta) / ddtimedelta) + 1
    gdt_list = []
    for i in range(ndt):
        gdt_list.append(sdtimedelta + ddtimedelta * i)

    levels = grid.levels
    nlevels = len(levels)

    nmember = grid.nmember
    if np.all(data == None):
        data = np.zeros((nmember, nlevels, ntime, ndt, nlat, nlon))
    else:
        data = data.reshape(nmember, nlevels, ntime, ndt, nlat, nlon)
    return (xr.DataArray(data, coords={'member': np.arange(nmember),'level': levels,'time': times,'dtime':gdt_list,
                               'lat': lat, 'lon': lon},
                         dims=['member', 'level','time', 'dtime','lat', 'lon']))

