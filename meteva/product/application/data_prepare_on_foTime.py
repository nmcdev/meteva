import meteva
import numpy as np
import datetime
import copy
import time
import pandas as pd
import os
import traceback
from multiprocessing import Process, Queue, Event
import multiprocessing

para_example= {
    "base_on":"foTime",
    "begin_time": datetime.datetime(2024,7,29,12),
    "end_time": datetime.datetime(2024,7,30,12),
    "time_type": "UT",
    "station_file":meteva.base.station_国家站,
    "defalut_value":999999,
    "interp": meteva.base.interp_gs_nearest,
    "recover":True,
    "cpu":1,
    "hdf_file_name":"test.h5",
    "ob_data":{
        "dir_ob": r"/g6/op_vfy/MUVOS/obs/station/sl/rainnew/rain_01/YYYYMM/rain01_YYYYMMDDHH.dat",
        "hour": None,
        "read_method": meteva.base.read_stadata_from_csv,
        "read_para": {"columns":["id","lat","lon","OBS"],"member_list":["OBS"]},
        "reasonable_value": [0, 1000],
        "operation":meteva.base.sum_of_sta,
        "operation_para":{"used_coords" : ["time"],"span" : 3},
        "time_type": "UT",
    },
    "fo_data":{
        "CTRL": {
            "dir_fo":  r"/g6/wangdan/2025-work/NEW/CTRL/REGION/MCV_results/YYYYMMDDHH/post.ctl",
            "hour": [12, 12, 24],
            "dtime": [0, 24, 3],
            "reasonable_value": [0, 1000],
            "read_method": meteva.base.read_griddata_from_ctl,
            "read_para": {"value_name":"rain", "add_block_head_tail":True,"dtime_dim" : "tdef","endian" : "<"},
            "operation": meteva.base.change,
            "operation_para": {"delta":3,"used_coords":"dtime"},
            "move_fo_time": 0,
            "time_type": "UT",
        },
        "data2":{
            "dir_fo":  r"/g6/wangdan/2025-work/NEW/data2/DATABANK/REGION/MCV_results/YYYYMMDDHH/post.ctl",
            "hour": [12, 12, 24],
            "dtime": [0, 24, 3],
            "reasonable_value": [0, 1000],
            "read_method": meteva.base.read_griddata_from_ctl,
            "read_para": {"value_name":"rain", "add_block_head_tail":True,"dtime_dim" : "tdef","endian" : "<"},
            "operation": meteva.base.change,
            "operation_para": {"delta": 3, "used_coords": "dtime"},
            "move_fo_time": 0,
            "time_type": "UT",
        },
    },
    "output_dir":r"/g5/liuch/result"
}



def prepare_dataset_on_foTime(para,recover = True):
    '''

    :param para: 根据配置参数从站点和网格数据中读取数据插值到指定站表上，在存储成hdf格式文件，然后从hdf格式文件中读取相应的文件合并成检验要的数据集合文件
    :return:
    '''
    if "dir_ob" in para["ob_data"].keys():

        # 全局参数预处理，站点列表的读取
        station = meteva.base.read_station(para["station_file"])
        station.iloc[:,-1] = para["defalut_value"]
        para["station"] = station

        if "hdf_file_name" in para.keys():
            hdf_filename = para["hdf_file_name"]
            filename1, type1 = os.path.splitext(hdf_filename)
            if "hdf_dir" in para["ob_data"].keys():
                hdf_path = para["ob_data"]["hdf_dir"] + "/" + para["hdf_file_name"]
            else:
                hdf_path = para["output_dir"] +"/"+filename1+ "/ob_data/"+hdf_filename
        else:
            hdf_path = None

        #找到最大的时效
        max_dtime = 0
        models = para["fo_data"].keys()
        for model in models:
            max1 = para["fo_data"][model]["dtime"][1]
            if max1 >max_dtime:
                max_dtime = max1
        para["max_dtime"] = max_dtime

        hdf_file_list = [hdf_path]
        para["ob_data"]["hdf_path"] = hdf_path
        sta_ob = creat_ob_dataset_on_foTime(para)
        operation = para["ob_data"]["operation"]
        operation_para = para["ob_data"]["operation_para"]
        if operation_para is None:
            operation_para = {}
        if operation is not None:
            sta_ob = operation(sta_ob,**operation_para)


        sta_fo_list = []

        for model in models:
            if "hdf_file_name" in para.keys():
                if "hdf_dir" in para["fo_data"][model].keys():
                    hdf_path = para["fo_data"][model]["hdf_dir"] + "/" + para["hdf_file_name"]
                else:
                    hdf_path = para["output_dir"] + "/" + filename1 + "/fo_" + model + "/" + hdf_filename
            else:
                hdf_path = None
            para["fo_data"][model]["hdf_path"] = hdf_path
            hdf_file_list.append(hdf_path)
            sta_fo = creat_fo_dataset_on_foTime(model,para)

            operation = para["fo_data"][model]["operation"]
            operation_para =  para["fo_data"][model]["operation_para"]
            if operation_para is None:
                operation_para = {}

            if operation is not None:
                sta_fo = operation(sta_fo, **operation_para)

            sta_fo_list.append(sta_fo)
        how_fo = "inner"
        if "how_fo" in para.keys():
            how_fo = para["how_fo"]
        sta_all = meteva.base.combine_on_obTime_id(sta_ob,sta_fo_list,how_fo=how_fo)
        if para["output_dir"] is not None:
            if "hdf_dir" in para["ob_data"].keys():
                output_file = para["output_dir"]  + "/" + para["hdf_file_name"]
            else:
                output_file = para["output_dir"] +"/"+filename1+ "/" + para["hdf_file_name"]
            meteva.base.creat_path(output_file)
            if os.path.exists(output_file):
                os.remove(output_file)
            file_type = output_file.split(".")[1]
            if file_type == "parquet":
                sta_all.to_parquet(output_file)
            else:
                sta_all.to_hdf(output_file, "df")
            print("success combined data to " + output_file)

        return sta_all

    else:
        prepare_dataset_without_combining_on_foTime(para,recover = recover)
        return None

