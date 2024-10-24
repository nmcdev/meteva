import os.path

import meteva.base as meb
import datetime
import numpy as np
import matplotlib.pyplot as plt
import meteva
import matplotlib.ticker as ticker

def spectrum_fft2_one_field(grd):
    data = grd.values.squeeze()
    fft_result = np.fft.fft2(data)
    # 移位使得零频率在中心
    fft_shifted = np.fft.fftshift(fft_result)
    # 计算能量谱
    energy_spectrum = np.abs(fft_shifted) ** 2

    # 获取二维能谱的尺寸
    ny, nx = energy_spectrum.shape

    # 创建一个与能谱尺寸相同的坐标网格
    x = np.arange(nx) - nx // 2
    y = np.arange(ny) - ny // 2
    xx, yy = np.meshgrid(x, y)

    # 计算每个点到中心的距离
    r = np.sqrt(xx ** 2 + yy ** 2)

    # 定义距离的离散区间
    nbins = int(np.sqrt(nx ** 2 + ny ** 2))
    bins = np.arange(nbins)

    # 进行径向平均
    hist, bin_edges = np.histogram(r, bins=bins, weights=energy_spectrum)
    counts, _ = np.histogram(r, bins=bins)
    radial_average = hist / counts
    mask = np.logical_not(np.isnan(radial_average))
    radial_average = radial_average[mask]

    return radial_average

def spectrum_fft2(para,show = None,save_path = None,title = None):
    grid0 = para["grid"]
    begin_time = para["begin_time"]
    end_time = para["end_time"]
    dtime = para["dtime"]
    time1 = begin_time - datetime.timedelta(hours=dtime)
    members = list(para["fo_data"].keys())

    sp_list_list = []
    while time1 <= end_time:
        time1 += datetime.timedelta(hours=dtime)

        time_ob = time1 + datetime.timedelta(hours=dtime)
        if para["time_type"] != para["ob_data"]["time_type"]:
            if para["time_type"]=="UT":
                time_ob_file = time_ob + datetime.timedelta(hours=8)
            else:
                time_ob_file = time_ob - datetime.timedelta(hours=8)
        else:
            time_ob_file = time_ob

        path_ob = meb.get_path(para["ob_data"]["dir_ob"],time_ob_file)
        if not os.path.exists(path_ob):continue
        grd = para["ob_data"]["read_method"](path_ob,grid = grid0,**para["ob_data"]["read_para"],show = True)
        if grd is None:continue
        if para["ob_data"]["operation"] is not None:
            grd = para["ob_data"]["operation"](grd,**para["ob_data"]["operation_para"])

        sp_list = []
        sp = spectrum_fft2_one_field(grd)
        sp_list.append(sp)

        for member in members:

            if para["time_type"] != para["fo_data"][member]["time_type"]:
                if para["time_type"] == "UT":
                    time_fo_file = time1 + datetime.timedelta(hours=8)
                else:
                    time_fo_file = time1 - datetime.timedelta(hours=8)
            else:
                time_fo_file = time1

            path_fo = meb.get_path(para["fo_data"][member]["dir_fo"], time_fo_file,dtime)
            if not os.path.exists(path_fo): continue
            grd = para["fo_data"][member]["read_method"](path_fo, grid=grid0, **para["fo_data"][member]["read_para"],show = True)
            if grd is None: continue
            if para["fo_data"][member]["operation"] is not None:
                grd = para["fo_data"][member]["operation"](grd, **para["fo_data"][member]["operation_para"])


            sp = spectrum_fft2_one_field(grd)
            sp_list.append(sp)

        if len(sp_list) == len(para["fo_data"].keys()) +1:
            sp_list_list.append(sp_list)


    sp_array = np.array(sp_list_list)
    sp_array_mean = np.mean(sp_array,axis=0)  #时间维度取平均
    sp_dict = {}
    sp_dict["obs"] = sp_array_mean[0,:]
    for m in range(len(members)):
        member = members[m]
        sp_dict[member] = sp_array_mean[m+1,:]


    if show is not None or save_path is not None:
        ns = 2
        ne = int(grid0.nlon / 4)
        for key in sp_dict.keys():
            sp = sp_dict[key]
            plt.plot(sp[ns:ne], label=key, linewidth=1)

        plt.yscale('log')  # 设置Y轴为对数坐标
        plt.xscale('log')  # 设置Y轴为对数坐标
        # 设置更多的刻度
        ticks = [1,2,3,4,5,7,10,20,30,40,60,100]
        labels = [str(t) for t in ticks]
        plt.xticks(ticks, labels)

        plt.xlabel('波数')

        if title is not None:
            plt.title(title)
        plt.ylabel('Power')
        plt.legend()

        if save_path is not None:
            plt.savefig(save_path, dpi=600)
            print("png result has been output to " + save_path)
        if show is not None:
            plt.show()

        plt.close()

    return sp_dict


