#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import numpy as np
import os
import pandas as pd
import nmc_verification
import traceback
import re
import copy


def read_from_micaps3(filename,station = None,time = None,dtime = None,level = None,data_name = 'data0'):
    """
    读取micaps3格式文件转换为pandas中dataframe结构的数据
    :param station:站号，默认：None
    :param reserve_time_dtime_level:保留时间，时效和层次，默认为rue
    :param data_name:dataframe中数值的values列的名称
    :return:返回一个dataframe结构的多列站点数据。
    """
    try:
        if os.path.exists(filename):
            file = open(filename,'r')
            skip_num = 0
            strs = []
            nline = 0
            nregion = 0
            nstart = 0
            while 1>0:
                skip_num += 1
                str1 = file.readline()
                strs.extend(str1.split())

                if(len(strs)>8):
                    nline = int(strs[8])
                if(len(strs)>11 + nline):
                    nregion = int(strs[11 + nline])
                    nstart = nline + 2 * nregion + 14
                    if(len(strs) == nstart):
                        break
            file.close()

            file_sta = open(filename)
            sta1 = pd.read_csv(file_sta, skiprows=skip_num, sep="\s+", header=None, usecols=[0, 1, 2,3,4])

            sta1.columns = ['id','lon','lat','alt',data_name]
            sta1.drop_duplicates(keep='first', inplace=True)
            #sta = bd.sta_data(sta1)
            sta = nmc_verification.nmc_vf_base.basicdata.sta_data(sta1)
            #print(sta)

            y2 = ""
            if len(strs[3]) == 2:
                year = int(strs[3])
                if year >= 50:
                    y2 = '19'
                else:
                    y2 = '20'
            if len(strs[3]) == 1: strs[3] = "0"+ strs[3]
            if len(strs[4]) == 1: strs[4] = "0" + strs[4]
            if len(strs[5]) == 1: strs[5] = "0" + strs[5]
            if len(strs[6]) == 1: strs[6] = "0" + strs[6]

            time_str = y2 + strs[3] + strs[4] + strs[5] + strs[6]
            time_file = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(time_str)
            if(level is None):
                level = int(strs[7])
            if level < 0: level = 0
            sta['level'] = level

            if time is None:
                sta['time'] = time_file
            else:
                sta['time'] = time
            if dtime is None:
                sta['dtime'] = 0
            else:
                if dtime[-1][0] == "h":
                    sta['dtime'] = dtime[0]
                else:
                    sta['dtime'] = 10000 + dtime[0]

            if(station is not None):
                sta = nmc_verification.nmc_vf_base.function.sxy_sxy.set_data_to(sta, station)
            return sta
        else:
            return None
    except:
        exstr = traceback.format_exc()
        print(exstr)
        return None

def read_station(filename,columns,skiprows = 0):
    """
    读取站点数据
    :param filename:带有站点信息的路径已经文件名
    :param columns 列名
    ：skiprows:读取时跳过的行数，默认为：0
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
        if 'alt' not in columns:
            sta['alt'] = 0
        # sta['time'] = method.time_tools.str_to_time64("2099010108")
        sta['time'] = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time64("2099010108")
        sta['level'] = 0
        sta['dtime'] = 0
        # sta.coloumns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt', 'data0']
        sta['data0'] = 0
        nmc_verification.nmc_vf_base.basicdata.reset_id(sta)
        return sta
    else:
        print(filename + " not exist")
        return None
   

def read_from_sevp(filename0, element=None):

    '''
    兼容多个时次的预报产品文件 txt格式
    param：filename:文件路径和名称
    param:index:从1到21列数据的索引。
    return：dataframe格式的站点数据
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
            sta1['time'] = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time64(num_list[0])
            sta1['id'] = 99999
            sta1['lat'] = 99999
            sta1['lon'] = 99999
            sta1['alt'] = 99999

            line6_list = re.findall(r'[0-9.]+', line6)

            sta_low_num = int(line6_list[4])

            sta1.iloc[0: sta_low_num, -4] = line6_list[0]
            sta1.iloc[0: sta_low_num, -3] = line6_list[1]
            sta1.iloc[0: sta_low_num, -2] = line6_list[2]
            sta1.iloc[0: sta_low_num, -1] = line6_list[3]

            sta1.rename(columns={0: 'dtime'}, inplace=True)

            for i in range(1, int(line5)):
                next_sta_num = int(sta1.iloc[sta_low_num, 4])
                sta1.iloc[sta_low_num + 1:sta_low_num + next_sta_num + 1, -4] = sta1.iloc[sta_low_num + 1, 0]
                sta1.iloc[sta_low_num + 1:sta_low_num + next_sta_num + 1, -3] = sta1.iloc[sta_low_num + 1, 1]
                sta1.iloc[sta_low_num + 1:sta_low_num + next_sta_num + 1, -2] = sta1.iloc[sta_low_num + 1, 2]
                sta1.iloc[sta_low_num + 1:sta_low_num + next_sta_num + 1, -1] = sta1.iloc[sta_low_num + 1, 3]
                sta_low_num += next_sta_num + 1
            drop_data = sta1[(sta1.id == 99999)].index.tolist()
            data = sta1.drop(drop_data)
            data = nmc_verification.nmc_vf_base.sta_data(data, ['id', 'time', 'dtime', 'lon', 'lat', 'alt'])

            if element == None:
                data = data.ix[:, ~(data == 1).all()]
                return data
            dframe1 = copy.deepcopy(data)
            data = data.iloc[:, :7]
            dframe1.drop(dframe1.columns[[1, 2, 3, 4, 5, 6]], axis=1, inplace=True)
            line_name = dframe1.columns.tolist()[element]
            data1 = dframe1.iloc[:, element]

            data = pd.concat([data, data1], axis=1)
            data.rename({line_name:'data0'},inplace=True)

            return data
        else:
            print("不存在此文件,即将结束！")
    except:
        exstr = traceback.format_exc()
        print(exstr)