def prepare_dataset_without_combining_on_foTime(para,recover = True):
    '''

    :param para: 根据配置参数从站点和网格数据中读取数据插值到指定站表上，在存储成hdf格式文件，然后从hdf格式文件中读取相应的文件合并成检验要的数据集合文件
    :return:
    '''

    # 找到最大的时效
    max_dtime = 0
    models = para["fo_data"].keys()
    for model in models:
        max1 = para["fo_data"][model]["dtime"][1]
        if max1 > max_dtime:
            max_dtime = max1
    para["max_dtime"] = max_dtime

    # 全局参数预处理，站点列表的读取
    station = meteva.base.read_station(para["station_file"])
    station.iloc[:,-1] = para["defalut_value"]
    para["station"] = station


    hdf_filename = para["hdf_file_name"]
    filename1, type1 = os.path.splitext(hdf_filename)

    elements = para["ob_data"].keys()
    if "dir_ob" in elements:
        if "hdf_dir" in para["ob_data"].keys():
            hdf_path = para["ob_data"]["hdf_dir"] + "/" + para["hdf_file_name"]
        else:
            hdf_path = para["output_dir"] +"/"+filename1+ "/ob_data/"+hdf_filename

        para["ob_data"]["hdf_path"] = hdf_path
        creat_ob_dataset_on_foTime(para)
    else:
        for ele in elements:
            para1 = copy.deepcopy(para)
            if "hdf_dir" in para["ob_data"][ele].keys():
                hdf_path = para["ob_data"][ele]["hdf_dir"] + "/" + para["hdf_file_name"]
            else:
                hdf_path = para["output_dir"]  +"/"+filename1+ "/ob_" +ele+ "/"+hdf_filename

            para1["ob_data"] = para["ob_data"][ele]
            para1["ob_data"]["hdf_path"] = hdf_path
            creat_ob_dataset_on_foTime(para1,ele,recover = recover)

    models = para["fo_data"].keys()
    for model in models:
        if "hdf_dir" in para["fo_data"][model].keys():
            hdf_path = para["fo_data"][model]["hdf_dir"] + "/" + para["hdf_file_name"]
        else:
            hdf_path = para["output_dir"] + "/" + filename1 + "/fo_" + model + "/" + hdf_filename
        para["fo_data"][model]["hdf_path"] = hdf_path
        creat_fo_dataset_on_foTime(model,para)



