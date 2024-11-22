import meteva
import numpy as np
import datetime
import copy
import time
import pandas as pd
import os



para_example= {
    "base_on":"obTime",
    "begin_time":datetime.datetime.now() - datetime.timedelta(days =7),
    "end_time":datetime.datetime.now(),
    "station_file":r"H:\task\other\202009-veri_objective_method\sta_info.m3",
    "defalut_value":0,
    "hdf_file_name":"last_week_data.h5",
    "interp": meteva.base.interp_gs_nearest,
    "how_fo":"outer",
    "time_type":"BT",
    "ob_data":{
        "dir_ob": r"\\10.20.22.27\rc\RAIN\rain0\YYYYMMDDHH.000",
        "hour":None,
        "read_method": meteva.base.io.read_stadata_from_micaps3,
        "read_para": {},
        "reasonable_value": [0, 1000],
        "operation":meteva.base.fun.sum_of_sta,
        "operation_para": {"used_coords": ["time"], "span": 24},
        "time_type": "BT",
    },
    "fo_data":{
        "ECMWF": {
            "dir_fo": r"S:\data\grid\ECMWF_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour":[8,20,12],
            "dtime":[0,240,12],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "reasonable_value": [0, 1000],
            "operation": meteva.base.fun.change,
            "operation_para": {"used_coords": "dtime", "delta": 24},
            "time_type": "BT",
            "move_fo_time": 12
        },

        "SCMOC": {
            "dir_fo": r"S:\data\grid\NWFD_SCMOC\RAIN03\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour": [8, 20,12],
            "dtime":[3,240,3],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "reasonable_value": [0, 1000],
            "operation": meteva.base.fun.sum_of_sta,
            "operation_para": {"used_coords": ["dtime"], "span": 24},
            "time_type": "BT",
            "move_fo_time": 0
        },
    },
    "output_dir":r"H:\test_data\output\mpd\application"
}

def prepare_dataset(para,recover = True):

    if "base_on" not in para.keys():
        para["base_on"] = "obTime"
    if "time_type" not in para.keys():
        para["time_type"] = "BT"



    if  para["base_on"] =="obTime":
        sta_all = prepare_dataset_on_obTime(para,recover=recover)

    else:
        sta_all = meteva.product.prepare_dataset_on_foTime(para,recover = recover)

    return sta_all



def prepare_dataset_without_combining(para,recover = True):
    on_obTime = "obTime"
    if "base_on" in para.keys():
        on_obTime = para["on_obTime"]

    if "time_type" not in para.keys():
        para["time_type"] = "BT"

    if on_obTime =="obTime":
        prepare_dataset_without_combining_on_obTime(para,recover=recover)

    else:
        meteva.product.prepare_dataset_without_combining_on_foTime(para,recover)



