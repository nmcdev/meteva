#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import numpy as np
import os
import pandas as pd
import nmc_verification
import traceback
import re
import copy
from . import DataBlock_pb2
from .GDS_data_service import GDSDataService
import struct
from collections import OrderedDict
import datetime
import math

def read_station(filename):
    '''
    :param filename: 站点文件路径，它可以是micaps第1、2、3、8类文件
    :return: 站点数据，其中time,dtime,level属性为设置的缺省值，数据内容都设置为0
    '''
    sta = None
    if os.path.exists(filename):
        file = open(filename,'r')
        head = file.readline()
        strs = head.split()

        if strs[1] == "3":
            sta = read_stadata_from_micaps3(filename)
        elif strs[1] == "16":
            sta = read_stadata_from_micaps16(filename)
        elif strs[1] == "1" or str[1] == "2" or str[1] == "8":
            sta = read_stadata_from_micaps1_2_8(filename,column=4)
        else:
            print(filename + "is not micaps第1、2、3、8类文件")
    else:
        print(filename + " not exist")
    if sta is not None:
        data_name = sta.columns[-1]
        sta[data_name] = 0
        nmc_verification.nmc_vf_base.set_stadata_coords(sta,time = datetime.datetime(2099,1,1,8,0),level = 0,dtime= 0)
        return sta

def read_stadata_from_micaps3(filename, station=None,  level=None,time=None, dtime=None, data_name='data0', drop_same_id=True):
    '''
    读取micaps3格式文件转换为pandas中dataframe结构的数据

    :param reserve_time_dtime_level:保留时间，时效和层次，默认为rue
    :param data_name:dataframe中数值的values列的名称
    :return:返回一个dataframe结构的多列站点数据。
    :param filename: 文件路径
    :param station: 站号，默认：None
    :param time: 起报时  默认：NOne
    :param dtime: 时效 默认：None
    :param level:  层次  默认：None
    :param data_name: 要素名  默认：'data0'
    :param drop_same_id: 是否要删除相同id的行  默认为True
    :return:
    '''
    try:
        if os.path.exists(filename):
            file = open(filename, 'r')
            skip_num = 0
            strs = []
            nline = 0
            nregion = 0
            nstart = 0
            while 1 > 0:
                skip_num += 1
                str1 = file.readline()
                strs.extend(str1.split())

                if (len(strs) > 8):
                    nline = int(strs[8])
                if (len(strs) > 11 + nline):
                    nregion = int(strs[11 + nline])
                    nstart = nline + 2 * nregion + 14
                    if (len(strs) == nstart):
                        break
            file.close()

            file_sta = open(filename)

            sta1 = pd.read_csv(file_sta, skiprows=skip_num, sep="\s+", header=None, usecols=[0, 1, 2, 4])
            sta1.columns = ['id', 'lon', 'lat', data_name]
            sta1.drop_duplicates(keep='first', inplace=True)
            if drop_same_id:
                sta1 = sta1.drop_duplicates(['id'])
            # sta = bd.sta_data(sta1)
            sta = nmc_verification.nmc_vf_base.basicdata.sta_data(sta1)
            # print(sta)

            y2 = ""
            if len(strs[3]) == 2:
                year = int(strs[3])
                if year >= 50:
                    y2 = '19'
                else:
                    y2 = '20'
            if len(strs[3]) == 1: strs[3] = "0" + strs[3]
            if len(strs[4]) == 1: strs[4] = "0" + strs[4]
            if len(strs[5]) == 1: strs[5] = "0" + strs[5]
            if len(strs[6]) == 1: strs[6] = "0" + strs[6]

            time_str = y2 + strs[3] + strs[4] + strs[5] + strs[6]
            time_file = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(time_str)
            sta.loc[:,"time"] = time_file
            sta.loc[:,"dtime"] = 0
            sta.loc[:,"level"] = 0 #int(strs[7])
            nmc_verification.nmc_vf_base.set_stadata_coords(sta, level=level, time=time, dtime=dtime)

            if (station is not None):
                sta = nmc_verification.nmc_vf_base.put_stadata_on_station(sta, station)
            return sta
        else:
            return None
    except:
        exstr = traceback.format_exc()
        print(exstr)
        return None

