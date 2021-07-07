# -*- coding: utf-8 -*-
"""
Created on Wed Jan 13 11:08:18 2021

@author: 1
"""
import meteva
import copy
import numpy as np


def center_distance(grd1,grd2):
    lon1,lat1 = center_of_mass(grd1)
    lon2,lat2 = center_of_mass(grd2)
    dis  = meteva.base.math_tools.earth_surface_dis(lon1,lat1,lon2,lat2)
    return dis

def center_of_mass(grd):
    grid0 = meteva.base.get_grid_of_data(grd)
    data_array_2D = grd.values.squeeze()
    xd = data_array_2D.shape
    xx, yy = np.meshgrid(np.arange(xd[1]), np.arange(xd[0]))
    data_sum = np.sum(data_array_2D)
    xx_c = np.sum(data_array_2D * xx) / data_sum
    yy_c = np.sum(data_array_2D * yy) / data_sum
    lon_c = grid0.slon + xx_c * grid0.dlon
    lat_c = grid0.slat + yy_c * grid0.dlat
    return lon_c,lat_c



def intRamt(look,ob_or_fo = "ob"):
        # 提取目标的总质量，和最大值
        if ob_or_fo != "ob":
            ob_or_fo  = "fo"
        grd_data = look["grd_"+ob_or_fo].values.squeeze()  # 提取原始网格数据值
        grd_feats = look["grd_"+ob_or_fo+"_features"]      # 提取观测或目标属性
        label_count = grd_feats["label_count"]
        mass = []
        max_value = []
        lon_c = []
        lat_c = []
        mean_value = []
        grid0 = look["grid"]
        for i in range(1, label_count+ 1):
            index1 = grd_feats[i]      #提取某一个目标的对应的各个点的位置
            data = grd_data[index1]    #提取某一个目标的对应的各个点的网格值
            # 求和
            v_sum_0 = np.sum(data)
            mass.append(v_sum_0)

            #求平均值
            mean_value.append(v_sum_0 / len(data))

            # 求最大值
            v_max_0 = np.max(data)
            max_value.append(v_max_0)


            #质心经度
            lon_c_0 = np.sum(index1[1] * data) / v_sum_0
            lon_c_0 = grid0.slon + grid0.dlon * lon_c_0
            lon_c.append(lon_c_0)

            #质心纬度
            lat_c_0 = np.sum(index1[0] * data) / v_sum_0
            lat_c_0 = grid0.slat + grid0.dlat * lat_c_0
            lat_c.append(lat_c_0)


        return np.array(mass),np.array(mean_value),np.array(max_value),np.array(lon_c),np.array(lat_c)


def sal(look):

    tmp = copy.deepcopy(look)
    grid0 =tmp["grid"]

    grd_ob = tmp["grd_ob"]
    grd_fo = tmp["grd_fo"]
    #计算强度误差
    #DomR_fo = np.mean(grd_fo.values)   #计算整场降水的平均值
    #DomR_ob = np.mean(grd_ob.values)   #计算整场降水的平均值
    #A = 2 * (DomR_fo - DomR_ob)/(DomR_fo + DomR_ob)  #返回内容A

    grd_ob_label = tmp["grd_ob_label"]
    index1 = np.where((grd_ob_label.values ==0))
    grd_ob.values[index1] =0  # 将未识别成目标的零散降水值置位0

    grd_fo_label = tmp["grd_fo_label"]
    index2 = np.where((grd_fo_label.values ==0))
    grd_fo.values[index2] =0  # 将未识别成目标的零散降水值置位0

    DomR_fo = np.mean(grd_fo.values)   #计算整场降水的平均值
    DomR_ob = np.mean(grd_ob.values)   #计算整场降水的平均值
    A = 2 * (DomR_fo - DomR_ob)/(DomR_fo + DomR_ob)  #返回内容A

    dmax = meteva.base.math_tools.earth_surface_dis(grid0.slon,grid0.slat,grid0.elon,grid0.elat)  #计算网格对角线的长度
    cen_ob_lon,cen_ob_lat = center_of_mass(tmp['grd_ob'])   #计算观测场的整场质心
    cen_fo_lon,cen_fo_lat = center_of_mass(tmp['grd_fo'])   #计算预报场的整场质心
    dis_between_centers = meteva.base.math_tools.earth_surface_dis(cen_ob_lon,cen_ob_lat,cen_fo_lon,cen_fo_lat)  # 计算观测预报整场质心间距离
    L1 = dis_between_centers/dmax         #返回内容L1

    #计算各目标的质量，平均值，最大值，质心位置
    mass_ob,mean_value_ob,max_value_ob,lon_c_ob,lat_c_ob = intRamt(tmp,ob_or_fo="ob")
    mass_fo,mean_value_fo,max_value_fo,lon_c_fo,lat_c_fo  = intRamt(tmp,ob_or_fo="fo")

    #计算观测的目标质心距离观测的整场质心的距离
    center_distance_label_to_grd_ob = np.zeros(len(lon_c_ob))
    for i in range(len(lon_c_ob)):
        dis1 = meteva.base.math_tools.earth_surface_dis(lon_c_ob[i], lat_c_ob[i],cen_ob_lon,cen_ob_lat)
        center_distance_label_to_grd_ob[i] = dis1

    #计算预报的目标质心距离观测的整场质心的距离
    center_distance_label_to_grd_fo  = np.zeros(len(lon_c_fo))
    for i in range(len(lon_c_fo)):
        dis1 = meteva.base.math_tools.earth_surface_dis(lon_c_fo[i], lat_c_fo[i],cen_fo_lon,cen_fo_lat)
        center_distance_label_to_grd_fo[i] = dis1

    mass_sum_ob = np.sum(mass_ob)  # 观测目标的质量总和
    mass_sum_fo = np.sum(mass_fo) # 预报目标的质量总和
    r_ob = np.sum(mass_ob * center_distance_label_to_grd_ob)/mass_sum_ob  #各目标距离整场质心的平均距离
    r_fo = np.sum(mass_fo * center_distance_label_to_grd_fo)/mass_sum_fo  #各目标距离整场质心的平均距离

    L2 = 2 * abs(r_fo - r_ob)/dmax  #返回内容L2


    #grd_ob_label.values[grd_ob_label.values!=0] = 1
    #grd_fo_label.values[grd_fo_label.values!=0] = 1
    #L1_labeled = center_distance(grd_ob_label,grd_fo_label)/dmax   #观测和预报目标场（不区分降水长度）的质心之间的距离

    v_ob = mean_value_ob/max_value_ob  # 用 平均值/最大值 表征一致性
    v_fo = mean_value_fo/max_value_fo  # 用 平均值/最大值 表征一致性
    V_ob = np.sum(mass_ob*v_ob)/np.sum(mass_ob)    #所有目标平均的 强度一致性
    V_fo = np.sum(mass_fo*v_fo)/np.sum(mass_fo)    #所有目标平均的 强度一致性

    S = 2 * (V_fo - V_ob)/(V_fo + V_ob)

    out={
        "S": S,
        'A':A,
        "L":L1+L2,
        "L1": L1,
        "L2": L2
    }
    return out
