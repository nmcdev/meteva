#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import numpy as np
import os
import math
import xarray as xr
import datetime
import pandas as pd
import traceback
import meteva
import struct
from . import DataBlock_pb2
from .GDS_data_service import GDSDataService
import copy

def grid_ragular(slon,dlon,elon,slat,dlat,elat):
    """
    规范化格点（起始经纬度，间隔经度，格点数）
    :param slon:起始经度
    :param dlon:经度的精度
    :param elon:结束经度
    :param slat:起始纬度
    :param dlat:纬度的精度
    :param elat:结束纬度
    :return:slon1,dlon1,elon1,slat1,dlat1,elat1,nlon1,nlat1
    返回规范化后的格点信息。
    """
    slon1 = slon
    dlon1 = dlon
    elon1 = elon
    slat1 = slat
    dlat1 = dlat
    elat1 = elat
    nlon = 1 + (elon1 - slon1) / dlon1
    error = abs(round(nlon) - nlon)
    if (error > 0.05):
        nlon1 = math.ceil(nlon)
    else:
        nlon1 = int(round(nlon))
    nlat = 1 + (elat - slat) / dlat
    error = abs(round(nlat) - nlat)
    if (error > 0.05):
        nlat1 = math.ceil(nlat)
    else:
        nlat1 = int(round(nlat))
    return slon1,dlon1,elon1,slat1,dlat1,elat1,nlon1,nlat1


def read_griddata_from_micaps4(filename,grid=None,level = None,time = None,dtime = None,data_name = "data0",show = False):
    '''
    读取micaps4格式的格点数据，并将其保存为xarray中DataArray结构的六维数据信息
    :param filename:Micaps4格式的文件路径和文件名
    :param grid:格点的经纬度信息，默认为：None,如果有传入grid信息，需要使用双线性插值进行提取。
    :return:返回一个DataArray结构的六维数据信息da
    '''
    try:
        encoding,str1 = meteva.base.io.get_encoding_of_file(filename)
        if encoding is None:return
        #file = open(filename,'r',encoding=encoding)
        #str1 = file.read()
        #file.close()
        strs = str1.split()
        year1 = int(strs[3])
        month = int(strs[4])
        day = int(strs[5])
        hour = int(strs[6])
        dts = int(strs[7])
        if level is None:
            level = float(strs[8])

        #由于m4只提供年份的后两位，因此，做了个暂时的换算范围在1920-2019年的范围可以匹配成功
        if len(str(year1)) ==4:
            year3 = str(year1)
        else:
            if year1 >= 50:
                year3 = '19' + str(year1)
            else:
                year3 = '20' + str(year1)
        ymd = year3 + "%02d" % month + "%02d" % day + "%02d" % hour + '00'
        dlon = float(strs[9])
        dlat = float(strs[10])
        slon = float(strs[11])
        elon = float(strs[12])
        slat = float(strs[13])
        elat = float(strs[14])
        slon1, dlon1, elon1, slat1, dlat1, elat1, nlon1, nlat1 = grid_ragular(slon,dlon,elon,slat,dlat,elat)
        if len(strs) - 22 >= nlon1 * nlat1 :
            #用户没有输入参数信息的时候，使用m4文件自带的信息
            k = 22
            dat = (np.array(strs[k:])).astype(float).reshape((1, 1, 1, 1, nlat1, nlon1))
            lon = np.arange(nlon1) * dlon1 + slon1
            lat = np.arange(nlat1) * dlat1 + slat1
            if time is None:
                time = pd.to_datetime(ymd, format = "%Y%m%d%H%M" )
            else:
                time = meteva.base.tool.time_tools.all_type_time_to_time64(time)
            #print(dates)
            #times = pd.date_range(dates, periods=1)
            if dtime is None:
                dtime = dts
            #print(levels,times,dts)
            da = xr.DataArray(dat, coords={'member': [data_name], 'level': [level], 'time': [time], 'dtime': [dtime],
                                           'lat': lat, 'lon': lon},
                              dims=['member', 'level', 'time', 'dtime', 'lat', 'lon'])
            da.attrs["dtime_type"] = "hour"
            da.name = "data0"
            meteva.base.reset(da)
            if grid is None:
                if show:
                    print("success read from " + filename)
                return da
            else:
                #如果传入函数有grid信息，就需要进行一次双线性插值，按照grid信息进行提取网格信息。
                da1 = meteva.base.interp_gg_linear(da, grid)
                if show:
                    print("success read from " + filename)
                return da1
        else:
            return None
    except (Exception, BaseException) as e:
        exstr = traceback.format_exc()
        print(exstr)
        print(e)
        return None

