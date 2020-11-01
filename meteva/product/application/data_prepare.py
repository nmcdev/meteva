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
    "begin_time":datetime.datetime.now() - datetime.timedelta(days=7),
    "end_time":datetime.datetime.now(),
    "station_file":r"H:\task\other\202009-veri_objective_method\sta_info.m3",
    "defalut_value":0,
    "hdf_file_name":"summer.h5",
    "interp": meteva.base.interp_gs_nearest,
    "ob_data":{
        "hdf_dir":r"H:\task\other\202009-veri_objective_method\ob_rain24",
        "dir_ob": r"Z:\data\surface\jiany_rr\r20\YYMMDDHH.000",
        "hour":None,
        "read_method": meteva.base.io.read_stadata_from_micaps3,
        "read_para": {},
        "reasonable_value": [0, 1000],
        "operation":None,
        "operation_para": {},
        "time_type": "BT",
    },
    "fo_data":{
        "ECMWF": {
            "hdf_dir": r"H:\task\other\202009-veri_objective_method\ECMWF_HR\rain24",
            "dir_fo": r"O:\data\grid\ECMWF_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour":[8,20,12],
            "dtime":[0,240,12],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": meteva.base.fun.change,
            "operation_para": {"used_coords": "dtime", "delta": 24},
            "time_type": "UT",
            "move_fo_time": 12
        },

        "SCMOC": {
            "hdf_dir": r"H:\task\other\202009-veri_objective_method\Forecaster\rain24",
            "dir_fo": r"O:\data\grid\NWFD_SCMOC\RAIN03\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour": [8, 20,12],
            "dtime":[3,240,3],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": meteva.base.fun.sum_of_sta,
            "operation_para": {"used_coords": ["dtime"], "span": 24},
            "time_type": "BT",
            "move_fo_time": 0
        },
    },
    "output_dir":r"H:\task\other\202009-veri_objective_method"
}



def prepare_dataset(para):
    '''

    :param para: 根据配置参数从站点和网格数据中读取数据插值到指定站表上，在存储成hdf格式文件，然后从hdf格式文件中读取相应的文件合并成检验要的数据集合文件
    :return:
    '''

    # 全局参数预处理，站点列表的读取
    station = meteva.base.read_station(para["station_file"])
    station.iloc[:,-1] = para["defalut_value"]
    para["station"] = station

    #全局参数预处理，起止日期的处理
    #day_num = para["day_num"]
    end_time = para["end_time"]
    if end_time is None:
        end_time = datetime.datetime.now()
    end_date = datetime.datetime(end_time.year, end_time.month, end_time.day, 0, 0) + datetime.timedelta(days=1)

    begin_time = para["begin_time"]
    if begin_time is None:
        begin_time = end_time - datetime.timedelta(days=7)
    begin_date = datetime.datetime(begin_time.year, begin_time.month, begin_time.day, 0, 0)

    para["begin_date"] = begin_date
    para["end_date"] = end_date
    para["day_num"] = int((end_date - begin_date).total_seconds()/3600/24)
    hdf_path = para["ob_data"]["hdf_dir"] + "/" + para["hdf_file_name"]
    hdf_file_list = [hdf_path]
    para["ob_data"]["hdf_path"] = hdf_path
    sta_ob = creat_ob_dataset(para)
    operation = para["ob_data"]["operation"]
    operation_para = para["ob_data"]["operation_para"]
    if operation_para is None:
        operation_para = {}
    if operation is not None:
        sta_ob = operation(sta_ob,**operation_para)

    sta_fo_list = []
    models = para["fo_data"].keys()
    for model in models:
        hdf_path = para["fo_data"][model]["hdf_dir"] + "/" + para["hdf_file_name"]
        para["fo_data"][model]["hdf_path"] = hdf_path
        hdf_file_list.append(hdf_path)
        sta_fo = creat_fo_dataset(model,para)

        operation = para["fo_data"][model]["operation"]
        operation_para =  para["fo_data"][model]["operation_para"]
        if operation_para is None:
            operation_para = {}
        move_fo_time =  para["fo_data"][model]["move_fo_time"]

        if operation is not None:
            sta_fo = operation(sta_fo, **operation_para)
        if move_fo_time != 0:
            sta_fo = meteva.base.move_fo_time(sta_fo, move_fo_time)
        sta_fo_list.append(sta_fo)
    start = time.time()
    #print(sta_ob)
    #print(sta_fo_list)
    sta_all = meteva.base.combine_on_obTime_id(sta_ob,sta_fo_list)
    print(time.time() - start)
    output_file = para["output_dir"] + "/" + para["hdf_file_name"]
    meteva.base.creat_path(output_file)
    sta_all.to_hdf(output_file, "df")
    print("success combined data to " + output_file)




