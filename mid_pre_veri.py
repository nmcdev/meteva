

import nmc_verification as nv
import datetime
import numpy as np

dir_ob = r"H:\task\other\201906-veri_middle_range\data\m3\jian_rr\YYMMDDHH.000"
dir_station = r"H:\task\other\201906-veri_middle_range\data\sta2513.txt"
station = nv.nmc_vf_base.io.read_stadata.read_from_micaps3(dir_station)
time0 = datetime.datetime(2019,4,30,8,0)
etime = datetime.datetime(2019,5,1,8,0)
grade_list = [0.1,10,25,50,100]
models = ["预报员","MPI","网格预报"]
model_dirs = [r"H:\task\other\201906-veri_middle_range\data\m3\rr\YYMMDDHH.TTT",
              r"H:\task\other\201906-veri_middle_range\data\m3\mpi\YYMMDDHH.TTT",
              r"H:\task\other\201906-veri_middle_range\data\m3\grid\YYYYMMDDHH.TTT"]
sta_all = None

while time0 <etime:
    time0 = time0 + datetime.timedelta(hours=24)
    for dh in range(96,121,24):
        time1 = time0 + datetime.timedelta(hours=dh)
        path = nv.nmc_vf_base.method.path_tools.get_path(dir_ob,time1)
        sta_ob = nv.nmc_vf_base.io.read_stadata.read_from_micaps3(path,station = station)
        if sta_ob is None:continue
        nv.nmc_vf_base.set_data_name(sta_ob, "ob")
        all_models = True
        sta_merge = sta_ob
        sta_merge['dtime'] = np.timedelta64(dh,'h')
        for m in range(len(models)):
            path = nv.nmc_vf_base.method.path_tools.get_path(model_dirs[m],time0,dh)
            sta_fo = nv.nmc_vf_base.io.read_stadata.read_from_micaps3(path,station = station)
            if sta_fo is None:
                all_models = False
                break
            nv.nmc_vf_base.set_data_name(sta_fo,models[m])
            sta_merge = nv.nmc_vf_base.function.put_into_sta_data.merge(sta_merge,sta_fo)
            #print(sta_merge)
            #print("a")
        if all_models:
            sta_all = nv.nmc_vf_base.function.put_into_sta_data.join(sta_all,sta_merge)
#print(sta_all)

sta_data_set = nv.nmc_vf_product.perspective.sta_data_set(sta_all)
sta_data_set.set_dhour_unfold()
veri_result = nv.nmc_vf_product.perspective.veri_result_set(["ts",'bias'],[0.1,10,25,50,100],sta_data_set)
result = veri_result.get_veri_result()
plot_set = nv.nmc_vf_product.perspective.veri_plot_set(subplot="method",legend="member",axis="dhour")

plot_set.bar(result)

#print(result)


