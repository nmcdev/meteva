import meteva
import numpy as np
import datetime
import copy
import matplotlib.pyplot as plt
import time
import pandas as pd
import math
import matplotlib as mpl
import os

para= {
    "ip_port_file":r"H:\test_data\input\meb\ip_port.txt",
    "local_hdf_dir":"O:/data/mdfs",
    "local_sta_dir": "O:/data/sta",
    "local_grid_dir":"O:/data/grid",
    "veri_day_count":7,
    "station_file":meteva.base.station_国家站,
    "sta_data":{},
    "grid_data":{
        "SCMOC":[
                 ["NWFD_SCMOC/TMP/2M_ABOVE_GROUND","instant",0],
                 ["NWFD_SCMOC/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND","instant",0],
                 ["NWFD_SCMOC/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND","instant",0],
                 ["NWFD_SCMOC/RAIN03","accumulate",24]
        ],
        "GRAPES":[
                  ["GRAPES_GFS/TMP/2M_ABOVE_GROUND",None],
                  ["GRAPES_GFS/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/","max",24],
                  ["GRAPES_GFS/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND/","min",24],
                  ["GRAPES_GFS/APCP","delta",24]
        ],
        "ECMWF":[

        ]
    },
    "data_name":"ob"
    }

def creat_week_dataset(para):
    ip,port = meteva.base.read_gds_ip_port(para["ip_port_file"])
    now = datetime.datetime.now()
    now = datetime.datetime(now.year,now.month,now.day,now.hour,0)
    today = datetime.datetime(now.year,now.month,now.day,0,0)
    station = meteva.base.read_station(para["station_file"])
    station["data0"] = meteva.base.IV
    veri_day_count =para["veri_day_count"]

    #读取grapes数据
    dir_hdf = "YYMMDDHH.h5"
    dir_nc = r"O:\data\grid\GRAPES_GFS\TMP\2M_ABOVE_GROUND\YYYYMMDD\YYMMDDHH.TTT.nc"
    dir_gds = r"GRAPES_GFS\TMP\2M_ABOVE_GROUND\YYMMDDHH.TTT"
    data_name = "grapes"
    sta_list = []
    dir_gds0,file = os.path.split(dir_gds)
    gds_file_list = meteva.base.tool.path_tools.get_gds_file_list_in_one_dir(ip,port,dir_gds0)
    hour_list,dhour_list = meteva.product.application.get_hour_dhour_list(gds_file_list)
    max_dd = veri_day_count + int(dhour_list[-1]/24)
    if max_dd > veri_day_count * 2:
        max_dd = veri_day_count
    for dd in range(max_dd):
        day2 = today - datetime.timedelta(days = dd)
        sta_1f = None
        for hour in hour_list:
            time2 =  datetime.datetime(day2.year,day2.month,day2.day,hour,0)
            path_hdf = meteva.base.tool.path_tools.get_path(dir_hdf,time2)
            if os.path.exists(path_hdf):
                sta_1f = pd.read_hdf(path_hdf,"df")
            else:
                sta_list_1f  = []
                all_exist = True
                for dh in dhour_list:
                    path_nc = meteva.base.tool.path_tools.get_path(dir_nc,time2,dh)
                    grd = None
                    if os.path.exists(path_nc):
                        grd = meteva.base.read_griddata_from_nc(path_nc)
                    else:
                        path_gds = meteva.base.tool.path_tools.get_path(dir_gds,time2,dh)
                        if path_gds in gds_file_list:
                            #判断是否在gds服务器中
                            grd = meteva.base.read_griddata_from_gds(ip,port,path_gds)
                    if grd is not None:
                        sta = meteva.base.interp_gs_linear(grd,station)
                        meteva.base.set_stadata_coords(sta,time = time2,dtime = dh,level = 0)
                        meteva.base.set_stadata_names(sta,[data_name])
                        sta_list_1f.append(sta)
                    else:
                        all_exist = False
                if(len(sta_list_1f)>0):
                    sta_1f = pd.concat(sta_list_1f,axis = 0)
                    meteva.base.creat_path(path_hdf)
                    if(all_exist):
                        sta_1f.to_hdf(path_hdf,"df")
        if sta_1f is not None:
            sta_list.append(sta_1f)
    grapes_all = pd.concat(sta_list,axis = 0)

def combine_data_from_hdf(hdf_file_list,s = None):
    sta_list = []
    for file in hdf_file_list:
        sta = pd.read_hdf(file,"df")
        sta_list.append(sta)
    print(len(sta_list))
    sta_all = meteva.base.combine_on_obTime_id(sta_list[0],sta_list[1:])
    sta_all_s = meteva.base.sele_by_dict(sta_all,s)
    return sta_all_s