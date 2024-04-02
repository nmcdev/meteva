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
import bz2
from .CMADaasAccess import CMADaasAccess
from .httpclient import get_http_result_cimiss
import json
import warnings

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


def read_griddata_from_micaps4(filename,grid=None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):
    '''
    读取micaps4格式的格点数据，并将其保存为xarray中DataArray结构的六维数据信息
    :param filename:Micaps4格式的文件路径和文件名
    :param grid:格点的经纬度信息，默认为：None,如果有传入grid信息，需要使用双线性插值进行提取。
    :return:返回一个DataArray结构的六维数据信息da
    '''
    try:
        if not os.path.exists(filename):
            print(filename + " does not exist")
            return None
        encoding,str1 = meteva.base.io.get_encoding_of_file(filename)
        if encoding is None:
            print("文件编码格式不识别")
            return None
        #file = open(filename,'r',encoding=encoding)
        #str1 = file.read()
        #file.close()
        str1 = str1.replace(",","")
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
                try:
                    time = pd.to_datetime(ymd, format = "%Y%m%d%H%M" )
                except:
                    print("m4 文件时间格式错误，因此数据时间被强制设置为2099年1月1日08时，建议在读取时设置参数time")
                    time = datetime.datetime(2099,1,1,8,0)
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
            da.attrs["dtime_units"] = dtime_units
            da.name = "data0"
            meteva.base.reset(da)
            if grid is None:
                if show:
                    print("success read from " + filename)
                return da
            else:
                #如果传入函数有grid信息，就需要进行一次双线性插值，按照grid信息进行提取网格信息。
                da1 = meteva.base.interp_gg_linear(da, grid,outer_value=outer_value)
                if show:
                    print("success read from " + filename)
                return da1
        else:
            print("自描述信息中的网格数是：" +str(nlon1) + "*" + str(nlat1) +"="+ str(nlon1 * nlat1))
            print("实际数据大小为："+str(len(strs) - 22))
            print("m4 文件式错误，文件自描述信息中网格数和实际数据大小不一致")
            return None
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)
        print(filename + "文件格式不能识别。可能原因：文件未按micaps4格式存储")
        return None

#读取nc数据
def read_griddata_from_nc(filename,grid = None,
            value_name = None,member_dim = None,level_dim = None,time_dim = None,dtime_dim = None,lat_dim = None,lon_dim = None,
                         level=None, time=None, dtime=None, data_name="data0",dtime_units = "hour",outer_value = None,show = False):

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

        try:
            #如果文件中包含多层次多时效数据，通过先选择部分时效、层次，提升效率
            dict_sel = {}
            if level is not None:
                if level_dim is not None:
                    if ds0[level_dim].values.size>1:
                        dict_sel[level_dim] = level
                else:
                    if "level" in ds0.coords:
                        if ds0["level"].values.size > 1:
                            dict_sel["level"] = level
            if dtime is not None:
                if dtime_dim is not None:
                    if ds0[dtime_dim].values.size > 1:
                        dict_sel[dtime_dim] = dtime
                else:
                    if "dtime" in ds0.coords:
                        if ds0["dtime"].values.size > 1:
                            dict_sel["dtime"] = dtime
            if len(dict_sel.keys())>0 and value_name is not None:
                ds0 = ds0[value_name]
                ds0 = ds0.loc[dict_sel]
        except:
            #如果不能提取
            pass

        da1 = meteva.base.xarray_to_griddata(ds0,value_name=value_name,member_dim=member_dim,level_dim=level_dim,time_dim=time_dim,dtime_dim=dtime_dim,
                                             lat_dim=lat_dim,lon_dim=lon_dim)

        #如果有level参数
        if level is not None:
            level_list = []
            if isinstance(level, list):
                level_list = level
            elif isinstance(level, np.ndarray):
                level_list = level.tolist()
            else:
                level_list =[level]

            #如果level参数和数据文件里面正好都是一层，就认为level是用来设置层次参数的
            if len(da1.coords["level"])==1 and len(level_list)==1:
                meteva.base.set_griddata_coords(da1,level_list=level_list)
            else:
                #如果level参数和数据文件不都为1层，则认为level是用来提取某些层次数据的
                da1 = meteva.base.in_level_list(da1,level_list=level_list)

        #如果有dtime参数
        if dtime is not None:
            dtime_list = []
            if isinstance(dtime, list):
                dtime_list = dtime
            elif isinstance(dtime, np.ndarray):
                dtime_list = dtime.tolist()
            else:
                dtime_list =[dtime]

            #如果level参数和数据文件里面正好都是一个时效，就认为dtime是用来设置时效参数的
            if len(da1.coords["dtime"])==1 and len(dtime_list)==1:
                meteva.base.set_griddata_coords(da1,dtime_list=dtime_list)
            else:
                #如果level参数和数据文件不都为1时效，则认为level是用来提取某些时效数据的
                da1 = meteva.base.in_dtime_list(da1,dtime_list=dtime_list)


        meteva.base.reset(da1)
        if time is not None and len(da1.coords["time"])==1:
            meteva.base.set_griddata_coords(da1,gtime=[time])
        if data_name is not None and len(da1.coords["member"])==1:
            meteva.base.set_griddata_coords(da1,member_list=[data_name])

        da1.attrs["dtime_units"] = dtime_units
        if grid is None:
            #da1.name = "data0"
            if show:
                print("success read from " + filename)
            return da1
        else:
            # 如果传入函数有grid信息，就需要进行一次双线性插值，按照grid信息进行提取网格信息。
            da2 = meteva.base.interp_gg_linear(da1, grid,outer_value=outer_value)
            #da2.name = "data0"
            if show:
                print("success read from " + filename)
            return da2
    except (Exception, BaseException) as e:
        exstr = traceback.format_exc()
        print(exstr)
        print(e)
        return None


def print_grib_file_info_old1(filename):
    try:
        ds1 = xr.open_dataset(filename, engine="cfgrib", backend_kwargs={"indexpath": ""})
        print(filename + "中只有一种leve_type，\n请根据以下数据内容信息，确认其中的level维度名称")
        print(ds1)
        ds1.close()
    except:
        exstr = traceback.format_exc()
        strs = exstr.split("\n")
        for str1 in strs:
            if str1.find("filter_by_keys=") >= 0:
                filter_by_keys = {}
                str1s = str1.split("=")
                str1s = str1s[1].replace("{","").replace("}","").replace("'","").replace(" ","").split(",")
                for str2 in str1s:
                    key,value = str2.split(":")
                    filter_by_keys[key] = value
                    print(filter_by_keys)
                    try:
                        ds2 = xr.open_dataset(filename, engine="cfgrib",
                                        backend_kwargs={'filter_by_keys': filter_by_keys, "indexpath": ""})
                        print(ds2)
                    except:
                        print("errorr****")
                        exstr2 = traceback.format_exc()
                        strs = exstr2.split("\n")
                        # print(strs)



