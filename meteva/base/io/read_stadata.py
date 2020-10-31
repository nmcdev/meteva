#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import numpy as np
import os
import pandas as pd
import meteva
import traceback
import re
import copy
from . import DataBlock_pb2
from .GDS_data_service import GDSDataService
import struct
from collections import OrderedDict
import datetime
import math
from io import StringIO



def read_station(filename,keep_alt = False,show = False):
    '''
    :param filename: 站点文件路径，它可以是micaps第1、2、3、8类文件
    :return: 站点数据，其中time,dtime,level属性为设置的缺省值，数据内容都设置为0
    '''
    if not os.path.exists(filename):
        print(filename+"文件不存在")
        return None
    else:
        encoding,_ = meteva.base.io.get_encoding_of_file(filename,read_rows=1)
        if encoding is None:
            print("文件编码格式不识别")
            return None
        try:
            file = open(filename, encoding=encoding)
            sta = None
            head = file.readline()
            strs = head.split()
            if strs[1] == "3":
                if keep_alt:
                    sta = read_sta_alt_from_micaps3(filename)
                else:
                    sta = read_stadata_from_micaps3(filename)
            elif strs[1] == "16":
                sta = read_stadata_from_micaps16(filename)
            elif strs[1] == "1" or str[1] == "2" or str[1] == "8":
                sta = read_stadata_from_micaps1_2_8(filename,column=3)
            else:
                print(filename + "is not micaps第1、2、3、8类文件")

            if sta is not None:
                data_name = sta.columns[-1]
                if not keep_alt:
                    sta[data_name] = 0
                else:
                    meteva.base.set_stadata_names(sta,["alt"])
                meteva.base.set_stadata_coords(sta,time = datetime.datetime(2099,1,1,8,0),level = 0,dtime= 0)
                if show:
                    print("success read from "+filename)
                return sta
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)

            print(filename + "文件格式不能识别。可能原因：文件未按micaps格式存储")
            return None

def read_sta_alt_from_micaps3(filename, station=None, drop_same_id=True,show = False):
    '''
    读取micaps3格式文件转换为pandas中dataframe结构的数据

    :param reserve_time_dtime_level:保留时间，时效和层次，默认为rue
    :param data_name:dataframe中数值的values列的名称
    :return:返回一个dataframe结构的多列站点数据。
    :param filename: 文件路径
    :param station: 站号，默认：None
    :param drop_same_id: 是否要删除相同id的行  默认为True
    :return:
    '''

    #print(os.path.exists(filename))
    if not os.path.exists(filename):
        print(filename+"文件不存在")
        return None
    else:
        encoding, _ = meteva.base.io.get_encoding_of_file(filename,read_rows=1)
        if encoding is None:
            print("文件编码格式不识别")
            return None

        try:
            file = open(filename, 'r',encoding= encoding)
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

            file_sta = open(filename,'r',encoding= encoding)

            sta1 = pd.read_csv(file_sta, skiprows=skip_num, sep="\s+", header=None, usecols=[0, 1, 2, 3])
            sta1.columns = ['id', 'lon', 'lat', 'alt']
            sta1.drop_duplicates(keep='first', inplace=True)
            if drop_same_id:
                sta1 = sta1.drop_duplicates(['id'])
            # sta = bd.sta_data(sta1)
            sta = meteva.base.basicdata.sta_data(sta1)
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
            time_file = meteva.base.tool.time_tools.str_to_time(time_str)
            sta.loc[:,"time"] = time_file
            sta.loc[:,"dtime"] = 0
            sta.loc[:,"level"] = 0 #int(strs[7])

            if (station is not None):
                sta = meteva.base.put_stadata_on_station(sta, station)
            if show:
                print("success read from " + filename)
            return sta
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)

            print(filename+"文件格式不能识别。可能原因：文件未按micaps3格式存储")
            return None