#读取nc数据
def read_griddata_from_nc(filename,grid = None,
            value_name = None,member_dim = None,level_dim = None,time_dim = None,dtime_dim = None,lat_dim = None,lon_dim = None,
                         level=None, time=None, dtime=None, data_name="data0",show = False):

    """
    读取NC文件，并将其保存为xarray中DataArray结构的六维数据信息
    :param filename:NC格式的文件路径和文件名
    :param value_name:nc文件中要素name的值,默认：None
    :param member:要素名,默认：None
    :param level:层次,默认：None
    :param time:时间,默认：None
    :param dt:时效,默认：None
    :param lat:纬度,默认：None
    :param lon:经度,默认：None
    :return:返回一个DataArray结构的六维数据信息da1
    """
    if not os.path.exists(filename):
        print(filename+" not exists")
        return
    try:
        ds0 = xr.open_dataset(filename)
        drop_list = []
        ds = xr.Dataset()
        #1判断要素成员member
        if(member_dim is None):
            member_dim = "member"
        if member_dim in list(ds0.coords) or member_dim in list(ds0):
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

        #2判断层次level
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
        if(time_dim is None):
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

        #5判断纬度lat
        if(lat_dim is None):
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
                ds.coords["lat"] = (("lat","lon"), lats)
            attrs_name = list(lats.attrs)
            for key in attrs_name:
                ds.lat.attrs[key] = lats.attrs[key]
        else:
            ds.coords["lat"] = ("lat",[0])

        #6判断经度lon
        if(lon_dim is None):
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
                ds.coords["lon"] = (("lat","lon"), lons)
            attrs_name = list(lons.attrs)
            for key in attrs_name:
                ds.lon.attrs[key] = lons.attrs[key]
        else:
            ds.coords["lon"] = ("lon",[0])

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
            if  "member" in dim.lower():
                dim_order["member"] = dim
            elif dim.lower().find("time") ==0:
                dim_order["time"] = dim
            elif dim.lower().find("dt") ==0:
                dim_order["dtime"] = dim
            elif dim.lower().find("lev") ==0:
                dim_order["level"] = dim
            elif dim.lower().find("lat") ==0 or 'y' == dim.lower():
                dim_order["lat"] = dim
            elif dim.lower().find("lon") ==0 or 'x' == dim.lower():
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
            da = da .expand_dims("lon")

        #print(da)
        da = da.transpose(dim_order["member"],dim_order["level"],dim_order["time"],
                          dim_order["dtime"],dim_order["lat"],dim_order["lon"])
        #print(name)
        ds[name] = (("member","level","time","dtime","lat","lon"),da)
        attrs_name = list(da.attrs)
        for key in attrs_name:
            ds[name].attrs[key] = da.attrs[key]
        attrs_name = list(ds0.attrs)
        for key in attrs_name:
            ds.attrs[key] = ds0.attrs[key]

        ds0.close()
        da1 = ds[name]
        da1.name = "data"
        if da1.coords['time'] is None:
            da1.coords['time'] = pd.date_range("2099-1-1",periods=1)
        if da1.coords['dtime'] is None:
            da1.coords['dtime'] = [0]


        if isinstance(da1.coords["dtime"].values[0], np.timedelta64):
            dtime_int_m = (da1.coords["dtime"]/np.timedelta64(1, 'm'))
            dtime_int_dm = dtime_int_m%60
            maxdm  = np.max(dtime_int_dm)
            if maxdm ==0:
                #print(dtime_int)
                da1.coords["dtime"] = (dtime_int_m/60).astype(np.int16)
            else:
                da1.coords["dtime"] = (dtime_int_m +10000).astype(np.int16)

        attrs_name = list(da1.attrs)
        if "dtime_type" in attrs_name:
            da1.attrs["dtime_type"]= "hour"

        meteva.base.reset(da1)
        if time is not None and len(da1.coords["time"])==1:
            meteva.base.set_griddata_coords(da1,gtime=[time])
        if dtime is not None and len(da1.coords["dtime"])==1:
            meteva.base.set_griddata_coords(da1,dtime_list=[dtime])
        if level is not None and len(da1.coords["level"])==1:
            meteva.base.set_griddata_coords(da1,level_list=[level])
        if data_name is not None and len(da1.coords["member"])==1:
            meteva.base.set_griddata_coords(da1,member_list=[data_name])

        if grid is None:
            da1.name = "data0"
            if show:
                print("success read from " + filename)
            return da1
        else:
            # 如果传入函数有grid信息，就需要进行一次双线性插值，按照grid信息进行提取网格信息。
            da2 = meteva.base.interp_gg_linear(da1, grid)
            da2.name = "data0"
            if show:
                print("success read from " + filename)
            return da2
    except (Exception, BaseException) as e:
        exstr = traceback.format_exc()
        print(exstr)
        print(e)
        return None