def print_grib_file_info_old(filename,level_type = None,level = None,filter_by_keys = {}):
    warnings.filterwarnings("ignore")
    try:
        if level_type is None and len(filter_by_keys.keys()) ==0:
            try:
                ds1 = xr.open_dataset(filename, engine="cfgrib", backend_kwargs={"indexpath": ""})
                print(filename + "中只有一种leve_type，\n请根据以下数据内容信息，确认其中的level维度名称")
                print(ds1)
                ds1.close()
            except:
                exstr = traceback.format_exc()
                strs = exstr.split("\n")
                print("请增加如下参数种的一种：")
                para_list = ""
                level_types = []
                for str1 in strs:
                    if str1.find("filter_by_keys=") >= 0:
                        para_list += str1
                        para_list += "\n"
                #         str2 = str1.split("={")[1].replace("}", "")
                #         str3 = str2.split(":")[1].strip()
                #         level_types.append(str3)
                # if len(level_types)>0:
                #     print(filename + "中包含的levelType有：")
                #     for str3 in level_types:
                #         print(str3)
                #     print("从上述文件读取数据前，需从上述选项中指定具体level_type值,其中：")
                # else:
                #     print(exstr)
                print(para_list +"后重试")
        else:
            #filter_by_keys = {}
            print(filter_by_keys)
            if level_type is not None:
                filter_by_keys['typeOfLevel'] = level_type.strip()

            if level is not None:
                filter_by_keys['level'] = level
            ds0 = xr.open_dataset(filename, engine="cfgrib", backend_kwargs={'filter_by_keys': filter_by_keys,"indexpath": ""})
            print(ds0)
            ds0.close()
    except :
        exstr = traceback.format_exc()
        strs = exstr.split("\n")
        print(exstr)
        # import pygrib
        # grbs = pygrib.open(filename)
        # for grb in grbs:
        #     print(str(grb))


def read_griddata_from_grib(filename,level_type= None,grid = None,
            value_name = None,member_dim = None,time_dim = None,dtime_dim = None,lat_dim = None,lon_dim = None,
                         level=None, time=None, dtime=None, data_name="data0",filter_by_keys = {},dtime_units = "hour",outer_value = None,show = False):
    try:

        if level_type is not None:filter_by_keys['typeOfLevel'] = level_type
        if "typeOfLevel" in filter_by_keys.keys(): level_type = filter_by_keys['typeOfLevel']
        ds0 = xr.open_dataset(filename, engine="cfgrib", backend_kwargs={'filter_by_keys': filter_by_keys,"indexpath": ""},)
        try:
            #如果文件中包含多层次多时效数据，通过先选择部分时效、层次，提升效率
            dict_sel = {}
            if level is not None:
                if level_type is not None:
                    if ds0[level_type].values.size>1:
                        dict_sel[level_type] = level
                else:
                    if "level" in ds0.coords:
                        if ds0["level"].values.size > 1:
                            dict_sel["level"] = level
            if dtime is not None:
                if dtime_dim is not None:
                    if ds0[dtime_dim].values.size > 1:
                        dict_sel[dtime_dim] = dtime
                else:
                    if "dtime" in ds0.coords:
                        if ds0["dtime"].values.size > 1:
                            dict_sel["dtime"] = dtime
            if len(dict_sel.keys())>0 and value_name is not None:
                ds0 = ds0[value_name]
                ds0 = ds0.loc[dict_sel]
        except:
            #如果不能提取
            pass


        da1 = meteva.base.xarray_to_griddata(ds0,value_name=value_name,member_dim=member_dim,level_dim=level_type,time_dim=time_dim,dtime_dim=dtime_dim,
                                             lat_dim=lat_dim,lon_dim=lon_dim)
        ds0.close()
        meteva.base.reset(da1)

        # 如果有level参数
        if level is not None:
            level_list = []
            if isinstance(level, list):
                level_list = level
            elif isinstance(level, np.ndarray):
                level_list = level.tolist()
            else:
                level_list = [level]

            # 如果level参数和数据文件里面正好都是一层，就认为level是用来设置层次参数的
            if len(da1.coords["level"]) == 1 and len(level_list) == 1:
                meteva.base.set_griddata_coords(da1, level_list=level_list)
            else:
                # 如果level参数和数据文件不都为1层，则认为level是用来提取某些层次数据的
                da1 = meteva.base.in_level_list(da1, level_list=level_list)

        # 如果有dtime参数
        if dtime is not None:
            dtime_list = []
            if isinstance(dtime, list):
                dtime_list = dtime
            elif isinstance(dtime, np.ndarray):
                dtime_list = dtime.tolist()
            else:
                dtime_list = [dtime]

            # 如果level参数和数据文件里面正好都是一个时效，就认为dtime是用来设置时效参数的
            if len(da1.coords["dtime"]) == 1 and len(dtime_list) == 1:
                meteva.base.set_griddata_coords(da1, dtime_list=dtime_list)
            else:
                # 如果level参数和数据文件不都为1时效，则认为level是用来提取某些时效数据的
                da1 = meteva.base.in_dtime_list(da1, dtime_list=dtime_list)

        if time is not None and len(da1.coords["time"])==1:
            meteva.base.set_griddata_coords(da1,gtime=[time])
        if data_name is not None and len(da1.coords["member"])==1:
            meteva.base.set_griddata_coords(da1,member_list=[data_name])

        da1.attrs["dtime_units"] = dtime_units
        if grid is None:
            #da1.name = "data0"
            if show:
                print("success read from " + filename)
            return da1
        else:
            # 如果传入函数有grid信息，就需要进行一次双线性插值，按照grid信息进行提取网格信息。
            da2 = meteva.base.interp_gg_linear(da1, grid,outer_value=outer_value)
            #da2.name = "data0"
            if show:
                print("success read from " + filename)
            return da2
    except (Exception, BaseException) as e:
        exstr = traceback.format_exc()
        print(exstr)
        print(e)
        return None


def read_griddata_from_gds_file(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):
    try:
        if not os.path.exists(filename):
            print(filename + " does not exist")
            return None
        file = open(filename, 'rb')
        byteArray = file.read()
        grd = decode_griddata_from_gds_byteArray(byteArray,grid,level,time,dtime,data_name)
        if show:
            print("success read from " + filename)
        grd.attrs["dtime_units"] = dtime_units
        return grd
    except Exception as e:
        print(e)
        return None