def read_stadata_from_micaps3(filename, station=None,  level=None,time=None, dtime=None, data_name='data0', drop_same_id=True,show = False):
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
    if not os.path.exists(filename):
        print(filename+"文件不存在")
        return None
    else:
        encoding, _ = meteva.base.io.get_encoding_of_file(filename,read_rows=1)
        if encoding is None:
            print("文件编码格式不识别")
            return None

        try:
            file = open(filename, 'r',encoding=encoding)
            skip_num = 0
            strs = []
            nline = 0
            nregion = 0
            nstart = 0
            while 1 > 0:
                skip_num += 1
                str1 = file.readline()
                #print(str1)
                strs.extend(str1.split())

                if (len(strs) > 8):
                    nline = int(strs[8])
                if (len(strs) > 11 + nline):
                    nregion = int(strs[11 + nline])
                    nstart = nline + 2 * nregion + 14
                    if (len(strs) == nstart):
                        break
            file.close()
            #print(skip_num)
            if int(strs[-1]) == 0:return None

            file_sta = open(filename, 'r',encoding=encoding)
            sta1 = pd.read_csv(file_sta, skiprows=skip_num, sep="\s+", header=None, usecols=[0, 1, 2, 4])
            sta1.columns = ['id', 'lon', 'lat', data_name]
            sta1.drop_duplicates(keep='first', inplace=True)
            if drop_same_id:
                sta1 = sta1.drop_duplicates(['id'])
            # sta = bd.sta_data(sta1)
            sta = meteva.base.basicdata.sta_data(sta1)
            #print(sta)

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
            time_file = meteva.base.tool.time_tools.str_to_time(time_str)
            sta.loc[:,"time"] = time_file
            sta.loc[:,"dtime"] = 0
            sta.loc[:,"level"] = 0 #int(strs[7])
            #print(time_str)
            meteva.base.set_stadata_coords(sta, level=level, time=time, dtime=dtime)

            if (station is not None):
                sta = meteva.base.put_stadata_on_station(sta, station)
            if show:
                print("success read from " + filename)
            return sta

        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)

            print(filename+"文件格式不能识别。可能原因：文件未按micaps3格式存储")
            return None

def read_stadata_from_csv(filename, columns, member_list,skiprows=0,level = None,time = None,dtime = None, drop_same_id=False,show = False,
                          sep = "\s+"):

    """
    读取站点数据
    :param filename:带有站点信息的路径已经文件名
    :param columns 列名
    :param skiprows:读取时跳过的行数，默认为：0
    :param drop_same_id: 是否要删除相同id的行  默认为True
    :return:返回带有'level','time','dtime','id','lon','lat','alt','data0'列的dataframe站点信息。
    """

    if os.path.exists(filename):
        encoding,_ = meteva.base.io.get_encoding_of_file(filename,read_rows=skiprows)
        if encoding is None:
            print("文件编码格式不识别")
            return None
        try:
            file_sta = open(filename, 'r',encoding = encoding)
            if "time" in columns:
                index = columns.index("time")
                sta0 = pd.read_csv(file_sta, skiprows=skiprows,  header=None,sep=sep,parse_dates=[index])
                sta0.columns = columns
            else:
                sta0 = pd.read_csv(file_sta, skiprows=skiprows, header=None, sep=sep)
                sta0.columns = columns

            station_column = []
            for column in columns:
                if column in meteva.base.get_coord_names():
                    station_column.append(column)
            if not isinstance(member_list,list):
                member_list = [member_list]

            sta0.drop_duplicates(keep='first', inplace=True)
            station_column.extend(member_list)
            sta1 = sta0[station_column]
            nsta = len(sta1.index)
            if "lon" in station_column:
                for i in range(nsta):
                    if sta1.loc[i, 'lon'] > 1000:
                        a = sta1.loc[i, 'lon'] // 100 + (a % 100) / 60
                        sta1.loc[i, 'lon'] = a
            if "lat" in station_column:
                for i in range(nsta):
                    if sta1.loc[i, 'lat'] > 1000:
                        a = sta1.loc[i, 'lat'] // 100 + (a % 100) / 60
                        sta1.loc[i, 'lat'] = a
            # sta = bd.sta_data(sta1)
            sta = meteva.base.basicdata.sta_data(sta1)

            if drop_same_id:
                sta = sta.drop_duplicates(['id'])

            # sta['time'] = method.time_tools.str_to_time64("2099010108")
            if time is not None:
                sta.loc[:,"time"] = time
            elif pd.isnull(sta.iloc[0,1]):
                sta.loc[:,'time'] = meteva.base.tool.time_tools.str_to_time64("2099010108")
            if dtime is not None:
                sta.loc[:,"dtime"] = dtime
            elif pd.isnull(sta.iloc[0,2]):
                sta.loc[:,"dtime"] = 0

            if level is not None:
                sta.loc[:,"level"] = level
            elif pd.isnull(sta.iloc[0,0]):
                sta.loc[:,"level"] = 0


            meteva.base.basicdata.reset_id(sta)
            if show:
                print("success read from "+filename)
            return sta
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)
            print(filename+"文件格式不能识别。可能原因：文件未按pandas能够识别的csv格式存储")
            return None
    else:
        print(filename + " not exist")
        return None


