import meteva
import numpy as np
from scipy.ndimage.filters import uniform_filter
import datetime
import pandas as pd

def fss_merge(fss_df,s = None):
    pass


def fss(grd_ob,grd_fo,grade_list=[1e-30],half_window_size_list=[1],compare = ">=", masker=None):
    '''
    :param grd_ob:
    :param grd_fo:
    :param grade_list:
    :param half_window_sizes_list:
    :param compare:
    :param masker_xy:
    :return:
    '''

    grd_ob_list = meteva.base.fun.split_grd(grd_ob,used_coords = ["time"])
    grd_ob_dict = {}
    for i in range(len(grd_ob_list)):
        grd_ob_one = grd_ob_list[i]
        time1 = meteva.base.all_type_time_to_datetime(grd_ob_one["time"].values[0])
        grd_ob_dict[time1] = grd_ob_one
    grd_fo_list = meteva.base.fun.split_grd(grd_fo)
    grid0 = meteva.base.get_grid_of_data(grd_fo_list[0])
    grid0 = meteva.base.grid(grid0.glon,grid0.glat)

    if masker is not None:
        masker1 = meteva.base.interp_gs_nearest(masker,grid0)
        masker_xy = masker1.values.squeeze()
    else:
        masker_xy = masker


    nw = len(half_window_size_list)
    nt = len(grade_list)
    result = []
    for i in range(len(grd_fo_list)):
        grd_fo_one = grd_fo_list[i]
        time1 = grd_fo_one["time"].values[0]
        dtime1 = int(grd_fo_one["dtime"].values[0])
        member1 = grd_fo_one["member"].values[0]
        time_ob = meteva.base.all_type_time_to_datetime(time1) + datetime.timedelta(hours=dtime1)
        if time_ob in grd_ob_dict.keys():
            grd_ob_one = grd_ob_dict[time_ob]
            ob_xy = grd_ob_one.values.squeeze()
            fo_xy = grd_fo_one.values.squeeze()
            fbs_pobfo_array = fbs_pobfo(ob_xy,fo_xy,grade_list = grade_list,half_window_size_list = half_window_size_list,
                                              compare = compare,masker = masker_xy)

            fss1 = 1 - fbs_pobfo_array[...,2]/(fbs_pobfo_array[...,0]+fbs_pobfo_array[...,1] + 1e-30)
            for j in range(nw):
                for k in range(nt):
                    result_one = {"time":time1,"dtime":dtime1,"fname":member1,
                                  "half_window_size":half_window_size_list[j],"grade":grade_list[k],
                                  "pob":fbs_pobfo_array[j,k,0],
                                  "pfo":fbs_pobfo_array[j,k,1],
                                  "fbs": fbs_pobfo_array[j, k, 2],
                                  "fss":fss1[j,k]}
                    result.append(result_one)
    df = pd.DataFrame(result)
    result_sta = meteva.base.sta_data(df)
    return result_sta


def fbs_pobfo(ob_xy, fo_xy,grade_list=[1e-30],half_window_size_list=[1],compare = ">=", masker=None):
    '''
    :param Ob: 实况数据 2维的numpy
    :param Fo: 实况数据 2维的numpy
    :param window_sizes_list: 卷积窗口宽度的列表，以格点数为单位
    :param threshold_list:  事件发生的阈值
    :param Masker:  2维的numpy检验的关注区域，在Masker网格值取值为0或1，函数只对网格值等于1的区域的数据进行计算。
    :return:
    '''
    def moving_ave(dat_xy, half_window_size):
        size = half_window_size * 2 + 1
        dat1 = uniform_filter(dat_xy, size=size)
        dat1 = np.round(dat1[:, :], 10)
        return dat1

    if compare not in [">=",">","<","<="]:
        print("compare 参数只能是 >=   >  <  <=  中的一种")
        return
    shape = ob_xy.shape
    nw = len(half_window_size_list)
    nt = len(grade_list)
    result = np.zeros((nw,nt,3))
    if masker is None:
        count = ob_xy.size
    else:
        count = np.sum(masker)

    for j in range(nt):
        ob_01 = np.zeros(shape)
        fo_01 = np.zeros(shape)
        if compare == ">=":
            ob_01[ob_xy>=grade_list[j]]  = 1
            fo_01[fo_xy>=grade_list[j]]  = 1
        elif compare =="<=":
            ob_01[ob_xy<=grade_list[j]]  = 1
            fo_01[fo_xy<=grade_list[j]]  = 1
        elif compare ==">":
            ob_01[ob_xy>grade_list[j]]  = 1
            fo_01[fo_xy>grade_list[j]]  = 1
        else:
            ob_01[ob_xy<grade_list[j]]  = 1
            fo_01[fo_xy<grade_list[j]]  = 1
        for i in range(nw):
            ob_01_smooth = moving_ave(ob_01, half_window_size_list[i])
            fo_01_smooth = moving_ave(fo_01, half_window_size_list[i])
            if masker is not None:
                ob_01_smooth *= masker
                fo_01_smooth *= masker
            result[i,j,2] = np.sum(np.square(ob_01_smooth - fo_01_smooth))
            result[i,j,0]  = np.sum(np.square(ob_01_smooth))
            result[i,j,1]  = np.sum(np.square(fo_01_smooth))

    result /= count
    return result