def read_griddata_from_gds(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"
    if meteva.base.gds_ip_port is None:
        print("请先使用set_config 配置gds的ip和port")
        return
    ip, port = meteva.base.gds_ip_port
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

                grd = decode_griddata_from_gds_byteArray(byteArray,grid,level,time,dtime,data_name)
                if show:
                    print("success read from " + filename)
                grd.attrs["dtime_units"] = dtime_units
                return grd
            else:
                print(filename + " not exist")
                return None
        else:
            print("连接服务的状态异常，不能读取相应的文件,可能原因相应的文件不在允许读取的时段范围")
            return None
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)

        print(filename + "数据读取错误")
        return None


def read_gridwind_from_gds(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"
    if meteva.base.gds_ip_port is None:
        print("请先使用set_config 配置gds的ip和port")
        return
    ip, port = meteva.base.gds_ip_port
    service = GDSDataService(ip,port)
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
                grd = decode_gridwind_from_gds_byteArray(byteArray,grid,level,time,dtime,data_name)
                if show:
                    print("success read from " + filename)
                grd.attrs["dtime_units"] = dtime_units
                return grd
            else:
                print(filename + " not exist")
                return None
        else:
            print("连接服务的状态异常，不能读取相应的文件,可能原因相应的文件不在允许读取的时段范围")
            return None
    except :
        if show:
            exstr = traceback.format_exc()
            print(exstr)

        print(filename + "数据读取错误")
        return None


def decode_griddata_from_gds_byteArray(byteArray,grid = None,level = None,time = None,dtime = None,data_name = "data0",outer_value = None):
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
        da = meteva.base.interp_gg_linear(grd, grid,outer_value=outer_value)
        da.name = "data0"
        return da


def decode_gridwind_from_gds_byteArray(byteArray,grid = None,level = None,time = None,dtime = None,data_name = "data0",outer_value = None):
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
    data_len =0
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
                return meteva.base.interp_gg_linear(wind, grid,outer_value=outer_value)
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
            return meteva.base.interp_gg_linear(wind_en, grid,outer_value=outer_value)


def read_gridwind_from_gds_file(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):
    try:
        if not os.path.exists(filename):
            print(filename + " does not exist")
            return None
        file = open(filename, 'rb')
        byteArray = file.read()
        wind = decode_gridwind_from_gds_byteArray(byteArray,grid=grid,level = level,time = time,dtime = dtime,data_name = data_name)
        if show:
            print("success read from " + filename)
        return wind
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)

        print(filename + "数据读取错误")
        return None

def read_gridwind_from_micaps2(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show =False):
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
                wind1 = meteva.base.interp_gg_linear(wind,grid=grid,level = level,time = time,dtime= dtime,data_name = data_name,outer_value=outer_value)
                if show:
                    print("success read from " + filename)
                wind1.attrs["dtime_units"] = dtime_units
                return wind1
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)

            print(filename + "文件读取错误，可能原因，文件不符合micaps2格式规范")
            return None
    else:
        print(filename + " not exists")
        return None

def read_gridwind_from_micaps11(filename,grid = None,level = None,time = None,dtime = None,data_name = "",dtime_units = "hour",outer_value = None,show = False):
    if os.path.exists(filename):
        try:
            encoding,str1 = meteva.base.io.get_encoding_of_file(filename)
            if encoding is None:
                print("文件编码格式不识别")
                return None
            strs = str1.split()
            dlon = float(strs[8])
            dlat = float(strs[9])
            slon = float(strs[10])
            elon = float(strs[11])
            slat = float(strs[12])
            elat = float(strs[13])
            nlon = float(strs[14])
            nlat = float(strs[15])
            delta_lon = abs((nlat - 1) * dlat - (elat - slat))
            delta_lat = abs((nlon - 1) * dlon - (elon - slon))
            if delta_lon <1e-5 and delta_lat<1e-5:
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
                    wind1 = meteva.base.interp_gg_linear(wind, grid,outer_value=outer_value)
                    if show:
                        print("success read from " + filename)
                    wind1.attrs["dtime_units"] = dtime_units
                    return wind1
            else:

                print(filename + " 格式错误")
                return None
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)

            print(filename + "文件读取错误，可能原因，文件不符合micaps11格式规范")
            return None
    else:
        print(filename + " 文件不存在")
        return None


def read_AWX_from_gds(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"
    if meteva.base.gds_ip_port is None:
        print("请先使用set_config 配置gds的ip和port")
        return
    ip, port = meteva.base.gds_ip_port
    service = GDSDataService(ip, port)
    try:
        filename = filename.replace("mdfs:///", "")
        filename = filename.replace("\\","/")
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
                meteva.base.reset(grd)
                meteva.base.set_griddata_coords(grd,gtime=[time],dtime_list=[dtime],level_list=[level],member_list=[data_name])
                grd.attrs["dtime_units"] = dtime_units
                if (grid is None):
                    grd.name = "data0"
                    if show:
                        print("success read from " + filename)
                    return grd
                else:
                    da = meteva.base.interp_gg_linear(grd, grid,outer_value=outer_value)
                    da.name = "data0"
                    if show:
                        print("success read from " + filename)
                    return da
            else:
                print(filename + " not exist")
                return None
        else:
            print("连接服务的状态异常，不能读取相应的文件,可能原因相应的文件不在允许读取的时段范围")
            return None
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)

        print(filename + "数据读取失败")
        return None


def decode_griddata_from_AWX_byteArray(byteArray,grid = None,level = None,time = None,dtime = None,data_name = "data0",outer_value = None):
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
    meteva.base.reset(grd)
    meteva.base.set_griddata_coords(grd,gtime=[time],dtime_list=[dtime],level_list=[level],member_list=[data_name])
    if (grid is None):
        grd.name = "data0"
        return grd
    else:
        da = meteva.base.interp_gg_linear(grd, grid,outer_value=outer_value)
        da.name = "data0"
        return da

def read_griddata_from_AWX_file(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):
    try:
        if not os.path.exists(filename):
            print(filename + " does not exist")
            return None
        file = open(filename, 'rb')
        byteArray = file.read()
        grd = decode_griddata_from_AWX_byteArray(byteArray,grid,level = level,time = time,dtime = dtime,data_name = data_name)
        grd.attrs["dtime_units"] = dtime_units
        if show:
            print("success read from " + filename)
        return grd
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)

        print(filename + "数据读取失败")
        return None

