import copy
import math
import pathlib
import meteva
import datetime
import pandas as pd
import os
import numpy as np
import  time


def read_ob_wind(path):
    speed = meteva.base.read_stadata_from_micaps1_2_8(path,column=meteva.base.m2_element_column.风速)
    angle = meteva.base.read_stadata_from_micaps1_2_8(path,column=meteva.base.m2_element_column.风向)
    if speed is not None and angle is not None:
        speed = meteva.base.sele_by_para(speed,value=[0,100])
        wind = meteva.base.speed_angle_to_wind(speed,angle)
        return wind
    else:
        return None


para_example= {
    "base_on": "foTime",
    "mid_method": meteva.method.na_uv,  # 统计检验的总量计算函数，
    "grade_list": None,  # 二分类检验所需的等级参数
    "compare": None,  # 二分类检验所需的对比方式参数
    "begin_time":datetime.datetime(2024,9,1,8),
    "end_time":datetime.datetime(2024,9,3,20),
    "time_type":"BT",  # 最终检验结果呈现时，采用北京时还是世界时，UT代表世界时，BT代表北京时
    "time_step": 12,  # 起报时间间隔
    "middle_result_path": r"H:\test_data\output\mps\na.h5",  #检验中间量数据的存储路径
    "station_file":meteva.base.station_国家站,  #检验站点表的存储路径
    "defalut_value":meteva.base.IV,
    "interp": meteva.base.interp_gs_nearest,
    "recover":False,    #False表示保留已经收集好的中间量，补齐未收集的数据，True表示删除已有的统计结果文件，重新开始收集
    "cpu":6,
    "ob_data":{
        "dir_ob": r"\\10.20.22.27\rc\WIND\w2mi0\YYYYMMDDHH.000", # 实况场数据路径
        "hour":[8,20,12],
        "read_method": read_ob_wind,    #读取数据的函数
        "read_para": {},                          #读取数据的函数参数
        "reasonable_value": None,
        "operation":None,  #实况数据读取后处理函数
        "operation_para": {},  #实况数据读取后处理参数
        "time_type": "BT",  # 数据文件中的时间类型，UT代表世界时
    },
    "fo_data":{
        "ECMWF": {
            "dir_fo": r"S:\data\grid\ECMWF_HR\WIND_10M\YYYYMMDD\YYMMDDHH.TTT.nc", # 数据路径
            "hour": [8, 20, 12],
            "dtime":[12,24,12],                #检验的时效
            "read_method": meteva.base.io.read_griddata_from_nc,  #读取数据的函数
            "read_para": {},  #读取数据的函数参数
            "reasonable_value": None,
            "operation": None,  #预报数据读取后处理函数
            "operation_para": {},   #预报数据读取后处理参数
            "time_type": "BT",  # 预报数据时间类型是北京时，即08时起报
            "move_fo_time": 12   #是否对预报的时效进行平移，12 表示将1月1日08时的36小时预报转换成1月1日20时的24小时预报后参与对比
        },

        "SCMOC": {
            "dir_fo": r"S:\data\grid\NWFD_SCMOC\WIND\10M_ABOVE_GROUND\YYYYMMDD\YYMMDDHH.TTT.nc",
            "hour": [8, 20, 12],
            "dtime":[12,24,12],
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "reasonable_value": None,
            "operation": None,
            "operation_para": {},
            "time_type": "BT",
            "move_fo_time": 0
        },
    },
    "output_dir":None  #观测站点合并数据的输出路径，设置为None时不输出收集数据的中间结果
}

def task_of_one_p_surface(para,time_fo):
    para_one = copy.deepcopy(para)
    para_one["begin_time"] = time_fo
    para_one["end_time"] = time_fo
    middle_result_dir_sep = os.path.split(para_one["middle_result_path"])[0] + "/sep/YYMMDDHH.h5"
    middle_result_path_sep = meteva.base.get_path(middle_result_dir_sep,time_fo)
    sta_all = meteva.product.data_prepare.prepare_dataset(para_one)
    df_mid = meteva.perspact.middle_df_sta(sta_all,para_one["mid_method"],grade_list=para_one["grade_list"],compare=para_one["compare"])
    meteva.base.creat_path(middle_result_path_sep)
    df_mid.to_hdf(middle_result_path_sep,"df")