def prepare_dataset_without_combining(para):
    '''

    :param para: 根据配置参数从站点和网格数据中读取数据插值到指定站表上，在存储成hdf格式文件，然后从hdf格式文件中读取相应的文件合并成检验要的数据集合文件
    :return:
    '''

    # 全局参数预处理，站点列表的读取
    station = meteva.base.read_station(para["station_file"])
    station.iloc[:,-1] = para["defalut_value"]
    para["station"] = station

    #全局参数预处理，起止日期的处理
    #day_num = para["day_num"]
    end_time = para["end_time"]
    if end_time is None:
        end_time = datetime.datetime.now()
    end_date = datetime.datetime(end_time.year, end_time.month, end_time.day, 0, 0) + datetime.timedelta(days=1)

    begin_time = para["begin_time"]
    if begin_time is None:
        begin_time = end_time - datetime.timedelta(days=7)
    begin_date = datetime.datetime(begin_time.year, begin_time.month, begin_time.day, 0, 0)

    para["begin_date"] = begin_date
    para["end_date"] = end_date
    para["day_num"] = int((end_date - begin_date).total_seconds()/3600/24)

    elements = para["ob_data"].keys()
    for ele in elements:
        para1 = copy.deepcopy(para)
        hdf_path = para["ob_data"][ele]["hdf_dir"] + "/" + para["hdf_file_name"]
        para1["ob_data"] = para["ob_data"][ele]
        para1["ob_data"]["hdf_path"] = hdf_path
        creat_ob_dataset(para1,ele)

    models = para["fo_data"].keys()
    for model in models:
        hdf_path = para["fo_data"][model]["hdf_dir"] + "/" + para["hdf_file_name"]
        para["fo_data"][model]["hdf_path"] = hdf_path
        creat_fo_dataset(model,para)



def creat_fo_dataset(model,para):

    station = para["station"]
    interp = para["interp"]
    end_date = para["end_date"]
    begin_date = para["begin_date"]
    day_num = para["day_num"] + 1
    para_model = para["fo_data"][model]
    hdf_path = para_model["hdf_path"]
    dir_fo  =para_model["dir_fo"]
    read_method = para_model["read_method"]
    read_para =para_model["read_para"]
    if read_para is None:
        read_para = {}


    data0 = None
    if os.path.exists(hdf_path):
        data0 = pd.read_hdf(hdf_path, "df")

    hours = None
    if para_model["hour"] is not None:
        hours = np.arange(para_model["hour"][0],para_model["hour"][1]+1,para_model["hour"][2]).tolist()


    dtimes = None
    if para_model["dtime"] is not None:
        dtimes = np.arange(para_model["dtime"][0],para_model["dtime"][1]+1,para_model["dtime"][2]).tolist()

    sta_list = [] #用于收集所有数据
    exist_dtimes = {}
    if data0 is None:
        if hours is None:
            hours = np.arange(0, 24, 1).tolist()
        if dtimes is None:
            dtimes = np.arange(0, 721, 1).tolist()
    else:
        data_left = meteva.base.sele_by_para(data0, time_range=[begin_date, end_date])
        data_name0 = meteva.base.get_stadata_names(data_left)
        print(data_name0)
        if len(data_name0) == 2:
            data_name1 = [model + "_u", model + "_v"]
        else:
            data_name1 = [model]
        meteva.base.set_stadata_names(data_left, data_name1)

        #meteva.base.set_stadata_names(data_left,model)
        sta_list.append(data_left)
        #id0 = station["id"].values[0]
        #data_id0 = meteva.base.sele_by_para(data0, id=id0)
        #print(data_id0)

        grouped_dict = dict(list(data_left.groupby("time")))
        keys = grouped_dict.keys()
        exist_time_list = []
        for key in keys:
            time1 = meteva.base.time_tools.all_type_time_to_datetime(key)
            exist_time_list.append(time1)
            ehours = grouped_dict[time1].loc[:, "dtime"].values.tolist()
            exist_dtimes[time1] = ehours
            #valid_group_list_list.append([key])
            #sta_ob_and_fos_list.append(grouped_dict[key])


        #times = data_left.loc[:, "time"].values.tolist()
        #times = list(set(times))
        #times.sort()
        #exist_time_list = []
        #for i in range(len(times)):
        #    time1 = meteva.base.time_tools.all_type_time_to_datetime(times[i])
        #    exist_time_list.append(time1)
        #    data_id0_time0 = meteva.base.sele_by_para(data_left, time=time1)
        #    ehours = data_id0_time0.loc[:, "dtime"].values.tolist()
        #    exist_dtimes[time1] = ehours

        if hours is None:
            hours = []
            for time1 in exist_time_list:
                hours.append(time1.hour)
            hours = list(set(hours))
            hours.sort()
        if dtimes is None:
            dtimes = data_left.loc[:, "dtime"].values.tolist()
            dtimes = list(set(dtimes))
            dtimes.sort()
        if len(hours) == 0:
            hours = np.arange(0,24,1).tolist()
        if len(dtimes) == 0:
            dtimes = np.arange(0, 721, 1).tolist()


    #print(exist_dtimes)
    for dd in range(day_num):
        for hh in range(len(hours)):
            hour = hours[hh]
            time1 = end_date - datetime.timedelta(days=dd) + datetime.timedelta(hours=hour)
            if time1 > end_date or time1< begin_date:continue
            if para_model["time_type"] == "BT":
                file_time = time1
            else:
                file_time = time1 - datetime.timedelta(hours = 8)


            for dt in dtimes:
                #data_exist = False
                if time1 in exist_dtimes.keys():
                    exist_dtime = exist_dtimes[time1]
                    if dt in exist_dtime:
                        #data_exist = True
                        continue
                #if data_exist:continue
                path = meteva.base.get_path(dir_fo, file_time, dt)
                if os.path.exists(path):
                    try:
                        dat = read_method(path,**read_para)
                        if dat is not None:
                            if not isinstance(dat, pd.DataFrame):
                                dat = interp(dat, station)
                            else:
                                dat = meteva.base.put_stadata_on_station(dat,station)
                            meteva.base.set_stadata_coords(dat,time = time1,dtime = dt)
                            data_name0 = meteva.base.get_stadata_names(dat)
                            if len(data_name0) ==2:
                                data_name1 = [model +"_u",model+"_v"]
                            else:
                                data_name1 = [model]
                            meteva.base.set_stadata_names(dat,data_name1)
                            sta_list.append(dat)
                            print("success read data from " + path)
                        else:
                            print("fail read data from " + path)
                    except:
                        print("fail read data from " + path)
                else:
                    print(path +" does not exist")

    if(len(sta_list) == 0):
        print("there is not file data in " + dir_fo)
        return
    sta_all = pd.concat(sta_list, axis=0)
    if "level" not in read_para.keys():
        meteva.base.set_stadata_coords(sta_all, level=0)
    meteva.base.creat_path(hdf_path)
    sta_all.to_hdf(hdf_path, "df")
    print(hdf_path)
    return sta_all