def prepare_dataset_on_obTime(para,recover = True):
    '''

    :param para: 根据配置参数从站点和网格数据中读取数据插值到指定站表上，在存储成hdf格式文件，然后从hdf格式文件中读取相应的文件合并成检验要的数据集合文件
    :return:
    '''
    if "dir_ob" in para["ob_data"].keys():

        # 全局参数预处理，站点列表的读取
        station = meteva.base.read_station(para["station_file"])
        station.iloc[:,-1] = para["defalut_value"]
        para["station"] = station
        #全局参数预处理，起止日期的处理
        #day_num = para["day_num"]
        end_time = para["end_time"]
        if end_time is None:
            end_time = datetime.datetime.now()
        #end_date = datetime.datetime(end_time.year, end_time.month, end_time.day, 0, 0) + datetime.timedelta(days=1)
        end_date = datetime.datetime(end_time.year, end_time.month, end_time.day, end_time.hour, 0)

        begin_time = para["begin_time"]
        if begin_time is None:
            begin_time = end_time - datetime.timedelta(days=7)
        begin_date = datetime.datetime(begin_time.year, begin_time.month, begin_time.day, 0, 0)

        hdf_filename = para["hdf_file_name"]
        filename1, type1 = os.path.splitext(hdf_filename)

        para["begin_date"] = begin_date
        para["end_date"] = end_date
        para["day_num"] = int((end_date - begin_date).total_seconds()/3600/24)
        if "hdf_dir" in para["ob_data"].keys():
            hdf_path = para["ob_data"]["hdf_dir"] + "/" + para["hdf_file_name"]
        else:
            hdf_path = para["output_dir"] +"/"+filename1+ "/ob_data/"+hdf_filename

        hdf_file_list = [hdf_path]
        para["ob_data"]["hdf_path"] = hdf_path
        sta_ob = creat_ob_dataset_on_obTime(para)
        operation = para["ob_data"]["operation"]
        operation_para = para["ob_data"]["operation_para"]
        if operation_para is None:
            operation_para = {}
        if operation is not None:
            sta_ob = operation(sta_ob,**operation_para)


        sta_fo_list = []
        models = para["fo_data"].keys()
        for model in models:
            if "hdf_dir" in para["fo_data"][model].keys():
                hdf_path = para["fo_data"][model]["hdf_dir"] + "/" + para["hdf_file_name"]
            else:
                hdf_path = para["output_dir"] + "/" + filename1 + "/fo_" + model + "/" + hdf_filename
            para["fo_data"][model]["hdf_path"] = hdf_path
            hdf_file_list.append(hdf_path)
            sta_fo = creat_fo_dataset_on_obTime(model,para)

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
        how_fo = "inner"
        if "how_fo" in para.keys():
            how_fo = para["how_fo"]
        sta_all = meteva.base.combine_on_obTime_id(sta_ob,sta_fo_list,how_fo=how_fo)
        if "hdf_dir" in para["ob_data"].keys():
            output_file = para["output_dir"]  + "/" + para["hdf_file_name"]
        else:
            output_file = para["output_dir"] +"/"+filename1+ "/" + para["hdf_file_name"]
        meteva.base.creat_path(output_file)
        if os.path.exists(output_file):
            os.remove(output_file)
        sta_all.to_hdf(output_file, "df")
        print("success combined data to " + output_file)
        return sta_all
    else:
        prepare_dataset_without_combining_on_obTime(para,recover = recover)
        return None

def prepare_dataset_without_combining_on_obTime(para,recover = True):
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
    hdf_filename = para["hdf_file_name"]
    filename1, type1 = os.path.splitext(hdf_filename)

    elements = para["ob_data"].keys()
    if "dir_ob" in elements:
        if "hdf_dir" in para["ob_data"].keys():
            hdf_path = para["ob_data"]["hdf_dir"] + "/" + para["hdf_file_name"]
        else:
            hdf_path = para["output_dir"] +"/"+filename1+ "/ob_data/"+hdf_filename

        para["ob_data"]["hdf_path"] = hdf_path
        creat_ob_dataset_on_obTime(para)
    else:
        for ele in elements:
            para1 = copy.deepcopy(para)
            if "hdf_dir" in para["ob_data"][ele].keys():
                hdf_path = para["ob_data"][ele]["hdf_dir"] + "/" + para["hdf_file_name"]
            else:
                hdf_path = para["output_dir"]  +"/"+filename1+ "/ob_" +ele+ "/"+hdf_filename

            para1["ob_data"] = para["ob_data"][ele]
            para1["ob_data"]["hdf_path"] = hdf_path
            creat_ob_dataset_on_obTime(para1,ele,recover = recover)

    models = para["fo_data"].keys()
    for model in models:
        if "hdf_dir" in para["fo_data"][model].keys():
            hdf_path = para["fo_data"][model]["hdf_dir"] + "/" + para["hdf_file_name"]
        else:
            hdf_path = para["output_dir"] + "/" + filename1 + "/fo_" + model + "/" + hdf_filename
        para["fo_data"][model]["hdf_path"] = hdf_path
        creat_fo_dataset_on_obTime(model,para)