def read_stadata_from_txt(filename, columns , skiprows=0, drop_same_id=True):

    """
    读取站点数据
    :param filename:带有站点信息的路径已经文件名
    :param columns 列名
    :param skiprows:读取时跳过的行数，默认为：0
    :param drop_same_id: 是否要删除相同id的行  默认为True
    :return:返回带有'level','time','dtime','id','lon','lat','alt','data0'列的dataframe站点信息。
    """
    if os.path.exists(filename):
        try:
            file_sta = open(filename, 'r')
            sta0 = pd.read_csv(file_sta, skiprows=skiprows, sep="\s+", header=None)
        except:
            try:
                file_sta = open(filename, 'r', encoding="UTF-8")
                sta0 = pd.read_csv(file_sta, skiprows=skiprows, sep="\s+", header=None)
            except:
                exstr = traceback.format_exc()
                print(exstr)
                return None
        sta0.columns = columns
        station_column = ['id', 'lon', 'lat', 'alt']
        colums1 = []
        for name in station_column:
            if name in columns:
                colums1.append(name)
        sta1 = sta0[colums1]
        nsta = len(sta1.index)
        for i in range(nsta):
            if sta1.loc[i, 'lon'] > 1000:
                a = sta1.loc[i, 'lon'] // 100 + (a % 100) / 60
                sta1.loc[i, 'lon'] = a
            if sta1.loc[i, 'lat'] > 1000:
                a = sta1.loc[i, 'lat'] // 100 + (a % 100) / 60
                sta1.loc[i, 'lat'] = a
        # sta = bd.sta_data(sta1)
        sta = nmc_verification.nmc_vf_base.basicdata.sta_data(sta1)
        if drop_same_id:
            sta = sta.drop_duplicates(['id'])

        # sta['time'] = method.time_tools.str_to_time64("2099010108")
        sta.loc[:,'time'] = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time64("2099010108")
        sta.loc[:,'level'] = 0
        sta.loc[:,'dtime'] = 0
        # sta.coloumns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt', 'data0']
        sta.loc[:,'data0'] = 0
        nmc_verification.nmc_vf_base.basicdata.reset_id(sta)
        return sta
    else:
        print(filename + " not exist")
        return None