def read_stadata_from_sevp(filename, element_id,level=None,time=None,data_name = "data0",show = False):
    '''
    兼容多个时次的预报产品文件 txt格式
    :param：filename:文件路径和名称
    :param: element:选取要素
    :param drop_same_id: 是否要删除相同id的行  默认为True
    :return：dataframe格式的站点数据

    '''

    if not os.path.exists(filename):
        print(filename+"文件不存在")
        return None
    else:
        encoding,lines = meteva.base.io.get_encoding_of_file(filename,read_rows=6)
        if encoding is None:
            print("文件编码格式不识别")
            return None
        try:
            #lines = heads.split("\n")
            file = open(filename,encoding = encoding)
            str_lines = file.readlines()
            if time is None:
                strs4 = lines[3].split()
                time_file = meteva.base.tool.time_tools.str_to_time(strs4[1])
            else:
                time_file = time
            if level is None:
                level = 0

            num_all = len(str_lines) - 1
            str_lines_list = []
            nline = 5
            while nline< num_all:
                str1 = str_lines[nline][:-1] +" "
                strs = str1.split()
                next_num = int(strs[4])
                for i in range(1,next_num+1):
                    e_str = str1 + str_lines[nline+i]
                    str_lines_list.append(e_str)
                nline += next_num+1
            strs_all = "".join(str_lines_list)

            f = StringIO(strs_all)
            df = pd.read_csv(f,header = None,sep="\s+")
            df = df.loc[:,[0,1,2,6,6 + element_id]]
            df.columns = ["id", "lon", "lat", "dtime",data_name]
            df["time"] = time_file
            df["level"] = level
            sta = meteva.base.sta_data(df)
            return sta
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)
            print(filename + " 文件格式异常")


def read_stadata_from_micaps1_2_8(filename, column, station=None, level=None,time=None, dtime=None, data_name='data0', drop_same_id=True,show = False):
    '''
    read_from_micaps1_2_8  读取m1、m2、m8格式的文件
    :param filename: 文件路径
    :param column: 选取哪列要素  4-len
    :param station: 站号 默认为None
    :param drop_same_id: 是否要删除相同id的行  默认为True
    :return:
    '''
    if not os.path.exists(filename):
        print(filename+"文件不存在")
        return None
    else:
        encoding,heads = meteva.base.io.get_encoding_of_file(filename,read_rows=2)
        if encoding is None:
            print("文件编码格式不识别")
            return None

        try:
            file = open(filename,encoding=encoding)
            sta1 = pd.read_csv(file, skiprows=2, sep="\s+", header=None, usecols=[0, 1, 2,  column])
            sta1.columns = ['id', 'lon', 'lat', data_name]
            sta2 = meteva.base.basicdata.sta_data(sta1)
            if drop_same_id:
                sta2 = sta2.drop_duplicates(['id'])
            strs0 = heads[0].split()
            strs = heads[1].split()
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
            time_file = meteva.base.tool.time_tools.str_to_time(time_str)
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

            meteva.base.set_stadata_coords(sta2,level= level,time = time,dtime= dtime)
            if show:
                print("success read from "+filename)
            if station is None:
                return sta2
            else:
                sta = meteva.base.put_stadata_on_station(sta2, station)
                return sta
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)
            print(filename+"文件格式不能识别。可能原因：文件未按micaps第1、2、8类格式存储")
            return None


