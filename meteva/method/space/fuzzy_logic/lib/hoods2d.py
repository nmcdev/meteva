import time
import numpy as np
from meteva.method.space.fuzzy_logic.lib.datagrabber_spatialVx import datagrabber_spatialVx
from meteva.method.space.fuzzy_logic.lib.fss2dfun import fss2dfun
from meteva.method.space.fuzzy_logic.lib.fuzzyjoint2dfun import fuzzyjoint2dfun
from meteva.method.space.fuzzy_logic.lib.mincvg2dfun import mincvg2dfun
from meteva.method.space.fuzzy_logic.lib.multicon2dfun import multicon2dfun
from meteva.method.space.fuzzy_logic.lib.progmatic2dfun import pragmatic2dfun
from meteva.method.space.fuzzy_logic.lib.thresholder import thresholder
from meteva.method.space.fuzzy_logic.lib.thresholder_spatialVx import thresholder_spatialVx
from meteva.method.space.fuzzy_logic.lib.hoods2dPrep import hoods2dPrep
from meteva.method.space.fuzzy_logic.lib.hoods2dSetUpLists import hoods2dSetUpLists
from meteva.method.space.fuzzy_logic.lib.hoods2dsmooth import hoods2dsmooth
from meteva.method.space.fuzzy_logic.lib.make_spatialVx import make_spatialVx




