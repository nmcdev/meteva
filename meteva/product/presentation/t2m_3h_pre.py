import datetime
import meteva

para_example= {
    "day_num":7,
    "end_time":datetime.datetime.now(),
    "station_file":meteva.base.station_国家站,
    "defalut_value":999999,
    "interp": meteva.base.interp_gs_linear,
    "hdf_file_name":"week.h5",
    "ob_data":{
        "hdf_dir":r"O:\data\hdf\SURFACE\QC_BY_FSOL\TMP_ALL_STATION",
        "dir_ob": r"O:\data\sta\SURFACE\QC_BY_FSOL\TMP_ALL_STATION\YYYYMMDD\YYYYMMDDHH0000.000",
        "read_method": meteva.base.io.read_stadata_from_gdsfile,
        "read_para": {},
        "operation":None,
        "operation_para":{}
    },
    "fo_data":{
        "SCMOC":{
            "hdf_dir": r"O:\data\hdf\NWFD_SCMOC\TMP\2M_ABOVE_GROUND",
            "dir_fo": r"O:\data\grid\NWFD_SCMOC\TMP\2M_ABOVE_GROUND\YYYYMMDD\YYMMDDHH.TTT.nc",
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para":{}
        },
        "GRAPES": {
            "hdf_dir": r"O:\data\hdf\GRAPES_GFS\TMP\2M_ABOVE_GROUND",
            "dir_fo": r"O:\data\grid\GRAPES_GFS\TMP\2M_ABOVE_GROUND\YYYYMMDD\YYMMDDHH.TTT.nc",
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para": {}
        },
        "ECMWF":{
            "hdf_dir": r"O:\data\hdf\ECMWF_HR\TMP_2M",
            "dir_fo": r"O:\data\grid\ECMWF_HR\TMP_2M\YYYYMMDD\YYMMDDHH.TTT.nc",
            "read_method": meteva.base.io.read_griddata_from_nc,
            "read_para": {},
            "operation": None,
            "operation_para":{}
        }
    },
    "output_dir":r"O:\data\hdf\combined\temp_2m"
}


if __name__ == '__main__':
    meteva.product.prepare_dataset(para_example)