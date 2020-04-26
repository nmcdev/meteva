#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import xarray as xr
import numpy as np
import pandas as pd
import datetime
import re

def set_griddata_coords(grd,name = None,gtime = None,dtime_list = None,level_list = None, member_list = None):
    """
    设置xarray的coords的一些属性
    :param grd:初始化之后的xarry结构的多维格点网格
    :param level:层次，默认为None
    :param time：时间，默认为None
    :param dtime:时效，默认为None
    :param member：要素，默认为None
    如果level不为None，并且grd的level维度上size = 1，则将level方向的坐标统一设置为传入的参数level,time,dtime,member一样类似处理。
    :return:grd:返回一个设置好的coords的格点网格信息。
    """
    if name is not None:
        grd.name = name
    nmember = int(len(grd.coords.variables.get(grd.coords.dims[0])))
    nlevel = int(len(grd.coords.variables.get(grd.coords.dims[1])))
    ndtime = int(len(grd.coords.variables.get(grd.coords.dims[3])))
    if level_list != None:
        if len(level_list) == nlevel:
            grd.coords["level"] = level_list
        else:
            print("level_list长度和grid_data的level维度的长度不一致")
    if dtime_list != None:
        if len(dtime_list) == ndtime:
            grd.coords["dtime"] = dtime_list
        else:
            print("dtime_list长度和grid_data的dtime维度的长度不一致")
    if member_list != None:
        if len(member_list) == nmember:
            grd.coords["member"] = member_list
        else:
            print("member_list长度和grid_data的member维度的长度不一致")
    ntime = int(len(grd.coords.variables.get(grd.coords.dims[2])))

    if gtime is not None:
        #time_list 内的内容兼容datetime 和str两种格式

        if len(gtime) == 1:
            if ntime == 1:
                if type(gtime[0]) == str:
                    num = ''.join([x for x in gtime[0] if x.isdigit()])
                    # 用户输入2019041910十位字符，后面补全加0000，为14位统一处理
                    if len(num) == 4:
                        num += "0101000000"
                    elif len(num) == 6:
                        num +="01000000"
                    elif len(num) == 8:
                        num +="000000"
                    elif len(num) == 10:
                        num +="0000"
                    elif len(num) == 12:
                        num +="00"
                    else:
                        print("输入日期有误，请检查！")
                    # 统一将日期变为datetime类型
                    time1 = datetime.datetime.strptime(num, '%Y%m%d%H%M%S')
                    grd.coords["time"] = [np.datetime64(time1)]
                else:
                    grd.coords["time"] = gtime
            else:
                print("gtime对应的时间序列长度和grid_data的time维度的长度不一致")
        elif len(gtime) ==3:
            num1 =[]
            if type(gtime[0]) == str:
                for i in range (0,2):
                    num = ''.join([x for x in gtime[i] if x.isdigit()])
                    #用户输入2019041910十位字符，后面补全加0000，为14位统一处理
                    if len(num) == 4:
                        num1.append(num + "0101000000")
                    elif len(num) == 6:
                        num1.append(num + "01000000")
                    elif len(num) == 8:
                        num1.append(num + "000000")
                    elif len(num) == 10:
                        num1.append(num + "0000")
                    elif len(num) == 12:
                        num1.append(num + "00")
                    elif len(num) == 14:
                        num1.append(num)
                    else:
                        print("输入日期有误，请检查！")
                    #统一将日期变为datetime类型
                stime = datetime.datetime.strptime(num1[0], '%Y%m%d%H%M%S')
                etime = datetime.datetime.strptime(num1[1], '%Y%m%d%H%M%S')
                stime = np.datetime64(stime)
                etime = np.datetime64(etime)
            else:
                stime = gtime[0]
                etime = gtime[1]



            times = pd.date_range(stime, etime, freq=gtime[2])
            if ntime == len(times):
                grd.coords["time"] = times
            else:
                print("gtime对应的时间序列长度和grid_data的time维度的长度不一致")

    return

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
    #print(grid.gtime[2])
    times = pd.date_range(grid.stime, grid.etime, freq=grid.gtime[2])
    ntime = len(times)
    # 根据timedelta的格式，算出ndt次数和gds时效列表

    ndt = len(grid.dtimes)
    gdt_list = grid.dtimes

    level_list = grid.levels
    nlevel_list = len(level_list)

    member_list = grid.members
    nmember = len(member_list)
    if data is None:
        data = np.zeros((nmember, nlevel_list, ntime, ndt, nlat, nlon))
    else:
        data = data.reshape(nmember, nlevel_list, ntime, ndt, nlat, nlon)

    grd = (xr.DataArray(data, coords={'member': member_list,'level': level_list,'time': times,'dtime':gdt_list,
                               'lat': lat, 'lon': lon},
                         dims=['member', 'level','time', 'dtime','lat', 'lon']))

    grd.name = "data0"
    return grd



