from nmc_verification.nmc_vf_base import *
from nmc_verification.nmc_vf_method import *
from nmc_verification.nmc_vf_product.base.fun import *

import numpy as np




def score(sta_ob_and_fos,method,group_by = None,group_list_list = None,para1 = None,para2 = None):
    if type(method) == str:
        method =  globals().get(method)
    if method == nmc_verification.nmc_vf_method.FSS_time:
        if group_by == "dtime":
            print("FSS_time 检验时，参数group_by不能选择dtime")
            return
    sta_ob_and_fos_list,group_list_list1 = group(sta_ob_and_fos,group_by,group_list_list)
    data_name = nmc_verification.nmc_vf_base.get_stadata_names(sta_ob_and_fos)
    fo_num = len(data_name) -1
    ensemble_score_method = [nmc_verification.nmc_vf_method.cr]
    group_num = len(sta_ob_and_fos_list)
    if para1 is None:
        para_num = 1
    else:
        para_num = len(para1)


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
    elif method == nmc_verification.nmc_vf_method.FSS_time:
        #统计dtime的集合
        dtime_list = list(set(sta_ob_and_fos["dtime"].values.tolist()))
        dtime_list.sort()
        ndtime = len(dtime_list)
        result= []
        for sta_ob_and_fo in sta_ob_and_fos_list:
            # 将观测和预报数据重新整理成FSS_time所需格式
            ob = in_member_list(sta_ob_and_fo,[data_name[0]])
            ob_dtimes = None
            for k in range(ndtime):
                dtimek = dtime_list[k]
                sta_obk = in_dtime_list(ob,[dtimek])
                set_stadata_names(sta_obk,[data_name[0]+ str(dtimek)])
                ob_dtimes = combine_on_leve_time_id(ob_dtimes,sta_obk)
            result1 = []
            #print(ob_dtimes)
            ob_array = ob_dtimes.values[:,6:]
            for j in range(fo_num):
                fo = in_member_list(sta_ob_and_fo, [data_name[j+1]])
                fo_dtimes = None
                for k in range(ndtime):
                    dtimek = dtime_list[k]
                    sta_fok = in_dtime_list(fo, [dtimek])
                    set_stadata_names(sta_fok, [data_name[j+1] + str(dtimek)])
                    fo_dtimes = combine_on_leve_time_id(fo_dtimes, sta_fok)
                fo_array = fo_dtimes.values[:,6:]

                #调用检验程序
                if para1 is None:
                    para1 = [1e-30]
                result2 = FSS_time(ob_array, fo_array, para1, para2)
                result1.append(result2)
            result.append(result1)

        result = np.array(result) #将数据转换成数组
    else:
        if fo_num ==0:
            result = np.zeros((group_num,para_num))
        else:
            result = np.zeros((group_num,fo_num,para_num))
        for i in range(group_num):
            #print(group_num)
            sta = sta_ob_and_fos_list[i]
            if(len(sta.index) == 0):
                result[i,:] = nmc_verification.nmc_vf_base.IV

            else:
                ob = sta[data_name[0]].values
                if fo_num>0:
                    for j in range(fo_num):
                        fo = sta[data_name[j+1]].values
                        if para1 is None:
                            result[i, j] = method(ob, fo)
                        else:
                            result[i,j] = method(ob, fo,para1)
                else:
                    if para1 is None:
                        result[i] = method(ob, None)
                    else:
                        result[i] = method(ob, None,para1)

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
