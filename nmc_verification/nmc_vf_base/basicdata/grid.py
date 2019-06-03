#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import math
import datetime
from datetime import timedelta
import re
from copy import deepcopy
import time
import pandas as pd
import numpy as np

'''
约定坐标顺序为: member, time,ddtime, level, lat,lon
添加一个grid类来存储网格的范围包括（起始经纬度、格距、起止时间，时间间隔，起止时效，时效间隔，层次列表，数据成员）
'''


class grid:
    def __init__(self,glon, glat, gtime=None, gdtime=None,levels=None,nmember = 1):

        self.nmember = nmember
        ############################################################################
        #提取层次维度信息
        if(levels == None):
            self.levels =[0]
        else:
            self.levels = levels
        ############################################################################
        #提取时间维度信息
        self.stime = np.datetime64('2099-01-01T00:00:00.000000')
        self.etime = np.datetime64('2099-01-01T00:00:00.000000')
        self.dtime_int = 1
        self.dtime_type = "hour"
        self.dtimedelta = np.timedelta64(1,'h')
        if(gtime == None):gtime = []
        if len(gtime) == 1:
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
                self.stime = datetime.strptime(num, '%Y%m%d%H%M%S')
                self.etime = datetime.strptime(num, '%Y%m%d%H%M%S')
                self.stime = np.datetime64(self.stime)
                self.etime = np.datetime64(self.etime)
            else:
                self.stime = gtime[0]
                self.etime = gtime[0]
            self.dtime_int = 1
            self.dtime_type = "hour"
            self.dtimedelta = np.timedelta64(0,'h')
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
                self.stime = datetime.strptime(num1[0], '%Y%m%d%H%M%S')
                self.etime = datetime.strptime(num1[1], '%Y%m%d%H%M%S')
                self.stime = np.datetime64(self.stime)
                self.etime = np.datetime64(self.etime)
            else:
                self.stime = gtime[0]
                self.etime = gtime[1]

            if type(gtime[2]) == str:
                self.dtime_int = re.findall(r"\d+", gtime[2])[0]
                dtime_type = re.findall(r"\D+", gtime[2])[0]
                if dtime_type == 'h':
                    self.dtime_type ="hour"
                    self.dtimedelta = np.timedelta64(self.dtime_int,'h')
                elif dtime_type == 'd':
                    self.dtime_type ="Day"
                    self.dtimedelta = np.timedelta64(self.dtime_int, 'D')
                elif dtime_type == 'm':
                    self.dtime_type ="minute"
                    self.dtimedelta = np.timedelta64(self.dtime_int, 'm')
            else:
                self.dtimedelta = gtime[2]
                seconds = gtime[2].total_seconds()
                if seconds % 3600 == 0:
                    self.dtime_type = "hour"
                    self.dtime_int = int(seconds/3600)
                else:
                    self.dtime_type = "minute"
                    self.dtime_int = int(seconds / 60)
        self.gtime = [self.stime,self.etime,str(self.dtime_int) + self.dtime_type]
        self.stime_str = str(self.stime).replace("-","").replace(" ","").replace(":","").replace("T","")[0:14]
        self.etime_str = str(self.etime).replace("-", "").replace(" ", "").replace(":", "").replace("T", "")[0:14]
        self.dtime_str = str(self.dtime_int) + self.dtime_type

        ############################################################################
        #提取预报时效维度信息

        self.sdt_int = 0
        self.edt_int = 0
        self.ddt_int = 1
        self.sdtimedelta = np.timedelta64(0, 'h')
        self.edtimedelta = np.timedelta64(0, 'h')
        self.ddtimedelta = np.timedelta64(1, 'h')
        self.gdtime_type = "hour"
        if (gdtime == None): gdtime = []
        if len(gdtime)==1:
            num2 = []
            if type(gdtime[0]) == str:
                for i in range(1):
                    gdt_num = ''.join([x for x in gdtime[i] if x.isdigit()])
                    num2.append(gdt_num)
                self.sdt_int = int(num2[0])
                self.edt_int = int(num2[0])
                self.ddt_int = 1
                # 提取出dtime_type类型
                TIME_type = re.findall(r"\D+", gdtime[2])[0]
                if TIME_type == 'h':
                    self.gdtime_type = "hour"
                    self.sdtimedelta = np.timedelta64(self.sdt_int, 'h')
                    self.edtimedelta = np.timedelta64(self.edt_int, 'h')
                    self.ddtimedelta = np.timedelta64(self.ddt_int, 'h')
                elif TIME_type == 'd':
                    self.gdtime_type = "Day"
                    self.sdtimedelta = np.timedelta64(self.sdt_int, 'D')
                    self.edtimedelta = np.timedelta64(self.edt_int, 'D')
                    self.ddtimedelta = np.timedelta64(self.edt_int, 'D')
                elif TIME_type == 'm':
                    self.gdtime_type = "minute"
                    self.sdtimedelta = np.timedelta64(self.sdt_int, 'm')
                    self.edtimedelta = np.timedelta64(self.edt_int, 'm')
                    self.ddtimedelta = np.timedelta64(self.edt_int, 'm')
            else:
                if isinstance(gdtime[0],datetime.timedelta):
                    seconds = gdtime[0].total_seconds()
                else:
                    seconds = gdtime[0].astype('timedelta64[s]')/np.timedelta64(1, 's')

                if seconds % 3600 == 0:
                    self.sdt_int = int(seconds / 3600)
                    self.edt_int = int(seconds / 3600)
                    self.ddt_int = 1
                    self.gdtime_type = "hour"
                    self.sdtimedelta = gdtime[0]
                    self.edtimedelta = gdtime[0]

                else:
                    self.dtime_type = "minute"
                    self.sdt_int = int(seconds / 60)
                    self.edt_int = int(seconds / 60)
                    self.ddt_int = 1
                self.sdtimedelta = gdtime[0]
                self.edtimedelta = gdtime[0]
                self.ddtimedelta = np.timedelta64(1, 'h')
        elif  len(gdtime) == 3:
            num2 = []
            if type(gdtime[0]) == str:
                for i in range(0, 3):
                    gdt_num = ''.join([x for x in gdtime[i] if x.isdigit()])
                    num2.append(gdt_num)
                self.sdt_int = int(num2[0])
                self.edt_int = int(num2[1])
                self.ddt_int = int(num2[2])
                #提取出dtime_type类型
                TIME_type = re.findall(r"\D+", gdtime[2])[0]
                if TIME_type == 'h':
                    self.gdtime_type = "hour"
                    self.sdtimedelta = np.timedelta64(self.sdt_int, 'h')
                    self.edtimedelta = np.timedelta64(self.edt_int, 'h')
                    self.ddtimedelta = np.timedelta64(self.ddt_int, 'h')
                elif TIME_type == 'd':
                    self.gdtime_type = "Day"
                    self.sdtimedelta = np.timedelta64(self.sdt_int, 'D')
                    self.edtimedelta = np.timedelta64(self.edt_int, 'D')
                    self.ddtimedelta = np.timedelta64(self.ddt_int, 'D')
                elif TIME_type == 'm':
                    self.gdtime_type = "minute"
                    self.sdtimedelta = np.timedelta64(self.sdt_int, 'm')
                    self.edtimedelta = np.timedelta64(self.edt_int, 'm')
                    self.ddtimedelta = np.timedelta64(self.ddt_int, 'm')
            else:
                seconds = gdtime[2].total_seconds()
                if seconds % 3600 == 0:
                    seconds1 = gdtime[0].total_seconds()
                    seconds2 = gdtime[1].total_seconds()
                    self.sdt_int = int(seconds1 / 3600)
                    self.edt_int = int(seconds2 / 3600)
                    self.ddt_int = int(seconds / 3600)
                    self.gdtime_type = "hour"
                    self.sdtimedelta = gdtime[0]
                    self.edtimedelta = gdtime[0]

                else:
                    self.dtime_type = "minute"
                    seconds1 = gdtime[0].total_seconds()
                    seconds2 = gdtime[1].total_seconds()
                    self.sdt_int = int(seconds1 / 60)
                    self.edt_int = int(seconds2 / 60)
                    self.ddt_int = int(seconds / 60)
                self.sdtimedelta = gdtime[0]
                self.edtimedelta = gdtime[1]
                self.ddtimedelta = gdtime[2]

        self.gdtime = [str(self.sdt_int),str(self.edt_int), str(self.ddt_int)+ self.gdtime_type[0]]

        ############################################################################
        #提取经度信息

        self.slon = glon[0]
        self.elon = glon[1]
        self.dlon = glon[2]
        nlon = 1 + (self.elon - self.slon) / self.dlon
        error = abs(round(nlon) - nlon)
        if (error > 0.01):
            self.nlon = math.ceil(nlon)
        else:
            self.nlon = int(round(nlon))
        self.elon = self.slon + (nlon - 1) * self.dlon
        self.glon = [self.slon,self.elon,self.dlon]

        ############################################################################
        #提取经度信息
        self.slat = glat[0]
        self.elat = glat[1]
        self.dlat = glat[2]
        nlat = 1 + (self.elat - self.slat) / self.dlat
        error = abs(round(nlat) - nlat)
        if (error > 0.01):
            self.nlat = math.ceil(nlat)
        else:
            self.nlat = int(round(nlat))
        self.elat = self.slat + (nlat - 1) * self.dlat
        self.glat = [self.slat,self.elat,self.dlat]




    def copy(self):
        return deepcopy(self)

    #reset的作用是把网格的坐标间隔统一为正数。
    def reset(self):
        if (self.dlon > 0 and self.dlat > 0):
            pass
        if (self.dlat < 0):
            tran = self.slat
            self.slat = self.elat
            self.elat = tran
            self.dlat = abs(self.dlat)
        if (self.dlon < 0):
            tran = self.slon
            self.slon = self.elon
            self.elon = tran
            self.dlon = abs(self.dlon)
        return

    # tostring 的作用是重置系统自动的函数，在print(grid) 的时候可以很整齐的看到所有信息
    def tostring(self):
        grid_str = ""
        grid_str += "member count:" + str(self.nmember) +"\n"
        grid_str += "levels:" + str(self.levels) + "\n"
        grid_str += "gtime:" + str([self.stime_str,self.etime_str,self.dtime_str]) + "\n"
        grid_str += "gdtime:" + str(self.gdtime)  +"\n"
        grid_str += "glon:" + str(self.glon) + "\n"
        grid_str += "glat:" + str(self.glat) + "\n"
        return grid_str
def get_grid_of_data(grid_data0):
    #print(grid_data0)
    nmember = len(grid_data0['member'].values)
    levels = grid_data0['level'].values
    times = grid_data0['time'].values
    print(times)
    if(len(times)>1):
        gtime = [times[0],times[-1],times[1]-times[0]]
    elif len(times) == 1:
        gtime = times
    else:
        gtime = None

    dtimes = grid_data0['dtime'].values
    if(len(dtimes)>1):
        gdt = [dtimes[0],dtimes[-1],dtimes[1]-dtimes[0]]
    elif len(dtimes) ==1:
        gdt = dtimes
    else:
        gdt = None

    lons = grid_data0['lon'].values
    glon = [lons[0],lons[-1],lons[1]-lons[0]]
    lats = grid_data0['lat'].values
    glat = [lats[0],lats[-1],lats[1]-lats[0]]
    grid01 = grid(glon, glat, gtime, gdt, levels, nmember)
    return grid01