def creat_ob_dataset(para,ele = "ob"):
    station = para["station"]
    data_name =ele
    day_num = para["day_num"] + 1
    end_date = para["end_date"]
    begin_date = para["begin_date"]

    hdf_path = para["ob_data"]["hdf_path"]
    dir_ob =para["ob_data"]["dir_ob"]
    read_method = para["ob_data"]["read_method"]
    read_para = para["ob_data"]["read_para"]
    if read_para is None:
        read_para = {}
    reasonable_value = para["ob_data"]["reasonable_value"]

    hours = None
    if para["ob_data"]["hour"] is not None:
        hours = np.arange(para["ob_data"]["hour"][0],para["ob_data"]["hour"][1]+1,para["ob_data"]["hour"][2]).tolist()

    exist_time_list = []
    sta_list = []
    data0 = None
    if os.path.exists(hdf_path):
        data0 = pd.read_hdf(hdf_path, "df")
    if data0 is None:
        if hours is None:
            hours = np.arange(0, 24, 1).tolist()
    else:
        data_left = meteva.base.sele_by_para(data0, time_range=[begin_date, end_date])
        data_name0 = meteva.base.get_stadata_names(data_left)
        if len(data_name0) == 1:
            meteva.base.set_stadata_names(data_left, data_name)
        sta_list.append(data_left)
        #id0 = station["id"].values[0]
        #data_id0 = meteva.base.sele_by_para(data0, id=id0)
        times = data_left.loc[:, "time"].values.tolist()
        times = list(set(times))
        times.sort()

        for i in range(len(times)):
            time1 = meteva.base.time_tools.all_type_time_to_datetime(times[i])
            exist_time_list.append(time1)
        if hours is None:
            hours = []
            for time1 in exist_time_list:
                hours.append(time1.hour)
            hours = list(set(hours))
            hours.sort()
        if len(hours) == 0:
            hours = np.arange(0,24,1).tolist()


    for dd in range(day_num):
        for hh in range(len(hours)):
            hour = hours[hh]
            time1 = end_date - datetime.timedelta(days=dd) + datetime.timedelta(hours=hour)
            if time1 > end_date or time1 < begin_date: continue
            if time1 in exist_time_list:
                continue
            if para["ob_data"]["time_type"] == "BT":
                file_time = time1
            else:
                file_time = time1 - datetime.timedelta(hours = 8)

            path = meteva.base.get_path(dir_ob, file_time)
            if os.path.exists(path):
                try:
                    dat = read_method(path,**read_para)
                    if dat is not None:
                        dat = meteva.base.fun.comp.put_stadata_on_station(dat,station)
                        if not isinstance(dat,pd.DataFrame):
                            interp = para["interp"]
                            dat = interp(dat,station)
                        if reasonable_value is not None:
                            dat = meteva.base.sele_by_para(dat,value=reasonable_value)
                        data_name0 = meteva.base.get_stadata_names(dat)
                        if len(data_name0) == 1:
                            meteva.base.set_stadata_names(dat,data_name)
                        meteva.base.set_stadata_coords(dat,time = time1)

                        sta_list.append(dat)
                    else:
                        print("fail read data from " + path)
                except:
                    print("fail read data from " + path)
            else:
                print(path +  "does not exist")
    sta_all = pd.concat(sta_list, axis=0)
    if "level" not in read_para.keys():
        meteva.base.set_stadata_coords(sta_all, level=0)
    meteva.base.creat_path(hdf_path)
    sta_all.to_hdf(hdf_path, "df")
    print(hdf_path)

    return sta_all