def read_stadata_from_sevp(filename0, element_id,level=None,time=None,data_name = "data0"):
    '''
    兼容多个时次的预报产品文件 txt格式
    :param：filename:文件路径和名称
    :param: element:选取要素
    :param drop_same_id: 是否要删除相同id的行  默认为True
    :return：dataframe格式的站点数据

    '''
    filename = filename0
    try:
        if os.path.exists(filename):
            try:
                file = open(filename, 'r')
                skip_num = 6
                line1 = file.readline()
                line2 = file.readline()
                line3 = file.readline()
                line4 = file.readline()
                line5 = file.readline()
                line6 = file.readline()
                file.close()
            except:
                try:
                    file = open(filename, 'r', encoding="UTF-8")
                    skip_num = 6
                    line1 = file.readline()
                    line2 = file.readline()
                    line3 = file.readline()
                    line4 = file.readline()
                    line5 = file.readline()
                    line6 = file.readline()
                    file.close()
                except:
                    exstr = traceback.format_exc()
                    print(exstr)
                    return None
            try:
                file_sta = open(filename)
                sta1 = pd.read_csv(file_sta, skiprows=skip_num, sep="\s+", header=None)
                file.close()
            except:
                try:
                    file_sta = open(filename, 'r', encoding="UTF-8")
                    sta1 = pd.read_csv(file_sta, skiprows=skip_num, sep="\s+", header=None)
                    file.close()
                except:
                    exstr = traceback.format_exc()
                    print(exstr)
                    return None
            num_list = re.findall(r"\d+", line3)
            strs4 = line4.split()
            time_file = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(strs4[1])
            line6_list = re.findall(r'[0-9.]+', line6)
            nline0 = int(line6_list[5])
            sta_all = sta1.iloc[0:nline0,[0,element_id]]
            sta_all.loc[:,"id"] = int(line6_list[0])
            sta_all.loc[:,"lon"] = float(line6_list[1])
            sta_all.loc[:,"lat"] = float(line6_list[2])
            #print(sta_all)
            dat_station = sta1.values[nline0,0:5]
            nline_all = len(sta1.index)
            while True:
                nline1 = nline0 + int(dat_station[-1])+1
                sta_one = sta1.iloc[nline0+1:nline1,[0,element_id]]
                sta_one.loc[:,"id"] = int(dat_station[0])
                sta_one.loc[:,"lon"] = int(dat_station[1])
                sta_one.loc[:,"lat"] = int(dat_station[2])
                sta_all = pd.concat([sta_all, sta_one])

                if nline1 >= nline_all - 1:break
                nline0 = nline1
                dat_station = sta1.values[nline0,0:5]

            sta_all.loc[:,"time"] = time_file
            #print(sta_all)
            sta_all.columns = ["dtime","data0","id","lon","lat","time"]
            sta_all.loc[:,"level"] = 0
            sta = nmc_verification.nmc_vf_base.sta_data(sta_all)
            nmc_verification.nmc_vf_base.set_stadata_coords(sta, level=level, time=time)
            nmc_verification.nmc_vf_base.set_stadata_names(sta, data_name_list=[data_name])

            return sta
        else:
            print("不存在此文件！")
    except:
        exstr = traceback.format_exc()
        print(exstr)

def read_stadata_from_micaps1_2_8(filename, column, station=None, level=None,time=None, dtime=None, data_name='data0', drop_same_id=True):
    '''
    read_from_micaps1_2_8  读取m1、m2、m8格式的文件
    :param filename: 文件路径
    :param column: 选取哪列要素  4-len
    :param station: 站号 默认为None
    :param drop_same_id: 是否要删除相同id的行  默认为True
    :return:
    '''
    if os.path.exists(filename):
        sta1 = pd.read_csv(filename, skiprows=2, sep="\s+", header=None, usecols=[0, 1, 2,  column])
        # print(sta1)
        sta1.columns = ['id', 'lon', 'lat', 'data0']
        sta2 = nmc_verification.nmc_vf_base.basicdata.sta_data(sta1)

        if drop_same_id:
            sta2 = sta2.drop_duplicates(['id'])


        file = open(filename,'r')
        head = file.readline()
        head1 = file.readline()
        file.close()
        strs0 = head.split()
        strs = head1.split()

        y2 = ""
        if len(strs[0]) == 2:
            year = int(strs[0])
            if year >= 50:
                y2 = '19'
            else:
                y2 = '20'
        if len(strs[0]) == 1: strs[0] = "0" + strs[0]
        if len(strs[1]) == 1: strs[1] = "0" + strs[1]
        if len(strs[2]) == 1: strs[2] = "0" + strs[2]
        if len(strs[3]) == 1: strs[3] = "0" + strs[3]

        time_str = y2 + strs[0] + strs[1] + strs[2] + strs[3]
        time_file = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(time_str)
        if time is None:
            sta2.loc[:,'time'] = time_file
        else:
            sta2.loc[:,'time'] = time
        #print(strs0)
        if strs0[1] == "1":
            sta2.loc[:,"level"] = 0
            sta2.loc[:,"dtime"] = 0
        elif strs0[1] == "2":
            sta2.loc[:,"level"] = int(strs[4])
            sta2.loc[:,"dtime"] = 0
        elif strs0[1] == "8":
            sta2.loc[:,"level"] = 0
            sta2.loc[:,"dtime"] = int(strs[4])
        else:
            print(filename + "is not micaps第1、2、3、8类文件")

        nmc_verification.nmc_vf_base.set_stadata_coords(sta2,level= level,time = time,dtime= dtime)
        nmc_verification.nmc_vf_base.set_stadata_names(sta2,data_name_list=[data_name])
        if station is None:
            return sta2
        else:
            sta = nmc_verification.nmc_vf_base.put_stadata_on_station(sta2, station)
            return sta
    else:
        return None

