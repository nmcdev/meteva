from nmc_verification.nmc_vf_method import *
from nmc_verification.nmc_vf_product.base.fun import *
import numpy as np

def table(sta_ob_and_fos,method,group_by = None,group_list_list = None,save_dir = None,para1 = None):
    sta_ob_and_fos_list,group_list_list1 = group_data(sta_ob_and_fos,group_by,group_list_list)
    data_name = nmc_verification.nmc_vf_base.get_stadata_names(sta_ob_and_fos)
    fo_num = len(data_name) -1
    ensemble_score_method = [nmc_verification.nmc_vf_method.cr]
    group_num = len(sta_ob_and_fos_list)

    valid_group_list_list = []
    result_all = []
    if type(method) == str:
        method =  globals().get(method)
    if method in ensemble_score_method:
        pass
    else:
        for i in range(group_num):
            sta = sta_ob_and_fos_list[i]
            if(len(sta.index) == 0):
                pass
            else:
                valid_group_list = None
                if group_list_list1 is None:
                    valid_group_list_list = None
                else:
                    valid_group_list = group_list_list1[i]
                    valid_group_list_list.append(group_list_list1[i])
                ob = sta[data_name[0]].values
                result_all1 = []
                for j in range(fo_num):

                    fo = sta[data_name[j+1]].values
                    save_path = get_save_path(save_dir,method,group_by,valid_group_list,data_name[j+1],".xlsx")

                    if para1 is None:
                        result1 = method(ob, fo,save_path = save_path)
                    else:
                        result1 = method(ob, fo,para1,save_path = save_path)
                    result_all1.append(result1)
                result_all.append(result_all1)
        result_all = np.array(result_all)
    result = result_all.squeeze()

    return result,valid_group_list_list