def read_griddata_from_binary(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):
    try:
        if not os.path.exists(filename):
            print(filename + " does not exist")
            return None
        file = open(filename, 'rb')
        bytes = file.read()
        file.close()
        head = np.frombuffer(bytes[0:24], dtype='float32')
        grid0 = meteva.base.grid([head[0],head[1],head[2]],[head[3],head[4],head[5]])
        dat  = np.frombuffer(bytes[24:], dtype='float32')
        grd = meteva.base.grid_data(grid0,dat)
        if grid is not None:
            grd = meteva.base.interp_gg_linear(grd,grid1=grid,outer_value=outer_value)
        meteva.base.set_griddata_coords(grd,gtime=[time],dtime_list=[dtime],level_list=[level],member_list=[data_name])
        grd.attrs["dtime_units"] = dtime_units
        if show:
            print("success read from " + filename)
        return grd
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)

        print(filename + "数据读取失败")
        return None





def decode_griddata_from_radar_byteArray(byteArray,grid = None,level = None,time = None,dtime = None,data_name = "data0",outer_value = None):
    CODE1 = 'B'
    CODE2 = 'H'
    INT1 = 'B'
    INT2 = 'H'
    INT4 = 'I'
    REAL4 = 'f'
    REAL8 = 'd'
    SINT1 = 'b'
    SINT2 = 'h'
    SINT4 = 'i'
    PT_HEADER = (
        ('DataName', '128s'),  # 产品名称描述
        ('VarName', '32s'),  # 数据类名，见表一
        ('UnitName', '16s'),  # 数据单位名称
        ('DataLabel', INT2),  # 经纬网格数据标识，固定值19532
        ('UnitLen', SINT2),  # 数据单元字节数，固定值2
        ('Slat', REAL4),  # 数据区的南纬（度）
        ('Wlon', REAL4),  # 数据区的西经（度）
        ('Nlat', REAL4),  # 数据区的北纬（度）
        ('Elon', REAL4),  # 数据区的东经（度）
        ('Clat', REAL4),  # 数据区中心纬度（度）
        ('Clon', REAL4),  # 数据区中心经度（度）
        ('rows', SINT4),  # 数据区的行数
        ('cols', SINT4),  # 每行数据的列数
        ('dlat', REAL4),  # 纬向分辨率（度）
        ('dlon', REAL4),  # 经向分辨率（度）
        ('nodata', REAL4),  # 无数据区的编码值
        ('levelbytes', SINT4),  # 单层数据字节数
        ('levelnum', SINT2),  # 数据层个数
        ('amp', SINT2),  # 数值放大系数
        ('compmode', SINT2),  # 数据压缩存储时为1，否则为0
        ('dates', INT2),  # 数据观测时间，为1970年1月1日以来的天数。
        ('seconds', INT4),  # 数据观测时间的秒数
        ('min_value', SINT2),  # 放大后的数据最小取值
        ('max_value', SINT2),  # 放大后的数据最大取值
        ('Reserved', '12s')  # 保留字节
    )
    #f = bz2.BZ2File(path)
    #buf = f.read()
    #f.close()

    if len(byteArray) < 256:
        return None

    pos = 0

    size = struct.calcsize('<' + ''.join([i[1] for i in PT_HEADER]))
    fmt = '<' + ''.join([i[1] for i in PT_HEADER])  # little-endian
    lst = struct.unpack(fmt, byteArray[pos:pos + size])
    spthead = dict(zip([i[0] for i in PT_HEADER], lst))

    #spthead = _unpack_from_buf(buf, pos, PT_HEADER)
    pos += struct.calcsize('<' + ''.join([i[1] for i in PT_HEADER]))
    datbuf = np.frombuffer(byteArray[pos:pos + spthead['levelbytes']], dtype='h')

    nlon = spthead["cols"] #列数
    nlat = spthead["rows"] #行数

    #数据中网格参数
    slat = spthead['Nlat'] # 西北角所在点的lat
    slon = spthead['Wlon'] # 西北角所在点的lon
    dlat = -spthead['dlat'] # lat 间距，从北向南所以取负
    dlon = spthead['dlon'] # lon 间距

    #设置数据的网格范围
    elat = slat + (nlat-1) * dlat
    elon = slon + (nlon-1) * dlon
    grid_data = meteva.base.grid([slon,elon,dlon],[slat,elat,dlat])
    dat = np.zeros((nlat,nlon))

    sflag = 0
    max_sflag = len(datbuf) -2
    while sflag <max_sflag :
        sy = datbuf[sflag + 0]
        sx = datbuf[sflag + 1]
        ns = datbuf[sflag + 2]
        dat[sy,sx:sx+ns] = datbuf[sflag+3 : sflag +3 +ns]
        sflag += ns +3
    dat[dat < -319] = 0
    dat[dat > 1000] = 0
    dat /= 10
    grd = meteva.base.grid_data(grid_data,dat)
    meteva.base.reset(grd)
    meteva.base.set_griddata_coords(grd,gtime=[time],dtime_list=[dtime],level_list=[level],member_list=[data_name])
    if (grid is None):
        grd.name = "data0"
        return grd
    else:
        da = meteva.base.interp_gg_linear(grd, grid,outer_value=outer_value)
        da.name = "data0"
        return da

def read_griddata_from_radar_latlon_file(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):
    try:
        if not os.path.exists(filename):
            print(filename + " does not exist")
            return None
        file = open(filename, 'rb')
        byteArray = file.read()
        grd = decode_griddata_from_radar_byteArray(byteArray,grid,level = level,time = time,dtime = dtime,data_name = data_name)
        grd.attrs["dtime_units"] = dtime_units
        if show:
            print("success read from " + filename)
        return grd
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)

        print(filename + "数据读取失败")
        return None

def read_griddata_from_bz2_file(filename,decode_method,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):

    if not os.path.exists(filename):
        print(filename + " not exist")
        return None
    try:
        f = bz2.BZ2File(filename)
        buf = f.read()
        f.close()
        grd = decode_method(buf,grid = grid,level = level,time = time,dtime = dtime,data_name = data_name)
        grd.attrs["dtime_units"] = dtime_units
        if show:
            print("successed read griddata from "+ filename)
        return grd
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)

        print(filename + "数据读取失败")
        return None



