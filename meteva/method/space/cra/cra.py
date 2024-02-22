import meteva
import numpy as np
import time
import sys
import copy
from meteva.method.space.mode import feature_finder
from meteva.method.space.mode.centmatch import centmatch
from meteva.method.space.mode.merge_force import merge_force
from meteva.method.space.mode import data_pre
from meteva.method.space.rigider import rigider


def get_rigid(x, ob_i,fo_j,stages,translate,rotate):
    '''
    调用刚体变换，将一个预报目标向通过平移和旋转至其匹配的观测目标的位置
    :param x:
    :param ob_i:
    :param fo_j:
    :param stages:
    :param translate:
    :param rotate:
    :return:
    '''
    grid0 = x["grid"] #网格

    grd_ob_i = meteva.base.grid_data(grid0)
    index = x["grd_ob_label"].values==ob_i
    grd_ob_i.values[index] =  x["grd_ob"].values[index]   #第i个观测目标区域保持要素值，其它区域清零

    grd_fo_j = meteva.base.grid_data(grid0)
    index = x["grd_fo_label"].values==fo_j
    grd_fo_j.values[index] =  x["grd_fo"].values[index]  #第j个预报目标区域保持要素值，其它区域清零

    look_rigid = rigider.rigid_optimal(grd_ob_i,grd_fo_j,stages=stages,translate=translate,rotate=rotate)  #通过刚体变换，找到最佳平移、旋转角度，以及变换后的预报场

    return look_rigid


def caculate_error_components(x, translate, rotate):
    '''
    根据刚体变换的结果计算预报误差的不同分量
    :param x:
    :param translate:
    :param rotate:
    :return:
    '''
    grd_fo = x['grd_fo']
    grd_ob = x['grd_ob']
    if translate:
        if rotate:
            grd_fo_shift = x['grd_fo_shift']  # rigider没有输出该结果
            grd_fo_shift_rotate = x['grd_fo_shift_rotate']
        else:
            grd_fo_shift = x['grd_fo_shift']
            grd_fo_shift_rotate = grd_fo_shift
    else:
        if rotate:
            grd_fo_shift = grd_fo
            grd_fo_shift_rotate = x['grd_fo_shift_rotate']
        else:
            print("刚体变换的translate 和rotate不能同时为False")
            return None

    values = np.abs(grd_ob.values) + np.abs(grd_fo.values) +np.abs(grd_fo_shift.values)+ np.abs(grd_fo_shift_rotate.values)
    index = np.where(values!=0)
    imax = np.max(index[-1])+1
    imin = np.min(index[-1])
    jmax = np.max(index[-2])+1
    jmin = np.min(index[-2])

    grd_ob_values = grd_ob.values[0,0,0,0,jmin:jmax,imin:imax]
    grd_fo_values = grd_fo.values[0,0,0,0,jmin:jmax,imin:imax]
    grd_fo_shift_values = grd_fo_shift.values[0,0,0,0,jmin:jmax,imin:imax]
    grd_fo_shift_rotate_values = grd_fo_shift_rotate.values[0,0,0,0,jmin:jmax,imin:imax]

    MSE_total = np.mean(np.power(grd_fo_values - grd_ob_values, 2))  # 总误差
    d2_shift_left = np.power(grd_fo_shift_values -grd_ob_values, 2)  #平移场剩余误差场
    MSE_shift_left = np.mean(d2_shift_left)                            # 平移剩余误差
    MSE_shift = MSE_total - MSE_shift_left                     #平移误差

    d2_shift_rotate_left = np.power(grd_fo_shift_rotate_values - grd_ob_values, 2)  #刚体变换后误差场
    MSE_shift_rotate_left = np.mean(d2_shift_rotate_left)                             #刚体变换后的均方误差


    fo_mean  = np.mean(grd_fo_values)     # 平移旋转后观测预报并集区域的均值。
    ob_mean  = np.mean(grd_ob_values)     # 平移旋转后观测预报并集区域的均值。
    MSE_volume = np.power(fo_mean - ob_mean, 2)


    res = {"ob_mean":ob_mean,"fo_mean":fo_mean,
        "MSE_total": MSE_total, "MSE_shift_left": MSE_shift_left,
           "MSE_shift": MSE_shift, "MSE_shift_rotate_left": MSE_shift_rotate_left,
           "MSE_rotate": MSE_shift_left - MSE_shift_rotate_left, "MSE_volume": MSE_volume,
           "MSE_pattern": MSE_shift_rotate_left - MSE_volume}

    return res

def craer(look_merge,stages=True,translate=True,rotate=True):

    out = {}
    nmatch = len(look_merge["matches"])
    for k in range(nmatch):
        ob_i = look_merge["matches"][k][0]
        fo_j = look_merge["matches"][k][1]
        look_rigid = get_rigid(look_merge,ob_i,fo_j,stages,translate,rotate)
        error_components = caculate_error_components(look_rigid,stages,rotate)
        for key in error_components.keys():
            look_rigid[key] = error_components[key]
        out[ob_i] = look_rigid

    return out

def operation(grd_ob,grd_fo,smooth,threshold,minsize,compare = ">=", stages = True,translate = True,rotate = True):
    look_featureFinder = feature_finder(grd_ob,grd_fo,smooth=smooth,threshold=threshold,minsize=minsize,compare=compare)
    look_match = centmatch(look_featureFinder)
    look_merge = merge_force(look_match)
    look_cra = craer(look_merge,stages,translate,rotate)
    result = {"merge":look_merge,
              "cra":look_cra}
    return result

def plot_value(look_cra,label,cmap = "rain_1h",clevs= None):

    rire = look_cra[label]
    grd_list = [rire["grd_ob"],rire["grd_fo"],rire["grd_fo_shift"],rire["grd_fo_shift_rotate"]]
    vmax = max(np.max(grd_list[0].values),np.max(grd_list[0].values))
    vmin = min(np.min(grd_list[0].values),np.min(grd_list[0].values))
    cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap, clevs=clevs, vmin=vmin, vmax=vmax)
    meteva.base.plot_tools.plot_2d_grid_list(grd_list,cmap=cmap1,clevs = clevs1,ncol= 2)




if __name__ == "__main__":

    filename_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    filename_fo = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    grd_ob = meteva.base.read_griddata_from_nc(filename_ob)
    grd_fo = meteva.base.read_griddata_from_nc(filename_fo)
    look_cra = operation(grd_ob,grd_fo,1,5,30)