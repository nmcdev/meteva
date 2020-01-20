import nmc_verification.nmc_vf_base as nvb
import datetime
import numpy as np
import pandas as pd
import os
import nmc_verification.nmc_vf_method as nvm


station = nvb.read_stadata_from_micaps3("station.txt")
print(station)
ip, port = nvb.read_gds_ip_port(r"H:\test_data\input\nvb\ip_port.txt")
path_input = r"ECMWF_HR/UGRD/800/20011708.024"


sta = nvb.read_stadata_from_gds_griddata(ip,port,path_input,station)
print(sta)
print()


def download_ec():
    ip, port = nvb.read_gds_ip_port(r"H:\test_data\input\nvb\ip_port.txt")
    filename_list = nvb.path_tools.get_gds_file_list_in_one_dir(ip, port, r"ECMWF_HR/UGRD/800")
    #filename_list = ["20011008.015"]
    for filename in filename_list:
        path_output = r"H:\test_data\ecmwf\ugrd\800" + "\\" + filename
        if not os.path.exists(path_output):
            path_input = "ECMWF_HR/UGRD/800/" + filename
            grd = nvb.read_griddata_from_gds(ip, port, path_input)
            if grd is not None:
                nvb.write_griddata_to_nc(grd,path_output,creat_dir=True)

    filename_list = nvb.path_tools.get_gds_file_list_in_one_dir(ip, port, r"ECMWF_HR/VGRD/800")
    #filename_list = ["20011008.015"]
    for filename in filename_list:
        path_output = r"H:\test_data\ecmwf\vgrd\800" + "\\" + filename
        if not os.path.exists(path_output):
            path_input = "ECMWF_HR/VGRD/800/" + filename
            grd = nvb.read_griddata_from_gds(ip, port, path_input)
            if grd is not None:
                nvb.write_griddata_to_nc(grd,path_output,creat_dir=True)

    time0 = datetime.datetime(2020,1,7,8,0)
    end_time = datetime.datetime.now()
    dir_u = r"H:\test_data\ecmwf\ugrd\800\YYMMDDHH.TTT"
    dir_v = r"H:\test_data\ecmwf\vgrd\800\YYMMDDHH.TTT"
    dir_speed = r"H:\test_data\ecmwf\speed\800\BTYYMMDDHH.TTT.nc"
    while time0 < end_time:
        for dh in range(0,241,3):
            path_output = nvb.get_path(dir_speed, time0, dh)
            if not os.path.exists(path_output):
                path_u = nvb.get_path(dir_u,time0,dh)
                path_v = nvb.get_path(dir_v,time0,dh)
                grd_u = nvb.read_griddata_from_nc(path_u)
                if grd_u is not None:
                    grid0 = nvb.get_grid_of_data(grd_u)
                    grd_v = nvb.read_griddata_from_nc(path_v)
                    if grd_v is not None:
                        grd_speed = nvb.grid_data(grid0)
                        grd_speed.values[...] = np.sqrt(np.power(grd_u.values[...],2) + np.power(grd_v.values[...],2))
                        path_output = nvb.get_path(dir_speed,time0,dh)
                        nvb.write_griddata_to_nc(grd_speed,path_output,creat_dir=True)
                    #print()
        time0 = time0 + datetime.timedelta(hours=12)
download_ec()

def download_grapes():
    ip, port = nvb.read_gds_ip_port(r"H:\test_data\input\nvb\ip_port.txt")
    root_dir = "GRAPES_GFS/WIND/800"
    filename_list = nvb.path_tools.get_gds_file_list_in_one_dir(ip, port, root_dir)
    #filename_list = ["20011008.015"]
    for filename in filename_list:
        path_output = r"H:\test_data\grapes_gfs\speed\800" + "\\" + filename
        if not os.path.exists(path_output):
            path_input = root_dir +"/" + filename
            grd = nvb.read_gridwind_from_gds(ip, port, path_input)
            if grd is not None:
                #print(grd)
                path_output = r"H:\test_data\grapes_gfs\wind\800"+"\\"+filename
                nvb.write_griddata_to_nc(grd,path_output,creat_dir=True)
                u = nvb.in_member_list(grd,member_list=["u"])
                v = nvb.in_member_list(grd,member_list=["v"])
                grid0 = nvb.get_grid_of_data(u)
                grd_speed = nvb.grid_data(grid0)
                grd_speed.values[...] = np.sqrt(np.power(u.values[...], 2) + np.power(v.values[...], 2))
                path_output =  r"H:\test_data\grapes_gfs\speed\800" + "\\" + filename
                nvb.write_griddata_to_nc(grd_speed,path_output,creat_dir=True)