def read_gds_ip_port(filename):
    file = open(filename)
    for i in range(6):
        file.readline()
    ip = file.readline().split("=")[1]
    ip = ip.strip()
    port = int(file.readline().split("=")[1])
    file.close()
    return ip,port

def read_stadata_from_gds(ip, port, filename,element_id,station = None, level=None,time=None, dtime=None, data_name='data0'):
    '''
    :param ip: 为字符串形式，示例 “10.20.30.40”
    :param port: 为整数形式 示例 8080
    :param filename0:
    :param element_id0:
    :param station:
    :param data_name:
    :return:
    '''
    directory, filename = os.path.split(filename)
    # connect to data service
    service = GDSDataService(ip, port)

    # get data file name
    element_id_str0 = str(element_id)
    try:
        status, response = service.getData(directory, filename)
    except ValueError:
        print('Can not retrieve data' + filename + ' from ' + directory)
        return None
    ByteArrayResult = DataBlock_pb2.ByteArrayResult()
    if status == 200:
        ByteArrayResult.ParseFromString(response)
        if ByteArrayResult is not None:
            byteArray = ByteArrayResult.byteArray
            # define head structure
            head_dtype = [('discriminator', 'S4'), ('type', 'i2'),
                          ('description', 'S100'),
                          ('level', 'f4'), ('levelDescription', 'S50'),
                          ('year', 'i4'), ('month', 'i4'), ('day', 'i4'),
                          ('hour', 'i4'), ('minute', 'i4'), ('second', 'i4'),
                          ('Timezone', 'i4'), ('extent', 'S100')]

            # read head information
            head_info = np.frombuffer(byteArray[0:288], dtype=head_dtype)
            if time is None:
                time = datetime.datetime(
                    head_info['year'][0], head_info['month'][0],
                    head_info['day'][0], head_info['hour'][0],
                    head_info['minute'][0], head_info['second'][0])
            if level is None:
                level = head_info["level"][0]
            if dtime is None:
                filename1 = os.path.split(filename)[1].split(".")
                dtime = int(filename1[1])
            ind = 288
            # read the number of stations
            station_number = np.frombuffer(
                byteArray[ind:(ind+4)], dtype='i4')[0]
            ind += 4

            # read the number of elements
            element_number = np.frombuffer(
                byteArray[ind:(ind+2)], dtype='i2')[0]

            if element_number == 0:
                return None
            ind += 2

            # construct record structure
            element_type_map = {
                1: 'b1', 2: 'i2', 3: 'i4', 4: 'i8', 5: 'f4', 6: 'f8', 7: 'S1'}
            element_map = {}
            element_map_len = {}
            for i in range(element_number):
                element_id = str(np.frombuffer(byteArray[ind:(ind+2)], dtype='i2')[0])
                ind += 2
                element_type = np.frombuffer(
                    byteArray[ind:(ind+2)], dtype='i2')[0]
                ind += 2
                element_map[element_id] = element_type_map[element_type]
                element_map_len[element_id] = int(element_type_map[element_type][1])




            dtype_str = element_map[element_id_str0]

            # loop every station to retrieve record
            record_head_dtype = [
                ('id', 'i4'), ('lon', 'f4'), ('lat', 'f4'), ('numb', 'i2')]
            records = []
            if station is None or len(station.index) * 100 > station_number:
                for i in range(station_number):
                    record_head = np.frombuffer(
                        byteArray[ind:(ind+14)], dtype=record_head_dtype)
                    ind += 14
                    record = {
                        'id': record_head['id'][0], 'lon': record_head['lon'][0],
                        'lat': record_head['lat'][0]}
                    for j in range(record_head['numb'][0]):    # the record element number is not same, missing value is not included.
                        element_id = str(np.frombuffer(byteArray[ind:(ind + 2)], dtype='i2')[0])
                        ind += 2
                        element_len = element_map_len[element_id]
                        if element_id == element_id_str0:
                            record[data_name] = np.frombuffer(
                                byteArray[ind:(ind + element_len)],
                                dtype=dtype_str)[0]
                            records.append(record)
                        ind += element_len
                records = pd.DataFrame(records)
                records.set_index('id')
                # get time

                records['time'] = time
                records['level'] = level
                records['dtime'] = dtime
                new_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', data_name]
                records = records.reindex(columns=new_columns)
                if station is None:
                    return records
                else:
                    sta = nmc_verification.nmc_vf_base.put_stadata_on_station(records, station)
                    return sta
            else:
                sta = copy.deepcopy(station)
                byte_num = len(byteArray)
                i4_num = (byte_num - ind -4) //4
                ids = np.zeros((i4_num,4),dtype=np.int32)

                ids[:, 0] = np.frombuffer(byteArray[ind:(ind + i4_num * 4)], dtype='i4')
                ids[:, 1] = np.frombuffer(byteArray[(ind +1):(ind + 1 + i4_num * 4)], dtype='i4')
                ids[:, 2] = np.frombuffer(byteArray[(ind + 2):(ind + 2 + i4_num * 4)], dtype='i4')
                ids[:, 3] = np.frombuffer(byteArray[(ind + 3):(ind + 3 + i4_num * 4)], dtype='i4')
                ids = ids.flatten()
                station_ids = station["id"].values
                dat = np.zeros(station_ids.size)

                for k in range(dat.size):
                    id1 = station_ids[k]
                    indexs = np.where(ids == id1)
                    if len(indexs[0]) >=1:
                        for n in range(len(indexs)):
                            ind1 =ind +  indexs[n][0]
                            record_head = np.frombuffer(byteArray[ind1:(ind1 + 14)], dtype=record_head_dtype)
                            if(record_head['lon'][0] >=-180 and record_head['lon'][0] <= 360 and
                                    record_head['lat'][0] >= -90 and record_head['lat'][0] <= 90 and record_head["numb"][0] < 1000):
                                ind1 += 14
                                for j in range(record_head['numb'][0]):  # the record element number is not same, missing value is not included.
                                    element_id = str(np.frombuffer(byteArray[ind1:(ind1 + 2)], dtype='i2')[0])
                                    ind1 += 2
                                    element_len = element_map_len[element_id]
                                    if element_id == element_id_str0:
                                        sta.iloc[k,-1] = np.frombuffer(byteArray[ind1:(ind1 + element_len)],dtype=dtype_str)[0]
                                    ind1 += element_len
                nmc_verification.nmc_vf_base.set_stadata_names(sta,[data_name])
                sta['time'] = time
                sta['level'] = level
                sta['dtime'] = dtime
                return sta
        else:
            return None
    else:
        return None


