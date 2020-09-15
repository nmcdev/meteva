#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import datetime as datetime
import os as os
import numpy as np
from ..io import DataBlock_pb2
from ..io.GDS_data_service import GDSDataService
import re
import pathlib

#获取最新的路径


#获取最新的gds路径
def get_latest_gds_path(ip,port,dir,time,dtime,dt_cell = "hour",dt_step = 1,farthest = 240):
    dir1,filemodel = os.path.split(dir)
    file_list = get_gds_file_list_in_one_dir(ip,port,dir1)
    for ddt in range(0,farthest,dt_step):
        if dt_cell.lower() == "hour":
            time1 = time - datetime.timedelta(hours=ddt)
        elif dt_cell.lower() == "minute":
            time1 = time - datetime.timedelta(minutes=ddt)
        filename = get_path(filemodel, time1, dtime + ddt, dt_cell)
        if filename in file_list:
            path = dir1 + "/" + filename
            return path

#获取最新的路径
def get_latest_path(dir,time,dt,dt_cell = "hour",dt_step = 1, farthest = 240):
    for ddt in range(0,240,dt_step):
        if dt_cell.lower()=="hour":
            time1 = time - datetime.timedelta(hours=ddt)
        elif dt_cell.lower()=="minute":
            time1 = time - datetime.timedelta(minutes=ddt)

        path = get_path(dir,time1,dt + ddt,dt_cell)
        if(os.path.exists(path)):
            return path
    return None


#获取路径
def get_path(dir,time,dt = None,dt_cell = "hour"):
    '''
    根据路径通配形式返回路径
    :param dir:
    :param time:
    :param dt:
    :param dt_cell:
    :return:
    '''
    if(dir.find("*")<0):
        return get_path_without_star(dir,time,dt,dt_cell)
    else:
        dir_0,filename_0 = os.path.split(dir)
        dir_1 = get_path_without_star(dir_0,time,dt,dt_cell)
        filename_1 = get_path_without_star(filename_0,time,dt,dt_cell)
        patten = dir_1  +"\\"+ filename_1
        patten = patten.replace("\\","/")
        patten = patten.replace("*","\\S+")
        files = os.listdir(dir_1)
        for file in files:
            path = dir_1 + "/" + file
            path = path.replace("\\","/")
            match = re.match(patten,path)
            if match is not None:
                return path
    return None



def get_path_without_star(dir,time,dt = None,dt_cell = "hour"):
    '''
    :param dir:
    :param time:
    :param dt:
    :param dt_cell:
    :return:
    '''
    if(dt is not None):
        if not (isinstance(dt,np.int16) or isinstance(dt,np.int32) or type(dt) == type(1)):
            if(dt_cell.lower()=="hour"):
                dt = int(dt.total_seconds() / 3600)
            elif(dt_cell.lower()=="minute"):
                dt = int(dt.total_seconds() / 60)
            elif(dt_cell.lower()=="day"):
                dt = int(dt.total_seconds() / (24*3600))
            else:
                dt = int(dt.total_seconds())
    else:
        dt = 0
    cdt3 = '%03d' % dt
    cdt4 = '%04d' % dt
    dir1 = dir.replace("TTTT",cdt4).replace("TTT",cdt3)
    y4 = time.strftime("%Y")
    y2 = y4[2:]
    mo = time.strftime("%m")
    dd = time.strftime("%d")
    hh = time.strftime("%H")
    mi = time.strftime("%M")
    ss = time.strftime("%S")
    dir1 = dir1.replace("YYYY",y4).replace("YY",y2).replace("MM",mo).replace("DD",dd).replace("HH",hh).replace("FF",mi).replace("SS",ss)
    dir1 = dir1.replace(">","")
    return dir1

#创建路径
def creat_path(path):
    if path is not None:
        [dir,filename] = os.path.split(path)
        #if(not os.path.exists(dir)):
        #    os.makedirs(dir)
        pathlib.Path(dir).mkdir(parents=True,exist_ok=True)


