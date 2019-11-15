import nmc_verification
import numpy as np
import xarray as xr
import copy


#检验一种sta,一种方法的结果
def ver_one_groupsta_one_method(sta,vmethod,para1,para2,data_names,sample_same):
    fo_num = len(data_names) - 1
    result = []
    if sta is not None and len(sta.index) > 0:
        #print(len(sta.index))
        data = copy.deepcopy(sta[data_names].values)
        if sample_same:
            # 首先判断全为9999的模式个数
            all_9999_num = 0
            for i in range(fo_num):
                fo = data[:,i+1]
                index = np.where(fo != 9999)
                #print(index)
                if len(fo[fo!=9999])== 0:
                    all_9999_num += 1

            #判断每一行为9999的数目是否等于 all_9999_num
            is_9999 = np.zeros(data.shape)
            is_9999[data !=9999] = 0
            is_9999[data == 9999] = 1
            #对于那些非全为9999的行
            sum_is_9999 = np.sum(is_9999,axis=1)
            index = np.where(sum_is_9999 == all_9999_num)[0]
            data = data[index,:]

    for i in range(fo_num):
        result_one_model = None
        if sta is not None and len(sta.index) > 0:

            ob = data[:, 0]
            fo = data[:,i+1]
            if not sample_same:
                ob = ob[fo != 9999]
                fo = fo[fo != 9999]

            if len(fo) > 0 and fo[0] != 9999:
                #print(fo[fo>1])
                if vmethod == "hmfn":
                    result_one_model = np.array(list(nmc_verification.nmc_vf_method.yes_or_no.score.hmfn(ob,fo,para1)))
                else:
                    result_one_model = np.array(list(nmc_verification.nmc_vf_method.yes_or_no.score.hmfn_of_sunny_rainy(ob, fo)))

        if result_one_model is None:
            if vmethod == "hmfn":
                result_one_model = np.zeros(4 * len(para1))
            else:
                result_one_model = np.zeros(4)

        re_list = result_one_model.flatten().tolist()
        #print(re_list)
        result.append(re_list)
    return result


# 输出中间检验结果,它是一个三维数组
def get_middle_veri_result(sta_list,para,data_name_list):

    #para 是中间量检验的参数

    sample_same = para["sample_must_be_same"]
    model_num = len(data_name_list) -1
    #print(data_name_list)

    veri_list_3d = []
    for sta in sta_list:
        #print(sta)
        veri_list_list = []
        for i in range(model_num):
            veri_list_list.append([])

        #计算总的非9999样本数
        if sta is None or len(sta.index)==0:
            for i in range(model_num):
                veri_list_list[i].append(0)
        else:
            for i in range(model_num):
                model_name = data_name_list[i + 1]
                fo = sta[model_name].values
                fo = fo[fo != 9999]
                veri_list_list[i].append(len(fo))

        para1 = None
        para2 = None
        if "para1" in para.keys():
            para1 = para["para1"]
        if "para2" in para.keys():
            para2 = para["para2"]
        for vmethod in para["method"]:
            result = ver_one_groupsta_one_method(sta,vmethod,para1,para2,data_name_list,sample_same)
            #print(result)
            for i in range(model_num):
                veri_list_list[i].extend(result[i])
        veri_list_3d.append(veri_list_list)
    veri_array_3d = np.array(veri_list_3d)
    return veri_array_3d



# 输出中间检验结果：
def get_middle_veri_result1(sta_data_set,para):
    result = []
    data_names = nmc_verification.nmc_vf_base.get_undim_data_names(sta_data_set.sta_data)
    sta_list, para_dict_list_list, para_dict_list_string = sta_data_set.get_sta_list()
    vmethod_list = []
    for vmethod in para["method"]:
        if vmethod.lower() == "hmfn":
            vmethod_list.extend(["hit","mis","fal","cn"])
            for sta in sta_list:
                hmfn_list = nmc_verification.nmc_vf_product.yes_or_no.hmfn(sta, para["para1"])
                result.append(hmfn_list)
        if vmethod.lower() == "abcd":
            vmethod_list.extend(["na","nb","nc","nd"])
            for sta in sta_list:
                abcd_list = nmc_verification.nmc_vf_product.yes_or_no.abcd(sta)
                result.append(abcd_list)

        else:
            pass

        shape = []
        coords = {}
        dims = []
        for key in para_dict_list_list.keys():
            shape.append(len(para_dict_list_list[key]))
            coords[key] = para_dict_list_string[key]
            dims.append(key)

        shape.append(len(data_names) - 1)
        coords['member'] = data_names[1:]
        dims.append('member')

        shape.append(len(vmethod_list))
        coords['vmethod'] = vmethod_list
        dims.append("vmethod")

        if("para1" in para.keys()):
            para1 = para["para1"]
            if (para1 is not None):
                shape.append(len(para1))
                coords["para1"] = para1
                dims.append("para1")

        shape = tuple(shape)
        result_array = np.array(result).reshape(shape)
        #print(coords)
        #print(dims)
        result_xr = xr.DataArray(result_array, coords=coords, dims=dims)
        return result_xr

    # 保存检验结果
    def save_veri_result(self):
        pass

    # 下载检验结果
    def load_veri_result(self):
        pass
