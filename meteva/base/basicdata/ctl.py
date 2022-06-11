#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import math
from copy import deepcopy
#创建一个类ctl,并初始化一些变量。
import os
import numpy as np
import datetime
import re


def read_ctl(ctl_filename):
    #print(ctl_filename)
    if os.path.exists(ctl_filename):
        ctl = {}
        file = open(ctl_filename, 'r')
        line = file.read()
        strs_all = line.split()
        file.close()

        file = open(ctl_filename, 'r')
        line = file.readline()
        strs = line.split()

        if strs[1].__contains__('^'):
            ctl["data_path"] = os.path.dirname(ctl_filename) + "/" + strs[1][1:]
        else:
            ctl["data_path"] = strs[1]
        print( ctl["data_path"])
        index_zdef = 0
        while line:
            strs = line.split()
            if len(strs) >0:
                index_zdef += len(strs)
                if strs[0].upper() == "PDEF":
                    ctl["pdef"] = {}
                    ctl["pdef"]["nx"] = int(strs[1])
                    ctl["pdef"]["ny"] = int(strs[2])
                    ctl["pdef"]["type"] = strs[3]
                    ctl["pdef"]["model_lat"] = float(strs[4])
                    ctl["pdef"]["model_lon"] = float(strs[5])
                    ctl["pdef"]["model_i"] = float(strs[6])
                    ctl["pdef"]["model_j"] = float(strs[7])
                    ctl["pdef"]["proj_slat"] = float(strs[8])
                    ctl["pdef"]["proj_elat"] = float(strs[9])
                    ctl["pdef"]["proj_mlon"] = float(strs[10])
                    ctl["pdef"]["dx"] = float(strs[11])
                    ctl["pdef"]["dy"] = float(strs[12])

                if strs[0].upper() == "XDEF":
                    if strs[2].lower() == "linear":
                        nlon = int(strs[1])
                        slon = float(strs[3])
                        dlon = float(strs[4])
                        elon = slon + (nlon -1) * dlon
                        ctl["xdef"] = (np.arange(nlon) * dlon + slon).tolist()
                        ctl["glon"] = [slon,elon,dlon]
                        ctl["nlon"] =nlon
                if strs[0].upper() == "YDEF":
                    if strs[2].lower() == "linear":
                        nlat = int(strs[1])
                        slat = float(strs[3])
                        dlat = float(strs[4])
                        elat = slat +(nlat-1)*dlat
                        ctl["ydef"] = (np.arange(nlat) * dlat + slat).tolist()
                        ctl["glat"] = [slat, elat, dlat]
                        ctl["nlat"] = nlat
                if strs[0].upper() == "ZDEF":
                    if strs[2].upper()=="LINEAR":
                        ctl["nlevel"] = int(strs[1])
                        levels = []
                        for ii in range(ctl["nlevel"]):

                            levels.append(float(strs[3]) + ii * float(strs[4]))
                        ctl["zdef"] = levels
                    else:
                        nlevel =  int(strs[1])
                        ctl["nlevel"] =nlevel
                        levels = []
                        if len(strs) > 3:
                            for i in range(nlevel):
                                levels.append(float(strs_all[index_zdef + i - nlevel]))
                        else:
                            for i in range(nlevel):
                                levels.append(float(strs_all[index_zdef + i]))

                        ctl["zdef"] = levels
                        ctl["nlevel"] = len(levels)


                if strs[0].upper() == "TDEF":
                    ntime = int(strs[1])
                    ctl["ntime"] = ntime
                    if strs[2].upper() == "LINEAR":
                        time_str = strs[3]
                        year = int(strs[3][-4:])
                        #print(strs[3])
                        mm_str = strs[3][-7:-4].lower()
                        dict1 = {"jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
                                 "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12}
                        mm = dict1[mm_str]
                        zindex = -1
                        if time_str.find("z") >= 0:
                            zindex = time_str.find("z")
                        elif time_str.find("Z") >= 0:
                            zindex = time_str.find("Z")

                        if zindex >= 0:
                            dd = int(time_str[zindex + 1:-7])
                            hh = int(time_str[0:zindex])
                        else:
                            dd = int(time_str[0:-7])
                            hh = 0
                        time_begin = datetime.datetime(year, mm, dd, hh, 0)
                        dtime_str = strs[4]
                        dt = int(dtime_str[0:-2])
                        dict2 = {"mn": "m", "hr": "H", "dy": "D", "mo": "M", "yr": "Y"}
                        dt_unit = dtime_str[-2:].lower()

                        if dt_unit == "mn":
                            time_end = time_begin + datetime.timedelta(minutes=dt * (ntime - 1))
                        elif dt_unit== "hr":
                            time_end = time_begin + datetime.timedelta(hours=dt * (ntime - 1))
                        elif dt_unit== "dy":
                            time_end = time_begin + datetime.timedelta(days=dt * (ntime - 1))
                        else:
                            time_end = None
                            print("暂时还不能支持逐月或逐年数据的读取")
                        ctl["gtime"] = [time_begin, time_end, str(dt) + dict2[dt_unit]]
                        ctl["dtime_list"] = (np.arange(ntime) * dt).tolist()
                    else:
                        print("TDEF 不是线性数组的情况暂不能支持")


                if (strs[0].upper() == "EDEF"):
                    nensemble = int(strs[1])
                    ctl["edef"] = np.arange(nensemble).tolist()
                    ctl["nensemble"] = nensemble

                if strs[0].upper() == "VARS":
                    nvar = int(strs[1])
                    ctl["vars"] = []
                    cumulate = 0
                    for v in range(nvar):
                        line = file.readline()
                        #strs = line.split()
                        strs = re.split("\s+|,",line)
                        onev = {}
                        onev["name"] = strs[0]
                        nlevel = int(strs[1])
                        if nlevel == 0:
                            nlevel = 1
                        onev["nlevel"] = nlevel
                        onev["type"] = int(strs[2])
                        onev["discription"] = strs[3]
                        onev["start_bolck_index"] = cumulate
                        cumulate += nlevel
                        ctl["vars"].append(onev)

            line = file.readline()
        if "edef" not in ctl.keys():
            ctl["edef"] = [0]
            ctl["nensemble"] = 1
        if "ntime" not in ctl.keys():
            ctl["ntime"] = 1
        return ctl
    else:
        return None

