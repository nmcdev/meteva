import datetime
import numpy as np
import copy
import nmc_verification
import collections
import os
import xarray as xr

#将参数数组转换为列表
def para_array_to_list(key_num,para_array):
    key_list = []
    for key in para_array.keys():
        key_list.append(key)
    key_count = len(key_list)

    if(key_num ==key_count-1):
        key = key_list[key_num]
        para_list = []
        list1 = para_array[key]
        for para in list1:
            dict1 = {}
            dict1[key] = para
            para_list.append(dict1)
    else:
        key = key_list[key_num]
        list1 = para_array[key]
        para_list0 = para_array_to_list(key_num+1,para_array)
        para_list = []
        for para in list1:
            for dict0 in para_list0:
                dict1 = {}
                dict1[key] = para
                for key0 in dict0.keys():
                    dict1[key0] = copy.deepcopy(dict0[key0])
                #print(dict1)
                para_list.append(dict1)

    return para_list

def get_middle_veri_para(veri_para):
    nead_hmfc_methods = ["ts","bias","ets","fal_rate","hit_rate","mis_rate"]
    nead_abcd_methods = ["pc","spc"]

    mpara = copy.deepcopy(veri_para)
    methods = veri_para["method"]
    middle_vm = []
    for method in methods:
        if method in nead_hmfc_methods:
            mpara["method"] = ["hit","mis","fal","cn"]
            break
        if method in nead_abcd_methods:
            mpara["method"] = ["na","nb","nc","nd"]
            break
        if method == "FSS":
            middle_vm = ["E2","ob2_p_fo2"]
            break

    return mpara

def middle_veri_result_add(middle_already,middle_part,sample_same):
    if sample_same:
        total_num = middle_part[:,:,0]
        shape = list(middle_part.shape)
        model_num = shape[1]
        shape.append(model_num)
        shape = tuple(shape)
        middle_part_4d = np.zeros(shape)
        num_0 = np.zeros(total_num.shape)
        num_0[total_num == 0] = 1
        sum_num_0 = np.sum(num_0,axis=1)
        #print(sum_num_0)

        for i in range(model_num):
            middle_part_4d[:,:,:,i] = middle_part[:,:,:]
            index_has0 = np.where(sum_num_0>i)[0]
            middle_part_4d[index_has0, :, :, i] = 0

        if middle_already is not None:
            middle_part_4d += middle_already
        return middle_part_4d
    else:
        middle_part_3d = middle_part
        if middle_already is not None:
            middle_part_3d += middle_already
        return middle_part_3d

def cut_sta_not_after(sta,time):
    if sta is None:
        return None,None
    else:
        not_after_part = sta.loc[sta["time"]<= time]
        after_part = sta.drop(not_after_part.index)
        return not_after_part,after_part

