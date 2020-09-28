from meteva.base.fun.grouping import *
from meteva.product.program.fun import *
from meteva.base.fun.selecting import *
import numpy as np

def table(sta_ob_and_fos0,method,s = None,g = None,gll = None,save_dir = None,**kwargs):
    if s is not None:
        if g is not None:
            if g == "last_range" or g == "last_step":
                s["drop_last"] = False
            else:
                s["drop_last"] = True
    sta_ob_and_fos = sele_by_dict(sta_ob_and_fos0, s)
    if(len(sta_ob_and_fos.index) == 0):
        print("there is no data to verify")
        return
    sta_ob_and_fos_list,gll1 = group(sta_ob_and_fos,g,gll)
    data_name = meteva.base.get_stadata_names(sta_ob_and_fos_list[0])
    ensemble_score_method = [meteva.method.cr]
    group_num = len(sta_ob_and_fos_list)

    valid_gll = []
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
                if gll1 is None:
                    valid_gll = None
                else:
                    valid_group_list = gll1[i]
                    valid_gll.append(gll1[i])
                ob = sta[data_name[0]].values
                fo = sta[data_name[1:]].values.T

                kwargs1 = copy.deepcopy(kwargs)
                if "save_path" not in kwargs.keys():
                    kwargs1["save_path"] = get_save_path(save_dir,method,g,valid_group_list,type = ".xlsx")
                kwargs1["member_list"] = data_name[1:]
                result1 = method(ob, fo, **kwargs1)
                result_all.append(result1)
        result_all = np.array(result_all)
    result = result_all.squeeze()

    return result,valid_gll


