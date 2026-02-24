import math
import os.path

import meteva.base as meb
import datetime
import numpy as np
import matplotlib.pyplot as plt
import meteva
import matplotlib.ticker as ticker
import xarray as xr

def spectrum_Spherical_Harmonic_one_field(grd):
    import pyshtools as sh
    """
    计算标量场的球谐能谱
    :param data: 输入高度场数据（Nx×Ny数组，经度×纬度）
    :param l_max: 最大球谐度数
    :return: 波数l数组，能谱E(l)
    """
    # 1. 创建SHGrid对象（需确保输入数据为规则网格）

    data = grd.values.squeeze()
    if data.shape[0] * 2 -1 != data.shape[1] and data.shape[0] * 2  != data.shape[1]:
        print("data.shape:",data.shape)
        print("进行球谐变换时需保证东西向格点数=南北向格点数×2-1(或0)",
              "number of grid points in the east-west direction should equal to the number of grid points in the north-south direction * 2 - 1(or 0)")
        return
    grid = sh.SHGrid.from_array(data)

    # 2. 执行球谐展开
    coeffs = grid.expand(normalization='ortho', csphase=-1) #, lmax_calc=l_max)

    # 3. 提取球谐系数
    height_coeffs = coeffs.coeffs
    l_max = height_coeffs.shape[1]

    # 4. 计算能谱（各向同性平均）
    E_l = np.zeros(l_max)
    for l in range(l_max):
        # 对每个l的所有m求和
        E_l[l] = 0.5 * np.sum(np.abs(height_coeffs[:, l, :]) ** 2) / (2 * l + 1)

    # 5. 归一化（可选）
    E_l_normalized = E_l / (4 * np.pi)

    return E_l_normalized


def spectrum_Spherical_Harmonic(para,show = None,save_path = None,title = None):
    grid0 = para["grid"]
    begin_time = para["begin_time"]
    end_time = para["end_time"]
    dtime = para["dtime"]
    time_step = para["time_step"]
    time1 = begin_time - datetime.timedelta(hours=dtime)
    members = list(para["fo_data"].keys())

    sp_list_list = []
    while time1 <= end_time:
        time1 += datetime.timedelta(hours=time_step)

        time_ob = time1 + datetime.timedelta(hours=dtime)
        if para["time_type"] != para["ob_data"]["time_type"]:
            if para["time_type"]=="UT":
                time_ob_file = time_ob + datetime.timedelta(hours=8)
            else:
                time_ob_file = time_ob - datetime.timedelta(hours=8)
        else:
            time_ob_file = time_ob

        path_ob = meb.get_path(para["ob_data"]["dir_ob"],time_ob_file)
        print(path_ob)
        if not os.path.exists(path_ob):continue
        grd = para["ob_data"]["read_method"](path_ob,grid = grid0,**para["ob_data"]["read_para"],time = time_ob_file,show = True)
        if grd is None:continue
        if para["ob_data"]["operation"] is not None:
            grd = para["ob_data"]["operation"](grd,**para["ob_data"]["operation_para"])

        sp_list = []
        sp = spectrum_Spherical_Harmonic_one_field(grd)
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
            print(path_fo)
            if not os.path.exists(path_fo): continue
            grd = para["fo_data"][member]["read_method"](path_fo, grid=grid0, **para["fo_data"][member]["read_para"],time = time_fo_file,dtime = dtime,show = True)
            if grd is None: continue
            if para["fo_data"][member]["operation"] is not None:
                grd = para["fo_data"][member]["operation"](grd, **para["fo_data"][member]["operation_para"])


            sp = spectrum_Spherical_Harmonic_one_field(grd)
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


        plt.xlabel('WaveNumber')

        if title is not None:
            plt.title(title)
        plt.ylabel('energy')
        plt.legend()

        if save_path is not None:
            print(save_path)
            plt.savefig(save_path, dpi=600)
            print("png result has been output to " + save_path)
        if show is not None:
            plt.show()

        plt.close()

    return sp_dict