def creat_fo_dataset_on_obTime(model,para):
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
    reasonable_value = para_model["reasonable_value"]
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

    gds_file_list = []
    is_gds = False
    if dir_fo is not None:
        if dir_fo.find("mdfs:") >= 0:
            dir1, gds_filename = os.path.split(dir_fo)
            dir1 = dir1.replace(">", "")
            gds_file_list = meteva.base.path_tools.get_gds_path_list_in_one_dir(dir1)
            is_gds = True

    if data0 is None:
        if hours is None:
            hours = np.arange(0, 24, 1).tolist()
        if dtimes is None:
            dtimes = np.arange(0, 721, 1).tolist()
    else:
        data_left = meteva.base.sele_by_para(data0, time_range=[begin_date, end_date])
        data_name0 = meteva.base.get_stadata_names(data_left)
        if len(data_name0) == 2:
            data_name1 = ["u_"+model , "v_"+model]
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
        dati_s = end_date  - datetime.timedelta(days=dd)
        dati_s = datetime.datetime(dati_s.year,dati_s.month,dati_s.day,0,0)
        for hh in range(len(hours)):
            hour = hours[hh]
            time1 =dati_s  + datetime.timedelta(hours=hour)

            if time1 > end_date or time1< begin_date:continue


            if para["time_type"] == para_model["time_type"]:
                file_time = time1
            else:
                if para["time_type"] == "BT":
                    #主程序是北京时，文件是世界时
                    file_time = time1 - datetime.timedelta(hours = 8)
                else:
                    #主程序是世界时，文件是北京时
                    file_time = time1 + datetime.timedelta(hours = 8)


            for dt in dtimes:
                #data_exist = False
                if time1 in exist_dtimes.keys():
                    exist_dtime = exist_dtimes[time1]
                    if dt in exist_dtime:
                        #data_exist = True
                        continue
                #if data_exist:continue
                if dir_fo is None:
                    dat = read_method(**read_para,time = file_time,dtime = dt)
                    if dat is not None:
                        if not isinstance(dat, pd.DataFrame):
                            dat = interp(dat, station)
                        else:
                            dat = meteva.base.put_stadata_on_station(dat, station)

                        if reasonable_value is not None:
                            dat = meteva.base.sele_by_para(dat, value=reasonable_value)

                        meteva.base.set_stadata_coords(dat, time=time1, dtime=dt)
                        data_name0 = meteva.base.get_stadata_names(dat)
                        if len(data_name0) == 2:
                            data_name1 = ["u_"+model , "v_"+model]
                        else:
                            data_name1 = [model]
                        meteva.base.set_stadata_names(dat, data_name1)
                        sta_list.append(dat)
                        print("success read data from " + str(read_para)+ str(file_time)+"."+str(dt))
                else:
                    file_exit = False
                    if is_gds:
                        path = meteva.base.get_path(dir_fo, file_time,dt)
                        if path in gds_file_list:
                            file_exit = True
                    else:
                        path = meteva.base.get_path(dir_fo, file_time,dt)
                        if os.path.exists(path) or path is None:
                            file_exit = True

                    if file_exit:
                    #if os.path.exists(path) or path is None:
                        try:
                            dat = read_method(path,**read_para)
                            if dat is not None:
                                if not isinstance(dat, pd.DataFrame):
                                    dat = interp(dat, station)
                                else:
                                    dat = meteva.base.put_stadata_on_station(dat,station)

                                if reasonable_value is not None:
                                    dat = meteva.base.sele_by_para(dat, value=reasonable_value)

                                meteva.base.set_stadata_coords(dat,time = time1,dtime = dt)
                                data_name0 = meteva.base.get_stadata_names(dat)
                                if len(data_name0) ==2:
                                    data_name1 = ["u_"+model , "v_"+model]
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
    if os.path.exists(hdf_path):
        os.remove(hdf_path)
    sta_all.to_hdf(hdf_path, "df")
    print(hdf_path)
    return sta_all

