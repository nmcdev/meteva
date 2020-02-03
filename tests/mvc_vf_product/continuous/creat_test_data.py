import nmc_verification.nmc_vf_base as nvb
import datetime


dir_input = r"Z:\data\surface\t1\YYMMDDHH.000"
dir_output = r"H:\test_data\input\nvp\ob\temp_2m\BTYYMMDDHH.000"
time0 = datetime.datetime(2019,1,1,2,0)
now = datetime.datetime(2020,1,29,8,0)
station = nvb.read_station(nvb.station_国家站)

grid0 = nvb.grid([116,117,0.5],[40,41,0.5])
station = nvb.in_grid_xy(station,grid0)
station["data0"] = nvb.IV
print(station)
while time0 < now:
    path_input = nvb.get_path(dir_input,time0)
    sta = nvb.read_stadata_from_micaps3(path_input,station,level=0,time = time0,dtime = 0)
    if sta is not None:
        path_output = nvb.get_path(dir_output,time0)
        nvb.write_stadata_to_micaps3(sta,save_path=path_output,creat_dir=True,effectiveNum=1)
        print(path_output)
    time0 = time0 + datetime.timedelta(hours=3)