def get_veri_from_middle_result(para_whole,middle_veri):

    nead_hmfc_methods = ["ts","bias","ets","fal_rate","hit_rate","mis_rate"]
    nead_abcd_methods = ["pc","spc"]

    #得到预报模式列表
    data_name_list = ["ob"]
    for model in para_whole["forecasts"]:
        data_name_list.append(model["name"])
    model_num = len(para_whole["forecasts"])

    veri_paras = para_whole["veri_set"]
    veri_result = {}
    group_set = para_whole["group_set"]
    for key in middle_veri.keys():
        data_array = middle_veri[key]["result"]
        shape = data_array.shape
        if len(shape) == 4:
            middle_veri_3d = np.zeros(shape[0:3])
            data_4d = data_array
            total_num = data_4d[:, :, 0,-1]
            num_0 = np.zeros(total_num.shape)
            num_0[total_num == 0] = 1
            sum_num_0 = np.sum(num_0, axis=1)
            #print(sum_num_0)

            for i in range(model_num):
                # 如果一个分类sta，它有i个模式中存在一个模式总和为0，即这些模式一直缺省
                # 则每个time的中间结果中，>i 个模式样本数为0的那个时次的结果会被全部置0
                index_has0 = np.where(sum_num_0 == i)[0]
                middle_veri_3d[index_has0,:,:] = data_4d[index_has0,:,:,i]
        else:
            middle_veri_3d = data_array


        dims = []
        coords ={}
        shape = []
        # group_set 的维度
        for coord in group_set.keys():
            if group_set[coord] != "fold":
                dims.append(coord)
                coords[coord] = group_set[coord]["group_name"]
                shape.append(len(coords[coord]))

        #模式维度
        dims.append("member")
        coords["member"] = data_name_list[1:]
        shape.append(model_num)

        #检验方法维度
        methods = veri_paras[key]["method"]
        dims.append("vmethod")
        coords["vmethod"] = methods
        shape.append(len(methods))

        #检验方法维度
        one_veri_para = veri_paras[key]
        if ("para1" in one_veri_para.keys()):
            para1 = one_veri_para["para1"]
            if (para1 is not None):
                shape.append(len(para1))
                coords["para1"] = para1
                dims.append("para1")
        if ("para2" in one_veri_para.keys()):
            para2 = one_veri_para["para2"]
            if (para1 is not None):
                shape.append(len(para2))
                coords["para2"] = para2
                dims.append("para2")

        shape = tuple(shape)
        result0 = np.zeros(shape)
        result_f = xr.DataArray(result0, coords=coords, dims=dims)
        print(middle_veri_3d)
        print(middle_veri_3d.shape)
        if methods[0] in nead_hmfc_methods:
            ngrade = len(one_veri_para["para1"])
            hit = middle_veri_3d[:,:,1:(1+ngrade)]
            mis = middle_veri_3d[:,:,(1+ngrade):(1+2 * ngrade)]
            fal = middle_veri_3d[:,:,(1+2*ngrade):(1+3 * ngrade)]
            cn = middle_veri_3d[:,:,(1+3*ngrade):(1+4 * ngrade)]
        elif  methods[0] in nead_abcd_methods:
            tn = middle_veri_3d[:,:,0]
            na = middle_veri_3d[:,:,1]
            nd = middle_veri_3d[:,:,4]

        for method in methods:
            shape_xr = result_f.loc[dict(vmethod = method)].shape
            #print(shape_xr)
            if method.lower() == "ts":
                ts = hit/(mis + fal +hit + 1e-6)
                result_f.loc[dict(vmethod = method)] = ts.reshape(shape_xr)
            elif method.lower() == "bias":
                bias = (hit + fal)/(mis + hit + 1e-6)
                result_f.loc[dict(vmethod = method)] = bias.reshape(shape_xr)
            elif method.lower() == "pc":
                pc = (na+nd)/(tn + 1e-6)
                result_f.loc[dict(vmethod = method)] = pc.reshape(shape_xr)
            else:
                pass
        #print(result_f)
        veri_result[key] = result_f
        #print()
    return veri_result

#通过指定参数获取站点信息
def get_sta_by_para(sta,para):
    sta1 = copy.deepcopy(sta)
    for key in para.keys():
        if key == "level":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_level_list(sta1,para[key])
        elif key == "time":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_time_list(sta1,para[key])
        elif key == "year":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_year_list(sta1,para[key])
        elif key == "month":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_month_list(sta1,para[key])
        elif key == "xun":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_xun_list(sta1,para[key])
        elif key == "hou":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_hou_list(sta1,para[key])
        elif key == "day":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_day_list(sta1,para[key])
        elif key == "hour":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_hour_list(sta1,para[key])
        elif key == "dtime":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dtime_list(sta1,para[key])
        elif key == "dday":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dday_list(sta1,para[key])
        elif key == "dhour":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dhour_list(sta1,para[key])
        elif key == "dminute":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dminute_list(sta1,para[key])
        elif key == "id":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_id_list(sta1,para[key])
        elif key == 'lon':
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_lon_range(sta1,para[key][0],para[key][1])
        elif key == 'lat':
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_lat_range(sta1, para[key][0], para[key][1])
        elif key == "alt":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_alt_range(sta1, para[key][0], para[key][1])
        else:
            if key in sta1.columns:
                #print(para[key])
                sta1 = sta1.loc[sta1[key].isin(para[key])]
            else:
                print("参数关键词不支持")
    return sta1

