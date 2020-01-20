import nmc_verification
from nmc_verification.nmc_vf_product.presentation.gds_data_dict import *

def pr_ob_multi_fo_time(ob_element,model_name,model_element,level,station_id,max_dh):
    para = {
        "value_type": "wind",
        "ip_port_file": r"H:\test_data\input\nvb\ip_port.txt",
        "ob_dir": r"SURFACE/PLOT_10MIN_OLYMPIC/YYYYMMDDHH0000.000",
        "ob_s_name":"speed",
        "ob_d_name":"direction",
        "ob_name":"data0",
        "fo_grd_dir": r"ECMWF_HR/TEMP/800/YYMMDDHH.TTT",
        "fo_grd_dir_u": r"ECMWF_HR/UGRD/800/YYMMDDHH.TTT",
        "fo_grd_dir_v": r"ECMWF_HR/VGRD/800/YYMMDDHH.TTT",
        "max_dh": 120,
        "ddh": 3,
        "update_hours": [8,20],
        "output_dir": r"H:\task\other\201911-预报司-冬奥会检验\冬奥观测数据",
        "title": "EC_wind_800hPa_2min_3Hour",
        "station_id_list" : [651701],
        "station_lon_list":[115.8136],
        "station_lat_list": [40.55861],
    }
    para["value_type"] = ob_element
    para["value_type"] = value_type_dict[ob_element]
    para["ob_s_name"] = ob_s_name_dict[ob_element]
    para["ob_d_name"] = ob_d_name_dict[ob_element]
    if model_element == "风":
        para["fo_grd_dir_u"] = fo_grd_dir_dict[model_name]["U"][level]
        para["fo_grd_dir_v"] = fo_grd_dir_dict[model_name]["V"][level]
    else:
        para["fo_grd_dir"] = fo_grd_dir_dict[model_name][model_element][level]
    para["output_dir"] = None
    para["id"] = id_dict[station_id]
    para["max_dh"] = max_dh
    para["title"] = model_name+"_"+ level+"_"+model_element+"_"+"观测"+ob_element+"("+station_id+")"
    para["refresh"] = model_update_hours_dict[model_name]
    nmc_verification.nmc_vf_product.application.ap_ob_multi_time_fo(para)