def read_radar_latlon_from_gds(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"
    if meteva.base.gds_ip_port is None:
        print("请先使用set_config 配置gds的ip和port")
        return
    ip, port = meteva.base.gds_ip_port
    service = GDSDataService(ip, port)
    try:
        filename = filename.replace("mdfs:///", "")
        filename = filename.replace("\\","/")

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
                grd = decode_griddata_from_radar_byteArray(byteArray,grid = grid,level = level,time = time,dtime = dtime,data_name = data_name)
                grd.attrs["dtime_units"] = dtime_units
                return grd
            else:
                print(filename + " not exist")
                return None
        else:
            print("连接服务的状态异常，不能读取相应的文件,可能原因相应的文件不在允许读取的时段范围")
            return None
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)
        print(filename + "数据读取失败")
        return None



def read_griddata_from_rasterData(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",outer_value = None,show = False):
    if not os.path.exists(filename):
        print(filename + " not exists")
        return
    try:
        #filename = r"H:\resource\地形数据\rastert_as_dem_1.txt"
        encoding, str1 = meteva.base.io.get_encoding_of_file(filename)
        strs = str1.split()
        nlon1 = int(strs[1])
        nlat1 = int(strs[3])
        slon = float(strs[5])
        slat = float(strs[7])
        dlon = float(strs[9])
        dlat = dlon
        #print(dlat)
        defalut = float(strs[11])
        dat = (np.array(strs[12:])).astype(float).reshape((1, 1, 1, 1, nlat1, nlon1))
        dat[dat == defalut] = meteva.base.IV
        elon = slon + (nlon1-1)*dlon
        elat = slat + (nlat1-1)*dlat
        grid0 = meteva.base.grid([slon,elon,dlon],[elat,slat,-dlat])
        grd = meteva.base.grid_data(grid0,dat)
        meteva.base.reset(grd)
        meteva.base.set_griddata_coords(grd, gtime=[time], dtime_list=[dtime], level_list=[level],
                                        member_list=[data_name])
        grd.attrs["dtime_units"] = dtime_units
        if (grid is None):
            grd.name = "data0"
            return grd
        else:
            da = meteva.base.interp_gg_linear(grd, grid,outer_value=outer_value)
            da.name = "data0"
            return da
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)
        print(filename + "数据读取失败")
        return None

def read_griddata_from_cmadaas(dataCode,element,level_type,level,time,dtime = None,grid = None,data_name= None,dtime_units = "hour",outer_value = None,show = False):

    if dataCode.find("SURF") >=0:
        qparams = { 'interfaceId':'getSurfEleGridByTime'
                    ,'dataCode':dataCode
                    ,'fcstEle':element
                    }
    else:
        if dtime is None:
            qparams = { 'interfaceId':'getNafpAnaEleGridByTimeAndLevel'
                        ,'dataCode':dataCode
                        ,'fcstEle':element
                        ,'levelType':str(level_type)
                        ,'fcstLevel':str(level)
                        }
        else:
            qparams = { 'interfaceId':'getNafpEleGridByTimeAndLevelAndValidtime'
                        ,'dataCode':dataCode
                        ,'fcstEle':element
                        ,'levelType':str(level_type)
                        ,'fcstLevel':str(level)
                        ,'validTime': dtime
                        }


    #print(qparams)
    time = meteva.base.all_type_time_to_datetime(time)

    url = CMADaasAccess.combine_url_from_para(qparams,time=time, time_name='time',show_url = show)
    grd = None
    try:
        if dtime is None:
            grd = CMADaasAccess.read_griddata_from_cmadaas(url, time=time)
        else:
            grd = CMADaasAccess.read_griddata_from_cmadaas(url, time=time, dtime=int(qparams['validTime']))
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)

    if grd is not None:
        meteva.base.reset(grd)
        meteva.base.set_griddata_coords(grd,level_list=[level])
        if data_name is None:
            meteva.base.set_griddata_coords(grd,member_list=[element])
        else:
             meteva.base.set_griddata_coords(grd,member_list=[data_name])
        grd.name = element
        if grid is not None:
            grd = meteva.base.interp_gg_linear(grd, grid,outer_value=outer_value)
    grd.attrs["dtime_units"] = dtime_units
    return grd


def read_griddata_from_cimiss(dataCode,element,level,time,dtime,grid = None,data_name=None,dtime_units = "hour",outer_value = None, show = False):

    time1 = meteva.base.all_type_time_to_datetime(time)
    time_str = time1.strftime("%Y%m%d%H%M%S")
    if dtime is None:
        interface_id ="getNafpAnaEleGridByTimeAndLevel"
        params = {'dataCode': dataCode,
                  'time': time_str,
                  'fcstLevel': str(level),
                  'fcstEle': element}
    else:
        interface_id = "getNafpEleGridByTimeAndLevelAndValidtime"
        params = {'dataCode': dataCode,
                  'time': time_str,
                  'fcstLevel': str(level),
                  'validTime': str(dtime),
                  'fcstEle': element}
    contents = get_http_result_cimiss(interface_id, params,show_url=show)
    if contents is None:
        return None
    contents = json.loads(contents.decode('utf-8'))
    if contents['returnCode'] != '0':
        return None

    slat = float(contents['startLat'])
    slon = float(contents['startLon'])
    nlon = int(contents['lonCount'])
    nlat = int(contents['latCount'])
    dlon = float(contents['lonStep'])
    dlat = float(contents['latStep'])
    elon = slon + (nlon-1)*dlon
    elat = slat + (nlat-1)*dlat
    if data_name is None:
        data_name = dataCode
    grid1 = meteva.base.grid([slon,elon,dlon],[slat,elat,dlat],gtime=[time1],dtime_list=[dtime],level_list=[level],member_list=[data_name])
    data = np.array(contents['DS'], dtype=np.float32)
    grd = meteva.base.grid_data(grid1,data)
    meteva.base.reset(grd)
    grd.name = element
    if grid is not None:
        grd = meteva.base.interp_gg_linear(grd, grid,outer_value=outer_value)
    grd.attrs["dtime_units"] = dtime_units
    return grd


