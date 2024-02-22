#import meteva.base as meb
#import meteva.method as mem
#import meteva.product as mpd
#import meteva.perspact as mps
import datetime
import copy
import numpy as np
import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import os
import meteva
import urllib.request
import traceback
import math

def acc(grd_ob,grd_fo):
    grid0 = meteva.base.get_grid_of_data(grd_ob)
    z500_cli_path = meteva.base.z500_cli
    if not os.path.exists(z500_cli_path):
        url = "https://github.com/nmcdev/meteva/tree/master/meteva/resources/z500_cli.nc"
        try:
            print("开始从github下载500hPa高度场气候平均数据，请稍等")
            urllib.request.urlretrieve(url, filename=z500_cli_path)
            z500_cli = meteva.base.read_griddata_from_nc(z500_cli_path, grid=grid0)
            if z500_cli is None:
                raise ValueError("z500_cli 不能是None")
            print("下载500hPa高度场气候平均数据下载成功")
        except Exception as e:
            print("从github下载地形高度数据失败，请重试，或者手动从\n" + url + "\n下载文件并保存至\n" + z500_cli_path)
            print(e)
            if os.path.exists(z500_cli_path):
                os.remove(z500_cli_path)
            return
    else:
        z500_cli =  meteva.base.read_griddata_from_nc(z500_cli_path, grid=grid0)

    time_ob = meteva.base.all_type_time_to_datetime(grid0.gtime[0])
    if time_ob.hour ==0 or time_ob.hour == 12:
        time_ob_ut = time_ob
    else:
        time_ob_ut = time_ob - datetime.timedelta(hours=8)

    time_cli = datetime.datetime(2020, time_ob_ut.month, time_ob_ut.day, time_ob_ut.hour)
    grd_cli =  meteva.base.in_time_list(z500_cli, [time_cli])
    grd_obs = copy.deepcopy(grd_ob)
    grd_obs.values -= grd_cli.values
    grd_fst = copy.deepcopy(grd_fo)
    grd_fst.values -= grd_cli.values

    lats = grd_ob["lat"].values
    lons = grd_ob["lon"].values
    xx,yy = np.meshgrid(lons,lats)
    weight = np.cos(yy*math.pi / 180)
    grid0 = meteva.base.get_grid_of_data(grd_ob)
    grd_weight = meteva.base.grid_data(grid0,weight)


    acc_value =  meteva.method.corr(grd_obs.values,grd_fst.values,grd_weight.values)
    return acc_value



def acc_middle_z500(para_acc):
    z500_cli_path = meteva.base.z500_cli
    if not os.path.exists(z500_cli_path):
        url = "https://github.com/nmcdev/meteva/raw/master/meteva/resources/z500_cli.nc"
        try:
            print("开始从github下载地形高度数据，请稍等")
            urllib.request.urlretrieve(url, filename=z500_cli_path)
        except Exception as e:
            print("从github下载地形高度数据失败，请重试，或者手动从\n" + url + "\n下载文件并保存至\n" + z500_cli_path)
            print(e)
            return

    middle_result_path = para_acc["middle_result_path"]
    model_name_list =list(para_acc["fo_data"].keys()) # ["ECMWF","PANGU","FENGWU"]  #数据的名称
    if para_acc["step"] is not None:
        marker = meteva.perspact.get_grid_marker(para_acc["grid"],step=para_acc["step"])
    else:
        marker = None
    z500_cli =  meteva.base.read_griddata_from_nc(z500_cli_path,grid = para_acc["grid"])

    tmmsss_list = []
    #创建一个空的DataFrame，用来记录哪些中间量已经收集
    df1 = pd.DataFrame(data=None,columns=['level', 'time', 'dtime', 'member'])
    if os.path.exists(middle_result_path):
        tmmsss0 = pd.read_hdf(middle_result_path)
        tmmsss_list.append(tmmsss0)
        df1 = tmmsss0[["level","time","dtime","member"]]   #如果有文件就替换掉df1
        df1.drop_duplicates(keep="first", inplace=True)   # 用来记录哪些时次已经收集了中间量


    for model in model_name_list:
        df2 = df1.loc[df1['member'].isin([model])]
        time1 = para_acc["begin_time"]
        save_k = 0 # 用来在收集的过程间隔一段时间报错一下结果，避免程序错误时没有任何输出导致要重头再来
        para_fo1 = para_acc["fo_data"][model]
        dtime_list = np.arange(para_fo1["dtime"][0], para_fo1["dtime"][1] + 1, para_fo1["dtime"][2]).tolist()
        while time1 <=  para_acc["end_time"]:
            df3 =  meteva.base.in_time_list(df2,time1)
            if len(df3.index) ==len(dtime_list):
                print(meteva.base.get_path(model + "YYYY年MM月DD日HH时起报的检验中间量已存在",time1))
            else:
                time_ut = time1 - datetime.timedelta(hours=8)
                for dh in dtime_list:
                    df4 =  meteva.base.in_dtime_list(df3,dtime_list=dh)
                    if len(df4.index) ==0:
                        save_k += 1  #
                        time_ob = time1 + datetime.timedelta(hours=dh)
                        time_ob_ut = time_ob - datetime.timedelta(hours=8)
                        if para_acc["ob_data"]["time_type"] =="BT":
                            time_path = time_ob
                        else:
                            time_path = time_ob_ut
                        time_cli = datetime.datetime(2020,time_ob_ut.month,time_ob_ut.day,time_ob_ut.hour)
                        grd_cli =  meteva.base.in_time_list(z500_cli,[time_cli])

                        path0 =  meteva.base.get_path(para_acc["ob_data"]["dir_ob"], time_path)
                        grd_obs = para_acc["ob_data"]["read_method"](path0, grid=para_acc["grid"], time=time_ob, dtime=0, data_name="OBS",show = True,**para_acc["ob_data"]["read_para"])
                        if grd_obs is None: continue

                        grd_obs.values *= para_acc["ob_data"]["multiple"]
                        grd_obs.values -= grd_cli.values

                        if para_fo1["time_type"]=="BT":
                            path1 =  meteva.base.get_path(para_fo1["dir_fo"],time1,dh)
                        else:
                            path1 =  meteva.base.get_path(para_fo1["dir_fo"], time_ut, dh)

                        grd_fo = para_fo1["read_method"](path1, grid=para_acc["grid"], time=time1, dtime=dh, data_name=model,show = True,**para_fo1["read_para"])
                        if grd_fo is not None:
                            grd_fo.values *=para_fo1["multiple"]
                            grd_fo.values -= grd_cli.values
                            df_mid =  meteva.perspact.middle_df_grd(grd_obs, grd_fo, meteva.method.tmmsss, marker=marker)
                            tmmsss_list.append(df_mid)

            time1 = time1 + datetime.timedelta(hours=para_acc["time_step"])

            #当收集了超过200个时效的数据时就输出一次
            if save_k % 500==0:
                tmmss_all =  meteva.base.concat(tmmsss_list)
                #先删除文件在重新输出文件，避免文件大小膨胀
                if os.path.exists(middle_result_path):
                    os.remove(middle_result_path)
                tmmss_all.to_hdf(middle_result_path,"df")  #将结果输出到文件

    tmmss_all =  meteva.base.concat(tmmsss_list)
    # 先删除文件在重新输出文件，避免文件大小膨胀
    if os.path.exists(middle_result_path):
        os.remove(middle_result_path)
    tmmss_all.to_hdf(middle_result_path, "df")  # 将结果输出到文件
    print("中间量统计程序运行完毕")
    return


