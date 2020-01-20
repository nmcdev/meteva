import nmc_verification.nmc_vf_base as nvb
import nmc_verification.nmc_vf_product as nvp
import datetime
import os
import pandas as pd
import numpy as np
import matplotlib.colors as colors
import matplotlib.pyplot as plt
import copy
import time

para ={
    "value_type":"wind",
    "ip_port_file":r"H:\test_data\input\nvb\ip_port.txt",
    "ob_dir":r"SURFACE/PLOT_10MIN_OLYMPIC/YYYYMMDDHH0000.000",
    "fo_grd_dir":None,
    "fo_grd_dir_u":r"ECMWF_HR/UGRD/800/YYMMDDHH.TTT",
    "fo_grd_dir_v":r"ECMWF_HR/VGRD/800/YYMMDDHH.TTT",
    "max_dh":120,
    "ddh":3,
    "dfo":12,
    "output_dir": r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据",
    "station_file":"station.txt",
    "title":"EC_wind_800hPa_2min_3Hour",
    "temp_fo":"temp_fo.txt"
}


def ob_multi_time_fo(para):
    begin = time.time()
    now = datetime.datetime.now()
    now = datetime.datetime(now.year, now.month, now.day, now.hour, 0)
    station = nvb.read_stadata_from_micaps3(para["station_file"])
    id_list = station["id"].values.tolist()
    ip, port = nvb.read_gds_ip_port(r"H:\test_data\input\nvb\ip_port.txt")
    if para["value_type"] == "wind":
        sta_ob_s_all = None
        sta_ob_d_all = None
        for i in range(para["max_dh"] + 12):
            time0 = now - datetime.timedelta(hours=i)
            path = nvb.get_path(para["ob_dir"], time0)
            sta_s = nvb.read_stadata_from_gds(ip, port, filename=path, element_id=nvb.gds_element_id.平均风速_2分钟)
            if sta_s is None: continue
            sta_ob_s_all = nvb.combine_join(sta_ob_s_all, sta_s)
            sta_d = nvb.read_stadata_from_gds(ip, port, filename=path, element_id=nvb.gds_element_id.平均风向_2分钟)
            if sta_d is None: continue
            sta_ob_d_all = nvb.combine_join(sta_ob_s_all, sta_d)
        sta_ob_all = nvb.diag.speed_angle_to_wind(sta_ob_s_all, sta_ob_d_all)

        dir_u, file_u = os.path.split(para["fo_grd_dir_u"])
        file_list_u = nvb.path_tools.get_gds_file_list_in_one_dir(ip, port, dir_u)
        dir_v, file_v = os.path.split(para["fo_grd_dir_v"])
        file_list_v = nvb.path_tools.get_gds_file_list_in_one_dir(ip, port, dir_v)
        # 读取预报数据
        sta_fo_all = None
        for i in range(para["max_dh"] + 12):
            time0 = now - datetime.timedelta(hours=i)
            for dh in range(para["max_dh"]):
                filename = nvb.get_path(file_u, time0, dh)
                if not filename in file_list_u: continue
                # grd = nvb.read_griddata_from_gds(ip,port,dir_u + "/"+filename)
                # if(grd is None):continue
                # sta_u = nvb.interp_gs_linear(grd,station)
                sta_u = nvb.read_stadata_from_gds_griddata(ip, port, dir_u + "/" + filename, station)
                if (sta_u is None): continue
                nvb.set_stadata_coords(sta_u, time=time0, dtime=dh)
                path = nvb.get_path(file_v, time0, dh)
                if not filename in file_list_v: continue
                # grd = nvb.read_griddata_from_gds(ip,port,dir_v + "/" + filename)
                # if (grd is None): continue
                # sta_v = nvb.interp_gs_linear(grd,station)
                sta_v = nvb.read_stadata_from_gds_griddata(ip, port, dir_v + "/" + filename, station)
                if sta_v is None: continue
                nvb.set_stadata_coords(sta_v, time=time0, dtime=dh)
                sta_uv = nvb.combine_on_all_coords(sta_u, sta_v)

                nvb.set_stadata_names(sta_uv, data_name_list=["u" + para["title"], "v" + para["title"]])
                sta_fo_all = nvb.combine_join(sta_fo_all, sta_uv)

        for id in id_list:
            output_path = para["output_dir"]
            if (output_path is not None):
                output_path = nvb.get_path(output_path, now)
                output_path = output_path + "/" + str(id) + ".png"
            sta_ob = nvb.in_id_list(sta_ob_all, [id])
            sta_fo = nvb.in_id_list(sta_fo_all, [id])
            nvp.continuous.wind_ob_and_multi_time_fo(sta_ob, sta_fo, pic_path=output_path, max_dh=para["max_dh"],
                                                     plot_error=True)
    else:
        sta_ob_all = None
        sta_ob_all = None
        for i in range(para["max_dh"] + 12):
            time0 = now - datetime.timedelta(hours=i)
            path = nvb.get_path(para["ob_dir"], time0)
            sta_s = nvb.read_stadata_from_gds(ip, port, filename=path, element_id=nvb.gds_element_id_dict[para["value_type"]])
            if sta_s is None: continue
            sta_ob_all = nvb.combine_join(sta_ob_all, sta_s)

        dir_u, file_u = os.path.split(para["fo_grd_dir_u"])
        file_list_u = nvb.path_tools.get_gds_file_list_in_one_dir(ip, port, dir_u)
        # 读取预报数据
        sta_fo_all = None
        for i in range(para["max_dh"] + 12):
            time0 = now - datetime.timedelta(hours=i)
            for dh in range(para["max_dh"]):
                filename = nvb.get_path(file_u, time0, dh)
                if not filename in file_list_u: continue
                sta_u = nvb.read_stadata_from_gds_griddata(ip, port, dir_u + "/" + filename, station)
                if (sta_u is None): continue
                nvb.set_stadata_names(sta_u, data_name_list=[para["title"]])
                sta_fo_all = nvb.combine_join(sta_fo_all, sta_u)

        for id in id_list:
            output_path = para["output_dir"]
            if (output_path is not None):
                output_path = nvb.get_path(output_path, now)
                output_path = output_path + "/" + str(id) + ".png"
            sta_ob = nvb.in_id_list(sta_ob_all, [id])
            sta_fo = nvb.in_id_list(sta_fo_all, [id])
            if para["value_type"] == "温度":
                nvp.continuous.temp_ob_and_multi_time_fo(sta_ob, sta_fo, pic_path=output_path, max_dh=para["max_dh"],
                                                     plot_error=True)
            elif para["value_type"] == "降水1h":
                pass

if __name__ == "__main__":
    ob_multi_time_fo(para)