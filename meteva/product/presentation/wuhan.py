import meteva
from meteva.product.presentation.gds_data_dict import *
from ipywidgets import widgets

id_lon_lat_dict = {
    "火神山" :[811739,114.0942,30.5319],
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
        "ip_port_file": r"H:\test_data\input\nvb\ip_port.txt",
        "ob_dir": r"SURFACE/PLOT_ALL/YYYYMMDDHH0000.000",
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
    para["station_id_list"] = [id_lon_lat_dict[station_id][0]]
    para["station_lon_list"] = [id_lon_lat_dict[station_id][1]]
    para["station_lat_list"] = [id_lon_lat_dict[station_id][2]]
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
