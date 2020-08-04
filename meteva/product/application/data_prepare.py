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

para_example= {
    "day_num":7,
    "end_time":datetime.datetime.now(),
    "station_file":meteva.base.station_国家站,
    "interp": meteva.base.interp_gs_nearest,
    "defalut_value":999999,
    "hdf_file_name":"week.h5",
    "ob_data":{
        "hdf_dir":r"O:\data\hdf\SURFACE\QC_BY_FSOL\TMP_ALL_STATION",
        "dir_ob": r"O:\data\sta\SURFACE\QC_BY_FSOL\TMP_ALL_STATION\YYYYMMDD\YYYYMMDDHH0000.000",
        "read_method":meteva.base.io.read_stadata_from_gdsfile,
        "read_para":{},
        "operation":None,
        "operation_para":{}
    },
    "fo_data":{
        "SCMOC":{
            "hdf_dir": r"O:\data\hdf\NWFD_SCMOC\TMP\2M_ABOVE_GROUND",
            "dir_fo": r"O:\data\grid\NWFD_SCMOC\TMP\2M_ABOVE_GROUND\YYYYMMDD\YYMMDDHH.TTT.nc",
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para_dict":{}
        },
        "GRAPES": {
            "hdf_dir": r"O:\data\hdf\GRAPES_GFS\TMP\2M_ABOVE_GROUND",
            "dir_fo": r"O:\data\grid\GRAPES_GFS\TMP\2M_ABOVE_GROUND\YYYYMMDD\YYMMDDHH.TTT.nc",
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para_dict": {}
        },
        "ECMWF":{
            "hdf_dir": r"O:\data\hdf\ECMWF_HR\TMP_2M",
            "dir_fo": r"O:\data\grid\ECMWF_HR\TMP_2M\YYYYMMDD\YYMMDDHH.TTT.nc",
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para_dict":{}
        }
    },
    "output_dir":r"O:\data\hdf\combined\temp_2m"
}


def prepare_dataset(para):
    '''

    :param para: 根据配置参数从站点和网格数据中读取数据插值到指定站表上，在存储成hdf格式文件，然后从hdf格式文件中读取相应的文件合并成检验要的数据集合文件
    :return:
    '''
    station = meteva.base.read_station(para["station_file"])
    station.iloc[:,-1] = para["defalut_value"]
    day_num = para["day_num"]
    end_time = para["end_time"]
    hdf_file_list = []
    hdf_file = para["ob_data"]["hdf_dir"] +"/"+ para["hdf_file_name"]
    hdf_file_list.append(hdf_file)
    read_para = para["ob_data"]["read_para"]
    creat_ob_dataset(hdf_file,para["ob_data"]["dir_ob"],station,"ob",end_time = end_time,day_num=day_num,
                     read_method=para["ob_data"]["read_method"], read_para = read_para,
                     operation=para["ob_data"]["operation"],operation_para = para["ob_data"]["operation_para"])
    models = para["fo_data"].keys()
    for model in models:
        hdf_file = para["fo_data"][model]["hdf_dir"] + "/" + para["hdf_file_name"]
        hdf_file_list.append(hdf_file)
        creat_fo_dataset(hdf_file,para["fo_data"][model]["dir_fo"],station,model,
                         end_time = end_time,day_num = day_num,
                         read_method=para["fo_data"][model]["read_method"], read_para=read_para,
                         operation = para["fo_data"][model]["operation"],
                         operation_para = para["fo_data"][model]["operation_para"],interp = para["interp"])

    output_file = para["output_dir"] + "/" + para["hdf_file_name"]
    meteva.base.path_tools.creat_path(output_file)
    combine_ob_fos_dataset(output_file,hdf_file_list)


def creat_fo_dataset(hdf_path, dir_fo, station,data_name,day_num,end_time = None,read_method= pd.read_hdf,read_para ={},interp = None, operation=None, operation_para={}):
    data0 = None
    if os.path.exists(hdf_path):
        data0 = pd.read_hdf(hdf_path, "df")
    # print(data0)
    sta_list = []
    if end_time is None:
        now = datetime.datetime.now()
    else:
        now = end_time
    today = datetime.datetime(now.year, now.month, now.day, 0, 0)
    before = today - datetime.timedelta(days=day_num)
    tomorrow = today + datetime.timedelta(days=1)
    exist_dtimes = {}


    if data0 is None:
        hours = np.arange(0, 24, 1).tolist()
        dtimes = np.arange(0, 721, 1).tolist()
    else:
        data_left = meteva.base.sele_by_para(data0, time_range=[before, tomorrow])
        if data_name is None:
            data_name = meteva.base.get_stadata_names(data_left)[0]
        else:
            meteva.base.set_stadata_names(data_left,data_name)
        sta_list.append(data_left)
        id0 = station["id"].values[0]
        data_id0 = meteva.base.sele_by_para(data0, id=id0)
        # print(data_id0)
        times = data_id0.loc[:, "time"].values.tolist()
        times = list(set(times))
        times.sort()
        # print(times)
        hours = []
        time1_list = []
        for i in range(len(times)):
            # print(times[i])
            time1 = meteva.base.time_tools.all_type_time_to_datetime(times[i])
            hours.append(time1.hour)
            time1_list.append(time1)
        hours = list(set(hours))
        hours.sort()

        dtimes = data_id0.loc[:, "dtime"].values.tolist()
        dtimes = list(set(dtimes))
        dtimes.sort()
        for time0 in time1_list:
            data_id0_time0 = meteva.base.sele_by_para(data_id0, time=time0)
            # print(data_id0_time0)
            ehours = data_id0_time0.loc[:, "dtime"].values.tolist()
            # print(ehours)
            exist_dtimes[time0] = ehours
    # print(hours)
    # print(dtimes)
    # print(exist_dtimes)
    for dd in range(day_num):
        for hh in range(len(hours)):
            hour = hours[hh]
            # print(hour)
            time1 = today - datetime.timedelta(days=dd) + datetime.timedelta(hours=hour)
            for dt in dtimes:
                if time1 in exist_dtimes.keys():
                    exist_dtime = exist_dtimes[time1]
                    if dt in exist_dtime:
                        continue
                path = meteva.base.get_path(dir_fo, time1, dt)
                if os.path.exists(path):
                    print(path)
                    #grd = meteva.base.read_griddata_from_nc(path, time=time1, dtime=dt,data_name= data_name)
                    #print(read_para)
                    dat = read_method(path,**read_para)

                    if dat is not None:
                        if not isinstance(dat, pd.DataFrame):
                            dat = interp(dat, station)
                        meteva.base.set_stadata_coords(dat,time = time1,dtime = dt)
                        meteva.base.set_stadata_names(dat,data_name)
                        sta_list.append(dat)

    if(len(sta_list) == 0):
        print("there is not file data in " + dir_fo)
        return
    sta_all = pd.concat(sta_list, axis=0)

    print(hdf_path)
    meteva.base.creat_path(hdf_path)
    sta_all.to_hdf(hdf_path, "df")

