import sys
sys.path.append(r"C:\running\python_code")
import nmc_verification.nmc_vf_base as nvb
import nmc_verification.nmc_vf_product as nvp
import datetime
import os
import pandas as pd
import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import copy

para ={
    "ob_dir_s":r"H:\test_data\yanqing\平均风速_2分钟\YYYYMMDDHH0000.000",
    "ob_dir_d":r"H:\test_data\yanqing\平均风向_2分钟\YYYYMMDDHH0000.000",
    "ob_dir_s_all": r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\timelist\ob_s_2min_mean.txt",
    "ob_dir_d_all": r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\timelist\ob_d_2min_mean.txt",
    "fo_grd_dir_u":r"H:\test_data\ecmwf\ugrd\800\YYMMDDHH.TTT",
    "fo_grd_dir_v":r"H:\test_data\ecmwf\vgrd\800\YYMMDDHH.TTT",
    "fo_sta_dir_u":r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\timelist\ec_u.txt",
    "fo_sta_dir_v":r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\timelist\ec_v.txt",
    "max_dh":72,
    "output_dir": r"Z:\verification_product\tiananmen\YYMMDDHH\EC_wind_3h_YYYYMMDDHH.JPG",
    "ob_ids" :[651701],
    "title":"EC_wind_800hPa_2min_3Hour"
}

def extract_fo(output_path,input_dir,station,data_name):
    sta = copy.deepcopy(station)
    now = datetime.datetime.now()
    end_time = datetime.datetime(now.year,now.month,now.day,20,0)

    time0 = end_time - datetime.timedelta(hours=240)
    if os.path.exists(output_path):
        sta_speed_all = nvb.read_stadata_from_csv(output_path)
    else:
        sta_speed_all = None
    while time0 < end_time:
        if sta_speed_all is not None:
            sta_t = nvb.in_time_list(sta_speed_all,[time0])
        else:
            sta_t = None
        if sta_t is None or len(sta_t.index) ==0 :
            for dh in range(0,241,3):
                if sta_t is not None:
                    sta_dt = nvb.in_dtime_list(sta_t,[dh])
                else:
                    sta_dt = None
                if sta_dt is None or len(sta_dt.index) == 0:
                    path_speed = nvb.get_path(input_dir,time0,dh)
                    print(path_speed)
                    if os.path.exists(path_speed):
                        grd_speed = nvb.read_griddata_from_nc(path_speed)
                        print(path_speed)
                        if grd_speed is not None:
                            #print(grd_speed)
                            sta1 = nvb.interp_gs_linear(grd_speed,sta)
                            nvb.set_stadata_coords(sta1,level=0,time=time0,dtime=dh)
                            sta_speed_all = nvb.combine_join(sta_speed_all,sta1)
                    #print(sta_speed_all)
        time0 = time0 + datetime.timedelta(hours=12)
    nvb.set_stadata_names(sta_speed_all,[data_name])
    sta_speed_all.to_csv(output_path)

def extract_ob(output_path,input_dir,station,data_name):
    ids = station["id"].values.tolist()
    now = datetime.datetime.now()
    end_time = datetime.datetime(now.year,now.month,now.day,now.hour,0)
    time0 = end_time - datetime.timedelta(hours=240)

    sta_speed_all = nvb.read_stadata_from_csv(output_path)
    while time0 < end_time:
        sta_t = nvb.in_time_list(sta_speed_all, [time0])
        if len(sta_t.index) == 0:
            path_in = nvb.get_path(input_dir, time0)
            if os.path.exists(path_in):
                sta = nvb.read_stadata_from_micaps3(path_in)
                print(path_in)
                if sta is not None:
                    #print(sta)
                    sta1 = nvb.put_stadata_on_station(sta,station)
                    print(sta1)
                    #sta1 = nvb.in_id_list(sta,ids)
                    nvb.set_stadata_coords(sta1, level=0, time=time0)
                    sta_speed_all = nvb.combine_join(sta_speed_all, sta1)
                    # print(sta_speed_all)
        time0 = time0 + datetime.timedelta(hours=1)
    nvb.set_stadata_names(sta_speed_all, [data_name])
    sta_speed_all.to_csv(output_path)

if __name__ == "__main__":
    now = datetime.datetime.now()
    now = datetime.datetime(now.year,now.month,now.day,now.hour,0)
    station = nvb.read_stadata_from_micaps3("station.txt")
    extract_fo(para["fo_sta_dir_u"],para["fo_grd_dir_u"],station,data_name="fou")
    extract_fo(para["fo_sta_dir_v"], para["fo_grd_dir_v"], station, data_name="fov")
    extract_ob(para["ob_dir_d_all"],para["ob_dir_d"],station,data_name="obd")
    extract_ob(para["ob_dir_s_all"], para["ob_dir_s"], station, data_name="obs")
    #读取观测数据
    sta_ob_all_s = nvb.read_stadata_from_csv(para["ob_dir_s_all"])
    sta_ob_all_s = nvb.between_value_range(sta_ob_all_s,0.00001,100)
    print(sta_ob_all_s)
    sta_ob_all_d = nvb.read_stadata_from_csv(para["ob_dir_d_all"])
    sta_ob_all = nvb.combine_on_all_coords(sta_ob_all_s,sta_ob_all_d)
    u  = -sta_ob_all["obs"] * np.sin(sta_ob_all["obd"] * 3.14 / 180)
    v = -sta_ob_all["obs"] * np.cos(sta_ob_all["obd"] * 3.14 / 180)
    sta_ob_all["u"+para["title"]] = u
    sta_ob_all["v"+para["title"]] = v
    sta_ob_all = sta_ob_all.drop(["obs","obd"],axis = 1)
    time_list = []
    for dh in range(-72,0,1):
        time_list.append(now + datetime.timedelta(hours=dh))
    sta_ob_all = nvb.in_time_list(sta_ob_all,time_list)
    print(sta_ob_all)
    #读取预报数据
    sta_fo_all_u = nvb.read_stadata_from_csv(para["fo_sta_dir_u"])
    sta_fo_all_v = nvb.read_stadata_from_csv(para["fo_sta_dir_v"])
    sta_fo_all = nvb.combine_on_all_coords(sta_fo_all_u,sta_fo_all_v)
    nvb.set_stadata_names(sta_fo_all,data_name_list=["u"+para["title"],"v"+para["title"]])
    print(sta_fo_all)
    cmap = plt.get_cmap("coolwarm")

    sta_fo_all["id"].values[:] = sta_ob_all["id"].values[0]
    sta_fo_all['level'].values[:] = sta_ob_all["level"].values[0]
    sta_fo_all['lon'].values[:] = sta_ob_all["lon"].values[0]
    sta_fo_all['lat'].values[:] = sta_ob_all["lat"].values[0]



    pic_path = r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\a.png"
    nvp.continuous.wind_ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path,120,plot_error=True)