if __name__=="__main__":


    para_acc = {
        "begin_time": datetime.datetime(2022,5,1,8),  #起始时间（预报）
        "end_time":  datetime.datetime(2022,5,5,8), #结束时间（预报）
        "time_step":12,     #起报时间间隔
        "middle_result_path":  r"H:\test_data\output\method\space\acc\tmmsss_z500.h5",
        "grid" :  meteva.base.grid([70,140,0.25],[0,60,0.25]),  # 检验区域
        "step":2,  #masker间隔（单位：°）
        "ob_data": {
            "dir_ob":r"H:\test_data\input\mem\acc\ECMWF\z500\YYMMDDHH.TTT.nc",  # 实况场数据路径
            "read_method": meteva.base.io.read_griddata_from_nc,   #实况数据读取函数
            "read_para": {},  #实况数据读取参数
            "time_type": "BT",  #实况数据时间类型
            "multiple": 9.8,    #当文件数据的单位是位势米，通过乘以9.8转换成位势
        },
        "fo_data": {
            "ECMWF": {
                "dir_fo":r"H:\test_data\input\mem\acc\ECMWF\z500\YYMMDDHH.TTT.nc", #预报数据路径
                "dtime": [12, 72, 12],    #检验时效
                "read_method": meteva.base.io.read_griddata_from_nc,  #预报数据读取函数
                "read_para": {},    #预报数据读取参数
                "time_type": "BT",#预报数据时间类型是北京时，即08时起报
                "multiple":9.8, #当文件数据的单位是位势米，通过乘以9.8转换成位势
            },
            "NCEP": {
                "dir_fo": r"H:\test_data\input\mem\acc\NCEP\z500\YYMMDDHH.TTT.nc",  #预报数据路径
                "dtime": [12, 72, 12],  #检验时效
                "read_method": meteva.base.io.read_griddata_from_nc, #预报数据读取函数
                "read_para": {},#预报数据读取参数
                "time_type": "UT", #预报数据时间类型是世界时，即00时起报
                "multiple": 1, #当文件数据的单位是位势，则×1表示，不变
            },
        },
    }


    #acc_middle_z500(para_acc)
    df_mid = pd.read_hdf(para_acc["middle_result_path"])
    print(df_mid["member"])
    score,gdict = meteva.perspact.score_df(df_mid,meteva.method.corr,g = ["member","dtime"],plot = "line",save_path = r"H:\test_data\output\method\space\acc\acc_dtime.png",
                 xlabel = "时效（单位：小时）",ylabel = "ACC",title = "acc随时效的变化",grid = True,
                               height = 4,width = 7,sup_fontsize = 20)


    meteva.perspact.score_xy_df(df_mid,meteva.method.corr,g = ["member"],save_path = r"H:\test_data\output\method\space\acc\acc_xy.png",ncol = 2)