if __name__ == "__main__":
    para = {
        "grid": meteva.base.grid([70,140,0.25],[10,60,0.25]),  # 检验区域
        "begin_time": datetime.datetime(2024, 9, 1, 8),  # 时段开始时刻(基于起报时间)
        "end_time": datetime.datetime(2024, 9, 3, 20),  # 时段结束时刻（基于起报时间）
        "time_step": 12,  # 起报时间间隔
        "dtime": 120,  # 预报时效
        "time_type": "BT",  # 最终检验结果呈现时，采用北京时还是世界时，UT代表世界时，BT代表北京时
        "ob_data": {
            "dir_ob": r"\\10.40.23.69\u02\data\model\ecmwf\YYYYMMDDHH\gh\500\YYYYMMDDHH.TTT",  # 实况场数据路径
            "hour": None,
            "read_method": meteva.base.io.read_griddata_from_micaps4,  # 读取数据的函数
            "operation": None,  # 预报数据读取后处理函数
            "operation_para": {},  # 预报数据读取后处理参数，用于对单位进行变换的操作
            "read_para": {},  # 读取数据的函数参数
            "time_type": "BT",  # 数据文件中的时间类型，UT代表世界时
        },
        "fo_data": {
            "ECMWF": {
                "dir_fo": r"\\10.40.23.69\u02\data\model\ecmwf\YYYYMMDDHH\gh\500\YYYYMMDDHH.TTT",  # 数据路径
                "read_method": meteva.base.io.read_griddata_from_micaps4,  # 读取数据的函数
                "read_para": {},  # 读取数据的函数参数
                "reasonable_value": [0, 1000],  # 合理的预报值的取值范围，超出范围观测将被过滤掉
                "operation": None,  # 预报数据读取后处理函数
                "operation_para": {},  # 预报数据读取后处理参数，用于对单位进行变换的操作
                "time_type": "BT",  # 预报数据时间类型是北京时，即08时起报
                "move_fo_time": 0  # 是否对预报的时效进行平移，12 表示将1月1日08时的36小时预报转换成1月1日20时的24小时预报后参与对比
            },

            "CMA_GFS": {
                "dir_fo": r"\\10.40.23.69\u02\data\model\cma_gfs\YYYYMMDDHH\gh\500\YYYYMMDDHH.TTT",  # 数据路径
                "read_method": meteva.base.io.read_griddata_from_micaps4,  # 读取数据的函数
                "read_para": {},  # 读取数据的函数参数
                "reasonable_value": [0, 1000],  # 合理的预报值的取值范围，超出范围观测将被过滤掉
                "operation": None,  # 预报数据读取后处理函数，用于对单位进行变换的操作
                "operation_para": {},  # #预报数据读取后处理参数
                "time_type": "BT",  # 预报数据时间类型是北京时，即08时起报
                "move_fo_time": 0  # 是否对预报的时效进行平移，12 表示将1月1日08时的36小时预报转换成1月1日20时的24小时预报后参与对比
            },
        },
        "output_dir": None  # 观测站点合并数据的输出路径，设置为None时不输出收集数据的中间结果
    }


    spectrum_fft2(para,save_path=r"H:\test_data\output\method\space\spectrum\test.png")