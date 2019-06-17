import nmc_verification
import numpy as np

def ts(sta,grade_list):
    data_names = nmc_verification.nmc_vf_base.basicdata.get_data_names(sta)
    ob = sta[data_names[0]].values
    fo_num = len(data_names) - 1
    ts_list = []
    for i in range(fo_num):
        fo = sta[data_names[i+1]].values
        ts = nmc_verification.nmc_vf_method.yes_or_no.score.ts(ob,fo,grade_list)
        ts_list.append(ts.tolist())
    ts_array = np.array(ts_list)
    ts_array = ts_array.reshape((fo_num,len(grade_list)))
    return ts_array,ts_list


def bias(sta,grade_list):
    data_names = nmc_verification.nmc_vf_base.basicdata.get_data_names(sta)
    ob = sta[data_names[0]].values
    fo_num = len(data_names) - 1
    ts_list = []
    for i in range(fo_num):
        fo = sta[data_names[i+1]].values
        ts = nmc_verification.nmc_vf_method.yes_or_no.score.bias(ob,fo,grade_list)
        ts_list.append(ts.tolist())
    ts_array = np.array(ts_list)
    ts_array = ts_array.reshape((fo_num,len(grade_list)))
    return ts_array,ts_list