#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import xarray as xr
import numpy as np
import pandas as pd
import datetime
import re
import copy

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

def xarray_to_griddata(xr0,value_name = None,member_dim = None,level_dim = None,time_dim = None,dtime_dim = None,lat_dim = None,lon_dim = None):
    drop_list = []
    ds = xr.Dataset()
    if isinstance(xr0,xr.DataArray):
        ds0 = xr.Dataset({'data0': xr0})
    else:
        ds0 = xr0
    # 1判断要素成员member
    if (member_dim is None):
        member_dim = "member"
    if member_dim in list(ds0.coords) or member_dim in list(ds0.dims):
        if member_dim in ds0.coords:
            members = ds0.coords[member_dim]
        else:
            members = ds0[member_dim]
            drop_list.append(member_dim)

        ds.coords["member"] = ("member", members)
        attrs_name = list(members.attrs)
        for key in attrs_name:
            ds.member.attrs[key] = members.attrs[key]
    else:
        ds.coords["member"] = ("member", [0])

    # 2判断层次level
    if (level_dim is None):
        if "level" in list(ds0.coords) or "level" in list(ds0):
            level_dim = "level"
        elif "lev" in ds0.coords or "lev" in list(ds0):
            level_dim = "lev"
    if level_dim in ds0.coords or level_dim in list(ds0):
        if level_dim in ds0.coords:
            levels = ds0.coords[level_dim]
        else:
            levels = ds0[level_dim]
            drop_list.append(level_dim)
        ds.coords["level"] = ("level", levels)
        attrs_name = list(levels.attrs)
        for key in attrs_name:
            ds.level.attrs[key] = levels.attrs[key]
    else:
        ds.coords["level"] = ("level", [0])

    # 3判断时间time
    if (time_dim is None):
        if "time" in ds0.coords or "time" in list(ds0):
            time_dim = "time"

    if time_dim in ds0.coords or time_dim in list(ds0):
        if time_dim in ds0.coords:
            times = ds0.coords[time_dim]
        else:
            times = ds0[time_dim]
        ds.coords["time"] = ("time", times)
        attrs_name = list(times.attrs)
        for key in attrs_name:
            ds.time.attrs[key] = times.attrs[key]
    else:
        ds.coords["time"] = ("time", [0])

    # 4判断时效dt
    if (dtime_dim is None):
        dtime_dim = "dtime"
    if dtime_dim in ds0.coords or dtime_dim in list(ds0):
        if dtime_dim in ds0.coords:
            dts = ds0.coords[dtime_dim]
        else:
            dts = ds0[dtime_dim]
            drop_list.append(dtime_dim)

        ds.coords["dtime"] = ("dtime", dts)
        attrs_name = list(dts.attrs)
        for key in attrs_name:
            ds.dtime.attrs[key] = dts.attrs[key]
    else:
        ds.coords["dtime"] = ("dtime", [0])

    # 5判断纬度lat
    if (lat_dim is None):
        if "latitude" in ds0.coords or "latitude" in list(ds0):
            lat_dim = "latitude"
        elif "lat" in ds0.coords or "lat" in list(ds0):
            lat_dim = "lat"
    if lat_dim in ds0.coords or lat_dim in list(ds0):
        if lat_dim in ds0.coords:
            lats = ds0.coords[lat_dim]
        else:
            lats = ds0[lat_dim]
            drop_list.append(lat_dim)
        dims = lats.dims
        if len(dims) == 1:
            ds.coords["lat"] = ("lat", lats)
        else:
            if "lon" in dims[0].lower() or "x" in dims.lower():
                lats = lats.values.T
            ds.coords["lat"] = (("lat", "lon"), lats)
        attrs_name = list(lats.attrs)
        for key in attrs_name:
            ds.lat.attrs[key] = lats.attrs[key]
    else:
        ds.coords["lat"] = ("lat", [0])

    # 6判断经度lon
    if (lon_dim is None):
        if "longitude" in ds0.coords or "longitude" in list(ds0):
            lon_dim = "longitude"
        elif "lon" in ds0.coords or "lon" in list(ds0):
            lon_dim = "lon"
    if lon_dim in ds0.coords or lon_dim in list(ds0):
        if lon_dim in ds0.coords:
            lons = ds0.coords[lon_dim]
        else:
            lons = ds0[lon_dim]
            print(lons)
            drop_list.append(lon_dim)

        dims = lons.dims
        if len(dims) == 1:
            ds.coords["lon"] = ("lon", lons)
        else:
            if "lon" in dims[0].lower() or "x" in dims.lower():
                lons = lons.values.T
            ds.coords["lon"] = (("lat", "lon"), lons)
        attrs_name = list(lons.attrs)
        for key in attrs_name:
            ds.lon.attrs[key] = lons.attrs[key]
    else:
        ds.coords["lon"] = ("lon", [0])

    da = None
    if value_name is not None:
        da = ds0[value_name]
        name = value_name
    else:
        name_list = list((ds0))
        for name in name_list:
            if name in drop_list: continue
            da = ds0[name]
            shape = da.values.shape
            size = 1
            for i in range(len(shape)):
                size = size * shape[i]
            if size > 1:
                break

    dims = da.dims
    dim_order = {}

    for dim in dims:
        if member_dim == dim:
            dim_order["member"] = dim
        elif level_dim == dim:
            dim_order["level"] = dim
        elif time_dim == dim:
            dim_order["time"] = dim
        elif dtime_dim == dim:
            dim_order["dtime"] = dim
        elif lon_dim == dim:
            dim_order["lon"] = dim
        elif lat_dim == dim:
            dim_order["lat"] = dim
    for dim in dims:
        if "member" not in dim_order.keys() and "member" in dim.lower():
            dim_order["member"] = dim
        elif "time" not in dim_order.keys() and dim.lower().find("time") == 0:
            dim_order["time"] = dim
        elif "dtime" not in dim_order.keys() and dim.lower().find("dt") == 0:
            dim_order["dtime"] = dim
        elif "level" not in dim_order.keys() and dim.lower().find("lev") == 0:
            dim_order["level"] = dim
        elif "lat" not in dim_order.keys() and (dim.lower().find("lat") == 0 or 'y' == dim.lower()):
            dim_order["lat"] = dim
        elif "lon" not in dim_order.keys() and (dim.lower().find("lon") == 0 or 'x' == dim.lower()):
            dim_order["lon"] = dim

    if "member" not in dim_order.keys():
        dim_order["member"] = "member"
        da = da.expand_dims("member")
    if "time" not in dim_order.keys():
        dim_order["time"] = "time"
        da = da.expand_dims("time")
    if "level" not in dim_order.keys():
        dim_order["level"] = "level"
        da = da.expand_dims("level")
    if "dtime" not in dim_order.keys():
        dim_order["dtime"] = "dtime"
        da = da.expand_dims("dtime")
    if "lat" not in dim_order.keys():
        dim_order["lat"] = "lat"
        da = da.expand_dims("lat")
    if "lon" not in dim_order.keys():
        dim_order["lon"] = "lon"
        da = da.expand_dims("lon")

    # print(da)
    da = da.transpose(dim_order["member"], dim_order["level"], dim_order["time"],
                      dim_order["dtime"], dim_order["lat"], dim_order["lon"])
    # print(name)
    ds[name] = (("member", "level", "time", "dtime", "lat", "lon"), da)
    attrs_name = list(da.attrs)
    for key in attrs_name:
        ds[name].attrs[key] = da.attrs[key]
    attrs_name = list(ds0.attrs)
    for key in attrs_name:
        ds.attrs[key] = ds0.attrs[key]

    ds0.close()
    da1 = ds[name]

    if da1.coords['time'] is None:
        da1.coords['time'] = pd.date_range("2099-1-1", periods=1)
    if da1.coords['dtime'] is None:
        da1.coords['dtime'] = [0]

    if isinstance(da1.coords["dtime"].values[0], np.timedelta64):
        dtime_int_m = (da1.coords["dtime"] / np.timedelta64(1, 'm'))
        dtime_int_dm = dtime_int_m % 60
        maxdm = np.max(dtime_int_dm)
        if maxdm == 0:
            # print(dtime_int)
            da1.coords["dtime"] = (dtime_int_m / 60).astype(np.int16)
        else:
            da1.coords["dtime"] = (dtime_int_m + 10000).astype(np.int16)

    attrs_name = list(da1.attrs)
    if "dtime_type" in attrs_name:
        da1.attrs["dtime_type"] = "hour"

    reset(da1)
    return da1



def DataArray_to_grd(dataArray,member = None,level = None,time = None,dtime = None,lat = None,lon= None):
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