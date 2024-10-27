import math
import pathlib
import meteva
import datetime
import pandas as pd
import os 
import numpy as np
import  time

para = {
    "mid_method":meteva.method.tase,
    "grade_list": None,
    "compare":None,
    "middle_result_path": r"H:\test_data\output\mps\tase_z.h5",
    "begin_time": datetime.datetime(2018,8,1,0),
    "end_time": datetime.datetime(2018,8,2,0),
    "time_type":"UT",
    "time_step":12,     #起报时间间隔
    "grid" :  meteva.base.grid([70,140,0.25],[10,60,0.25]),  # 检验区域
    "level_list":  [ 850, 700, 500],
    "step":5,  #masker间隔（单位：°）
    "recover":False,
    "cpu":1,
    "ob_data": {
        "CRA40":{
        "dirm": r"\\10.28.16.234\data2\AI\CRA40\2018\Z\LLL\YYYYMMDDHH.nc",  # 实况场数据路径
        "read_method": meteva.base.read_griddata_from_nc,
        "read_para": {},
        "time_type": "UT",  # 实况数据时间类型
        "multiple": 1,  # 当文件数据的单位是位势米，通过乘以9.8转换成位势
        }
    },
    "fo_data": {
        "Fu":{
            "dirm": r"\\10.28.16.234\data2\AI\fuxi\Z\LLL\YYYYMMDDHH\YYYYMMDDHH.TTT.nc",
            "dtime": [12, 240, 12],
            "read_method": meteva.base.read_griddata_from_nc,
            "read_para": {},
            "time_type": "UT",  # 预报数据时间类型是北京时，即08时起报
            "multiple": 1,  # 当文件数据的单位是位势米，通过乘以9.8转换成位势
            "move_fo_time":0,
            "veri_by":"CRA40",
            "gh":{
                "dirm": r"\\10.28.16.234\data2\AI\fuxi\Z\LLL\YYYYMMDDHH\YYYYMMDDHH.TTT.nc",  #位势高度的文件路径
                "read_method": meteva.base.read_griddata_from_nc,     #读取位势高度的函数
                "read_para": {},                                      #读取位势高度所用的函数参数
            },
        },

        "pa": {
            "dirm":   r"\\10.28.16.234\data2\AI\Pangu_ERA5\Z\LLL\YYYYMMDDHH\YYYYMMDDHH.TTT.nc",
            "dtime": [12, 240, 12],
            "read_method": meteva.base.read_griddata_from_nc,
            "read_para": {},
            "time_type": "UT",#预报数据时间类型是北京时，即08时起报
            "multiple":1, #当文件数据的单位是位势米，通过乘以9.8转换成位势
            "move_fo_time": 12,
            "veri_by": "CRA40",
            "gh": {
                "dirm": r"\\10.28.16.234\data2\AI\Pangu_ERA5\Z\LLL\YYYYMMDDHH\YYYYMMDDHH.TTT.nc", #位势高度的文件路径
                "read_method": meteva.base.read_griddata_from_nc,    #读取位势高度的函数
                "read_para": {},   #读取位势高度所用的函数参数
            },
        },
    },

    "zs": {
        "path": r"\\10.28.16.234\data2\AI\fuxi\Z\LLL\YYYYMMDDHH\YYYYMMDDHH.TTT.nc",     #地形高度的文件路径
        "read_method": meteva.base.read_griddata_from_nc,   #读取地形高度的函数
        "read_para": {},     #读取地形高度的函数参数
    }
}


