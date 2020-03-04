import datetime
import numpy as np
import copy
import meteva
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
    for method in methods:
        if method in nead_hmfc_methods:
            mpara["method"] = ["hmfn"]
            break
        if method in nead_abcd_methods:
            mpara["method"] = ["abcd"]
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
            sta1 = meteva.base.function.get_from_sta_data.sta_in_level_list(sta1,para[key])
        elif key == "time":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_time_list(sta1,para[key])
        elif key == "year":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_year_list(sta1,para[key])
        elif key == "month":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_month_list(sta1,para[key])
        elif key == "xun":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_xun_list(sta1,para[key])
        elif key == "hou":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_hou_list(sta1,para[key])
        elif key == "day":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_day_list(sta1,para[key])
        elif key == "hour":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_hour_list(sta1,para[key])
        elif key == "dtime":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_dtime_list(sta1,para[key])
        elif key == "dday":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_dday_list(sta1,para[key])
        elif key == "dhour":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_dhour_list(sta1,para[key])
        elif key == "dminute":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_dminute_list(sta1,para[key])
        elif key == "id":
            sta1 = meteva.base.function.get_from_sta_data.sta_in_id_list(sta1,para[key])
        elif key == 'lon':
            sta1 = meteva.base.function.get_from_sta_data.sta_between_lon_range(sta1,para[key][0],para[key][1])
        elif key == 'lat':
            sta1 = meteva.base.function.get_from_sta_data.sta_between_lat_range(sta1, para[key][0], para[key][1])
        elif key == "alt":
            sta1 = meteva.base.function.get_from_sta_data.sta_between_alt_range(sta1, para[key][0], para[key][1])
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
    #首先根据预报时效范围计算观测时效的范围,并且建立每个观测时间对应的多个起报时间和预报时效
    fo_start_time = meteva.base.tool.time_tools.str_to_time(para["fo_time_range"][0])
    fo_end_time = meteva.base.tool.time_tools.str_to_time(para["fo_time_range"][1])
    time_step = int(para["fo_time_range"][2][0:-1])
    time_type = para["fo_time_range"][2][-1]
    ob_time_dict = {}
    time1 = fo_start_time
    dtime_list = para["dtime"][0:-1]
    while time1 <= fo_end_time:
        for dh in dtime_list:
            ob_time = time1 + datetime.timedelta(hours=dh)
            if ob_time not in ob_time_dict.keys():
                ob_time_dict[ob_time] = [[time1,dh]]
            else:
                ob_time_dict[ob_time].append([time1,dh])
        time1 = time1 + datetime.timedelta(hours=time_step)

    #设置中间检验结果
    veri_group_num = len(para["veri_set"])
    middle_veri = {}
    for i in range(veri_group_num):
        middle_veri[i] = {}
        middle_veri[i]["para"] = get_middle_veri_para(para["veri_set"][i])
        middle_veri[i]["result"] = None

    #print(middle_veri)
    #读取站点信息：
    station = meteva.base.io.read_stadata.read_from_micaps3(para["station"]["path"])
    station["data0"] = 9999
    #print(station)
    time1 = fo_start_time
    ob_sta_all = None
    #print(dtime_list)
    #判断每个维度类型文件是否为固定文件
    para_dim_type = para["dim_type"]
    dim_type_num = 0
    dim_type_sta_all_dict = collections.OrderedDict()
    if para_dim_type is not None:
        dim_type_num = len(para_dim_type)
        dim_type_sta1_list = []
        for i in range(dim_type_num):
            dim_type_sta1_list.append(None)
            path = para_dim_type[i]["path"]
            fix = True
            if path.find("YY") >0:
                fix = False
            if path.find("MM") >0:
                fix = False
            if path.find("DD") >0:
                fix = False
            if path.find("HH") >0:
                fix = False
            para_dim_type[i]["fix"] = fix

        #print(para_dim_type)
        for i in range(dim_type_num):
            dim_type_sta_all_dict[i] = None

    fo_type_num = len(para["forecasts"])
    fo_sta_all_dict = collections.OrderedDict()
    for i in range(fo_type_num):
        fo_sta_all_dict[i] = None

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
        #读取dim_type
        for i in range(dim_type_num):
            sta = None
            if para_dim_type[i]["fix"]:
                if len(dim_type_sta1_list) >i:
                    path = para_dim_type[i]["path"]
                    if para_dim_type[i]["type"] =="grid_data":
                        grd = meteva.base.io.read_griddata.read_from_nc(path)
                        if grd is not None:
                            sta = meteva.base.function.gxy_sxy.interpolation_nearest(grd,station)
                    else:
                        sta = meteva.base.io.read_stadata.read_from_micaps3(path,station)
                else:
                    sta = copy.deepcopy(dim_type_sta1_list[i])
                    dim_type_sta1_list.append(sta)
            else:
                dir = para_dim_type[i]["path"]
                path =meteva.base.tool.path_tools.get_path(dir,time1)
                if para_dim_type[i]["type"] == "grid_data":
                    grd = meteva.base.io.read_griddata.read_from_nc(path)
                    sta = meteva.base.function.gxy_sxy.interpolation_nearest(grd, station)
                else:
                    sta = meteva.base.io.read_stadata.read_from_micaps3(path, station)
            for dtime in dtime_list:
                sta1 = copy.deepcopy(sta)
                meteva.base.set_time_dtime_level_name(sta1,time = time1,dtime = dtime,level=0,data_name=para_dim_type[i]["name"])
                dim_type_sta_all_dict[i] = meteva.base.function.put_into_sta_data.join(dim_type_sta_all_dict[i],sta1)

        #print(dim_type_sta_all_dict[0])
        #读取观测
        for dtime in dtime_list:
            ob_time = time1 + datetime.timedelta(hours=dtime)
            if ob_time in ob_time_dict.keys():
                path = meteva.base.tool.path_tools.get_path(para["observation"]["path"],ob_time)
                #print(path)
                ob_sta = meteva.base.io.read_stadata.read_from_micaps3(path,station=station)
                if ob_sta is not None:
                    ob_sta = meteva.base.function.get_from_sta_data.sta_between_value_range(ob_sta,value_s,value_e)
                    time_dtime_list = ob_time_dict[ob_time]
                    for time_dtime in time_dtime_list:
                        #print(time_dtime)
                        ob_sta1 = copy.deepcopy(ob_sta)
                        time_p = time_dtime[0]
                        dtime = time_dtime[1]
                        meteva.base.set_time_dtime_level_name(ob_sta1,time = time_p,dtime= dtime,level=0,data_name="ob")
                        ob_sta_all = meteva.base.function.put_into_sta_data.join(ob_sta_all,ob_sta1)
                ob_time_dict.pop(ob_time)
        #print(ob_sta_all)
        #print()
        #读取预报
        #print(fo_type_num)
        for i in range(fo_type_num):
            one_fo_para = para["forecasts"][i]
            data_name = one_fo_para["name"]
            for dtime in dtime_list:
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
                        path = meteva.base.tool.path_tools.get_path(one_fo_para["path"], time_model,dtime_model_int)
                        if os.path.exists(path):
                            find_file = True
                            break
                    if find_file:
                        break
                fo_sta = None
                if find_file:
                    if one_fo_para["type"] == "sta_data":
                        fo_sta = meteva.base.io.read_stadata.read_from_micaps3(path, station)
                    else:
                        grd = meteva.base.io.read_griddata.read_from_nc(path)
                        if grd is not None:
                            fo_sta = meteva.base.function.gxy_sxy.interpolation_nearest(grd,station)
                            fo_sta = meteva.base.function.sxy_sxy.set_data_to(fo_sta,station)
                if fo_sta is None:
                    fo_sta = copy.deepcopy(station)
                fo_sta = meteva.base.function.sxy_sxy.set_value_out_9999(fo_sta,value_s,value_e)
                meteva.base.set_time_dtime_level_name(fo_sta, level=0, time=time1, dtime=dtime,data_name=data_name)
                #meteva.base.io.write_stadata.write_to_micaps3(fo_sta,filename="G:\\a.txt")
                fo_sta_all_dict[i] = meteva.base.function.put_into_sta_data.join(fo_sta_all_dict[i],fo_sta)
                # print(fo_sta_all_dict[i])

        #提取起报时间在现在或过期的数据部分
        #print(len(ob_sta_all.index))
        merge = None
        #提取dim_type中数据
        for key in dim_type_sta_all_dict.keys():
            merge = meteva.base.function.put_into_sta_data.merge_on_all_dim(merge,dim_type_sta_all_dict[key])

        #提取观测序列的数据
        sta_before,sta_after = cut_sta_not_after(ob_sta_all,time1)
        ob_sta_all = sta_after
        if sta_before is None:
            continue
        merge = meteva.base.function.put_into_sta_data.merge_on_all_dim(merge, sta_before)
        #print(merge)
        #提取预报数据
        for key in fo_sta_all_dict.keys():
            merge = meteva.base.function.put_into_sta_data.merge_on_all_dim(merge,fo_sta_all_dict[key])
            #print(merge)
            #print()

        sta_list = group_sta(merge,para["group_set"])

        #print(sta_set.get_para_dict_list_list())
        #print(sta_list)
        for key in middle_veri.keys():
            mpara = middle_veri[key]["para"]
            mpara["sample_must_be_same"] = para["sample_must_be_same"]
            #print(mpara)
            methods = mpara["method"]
            para1 = None
            if "para1" in mpara.keys():
                para1 = mpara["para1"]
            para2 = None
            if "para2" in mpara.keys():
                para2 = mpara["para2"]
            #print(len(sta_list))
            middle_result_part = meteva.perspact.perspective.get_middle_veri_result(sta_list, mpara, data_name_list)
            #print(middle_result_part)
            middle_veri[key]["result"] = middle_veri_result_add(middle_veri[key]["result"],middle_result_part,para["sample_must_be_same"])
            #print(middle_veri[key]["result"])
            #veri_result = get_veri_from_middle_result(para,middle_veri)
            #print()

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
        plot_set = meteva.perspact.perspective.veri_plot_set(subplot=para["plot_set"]["subplot"], legend=para["plot_set"]["legend"],
                                                                            axis=para["plot_set"]["axis"], save_dir=save_dir)
        plot_type = para["veri_set"][key]["plot_type"]
        if plot_type == "bar":
            plot_set.bar(result)
    return