def read_stadata_from_micaps41_lightning(filename, column, level=0,data_name='data0', show = False,keep_millisecond = False):
    '''
        read_from_micaps41  读取m41格式的文件
        :param filename: 文件路径
        :param column: 选取哪列要素  4-len
        :param station: 站号 默认为None
        :param drop_same_id: 是否要删除相同id的行  默认为True
        :return:
        '''
    if not os.path.exists(filename):
        print(filename + "文件不存在")
        return None
    else:
        encoding, heads = meteva.base.io.get_encoding_of_file(filename, read_rows=2)
        if encoding is None:
            print("文件编码格式不识别")
            return None

        try:
            file = open(filename, encoding=encoding)
            sta1 = pd.read_csv(file, skiprows=2, sep="\s+", header=None, usecols=[0, 1, 4,5,column])
            sta1.columns = ['id','time', 'lon', 'lat', data_name]
            sta1['time'] = pd.to_datetime(sta1['time'],format="%Y%m%d%H%M%S%f")
            if not keep_millisecond:
                sta1['time'] = sta1['time'].dt.ceil("S")
            sta2 = meteva.base.basicdata.sta_data(sta1)

            sta2.loc[:, "level"] = level
            sta2.loc[:, "dtime"] = 0

            if show:
                print("success read from " + filename)
            return sta2

        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)
            print(filename + "文件格式不能识别。可能原因：文件未按micaps第41类格式存储")
            return None


def set_io_config(filename):
    if os.path.exists(filename):
        try:
            ip,port = read_gds_ip_port(filename)
            ips = ip.split(".")
            if len(ips) == 4:
                for i in range(4):
                    digital = int(ips[i])
            else:
                print("filename  内容的格式不符合要求")
            meteva.base.gds_ip_port = ip,port
            print("配置文件设置成功")
        except:
            print("filename  内容的格式不符合要求")
    else:
        print("filename not exist")

def read_gds_ip_port(filename,show = False):
    if filename is None:
        print("请使用set_config_ip_port 函数设置存储ip，port的配置文件的路径")
    file = open(filename)
    for i in range(100):
        title = file.readline()
        if title.find("MICAPS") >=0:
            break
    ip = file.readline().split("=")[1]
    ip = ip.strip()
    port = int(file.readline().split("=")[1])
    file.close()
    if show:
        print("success read from " + filename)
    return ip,port

def read_stadata_from_gds(filename,element_id = None,station = None, level=None,time=None, dtime=None, data_name='data0',show = False):
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
    if meteva.base.gds_ip_port is None:
        print("请先使用set_config 配置gds的ip和port")
        return
    ip,port = meteva.base.gds_ip_port
    service = GDSDataService(ip, port)

    # get data file name
    element_id0 = element_id
    if element_id is not None:
        element_id_str0 = str(element_id)

    try:
        directory = directory.replace("mdfs:///", "")
        directory = directory.replace("\\","/")
        status, response = service.getData(directory, filename)
    except ValueError:
        print('Can not retrieve data' + filename + ' from ' + directory)
        return None
    try:
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
                #print(head_info)
                if time is None:
                    time = datetime.datetime(
                        head_info['year'][0], head_info['month'][0],
                        head_info['day'][0], head_info['hour'][0],
                        head_info['minute'][0], head_info['second'][0])
                else:
                    time = meteva.base.tool.time_tools.all_type_time_to_time64(time)
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

                if element_id0 is None:
                    dict0 = {}
                    id_dict = meteva.base.gds_element_id_dict
                    for key in element_map.keys():
                        if (int(key) in id_dict.values()):
                            for ele in id_dict.keys():
                                if int(key) == id_dict[ele]:
                                    dict0[ele] = key
                    if len(dict0.keys()) > 1:
                        print("element_id can not be None for this file")
                    else:
                        element_id_str0 = list(dict0.values())[0]
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
                        sta = meteva.base.put_stadata_on_station(records, station)
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
                    meteva.base.set_stadata_names(sta,[data_name])
                    sta['time'] = time
                    sta['level'] = level
                    sta['dtime'] = dtime
                    if show:
                        print("success read from " + filename)
                    return sta
            else:
                print("连接服务状态正常，但返回的输入内容为空")
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

