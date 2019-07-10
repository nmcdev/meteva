import nmc_verification
import numpy as np

#TS评分
def ts(sta,grade_list):
    data_names = nmc_verification.nmc_vf_base.basicdata.get_undim_data_names(sta)
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

#计算偏差值
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

#漏报率
def mis_rate(sta,grade_list):
    data_names = nmc_verification.nmc_vf_base.basicdata.get_data_names(sta)
    ob = sta[data_names[0]].values
    fo_num = len(data_names) - 1
    ts_list = []
    for i in range(fo_num):
        fo = sta[data_names[i+1]].values
        ts = nmc_verification.nmc_vf_method.yes_or_no.score.mis_rate(ob,fo,grade_list)
        ts_list.append(ts.tolist())
    ts_array = np.array(ts_list)
    ts_array = ts_array.reshape((fo_num,len(grade_list)))
    return ts_array,ts_list

#失败率
def fal_rate(sta,grade_list):
    data_names = nmc_verification.nmc_vf_base.basicdata.get_data_names(sta)
    ob = sta[data_names[0]].values
    fo_num = len(data_names) - 1
    ts_list = []
    for i in range(fo_num):
        fo = sta[data_names[i+1]].values
        ts = nmc_verification.nmc_vf_method.yes_or_no.score.fal_rate(ob,fo,grade_list)
        ts_list.append(ts.tolist())
    ts_array = np.array(ts_list)
    ts_array = ts_array.reshape((fo_num,len(grade_list)))
    return ts_array,ts_list


#hmfc命中，漏报，空报，正确否定
def hmfn(sta,grade_list):
    data_names = nmc_verification.nmc_vf_base.basicdata.get_undim_data_names(sta)
    ob = sta[data_names[0]].values
    fo_num = len(data_names) - 1
    re_list = []
    for i in range(fo_num):
        fo = sta[data_names[i+1]].values
        hit,mis,fal,cn = nmc_verification.nmc_vf_method.yes_or_no.score.hmfn(ob,fo,grade_list)
        re_list.append(hit.tolist())
        re_list.append(mis.tolist())
        re_list.append(fal.tolist())
        re_list.append(cn.tolist())
    return re_list

#abcd,晴雨准确率计算联立表，命中，漏报，空报，正确否定
def abcd(sta):
    data_names = nmc_verification.nmc_vf_base.basicdata.get_undim_data_names(sta)
    ob = sta[data_names[0]].values
    fo_num = len(data_names) - 1
    re_list = []
    for i in range(fo_num):
        fo = sta[data_names[i+1]].values
        hit,mis,fal,cn = nmc_verification.nmc_vf_method.yes_or_no.score.abcd_of_sunny_rainy(ob,fo)
        re_list.append(hit.tolist())
        re_list.append(mis.tolist())
        re_list.append(fal.tolist())
        re_list.append(cn.tolist())
    return re_list