def group_sta(sta,para_group_set):
    para_dict_list_list = {}
    for key in para_group_set:
        if para_group_set[key] != "fold":
            para_dict_list_list[key] = para_group_set[key]["group"]

    para_list_dict_list = para_array_to_list(0, para_dict_list_list)
    sta_list = []
    for para_dict_list in para_list_dict_list:
        sta1 = get_sta_by_para(sta, para_dict_list)
        sta_list.append(sta1)
    return sta_list



def verification_with_complite_para(para):
    station = para["station"]
    if station is None:
        veri_on_grid(para)
    else:
        veri_on_sta(para)
def veri_on_sta(para):
    pass

def veri_on_grid(para):


    fo_start_time = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(para["fo_time_range"][0])
    fo_end_time = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(para["fo_time_range"][1])
    time_step = int(para["fo_time_range"][2][0:-1])
    time_type = para["fo_time_range"][2][-1]
    ob_grid_dict = {}
    dtime_list = para["dtime"][0:-1]
    grid_set = nmc_verification.nmc_vf_base.grid(para["grid"][0],para["grid"][1])
    masker = nmc_verification.nmc_vf_base.io.read_griddata.read_from_nc(para["masker"],grid=grid_set)

    if para["dim_type"] is not None:
        dim_type_num = len(para["dim_type"])
    else:
        dim_type_num = 0

    #设置中间检验结果
    veri_group_num = len(para["veri_set"])
    middle_veri = {}

    for i in range(veri_group_num):
        middle_veri[i] = {}
        middle_veri[i]["para"] = get_middle_veri_para(para["veri_set"][i])
        middle_veri[i]["result"] = None

    #print(middle_veri)
    fo_type_num = len(para["forecasts"])

    #print(dtime_list)
    #预执行，判断dim 和 ob文件被使用多少遍
    time1 = fo_start_time
    path_time_dict = {}
    while time1 <= fo_end_time:
        for dtime in dtime_list:
            ob_time = time1 + datetime.timedelta(hours=dtime)
            path = nmc_verification.nmc_vf_base.tool.path_tools.get_path(para["observation"]["path"], ob_time)
            if path in path_time_dict.keys():
                path_time_dict[path]["num"] += 1
            else:
                path_time_dict[path] = {}
                path_time_dict[path]["num"] = 1
                path_time_dict[path]["grd"] = None
            for i in range(dim_type_num):
                dir =  para["dim_type"][i]["path"]
                path = nmc_verification.nmc_vf_base.tool.path_tools.get_path(dir, time1,dtime)
                if path in path_time_dict.keys():
                    path_time_dict[path]["num"] += 1
                else:
                    path_time_dict[path] = {}
                    path_time_dict[path]["num"] = 1
                    path_time_dict[path]["grd"] = None

    value_s = para["observation"]["valid"][0]
    value_e = para["observation"]["valid"][1]

    # 获取group_set 中hour的集合
    if para["group_set"]["hour"] != "fold":
        list_list = para["group_set"]["hour"]["group"]
        list1 = []
        for list0 in list_list:
            list1.extend(list0)
        hour_list = list(set(list1))
    else:
        hour_list= np.arange(24).tolist()


    # 获取group_set 中hour的集合
    if para["group_set"]["month"] != "fold":
        list_list = para["group_set"]["month"]["group"]
        list1 = []
        for list0 in list_list:
            list1.extend(list0)
        month_list = list(set(list1))
    else:
        month_list= np.arange(1,13).tolist()

    #设置中间检验结果
    veri_group_num = len(para["veri_set"])
    middle_veri = {}
    for i in range(veri_group_num):
        middle_veri[i] = {}
        middle_veri[i]["para"] = get_middle_veri_para(para["veri_set"][i])
        middle_veri[i]["result"] = None

    #得到预报模式列表
    data_name_list = ["ob"]
    for model in para["forecasts"]:
        data_name_list.append(model["name"])

    time1 = fo_start_time - datetime.timedelta(hours=time_step)
    while time1 <= fo_end_time:
        if(time_type =="h"):
            time1 = time1 + datetime.timedelta(hours=time_step)
        else:
            time1 = time1 + datetime.timedelta(minutes=time_step)

        #判断时间是否在分析列表里
        if not time1.hour in hour_list:continue
        print(time1)
        for dtime in dtime_list:
            dim_grd_list = []
            all_file = True
            for i in range(dim_type_num):
                dir =  para["dim_type"][i]["path"]
                path = nmc_verification.nmc_vf_base.tool.path_tools.get_path(dir, time1,dtime)

                if path_time_dict[path]["grd"] is None:
                    grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_nc(path)
                    path_time_dict[path]["num"] -=1
                    if path_time_dict[path]["num"] >0:
                        path_time_dict[path]["grd"] = grd
                else:
                    grd = path_time_dict[path]["grd"]
                    path_time_dict[path]["num"] -= 1
                    if path_time_dict[path]["num"] ==0:
                        path_time_dict.pop(path)
                if grd is None:
                    all_file = False
                    break
                dim_grd_list.append(grd)
            if not all_file:continue
            #读取观测
            ob_time = time1 + datetime.timedelta(hours=dtime)
            path = nmc_verification.nmc_vf_base.tool.path_tools.get_path(para["observation"]["path"], ob_time)

            if path_time_dict[path]["grd"] is None:
                ob_grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_nc(path)
                path_time_dict[path]["num"] -= 1
                if path_time_dict[path]["num"] > 0:
                    path_time_dict[path]["grd"] = ob_grd
            else:
                ob_grd = path_time_dict[path]["grd"]
                path_time_dict[path]["num"] -= 1
                if path_time_dict[path]["num"] == 0:
                    path_time_dict.pop(path)
            if ob_grd is None: continue

            #读取预报
            #print(fo_type_num)
            for i in range(fo_type_num):
                one_fo_para = para["forecasts"][i]
                data_name = one_fo_para["name"]

                range_b = one_fo_para["fo_time_move_back"]
                fo_time_move_backs = np.arange(range_b[0],range_b[1],range_b[2]).tolist()
                find_file = False
                path = None
                for move_back in fo_time_move_backs:
                    time_model = time1 - datetime.timedelta(hours=move_back)
                    dtime_model_max = dtime + move_back

                    if one_fo_para["ob_time_need_be_same"]:
                        dtime_model_try = [dtime_model_max]
                    else:
                        dtime_model_try = np.arange(dtime_model_max,-1,-1).tolist()
                    for dtime_model in dtime_model_try:
                        dtime_model_int = int(dtime_model)
                        path = nmc_verification.nmc_vf_base.tool.path_tools.get_path(one_fo_para["path"], time_model,dtime_model_int)
                        if os.path.exists(path):
                            find_file = True
                            break
                    if find_file:
                        break
                fo_sta = None
                if find_file:
                    grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_nc(path)
                    if grd is None:
                        all_file = False
                        break
                else:
                    all_file = False
                    break



            #开始网格检验
            for key in middle_veri.keys():
                # 首先根据
                mpara = middle_veri[key]["para"]
                mpara["sample_must_be_same"] = para["sample_must_be_same"]
                methods = mpara["method"]
                para1 = None
                if "para1" in mpara.keys():
                    para1 = mpara["para1"]
                para2 = None
                if "para2" in mpara.keys():
                    para2 = mpara["para2"]
                for i in range(fo_type_num):
                    middle_result_part = nmc_verification.nmc_vf_product.perspective.get_middle_veri_result(grd, mpara)


    #print(middle_veri[0]["result"])
    veri_result = get_veri_from_middle_result(para,middle_veri)
    print(veri_result)
    for key in veri_result.keys():
        #保存检验结果
        veri_name = para["veri_set"][key]["name"]
        path = para["save_dir"] + "/" + veri_name + ".nc"
        result = veri_result[key]
        result.to_netcdf(path)
        save_dir = para["save_dir"] + "/" + veri_name +"/"
        plot_set = nmc_verification.nmc_vf_product.perspective.veri_plot_set(subplot=para["plot_set"]["subplot"], legend=para["plot_set"]["legend"],
                                                 axis=para["plot_set"]["axis"], save_dir=save_dir)
        plot_type = para["veri_set"][key]["plot_type"]
        if plot_type == "bar":
            plot_set.bar(result)
    return
