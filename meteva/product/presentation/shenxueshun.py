import meteva
import datetime

para_example= {
    "day_num":60,
    "end_time":datetime.datetime(2014,12,31,8,0),
    "station_file":meteva.base.station_国家站,
    "defalut_value":0,
    "interp": meteva.base.interp_gs_nearest,
    "hdf_file_name":"years.h5",
    "keep_IV":False,
    "ob_data":{
        "hdf_dir":r"E:\hdf\rain24\ob",
        "dir_ob": r"D:\r20\YYMMDDHH.000",
        "read_method": meteva.base.io.read_stadata_from_micaps3,
        "read_para": {},
        "operation":None,
        "operation_para":{}
    },
    "fo_data":{
        "MESO":{
            "hdf_dir":r"E:\hdf\rain24\meso",
            "dir_fo": r"F:\shenxueshun\meso\rain24\YYYYMM\YYMMDDHH.TTT.nc",
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para":{}
        },
    },
    "output_dir":r"E:\hdf\rain24"
}

meteva.product.prepare_dataset(para_example)