def task_of_one_p(para,middle_result_path,v_df,mid0 = None,zs = None):

    time_cost_dict = {"total_cost":0,"veri_cost":0}
    time_cost_total0 = time.time()
    grid0 = para["grid"]
    if para["step"] is None:
        marker = None
    else:
        marker = meteva.perspact.get_grid_marker(grid0, step=para["step"])
    mid_method = para["mid_method"]
    if mid0 is None:
        mid_list = []
    else:
        mid_list = [mid0]
    save_k = 0  # 用来在收集的过程间隔一段时间报错一下结果，避免程序错误时没有任何输出导致要重头再来
    v_df_group, level_list = meteva.base.group(v_df, g="level")
    for i in range(len(level_list)):
        level = level_list[i]
        v_df1 = v_df_group[i]
        v_df_group1, ob_time_list = meteva.base.group(v_df1, g="ob_time")
        for j in range(len(v_df_group1)):
            # 在相同的实况时间分组里，可以重复使用相同的实况
            grd_obs_dict = {}  # 记录读过的实况，ob_time变化时清空

            time_ob = ob_time_list[j]
            time_ob_bt = time_ob + datetime.timedelta(hours=8)
            v_df2 = v_df_group1[j]
            for k in range(len(v_df2.index)):
                time1 = meteva.base.all_type_time_to_datetime(v_df2["time"].values[k])
                dh = v_df2["dtime"].values[k]
                model = v_df2["member"].values[k]
                para_fo1 = para["fo_data"][model]
                move_fo_time = para_fo1["move_fo_time"]
                veri_by = para_fo1["veri_by"]
                if veri_by == "self":
                    veri_by = model

                if veri_by in grd_obs_dict.keys():
                    # 如果已经读过某个名字的实况，就直接取
                    grd_obs = grd_obs_dict[veri_by]
                else:
                    move_fo_time = para_fo1["move_fo_time"]
                    if veri_by == model:  # veri_by == self
                        para_ob1 = para_fo1
                    else:
                        para_ob1 = para["ob_data"][veri_by]

                    if para_ob1["time_type"].lower() == "bt":
                        time_path = time_ob_bt
                    else:
                        time_path = time_ob

                    path0 = meteva.base.get_path(para_ob1["dirm"], time_path)
                    path0 = path0.replace("LLL", str(level))
                    if not os.path.exists(path0):
                        print(path0 + " not exist")
                        continue

                    time_cost0 = time.time()
                    grd_obs = para_ob1["read_method"](path0, grid=para["grid"], time=time_ob,
                                                      dtime=0, data_name="OBS", show=True, level=level,
                                                      **para_ob1["read_para"])
                    time_cost = time.time() - time_cost0
                    if veri_by not in time_cost_dict.keys():
                        time_cost_dict[veri_by] = 0
                    time_cost_dict[veri_by] += time_cost


                    if grd_obs is None:
                        print("faild to read " + path0)
                        continue
                    grd_obs.values *= para_ob1["multiple"]
                    grd_obs_dict[veri_by] = grd_obs

                time1_ = time1
                if para_fo1["time_type"].lower() == "bt":
                    time1_ = time1 + datetime.timedelta(hours=8)
                time1_ -= datetime.timedelta(hours=move_fo_time)
                if para_fo1["dirm"] is not None:
                    path1 = meteva.base.get_path(para_fo1["dirm"], time1_, dh + move_fo_time)
                    path1 = path1.replace("LLL", str(level))
                    time_cost0 = time.time()
                    grd_fo = para_fo1["read_method"](path1, grid=para["grid"], time=time1, dtime=dh, level=level,
                                                     data_name=model, show=True, **para_fo1["read_para"])
                else:
                    grd_fo = para_fo1["read_method"](grid=para["grid"], time=time1, dtime=dh, level=level,
                                                     data_name=model, show=True)
                time_cost = time.time() - time_cost0
                if model not in time_cost_dict.keys():
                    time_cost_dict[model] = 0
                time_cost_dict[model] += time_cost

                if grd_fo is not None:
                    grd_fo.values *= para_fo1["multiple"]
                    time_cost0 = time.time()

                    #读取位势高度用于判断是否在地下
                    if zs is not None:
                        if para_fo1["gh"]["dirm"] is not None:
                            path1 = meteva.base.get_path(para_fo1["gh"]["dirm"], time1_, dh + move_fo_time)
                            path1 = path1.replace("LLL", str(level))
                            time_cost0 = time.time()
                            grd_gh = para_fo1["gh"]["read_method"](path1, grid=para["grid"], time=time1, dtime=dh,
                                                             level=level,
                                                             data_name=model, show=True, **para_fo1["gh"]["read_para"])
                        else:
                            grd_gh = para_fo1["gh"]["read_method"](grid=para["grid"], time=time1, dtime=dh, level=level,
                                                             data_name=model, show=True)

                        grd_fo.values[grd_gh.values<zs.values] = np.nan


                    df_mid = meteva.perspact.middle_df_grd(grd_obs, grd_fo, mid_method, marker=marker,
                                                           grade_list=para["grade_list"], compare=para["compare"])
                    time_cost = time.time() - time_cost0
                    time_cost_dict["veri_cost"] += time_cost

                    mid_list.append(df_mid)
                else:
                    print("faild to read " + path1)

                save_k += 1
                # 当收集了超过500个时效的数据时就输出一次
                if save_k % 500 == 0:
                    mid_all = meteva.base.concat(mid_list)
                    # 先删除文件在重新输出文件，避免文件大小膨胀
                    if os.path.exists(middle_result_path):
                        os.remove(middle_result_path)
                    mid_all.to_hdf(middle_result_path, "df")  # 将结果输出到文件

    mid_all = meteva.base.concat(mid_list)
    mid_all.sort_values(by=["time", "dtime", "level", "member"], inplace=True)
    # 先删除文件在重新输出文件，避免文件大小膨胀
    if os.path.exists(middle_result_path):
        os.remove(middle_result_path)
    mid_all.to_hdf(middle_result_path, "df")  # 将结果输出到文件
    print("中间量统计程序运行完毕")
    print("中间结果已输出至" + middle_result_path)
    time_cost_dict["total_cost"] = time.time() - time_cost_total0
    print("单进程耗时："+ str(time_cost_dict["total_cost"]))
    print("检验计算耗时："+str(time_cost_dict["veri_cost"]))
    for key in time_cost_dict:
        if  not key in ["total_cost","veri_cost"]:
            print("读取"+key+"耗时："+str(time_cost_dict[key]))

    return mid_all