def read_stadata_from_gdsfile(filename,element_id = None,station = None, level=None,time=None, dtime=None, data_name='data0',show = False):

    element_id0 = element_id
    if element_id is not None:
        element_id_str0 = str(element_id)

    if os.path.exists(filename):
        try:
            element_id_str0 = str(element_id)
            file = open(filename,"rb")
            byteArray = file.read()
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
            else:
                time = meteva.base.tool.time_tools.all_type_time_to_time64(time)
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

            if element_id0 is None:
                dict0 = {}
                id_dict = meteva.base.gds_element_id_dict
                for key in element_map.keys():
                    if (int(key) in id_dict.values()):
                        for ele in id_dict.keys():
                            if int(key) == id_dict[ele]:
                                dict0[ele] = key
                if len(dict0.keys())>1:
                    print("element_id can not be None for this file" )
                else:
                    element_id_str0 = list(dict0.values())[0]
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
                    sta = meteva.base.put_stadata_on_station(records, station)
                    if show:
                        print("success read from " + filename)
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
                meteva.base.set_stadata_names(sta,[data_name])
                sta['time'] = time
                sta['level'] = level
                sta['dtime'] = dtime
                if show:
                    print("success read from " + filename)
                return sta
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)
            print(filename + "数据读取失败")
            return None
    else:
        print(filename + " not exist")

def read_stawind_from_gds(filename,station = None, level=None,time=None, dtime=None,data_name = "",show = True):

    if meteva.base.gds_ip_port is None:
        print("请先使用set_config 配置gds的ip和port")
        return
    directory, filename = os.path.split(filename)
    ip,port = meteva.base.gds_ip_port
    service = GDSDataService(ip, port)

    try:
        directory = directory.replace("mdfs:///", "")
        directory = directory.replace("\\","/")
        #print(filename)
        status, response = service.getData(directory, filename)

    except ValueError:
        print('Can not retrieve data' + filename + ' from ' + directory)
        return None
    try:
        ByteArrayResult = DataBlock_pb2.ByteArrayResult()
        if status == 200:
            ByteArrayResult.ParseFromString(response)
            if ByteArrayResult is not None:
                byteArray = ByteArrayResult.byteArray

                head_dtype = [('discriminator', 'S4'), ('type', 'i2'),
                          ('description', 'S100'),
                          ('level', 'f4'), ('levelDescription', 'S50'),
                          ('year', 'i4'), ('month', 'i4'), ('day', 'i4'),
                          ('hour', 'i4'), ('minute', 'i4'), ('second', 'i4'),
                          ('Timezone', 'i4'), ('extent', 'S100')]
                if(len(byteArray)<300):
                    return None
                # read head information
                head_info = np.frombuffer(byteArray[0:288], dtype=head_dtype)
                if time is None:
                    time = datetime.datetime(
                        head_info['year'][0], head_info['month'][0],
                        head_info['day'][0], head_info['hour'][0],
                        head_info['minute'][0], head_info['second'][0])
                else:
                    time = meteva.base.tool.time_tools.all_type_time_to_time64(time)
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

                dict0 = {}
                id_dict = meteva.base.gds_element_id_dict



                speed_id = -1
                angle_id = -1
                for key in element_map.keys():
                    if (int(key) in id_dict.values()):
                        for ele in id_dict.keys():
                            if int(key) == id_dict[ele]:
                                dict0[ele] = key
                                if ele.find("风速")>0:
                                    speed_id = key
                                    #print(ele)
                                if ele.find("风向")>0:
                                    angle_id = key
                                    #print(ele)

                if speed_id == -1 or angle_id == -1:
                    print("the file doesn't contains wind")
                dtype_str_speed = element_map[speed_id]
                dtype_str_angle = element_map[angle_id]

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
                            hadwind = False
                            if element_id == speed_id:
                                record["speed"] = np.frombuffer(
                                    byteArray[ind:(ind + element_len)],
                                    dtype=dtype_str_speed)[0]
                                hadwind = True
                            if element_id == angle_id:
                                record["angle"] = np.frombuffer(
                                    byteArray[ind:(ind + element_len)],
                                    dtype=dtype_str_angle)[0]
                                hadwind = True
                            if hadwind:
                                records.append(record)
                            ind += element_len
                    records = pd.DataFrame(records)
                    records.set_index('id')
                    # get time

                    records['time'] = time
                    records['level'] = level
                    records['dtime'] = dtime
                    new_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', "speed"+data_name,"angle"+data_name]
                    records = records.reindex(columns=new_columns)
                    if station is None:
                        return records
                    else:
                        sta = meteva.base.put_stadata_on_station(records, station)
                        if show:
                            print("success read from " + filename)
                        return sta
                else:
                    sta = copy.deepcopy(station)
                    meteva.base.set_stadata_names(sta,["speed"+data_name])
                    sta["angle"+data_name] = meteva.base.IV
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
                                        if element_id == speed_id:
                                            sta.iloc[k,-2] = np.frombuffer(byteArray[ind1:(ind1 + element_len)],dtype=dtype_str_speed)[0]
                                        if element_id == angle_id:
                                            sta.iloc[k,-1] = np.frombuffer(byteArray[ind1:(ind1 + element_len)],dtype=dtype_str_angle)[0]
                                        ind1 += element_len
                    sta['time'] = time
                    sta['level'] = level
                    sta['dtime'] = dtime

                    if show:
                        print("success read from " + filename)
                    return sta
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