#读取nc数据
def read_griddata_from_nc1(filename,grid = None,value_name = None,member = None,level = None,time = None,dt = None,lat = None,lon = None):

    """
    读取NC文件，并将其保存为xarray中DataArray结构的六维数据信息
    :param filename:NC格式的文件路径和文件名
    :param value_name:nc文件中要素name的值,默认：None
    :param member:要素名,默认：None
    :param level:层次,默认：None
    :param time:时间,默认：None
    :param dt:时效,默认：None
    :param lat:纬度,默认：None
    :param lon:经度,默认：None
    :return:返回一个DataArray结构的六维数据信息da1
    """
    try:
        ds0 = xr.open_dataset(filename)
        drop_list = []
        ds = xr.Dataset()
        #1判断要素成员member
        if member in list(ds0):
            drop_list.append(member)
            member =  ds0[member]

        #2判断层次level
        if level in list(ds0):
            drop_list.append(level)
            level = ds0[level]
        #3 time
        if time is None:
            if "time" in ds0.coords or "time" in list(ds0):
                time = "time"
        elif time in list(ds0):
            drop_list.append(time)
            time = ds0[time]

        if dt in list(ds0):
            drop_list.append(dt)
            dt = ds0[dt]

        #5判断纬度lat
        if(lat is None):
            if "latitude" in ds0.coords or "latitude" in list(ds0):
                lat = "latitude"
            elif "lat" in ds0.coords or "lat" in list(ds0):
                lat = "lat"

        if lat in list(ds0):
            drop_list.append(lat)
            lat = ds0[lat]

        #6判断经度lon
        if(lon is None):
            if "longitude" in ds0.coords or "longitude" in list(ds0):
                lon = "longitude"
            elif "lon" in ds0.coords or "lon" in list(ds0):
                lon = "lon"
        if lon in list(ds0):
            drop_list.append(lon)
            lon = ds0[lon]

        da = None
        if value_name is not None:
            da = ds0[value_name]
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
        da1 = meteva.base.basicdata.DataArray_to_grd(da,member,level,time,dt,lat,lon)

        meteva.base.reset(da1)
        if grid is None:
            da1.name = "data0"
            return da1
        else:
            # 如果传入函数有grid信息，就需要进行一次双线性插值，按照grid信息进行提取网格信息。
            da2 = meteva.base.interp_gg_linear(da1, grid)
            da2.name = "data0"
            return da2


    except:
        exstr = traceback.format_exc()
        print(exstr)