def kinetic_energy_spectrum(para):
    grid0 = para["grid"]
    begin_time = para["begin_time"]
    end_time = para["end_time"]
    dtime = para["dtime"]
    time_step = para["time_step"]
    time1 = begin_time - datetime.timedelta(hours=dtime)
    members = list(para["fo_data"].keys())

    sp_list_list = []
    sp_list_list_vor = []
    sp_list_list_div = []
    while time1 <= end_time:
        time1 += datetime.timedelta(hours=time_step)

        time_ob = time1 + datetime.timedelta(hours=dtime)
        if para["time_type"] != para["ob_data"]["u"]["time_type"]:
            if para["time_type"] == "UT":
                time_ob_file = time_ob + datetime.timedelta(hours=8)
            else:
                time_ob_file = time_ob - datetime.timedelta(hours=8)
        else:
            time_ob_file = time_ob

        path_ob = meb.get_path(para["ob_data"]["u"]["dir_ob"], time_ob_file)
        print(path_ob)
        if not os.path.exists(path_ob): continue
        grd_u = para["ob_data"]["u"]["read_method"](path_ob, grid=grid0, **para["ob_data"]["u"]["read_para"],
                                                    time=time_ob_file, show=True)
        if grd_u is None: continue
        if para["ob_data"]["u"]["operation"] is not None:
            grd_u = para["ob_data"]["u"]["operation"](grd_u, **para["ob_data"]["u"]["operation_para"])

        path_ob = meb.get_path(para["ob_data"]["v"]["dir_ob"], time_ob_file)
        grd_v = para["ob_data"]["v"]["read_method"](path_ob, grid=grid0, **para["ob_data"]["v"]["read_para"],
                                                    time=time_ob_file, show=True)
        if grd_v is None: continue
        if para["ob_data"]["v"]["operation"] is not None:
            grd_v = para["ob_data"]["v"]["operation"](grd_v, **para["ob_data"]["v"]["operation_para"])

        sp_list = []
        sp_u = spectrum_Spherical_Harmonic_one_field(grd_u)
        sp_v = spectrum_Spherical_Harmonic_one_field(grd_v)
        sp_list.append(sp_u + sp_v)

        sp_list_div = []
        sp_list_vor = []

        if para["need_Rotational_Divergent"]:
            div = meteva.base.uv_to_div(grd_u, grd_v)
            vor = meteva.base.uv_to_vor(grd_u, grd_v)

            sp_vor = spectrum_Spherical_Harmonic_one_field(vor)
            sp_div = spectrum_Spherical_Harmonic_one_field(div)

            sp_list_vor.append(sp_vor)
            sp_list_div.append(sp_div)

        for member in members:

            if para["time_type"] != para["fo_data"][member]["u"]["time_type"]:
                if para["time_type"] == "UT":
                    time_fo_file = time1 + datetime.timedelta(hours=8)
                else:
                    time_fo_file = time1 - datetime.timedelta(hours=8)
            else:
                time_fo_file = time1

            path_fo = meb.get_path(para["fo_data"][member]["u"]["dir_fo"], time_fo_file, dtime)
            print(path_fo)
            if not os.path.exists(path_fo): continue
            grd_u = para["fo_data"][member]["u"]["read_method"](path_fo, grid=grid0,
                                                                **para["fo_data"][member]["u"]["read_para"],
                                                                time=time_fo_file, dtime=dtime, show=True)
            if grd_u is None: continue
            if para["fo_data"][member]["u"]["operation"] is not None:
                grd_u = para["fo_data"][member]["u"]["operation"](grd_u,
                                                                  **para["fo_data"][member]["u"]["operation_para"])
            sp_u = spectrum_Spherical_Harmonic_one_field(grd_u)

            path_fo = meb.get_path(para["fo_data"][member]["v"]["dir_fo"], time_fo_file, dtime)
            grd_v = para["fo_data"][member]["v"]["read_method"](path_fo, grid=grid0,
                                                                **para["fo_data"][member]["v"]["read_para"],
                                                                time=time_fo_file, dtime=dtime, show=True)
            if grd_v is None: continue
            if para["fo_data"][member]["v"]["operation"] is not None:
                grd_v = para["fo_data"][member]["v"]["operation"](grd_v,
                                                                  **para["fo_data"][member]["v"]["operation_para"])
            sp_v = spectrum_Spherical_Harmonic_one_field(grd_v)

            sp_list.append(sp_u + sp_v)

            if para["need_Rotational_Divergent"]:
                div = meteva.base.uv_to_div(grd_u, grd_v)
                vor = meteva.base.uv_to_vor(grd_u, grd_v)

                sp_vor = spectrum_Spherical_Harmonic_one_field(vor)
                sp_div = spectrum_Spherical_Harmonic_one_field(div)

                sp_list_vor.append(sp_vor)
                sp_list_div.append(sp_div)

        if len(sp_list) == len(para["fo_data"].keys()) + 1:
            sp_list_list.append(sp_list)
            if para["need_Rotational_Divergent"]:
                sp_list_list_div.append(sp_list_div)
                sp_list_list_vor.append(sp_list_vor)

    sp_array = np.array(sp_list_list)
    sp_array_mean = np.mean(sp_array, axis=0)  # 时间维度取平均

    if para["need_Rotational_Divergent"]:
        sp_array_div = np.array(sp_list_list_div)
        sp_array_mean_div = np.mean(sp_array_div, axis=0)  # 时间维度取平均
        sp_array_vor = np.array(sp_list_list_vor)
        sp_array_mean_vor = np.mean(sp_array_vor, axis=0)  # 时间维度取平均

        # 归一化处理
        rate = (sp_array_mean_div + sp_array_mean_vor) / sp_array_mean
        sp_array_mean_div /= rate
        sp_array_mean_vor /= rate

        obs_name = para["ob_data"]["data_name"]

        sp_dict = {}
        sp_dict[obs_name] = sp_array_mean[0, :]
        sp_dict[f"{obs_name}_rot"] = sp_array_mean_vor[0, :]
        sp_dict[f"{obs_name}_div"] = sp_array_mean_div[0, :]

        for m in range(len(members)):
            member = members[m]
            sp_dict[member] = sp_array_mean[m + 1, :]
            sp_dict[member + "_rot"] = sp_array_mean_vor[m + 1, :]
            sp_dict[member + "_div"] = sp_array_mean_div[m + 1, :]
    else:
        sp_dict = {}
        obs_name = para["ob_data"]["data_name"]
        sp_dict[obs_name] = sp_array_mean[0, :]
        for m in range(len(members)):
            member = members[m]
            sp_dict[member] = sp_array_mean[m + 1, :]

    return sp_dict


