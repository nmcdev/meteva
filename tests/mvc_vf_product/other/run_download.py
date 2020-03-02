
para= {
    "cup_count":1,
    "ip_port_file":r"H:\test_data\input\nvb\ip_port.txt",
    "local_binary_dir":"O:/data/mdfs",
    "local_sta_dir": "O:/data/sta",
    "local_grid_dir":"O:/data/grid",
    "max_save_day":60,
    "sta_origin_dirs": [
        ["mdfs:///SURFACE/PLOT_NATIONAL", 0, 2359],
        ["mdfs:///SURFACE/RAIN24_NATIONAL_08-08", 0, 2359],
        ["mdfs:///SURFACE/RAIN24_NATIONAL_20-20/", 0, 2359],
        ["mdfs:///SURFACE/RAIN01_GLOBAL_STATION/", 0, 2359],
        ["mdfs:///SURFACE/QC_BY_FSOL/RAIN01_ALL_STATION/", 0, 2359],
        ["mdfs:///SURFACE/QC_BY_FSOL/WIND_AVERAGE_10MIN_ALL_STATION/", 0, 2359],
        ["mdfs:///SURFACE/QC_BY_FSOL/WIND_AVERAGE_2MIN_ALL_STATION/", 0, 2359],
        ["mdfs:///SURFACE/QC_BY_FSOL/TMP_ALL_STATION/", 0, 2359],
        ["mdfs:///SURFACE/QC_BY_FSOL/TMP_MAX_ALL_STATION/", 0, 2359],
        ["mdfs:///SURFACE/QC_BY_FSOL/TMP_MIN_ALL_STATION/", 0, 2359],
        ["mdfs:///SURFACE/ATMOS/PM25_1H/", 0, 2359],
        ["mdfs:///SURFACE/PLOT_5MIN_OLYMPIC/", 0, 2359],
        ["mdfs:///SURFACE/PLOT_5MIN/", 0, 2359],
        ["mdfs:///SURFACE/PLOT_GLOBAL_1H/", 0, 2359],
        ["mdfs:///SURFACE/TMP_MAX_24H_ALL_STATION/", 0, 2359],
        ["mdfs:///SURFACE/TMP_MIN_24H_ALL_STATION/", 0, 2359],
        ["mdfs:///SURFACE/TMP_MAX_24H_GLOBAL_STATION/", 0, 2359],
        ["mdfs:///SURFACE/TMP_MIN_24H_GLOBAL_STATION/", 0, 2359],
        ["mdfs:///SURFACE/SNOW_DEPTH_NATIONAL/", 0, 2359],
        ["mdfs:///SURFACE/SNOW_DEPTH_GLOBAL_STATION/", 0, 2359],
    ],
    "grid_origin_dirs":{
        "awx": [

        ],
        "NWFD_SCMOC": [
            ["NWFD_SCMOC/LAND_WEATHER_PHENOMENON/", 0, 2359],
            ["NWFD_SCMOC/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC/MINIMUM_RELATIVE_HUMIDITY/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC/PRECIPITATION_TYPE", 0, 2359],
            ["NWFD_SCMOC/RAIN03", 0, 2359],
            ["NWFD_SCMOC/RAIN03_GLOBAL", 0, 2359],
            ["NWFD_SCMOC/RAIN06", 0, 2359],
            ["NWFD_SCMOC/RAIN12", 0, 2359],
            ["NWFD_SCMOC/RAIN24", 0, 2359],
            ["NWFD_SCMOC/RH/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC/TCDC", 0, 2359],
            ["NWFD_SCMOC/TMP/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC/TMP_CHANGE_24H/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC/TMP_CHANGE_48H/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC/WIND/10M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC/VIS_SURFACE", 0, 2359],
        ],
        "NWFD_SCMOC_1H": [
            ["NWFD_SCMOC_1H/RAIN01", 0, 2359],
            ["NWFD_SCMOC_1H/RH/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC_1H/TCDC", 0, 2359],
            ["NWFD_SCMOC_1H/TMP/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC_1H/TMP_CHANGE_24H/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC_1H/TMP_CHANGE_48H/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SCMOC_1H/WIND/10M_ABOVE_GROUND", 0, 2359],
        ],
        "NWFD_SMERGE": [
            ["NWFD_SMERGE//MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SMERGE//MINIMUM_TEMPERATURE/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SMERGE/PRECIPITATION_TYPE", 0, 2359],
            ["NWFD_SMERGE/RAIN03", 0, 2359],
            ["NWFD_SMERGE/RH/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SMERGE/TCDC", 0, 2359],
            ["NWFD_SMERGE/TMP/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SMERGE/TMP_CHANGE_24H/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SMERGE/TMP_CHANGE_48H/2M_ABOVE_GROUND", 0, 2359],
            ["NWFD_SMERGE/WIND/10M_ABOVE_GROUND", 0, 2359],
        ],
        "EWMWF": [
            ["ECMWF_HR/DPT_2M/", 0, 2359],
            ["ECMWF_HR/LCDC/", 0, 2359],
            ["ECMWF_HR/MAXIMUM_TEMPERATURE_AT_2_METRES_IN_THE_LAST_3_HOURS/", 0, 2359],
            ["ECMWF_HR/MAXIMUM_TEMPERATURE_AT_2_METRES_IN_THE_LAST_6_HOURS/", 0, 2359],
            ["ECMWF_HR/MINIMUM_TEMPERATURE_AT_2_METRES_IN_THE_LAST_3_HOURS/", 0, 2359],
            ["ECMWF_HR/MINIMUM_TEMPERATURE_AT_2_METRES_IN_THE_LAST_6_HOURS/", 0, 2359],
            ["ECMWF_HR/PRECIPITATION_TYPE/", 0, 2359],
            ["ECMWF_HR/SKINT/", 0, 2359],
            ["ECMWF_HR/SNOD/", 0, 2359],
            ["ECMWF_HR/TCDC/", 0, 2359],
            ["ECMWF_HR/TMP_2M/", 0, 2359],
            ["ECMWF_HR/FZRA/", 0, 2359],
            ["ECMWF_HR/APCP/", 0, 2359],
            ["ECMWF_HR/ASNOW/", 0, 2359],
            ["mdfs:///ECMWF_HR/WIND_10M/", 0, 2359],
            ["mdfs:///ECMWF_HR/WIND/700/", 0, 2359],
            ["mdfs:///ECMWF_HR/WIND/800/", 0, 2359],
            ["mdfs:///ECMWF_HR/WIND/850/", 0, 2359],
            ["mdfs:///ECMWF_HR/WIND_100M/", 0, 2359],
            ["mdfs:///ECMWF_HR/10_METRE_WIND_GUST_IN_THE_LAST_3_HOURS/", 0, 2359],
            ["mdfs:///ECMWF_HR/10_METRE_WIND_GUST_IN_THE_LAST_6_HOURS/", 0, 2359],
            ["ECMWF_HR/VIS/", 0, 2359],
        ],
        "CLDAS": [
            ["CLDAS/MAXIMUM_RELATIVE_HUMIDITY/2M_ABOVE_GROUND", 0, 2359],
            ["CLDAS/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND", 0, 2359],
            ["CLDAS/MAX_WIND/10M_ABOVE_GROUND", 0, 2359],
            ["CLDAS/MINIMUM_RELATIVE_HUMIDITY/2M_ABOVE_GROUND", 0, 2359],
            ["CLDAS/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND", 0, 2359],
            ["CLDAS/RAIN01_BI_DATA_SOURCE", 0, 2359],
            ["CLDAS/RAIN01_TRI_DATA_SOURCE", 0, 2359],
            ["CLDAS/RAIN03_BI_DATA_SOURCE", 0, 2359],
            ["CLDAS/RAIN03_TRI_DATA_SOURCE", 0, 2359],
            ["CLDAS/RAIN24_BI_DATA_SOURCE", 0, 2359],
            ["CLDAS/RAIN24_TRI_DATA_SOURCE", 0, 2359],
            ["CLDAS/RH/2M_ABOVE_GROUND", 0, 2359],
            ["CLDAS/TCDC/", 0, 2359],
            ["CLDAS/TMP/2M_ABOVE_GROUND", 0, 2359],
            ["CLDAS/VIS", 0, 2359],
            ["CLDAS/WIND/10M_ABOVE_GROUND", 0, 2359],
        ],
        "BEIJING_9km": [
            ["BEIJING_MR/DPT/2M_ABOVE_GROUND", 0, 2359],
            ["BEIJING_MR/TCDC/ENTIRE_ATMOSPHERE", 0, 2359],
            ["BEIJING_MR/TMP/2M_ABOVE_GROUND", 0, 2359],
            ["BEIJING_MR/APCP", 0, 2359],
            ["BEIJING_MR/WATER_EQUIVALENT_OF_ACCUMULATED_SNOW_DEPTH", 0, 2359],
            ["BEIJING_MR/WIND/10M_ABOVE_GROUND", 0, 2359],
            ["BEIJING_MR/VIS", 0, 2359],
        ],
        "GMOSRR": [
            ["GMOSRR/ROLLING_UPDATE/RH/2M_ABOVE_GROUND/", 0, 2359],
            ["GMOSRR/ROLLING_UPDATE/TMP/2M_ABOVE_GROUND/", 0, 2359],
            ["mdfs:///GMOSRR/ROLLING_UPDATE/WIND/10M_ABOVE_GROUND/", 0, 2359],
        ],
        "GRAPES_3km": [
            ["GRAPES_3KM/DPT/2M_ABOVE_GROUND/", 0, 2359],
            ["mdfs:///GRAPES_3KM/MAX_WIND/10M_ABOVE_GROUND/", 0, 2359],
            ["GRAPES_3KM/SNOD/", 0, 2359],
            ["GRAPES_3KM/TCDC/", 0, 2359],
            ["GRAPES_3KM/TMP/2M_ABOVE_GROUND/", 0, 2359],
            ["GRAPES_3KM/APCP/", 0, 2359],
            ["GRAPES_3KM/ASNOW/", 0, 2359],
            ["mdfs:///GRAPES_3KM/WIND/10M_ABOVE_GROUND/", 0, 2359],
        ],
        "GRAPES_GFS": [
            ["GRAPES_GFS/DPT/2M_ABOVE_GROUND/", 0, 2359],
            ["mdfs:///GRAPES_GFS/WIND/10M_ABOVE_GROUND/", 0, 2359],
            ["GRAPES_GFS/MAXIMUM_RELATIVE_HUMIDITY/2M_ABOVE_GROUND/", 0, 2359],
            ["GRAPES_GFS/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND/", 0, 2359],
            ["GRAPES_GFS/MINIMUM_RELATIVE_HUMIDITY/2M_ABOVE_GROUND", 0, 2359],
            ["GRAPES_GFS/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND", 0, 2359],
            ["GRAPES_GFS/SNOD", 0, 2359],
            ["GRAPES_GFS/TCDC", 0, 2359],
            ["GRAPES_GFS/TMP/2M_ABOVE_GROUND", 0, 2359],
            ["GRAPES_GFS/APCP", 0, 2359],
            ["GRAPES_GFS/ASNOW", 0, 2359],
            ["GRAPES_GFS/WIND/800", 0, 2359],
        ],
        "GRAPES_MESO": [
            ["GRAPES_MESO_HR/DPT/2M_ABOVE_GROUND", 0, 2359],
            ["GRAPES_MESO_HR/MAX_WIND/10M_ABOVE_GROUND", 0, 2359],
            ["GRAPES_MESO_HR/SNOD", 0, 2359],
            ["GRAPES_MESO_HR/TCDC", 0, 2359],
            ["GRAPES_MESO_HR/TMP/2M_ABOVE_GROUND", 0, 2359],
            ["GRAPES_MESO_HR/APCP", 0, 2359],
            ["GRAPES_MESO_HR/ASNOW", 0, 2359],
            ["GRAPES_MESO_HR/WIND/10M_ABOVE_GROUND", 0, 2359],
        ],
        "GUANGZHOU_HR": [
            ["mdfs:///GUANGZHOU_HR/DPT/2M_ABOVE_GROUND/", 0, 2359],
            ["mdfs:///GUANGZHOU_HR/APCP/", 0, 2359],
            ["mdfs:///GUANGZHOU_HR/WIND/10M_ABOVE_GROUND/", 0, 2359],
            ["mdfs:///GUANGZHOU_HR/TMP/2M_ABOVE_GROUND/", 0, 2359],
            ["mdfs:///GUANGZHOU_HR/RH/2M_ABOVE_GROUND/", 0, 2359],
            ["mdfs:///GUANGZHOU_HR/VIS/", 0, 2359],
            ["mdfs:///GUANGZHOU_HR/TCDC/", 0, 2359],

        ],
        "NCEP_GFS_HR": [
            ["NCEP_GFS_HR/DPT/2M_ABOVE_GROUND/", 0, 2359],
            ["mdfs:///NCEP_GFS_HR/WIND/10M_ABOVE_GROUND/", 0, 2359],
            ["NCEP_GFS_HR/MAXIMUM_TEMPERATURE/2M_ABOVE_GROUND", 0, 2359],
            ["NCEP_GFS_HR/MINIMUM_TEMPERATURE/2M_ABOVE_GROUND", 0, 2359],
            ["NCEP_GFS_HR/SNOD", 0, 2359],
            ["NCEP_GFS_HR/TMP/SURFACE", 0, 2359],
            ["NCEP_GFS_HR/TCDC/ENTIRE_ATMOSPHERE", 0, 2359],
            ["NCEP_GFS_HR/TMP/2M_ABOVE_GROUND", 0, 2359],
            ["NCEP_GFS_HR/APCP", 0, 2359],
        ],
        "SHANGHAI_HR": [
            ["SHANGHAI_HR/DPT/2M_ABOVE_GROUND", 0, 2359],
            ["SHANGHAI_HR/TCDC/ENTIRE_ATMOSPHERE", 0, 2359],
            ["SHANGHAI_HR/TMP/2M_ABOVE_GROUND", 0, 2359],
            ["SHANGHAI_HR/APCP", 0, 2359],
            ["SHANGHAI_HR/WATER_EQUIVALENT_OF_ACCUMULATED_SNOW_DEPTH", 0, 2359],
            ["SHANGHAI_HR/WIND/10M_ABOVE_GROUND", 0, 2359],
            ["SHANGHAI_HR/VIS", 0, 2359],
        ],
    },
}

