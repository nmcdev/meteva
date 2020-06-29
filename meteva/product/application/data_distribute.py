import datetime
import meteva
import shutil
import os
import numpy as np


para_list_example = [
    {
        "input":r"O:\data\grid\GRAPES_GFS\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "output":r"L:\luoqi\GRAPES_GFS\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "start":datetime.datetime(2020,3,1,8,0),
        "end":datetime.datetime(2020,6,1,8,0),
        "hour_range":[8,21,12],
        "dh_range":[3,241,3],
        "recover":False
    },

    {
        "input": r"O:\data\grid\ECMWF_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "output": r"L:\luoqi\ECMWF_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "start": datetime.datetime(2020, 3, 1, 8, 0),
        "end": datetime.datetime(2020, 6, 1, 8, 0),
        "hour_range": [8, 21, 12],
        "dh_range": [3, 241, 3],
        "recover": False
    },

    {
        "input": r"O:\data\grid\NCEP_GFS_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "output": r"L:\luoqi\NCEP_GFS_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "start": datetime.datetime(2020, 3, 1, 8, 0),
        "end": datetime.datetime(2020, 6, 1, 8, 0),
        "hour_range": [8, 21, 12],
        "dh_range": [3, 241, 3],
        "recover": False
    },

    {
        "input": r"O:\data\grid\SHANGHAI_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "output": r"L:\luoqi\SHANGHAI_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "start": datetime.datetime(2020, 3, 1, 8, 0),
        "end": datetime.datetime(2020, 6, 1, 8, 0),
        "hour_range": [0, 24, 1],
        "dh_range": [0, 25, 1],
        "recover": False
    },

    {
        "input": r"O:\data\grid\GRAPES_MESO_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "output": r"L:\luoqi\GRAPES_MESO_HR\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "start": datetime.datetime(2020, 3, 1, 8, 0),
        "end": datetime.datetime(2020, 6, 1, 8, 0),
        "hour_range": [2, 24, 3],
        "dh_range": [0, 85, 1],
        "recover": False
    },

    {
        "input": r"O:\data\grid\GRAPES_3KM\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "output": r"L:\luoqi\GRAPES_3KM\APCP\YYYYMMDD\YYMMDDHH.TTT.nc",
        "start": datetime.datetime(2020, 3, 1, 8, 0),
        "end": datetime.datetime(2020, 6, 1, 8, 0),
        "hour_range": [2, 24, 3],
        "dh_range": [0, 37, 1],
        "recover": False
    },

]




def copy_data_file(para_list):
    for para in para_list:
        time0 = para["start"]
        time1 = datetime.datetime(time0.year,time0.month,time0.day,0,0)
        hour_list =  np.arange(para["hour_range"][0],para["hour_range"][1],para["hour_range"][2]).tolist()
        dh_list = np.arange(para["dh_range"][0], para["dh_range"][1], para["dh_range"][2]).tolist()
        recover = para["recover"]
        while time1 <= para["end"]:
            for hour in hour_list:
                time2 = time1 +datetime.timedelta(hours=hour)
                for dh in dh_list:
                    path_out = meteva.base.get_path(para["output"],time2,dh)
                    if recover or not os.path.exists(path_out):
                        path_in = meteva.base.get_path(para["input"],time2,dh)
                        if os.path.exists(path_in):
                            meteva.base.creat_path(path_out)
                            shutil.copyfile(path_in,path_out)
            time1 = time1 + datetime.timedelta(hours=24)


def copy_during_data_file(root_in,root_out,start = None,end = None,recover = False):
    path_list = meteva.base.path_tools.get_during_path_list_in_dir(root_in,None,start,end)
    for path in path_list:
        path_copy = path.replace(root_in,root_out)
        if not os.path.exists(path_copy) or recover:
            meteva.base.path_tools.creat_path(path_copy)
            shutil.copy(path,path_copy)

if __name__ == '__main__':
    #copy_data_file(para_list1)
    pass