def creat_ob_dataset(hdf_path, dir_ob,station,data_name,day_num,end_time = None,read_method = pd.read_hdf,read_para = {}, interp = None,operation=None, operation_para={}):
    data0 = None
    if os.path.exists(hdf_path):
        data0 = pd.read_hdf(hdf_path, "df")
    # print(data0)
    sta_list = []
    if end_time is None:
        now = datetime.datetime.now()
    else:
        now = end_time

    today = datetime.datetime(now.year, now.month, now.day, 0, 0)
    before = today - datetime.timedelta(days=day_num)
    tomorrow = today + datetime.timedelta(days=1)
    time1_list = []
    if data0 is None:
        hours = np.arange(0, 24, 1).tolist()
    else:
        data_left = meteva.base.sele_by_para(data0, time_range=[before, tomorrow])
        if data_name is None:
            data_name = meteva.base.get_stadata_names(data_left)[0]
        else:
            meteva.base.set_stadata_names(data_left,data_name)
        sta_list.append(data_left)
        id0 = station["id"].values[0]
        data_id0 = meteva.base.sele_by_para(data0, id=id0)
        # print(data_id0)
        times = data_id0.loc[:, "time"].values.tolist()
        times = list(set(times))
        times.sort()
        # print(times)
        hours = []
        for i in range(len(times)):
            #print(times[i])
            time1 = meteva.base.time_tools.all_type_time_to_datetime(times[i])
            hours.append(time1.hour)
            time1_list.append(time1)
        hours = list(set(hours))
        hours.sort()


    for dd in range(day_num):
        for hh in range(len(hours)):
            hour = hours[hh]
            # print(hour)
            time1 = today - datetime.timedelta(days=dd) + datetime.timedelta(hours=hour)
            if time1 in time1_list:
                continue
            path = meteva.base.get_path(dir_ob, time1)
            if os.path.exists(path):
                print(path)
                #sta = meteva.base.read_stadata_from_gdsfile(path, station=station, time=time1,data_name= data_name)
                dat = read_method(path,**read_para)
                if dat is not None:
                    dat = meteva.base.fun.comp.put_stadata_on_station(dat,station)
                    if not isinstance(dat,pd.DataFrame):
                        dat = interp(dat,station)
                    meteva.base.set_stadata_names(dat,data_name)
                    meteva.base.set_stadata_coords(dat,time = time1)
                    sta_list.append(dat)
    sta_all = pd.concat(sta_list, axis=0)
    meteva.base.creat_path(hdf_path)
    print(hdf_path)
    sta_all.to_hdf(hdf_path, "df")

def load_ob_fos_dataset(ob_fos_path_list,ob_fos_name_list = None,reset_level = True):
    sta_all_list = []
    level_ob =0
    for i in range(len(ob_fos_path_list)):
        sta_all = pd.read_hdf(ob_fos_path_list[i],"df")
        if ob_fos_name_list is not None:
            meteva.base.set_stadata_names(sta_all,[ob_fos_name_list[i]])
        if reset_level and i==0:
            level_ob = sta_all.iloc[0,0]
        if np.isnan(level_ob):
            level_ob = 0
            meteva.base.set_stadata_coords(sta_all, level=level_ob)
        else:
            if reset_level and i !=0:
                meteva.base.set_stadata_coords(sta_all,level = level_ob)
        sta_all_list.append(sta_all)
        print(sta_all)
    sta_all_merged = meteva.base.combine_on_obTime_id(sta_all_list[0],sta_all_list[1:])
    return sta_all_merged

def combine_ob_fos_dataset(output_path,ob_fos_path_list,ob_fos_name_list = None,reset_level = True):
    sta_all_merged = load_ob_fos_dataset(ob_fos_path_list, ob_fos_name_list=ob_fos_name_list,reset_level= reset_level)
    sta_all_merged.to_hdf(output_path, "df")
    print("success combined data to " + output_path)


