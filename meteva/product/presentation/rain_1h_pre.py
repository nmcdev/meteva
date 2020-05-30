import datetime
import meteva

para_example= {
    "day_num":3,
    "end_time":datetime.datetime.now(),
    "station_file":meteva.base.station_国家站,
    "defalut_value":0,
    "hdf_file_name":"week.h5",
    "ob_data":{
        "hdf_dir":r"O:\data\hdf\SURFACE\QC_BY_FSOL\RAIN01_ALL_STATION",
        "dir_ob": r"O:\data\sta\SURFACE\QC_BY_FSOL\RAIN01_ALL_STATION\YYYYMMDD\YYYYMMDDHH0000.000",
        "operation":None,
        "operation_para_dict":{}
    },
    "fo_data":{
        "GMOSRR":{
            "hdf_dir": r"O:\data\grid\GMOSRR\ROLLING_UPDATE\RAIN01",
            "dir_fo": r"O:\data\grid\GMOSRR\ROLLING_UPDATE\RAIN01\YYYYMMDD\YYMMDDHH.TTT.nc",
            "operation": None,
            "operation_para_dict":{}
        },
    },
    "output_dir":r"O:\data\hdf\combined\rain01"
}


if __name__ == '__main__':
    meteva.product.prepare_dataset(para_example)