#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 28 15:50:52 2023

@author: tangbuxing
"""
import sys
import numpy as np
import matplotlib.pyplot as plt
import meteva
from  matplotlib import  cm


def Geo_Box_Plot(frequency_ob,frequency_fo,grade_list,member_list = None):
    out = {}
    if len(frequency_ob) != len(grade_list) :
        sys.exit("参数frequency_ob与参数grade_list长度需一样。")
        return
    if len(frequency_fo) != len(grade_list) :
        sys.exit("参数frequency_fo与参数grade_list长度需一样。")
        return



    if member_list is None:
        xticks = ['观测']
        if member_list[0] == 1:
            xticks.append('预报')
        else:
            for i in range(member_list[0]):
                xticks.append('预报' + str(i + 1))
    else:
        xticks = member_list


    obs_array = np.array([])
    for i in range(len(grade_list)):
        c = np.repeat(grade_list[i],frequency_ob[i])
        #print(c)
        obs_array = np.append(obs_array, c)
        #print(d)

    fst_array = np.array([])
    for i in range(len(grade_list)):
        c = np.repeat(grade_list[i],frequency_fo[i])
        #print(c)
        fst_array= np.append(fst_array, c)
        #print(d)
    out = plt.boxplot(np.array([obs_array,fst_array]), labels=xticks)



    plt.show()
    plt.close()
    return


def GeoBoxPlot(x, areas):
    out = {}
    if len(x) != len(areas):
        sys.exit("参数x与参数areas长度需一样。")
    d = np.array([])

    for i in range(len(x)):
        c = np.repeat(x[i],areas[i])
        #print(c)
        d = np.append(d, c)
        #print(d)
    out = plt.boxplot(d)
    plt.show()
    plt.close()
    return
    
if __name__ == '__main__':

    #x = [4,9,1,3,10,6,7]
    #areas = [1,1,1,1,2,1,3]
    #GeoBoxPlot(x, areas)
    import meteva.base as meb
    path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    path_fo = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo = meb.read_griddata_from_nc(path_fo, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")
    obs_array = grd_ob.values.squeeze()
    fst_array = grd_fo.values.squeeze()

    conf_mx = meteva.method.multi_category.table.frequency_table(obs_array,fst_array,grade_list=np.arange(0,300))

    print(conf_mx)