def read_stawind_from_gdsfile(filename,station = None, level=None,time=None, dtime=None,data_name = "",show = False):
    if os.path.exists(filename):
        try:
            file = open(filename,"rb")
            byteArray = file.read()
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
            else:
                time = meteva.base.tool.time_tools.all_type_time_to_time64(time)

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

            dict0 = {}
            id_dict = meteva.base.gds_element_id_dict



            speed_id = -1
            angle_id = -1
            for key in element_map.keys():
                if (int(key) in id_dict.values()):
                    for ele in id_dict.keys():
                        if int(key) == id_dict[ele]:
                            dict0[ele] = key
                            if ele.find("风速")>0:
                                speed_id = key
                                print(ele)
                            if ele.find("风向")>0:
                                angle_id = key
                                print(ele)

            if speed_id == -1 or angle_id == -1:
                print("the file doesn't contains wind")
            dtype_str_speed = element_map[speed_id]
            dtype_str_angle = element_map[angle_id]

            # loop every station to retrieve record
            record_head_dtype = [
                ('id', 'i4'), ('lon', 'f4'), ('lat', 'f4'), ('numb', 'i2')]
            records = []
            speed_name = "speed"+data_name
            angle_name = "angle"+data_name
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
                        hadwind = False
                        if element_id == speed_id:
                            record[speed_name] = np.frombuffer(
                                byteArray[ind:(ind + element_len)],
                                dtype=dtype_str_speed)[0]
                            hadwind = True
                        if element_id == angle_id:
                            record[angle_name] = np.frombuffer(
                                byteArray[ind:(ind + element_len)],
                                dtype=dtype_str_angle)[0]
                            hadwind = True
                        if hadwind:
                            records.append(record)
                        ind += element_len
                records = pd.DataFrame(records)
                records.set_index('id')
                # get time

                records['time'] = time
                records['level'] = level
                records['dtime'] = dtime
                new_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', "speed"+data_name,"angle"+data_name]
                records = records.reindex(columns=new_columns)
                if station is None:
                    return records
                else:
                    sta = meteva.base.put_stadata_on_station(records, station)
                    if show:
                        print("success read from " + filename)
                    return sta
            else:
                sta = copy.deepcopy(station)
                meteva.base.set_stadata_names(sta,["speed"+data_name])
                sta["angle"+data_name] = meteva.base.IV
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
                                    if element_id == speed_id:
                                        sta.iloc[k,-2] = np.frombuffer(byteArray[ind1:(ind1 + element_len)],dtype=dtype_str_speed)[0]
                                    if element_id == angle_id:
                                        sta.iloc[k,-1] = np.frombuffer(byteArray[ind1:(ind1 + element_len)],dtype=dtype_str_angle)[0]
                                    ind1 += element_len
                sta['time'] = time
                sta['level'] = level
                sta['dtime'] = dtime
                if show:
                    print("success read from " + filename)
                return sta
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)
            print(filename + "数据读取失败")
            return None
    else:
        print(filename +" not exists")
        return None

