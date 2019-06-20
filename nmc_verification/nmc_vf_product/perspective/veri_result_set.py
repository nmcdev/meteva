
import nmc_verification
import numpy as np
import xarray as xr

#检验结果设置类
class veri_result_set:
    #类初始化一些默认参数
    def __init__(self,vmethod_list, grade_list = None,sta_data_set = None,save_dir = None):
        self.vmethod_list = vmethod_list
        self.grade_list = grade_list
        self.sta_data_set = sta_data_set
        self.save_dir = save_dir
        self.result = None
    
    #获取检验结果
    def get_veri_result(self):
        result = []
        data_names = nmc_verification.nmc_vf_base.get_data_names(self.sta_data_set.sta_data)
        sta_list, para_dict_list_list,para_dict_list_string = self.sta_data_set.get_sta_list()
        for vmethod in self.vmethod_list:
            if vmethod.lower() == "ts":
                for sta in sta_list:
                    _,ts_list = nmc_verification.nmc_vf_product.yes_or_no.ts(sta,self.grade_list)
                    result.append(ts_list)
            elif vmethod.lower() == "bias":

                for sta in sta_list:
                    _,ts_list = nmc_verification.nmc_vf_product.yes_or_no.bias(sta,self.grade_list)
                    result.append(ts_list)
            elif vmethod.lower() == "mis_rate":

                for sta in sta_list:
                    _,ts_list = nmc_verification.nmc_vf_product.yes_or_no.mis_rate(sta,self.grade_list)
                    result.append(ts_list)
            elif vmethod.lower() == "fal_rate":

                for sta in sta_list:
                    _,ts_list = nmc_verification.nmc_vf_product.yes_or_no.fal_rate(sta,self.grade_list)
                    result.append(ts_list)
            else:
                pass

        shape = [len(self.vmethod_list)]
        coords = {}
        coords['vmethod'] = self.vmethod_list
        dims = ["vmethod"]

        for key in para_dict_list_list.keys():
            shape.append(len(para_dict_list_list[key]))
            coords[key] = para_dict_list_string[key]
            dims.append(key)

        shape.append(len(data_names) -1)
        coords['member'] = data_names[1:]
        dims.append('member')

        if(self.grade_list is not None):
            shape.append(len(self.grade_list))
            coords["grade"] = self.grade_list
            dims.append("grade")

        shape = tuple(shape)
        result_array = np.array(result).reshape(shape)
        print(coords)
        print(dims)
        result_xr = xr.DataArray(result_array,coords = coords,dims = dims)

        self.result = result_xr
        return result_xr

    #保存检验结果
    def save_veri_result(self):
        pass
    
    #下载检验结果
    def load_veri_result(self):
        pass



