
fo_grd_dir_dict = {
    "ECMWF" :{
        "temp" :{
            "2M" :"ECMWF_HR/UGRD/TMP_2M/YYMMDDHH.TTT",
            "800hPa" :"ECMWF_HR/UGRD/TMP/800/YYMMDDHH.TTT"
        },
        "U" :{
            "10M" :r"ECMWF_HR/UGRD_10M/YYMMDDHH.TTT",
            "100M": r"ECMWF_HR/UGRD_100M/YYMMDDHH.TTT",
            "800hPa" :r"ECMWF_HR/UGRD/800/YYMMDDHH.TTT",
            "700hPa" :r"ECMWF_HR/UGRD/700/YYMMDDHH.TTT"
        },
        "V" :{
            "10M": r"ECMWF_HR/VGRD_10M/YYMMDDHH.TTT",
            "100M": r"ECMWF_HR/VGRD_100M/YYMMDDHH.TTT",
            "800hPa": r"ECMWF_HR/VGRD/800/YYMMDDHH.TTT",
            "700hPa": r"ECMWF_HR/VGRD/700/YYMMDDHH.TTT"
        }
    }
}
model_update_hours_dict = {
    "ECMWF":[8,20]
}
id_dict = {
    "竞赛1号站" :651801,
}
value_type_dict = {
    "平均风_2分钟": "wind"
}
ob_s_name_dict = {
    "平均风_2分钟": "平均风速_2分钟",
}
ob_d_name_dict = {
    "平均风_2分钟": "平均风向_2分钟",
}