class fo_data_loader():
    def __init__(self,model,para,cpu):
        super().__init__()
        self.model = model
        self.para = para

        self.station = para["station"]
        self.interp = para["interp"]

        self.end_time = para["end_time"]
        self.begin_time = para["begin_time"]

        self.para_model = para["fo_data"][model]
        self.hdf_path = self.para_model["hdf_path"]
        self.dir_fo  =self.para_model["dir_fo"]
        self.read_method = self.para_model["read_method"]
        self.read_para =self.para_model["read_para"]
        self.reasonable_value = self.para_model["reasonable_value"]
        self.move_fo_time = self.para_model["move_fo_time"]

        self.gds_file_list = []
        self.is_gds = False
        if self.dir_fo is not None:
            if self.dir_fo.find("mdfs:") >= 0:
                dir1, gds_filename = os.path.split(self.dir_fo)
                dir1 = dir1.replace(">", "")
                self.gds_file_list = meteva.base.path_tools.get_gds_path_list_in_one_dir(dir1)
                self.is_gds = True

        if self.read_para is None:
            self.read_para = {}

        if "recover" in para.keys():
            recover = para["recover"]
        else:
            recover = False

        data0 = None
        if not recover:
            if self.hdf_path is not None:
                if os.path.exists(self.hdf_path):
                    data0 = pd.read_hdf(self.hdf_path, "df")

        hours = None
        if self.para_model["hour"] is not None:
            hours = np.arange(self.para_model["hour"][0],self.para_model["hour"][1]+1,self.para_model["hour"][2]).tolist()

        dtimes = None
        if self.para_model["dtime"] is not None:
            dtimes = np.arange(self.para_model["dtime"][0],self.para_model["dtime"][1]+1,self.para_model["dtime"][2]).tolist()

        exist_dtimes = {}

        self.sta_list = []
        if data0 is None:
            if hours is None:
                hours = np.arange(0, 24, 1).tolist()
            if dtimes is None:
                dtimes = np.arange(0, 721, 1).tolist()
        else:
            data_left = meteva.base.sele_by_para(data0, time_range=[self.begin_time, self.end_time])
            data_name0 = meteva.base.get_stadata_names(data_left)
            if len(data_name0) == 2:
                data_name1 = ["u_"+model , "v_"+model]
            else:
                data_name1 = [model]
            meteva.base.set_stadata_names(data_left, data_name1)

            #meteva.base.set_stadata_names(data_left,model)
            self.sta_list.append(data_left)
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

        self.count_total = multiprocessing.Array('i', range(1))

        self.task_queue = Queue()
        self.loaded_queue = Queue()
        #self.finished_squeue = Queue()

        self.w_list = []
        for i in range(cpu):
            w = Process(target=self.load_one_filed)
            w.daemon = True
            w.start()
            self.w_list.append(w)



        time1 = self.begin_time
        count = 0
        while time1 <= self.end_time:
            if time1.hour in hours:

                if para["time_type"] == self.para_model["time_type"]:
                    file_time = time1
                else:
                    if para["time_type"] == "BT":
                        #主程序是北京时，文件是世界时
                        file_time = time1 - datetime.timedelta(hours = 8)
                    else:
                        #主程序是世界时，文件是北京时
                        file_time = time1 + datetime.timedelta(hours = 8)

                file_time_moved = file_time - datetime.timedelta(hours = self.move_fo_time)

                for dt in dtimes:
                    #data_exist = False
                    if time1 in exist_dtimes.keys():
                        exist_dtime = exist_dtimes[time1]
                        if dt in exist_dtime:
                            #data_exist = True
                            continue
                    dt_moved = dt + self.move_fo_time
                    self.task_queue.put((file_time_moved,dt_moved,time1,dt))
                    count += 1

            time1 += datetime.timedelta(hours = 1)

        if count ==0:
            self.count_total[0] = -1
        else:
            self.count_total[0] = count


    def load_one_filed(self):
        # if data_exist:continue
        while True:  #进程是常驻的
            file_time_moved,dt_moved,time1,dt = self.task_queue.get()

            if self.dir_fo is None:
                dat = self.read_method(**self.read_para, time=file_time_moved, dtime=dt_moved)
                if dat is not None:
                    if not isinstance(dat, pd.DataFrame):
                        dat = self.interp(dat, self.station)
                    else:
                        dat = meteva.base.put_stadata_on_station(dat, self.station)

                    if self.reasonable_value is not None:
                        dat = meteva.base.sele_by_para(dat, value=self.reasonable_value)

                    meteva.base.set_stadata_coords(dat, time=time1, dtime=dt)
                    data_name0 = meteva.base.get_stadata_names(dat)
                    if len(data_name0) == 2:
                        data_name1 = ["u_" + self.model, "v_" + self.model]
                    else:
                        data_name1 = [self.model]
                    meteva.base.set_stadata_names(dat, data_name1)

                    self.loaded_queue.put(dat)
                    print("success read data from " + str(self.read_para) + str(file_time_moved) + "." + str(dt_moved))
            else:
                file_exit = False
                if self.is_gds:
                    path = meteva.base.get_path(self.dir_fo, file_time_moved, dt_moved)
                    if path in self.gds_file_list:
                        file_exit = True
                else:
                    path = meteva.base.get_path(self.dir_fo, file_time_moved, dt_moved)
                    if os.path.exists(path) or path is None:
                        file_exit = True

                if file_exit:
                    # if os.path.exists(path) or path is None:
                    try:
                        dat = self.read_method(path, time=file_time_moved, dtime=dt_moved, **self.read_para)
                        if dat is not None:
                            if not isinstance(dat, pd.DataFrame):
                                dat = self.interp(dat, self.station)
                            else:
                                dat = meteva.base.put_stadata_on_station(dat, self.station)

                            if self.reasonable_value is not None:
                                dat = meteva.base.sele_by_para(dat, value=self.reasonable_value)

                            meteva.base.set_stadata_coords(dat, time=time1, dtime=dt)
                            data_name0 = meteva.base.get_stadata_names(dat)
                            if len(data_name0) == 2:
                                data_name1 = ["u_" + self.model, "v_" + self.model]
                            else:
                                data_name1 = [self.model]
                            meteva.base.set_stadata_names(dat, data_name1)

                            self.loaded_queue.put(dat)
                            print("success read data from " + path)
                        else:
                            self.loaded_queue.put(None)
                            print("fail read data from " + path)
                    except:
                        self.loaded_queue.put(None)
                        exstr = traceback.format_exc()
                        print(exstr)
                        print("fail read data from " + path)
                else:
                    self.loaded_queue.put(None)
                    print(path + " does not exist")

    def gather_data(self):
        count = 0
        stop_time = time.time()
        while True:
            if not self.loaded_queue.empty():
                sta = self.loaded_queue.get()
                count += 1
                self.sta_list.append(sta)
                stop_time = time.time()

                if self.count_total[0] > 0 and count == self.count_total[0]:
                    print(f"共加载{count}个场")

                    #self.finished_squeue.put(True)
                    break
            else:
                time.sleep(0.01)  # 如果队列为空，等待0.01秒后再检查

                if self.count_total[0] >0:
                    if count == self.count_total[0]:
                        print(f"完成加载，共{count}个场")
                        #self.finished_squeue.put(True)
                        break

                    if time.time() - stop_time > 3600:  #有可能个别数据出现了bug,导致总数量达不到预期，此时等待600秒后退出
                        print("超时退出")
                        break

                if self.count_total[0] <0:
                    print(f"没有需要检验的场")
                    break


        for w in self.w_list:
            w.terminate()  # 发送终止信号
            w.join()       # 等待进程资源释放（避免僵尸进程）
        return self.sta_list


