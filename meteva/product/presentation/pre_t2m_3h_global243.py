import datetime
import meteva
import pandas as pd

para_r45= {
    "day_num":7,
    "end_time":datetime.datetime.now(),
    "station_file":meteva.base.station_全球重点城市,
    "defalut_value":999999,
    "interp": None,
    "hdf_file_name":"t2m_week_r45.h5",
    "ob_data":{
        "hdf_dir":r"F:\veri_report\global\t2m\OBS243",
        "dir_ob": r"X:\For Verification\OBS\TEM\YYYYMMDDHH.h5",
        "read_method": pd.read_hdf,
        "read_para": {},
        "operation":None,
        "operation_para":{}
    },
    "fo_data":{
        "Station_243":{
            "hdf_dir": r"F:\veri_report\global\t2m\Station_243",
            "dir_fo": r"X:\For Verification\Station_243\YYYYMMDDHH\t2m\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para":{}
        },
        "Station_243_Blend": {
            "hdf_dir": r"F:\veri_report\global\t2m\Station_243_Blend",
            "dir_fo": r"X:\For Verification\Station_243_Blend\YYYYMMDDHH\t2m\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para": {}
        },

        "GRID_243":{
            "hdf_dir": r"F:\veri_report\global\t2m\GRID_243",
            "dir_fo": r"X:\For Verification\GRID_243\YYYYMMDDHH\tem\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para":{}
        },

        "WEATHER": {
            "hdf_dir": r"F:\veri_report\global\t2m\WEATHER",
            "dir_fo": r"X:\For Verification\Station_WEATHER\YYYYMMDDHH\t2m\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para": {}
        },
        "DARKSKY": {
            "hdf_dir": r"F:\veri_report\global\t2m\Station_DARKSKY",
            "dir_fo": r"X:\For Verification\Station_DARKSKY\YYYYMMDDHH\t2m\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para": {}
        }
    },
    "output_dir":r"F:\veri_report\global\t2m"
}


para_r168= {
    "day_num":7,
    "end_time":datetime.datetime.now(),
    "station_file":meteva.base.station_全球重点城市,
    "defalut_value":999999,
    "interp": None,
    "hdf_file_name":"t2m_week_r168.h5",
    "ob_data":{
        "hdf_dir":r"F:\veri_report\global\t2m\OBS243",
        "dir_ob": r"X:\For Verification\OBS\TEM\YYYYMMDDHH.h5",
        "read_method": pd.read_hdf,
        "read_para": {},
        "operation":None,
        "operation_para":{}
    },
    "fo_data":{
        "Station_243":{
            "hdf_dir": r"F:\veri_report\global\t2m\Station_243",
            "dir_fo": r"X:\For Verification\Station_243\YYYYMMDDHH\t2m\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para":{}
        },
        "Station_243_Blend": {
            "hdf_dir": r"F:\veri_report\global\t2m\Station_243_Blend",
            "dir_fo": r"X:\For Verification\Station_243_Blend\YYYYMMDDHH\t2m\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para": {}
        },

        "GRID_243":{
            "hdf_dir": r"F:\veri_report\global\t2m\GRID_243",
            "dir_fo": r"X:\For Verification\GRID_243\YYYYMMDDHH\tem\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para":{}
        },

        "DARKSKY": {
            "hdf_dir": r"F:\veri_report\global\t2m\Station_DARKSKY",
            "dir_fo": r"X:\For Verification\Station_DARKSKY\YYYYMMDDHH\t2m\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para": {}
        }
    },
    "output_dir":r"F:\veri_report\global\t2m"
}

para_r240= {
    "day_num":7,
    "end_time":datetime.datetime.now(),
    "station_file":meteva.base.station_全球重点城市,
    "defalut_value":999999,
    "interp": None,
    "hdf_file_name":"t2m_week_r240.h5",
    "ob_data":{
        "hdf_dir":r"F:\veri_report\global\t2m\OBS243",
        "dir_ob": r"X:\For Verification\OBS\TEM\YYYYMMDDHH.h5",
        "read_method": pd.read_hdf,
        "read_para": {},
        "operation":None,
        "operation_para":{}
    },
    "fo_data":{
        "Station_243":{
            "hdf_dir": r"F:\veri_report\global\t2m\Station_243",
            "dir_fo": r"X:\For Verification\Station_243\YYYYMMDDHH\t2m\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para":{}
        },
        "Station_243_Blend": {
            "hdf_dir": r"F:\veri_report\global\t2m\Station_243_Blend",
            "dir_fo": r"X:\For Verification\Station_243_Blend\YYYYMMDDHH\t2m\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para": {}
        },

        "GRID_243":{
            "hdf_dir": r"F:\veri_report\global\t2m\GRID_243",
            "dir_fo": r"X:\For Verification\GRID_243\YYYYMMDDHH\tem\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para":{}
        },

        "DARKSKY": {
            "hdf_dir": r"F:\veri_report\global\t2m\Station_DARKSKY",
            "dir_fo": r"X:\For Verification\Station_DARKSKY\YYYYMMDDHH\t2m\YYYYMMDDHH.TTT.h5",
            "read_method": pd.read_hdf,
            "read_para": {},
            "operation": None,
            "operation_para": {}
        }
    },
    "output_dir":r"F:\veri_report\global\t2m"
}

if __name__ == '__main__':
    meteva.product.prepare_dataset(para_r45)
    meteva.product.prepare_dataset(para_r168)
    meteva.product.prepare_dataset(para_r240)