#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import numpy as np
import os
import pandas as pd
import nmc_verification.nmc_vf_base.basicdata as bd
import nmc_verification.nmc_vf_base.function as fun
import nmc_verification.nmc_vf_base.method as method
import traceback

def read_from_micaps3(filename,station = None,reserve_time_dtime_level = False):
    print(filename)
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
            sta1.columns = ['id','lon','lat','alt','data0']
            sta1.drop_duplicates(keep='first', inplace=True)
            sta = bd.sta_data(sta1)
            #print(sta)
            if(reserve_time_dtime_level):
                y2 = ""
                if len(strs[3]) == 2:
                    year = int(strs[3])
                    if year >= 50:
                        y2 = '19'
                    else:
                        y2 = '20'
                time_str = y2 + strs[3] + strs[4] + strs[5] + strs[6]
                time64 = method.time_tools.str_to_time64(time_str)
                level = int(strs[7])
                if level < 0: level = 0
                sta['time'] = time64
                sta['level'] = level
                sta['dtime'] = np.timedelta64(0,'h')
            if(station is not None):
                sta = fun.sta_sta.set_data_to(sta,station)
            return sta
        else:
            return None
    except:
        exstr = traceback.format_exc()
        print(exstr)
        return None