def middle_of_score(para):

    time_cost = time.time()
    middle_result_path = para["middle_result_path"]
    meteva.base.creat_path(middle_result_path)
    model_name_list = list(para["fo_data"].keys())
    mid_method = para["mid_method"]
    grid0 = para["grid"]
    # grid0 = meteva.base.grid([0,359.75,0.25],[-89.75,89.75,0.25])
    if para["step"] is None:
        marker = None
    else:
        marker = meteva.perspact.get_grid_marker(grid0, step=para["step"])
    level_list =para["level_list"]
    mid_list = []
    # 创建一个空的DataFrame，用来记录哪些中间量已经收集
    df1 = pd.DataFrame(data=None, columns=['level', 'time', 'dtime', 'member'])
    mid0 = None
    if os.path.exists(middle_result_path):
        if not para["recover"]:
            mid0 = pd.read_hdf(middle_result_path)
            mid_list.append(mid0)
            df1 = mid0[["level", "time", "dtime", "member"]]  # 如果有文件就替换掉df1
            df1.drop_duplicates(keep="first", inplace=True)  # 用来记录哪些时次已经收集了中间量

    begin_time = para["begin_time"]
    end_time = para["end_time"]
    if para["time_type"].lower()=="bt":
        begin_time -= datetime.timedelta(hours=8)
        end_time -= datetime.timedelta(hours=8)

    v_member_list = []
    v_time_list = []
    v_dtime_list = []
    v_level_list = []
    for model in model_name_list:
        df1_= df1.loc[df1['member'].isin([model])]
        time1 = begin_time
        para_fo1 = para["fo_data"][model]

        dtime_list = np.arange(para_fo1["dtime"][0], para_fo1["dtime"][1] + 1, para_fo1["dtime"][2]).tolist()

        while time1 <= end_time:
            df2 = meteva.base.in_time_list(df1_, time1)
            if len(df2.index) ==len(dtime_list):
                print(meteva.base.get_path(model + "YYYY年MM月DD日HH时起报的检验中间量已存在",time1))
            else:
                for dh in dtime_list:
                    df3 = meteva.base.in_dtime_list(df2, dtime_list=dh)
                    for level in level_list:
                        df4 = meteva.base.in_level_list(df3, level_list=level)
                        if len(df4.index) ==0:
                            v_member_list.append(model)
                            v_time_list.append(time1)
                            v_dtime_list.append(dh)
                            v_level_list.append(level)
            time1 = time1 + datetime.timedelta(hours=para["time_step"])

    v_df = pd.DataFrame({
        "level":v_level_list,
        "time":v_time_list,
        "dtime":v_dtime_list,
        "member":v_member_list
    })

    zs = None
    #读取地形高度
    if "zs" in para.keys():
        if "read_method" in para["zs"]:
            if para["zs"]["read_method"] is not None:
                zs = para["zs"]["read_method"](para["zs"]["path"],grid = para["grid"],**para["zs"]["read_para"])
                if zs is None:
                    print("地形高度数据读取失败，请检查地形数据文件是否存在，地形数据读取函数和地形数据格式是否吻合")

    if "cpu" not in para.keys() or para["cpu"] ==1:
        task_of_one_p(para,middle_result_path,v_df,mid0 = mid0,zs= zs)

    else:
        #多进程并行方案

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


        v_df["ob_time"] = v_df["time"].astype("datetime64[us]") + v_df["dtime"]*np.timedelta64(1,"h")
        v_df.sort_values(by=["level","ob_time"],inplace=True)  #按层次、实况时间排序，可以尽可能让共用实况的任务靠近
        ntask = len(v_df.index)
        cpu = para["cpu"]

        task_of_one_cpu = int(math.ceil(ntask/cpu))
        middle_result_path_list = []
        v_df_list = []
        for i in range(cpu):
            index_s = task_of_one_cpu*(i)
            index_e = task_of_one_cpu*(i+1)
            df1 = v_df.iloc[index_s:index_e,:]
            v_df_list.append(df1)
            middle_result_path_list.append(middle_result_dir_sep+"/"+str(i)+".h5")

        #采用多进程统计中间量
        meteva.base.multi_run(cpu,task_of_one_p,para=para,middle_result_path=middle_result_path_list,v_df = v_df_list,zs = zs)

        #将中间量的结果进行合并
        df_list = [mid0]
        file_list = os.listdir(middle_result_dir_sep)
        for file1 in file_list:
            path = middle_result_dir_sep + "/" + file1
            df = pd.read_hdf(path)
            df_list.append(df)
            os.remove(path)

        mid_all = meteva.base.concat(df_list)
        mid_all.sort_values(by=["time","dtime","level","member"],inplace=True)
        # 先删除文件在重新输出文件，避免文件大小膨胀
        if os.path.exists(middle_result_path):
            os.remove(middle_result_path)
        mid_all.to_hdf(middle_result_path, "df")  # 将结果输出到文件
        print("中间量拼接程序运行完毕")
        print("拼接后的中间结果已输出至"+middle_result_path)

    print("总耗时："+str(time.time()-time_cost))
    return



if __name__ == "__main__":


    pass