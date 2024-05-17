import meteva 
import datetime
import pandas as pd
import os 
import numpy as np


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
            "veri_by":"CRA40"
        },

        "pa": {
            "dirm":   r"\\10.28.16.234\data2\AI\Pangu_ERA5\Z\LLL\YYYYMMDDHH\YYYYMMDDHH.TTT.nc",
            "dtime": [12, 240, 12],
            "read_method": meteva.base.read_griddata_from_nc,
            "read_para": {},
            "time_type": "UT",#预报数据时间类型是北京时，即08时起报
            "multiple":1, #当文件数据的单位是位势米，通过乘以9.8转换成位势
            "move_fo_time": 12,
            "veri_by": "CRA40"
        },
    },
}


def middle_of_score(para):
    middle_result_path = para["middle_result_path"]
    meteva.base.creat_path(middle_result_path)
    model_name_list = list(para["fo_data"].keys())
    mid_method = para["mid_method"]
    grid0 = para["grid"]
    # grid0 = meteva.base.grid([0,359.75,0.25],[-89.75,89.75,0.25])
    marker = meteva.perspact.get_grid_marker(grid0, step=para["step"])
    # marker = None
    level_list =para["level_list"]
    mid_list = []
    # 创建一个空的DataFrame，用来记录哪些中间量已经收集
    df1 = pd.DataFrame(data=None, columns=['level', 'time', 'dtime', 'member'])
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


    for model in model_name_list:
        df1_= df1.loc[df1['member'].isin([model])]
        time1 = begin_time
        para_fo1 = para["fo_data"][model]
        move_fo_time = para_fo1["move_fo_time"]
        veri_by = para_fo1["veri_by"]
        if veri_by =="self":
            para_ob1 = para_fo1
        else:
            para_ob1 = para["ob_data"][veri_by]

        save_k = 0  # 用来在收集的过程间隔一段时间报错一下结果，避免程序错误时没有任何输出导致要重头再来
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
                            save_k += 1  #
                            time_ob = time1 + datetime.timedelta(hours=dh)
                            time_ob_bt = time_ob + datetime.timedelta(hours=8)
                            if para_ob1["time_type"].lower() == "bt":
                                time_path = time_ob_bt
                            else:
                                time_path = time_ob

                            path0 = meteva.base.get_path(para_ob1["dirm"], time_path)
                            path0 = path0.replace("LLL",str(level))
                            if not os.path.exists(path0):
                                print(path0 +" not exist")
                                continue
                            grd_obs = para_ob1["read_method"](path0, grid=para["grid"], time=time_ob,
                                                                         dtime=0, data_name="OBS", show=True,level = level,
                                                                         **para_ob1["read_para"])
                            if grd_obs is None:
                                print("faild to read "+ path0)
                                continue

                            grd_obs.values *= para_ob1["multiple"]

                            time1_ = time1
                            if para_fo1["time_type"].lower() == "bt":
                                time1_ = time1 + datetime.timedelta(hours=8)
                            time1_ -= datetime.timedelta(hours=move_fo_time)


                            path1 = meteva.base.get_path(para_fo1["dirm"], time1_, dh+move_fo_time)

                            path1 = path1.replace("LLL", str(level))
                            grd_fo = para_fo1["read_method"](path1, grid=para["grid"], time=time1, dtime=dh,level = level,
                                                             data_name=model, show=True, **para_fo1["read_para"])
                            if grd_fo is not None:
                                grd_fo.values *= para_fo1["multiple"]
                                df_mid = meteva.perspact.middle_df_grd(grd_obs, grd_fo,mid_method, marker=marker,
                                                                       grade_list=para["grade_list"],compare=para["compare"])
                                mid_list.append(df_mid)
                            else:
                                print("faild to read " + path1)

                            # 当收集了超过500个时效的数据时就输出一次
                            if save_k % 500 == 0:
                                mid_all = meteva.base.concat(mid_list)
                                # 先删除文件在重新输出文件，避免文件大小膨胀
                                if os.path.exists(middle_result_path):
                                    os.remove(middle_result_path)
                                mid_all.to_hdf(middle_result_path, "df")  # 将结果输出到文件


            time1 = time1 + datetime.timedelta(hours=para["time_step"])
    mid_all = meteva.base.concat(mid_list)
    # 先删除文件在重新输出文件，避免文件大小膨胀
    if os.path.exists(middle_result_path):
        os.remove(middle_result_path)
    mid_all.to_hdf(middle_result_path, "df")  # 将结果输出到文件
    print("中间量统计程序运行完毕")
    print("中间结果已输出至"+middle_result_path)
    return





if __name__ == "__main__":


    pass