def creat_fo_dataset_on_foTime(model,para):

    if "cpu" in para.keys():
        cpu = para["cpu"]
    else:
        cpu = 1
    para_model = para["fo_data"][model]
    read_para =para_model["read_para"]
    hdf_path = para_model["hdf_path"]
    dir_fo  =para_model["dir_fo"]
    if "recover" in para.keys():
        recover = para["recover"]
    else:
        recover = False

    sta_list = [] #用于收集所有数据
    if cpu >1:
        loader = fo_data_loader(model,para,cpu)
        sta_list = loader.gather_data()
    else:

        station = para["station"]
        interp = para["interp"]

        end_time = para["end_time"]
        begin_time = para["begin_time"]


        read_method = para_model["read_method"]

        reasonable_value = para_model["reasonable_value"]
        move_fo_time = para_model["move_fo_time"]
        if read_para is None:
            read_para = {}
        data0 = None
        if not recover:
            if hdf_path is not None:
                if os.path.exists(hdf_path):
                    data0 = pd.read_hdf(hdf_path, "df")

        hours = None
        if para_model["hour"] is not None:
            hours = np.arange(para_model["hour"][0],para_model["hour"][1]+1,para_model["hour"][2]).tolist()


        dtimes = None
        if para_model["dtime"] is not None:
            dtimes = np.arange(para_model["dtime"][0],para_model["dtime"][1]+1,para_model["dtime"][2]).tolist()


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
            data_left = meteva.base.sele_by_para(data0, time_range=[begin_time, end_time])
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
        time1 = begin_time
        while time1 <= end_time:
            if time1.hour in hours:

                if para["time_type"] == para_model["time_type"]:
                    file_time = time1
                else:
                    if para["time_type"] == "BT":
                        #主程序是北京时，文件是世界时
                        file_time = time1 - datetime.timedelta(hours = 8)
                    else:
                        #主程序是世界时，文件是北京时
                        file_time = time1 + datetime.timedelta(hours = 8)

                file_time_moved = file_time - datetime.timedelta(hours = move_fo_time)

                for dt in dtimes:
                    #data_exist = False
                    if time1 in exist_dtimes.keys():
                        exist_dtime = exist_dtimes[time1]
                        if dt in exist_dtime:
                            #data_exist = True
                            continue
                    dt_moved = dt + move_fo_time
                    if dir_fo is None:
                        dat = read_method(**read_para, time=file_time_moved, dtime=dt_moved)
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
                                data_name1 = ["u_" + model, "v_" + model]
                            else:
                                data_name1 = [model]
                            meteva.base.set_stadata_names(dat, data_name1)
                            sta_list.append(dat)
                            print("success read data from " + str(read_para) + str(file_time_moved) + "." + str(dt_moved))
                    else:
                        file_exit = False
                        if is_gds:
                            path = meteva.base.get_path(dir_fo, file_time_moved, dt_moved)
                            if path in gds_file_list:
                                file_exit = True
                        else:
                            path = meteva.base.get_path(dir_fo, file_time_moved, dt_moved)
                            if os.path.exists(path) or path is None:
                                file_exit = True

                        if file_exit:
                            # if os.path.exists(path) or path is None:
                            try:
                                dat = read_method(path, time=file_time_moved, dtime=dt_moved, **read_para)
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
                                        data_name1 = ["u_" + model, "v_" + model]
                                    else:
                                        data_name1 = [model]
                                    meteva.base.set_stadata_names(dat, data_name1)
                                    sta_list.append(dat)
                                    print("success read data from " + path)
                                else:
                                    print("fail read data from " + path)
                            except:
                                exstr = traceback.format_exc()
                                print(exstr)
                                print("fail read data from " + path)
                        else:
                            print(path + " does not exist")


            time1 += datetime.timedelta(hours = 1)


    if(len(sta_list) == 0):
        print("there is not file data in " + dir_fo)
        return
    sta_all = pd.concat(sta_list, axis=0)
    if "level" not in read_para.keys():
        meteva.base.set_stadata_coords(sta_all, level=0)

    if hdf_path is not None:
        meteva.base.creat_path(hdf_path)
        if os.path.exists(hdf_path):
            os.remove(hdf_path)

        file_type = hdf_path.split(".")[1]
        if file_type == "parquet":
            sta_all.to_parquet(hdf_path)
        else:
            sta_all.to_hdf(hdf_path, "df")
        print(hdf_path)
    return sta_all