def middle_of_score_surface(para):

    para["base_on"] = "foTime"
    time_cost = time.time()
    middle_result_path = para["middle_result_path"]
    meteva.base.creat_path(middle_result_path)
    model_name_list = list(para["fo_data"].keys())
    mid_method = para["mid_method"]


    mid_list = []
    # 创建一个空的DataFrame，用来记录哪些中间量已经收集
    df1 = pd.DataFrame(data=None, columns=['time', 'dtime', 'member'])
    mid0 = None
    if os.path.exists(middle_result_path):
        if not para["recover"]:
            mid0 = pd.read_hdf(middle_result_path)
            mid_list.append(mid0)
            df1 = mid0[[ "time", "dtime", "member"]]  # 如果有文件就替换掉df1
            df1.drop_duplicates(keep="first", inplace=True)  # 用来记录哪些时次已经收集了中间量

    begin_time = para["begin_time"]
    end_time = para["end_time"]


    v_time_list = []
    for model in model_name_list:
        df1_= df1.loc[df1['member'].isin([model])]
        time1 = begin_time
        para_fo1 = para["fo_data"][model]

        dtime_list = np.arange(para_fo1["dtime"][0], para_fo1["dtime"][1] + 1, para_fo1["dtime"][2]).tolist()

        dtime_list_v = dtime_list
        if para_fo1["operation_para"] is not None:
            d = 0
            if "delta" in  para_fo1["operation_para"].keys():
                d = para_fo1["operation_para"]["delta"]
            elif "span" in para_fo1["operation_para"].keys() :
                d = para_fo1["operation_para"]["span"]

            if d!=0:
                dtime_list.insert(0,0)
                array0 = np.array(dtime_list)
                array1 = array0 + d
                dtime_list_c = list(set((set(array0.tolist())&set(array1.tolist()))))
                dtime_list_c.sort()
                dtime_list_v = dtime_list_c


        while time1 <= end_time:
            df2 = meteva.base.in_time_list(df1_, time1)
            if len(df2.index) ==len(dtime_list_v):
                print(meteva.base.get_path(model + "YYYY年MM月DD日HH时起报的检验中间量已存在",time1))
            else:
                v_time_list.append(time1)


            time1 = time1 + datetime.timedelta(hours=para["time_step"])

    v_time_list = list(set(v_time_list))
    v_time_list.sort()

    if "cpu" not in para.keys():
        cpu = 1
    else:
        cpu = para["cpu"]


    #先删除已有的拆分的中间结果
    dir1,_ =  os.path.split(os.path.abspath(middle_result_path))
    middle_result_dir_sep =dir1+"/sep"
    if os.path.exists(middle_result_dir_sep):
        #删除已有的拆分的中间结果
        file_list = os.listdir(middle_result_dir_sep)
        for file1 in file_list:
            path = middle_result_dir_sep + "/"+ file1
            os.remove(path)
    else:
        pathlib.Path(middle_result_dir_sep).mkdir(parents=True, exist_ok=True)  #创建文件夹

    print(v_time_list)
    #采用多进程统计中间量
    meteva.base.multi_run(cpu,task_of_one_p_surface,para=para,time_fo = v_time_list)

    #将中间量的结果进行合并
    df_list = [mid0]
    file_list = os.listdir(middle_result_dir_sep)
    for file1 in file_list:
        path = middle_result_dir_sep + "/" + file1
        df = pd.read_hdf(path)
        df_list.append(df)
        os.remove(path)

    mid_all = meteva.base.concat(df_list)
    mid_all.sort_values(by=["time","dtime","member"],inplace=True)
    # 先删除文件在重新输出文件，避免文件大小膨胀
    if os.path.exists(middle_result_path):
        os.remove(middle_result_path)
    mid_all.to_hdf(middle_result_path, "df")  # 将结果输出到文件
    print("中间量拼接程序运行完毕")
    print("拼接后的中间结果已输出至"+middle_result_path)

    print("总耗时："+str(time.time()-time_cost))
    return



if __name__ == "__main__":

    middle_of_score_surface(para_example)
    path = r"H:\test_data\output\mps\na.h5"
    df = pd.read_hdf(path)
    print(df)
    print()

    meteva.base.interp_ss_idw()