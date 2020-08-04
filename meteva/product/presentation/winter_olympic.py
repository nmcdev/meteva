import meteva
from meteva.product.presentation.gds_data_dict import *
from ipywidgets import widgets
import datetime

para_winter_olympic= {
    "day_num":7,
    "end_time":datetime.datetime.now(),
    "station_file":meteva.base.station_国家站,
    "interp": meteva.base.interp_gs_linear,
    "defalut_value":999999,
    "hdf_file_name":"winter_olympic_week.h5",
    "ob_data":{
        "hdf_dir":r"O:\data\hdf\SURFACE\QC_BY_FSOL\TMP_ALL_STATION",
        "dir_ob": r"O:\data\sta\SURFACE\QC_BY_FSOL\TMP_ALL_STATION\YYYYMMDD\YYYYMMDDHH0000.000",
        "read_method":meteva.base.io.read_stadata_from_gdsfile,
        "read_para":{},
        "operation":None,
        "operation_para":{}
    },
    "fo_data":{
        "ECMWF_2m":{
            "hdf_dir": r"O:\data\hdf\ECMWF_HR\TMP_2M",
            "dir_fo": r"O:\data\grid\ECMWF_HR\TMP_2M\YYYYMMDD\YYMMDDHH.TTT.nc",
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para_dict":{}
        },
        "ECMWF_800hPa": {
            "hdf_dir": r"O:\data\hdf\ECMWF_HR\TMP_2M",
            "dir_fo": r"O:\data\grid\ECMWF_HR\TEMP\YYYYMMDD\YYMMDDHH.TTT.nc",
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para_dict":{}
        }
    },
    "output_dir":r"O:\data\hdf\combined\temp_2m\winter_olympic"
}



id_lon_lat_dict = {
    "竞速1" :[651701,115.8136111,40.55861],
    "竞速3" :[651703,115.8036111,40.55583333],
    "竞速5" :[651705,115.8033333,40.54972222],
    "竞速8" :[651708,115.7977778,40.54111111],
    "竞技1" :[651710,115.815,40.55194444],
    "竞技2" :[651711,115.8133333,40.54972222],
    "竞技3" :[651712,115.8069444,40.5475],
    "西大庄科":[651489,115.7825	,40.52027778],
    "云顶1":[661620,115.42,40.95972222],
    "云顶2":[661627,115.4177778,40.95916667],
    "云顶4":[661629,115.4102778,40.95583333],
    "云顶6":[661637,115.4111111,40.95805556],
    "越野2":[661649,115.4738889,40.89805556],
    "越野3":[661650,115.4658333,40.90166667],
    "冬两1":[661638,115.4747222,40.90972222],
    "跳台2":[663158,115.4644444,40.91],
    "跳台3":[663159,115.4652778,40.90888889],
}


value_type_dict= {
    "平均风_2分钟": "风",
    "温度": "温度",
    "相对湿度": "相对湿度",
    "能见度": "能见度",
}

ob_name_dict = {
    "平均风_2分钟": "风",
    "温度": "温度",
    "相对湿度":"相对湿度",
    "能见度":"平均水平能见度_1分钟",
}
ob_s_name_dict = {
    "平均风_2分钟": "平均风速_2分钟",
}
ob_d_name_dict = {
    "平均风_2分钟": "平均风向_2分钟",
}

def ob_multi_fo_time(ob_element,model_name,model_level,station_id,max_dh):
    para = {
        "value_type": "wind",
        "local_root":"H:/test_data/input/nvb/binary1",
        "ip_port_file": ["/home/forecaster/config_met_io.ini",r"H:\test_data\input\nvb\ip_port.txt"],
        "ob_dir": r"SURFACE/PLOT_10MIN_OLYMPIC/YYYYMMDDHH0000.000",
        "ob_s_name":"speed",
        "ob_d_name":"direction",
        "ob_name":"data0",
        "fo_grd_dir": r"ECMWF_HR/TEMP/800/YYMMDDHH.TTT",
        "fo_grd_dir_u": r"ECMWF_HR/UGRD/800/YYMMDDHH.TTT",
        "fo_grd_dir_v": r"ECMWF_HR/VGRD/800/YYMMDDHH.TTT",
        "max_dh": 120,
        "update_hours": [8,20],
        "output_dir": None,
        "title": "EC_wind_800hPa_2min_3Hour",
        "station_id_list" : [651701],
        "station_lon_list":[115.8136],
        "station_lat_list": [40.55861],
    }
    value_type =  value_type_dict[ob_element]
    para["value_type"] = value_type
    if value_type == "风":
        para["ob_s_name"] = ob_s_name_dict[ob_element]
        para["ob_d_name"] = ob_d_name_dict[ob_element]
        if model_level not in fo_grd_dir_dict[model_name]["U"].keys():
            print(model_name + "没有" + model_level + "层的风场预报")
            return
        para["fo_grd_dir_u"] = fo_grd_dir_dict[model_name]["U"][model_level]
        para["fo_grd_dir_v"] = fo_grd_dir_dict[model_name]["V"][model_level]
    else:
        para["ob_name"] = ob_name_dict[ob_element]
        if value_type  not in fo_grd_dir_dict[model_name].keys():
            print(model_name + "没有" + value_type +"的预报")
            return
        elif model_level not in fo_grd_dir_dict[model_name][value_type].keys():
            print(model_name + "没有" +model_level+"层"+ value_type +"的预报")
            return
        para["fo_grd_dir"] = fo_grd_dir_dict[model_name][value_type][model_level]
    para["max_dh"] = max_dh
    para["update_hours"] = model_update_hours_dict[model_name]
    para["id"] = [id_lon_lat_dict[station_id][0]]
    para["lon"] = [id_lon_lat_dict[station_id][1]]
    para["lat"] = [id_lon_lat_dict[station_id][2]]
    para["title"] = model_name+"_"+ model_level+"_"+value_type+"_"+"观测"+ob_element+"("+station_id+")"
    meteva.nmc_vf_product.gds_ob_multi_time_fo(para)


tb_ob_element = widgets.ToggleButtons(
    options=value_type_dict.keys(),
    description='观测要素:',
    disabled=False,
)
tb_model_name = widgets.ToggleButtons(
    options=fo_grd_dir_dict.keys(),
    description='模式:',
    disabled=False,
)

tb_model_level = widgets.ToggleButtons(
    options=['850hPa','800hPa', '700hPa', "10M","2M"],
    description='模式层次:',
    disabled=False,
)
tb_station_id =  widgets.ToggleButtons(
    options=id_lon_lat_dict.keys(),
    description='站点:',
    disabled=False,
)
tb_max_dh =  widgets.ToggleButtons(
    options=[24,36,48,60,72,96,120,144,168,240],
    description='覆盖时效:',
    disabled=False,
)