def decode_griddata_from_radar_mosaic_v3_byteArray(byteArray, grid=None, level=None, time=None, dtime=None,
                                             data_name="data0",outer_value = None):
    if time is None:
        ts = np.frombuffer(byteArray[100:112], dtype='short')
        time = datetime.datetime(ts[0], ts[1], ts[2], ts[3], ts[4])
        timezone = np.frombuffer(byteArray[96:100], dtype='int32')[0]
        if timezone == 0:
            time = time + datetime.timedelta(hours=8)

    if dtime is None:
        dtime = 0
    if level is None:
        level = 0

    g = np.frombuffer(byteArray[124:164], dtype='int32')
    slon = g[1] / 1000
    slat = g[0] / 1000
    dlon = g[9] / 10000
    dlat = g[8] / 10000
    elon = slon + dlon * (g[6] - 1)
    elat = slat + dlat * (g[7] - 1)
    grid0 = meteva.base.grid([slon, elon, dlon], [elat, slat, -dlat])
    compress = np.frombuffer(byteArray[166:168], dtype='int16')[0]
    if compress == 1:
        blockpos = np.frombuffer(byteArray[88:92], dtype='int32')[0]
        scale = np.frombuffer(byteArray[176:178], dtype='short')[0] + 0.0
        data_bytes = bz2.decompress(byteArray[blockpos:])
        data = np.frombuffer(data_bytes, dtype='short')

        index = np.where(data < 0)
        data = data / scale
        data[index] = np.nan
        grd = meteva.base.grid_data(grid0, data)
        meteva.base.reset(grd)
        meteva.base.set_griddata_coords(grd, gtime=[time], dtime_list=[dtime], level_list=[level])
        if grid is not None:
            grd = meteva.base.interp_gg_linear(grd, grid,outer_value=outer_value)
        meteva.base.set_griddata_coords(grd, member_list=[data_name])
        return grd
    else:
        return None


def read_griddata_from_radar_mosaic_v3_file(filename, grid=None, level=None, time=None, dtime=None, data_name="data0",dtime_units = "hour",outer_value = None,
                                      show=False):
    try:
        if not os.path.exists(filename):
            print(filename + " does not exist")
            return None
        file = open(filename, 'rb')
        byteArray = file.read()
        grd = decode_griddata_from_radar_mosaic_v3_byteArray(byteArray, grid, level=level, time=time, dtime=dtime,
                                                       data_name=data_name)
        grd.attrs["dtime_units"] = dtime_units
        if show:
            print("success read from " + filename)
        return grd
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)
        print(filename + "数据读取失败")
        return None

def read_griddata_from_radar_mosaic_v3_gds(filename, grid=None, level=None, time=None, dtime=None, data_name="data0",dtime_units = "hour",outer_value = None,
                                      show=False):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"
    if meteva.base.gds_ip_port is None:
        print("请先使用set_config 配置gds的ip和port")
        return
    ip, port = meteva.base.gds_ip_port
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

                grd = decode_griddata_from_radar_mosaic_v3_byteArray(byteArray,grid,level,time,dtime,data_name)
                grd.attrs["dtime_units"] = dtime_units
                if show:
                    print("success read from " + filename)
                return grd
            else:
                print(filename + " not exist")
                return None
        else:
            print("连接服务的状态异常，不能读取相应的文件,可能原因相应的文件不在允许读取的时段范围")
            return None
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)

        print(filename + "数据读取错误")
        return None


def read_griddata_from_ctl(ctl_path,data_path = None,value_name = None,dtime_dim = None,dtime_start = 0,time = None,level = None, grid = None,endian = "<",
                           data_name=None,dtime_units = "hour",outer_value = None,
                           show=False
                           ):

    try:
        ctl = meteva.base.read_ctl(ctl_path)
        #print(ctl)
        #print(ctl["pdef"])
        #print(ctl_path)
        if data_path is None:
            data_path = ctl["data_path"]
        value_index =0
        if value_name is None:
            if len(ctl["vars"]) != 1:
                print("请指定要读取的要素名称 value_name")
                return None
        else:
            for i in range(len(ctl["vars"])):
                if ctl["vars"][i]["name"] == value_name:
                    value_index = i
                    break

        file_size = os.path.getsize(data_path)
        total_level_count = 0
        nvar = len(ctl["vars"])
        for nv in range(nvar):
            total_level_count += ctl["vars"][nv]["nlevel"]


        file = open(data_path, "rb")

        if "pdef" in ctl.keys():
            if grid is None:
                lons = ctl["xdef"]
                lons.sort()
                lats = ctl["ydef"]
                lats.sort()
                grid_xy = meteva.base.grid([lons[0],lons[-1],lons[1] - lons[0]],[lats[0],lats[-1],lats[1] - lats[0]])
            else:
                grid_xy = grid

            nx = ctl["pdef"]["nx"]
            ny = ctl["pdef"]["ny"]
            blocksize_xy =  nx * ny * 4  #+ 8   #+8是否因为数据有问题
            block_count = int(file_size/blocksize_xy)  #获得总的平面场个数
            nt = ctl["ntime"]

            dt_str = ctl["gtime"][2]
            if dt_str.find("m") >= 0:
                dt_str = dt_str.replace("m", "min")
            index_time_dict = {}
            times_all = pd.date_range(ctl["gtime"][0], ctl["gtime"][1], freq=dt_str)
            nt_return = nt

            grd_list = []
            index_time_list = np.arange(nt).tolist()
            if time is not None:
                #判断所选时间所在的索引
                if nt >1:
                    for index1 in range(nt):
                        time_str = meteva.base.tool.time_tools.all_type_time_to_str(times_all[index1])
                        index_time_dict[time_str] = index1
                    time1 = meteva.base.tool.time_tools.all_type_time_to_str(time)
                    if time1 not in index_time_dict.keys():
                        print("time取值不在tdef的列表内")
                    index_time_list= [index_time_dict[time1]]
                times_all = [time]

            nlevel =  ctl["vars"][value_index]["nlevel"]
            index_level = np.arange(nlevel)
            levels_all =ctl["zdef"]

            if level is not None:
                if nlevel >1:
                    index_level_dict = {}
                    for index1 in range(nlevel):
                        level1 = ctl["zdef"][index1]
                        index_level_dict[level1] = index1
                    if level not in index_level_dict.keys():
                        print("level取值不在zdef的列表内")
                    index_level= [index_level_dict[level]]
                levels_all = [level]
            else:
                if nlevel ==1:
                    levels_all = [levels_all[0]]

            blocksize_xyz = blocksize_xy * nlevel
            for nt1 in range(len(index_time_list)):
                index1 = index_time_list[nt1]
                time1 = times_all[nt1]
                block_pass = index1 * total_level_count + ctl["vars"][value_index]["start_bolck_index"]
                start_index = block_pass * blocksize_xy
                position = file.seek(start_index)
                content = file.read(blocksize_xyz)
                data = np.frombuffer(content, dtype='>f')
                # data = data[1:-1]  #数据是否有问题？
                data = data.reshape((nlevel,ny, nx))

                for nn in range(len(levels_all)):
                    index2 = index_level[nn]
                    grid1 = meteva.base.grid(grid_xy.glon,grid_xy.glat,gtime =[time1],level_list=[levels_all[index2]])
                    grd1 = meteva.base.tool.math_tools.ctl_proj(grid1, ctl["pdef"], data[index2,:,:])
                    grd_list.append(grd1)

            file.close()
            grd = meteva.base.concat(grd_list)
            if data_name is not None:
                meteva.base.set_griddata_coords(grd, member_list=[data_name])
            if dtime_start != 0:
                grd = meteva.base.move_fo_time(grd, -dtime_start)
            return grd

        else:
            grid0 = meteva.base.grid(ctl["glon"],ctl["glat"])
            blocksize_xy = grid0.nlon * grid0.nlat * 4

            data_list = []
            blocksize_one_time = ctl["cumulate_levels"] *blocksize_xy
            nlevel = ctl["vars"][value_index]["nlevel"]
            for nn in range(ctl["nensemble"]):
                for t in range(ctl["ntime"]):
                    start_index =blocksize_one_time *ctl["ntime"] * nn +  t * blocksize_one_time + ctl["vars"][value_index][
                        "start_bolck_index"] * blocksize_xy
                    position = file.seek(start_index)
                    blocksize_one_value = blocksize_xy * nlevel
                    content = file.read(blocksize_one_value)
                    data1 = np.frombuffer(content, dtype=endian + "f")
                    data_list.append(data1)

            data = np.array(data_list)
            data = data.reshape(ctl["nensemble"], ctl["ntime"], nlevel, ctl["nlat"], ctl["nlon"])
            data = data.transpose(0,2,1,3,4)
            if nlevel != len(ctl["zdef"]):
                level_list = np.arange(ctl["vars"][value_index]["nlevel"])
            else:
                level_list =ctl["zdef"]

            if dtime_dim is None:
                grid1 = meteva.base.grid(ctl["glon"],ctl["glat"],gtime=ctl["gtime"],dtime_list=[0],level_list=level_list,member_list=ctl["edef"])
            else:

                grid1 = meteva.base.grid(ctl["glon"], ctl["glat"], gtime=[ctl["gtime"][0]], dtime_list=ctl["dtime_list"] ,
                                         level_list=level_list, member_list=ctl["edef"])

            #print(grid1)
            grd_one_var = meteva.base.grid_data(grid1,data)
            if grid is not None:
                grd_one_var = meteva.base.interp_gg_linear(grd_one_var,grid=grid,outer_value=outer_value)
            if data_name is not None:
                meteva.base.set_griddata_coords(grd_one_var, member_list=[data_name])
            file.close()
            grd_one_var.attrs["dtime_units"] = dtime_units
            if dtime_start != 0:
                grd_one_var = meteva.base.move_fo_time(grd_one_var, -dtime_start)
            return grd_one_var
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)

        print(ctl_path + "数据读取错误")
        return None