def read_stadata_from_gds_griddata(filename,station,level = None,time =None,dtime = None,data_name = "data0",show = False):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"
    if meteva.base.gds_ip_port is None:
        print("请先使用set_config 配置gds的ip和port")
        return
    ip,port = meteva.base.gds_ip_port
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
                level1, y, m, d, h, timezone, period = struct.unpack("fiiiiii", byteArray[106:134])
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
                if time is None:
                    time = datetime.datetime(y, m, d, h, 0)
                else:
                    time = meteva.base.tool.time_tools.all_type_time_to_time64(time)
                if level is None:
                    level = level1
                if dtime is None:
                    dtime = period
                sta.loc[:, "level"] = level
                sta.loc[:, "time"] = time
                sta.loc[:, "dtime"] = dtime
                meteva.base.set_stadata_names(sta,[data_name])
                if show:
                    print("success read from " + filename)
                return sta
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
        print(filename +" 数据读取失败")
        return None

def print_gds_file_values_names(filename):
    # ip 为字符串形式，示例 “10.20.30.40”
    # port 为整数形式
    # filename 为字符串形式 示例 "ECMWF_HR/TCDC/19083108.000"
    value_id_list= []

    if os.path.exists(filename):
        ip,port = None,None
    else:
        if meteva.base.gds_ip_port is None:
            print("请先使用set_config 配置gds的ip和port")
            return
        ip,port = meteva.base.gds_ip_port

    filename = filename.replace("mdfs:///", "")
    filename = filename.replace("\\", "/")

    if ip is not None:
        service = GDSDataService(ip, port)
        try:
            directory, fileName = os.path.split(filename)
            status, response = service.getData(directory, fileName)
            ByteArrayResult = DataBlock_pb2.ByteArrayResult()
            if status == 200:
                ByteArrayResult.ParseFromString(response)
                if ByteArrayResult is not None:
                    byteArray = ByteArrayResult.byteArray
            else:
                print("数据内容不可读")
        except:
            exstr = traceback.format_exc()
            print(exstr)
    else:
        file = open(filename, "rb")
        byteArray = file.read()

    ind = 288
    # read the number of stations
    station_number = np.frombuffer(
        byteArray[ind:(ind + 4)], dtype='i4')[0]
    ind += 4

    # read the number of elements
    element_number = np.frombuffer(
        byteArray[ind:(ind + 2)], dtype='i2')[0]

    if element_number == 0:
        return None
    ind += 2

    # construct record structure
    element_type_map = {
        1: 'b1', 2: 'i2', 3: 'i4', 4: 'i8', 5: 'f4', 6: 'f8', 7: 'S1'}
    element_map = {}
    element_map_len = {}
    for i in range(element_number):
        element_id = str(np.frombuffer(byteArray[ind:(ind + 2)], dtype='i2')[0])
        ind += 2
        element_type = np.frombuffer(
            byteArray[ind:(ind + 2)], dtype='i2')[0]
        ind += 2
        element_map[element_id] = element_type_map[element_type]
        element_map_len[element_id] = int(element_type_map[element_type][1])
    id_dict = meteva.base.gds_element_id_dict

    dict0 = {}
    for key in element_map.keys():
        if(int(key) in id_dict.values()):
            for ele in id_dict.keys():
                if int(key) == id_dict[ele]:
                    dict0[ele] = int(key)
                    print(ele + ":" + key)
    return dict0

def read_stadata_from_micaps16(filename,level = None,time= None,dtime = None,data_name = "data0",show = False):
    if not os.path.exists(filename):
        print(filename+"文件不存在")
        return None
    else:
        encoding,_ = meteva.base.io.get_encoding_of_file(filename,read_rows=1)
        if encoding is None:
            print("文件编码格式不识别")
            return None
        try:
            file = open(filename, 'r',encoding=encoding)
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
            station = pd.DataFrame(dat, columns=['id','lon', 'lat', data_name])
            station = meteva.base.sta_data(station)
            meteva.base.set_stadata_coords(station,level=level,time= time,dtime = dtime)
            if show:
                print("success read from " + filename)
            return station
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)
            print(filename+"文件格式不能识别。可能原因：文件未按micaps16格式存储")
            return None


