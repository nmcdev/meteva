
from nmc_verification.nmc_vf_method import *
from nmc_verification.nmc_vf_product.base.fun import *
import numpy as np



def score(sta_ob_and_fos,method,group_by = None,group_list_list = None,para1 = None):
    sta_ob_and_fos_list,group_list_list1 = group_data(sta_ob_and_fos,group_by,group_list_list)
    data_name = nmc_verification.nmc_vf_base.get_stadata_names(sta_ob_and_fos)
    fo_num = len(data_name) -1
    ensemble_score_method = [nmc_verification.nmc_vf_method.cr]
    group_num = len(sta_ob_and_fos_list)
    if para1 is None:
        para_num = 1
    else:
        para_num = len(para1)

    if type(method) == str:
        method =  globals().get(method)
    if method in ensemble_score_method:
        result = np.zeros((group_num,para_num))
        for i in range(group_num):
            sta = sta_ob_and_fos_list[i]
            if(len(sta.index) == 0):
                result[i,:] = nmc_verification.nmc_vf_base.IV
            else:
                ob = sta[data_name[0]].values
                fo = sta[data_name[1:]].values
                if para1 is None:
                    result[i, :] = method(ob, fo)
                else:
                    result[i,:] = method(ob, fo,para1)
    else:
        result = np.zeros((group_num,fo_num,para_num))
        for i in range(group_num):
            sta = sta_ob_and_fos_list[i]
            if(len(sta.index) == 0):
                result[i,:] = nmc_verification.nmc_vf_base.IV
            else:
                ob = sta[data_name[0]].values
                for j in range(fo_num):
                    fo = sta[data_name[j+1]].values
                    if para1 is None:
                        result[i, j] = method(ob, fo)
                    else:
                        result[i,j] = method(ob, fo,para1)

    result = result.squeeze()
    return result,group_list_list1


'''
df = pd.DataFrame({"level":[850,500],
                   "time":[datetime.datetime(2018,1,1,8,0),datetime.datetime(2019,12,20,20,0)],
                   "dtime":[12,36],
                   "id":[54511,54512],
                   "lon":[100,110],
                  "lat":[30,40],
                  "ob":[0,2],
                  "fo1":[1,1],
                  "fo2":[2,3]})
sta = nmc_verification.nmc_vf_base.sta_data(df)
print(sta)
veri = score(sta,nvm.mae,group_by="ob_day")
print(veri)
'''