def DataArray_to_grd(dataArray,member = None,level = None,time = None,dtime = None,lat = None,lon = None):
    da = copy.deepcopy(dataArray)
    dim_order = {}
    new_coods = {}

    if member is None:
        da  = da.expand_dims("member")
        dim_order["member"] = "member"
        new_coods["member"] = [0]
    elif type(member) == str:
        if member in da.coords:
            dim_order["member"] = member
            new_coods["member"] = da.coords[member]
        else:
            da = da.expand_dims("member")
            dim_order["member"] = "member"
            new_coods["member"] = [0]
    else:
        dim_order["member"] = member.dims[0]
        new_coods["member"] = member.values.tolist()

    if level is None:
        da = da.expand_dims("level")
        dim_order["level"] = "level"
        new_coods["level"] = [0]
    elif type(level) == str:
        if level in da.coords:
            dim_order["level"] = level
            new_coods["level"] = da.coords[level]
        else:
            da = da.expand_dims("level")
            dim_order["level"] = "level"
            new_coods["level"] = [0]
    else:
        dim_order["level"] = level.dims[0]
        new_coods["level"] = level.values.tolist()


    if time is None:
        da = da.expand_dims("time")
        dim_order["time"] = "time"
        new_coods["time"] = pd.date_range("2099-1-1", periods=1)
    elif type(time) == str:
        if time in da.coords:
            dim_order["time"] = time
            new_coods["time"] = da.coords[time]
        else:
            da = da.expand_dims("time")
            dim_order["time"] = "time"
            new_coods["time"] = pd.date_range("2099-1-1", periods=1)
    else:
        dim_order["time"] = time.dims[0]
        new_coods["time"] = time.values.tolist()

    if dtime is None:
        da = da.expand_dims("dtime")
        dim_order["dtime"] = "dtime"
        new_coods["dtime"] = [0]
    elif type(dtime) == str:
        if dtime in da.coords:
            dim_order["dtime"] = dtime
            new_coods["dtime"] = da.coords[dtime]
        else:
            da = da.expand_dims("dtime")
            dim_order["dtime"] = "dtime"
            new_coods["dtime"] = [0]
    else:
        dim_order["level"] = dtime.dims[0]
        new_coods["dtime"] = dtime.values.tolist()

    if lat is None:
        da = da.expand_dims("lat")
        dim_order["lat"] = "latitude"
        new_coods["lat"] = [0]
    elif type(lat) == str:
        if lat in da.coords:
            dim_order["lat"] = lat
            new_coods["lat"] = da.coords[lat]
        else:
            da = da.expand_dims("lat")
            dim_order["lat"] = "latitude"
            new_coods["lat"] = [0]
    else:
        dim_order["lat"] = lat.dims[0]
        new_coods["lat"] = lat.values.tolist()

    if lon is None:
        da = da.expand_dims("lon")
        dim_order["lon"] = "longitude"
        new_coods["lon"] = [0]
    elif type(lon) == str:
        if lon in da.coords:
            dim_order["lon"] = lon
            new_coods["lon"] = da.coords[lon]
        else:
            da = da.expand_dims("lon")
            dim_order["lon"] = "longitude"
            new_coods["lon"] = [0]
    else:
        dim_order["lon"] = lon.dims[0]
        new_coods["lon"] = lon.values.tolist()
    da = da.transpose(dim_order["member"], dim_order["level"], dim_order["time"],
                      dim_order["dtime"], dim_order["lat"], dim_order["lon"])

    da = xr.DataArray(da.values, coords=new_coods, dims=["member","level","time","dtime","latitude","longitude"])
    da.name ="data"
    return da




def reset(grd):
    lats = grd["lat"].values

    if lats[0]>lats[1]:
        lats = grd["lat"].values[::-1]
        grd['lat'] = lats
        dat = grd.values[:, :, :, :, ::-1, :]
        grd.values = dat

    return