def read_stadata_from_gds_griddata_file(filename,station,level = None,time = None,dtime = None,data_name = "data0",show = False):
    if os.path.exists(filename):
        try:
            file = open(filename,"rb")
            position = file.seek(106)
            content = file.read(28)
            level1, y, m, d, h, timezone, period = struct.unpack("fiiiiii", content)
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
            file.close()
            sta = copy.deepcopy(station)
            sta.iloc[:, -1] = dat[:]
            if time is None:
                time = datetime.datetime(y, m, d, h, 0)
            else:
                time = meteva.base.tool.time_tools.all_type_time_to_time64(time)
            if level is None:
                level = level1
            if dtime is None:
                dtime = period
            sta.loc[:, "level"] = level
            sta.loc[:, "time"] = time
            sta.loc[:, "dtime"] = dtime
            meteva.base.set_stadata_names(sta, [data_name])

            if show:
                print("success read from " + filename)
            return sta
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)
            print(filename+"文件格式不能识别")
            return None
    else:
        print(filename + " not exist")
        return None

def read_stawind_from_gds_gridwind_file(filename,station,level = None,time = None,dtime = None,data_name = "",show = False):
    if os.path.exists(filename):
        try:
            file = open(filename, "rb")
            position = file.seek(106)
            content = file.read(28)
            level1, y, m, d, h, timezone, period = struct.unpack("fiiiiii", content)
            position = file.seek(134)
            content = file.read(32)
            slon, elon, dlon, nlon, slat, elat, dlat, nlat = struct.unpack("fffifffi", content)
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
            udata = np.zeros(nsta)
            vdata = np.zeros(nsta)
            i_s0 = 278
            i_s1 = i_s0 + nlon * nlat * 4

            for i in range(nsta):
                position = file.seek(i00[i] * 4 + i_s0)
                content = file.read(4)
                dat00 = np.frombuffer(content, dtype='float32')
                position = file.seek(i01[i] * 4 + i_s0)
                content = file.read(4)
                dat01 = np.frombuffer(content, dtype='float32')
                position = file.seek(i10[i] * 4 + i_s0)
                content = file.read(4)
                dat10 = np.frombuffer(content, dtype='float32')
                position = file.seek(i11[i] * 4 + i_s0)
                content = file.read(4)
                dat11 = np.frombuffer(content, dtype='float32')
                udata[i] = c00[i] * dat00 + c01[i] * dat01 + c10[i] * dat10 + c11[i] * dat11

                position = file.seek(i00[i] * 4 + i_s1)
                content = file.read(4)
                dat00 = np.frombuffer(content, dtype='float32')
                position = file.seek(i01[i] * 4 + i_s1)
                content = file.read(4)
                dat01 = np.frombuffer(content, dtype='float32')
                position = file.seek(i10[i] * 4 + i_s1)
                content = file.read(4)
                dat10 = np.frombuffer(content, dtype='float32')
                position = file.seek(i11[i] * 4 + i_s1)
                content = file.read(4)
                dat11 = np.frombuffer(content, dtype='float32')
                vdata[i] = c00[i] * dat00 + c01[i] * dat01 + c10[i] * dat10 + c11[i] * dat11
            file.close()
            sta = copy.deepcopy(station)
            sta.iloc[:, -1] = udata[:]
            sta["v"] = vdata
            if time is None:
                time = datetime.datetime(y, m, d, h, 0)
            else:
                time = meteva.base.tool.time_tools.all_type_time_to_time64(time)
            if level is None:
                level = level1
            if dtime is None:
                dtime = period
            sta.loc[:, "level"] = level
            sta.loc[:, "time"] = time
            sta.loc[:, "dtime"] = dtime
            meteva.base.set_stadata_names(sta,["u"+data_name,"v"+data_name])

            if show:
                print("success read from " + filename)
            return sta
        except:
            if show:
                exstr = traceback.format_exc()
                print(exstr)
            print(filename + "文件格式不能识别")
            return None
    else:
        print(filename + " not exist")
        return None