def extract(output_path,input_path,data_name):

    df = {"id":["1701"],"lon":[115.8136],"lat":[40.55861],"data0":[0]}
    df = pd.DataFrame(df)
    sta = nvb.sta_data(df)
    time0 = datetime.datetime(2020,1,7,8,0)
    end_time = datetime.datetime.now()

    sta_speed_all = nvb.read_stadata_from_csv(output_path)
    while time0 < end_time:
        sta_t = nvb.in_time_list(sta_speed_all,[time0])
        if len(sta_t.index) ==0:
            for dh in range(0,241,3):
                sta_dt = nvb.in_dtime_list(sta_t,[dh])
                if len(sta_dt.index) == 0:
                    path_speed = nvb.get_path(input_path,time0,dh)
                    if os.path.exists(path_speed):
                        grd_speed = nvb.read_griddata_from_nc(path_speed)
                        print(path_speed)
                        if grd_speed is not None:
                            sta1 = nvb.interp_gs_linear(grd_speed,sta)
                            nvb.set_stadata_coords(sta1,level=0,time=time0,dtime=dh)
                            sta_speed_all = nvb.combine_join(sta_speed_all,sta1)
                    #print(sta_speed_all)
        time0 = time0 + datetime.timedelta(hours=12)
    nvb.set_stadata_names(sta_speed_all,[data_name])
    sta_speed_all.to_csv(output_path)

#output_path = r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\timelist\EC_speed800.txt"
#input_path = r"H:\test_data\ecmwf\speed\800\BTYYMMDDHH.TTT.nc"
#extract(output_path,input_path,"ec800")
#output_path = r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\timelist\GRAPESspeed800.txt"
#input_path = r"H:\test_data\grapes_gfs\speed\800\YYMMDDHH.TTT"
#extract(output_path,input_path,"grapes800")

def download_ob():
    ip, port = nvb.read_gds_ip_port(r"H:\test_data\input\nvb\ip_port.txt")
    gds_dir = r"SURFACE/PLOT_10MIN_OLYMPIC"
    filename_list = nvb.path_tools.get_gds_file_list_in_one_dir(ip, port, gds_dir)
    value_list = ["测站高度","相对湿度","平均风向_2分钟","平均风速_2分钟","温度","气压"]
    dir = "H:/test_data/yanqing/"
    for filename in filename_list:
        for value in value_list:
            path_out = dir+value+"/"+filename
            if not os.path.exists(path_out):
                path_in = gds_dir + "/" + filename
                sta = nvb.read_stadata_from_gds(ip,port,path_in,element_id=nvb.gds_element_id_dict[value])
                if(sta is not None):
                    nvb.write_stadata_to_micaps3(sta,path_out,creat_dir=True)

download_ob()



def merge1():
    time0 = datetime.datetime(2020, 1, 7, 0, 0)
    dir  = r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\延庆赛区\10分钟数据集\A1701\YYYYMM\YYYYMMDD.csv"
    end_time = datetime.datetime.now()
    sta_ob_all = None
    while time0 < end_time:
        filename = nvb.get_path(dir,time0,0)
        if os.path.exists(filename):
            file = open(filename, 'r')
            sta = pd.read_csv(file, parse_dates=['观测时间'])
            sta = sta[["观测时间", "2分钟平均风速"]]
            sta.columns = ["time", "ob"]
            sta["id"] = 1701
            sta = nvb.sta_data(sta)
            nvb.set_stadata_coords(sta, level=0, dtime=0, lon=115.8136, lat=40.55861)

            sta_ob_all = nvb.combine_join(sta_ob_all,sta)
            #print(sta_ob_all)
        time0 = time0 + datetime.timedelta(hours=24)
    sta_ob_all.to_csv(r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\ob\speed_ob.txt")
def merge():
    sta_ob_all = nvb.read_stadata_from_csv(r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\ob\speed_ob.txt")
    sta_ec700 = nvb.read_stadata_from_csv(r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\ec\speed700.txt")
    sta_ec800 = nvb.read_stadata_from_csv(r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\ec\speed800.txt")
    #sta_ec700 = nvb.in_dtime_list(sta_ec700,[0])
    #sta_ec700 = nvb.in_time_list(sta_ec700,[datetime.datetime(2020,1,12,8,0)])
    #sta_ob_all = nvb.in_time_list(sta_ob_all,[datetime.datetime(2020,1,12,8,0)])
    #print(sta_ob_all)
    #print(sta_ec700)
    sta = nvb.in_time_list(sta_ec800,[datetime.datetime(2020,1,10,8,0)])
    print(sta)
    sta_all = nvb.combine_on_id_and_obTime(sta_ob_all,[sta_ec700,sta_ec800])
    print(sta_all)
    sta_all.to_csv(r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\ob_fo.txt")

#merge()

def plot():
    sta_all = nvb.read_stadata_from_csv(r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\ob_fo.txt")
    nvm.continuous.plot.scatter_regress()
#plot()

#grd = nvb.read_griddata_from_nc(r"H:\test_data\ecmwf\vgrd\700\20011008.015")
#nvb.write_griddata_to_micaps4(grd,r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据\a.txt")