#字符转换为datetime
def str_to_time(str0):
    return datetime.datetime.strptime(str0, '%Y%m%d%H%M')

#获取预报时效路径
def get_forecat_hour_of_path(path_model,path):
    ttt_index = path_model.find("TTT")
    if (ttt_index >= 0):
        ttt = int(path[ttt_index:ttt_index + 3])
    else:
        ttt = 0
    return ttt

#获取时间命名的路径
def get_time_of_path(path_model,path):

    yy_index = path_model.find("YYYY")
    if  yy_index < 0:
        yy_index = path_model.find("YY")
        if(yy_index <0):
            yy = 2000
        else:
            yy = int(path[yy_index: yy_index + 2])
    else:
        yy = int(path[yy_index: yy_index+4])

    mm_index = path_model.find("MM")
    if(mm_index >=0):
        mm = int(path[mm_index:mm_index+2])
    else:
        mm = 1

    dd_index = path_model.find("DD")
    if(dd_index>=0):
        dd = int(path[dd_index:dd_index + 2])
    else:
        dd = 1
    hh_index = path_model.find("HH")
    if(hh_index>=0):
        hh = int(path[hh_index:hh_index + 2])
    else:
        hh = 0
    ff_index = path_model.find("FF")
    if(ff_index>=0):
        ff = int(path[ff_index:ff_index + 2])
    else:
        ff = 0
    ss_index = path_model.find("SS")
    if(ss_index>=0):
        ss = int(path[ss_index:ss_index + 2])
    else:
        ss = 0
    return datetime.datetime(yy,mm,dd,hh,ff,ss)

#获取按照时间命名的文件夹名称
def get_dir_of_time(path_model,time):
    dir = os.path.split(get_path(path_model,time))[0]
    return dir

#获取按照时间命名的文件夹名称列表
def get_path_list_of_time(path_model,time):
    dir = get_dir_of_time(path_model,time) +"/"
    path_list = []
    if(os.path.exists(dir)):
        path_list = os.listdir(dir)
        for i in range(len(path_list)):
            path_list[i] = dir  + path_list[i]
    return path_list

#按照最新的时间命名文件路径
def get_time_nearest_path(path_model,time,max_seconds,path_list = None):
    if(path_list is None):
        path_list = get_path_list_of_time(path_model,time)
    dt_min = max_seconds
    nearest_path = None
    for path in path_list:
        time1 = get_time_of_path(path_model,path)
        dt = abs((time1 - time).total_seconds())
        if(dt < dt_min):
            dt_min = dt
            nearest_path = path
    return nearest_path

#按照上一个时效命名文件路径
def get_time_before_nearest_path(path_model,time,max_seconds,path_list = None):
    if(path_list is None):
        path_list = get_path_list_of_time(path_model,time)
    dt_min = max_seconds
    nearest_path = None
    for path in path_list:
        time1 = get_time_of_path(path_model,path)
        dt = (time - time1).total_seconds()
        if(dt < dt_min and dt >=0):
            dt_min = dt
            nearest_path = path
    return nearest_path

##按照下一个时效命名文件路径
def get_time_after_nearest_path(path_model,time,max_seconds,path_list = None):
    if(path_list is None):
        path_list = get_path_list_of_time(path_model,time)
    dt_min = max_seconds
    nearest_path = None
    for path in path_list:
        time1 = get_time_of_path(path_model,path)
        dt = (time1 - time).total_seconds()
        if(dt < dt_min  and dt >=0):
            dt_min = dt
            nearest_path = path
    return nearest_path

#以列表的形式返回根目录下所有文件的路径
def get_path_list_in_dir(root_dir,all_path = None):
    if not os.path.exists(root_dir):
        return []
    files = os.listdir(root_dir)
    if all_path is None:
        all_path = []
    for file in files:
        fi_d = os.path.join(root_dir,file)
        if os.path.isdir(fi_d):
            get_path_list_in_dir(fi_d,all_path)
        else:
            all_path.append(fi_d)

    return all_path