def fss_time_base_on_mid(mid_array):
    '''

    :param mid_array:
    :return:
    '''
    result = 1 - mid_array[..., 0] / (mid_array[..., 1] + 1e-30)
    return result



def fss_time(Ob,Fo,grade_list = [1e-30],compare =">-",window_size = None):
    '''
    :param Ob: 二维numpy数组Ob[i,j]，其中i取值为0  - 站点数， j为取值为0 - 时效维度的size
    :param Fo: 二维numpy数组Fo[i,j]，其中i取值为0  - 站点数， j为取值为0 - 时效维度的size
    :param window_size:
    :param grade_list:
    :return:
    '''
    mid_array = mid_fss_time(Ob,Fo,grade_list,window_size=window_size,compair = compare)
    result = fss_time_base_on_mid(mid_array)
    return result

#

def merge_mid_fss_time(mid_array1,mid_array2):
    '''

    :param mid_array1:
    :param mid_array2:
    :return:
    '''
    if mid_array1 is None:
        return mid_array2
    if mid_array2 is None:
        return mid_array1
    return mid_array1 + mid_array2

def mid_fss_time(Ob,Fo,grade_list = [1e-30],compare =">-",compair = ">=",window_size = None):
    '''
    :param Ob: 二维numpy数组Ob[i,j]，其中i取值为0  - 站点数， j为取值为0 - 时效维度的size
    :param Fo: 二维numpy数组Fo[i,j]，其中i取值为0  - 站点数， j为取值为0 - 时效维度的size
    :param window_size:
    :param grade_list:
    :return:
    '''
    if compair not in [">=",">","<","<="]:
        print("compair 参数只能是 >=   >  <  <=  中的一种")
        return
    shape = Ob.shape
    if len(shape) == 1:
        Ob = Ob.reshape(1,shape[0])
        Fo = Fo.reshape(1,shape[0])
        shape = Ob.shape
    if window_size is None:
        window_size = shape[1]//3
    left_size = shape[1] - window_size
    ng = len(grade_list)
    result = np.zeros((ng,window_size,left_size,2))
    for i in range(1,1+window_size):
        for j in range(left_size):
            for g in range(ng):
                ob1 = np.zeros((shape[0],i))
                fo1 = np.zeros((shape[0],i))
                if compair == ">=":
                    ob1[Ob[:, j + window_size -i:j+window_size] >= grade_list[g]] = 1
                    fo1[Fo[:, j + window_size -i:j+window_size] >= grade_list[g]] = 1
                elif compair == "<=":
                    ob1[Ob[:, j + window_size -i:j+window_size] <= grade_list[g]] = 1
                    fo1[Fo[:, j + window_size -i:j+window_size] <= grade_list[g]] = 1
                elif compair == ">":
                    ob1[Ob[:, j + window_size -i:j+window_size] > grade_list[g]] = 1
                    fo1[Fo[:, j + window_size -i:j+window_size] > grade_list[g]] = 1
                elif compair == "<":
                    ob1[Ob[:, j + window_size -i:j+window_size] < grade_list[g]] = 1
                    fo1[Fo[:, j + window_size -i:j+window_size] < grade_list[g]] = 1

                ob_hap_p =np.sum(ob1,axis=1)
                fo_hap_p =np.sum(fo1,axis=1)
                result[g,i - 1, j,  0] = np.sum(np.power(ob_hap_p - fo_hap_p, 2))
                result[g,i - 1, j,  1] = np.sum(np.power(ob_hap_p, 2)) + np.sum(np.power(fo_hap_p, 2))
    return result



def fss_fof(fbs_pobfo_array):
    '''
    :param fbs_pobfo_array:
    :return:
    '''

    if fbs_pobfo_array[..., 0].size == 1:
        fss1 = 1 - fbs_pobfo_array[2] / (fbs_pobfo_array[0] + fbs_pobfo_array[1] + 1e-30)
    else:
        fss1 = 1 - fbs_pobfo_array[..., 2] / (fbs_pobfo_array[..., 0] + fbs_pobfo_array[..., 1] + 1e-30)
    return fss1
