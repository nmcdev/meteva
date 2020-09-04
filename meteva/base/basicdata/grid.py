import math
import datetime
from datetime import timedelta
import re
from copy import deepcopy
import time
import pandas as pd
import numpy as np

class grid:
    '''
        定义一个格点的类grid，来存储网格的范围包括（起始经纬度、格距、起止时间，时间间隔，起止时效，时效间隔，层次列表，数据成员）
        约定坐标顺序为: member, time,ddtime, level, lat,lon
    '''
    def __init__(self,glon, glat, gtime=None, dtime_list=None,level_list=None,member_list = None):

        #提取成员维度信息
        if(member_list is None):
            self.members =['data0']
        else:
            self.members = member_list
        ############################################################################
        #提取层次维度信息
        if(level_list is None):
            self.levels =[0]
        else:
            self.levels = level_list
        ############################################################################
        #提取时间维度信息
        self.stime = np.datetime64('2099-01-01T00:00:00.000000')
        self.etime = np.datetime64('2099-01-01T00:00:00.000000')
        self.dtime_int = 1
        self.dtime_type = "h"
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
                self.stime = datetime.datetime.strptime(num, '%Y%m%d%H%M%S')
                self.etime = datetime.datetime.strptime(num, '%Y%m%d%H%M%S')
                self.stime = np.datetime64(self.stime)
                self.etime = np.datetime64(self.etime)
            else:
                self.stime = gtime[0]
                self.etime = gtime[0]
            self.dtime_int = 1
            self.dtime_type = "h"
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
                #print(num1)
                self.stime = datetime.datetime.strptime(num1[0], '%Y%m%d%H%M%S')
                self.etime = datetime.datetime.strptime(num1[1], '%Y%m%d%H%M%S')
                self.stime = np.datetime64(self.stime)
                self.etime = np.datetime64(self.etime)
            elif isinstance(gtime[0],np.datetime64):
                stime = gtime[0].astype(datetime.datetime)
                etime = gtime[1].astype(datetime.datetime)
                if isinstance(stime, int):
                    stime = datetime.datetime.utcfromtimestamp(stime / 1000000000)
                    etime = datetime.datetime.utcfromtimestamp(etime / 1000000000)
                self.stime = stime
                self.etime = etime
            else:
                self.stime = gtime[0]
                self.etime = gtime[1]

            if type(gtime[2]) == str:
                self.dtime_int = re.findall(r"\d+", gtime[2])[0]
                dtime_type = re.findall(r"\D+", gtime[2])[0]
                if dtime_type == 'h':
                    self.dtime_type ="h"
                    self.dtimedelta = np.timedelta64(self.dtime_int,'h')
                elif dtime_type == 'd':
                    self.dtime_type ="D"
                    self.dtimedelta = np.timedelta64(self.dtime_int, 'D')
                elif dtime_type == 'm':
                    self.dtime_type ="m"
                    self.dtimedelta = np.timedelta64(self.dtime_int, 'm')
            elif isinstance(gtime[2],np.timedelta64):
                seconds = int(gtime[2] / np.timedelta64(1, 's'))
                if seconds % 3600 == 0:
                    self.dtime_type = "h"
                    self.dtime_int = int(seconds / 3600)
                else:
                    self.dtime_type = "m"
                    self.dtime_int = int(seconds / 60)
            else:
                self.dtimedelta = gtime[2]
                seconds = gtime[2].total_seconds()
                if seconds % 3600 == 0:
                    self.dtime_type = "h"
                    self.dtime_int = int(seconds/3600)
                else:
                    self.dtime_type = "m"
                    self.dtime_int = int(seconds / 60)
        self.gtime = [self.stime,self.etime,str(self.dtime_int) + self.dtime_type]
        self.stime_str = str(self.stime).replace("-","").replace(" ","").replace(":","").replace("T","")[0:14]
        self.etime_str = str(self.etime).replace("-", "").replace(" ", "").replace(":", "").replace("T", "")[0:14]
        self.dtime_str = str(self.dtime_int) + self.dtime_type

        ############################################################################
        #提取预报时效维度信息
        if dtime_list is None:
            self.dtimes = [0]
        else:
            self.dtimes = dtime_list
        ############################################################################
        #提取经度信息

        self.slon = glon[0]
        self.elon = glon[1]
        self.dlon = glon[2]
        nlon = 1 + (self.elon - self.slon) / self.dlon
        error = abs(round(nlon) - nlon)/nlon
        if (error > 0.01):
            self.nlon = int(math.ceil(nlon))
        else:
            self.nlon = int(round(nlon))
        self.elon = self.slon + (nlon - 1) * self.dlon
        self.glon = [self.slon,self.elon,self.dlon]

        ############################################################################
        #提取纬度信息
        self.slat = glat[0]
        self.elat = glat[1]
        self.dlat = glat[2]
        nlat = 1 + (self.elat - self.slat) / self.dlat
        error = abs(round(nlat) - nlat)/nlat
        if (error > 0.01):
            self.nlat = int(math.ceil(nlat))
        else:
            self.nlat = int(round(nlat))
        self.elat = self.slat + (nlat - 1) * self.dlat
        self.glat = [self.slat,self.elat,self.dlat]



    #对原有的格点数据进行一次深拷贝，不改变原有的值和结构。
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


    def __str__(self):
        '''
        重置系统自动的函数，在print(grid) 的时候可以很整齐的看到所有信息
        :return:  string
        '''
        grid_str = ""
        grid_str += "members:" + str(self.members) +"\n"
        grid_str += "levels:" + str(self.levels) + "\n"
        grid_str += "gtime:" + str([self.stime_str,self.etime_str,self.dtime_str]) + "\n"
        grid_str += "dtimes:" + str(self.dtimes)  +"\n"
        grid_str += "glon:" + str(self.glon) + "\n"
        grid_str += "glat:" + str(self.glat) + "\n"
        return grid_str

def get_grid_of_data(grid_data0):
    '''
     获取grid的数据values值
    :param grid_data0:初始化之后的网格数据
    :return:返回grid数据。
    '''
    member_list = grid_data0['member'].values
    level_list = grid_data0['level'].values
    times = grid_data0['time'].values
    #print(times)
    if(len(times)>1):
        gtime = [times[0],times[-1],times[1]-times[0]]
    elif len(times) == 1:
        gtime = times
    else:
        gtime = None

    gdt = grid_data0['dtime'].values.tolist()
    attrs_name = list(grid_data0.attrs)

    lons = grid_data0['lon'].values
    glon = [lons[0],round(lons[-1],6),round(lons[1]-lons[0],6)]
    lats = grid_data0['lat'].values
    glat = [lats[0],round(lats[-1],6),round(lats[1]-lats[0],6)]
    grid01 = grid(glon, glat, gtime, gdt, level_list, member_list)
    return grid01


def reset_grid(grid0):
    if grid0.dlat <0:
        grid0.dlat = - grid0.dlat
        tran = grid0.slat
        grid0.slat = grid0.elat
        grid0.elat = tran
    return
