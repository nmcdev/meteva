import datetime
import nmc_verification.nmc_vf_base.method.path_tools as path_tools
import nmc_verification.nmc_vf_base.io.read_griddata as rg
import nmc_verification.nmc_vf_base.io.read_stadata as rs
import nmc_verification.nmc_vf_base.io.write_griddata as wg
import nmc_verification.nmc_vf_base.io.write_stadata as ws
import nmc_verification.nmc_vf_base.function as fun
import nmc_verification.nmc_vf_base.basicdata as bd
import nmc_verification.nmc_vf_method.yes_or_no as yes_or_no
#设置路径通配格式
dir_fo = "G:/TRAPS/1822MANGKHUT_GFS_YYYYMMDDHH_d02.TTT"
dir_ob = "G:/r01_2018/YYMMDDHH.000"

#读取网格预报，累加成24小时降水量
time_fo = datetime.datetime(2018,9,15,12)
grid = bd.grid([105,115,0.5],[18,30,0.5])
sum_fo = None
for dh in range(18,37,6):
    path = path_tools.get_path(dir_fo,time_fo,dh)
    sta = rs.read_from_micaps3(path)
    grd = fun.sxy_gxy.transform(sta)
    sum_fo = fun.gxy_gxy.add(sum_fo,grd)
#输出累积降水量
#wg.write_to_micaps4(sum_fo)


#读取站点观测数据，累加成24小时降水量
station = rs.read_from_micaps3("国家站.txt")
station.iloc[:,7] = 0
grid_fo = bd.get_grid_of_data(sum_fo)
station = fun.get_from_sta.sta_in_grid_xy(station,grid_fo)

sum_ob = None
for dh in range(13,37,1):
    time_ob = time_fo + datetime.timedelta(hours=8+dh)
    path = path_tools.get_path(dir_ob,time_ob)
    #print(path)
    sta = rs.read_from_micaps3(path,station=station)
    #print(sta)
    sum_ob = fun.sxy_sxy.add_on_id(sum_ob,sta)

#ws.write_to_micaps3(sum_ob)

#提取站点观测数据列至一个numpy数组
ob = sum_ob.iloc[:,7].values

#采用最邻近点插值法将网格值插值到站点
sta_fo = fun.gxy_sxy.interpolation_nearest(sum_fo,station)

#提取站点观测数据列至一个numpy数组
fo = sta_fo.iloc[:,7].values

#设置检验阈值列表
thresholds = [0.1,10,25,50,100]

#计算检验结果
ts = yes_or_no.threshold_list.ts(ob,fo,threshold_list=thresholds)
print(ts)