def read_griddata_from_gds_file(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",show = False):
    try:
        if not os.path.exists(filename):
            print(filename + " is not exist")
            return None
        file = open(filename, 'rb')
        byteArray = file.read()
        grd = byteArray_to_griddata(byteArray,grid,level,time,dtime,data_name)
        if show:
            print("success read from " + filename)
        return grd
    except Exception as e:
        print(e)
        return None



def read_griddata_from_gds(ip,port,filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",show = False):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"

    service = GDSDataService(ip, port)
    try:
        if(service is None):
            print("service is None")
            return
        filename = filename.replace("mdfs:///", "")
        filename = filename.replace("\\","/")
        directory,fileName = os.path.split(filename)
        status, response = service.getData(directory, fileName)
        ByteArrayResult = DataBlock_pb2.ByteArrayResult()

        if status == 200:
            ByteArrayResult.ParseFromString(response)
            if ByteArrayResult is not None:
                byteArray = ByteArrayResult.byteArray
                grd = byteArray_to_griddata(byteArray,grid,level,time,dtime,data_name)
                if show:
                    print("success read from " + filename)
                return grd
        elif status == 416:
            print(filename + "超出可读时间")
            return None
    except Exception as e:
        print(e)
        return None


def read_gridwind_from_gds(ip,port,filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",show = False):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"

    service = GDSDataService(ip, port)
    try:
        if(service is None):
            print("service is None")
            return
        filename = filename.replace("mdfs:///", "")
        filename = filename.replace("\\","/")
        directory,fileName = os.path.split(filename)
        status, response =  service.getData(directory, fileName)
        ByteArrayResult = DataBlock_pb2.ByteArrayResult()
        if status == 200:
            ByteArrayResult.ParseFromString(response)
            if ByteArrayResult is not None:
                byteArray = ByteArrayResult.byteArray
                grd = byteArray_to_gridwind(byteArray,grid,level,time,dtime,data_name)
                if show:
                    print("success read from " + filename)
                return grd
    except Exception as e:
        print(e)
        return None


def byteArray_to_griddata(byteArray,grid = None,level = None,time = None,dtime = None,data_name = "data0"):
    #discriminator = struct.unpack("4s", byteArray[:4])[0].decode("gb2312")
    data_type = np.frombuffer(byteArray[4:6], dtype="i2")[0]

    #mName = struct.unpack("20s", byteArray[6:26])[0].decode("gb2312")
    #eleName = struct.unpack("50s", byteArray[26:76])[0].decode("gb2312")
    #description = struct.unpack("30s", byteArray[76:106])[0].decode("gb2312")
    level1, y, m, d, h, timezone, period = struct.unpack("fiiiiii", byteArray[106:134])
    startLon, endLon, lonInterval, nlon = struct.unpack("fffi", byteArray[134:150])
    startLat, endLat, latInterval, nlat = struct.unpack("fffi", byteArray[150:166])
    #isolineStartValue, isolineEndValue, isolineInterval = struct.unpack("fff", byteArray[166:178])

    nmem = np.frombuffer(byteArray[180:182], dtype="i2")[0]
    #description = mName.rstrip('\x00') + '_' + eleName.rstrip('\x00') + "_" + str(
    #    level) + '(' + description.rstrip('\x00') + ')' + ":" + str(period)
    if data_type == 4:
        data_dtype1 = [('data', 'f4', (nlat, nlon))]
        data_len = nlat * nlon * 4
    elif data_type == 11:
        data_dtype1 = [('data', 'f4', (2, nlat, nlon))]
        data_len = 2 * nlat * nlon * 4


    grd = None
    if (startLat > 90): startLat = 90.0
    if (startLat < -90): startLat = -90.0
    if (endLat > 90): endLat = 90.0
    if (endLat < -90): endLat = -90.0
    lonInterval = (endLon - startLon) / (nlon - 1)
    latInterval = (endLat - startLat) / (nlat - 1)
    if nmem ==0:
        nmem = 1
        if (data_len  == (len(byteArray) - 278) ):
            grid0 = meteva.base.grid([startLon, endLon, lonInterval],
                                                      [startLat, endLat, latInterval])
            grd = meteva.base.grid_data(grid0)
            grd.values = np.frombuffer(byteArray[278:], dtype='float32').reshape(1, 1, 1, 1, grid0.nlat,
                                                                         grid0.nlon)
    else:
        grid0 = meteva.base.grid([startLon, endLon, lonInterval],
                                 [startLat, endLat, latInterval],member_list= np.arange(nmem).tolist())
        grd = meteva.base.grid_data(grid0)
        ind = 0
        for imem in range(nmem):
            #head_info_mem = np.frombuffer(
            #    byteArray[ind:(ind + 278)], dtype=head_dtype)
            ind += 278
            data_mem = np.frombuffer(
                byteArray[ind:(ind + data_len)], dtype=data_dtype1)
            ind += data_len
            #number = head_info_mem['perturbationNumber'][0]
            grd.values[imem,0,0,0, :, :] = np.squeeze(data_mem['data'])


    if grd is not None:
        grd.attrs["dtime_type"] = "hour"
        meteva.base.reset(grd)
        if time is None:
            time = datetime.datetime(y, m, d, h, 0)
        else:
            time = meteva.base.tool.time_tools.all_type_time_to_time64(time)
        if level is None:
            level = level1
        if dtime is None:
            dtime = period

        if nmem==1:
            member_list = [data_name]
        else:
            member_list = np.arange(nmem).tolist()
        meteva.base.set_griddata_coords(grd,gtime=[time],dtime_list=[dtime],level_list=[level],member_list=member_list)

    if (grid is None):
        grd.name = "data0"
        return grd
    else:
        da = meteva.base.interp_gg_linear(grd, grid)
        da.name = "data0"
        return da


def byteArray_to_gridwind(byteArray,grid = None,level = None,time = None,dtime = None,data_name = "data0"):
    #discriminator = struct.unpack("4s", byteArray[:4])[0].decode("gb2312")
    data_type = np.frombuffer(byteArray[4:6], dtype="i2")[0]

    #mName = struct.unpack("20s", byteArray[6:26])[0].decode("gb2312")
    #eleName = struct.unpack("50s", byteArray[26:76])[0].decode("gb2312")
    #description = struct.unpack("30s", byteArray[76:106])[0].decode("gb2312")
    level1, y, m, d, h, timezone, period = struct.unpack("fiiiiii", byteArray[106:134])
    startLon, endLon, lonInterval, nlon = struct.unpack("fffi", byteArray[134:150])
    startLat, endLat, latInterval, nlat = struct.unpack("fffi", byteArray[150:166])
    #isolineStartValue, isolineEndValue, isolineInterval = struct.unpack("fff", byteArray[166:178])

    nmem = np.frombuffer(byteArray[180:182], dtype="i2")[0]
    #description = mName.rstrip('\x00') + '_' + eleName.rstrip('\x00') + "_" + str(
    #    level) + '(' + description.rstrip('\x00') + ')' + ":" + str(period)
    if data_type == 4:
        data_dtype1 = [('data', 'f4', (nlat, nlon))]
        data_len = nlat * nlon * 4
    elif data_type == 11:
        data_dtype1 = [('data', 'f4', (nlat, nlon))]
        data_len = nlat * nlon * 4


    grd = None
    if (startLat > 90): startLat = 90.0
    if (startLat < -90): startLat = -90.0
    if (endLat > 90): endLat = 90.0
    if (endLat < -90): endLat = -90.0
    lonInterval = (endLon - startLon) / (nlon - 1)
    latInterval = (endLat - startLat) / (nlat - 1)
    wind = None
    print(nmem)
    if nmem ==0:
        if (data_len * 2 == (len(byteArray) - 278)):
            grid0 = meteva.base.grid([startLon, endLon, lonInterval], [startLat, endLat, latInterval])
            speed = meteva.base.grid_data(grid0)
            i_s = 278
            i_e = 278 + grid0.nlon * grid0.nlat * 4
            speed.values = np.frombuffer(byteArray[i_s:i_e], dtype='float32').reshape(1, 1, 1, 1, grid0.nlat, grid0.nlon)
            i_s += grid0.nlon * grid0.nlat * 4
            i_e += grid0.nlon * grid0.nlat * 4
            angle = meteva.base.grid_data(grid0)
            angle.values = np.frombuffer(byteArray[i_s:i_e], dtype='float32').reshape(1, 1, 1, 1, grid0.nlat, grid0.nlon)
            meteva.base.reset(speed)
            meteva.base.reset(angle)

            wind = meteva.base.diag.speed_angle_to_wind(speed, angle)

            if time is None:
                time = datetime.datetime(y, m, d, h, 0)
            else:
                time = meteva.base.tool.time_tools.all_type_time_to_time64(time)
            if level is None:
                level = level1
            if dtime is None:
                dtime = period

            meteva.base.set_griddata_coords(wind,gtime=[time],dtime_list=[dtime],level_list=[level],member_list=["u"+data_name,"v"+data_name])
            if (grid is None):
                return wind
            else:
                return meteva.base.diag.interp_gg_linear(wind, grid)
    else:
        member_list = []
        for im in range(nmem):
            member_list.append("u"+str(im))
            member_list.append("v" + str(im))
        grid_en = meteva.base.grid([startLon, endLon, lonInterval], [startLat, endLat, latInterval],member_list= member_list)
        wind_en = meteva.base.grid_data(grid_en)
        for im in range(nmem):
            grid0 = meteva.base.grid([startLon, endLon, lonInterval], [startLat, endLat, latInterval])
            speed = meteva.base.grid_data(grid0)
            i_s = 278 +data_len * im
            i_e = 278 + data_len * (im+1)
            speed.values = np.frombuffer(byteArray[i_s:i_e], dtype="float32").reshape(1, 1, 1, 1, grid0.nlat, grid0.nlon)
            i_s = 278 +data_len * (im+1)
            i_e = 278 + data_len * (im+2)
            angle = meteva.base.grid_data(grid0)
            angle.values = np.frombuffer(byteArray[i_s:i_e], dtype="float32").reshape(1, 1, 1, 1, grid0.nlat, grid0.nlon)
            meteva.base.reset(speed)
            meteva.base.reset(angle)

            wind = meteva.base.diag.speed_angle_to_wind(speed, angle)
            wind_en.values[im*2:im*2+2,0,0,0,:,:] = wind.values[:,0,0,0,:,:]
        if time is None:
            time = datetime.datetime(y, m, d, h, 0)
        else:
            time = meteva.base.tool.time_tools.all_type_time_to_time64(time)
        if level is None:
            level = level1
        if dtime is None:
            dtime = period

        meteva.base.set_griddata_coords(wind, gtime=[time], dtime_list=[dtime], level_list=[level],
                                        member_list=["u" + data_name, "v" + data_name])
        if (grid is None):
            return wind_en
        else:
            return meteva.base.diag.interp_gg_linear(wind_en, grid)


def read_gridwind_from_gds_file(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",show = False):
    try:
        if not os.path.exists(filename):
            print(filename + " is not exist")
            return None
        file = open(filename, 'rb')
        byteArray = file.read()
        wind = byteArray_to_gridwind(byteArray,grid=grid,level = level,time = time,dtime = dtime,data_name = data_name)
        if show:
            print("success read from " + filename)
        return wind
    except Exception as e:
        print(e)
        return None

def read_gridwind_from_micaps2(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",show =False):
    if os.path.exists(filename):
        try:
            column = meteva.base.m2_element_column.风向
            sta_angle = meteva.base.io.read_stadata_from_micaps1_2_8(filename,column,drop_same_id=False)
            column = meteva.base.m2_element_column.风速
            sta_speed = meteva.base.io.read_stadata_from_micaps1_2_8(filename, column,drop_same_id=False)
            grid_angle = meteva.base.trans_sta_to_grd(sta_angle)
            grid_angle.values = 270 - grid_angle.values
            grid_speed = meteva.base.trans_sta_to_grd(sta_speed)
            wind = meteva.base.diag.speed_angle_to_wind(grid_speed,grid_angle)
            meteva.base.reset(wind)
            if grid is None:
                return wind
            else:
                wind1 = meteva.base.interp_gg_linear(wind,grid=grid,level = level,time = time,dtime= dtime,data_name = data_name)
                if show:
                    print("success read from " + filename)
                return wind1
        except (Exception, BaseException) as e:
            exstr = traceback.format_exc()
            print(exstr)
            print(e)
            return None
    else:
        print(filename + " not exists")
        return None

def read_gridwind_from_micaps11(filename,grid = None,level = None,time = None,dtime = None,data_name = "",show = False):
    if os.path.exists(filename):
        encoding,str1 = meteva.base.io.get_encoding_of_file(filename)
        if encoding is None:return
        strs = str1.split()
        dlon = float(strs[8])
        dlat = float(strs[9])
        slon = float(strs[10])
        elon = float(strs[11])
        slat = float(strs[12])
        elat = float(strs[13])
        nlon = float(strs[14])
        nlat = float(strs[15])
        if (nlat - 1) * dlat == (elat - slat) and (nlon - 1) * dlon == (elon - slon):
            k = 16
            grid0 =meteva.base.grid([slon,elon,dlon],[slat,elat,dlat])
        else:
            dlon = float(strs[9])
            dlat = float(strs[10])
            slon = float(strs[11])
            elon = float(strs[12])
            slat = float(strs[13])
            elat = float(strs[14])
            k = 17
            grid0 =meteva.base.grid([slon,elon,dlon],[slat,elat,dlat])
        if (len(strs) - k +1) >= 2 * grid0.nlon * grid0.nlat:
            dat_u= (np.array(strs[k:(k + grid0.nlon * grid0.nlat)])).astype(float).reshape((grid0.nlat,grid0.nlon))
            k += grid0.nlon * grid0.nlat
            dat_v = (np.array(strs[k:(k + grid0.nlon * grid0.nlat)])).astype(float).reshape((grid0.nlat, grid0.nlon))
            grid_u = meteva.base.grid_data(grid0,dat_u)
            grid_v = meteva.base.grid_data(grid0,dat_v)
            wind = meteva.base.diag.u_v_to_wind(grid_u,grid_v)
            meteva.base.reset(wind)
            meteva.base.set_griddata_coords(wind, gtime=[time], dtime_list=[dtime], level_list=[level],
                                            member_list=["u" + data_name, "v" + data_name])
            if grid is None:
                return wind
            else:
                wind1 = meteva.base.interp_gg_linear(wind, grid)
                if show:
                    print("success read from " + filename)
                return wind1
        else:

            print(filename + " 格式错误")
            return None
    else:
        print(filename + " 文件不存在")
        return None


def read_AWX_from_gds(ip,port,filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",show = False):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"

    service = GDSDataService(ip, port)
    try:
        if(service is None):
            print("service is None")
            return
        directory,fileName = os.path.split(filename)
        status, response = byteArrayResult = service.getData(directory, fileName)
        ByteArrayResult = DataBlock_pb2.ByteArrayResult()
        if status == 200:
            ByteArrayResult.ParseFromString(response)
            if ByteArrayResult is not None:
                byteArray = ByteArrayResult.byteArray
                sat96 = struct.unpack("12s", byteArray[:12])[0]
                levl = np.frombuffer(byteArray[12:30], dtype='int16').astype(dtype="int32")
                formatstr = struct.unpack("8s", byteArray[30:38])[0]
                qualityflag = struct.unpack("h", byteArray[38:40])[0]
                satellite = struct.unpack("8s", byteArray[40:48])[0]
                lev2 = np.frombuffer(byteArray[48:104], dtype='int16').astype(dtype="int32")

                recordlen = levl[4]
                headnum = levl[5]
                datanum = levl[6]
                timenum = lev2[0:5]
                nlon = lev2[7]
                nlat = lev2[8]
                range = lev2[12:16].astype("float32")
                slat = range[0] / 100
                elat = range[1] / 100
                slon = range[2] / 100
                elon = range[3] / 100

                # nintels=lev2[20:22].astype("float32")
                dlon = (elon - slon) / (nlon - 1)
                dlat = (elat - slat) / (nlat - 1)

                colorlen = lev2[24]
                caliblen = lev2[25]
                geololen = lev2[26]

                # print(levl)
                # print(lev2)
                head_lenght = headnum * recordlen
                data_lenght = datanum * recordlen
                # print(head_lenght  + data_lenght)
                # print( data_lenght)
                # print(grd.nlon * grd.nlat)
                # headrest = np.frombuffer(byteArray[:head_lenght], dtype='int8')
                data_awx = np.frombuffer(byteArray[head_lenght:(head_lenght + data_lenght)], dtype='int8')

                if colorlen <= 0:
                    calib = np.frombuffer(byteArray[104:(104 + 2048)], dtype='int16').astype(dtype="float32")
                else:
                    # color = np.frombuffer(byteArray[104:(104+colorlen*2)], dtype='int16')
                    calib = np.frombuffer(byteArray[(104 + colorlen * 2):(104 + colorlen * 2 + 2048)],
                                          dtype='int16').astype(
                        dtype="float32")

                realcalib = calib / 100.0
                realcalib[calib < 0] = (calib[calib < 0] + 65536) / 100.0

                awx_index = np.empty(len(data_awx), dtype="int32")
                awx_index[:] = data_awx[:]
                awx_index[data_awx < 0] = data_awx[data_awx < 0] + 256
                awx_index *= 4
                real_data_awx = realcalib[awx_index]
                grid0 = meteva.base.grid([slon, elon, dlon],[slat, elat, dlat])
                grd = meteva.base.grid_data(grid0)
                grd.values = real_data_awx.reshape(1,1,1,1,grid0.nlat, grid0.nlon)
                grd.attrs["dtime_type"] = "hour"
                meteva.base.reset(grd)
                meteva.base.set_griddata_coords(grd,gtime=[time],dtime_list=[dtime],level_list=[level],member_list=[data_name])
                if (grid is None):
                    grd.name = "data0"
                    if show:
                        print("success read from " + filename)
                    return grd
                else:
                    da = meteva.base.interp_gg_linear(grd, grid)
                    da.name = "data0"
                    if show:
                        print("success read from " + filename)
                    return da
    except Exception as e:
        print(e)
        return None


def AWX_byteArray_to_griddata(byteArray,grid = None,level = None,time = None,dtime = None,data_name = "data0"):
    sat96 = struct.unpack("12s", byteArray[:12])[0]
    levl = np.frombuffer(byteArray[12:30], dtype='int16').astype(dtype="int32")
    formatstr = struct.unpack("8s", byteArray[30:38])[0]
    qualityflag = struct.unpack("h", byteArray[38:40])[0]
    satellite = struct.unpack("8s", byteArray[40:48])[0]
    lev2 = np.frombuffer(byteArray[48:104], dtype='int16').astype(dtype="int32")

    recordlen = levl[4]
    headnum = levl[5]
    datanum = levl[6]
    timenum = lev2[0:5]
    nlon = lev2[7]
    nlat = lev2[8]
    range = lev2[12:16].astype("float32")
    slat = range[0] / 100
    elat = range[1] / 100
    slon = range[2] / 100
    elon = range[3] / 100

    # nintels=lev2[20:22].astype("float32")
    dlon = (elon - slon) / (nlon - 1)
    dlat = (elat - slat) / (nlat - 1)

    colorlen = lev2[24]
    caliblen = lev2[25]
    geololen = lev2[26]

    # print(levl)
    # print(lev2)
    head_lenght = headnum * recordlen
    data_lenght = datanum * recordlen
    # print(head_lenght  + data_lenght)
    # print( data_lenght)
    # print(grd.nlon * grd.nlat)
    # headrest = np.frombuffer(byteArray[:head_lenght], dtype='int8')
    data_awx = np.frombuffer(byteArray[head_lenght:(head_lenght + data_lenght)], dtype='int8')

    if colorlen <= 0:
        calib = np.frombuffer(byteArray[104:(104 + 2048)], dtype='int16').astype(dtype="float32")
    else:
        # color = np.frombuffer(byteArray[104:(104+colorlen*2)], dtype='int16')
        calib = np.frombuffer(byteArray[(104 + colorlen * 2):(104 + colorlen * 2 + 2048)],
                              dtype='int16').astype(
            dtype="float32")

    realcalib = calib / 100.0
    realcalib[calib < 0] = (calib[calib < 0] + 65536) / 100.0

    awx_index = np.empty(len(data_awx), dtype="int32")
    awx_index[:] = data_awx[:]
    awx_index[data_awx < 0] = data_awx[data_awx < 0] + 256
    awx_index *= 4
    real_data_awx = realcalib[awx_index]
    grid0 = meteva.base.grid([slon, elon, dlon], [slat, elat, dlat])
    grd = meteva.base.grid_data(grid0)
    grd.values = real_data_awx.reshape(1, 1, 1, 1, grid0.nlat, grid0.nlon)
    grd.attrs["dtime_type"] = "hour"
    meteva.base.reset(grd)
    meteva.base.set_griddata_coords(grd,gtime=[time],dtime_list=[dtime],level_list=[level],member_list=[data_name])
    if (grid is None):
        grd.name = "data0"
        return grd
    else:
        da = meteva.base.interp_gg_linear(grd, grid)
        da.name = "data0"
        return da

def read_griddata_from_AWX_file(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",show = False):
    try:
        if not os.path.exists(filename):
            print(filename + " is not exist")
            return None
        file = open(filename, 'rb')
        byteArray = file.read()
        grd = AWX_byteArray_to_griddata(byteArray,grid,level = level,time = time,dtime = dtime,data_name = data_name)
        if show:
            print("success read from " + filename)
        return grd
    except Exception as e:
        print(e)
        return None

def read_griddata_from_binary(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",show = False):
    try:
        if not os.path.exists(filename):
            print(filename + " is not exist")
            return None
        file = open(filename, 'rb')
        bytes = file.read()
        file.close()
        head = np.frombuffer(bytes[0:24], dtype='float32')
        grid0 = meteva.base.grid([head[0],head[1],head[2]],[head[3],head[4],head[5]])
        dat  = np.frombuffer(bytes[24:], dtype='float32')
        grd = meteva.base.grid_data(grid0,dat)
        if grid is not None:
            grd = meteva.base.interp_gg_linear(grd,grid1=grid)
        meteva.base.set_griddata_coords(grd,gtime=[time],dtime_list=[dtime],level_list=[level],member_list=[data_name])
        if show:
            print("success read from " + filename)
        return grd
    except Exception as e:
        print(e)
        return None
