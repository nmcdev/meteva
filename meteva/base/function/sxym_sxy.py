import numpy as np
import meteva
import pandas as  pd
def mean_of_sta_ensemble(sta_ensemble):
    sta_mean = sta_ensemble[meteva.base.get_coord_names()]
    sta_data = sta_ensemble[meteva.base.get_data_names(sta_ensemble)]
    value = sta_data.values
    mean = np.mean(value,axis=1)
    sta_mean['data0'] =mean
    return sta_mean

def std_of_sta_ensemble(sta_ensemble):
    sta_std = sta_ensemble[meteva.base.get_coord_names()]
    sta_data = sta_ensemble[meteva.base.get_data_names(sta_ensemble)]
    value = sta_data.values
    std = np.std(value, axis=1)
    sta_std['data0'] = std
    return sta_std

def var_of_sta_ensemble(sta_ensemble):
    sta_var = sta_ensemble[meteva.base.get_coord_names()]
    sta_data = sta_ensemble[meteva.base.get_data_names(sta_ensemble)]
    value = sta_data.values
    var = np.var(value, axis=1)
    sta_var['data0'] = var
    return sta_var


def max_of_sta_ensemble(sta_ensemble):
    sta_max = sta_ensemble[meteva.base.get_coord_names()]
    sta_data = sta_ensemble[meteva.base.get_data_names(sta_ensemble)]
    value = sta_data.values
    max1 = np.max(value, axis=1)
    sta_max['data0'] = max1
    return sta_max

def min_fo_sta_ensemble(sta_ensemble):
    sta_min = sta_ensemble[meteva.base.get_coord_names()]
    sta_data = sta_ensemble[meteva.base.get_data_names(sta_ensemble)]
    value = sta_data.values
    min1 = np.min(value, axis=1)
    sta_min['data0'] = min1
    return sta_min

def get_one_element_by_name(sta_ensemble,name):
    column = meteva.base.get_coord_names()
    column.append(name)
    sta = sta_ensemble[column]
    return sta

def get_one_element_by_number(sta_ensemble,number):
    column = meteva.base.get_coord_names()
    data_names = meteva.base.get_data_names(sta_ensemble)
    column.append(data_names[number])
    sta = sta_ensemble[column]
    return sta