def hoods2d(input_object, which_methods=None, time_point=1,
            obs=0, model=0, pe=None, levels=None, max_n=None, rule=">=", verbose=False):

    #hoods2d可以同时计算"mincvr", "multi_event", "fuzzy", "joint", "fss", "pragmatic" 六种空间方法的结果
    if which_methods is None:
        which_methods = ["mincvr", "multi_event", "fuzzy", "joint", "fss", "pragmatic"]


    smooth_fun = "hoods2dsmooth"  # 平滑方法
    smooth_params = None
    input_object['data'] = [input_object['X'], input_object['Xhat']]  #从输入的数据中提取观测和预报数据

    # 根据输入参数计算对应的levels, pe, max_n
    input_object = hoods2dPrep(input_object=input_object, pe=pe, levels=levels,
                               max_n=max_n, smooth_fun=smooth_fun, smooth_params=smooth_params)

    #是否显示
    if verbose:
        begin_time = time.time()

    thresholds = input_object['thresholds']  #输入的数据中包含阈值
    q = thresholds[0].shape[0]
    levels = input_object['levels']   #从输入中提取窗口宽度参数
    l = len(levels)

    # 抓取数据
    dat = datagrabber_spatialVx(input_object, time_point=time_point, obs=obs, model=model)

    x = dat['X'] #观测场
    outmat = np.zeros((l, q))
    #pd.DataFrame(outmat, columns=json.loads(input_object["qs"]), index=levels)

    # 根据输入参数，初始化返回结果
    out = hoods2dSetUpLists(input_object=input_object, which_methods=which_methods, mat=outmat)
    sub = input_object["subset"]


    if verbose:
        print("Looping through thresholds.\n")
    for threshold in range(0, q, 1):
        if len({"mincvr", "mincvr", "multi_event", "fuzzy", "joint", "fss", "pragmatic"}.intersection(
                which_methods)) > 0:
            if verbose:
                print("\n", "Setting up binary objects for threshold ", threshold, "\n")

            # 根据thresholds, rule，替换矩阵中的元素
            dat2 = thresholder_spatialVx(input_object, func_type="binary", th=threshold, rule=rule, time_point=time_point, obs=obs,
                                         model=model)
            ix = dat2['X']  #观测
            iy = dat2['Xhat'] #预报


        if "fss" in which_methods:
            if sub is None:
                f0 = np.mean(ix)
            else:
                f0 = np.mean(ix['subset'])
            if threshold == 1:
                out["fss"]["fss_uniform"] = 0.5 + f0 / 2
                out["fss"]["fss_random"] = f0
            else:
                out["fss"]["fss_uniform"] = [out["fss"]["fss_uniform"], 0.5 + f0 / 2]
                out["fss"]["fss_random"] = [out["fss"]["fss_random"], f0]
        if verbose:
            print("Looping through levels.\n")
        for level in range(0, l, 1):
            if verbose:
                print("Neighborhood length = ", levels[level], "\n")

            # 平滑处理
            level_w = hoods2dsmooth(x, levels[level], None, True)
            if len({"mincvr", "multi_event", "fuzzy", "joint", "pragmatic", "fss"}.intersection(
                    which_methods)) > 0:
                if len({"mincvr", "multi_event", "fuzzy", "joint", "fss"}.intersection(which_methods)) > 0:
                    s_px = hoods2dsmooth(ix, levels[level], level_w)
                s_py = hoods2dsmooth(iy, levels[level], level_w)

            if len({"mincvr", "multi_event"}.intersection(which_methods)) > 0:
                s_ix = thresholder(s_px, func_type="binary", th=input_object["pe"][level])
                s_iy = thresholder(s_py, func_type="binary", th=input_object["pe"][level])
                if "mincvr" in which_methods:
                    tmp = mincvg2dfun(s_iy=s_iy, s_ix=s_ix, subset=sub)
                    out["mincvr"]["pod"][level, threshold] = tmp["pod"]
                    out["mincvr"]["far"][level, threshold] = tmp["far"]
                    out["mincvr"]["ets"][level, threshold] = tmp["ets"]

                if "multi_event" in which_methods:
                    tmp = multicon2dfun(s_iy=s_iy, ix=ix, subset=sub)
                    out["multi_event"]["pod"][level, threshold] = tmp["pod"]
                    out["multi_event"]["f"][level, threshold] = tmp["f"]
                    out["multi_event"]["hk"][level, threshold] = tmp["hk"]

            if len({"fuzzy", "joint"}.intersection(which_methods)) > 0:
                tmp = fuzzyjoint2dfun(s_py=s_py, s_px=s_px, subset=sub)
                if "fuzzy" in which_methods:
                    out["fuzzy"]["pod"][level, threshold] = tmp["fuzzy"]["pod"]
                    out["fuzzy"]["far"][level, threshold] = tmp["fuzzy"]["far"]
                    out["fuzzy"]["ets"][level, threshold] = tmp["fuzzy"]["ets"]

                if "joint" in which_methods:
                    out["joint"]["pod"][level, threshold] = tmp["joint"]["pod"]
                    out["joint"]["far"][level, threshold] = tmp["joint"]["far"]
                    out["joint"]["ets"][level, threshold] = tmp["joint"]["ets"]

            if "fss" in which_methods:
                out["fss"]["values"][level, threshold] = fss2dfun(s_py=s_py, s_px=s_px, subset=sub)
            if "pragmatic" in which_methods:
                tmp = pragmatic2dfun(s_py=s_py, ix=ix)
                out["pragmatic"]["bs"][level, threshold] = tmp["bs"]
                out["pragmatic"]["bss"][level, threshold] = tmp["bss"]

    if verbose:
        print(time.time() - begin_time)
    #out["time_point"] = time_point
    #out["model_num"] = model

    return out


if __name__ == '__main__':
    import meteva.base as meb
    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    path_fo_03 = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    path_fo_27 = r'H:\test_data\input\mem\mode\ec\rain03\20072508.027.nc'
    grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo_03 = meb.read_griddata_from_nc(path_fo_03, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")
    grd_fo_27 = meb.read_griddata_from_nc(path_fo_27, grid=grid1, time="2020072508", dtime=27, data_name="ECMWF")

    obs_array = grd_ob.values.squeeze()
    fst_array = grd_fo_03.values.squeeze()
    hold = make_spatialVx(obs_array,fst_array)
    look = hoods2d(hold,levels=[3])
    print(look["joint"])