def read_stadata_from_gds_griddata(ip,port,filename,station):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"

    service = GDSDataService(ip, port)
    try:
        if(service is None):
            print("service is None")
            return
        directory,fileName = os.path.split(filename)
        status, response = service.getData(directory, fileName)
        ByteArrayResult = DataBlock_pb2.ByteArrayResult()
        if status == 200:
            ByteArrayResult.ParseFromString(response)
            if ByteArrayResult is not None:
                byteArray = ByteArrayResult.byteArray
                startLon, endLon, dlon, nlon= struct.unpack("fffi", byteArray[134:150])
                startLat, endLat, dlat, nlat = struct.unpack("fffi", byteArray[150:166])
                nsta = len(station.index)
                ig = ((station['lon'].values - startLon) // dlon).astype(dtype='int32')
                jg = ((station['lat'].values - startLat) // dlat).astype(dtype='int32')
                dx = (station['lon'].values - startLon) / dlon - ig
                dy = (station['lat'].values - startLat) / dlat - jg
                c00 = (1 - dx) * (1 - dy)
                c01 = dx * (1 - dy)
                c10 = (1 - dx) * dy
                c11 = dx * dy
                ig1 = np.minimum(ig + 1, nlon - 1)
                jg1 = np.minimum(jg + 1, nlat - 1)
                i00 = (nlon * jg + ig)
                i01 = nlon * jg+ ig1
                i10 = nlon * jg1 + ig
                i11 = nlon * jg1 + ig1
                dat = np.zeros(nsta)
                #i4 = np.arange(4)
                #xx,yy = np.meshgrid(i4,i00)
                #i00 = xx + yy
                #i00 = i00.flatten()
                for i in range(nsta):
                    dat00 = np.frombuffer(byteArray[278 + i00[i] * 4:i00[i] * 4 + 282], dtype='float32')
                    dat01 = np.frombuffer(byteArray[278 + i01[i] * 4:i01[i] * 4 + 282], dtype='float32')
                    dat10 = np.frombuffer(byteArray[278 + i10[i] * 4:i10[i] * 4 + 282], dtype='float32')
                    dat11 = np.frombuffer(byteArray[278 + i11[i] * 4:i11[i] * 4 + 282], dtype='float32')
                    dat[i] = c00[i] * dat00 + c01[i] * dat01 +c10[i] * dat10 + c11[i] * dat11
                #grd.values = np.frombuffer(byteArray[278:], dtype='float32')
                sta = copy.deepcopy(station)
                sta.iloc[:,-1] = dat[:]
                filename1 = os.path.split(filename)[1].split(".")
                #print(filename1)
                #time1 = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(filename1[0])
                sta.loc[:, "level"] = 0
                #sta.loc[:, "time"] = time1
                sta.loc[:,"time"] = datetime.datetime(2099,1,1,8,0)
                sta.loc[:, "dtime"] = int(filename1[1])
                return sta
    except Exception as e:
        print(e)
        return None


def print_gds_file_values_names(ip,port,filename):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"
    value_id_list= []
    service = GDSDataService(ip, port)
    try:
        directory, fileName = os.path.split(filename)
        status, response = service.getData(directory, fileName)
        ByteArrayResult = DataBlock_pb2.ByteArrayResult()
        if status == 200:
            ByteArrayResult.ParseFromString(response)
            if ByteArrayResult is not None:
                byteArray = ByteArrayResult.byteArray
                nsta = struct.unpack("i", byteArray[288:292])[0]
                id_num = struct.unpack("h", byteArray[292:294])[0]
                id_tpye = {}
                for i in range(id_num):
                    element_id0 = struct.unpack("h", byteArray[294 + i * 4:296 + i * 4])[0]
                    id_tpye[element_id0] = struct.unpack("h", byteArray[296 + i * 4:298 + i * 4])[0]
                station_data_dict = OrderedDict()
                index = 294 + id_num * 4
                type_lenght_dict = {1: 1, 2: 2, 3: 4, 4: 4, 5: 4, 6: 8, 7: 1}
                type_str_dict = {1: 'b', 2: 'h', 3: 'i', 4: 'l', 5: 'f', 6: 'd', 7: 'c'}

                for i in range(nsta):
                    one_station_dat = {}
                    one_station_dat["id"] = str(struct.unpack("i", byteArray[index: index + 4])[0])
                    index += 4
                    one_station_dat['lon'] = struct.unpack("f", byteArray[index: index + 4])[0]
                    index += 4
                    one_station_dat['lat'] = (struct.unpack("f", byteArray[index: index + 4])[0])
                    index += 4
                    value_num = struct.unpack("h", byteArray[index:index + 2])[0]
                    index += 2
                    values = {}
                    for j in range(value_num):
                        id = struct.unpack("h", byteArray[index:index + 2])[0]
                        index += 2
                        id_tpye0 = id_tpye[id]
                        dindex = type_lenght_dict[id_tpye0]
                        type_str = type_str_dict[id_tpye0]
                        index += dindex
                        value_id_list.append(id)
            value_id_set = set(value_id_list)
            id_dict = nmc_verification.nmc_vf_base.gds_element_id_dict
            for value_id in value_id_set:
                for ele in id_dict.keys():
                    if value_id == id_dict[ele]:
                        print(ele)
    except:
        exstr = traceback.format_exc()
        print(exstr)

def read_stadata_from_micaps16(filename):
    if os.path.exists(filename):
        file = open(filename,'r')
        head = file.readline()
        head = file.readline()
        stationids = []
        row1 = []
        row2 = []
        row3 = []
        while(head is not None and head.strip() != ""):
            strs = head.split()
            stationids.append(strs[0])
            a = int(strs[1])
            b = a // 100 + (a % 100) /60
            row1.append(b)
            a = int(strs[2])
            b = a // 100 + (a % 100) /60
            row2.append(b)
            row3.append(float(strs[3]))
            head =  file.readline()

        row1 = np.array(row1)
        row2 = np.array(row2)
        row3 = np.array(row3)
        ids = np.array(stationids)
        dat = np.zeros((len(row1),4))
        dat[:,0] = ids[:]
        if(np.max(row2) > 90 or np.min(row2) <-90):
            dat[:,1] = row2[:]
            dat[:,2] = row1[:]
        else:
            dat[:,1] = row1[:]
            dat[:,2] = row2[:]
        dat[:,3] = row3[:]
        station = pd.DataFrame(dat, columns=['id','lon', 'lat', "data0"])
        station = nmc_verification.nmc_vf_base.sta_data(station)
        return station
    else:
        print(filename +" not exist")
        return None

def read_stadata_from_csv(filename):
    file = open(filename,"r")
    sta = pd.read_csv(file,parse_dates=['time'])
    sta.drop(sta.columns[[0]], axis=1, inplace=True)
    sta.dropna(axis=0, how='any', inplace=True)
    return sta

def read_stadata_from_gds_griddata_file(filename,station):
    if os.path.exists(filename):
        file = open(filename,"rb")
        position = file.seek(134)
        content = file.read(32)
        slon, elon, dlon,nlon,slat,elat,dlat,nlat = struct.unpack("fffifffi", content)
        nsta = len(station.index)
        ig = ((station['lon'].values - slon) // dlon).astype(dtype='int32')
        jg = ((station['lat'].values - slat) // dlat).astype(dtype='int32')
        dx = (station['lon'].values - slon) / dlon - ig
        dy = (station['lat'].values - slat) / dlat - jg
        c00 = (1 - dx) * (1 - dy)
        c01 = dx * (1 - dy)
        c10 = (1 - dx) * dy
        c11 = dx * dy
        ig1 = np.minimum(ig + 1, nlon - 1)
        jg1 = np.minimum(jg + 1, nlat - 1)
        i00 = (nlon * jg + ig)
        i01 = nlon * jg + ig1
        i10 = nlon * jg1 + ig
        i11 = nlon * jg1 + ig1
        dat = np.zeros(nsta)
        for i in range(nsta):
            position = file.seek(i00[i] * 4+278)
            content = file.read(4)
            dat00 = np.frombuffer(content, dtype='float32')
            position = file.seek(i01[i] * 4+278)
            content = file.read(4)
            dat01 = np.frombuffer(content, dtype='float32')
            position = file.seek(i10[i] * 4+278)
            content = file.read(4)
            dat10 = np.frombuffer(content, dtype='float32')
            position = file.seek(i11[i] * 4+278)
            content = file.read(4)
            dat11 = np.frombuffer(content, dtype='float32')
            dat[i] = c00[i] * dat00 + c01[i] * dat01 + c10[i] * dat10 + c11[i] * dat11
        sta = copy.deepcopy(station)
        sta.iloc[:, -1] = dat[:]
        filename1 = os.path.split(filename)[1].split(".")
        sta.loc[:,"time"] = datetime.datetime(2099,1,1,8,0)
        sta.loc[:, "level"] = 0
        sta.loc[:, "dtime"] = int(filename1[1])
        file.close()
        return sta
    else:
        return None