def decode_griddata_from_swan_d131_byteArray(byteArray,grid = None,level = None,time = None,dtime = 0,data_name = "data0",scale_type=0,outer_value = None):
    head_dtype_raw = [
        ('ZonName', 'S12'),
        ('DataName', 'S38'),
        ('Flag', 'S8'),
        ('Version', 'S8'),
        ('year', 'i2'),
        ('month', 'i2'),
        ('day', 'i2'),
        ('hour', 'i2'),
        ('minute', 'i2'),
        ('interval', 'i2'),
        ('XNumGrids', 'i2'),
        ('YNumGrids', 'i2'),
        ('ZNumGrids', 'i2'),
        ('RadarCount', 'i4'),
        ('StartLon', 'f4'),
        ('StartLat', 'f4'),
        ('CenterLon', 'f4'),
        ('CenterLat', 'f4'),
        ('XReso', 'f4'),
        ('YReso', 'f4'),
        ('ZhighGrids', 'f4', 40),
        ('RadarStationName', 'S20', 16),
        ('RadarLongitude', 'f4', 20),
        ('RadarLatitude', 'f4', 20),
        ('RadarAltitude', 'f4', 20),
        ('MosaicFlag', 'S1', 20),
        ('m_iDataType', 'i2'),
        ('m_iLevelDimension', 'i2')]

    head_suffix_01 = [('Reserved', 'S168')]  # v1.0
    head_suffix_02 = [('offset', 'f4'),
                      ('scale', 'f4'),
                      ('Reserved', 'S160')]  # v2.0
    head_dtype = head_dtype_raw + head_suffix_02
    # print(head_dtype)
    # read head information
    head_info = np.frombuffer(byteArray[0:1024], dtype=head_dtype)
    ind = 1024
    # get coordinates
    version = head_info['Version'][0].astype(np.float)
    nlon = head_info['XNumGrids'][0].astype(np.int64)
    nlat = head_info['YNumGrids'][0].astype(np.int64)
    nlev = head_info['ZNumGrids'][0].astype(np.int64)
    dlon = head_info['XReso'][0].astype(np.float)
    dlat = head_info['YReso'][0].astype(np.float)
    slon = head_info['StartLon'][0]
    slat = head_info['StartLat'][0]
    clat = head_info['CenterLat'][0]
    if slat>clat and dlat>0:
        slat = clat*2 - slat
    elon = slon + (nlon - 1) * dlon
    elat = slat + (nlat - 1) * dlat

    if level is None:
        levels = head_info['ZhighGrids'][0][0:nlev]
    else:
        levels = [level]
    data_type = ['u1', 'u1', 'u2', 'i2']
    ih = head_info['m_iDataType'][0]
    if ih ==4:ih =3
    data_type = data_type[ih]
    data_len = (nlon * nlat * nlev)
    data = np.frombuffer(
        byteArray[ind:(ind + data_len * int(data_type[1]))],
        dtype=data_type, count=data_len)
    # convert data type
    data.shape = (nlev, nlat, nlon)
    data = data.astype(np.float32)
    # scale
    if scale_type == 0:  # qpe等
        scale = [0.1, 0]
    elif scale_type == 1:  # 雷达等
        scale = [0.5, -33]
    if version >= 2.:
        scale[1] = head_info['offset'][0]
        scale[0] = head_info['scale'][0]
    # print('SWAN Version:', version)
    # print('scale:', scale)
    data = data * scale[0] + scale[1]
    data = np.flip(data, 1) # reverse latitude axis
    if time is None:
        init_time = datetime.datetime(
            head_info['year'][0], head_info['month'][0],
            head_info['day'][0], head_info['hour'][0], head_info['minute'][0])
    else:
        init_time = time
    grid_file = meteva.base.grid([slon,elon,dlon],[slat,elat,dlat],gtime=[init_time],dtime_list=[dtime],level_list=levels,member_list=[data_name])
    grd = meteva.base.grid_data(grid_file,data)
    meteva.base.reset(grd)
    if grid is not None:
        grd  = meteva.base.interp_gg_linear(grd,grid,outer_value=outer_value)
    if data_name is not None:
        grd.attrs['short_name'] = data_name
        grd.attrs['units'] = 'mm'
    grd.attrs['Conventions'] = "CF-1.6"
    grd.attrs['Origin'] = 'MICAPS Cassandra Server'
    return grd