def plot_kinetic_energy_spectrum(sp_dict,  para,
                                 target_members=None,
                                 save_path=None, title=None, show=None):
    """
    绘制动能谱图
    参数:
    sp_dict: 包含各成员谱数据的字典
    grid0: 网格信息
    para: 参数字典
    target_members: 要绘制的成员列表，None表示绘制所有成员
    save_path: 图片保存路径
    title: 图片标题
    show: 是否显示图形
    """
    ns = 2

    grid0 = para["grid"]
    # 获取观测名称
    obs_name = para["ob_data"].get("data_name", "obs")

    # 确定要绘制的键
    if target_members is None:
        keys = list(sp_dict.keys())
    else:
        keys = []
        for member in target_members:
            # 添加成员的所有变体（原始、旋转、辐散）
            if member in sp_dict:
                keys.append(member)
            if f"{member}_rot" in sp_dict:
                keys.append(f"{member}_rot")
            if f"{member}_div" in sp_dict:
                keys.append(f"{member}_div")

    # 定义颜色列表
    colors = ['#ff7f0e', '#1f77b4', '#2ca02c', '#d62728', '#9467bd',
              '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    # 计算所有谱数据的最小值
    vmin = min(np.min(sp_dict[key][ns:]) for key in sp_dict.keys())

    # 创建图形
    plt.figure(figsize=(10, 6))
    color_index = 0
    color_dict = {}

    for key in keys:
        if key not in sp_dict:
            continue  # 跳过不存在的数据
        sp = sp_dict[key][ns:]
        # 确定基名和颜色
        base_key = key[:-4] if key.endswith(('_rot', '_div')) else key
        if base_key not in color_dict:
            if base_key == obs_name:
                color_dict[base_key] = 'black'
            else:
                color_dict[base_key] = colors[color_index % len(colors)]
                color_index += 1
        color = color_dict[base_key]

        # 确定线型
        if key.endswith('_rot'):
            linestyle = '--'
        elif key.endswith('_div'):
            linestyle = '-.'
        else:
            linestyle = '-'

        plt.plot(sp, linestyle, label=key, linewidth=1.2, color=color)

    # 添加参考线
    x = np.arange(10, 100, 1.0)

    # -3次方定律
    y = np.power(x, -3.0)
    y = 10 * y / np.max(y)
    plt.plot(x, y, "-.", label="-3 power law", linewidth=1.0, color="gray", alpha=0.7)

    # -5/3次方定律
    y = np.power(x, -5 / 3.0)
    y = 10 * y / np.max(y)
    plt.plot(x, y, "--", label="-5/3 power law", linewidth=1.0, color="gray", alpha=0.7)

    # 添加垂直参考线
    for vline in para["vline"]:
        plt.axvline(x=int(grid0.nlon / vline), color='cyan',
                    linestyle='--', linewidth=0.8, alpha=0.7,
                    label=f'{vline}$\\bigtriangleup$')

    plt.yscale('log')
    plt.xscale('log')
    plt.xlabel('WaveNumber')
    plt.ylim(vmin / 3, 2e2)

    # 处理标题
    if title is None:
        if target_members is None:
            title = "Kinetic Energy Spectrum - All Members"
        else:
            title = f"Kinetic Energy Spectrum - {', '.join(target_members)}"
    plt.title(title, fontsize=14)

    plt.ylabel('Kinetic energy($m^2s^{-2}$)', fontsize=12)
    plt.legend(loc="best", fontsize=9, ncol=2)
    plt.grid(True, which="both", ls="--", alpha=0.3)

    # 处理保存路径
    if save_path is not None:
        print(f"Saving figure to: {save_path}")
        plt.savefig(save_path, dpi=600, bbox_inches='tight')

    if show:
        plt.show()
    plt.close()

if __name__ == "__main__":
    para = {
        "grid": meteva.base.grid([0,359.75,0.25],[-89.875,89.875,0.25]),  # 检验区域
        "begin_time": datetime.datetime(2018, 9, 1, 0),  # 时段开始时刻(基于起报时间)
        "end_time": datetime.datetime(2018, 9, 2, 0),  # 时段结束时刻（基于起报时间）
        "time_step": 12,  # 起报时间间隔
        "dtime": 12,  # 预报时效
        "time_type": "BT",  # 最终检验结果呈现时，采用北京时还是世界时，UT代表世界时，BT代表北京时
        "need_Rotational_Divergent":True,
        "vline":[5,10],
        "ob_data": {
            "data_name":"ERA5",
            "u":{
            "dir_ob": r"\\10.28.16.234\data2\AI\Fengwu_ERA5\U\200\YYYYMMDDHH\YYYYMMDDHH.012.nc",  # 实况场数据路径
            "hour": None,
            "read_method": meb.read_griddata_from_nc,  # 读取数据的函数
            "operation": None,  # 预报数据读取后处理函数
            "operation_para": {},  # 预报数据读取后处理参数，用于对单位进行变换的操作
            "read_para": {},  # 读取数据的函数参数
            "time_type": "BT",  # 数据文件中的时间类型，UT代表世界时
            },
            "v":{
                "dir_ob": r"\\10.28.16.234\data2\AI\Fengwu_ERA5\V\200\YYYYMMDDHH\YYYYMMDDHH.012.nc",  # 实况场数据路径
                "hour": None,
                "read_method": meb.read_griddata_from_nc,  # 读取数据的函数
                "operation": None,  # 预报数据读取后处理函数
                "operation_para": {},  # 预报数据读取后处理参数，用于对单位进行变换的操作
                "read_para": {},  # 读取数据的函数参数
                "time_type": "BT",  # 数据文件中的时间类型，UT代表世界时
            }
        },
        "fo_data": {
            "FENGWU": {
                "u":{
                    "dir_fo": r"\\10.28.16.234\data2\AI\Fengwu_ERA5\U\200\YYYYMMDDHH\YYYYMMDDHH.TTT.nc",  # 数据路径
                    "read_method": meb.read_griddata_from_nc,  # 读取数据的函数
                    "read_para": {},  # 读取数据的函数参数
                    "reasonable_value": [0, 1000],  # 合理的预报值的取值范围，超出范围观测将被过滤掉
                    "operation": None,  # 预报数据读取后处理函数，用于对单位进行变换的操作
                    "operation_para": {},  # #预报数据读取后处理参数
                    "time_type": "BT",  # 预报数据时间类型是北京时，即08时起报
                    "move_fo_time": 0  # 是否对预报的时效进行平移，12 表示将1月1日08时的36小时预报转换成1月1日20时的24小时预报后参与对比
                },
                "v":{
                    "dir_fo": r"\\10.28.16.234\data2\AI\Fengwu_ERA5\V\200\YYYYMMDDHH\YYYYMMDDHH.TTT.nc",  # 数据路径
                    "read_method": meb.read_griddata_from_nc,  # 读取数据的函数
                    "read_para": {},  # 读取数据的函数参数
                    "reasonable_value": [0, 1000],  # 合理的预报值的取值范围，超出范围观测将被过滤掉
                    "operation": None,  # 预报数据读取后处理函数，用于对单位进行变换的操作
                    "operation_para": {},  # #预报数据读取后处理参数
                    "time_type": "BT",  # 预报数据时间类型是北京时，即08时起报
                    "move_fo_time": 0  # 是否对预报的时效进行平移，12 表示将1月1日08时的36小时预报转换成1月1日20时的24小时预报后参与对比
                }
            },
            "FUXI": {
                "u": {
                    "dir_fo": r"\\10.28.16.234\data2\AI\fuxi_ERA5\U\200\YYYYMMDDHH\YYYYMMDDHH.TTT.nc",  # 数据路径
                    "read_method": meb.read_griddata_from_nc,  # 读取数据的函数
                    "read_para": {},  # 读取数据的函数参数
                    "reasonable_value": [0, 1000],  # 合理的预报值的取值范围，超出范围观测将被过滤掉
                    "operation": None,  # 预报数据读取后处理函数，用于对单位进行变换的操作
                    "operation_para": {},  # #预报数据读取后处理参数
                    "time_type": "BT",  # 预报数据时间类型是北京时，即08时起报
                    "move_fo_time": 0  # 是否对预报的时效进行平移，12 表示将1月1日08时的36小时预报转换成1月1日20时的24小时预报后参与对比
                },
                "v": {
                    "dir_fo": r"\\10.28.16.234\data2\AI\fuxi_ERA5\V\200\YYYYMMDDHH\YYYYMMDDHH.TTT.nc",  # 数据路径
                    "read_method": meb.read_griddata_from_nc,  # 读取数据的函数
                    "read_para": {},  # 读取数据的函数参数
                    "reasonable_value": [0, 1000],  # 合理的预报值的取值范围，超出范围观测将被过滤掉
                    "operation": None,  # 预报数据读取后处理函数，用于对单位进行变换的操作
                    "operation_para": {},  # #预报数据读取后处理参数
                    "time_type": "BT",  # 预报数据时间类型是北京时，即08时起报
                    "move_fo_time": 0  # 是否对预报的时效进行平移，12 表示将1月1日08时的36小时预报转换成1月1日20时的24小时预报后参与对比
                }
            },
        },
        "output_dir": None  # 观测站点合并数据的输出路径，设置为None时不输出收集数据的中间结果
    }

    # 1. 计算动能谱
    sp_dict = kinetic_energy_spectrum(para)

    # 2. 绘制各种图表
    # 2.1 仅绘制观测
    plot_kinetic_energy_spectrum(
        sp_dict=sp_dict,
        para=para,
        target_members=["ERA5"],
        save_path="kes_obs.png",
        title="Kinetic Energy Spectrum - Observations"
    )

    # 2.2 仅绘制单个试验组
    plot_kinetic_energy_spectrum(
        sp_dict=sp_dict,
        para=para,
        target_members=["FENGWU"],
        save_path="kes_single_CMA_GFS.png",
        title="Kinetic Energy Spectrum - CMA_GFS"
    )

    # 2.3 绘制多个试验组对比
    plot_kinetic_energy_spectrum(
        sp_dict=sp_dict,
        para=para,
        target_members=["ERA5", "FENGWU"],
        save_path="kes_comparison_ERA5_CMA_GFS.png",
        title="Kinetic Energy Spectrum - ERA5 vs CMA_GFS"
    )

    # 2.4 所有成员在一张图
    plot_kinetic_energy_spectrum(
        sp_dict=sp_dict,
        para=para,
        target_members=None,  # None表示绘制所有成员
        save_path="kes_all.png",
        title="Kinetic Energy Spectrum - All Members"
    )

    # 2.5 绘制旋转分量和辐散分量
    plot_kinetic_energy_spectrum(
        sp_dict=sp_dict,
        para=para,
        target_members=["ERA5_rot", "ERA5_div", "FENGWU_rot", "FENGWU_div"],
        save_path="kes_rot_div.png",
        title="Kinetic Energy Spectrum - Rotational and Divergent Components"
    )