para1= {
    "cup_count":4,
    "ip_port_file":r"H:\test_data\input\nvb\ip_port.txt",
    "local_binary_dir":"O:/data/mdfs",
    "local_sta_dir": "O:/data/sta",
    "local_grid_dir":"O:/data/grid",
    "max_save_day":60,
    "sta_origin_dirs": [
        ["mdfs:///SURFACE/PLOT_5MIN/", 0, 2359],
    ],
    "grid_origin_dirs":{
        "EWMWF": [
            ["ECMWF_HR/DPT_2M/", 0, 2359],
            ["ECMWF_HR/LCDC/", 0, 2359],
            ["ECMWF_HR/MAXIMUM_TEMPERATURE_AT_2_METRES_IN_THE_LAST_3_HOURS/", 0, 2359],
            ["ECMWF_HR/MAXIMUM_TEMPERATURE_AT_2_METRES_IN_THE_LAST_6_HOURS/", 0, 2359],
            ["ECMWF_HR/MINIMUM_TEMPERATURE_AT_2_METRES_IN_THE_LAST_3_HOURS/", 0, 2359],
            ["ECMWF_HR/MINIMUM_TEMPERATURE_AT_2_METRES_IN_THE_LAST_6_HOURS/", 0, 2359],
            ["ECMWF_HR/PRECIPITATION_TYPE/", 0, 2359],
            ["ECMWF_HR/SKINT/", 0, 2359],
            ["ECMWF_HR/SNOD/", 0, 2359],
            ["ECMWF_HR/TCDC/", 0, 2359],
            ["ECMWF_HR/TMP_2M/", 0, 2359],
            ["ECMWF_HR/FZRA/", 0, 2359],
            ["ECMWF_HR/APCP/", 0, 2359],
            ["ECMWF_HR/ASNOW/", 0, 2359],
            ["mdfs:///ECMWF_HR/WIND_10M/", 0, 2359],
            ["mdfs:///ECMWF_HR/WIND/700/", 0, 2359],
            ["mdfs:///ECMWF_HR/WIND/800/", 0, 2359],
            ["mdfs:///ECMWF_HR/WIND/850/", 0, 2359],
            ["mdfs:///ECMWF_HR/WIND_100M/", 0, 2359],
            ["mdfs:///ECMWF_HR/10_METRE_WIND_GUST_IN_THE_LAST_3_HOURS/", 0, 2359],
            ["mdfs:///ECMWF_HR/10_METRE_WIND_GUST_IN_THE_LAST_6_HOURS/", 0, 2359],
            ["ECMWF_HR/VIS/", 0, 2359],
        ],

    },
}


import os
import shutil
import nmc_verification
def rename():
    dir = "O:/data/sta"
    file_list = nmc_verification.nmc_vf_base.tool.path_tools.get_path_list_in_dir(dir)
    for file in file_list:
        savepath,ft = os.path.splitext(file)
        if ft ==".nc":
            shutil.move(file,savepath)
        pass

from nmc_verification.nmc_vf_product.application.data_collection import download,remove
from multiprocessing import freeze_support
if __name__ == '__main__':

    #grd = nmc_verification.nmc_vf_base.read_griddata_from_nc(r"H:\2020022800FD024.nc",member = "pr24")
    #print(grd)
    freeze_support()
    download(para1)