#返回根目录下nc格点文件的长名字
def get_path_of_grd_nc_longname(root_dir,time,dhour,nc_Fname,fhour_add):
    ruc_file = "{4}_IT_{0}_VT_{1}_FH_{2:0>3d}_AT_{3:0>3d}.nc".format(time.strftime("%Y%m%d%H"),
                                                                     (time + datetime.timedelta(hours=int(dhour))).strftime(
                                                                         "%Y%m%d%H"), dhour, fhour_add, nc_Fname)
    file = r"{0}\{1}\{2}".format(root_dir, time.strftime("%Y%m%d"), ruc_file)
    return file


def get_gds_file_list_in_one_dir(ip,port,dir):
    dir = dir.replace("mdfs:///", "")
    service = GDSDataService(ip, port)
    # 获得指定目录下的所有文件
    status, response = service.getFileList(dir)
    MappingResult = DataBlock_pb2.MapResult()
    file_list = []
    if status == 200:
        if MappingResult is not None:
            # Protobuf的解析
            MappingResult.ParseFromString(response)
            results = MappingResult.resultMap
            # 遍历指定目录
            for name_size_pair in results.items():
                if (name_size_pair[1] != 'D'):
                    file_list.append(name_size_pair[0])
    return file_list

def get_gds_all_dir(ip,port,path,all_path,service = None):
    # 初始化GDS客户端

    if service is None:
        service = GDSDataService(ip, port)
    # 获得指定目录下的所有文件
    path = path.replace("mdfs:///", "")
    status, response = service.getFileList(path)
    MappingResult = DataBlock_pb2.MapResult()
    if status == 200:
        if MappingResult is not None:
            # Protobuf的解析
            MappingResult.ParseFromString(response)
            results = MappingResult.resultMap
            # 遍历指定目录
            contain_dir = False
            for name_size_pair in results.items():
                if (name_size_pair[1] == 'D'):
                    contain_dir = True
                    path1 = '%s%s%s' % (path, "/" , name_size_pair[0])
                    if(path1[0:1] == "/"):
                        path1 = path1[1:]
                    if(path1[0:1] == "/"):
                        path1 = path1[1:]
                    get_gds_all_dir(ip,port,path1,all_path,service)
                    #print(name_size_pair[0])
            if(not contain_dir):
                all_path.append(path)



def get_dati_of_path(path):
    try:
        dir,filename = os.path.split(path)
        filename0 = os.path.splitext(filename)[0]
        a = int(filename0[0:2])
        b = int(filename0[2:4])
        if a ==20:
            if b >12:
                pass
            else:
                filename0 = "20" + filename0
        elif a == 19:
            if b >12:
                pass
            else:
                filename0 = "20" + filename0
        else:
            filename0 = "20" + filename0

        dati = str_to_time(filename0)
        return dati
    except:
        return None

#以列表的形式返回根目录下所有文件的路径
def get_during_path_list_in_dir(root_dir,all_path = None,start = None,end = None):
    start_time = None
    if start is None:
        start_time = datetime.datetime(1900,1,1,0,0)
    else:
        start_time = start
    if end is None:
        end_time = datetime.datetime.now()
    else:
        end_time = end
    time_compair = False
    if start is not None or end is not None:
        time_compair = True

    if not os.path.exists(root_dir):
        return []
    files = os.listdir(root_dir)
    if all_path is None:
        all_path = []
    for file in files:
        fi_d = os.path.join(root_dir,file)
        if os.path.isdir(fi_d):
            if time_compair:
                dati = get_dati_of_path(fi_d)
                if dati is None:
                    get_during_path_list_in_dir(fi_d, all_path, start, end)
                else:
                    if dati >= start_time and dati <= end_time:
                        get_during_path_list_in_dir(fi_d,all_path,start,end)
            else:
                get_during_path_list_in_dir(fi_d, all_path, start, end)
        else:
            all_path.append(fi_d)
    return all_path