def creat_ob_dataset_on_obTime(para,ele = "ob",recover = True):
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
        if not recover:
            return data0
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


    gds_file_list = []
    is_gds = False
    if dir_ob is not None:
        if dir_ob.find("mdfs:") >= 0:
            dir1, gds_filename = os.path.split(dir_ob)
            gds_file_list = meteva.base.path_tools.get_gds_path_list_in_one_dir(dir1)
            if(len(gds_file_list) == 0):
                if dir1.find("HH")>=0:
                    for hh in hours:
                        dir2 = dir1.replace("HH","%02d"%hh)
                        gds_file_list2 = meteva.base.path_tools.get_gds_path_list_in_one_dir(dir2)
                        gds_file_list.extend(gds_file_list2)
            is_gds = True

    for dd in range(day_num):
        dati_s = end_date  - datetime.timedelta(days=dd)
        dati_s = datetime.datetime(dati_s.year,dati_s.month,dati_s.day,0,0)

        for hh in range(len(hours)):
            hour = hours[hh]
            #time1 = end_date - datetime.timedelta(days=dd) + datetime.timedelta(hours=hour)
            time1 = dati_s + datetime.timedelta(hours=hour)
            if time1 > end_date or time1 < begin_date: continue
            if time1 in exist_time_list:
                continue

            if para["time_type"] == para["ob_data"]["time_type"]:
                file_time = time1
            else:
                if para["time_type"] == "BT":
                    #主程序是北京时，文件是世界时
                    file_time = time1 - datetime.timedelta(hours = 8)
                else:
                    #主程序是世界时，文件是北京时
                    file_time = time1 + datetime.timedelta(hours = 8)

            if dir_ob is None:
                dat = read_method(**read_para, time=file_time)
                if dat is not None:
                    if not isinstance(dat, pd.DataFrame):
                        interp = para["interp"]
                        dat = interp(dat, station)
                    else:
                        dat = meteva.base.fun.comp.put_stadata_on_station(dat, station)
                    if reasonable_value is not None:
                        dat = meteva.base.sele_by_para(dat, value=reasonable_value)
                    data_name0 = meteva.base.get_stadata_names(dat)
                    if len(data_name0) == 1:
                        meteva.base.set_stadata_names(dat, data_name)
                    meteva.base.set_stadata_coords(dat, time=time1)
                    sta_list.append(dat)
                    print("success read data from " + str(read_para) + str(file_time))
            else:
                file_exit = False
                path = meteva.base.get_path(dir_ob, file_time)
                if is_gds:
                    if path in gds_file_list:
                        file_exit = True
                else:
                    if os.path.exists(path) or path is None:
                        file_exit = True
                if file_exit:
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
                            print("success read data from "+ path)
                        else:
                            print("fail read data from " + path)
                    except:
                        print("fail read data from " + path)
                else:
                    print(path +  "does not exist")
    if(len(sta_list)==0):return None
    sta_all = pd.concat(sta_list, axis=0)
    if "level" not in read_para.keys():
        meteva.base.set_stadata_coords(sta_all, level=0)

    meteva.base.creat_path(hdf_path)
    if os.path.exists(hdf_path):
        os.remove(hdf_path)
    sta_all.to_hdf(hdf_path, "df")
    #print(hdf_path)

    return sta_all


def rename_hdf_file(old_para,new_para):
    '''
    更改数据收集参数中的hdf文件名称时，涉及到多个中间文件。当需要更改文件名称时，通过该程序自动的完成所有文件的重命名
    :param old_hdf_filename:  更改前的文件名称
    :param para:  包含更改后文件名的运行参数
    :return:  不返还值
    '''
    import shutil
    # 更改观测的hdf文件
    old_hdf_filename = old_para["hdf_file_name"]
    new_hdf_filename = new_para["hdf_file_name"]
    filename1,type1 = os.path.splitext(new_hdf_filename)
    if "dir_ob" in old_para["ob_data"].keys():
        filename_old = old_para["ob_data"]["hdf_dir"] + "/"+old_hdf_filename
        filename_new = new_para["output_dir"] +"/"+filename1+ "/ob_data/"+new_hdf_filename
        meteva.base.creat_path(filename_new)
        try:
            shutil.move(filename_old,filename_new)
        except:
            print(filename_old+"移动失败")
    else:
        elements = old_para["ob_data"].keys()
        for ele in elements:
            filename_old = old_para["ob_data"][ele]["hdf_dir"] + "/" + old_hdf_filename
            filename_new = new_para["output_dir"]  +"/"+filename1+ "/ob_" +ele+ "/"+new_hdf_filename
            meteva.base.creat_path(filename_new)
            shutil.move(filename_old, filename_new)
    # 重命名预报的hdf文件
    elements = old_para["fo_data"].keys()
    for ele in elements:
        filename_old = old_para["fo_data"][ele]["hdf_dir"] + "/" + old_hdf_filename
        filename_new = new_para["output_dir"]  +"/"+filename1+ "/fo_" +ele+ "/"+new_hdf_filename
        meteva.base.creat_path(filename_new)
        shutil.move(filename_old, filename_new)
    return

if __name__ == "__main__":

    prepare_dataset(para_example)