def read_griddata_from_swan_d131(filename,grid = None,level = None,time = None,dtime = None,data_name = "data0",dtime_units = "hour",show = False,scale_type = 0,outer_value = None):
    try:
        if not os.path.exists(filename):
            print(filename + " does not exist")
            return None
        file = open(filename, 'rb')
        if dtime is None:
            dtime = 0
            try:
                dtime = int(int(filename.split('.')[1]) / 60.0)
            except:
                pass
        byteArray = file.read()
        if filename[-4:].lower() == ".bz2":
            byteArray = bz2.decompress(byteArray)

        grd = decode_griddata_from_swan_d131_byteArray(byteArray, grid, level=level, time=time, dtime=dtime,
                                                   data_name=data_name,scale_type=scale_type)
        if show:
            print("success read from " + filename)
        grd.attrs["dtime_units"] = dtime_units
        return grd
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)

        print(filename + "数据读取失败")
        return None



def jd2ce(JDN):
    import math
    ## 儒略时间（julia_date）转为datetime.
    JDN = JDN + 0.5
    Z = int(JDN)
    F = JDN - Z
    if Z < 2299161:  # 儒略历
        A = Z
    else:  # 格里历
        a = int((Z - 2305447.5) / 36524.25)
        A = Z + 10 + a - int(a / 4)
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)
    day = B - D - int(30.6001 * E) + F
    if E < 14:
        month = E - 1
    elif E < 16:
        month = E - 13
    if month > 2:
        year = C - 4716
    elif month in [1, 2]:
        year = C - 4715
    day = round(day, 4)
    hour = (day - math.floor(day)) * 24
    minute = (hour - math.floor(hour)) * 60
    ## 结果输出
    day = math.floor(day)
    hour = math.floor(hour)
    minute = math.floor(minute)
    date = datetime.datetime(year, month, day, hour, minute)
    print("儒略日{}对应的公历日期为{}年{}月{}日{}时{}分".format(JDN - 0.5, year, month, day, hour, minute), '\n')
    return (date)

def read_griddata_from_ensemble_sav(filename, dt=None, unit='mm', var=None,dtime_units = "hour",outer_value = None):  ## 可改为使用meb.grid类
    """
    从集合团队IDL的sav数据中，读取meteva类型的xarray格点数据，并返回
    dt: 预报数据起报时间，datetime.datetime类型
    var: 如果多变量sav， 需要指定该参数， 解码具体单变量
    unit: 预报量单位，默认为mm
    """
    import scipy.io
    if not os.path.exists(filename):
        print("Grads file not EXISTs")
        return ()

    sav = scipy.io.readsav(filename)
    ## 读取各维度数据信息
    if dt is None:
        dim_time = [jd2ce(sav['datastruct']['inittime'][0])]
    else:
        dim_time = [dt]
    data = np.squeeze(np.array(sav['datastruct']['DATA'][0]))
    dim_lon = np.array(sav['datastruct']['LON'][0], dtype=np.float64)
    dim_lat = np.array(sav['datastruct']['LAT'][0], dtype=np.float64)
    dim_ens = [fn.decode('utf-8') for fn in sav['datastruct']['memname'][0]]  # 前缀为‘b’为btyes类型。用decode转为str类型
    dim_dtime = np.array(sav['datastruct']['fhour'][0], dtype=np.int32)
    dim_level = np.array(sav['datastruct']['lev'][0], dtype=np.float64)
    nens = len(dim_ens)
    ntime = len(dim_time)
    ndtime = len(dim_dtime)
    nlevel = len(dim_level)
    nlon = len(dim_lon)
    nlat = len(dim_lat)
    if var is not None:
        dim_var = [fn.decode('utf-8') for fn in np.squeeze(np.array(sav['datastruct']['varname'])).tolist().tolist()]
        try:
            index = dim_var.index(var)
            data = data[:, :, index, :, :]
        except Exception as err:
            print(err)
            return None
            ## 转为meteva的xarray格式
    data.shape = nens, ndtime, ntime, nlevel, nlat, nlon
    grd_ens = xr.DataArray(data
                           , coords=[dim_ens, dim_dtime, dim_time, dim_level, dim_lat, dim_lon]
                           , dims=['member', 'dtime', 'time', 'level', 'lat', 'lon'])
    grd_ens.attrs["units"] = unit
    grd_ens.name = 'data0'
    grd_ens1 = grd_ens.transpose('member', 'level', 'time', 'dtime', 'lat', 'lon')
    grd_ens1.attrs["dtime_units"] = dtime_units
    return grd_ens1


def read_griddata_from_swan_d131_gds(filename, grid=None, level=None, time=None, dtime=None, data_name="data0",dtime_units = "hour",
                                     show=False, scale_type=0,outer_value = None):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"
    if meteva.base.gds_ip_port is None:
        print("请先使用set_config 配置gds的ip和port")
        return
    ip, port = meteva.base.gds_ip_port
    service = GDSDataService(ip, port)
    try:
        filename = filename.replace("mdfs:///", "")
        filename = filename.replace("\\", "/")

        if (service is None):
            print("service is None")
            return
        directory, fileName = os.path.split(filename)
        status, response = byteArrayResult = service.getData(directory, fileName)
        ByteArrayResult = DataBlock_pb2.ByteArrayResult()
        if status == 200:
            ByteArrayResult.ParseFromString(response)
            if ByteArrayResult is not None:
                byteArray = ByteArrayResult.byteArray

                if fileName[-4:].lower() == ".bz2":
                    byteArray = bz2.decompress(byteArray)

                grd = decode_griddata_from_swan_d131_byteArray(byteArray, grid, level=level, time=time, dtime=dtime,
                                                               data_name=data_name, scale_type=scale_type)
                grd.attrs["dtime_units"] = dtime_units
                return grd
            else:
                print(filename + " not exist")
                return None
        else:
            print("连接服务的状态异常，不能读取相应的文件,可能原因相应的文件不在允许读取的时段范围")
            return None
    except:
        if show:
            exstr = traceback.format_exc()
            print(exstr)
        print(filename + "数据读取失败")
        return None