def creat_ob_dataset_on_foTime(para,ele = "ob",recover = True):
    max_dtime = para["max_dtime"]
    station = para["station"]
    data_name =ele
    #day_num = para["day_num"] + 1 + int(max_dtime/24)
    #end_date = para["end_date"] + datetime.timedelta(hours=max_dtime)
    #begin_date = para["begin_date"]

    begin_time = meteva.base.all_type_time_to_datetime(para["begin_time"])
    end_time = meteva.base.all_type_time_to_datetime(para["end_time"]) + datetime.timedelta(hours=max_dtime)

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

    if hdf_path is not None:
        if os.path.exists(hdf_path):
            data0 = pd.read_hdf(hdf_path, "df")
            if not recover:
                return data0
    if data0 is None:
        if hours is None:
            hours = np.arange(0, 24, 1).tolist()
    else:
        data_left = meteva.base.sele_by_para(data0, time_range=[para["begin_time"], para["end_time"]])
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


    time1 = begin_time
    while time1 <= end_time:
        if time1.hour in hours:
            if time1 not in exist_time_list:
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
                            dat = read_method(path,time = file_time,**read_para)
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
                            exstr = traceback.format_exc()
                            print(exstr)
                            print("fail read data from " + path)
                    else:
                        print(path +  "does not exist")

        time1 += datetime.timedelta(hours=1)


    if(len(sta_list)==0):return None
    sta_all = pd.concat(sta_list, axis=0)
    if "level" not in read_para.keys():
        meteva.base.set_stadata_coords(sta_all, level=0)

    if hdf_path is not None:
        meteva.base.creat_path(hdf_path)
        if os.path.exists(hdf_path):
            os.remove(hdf_path)

        file_type = hdf_path.split(".")[1]
        if file_type == "parquet":
            sta_all.to_parquet(hdf_path)
        else:
            sta_all.to_hdf(hdf_path, "df")
        print(hdf_path)

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

    #prepare_dataset_on_foTime(para_example)
    prepare_dataset_without_combining_on_foTime(para_example)
