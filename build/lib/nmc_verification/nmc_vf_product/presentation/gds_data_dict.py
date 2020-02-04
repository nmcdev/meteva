
fo_grd_dir_dict = {
    "ECMWF" :{
        "温度" :{
            "2M" :"ECMWF_HR/TMP_2M/YYMMDDHH.TTT",
            "800hPa" :"ECMWF_HR/TMP/800/YYMMDDHH.TTT",
            "700hPa" :"ECMWF_HR/TMP/700/YYMMDDHH.TTT",
            "850hPa" :"ECMWF_HR/TMP/850/YYMMDDHH.TTT",
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
        },
        "能见度":{
            "2M" :r"ECMWF_HR/VIS/YYMMDDHH.TTT",
        },
        "相对湿度":{
            "800hPa": "ECMWF_HR/RH/800/YYMMDDHH.TTT",
            "700hPa": "ECMWF_HR/RH/700/YYMMDDHH.TTT",
            "850hPa": "ECMWF_HR/RH/850/YYMMDDHH.TTT",
        }

    }
}
model_update_hours_dict = {
    "ECMWF":[8,20],
    "GRAPES_GFS":[8,20],
    "NCEP":[8,20],
}


