
import datetime
import  nmc_verification as nv
import nmc_verification.nmc_vf_base.method.path_tools as pt
import nmc_verification.nmc_vf_base as nvb

station = nvb.io.read_station(nvb.sta)





# 累加观测文件
def ca_ob():
    dir = r"H:\task\other\201906-中期检验\data\sta2513.txt"
    station = nv.nmc_vf_base.io.read_stadata.read_from_micaps3(dir)

    dir = r"H:\task\other\201906-中期检验\data\ob\YYYYMMDDHH.000"
    time1 = datetime.datetime(2019,1,2,8)
    time_end = datetime.datetime(2019,6,12,8)
    dir_out = r"H:\task\other\201906-中期检验\data\m3\ob\YYYYMMDDHH.000"
    while time1 < time_end:
        rain24 = None
        for dh in range(-23,1,1):
            time0 = time1 + datetime.timedelta(hours= dh)
            path = pt.get_path(dir,time0)
            rain01 = nv.nmc_vf_base.io.read_stadata.read_from_micaps3(path,station= station)
            rain24 = nv.nmc_vf_base.function.sxy_sxy.add_on_id(rain24,rain01)
            print(rain24)
            print(len(rain24.index))
            print(len(rain01.index))
        path = pt.get_path(dir_out,time0)
        nv.nmc_vf_base.io.write_stadata.write_to_micaps3(rain24,path)
        print(time1)

#ca_ob()


# 网格预报转站点
def grid_to_sta():
    dir = r"H:\task\other\201906-veri_middle_range\data\sta2513.txt"
    station = nv.nmc_vf_base.io.read_stadata.read_from_micaps3(dir)
    dir_in = r"H:\task\other\201906-veri_middle_range\data\nc\grid\RAIN24\YYMMDD\YYMMDDHH.TTT.nc"
    time1 = datetime.datetime(2019,1,1,8)
    time_end = datetime.datetime(2019,6,12,8)
    dir_out = r"H:\task\other\201906-veri_middle_range\data\m3\grid\YYYYMMDDHH.TTT"
    while time1 < time_end:
        for dh in range(24,241,24):
            path = pt.get_path(dir_in,time1,dh)
            grd = nv.nmc_vf_base.io.read_griddata.read_from_nc(path)
            if(grd is not None):
                sta = nv.nmc_vf_base.function.gxy_sxy.interpolation_nearest(grd,station)
                path = pt.get_path(dir_out,time1,dh)
                nv.nmc_vf_base.io.write_stadata.write_to_micaps3(sta,path)
                print(path)
            #print(sta)
            #print(rain24)
        time1 = time1 + datetime.timedelta(hours=24)
#grid_to_sta()

# 检验计算
import  numpy as np
import  os
dir_ob =  r"H:\task\other\201906-veri_middle_range\data\m3\jian_rr\YYMMDDHH.000"
dir_model = [r"H:\task\other\201906-veri_middle_range\data\m3\rr\YYMMDDHH.TTT",
             r"H:\task\other\201906-veri_middle_range\data\m3\mpi\YYMMDDHH.TTT",
             r"H:\task\other\201906-veri_middle_range\data\m3\grid\YYYYMMDDHH.TTT"]

dir = r"H:\task\other\201906-veri_middle_range\data\sta2513.txt"
station = nv.nmc_vf_base.io.read_stadata.read_from_micaps3(dir)

def veri():
    hit = np.zeros((4,3,5))
    mis = np.zeros(hit.shape)
    fal = np.zeros(hit.shape)
    thre_list = [0.1,10,25,50,100]
    for dh in range(96,169,24):
        time1 = datetime.datetime(2019, 1, 1, 8)
        time_end = datetime.datetime(2019, 6, 1, 8)
        i = int(dh /24 - 4)
        while time1 < time_end:
            time_ob = time1 + datetime.timedelta(hours=dh)
            path_ob = pt.get_path(dir_ob,time_ob)
            sta_ob = nv.nmc_vf_base.io.read_stadata.read_from_micaps3(path_ob,station=station)
            print(sta_ob)

            if(sta_ob is not None):
                ob = sta_ob['data0'].values
                ob[ob>1000] = 0
                print(ob)
                all_model = True
                sta_fo_list = []
                for m in range(len(dir_model)):
                    path_fo = pt.get_path(dir_model[m],time1,dh)
                    sta_fo = nv.nmc_vf_base.io.read_stadata.read_from_micaps3(path_fo,station=station)
                    if(sta_fo is  None):
                        all_model = False
                        break
                    else:
                        sta_fo_list.append(sta_fo)
                if(all_model):
                    for m in range(len(dir_model)):
                        sta_fo = sta_fo_list[m]
                        fo = sta_fo['data0'].values
                        #print(fo)
                        hit1,mis1,fal1,_ = nv.nmc_vf_method.yes_or_no.threshold_list.hmfn(ob,fo,threshold_list=thre_list)
                        #print(hit1)
                        hit[i,m,:] += hit1
                        mis[i,m,:] += mis1
                        fal[i,m,:] += fal1

            time1 = time1 + datetime.timedelta(hours = 24)

    ts = hit/(hit + mis +fal + 0.00001)
    bias = (hit + fal)/(hit +mis +0.00001)
    print(ts)
    for i in range(len(thre_list)):
        filename = "ts" + str(i) + ".txt"
        np.savetxt(filename,ts[:,:,i])
        filename = "bias" +str(i) +".txt"
        np.savetxt(filename,bias[:,:,i])
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号

def plot_veri():
    grade_name = ["小雨","中雨","大雨","暴雨","大暴雨"]
    dh_list= [96,120,144,168]
    x = np.arange(len(dh_list))
    width = 0.15
    for i in range(len(grade_name)):
        filename = "ts" + str(i) + ".txt"
        ts = np.loadtxt(filename)
        filename = "bias" +str(i) +".txt"
        bias = np.loadtxt(filename)
        fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10, 4))
        axes[0].bar(x -0.2, ts[:, 0],width,color =  'r', label="预报员")
        axes[0].bar(x, ts[:, 1], width,color =  'g',label="MPI")
        axes[0].bar(x + 0.2, ts[:, 2],width,color= 'b', label="网格预报")
        axes[0].set_title("2019年1-5月"+grade_name[i] + "TS评分")
        axes[0].set_xticks(x)
        axes[0].set_xticklabels(dh_list)
        axes[0].legend()
        max_value = np.max(ts) * 1.4
        axes[0].set_ylim(0,max_value)

        axes[1].bar(x-0.2, bias[:, 0], width,color = 'r', label="预报员")
        axes[1].bar(x, bias[:, 1], width,color = 'g', label="MPI")
        axes[1].bar(x + 0.2, bias[:, 2], width,color = 'b', label="网格预报")
        axes[1].set_title("2019年1-5月"+grade_name[i] + "BIAS评分")
        axes[1].set_xticks(x)
        axes[1].set_xticklabels(dh_list)
        axes[1].legend()
        max_value = np.max(bias) * 1.4
        axes[1].set_ylim(0,max_value)

        filename = "pig" + str(i) + ".png"
        plt.savefig(filename)
        plt.close()

plot_veri()
