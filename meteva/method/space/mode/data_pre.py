# -*- coding: utf-8 -*-
"""
Created on Tue Oct 20 16:26:07 2020

@author: 1
"""
import numpy as np
import xarray as xr
import meteva

#提取连通域分析以后被标记的数据
def pick_labels(data):
    ret = {}
    for item, values in data.items():
        if isinstance(item,int):
            #print(item, values)
            ret0 = {item : values}
            ret.update(ret0)
    return ret

#连通域分析后被标记的目标
def relabeled(x):
    label = np.array(())
    ret = None
    for i in range(len(x)):
        label = x['labels_'+str(i+1)]
        label[label == 1] = i+1
        if ret is None:
            ret = label
        else: 
            ret =ret + label
    return ret

#利用xarray将数据转换为grid格式
def get_grd(dataset_ob, data):
    #dataset_ob参数是为了获取原始场的起始经纬度坐标和间隔
    #整理无坐标信息的格点场的坐标：原始的观测场和预报场的经纬度范围应该是对应的
    glon = [dataset_ob["lon"].values[0], dataset_ob["lon"].values[-1],
            dataset_ob["lon"].values[1]-dataset_ob["lon"].values[0]]    #经度的起点、终点、间隔
    glat = [dataset_ob["lat"].values[0], dataset_ob["lat"].values[-1],
             dataset_ob["lat"].values[1]-dataset_ob["lat"].values[0]]    #纬度的起点、终点、间隔

    grid1 = meteva.base.grid(glon, glat)
    data_tr = meteva.base.grid_data(grid1, data)
    return data_tr 

#调整数组存放结构
def funtion(fo_id_list,ob_id_list):

    n_row = len(ob_id_list)
    ob_index_dict = {}
    fo_index_dict = {}
    index_list_dict = {}
    index = 0

    for i in range(n_row):
        if ob_id_list[i] in ob_index_dict.keys() or fo_id_list[i] in fo_index_dict.keys():
            if ob_id_list[i] in ob_index_dict.keys():
                index1 = ob_index_dict[ob_id_list[i]]
                fo_index_dict[fo_id_list[i]] = index1
            elif fo_id_list[i] in fo_index_dict.keys():
                index1 = fo_index_dict[fo_id_list[i]]
                ob_index_dict[ob_id_list[i]] = index1
        else:
            ob_index_dict[ob_id_list[i]] = index
            fo_index_dict[fo_id_list[i]] = index
            index1 = index
            index_list_dict[index1] = []
            index = index + 1
        index_list_dict[index1].append([fo_id_list[i],ob_id_list[i]])

    list_list = list(index_list_dict.values())

    #将ob,或fo id有重复的列表进行合并
    while True:
        len0 = len(list_list)
        changed = False
        for i in range(len0-1):
            dat_i = np.array(list_list[i])
            ob_seti = set(dat_i[:,0])
            fo_seti = set(dat_i[:,1])
            for j in range(i+1,len0):
                dat_j = np.array(list_list[j])
                ob_setj = set(dat_j[:,0])
                fo_setj = set(dat_j[:,1])
                if len(ob_seti&ob_setj) >0 or  len(fo_seti&fo_setj) >0:
                    list_list[i].extend(list_list[j])
                    list_list.pop(j)
                    changed = True
                    break
            if changed:
                break
        if not changed:
            break
    return list_list

#if __name__ == '__main__':
    #fo_id_list = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 3, 3, 4, 5, 5, 5, 8, 9, 10]
    #ob_id_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13, 14, 15, 16, 17, 19, 9, 7, 10, 14, 14, 15, 22, 19, 20, 23]

    #list_list = funtion(fo_id_list,ob_id_list)