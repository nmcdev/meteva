import datetime
import numpy as np
import copy
import nmc_verification
import collections
import os
import xarray as xr


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


def middle_veri_result_add(middle1,middle2):
    if middle1 is None:
        return middle2
    elif middle2 is None:
        return middle1
    else:
        middle3 = copy.deepcopy(middle1)
        middle3.values = middle1.values + middle2.values
        return middle3

def cut_sta_not_after(sta,time):
    if sta is None:
        return None,None
    else:
        not_after_part = sta.loc[sta["time"]<= time]
        after_part = sta.drop(not_after_part.index)
        return not_after_part,after_part

def get_veri_from_middle_result(root_para,middle_veri):

    veri_paras = root_para["veri_set"]
    veri_result = {}
    group_set = root_para["group_set"]
    for key in middle_veri.keys():
        para_m = middle_veri[key]["para"]
        result_m = middle_veri[key]["result"]
        para_f = veri_paras[key]
        coords_m = list(result_m.coords)
        #print(coords_m)
        dims = []
        coords ={}
        shape = []
        for coord in coords_m:
            if coord.find("vmethod") !=0:
                dims.append(coord)
                if coord in group_set.keys():
                    coords[coord] = group_set[coord]["group_name"]
                else:
                    coords[coord] = result_m.coords[coord]
                shape.append(len(result_m.coords[coord]))
            else:
                dims.append(coord)
                coords[coord] = para_f["method"]
                shape.append(len(para_f["method"]))
        shape = tuple(shape)
        result0 = np.zeros(shape)
        result_f = xr.DataArray(result0, coords=coords, dims=dims)
        methods = para_f["method"]
        for method in methods:
            if method.lower() == "ts":
                hit = result_m.sel(vmethod = "hit").values
                mis = result_m.sel(vmethod="mis").values
                fal = result_m.sel(vmethod="fal").values
                cn = result_m.sel(vmethod = "cn").values
                ts = hit/(mis + fal +hit + 1e-6)
                result_f.loc[dict(vmethod = method)] = ts
            elif method.lower() == "bias":
                hit = result_m.sel(vmethod = "hit").values
                mis = result_m.sel(vmethod="mis").values
                fal = result_m.sel(vmethod="fal").values
                cn = result_m.sel(vmethod = "cn").values
                bias = (hit + fal)/(mis + hit + 1e-6)
                result_f.loc[dict(vmethod = method)] = bias
            elif method.lower() == "pc":
                na = result_m.sel(vmethod = "na").values
                nb = result_m.sel(vmethod="nb").values
                nc = result_m.sel(vmethod="nc").values
                nd = result_m.sel(vmethod = "nd").values
                pc = (na+nd)/(na+nb+nc+nd)
                result_f.loc[dict(vmethod = method)] = pc
            else:
                pass
        #print(result_f)
        veri_result[key] = result_f

        #print()


    return veri_result

def group_sta(sta,para):
    sta_set = nmc_verification.nmc_vf_product.perspective.sta_data_set(sta)
    if para["dtime"] != "fold":
        sta_set.set_dtime_unfold(dtime_list_list=para["dtime"]["group"])

    for key in para.keys():
        if key.find("dim_type") == 0:
            sta_set.set_dim_type_unfold(key,para[key]["group"])
    return sta_set

def verification_with_complite_para(para):

    veri_group_num = len(para["veri_set"])
    middle_veri = {}
    for i in range(veri_group_num):
        middle_veri[i] = {}
        middle_veri[i]["para"] = get_middle_veri_para(para["veri_set"][i])
        middle_veri[i]["result"] = None

    #print(middle_veri)
    #读取站点信息：
    station = nmc_verification.nmc_vf_base.io.read_stadata.read_from_micaps3(para["station"]["path"])
    #print(station)
    time0 = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(para["time_range"][0])
    end_time = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(para["time_range"][1])
    #print(time0)
    #print(end_time)
    #print(para["time_range"][2])
    #print(para["time_range"][2][-1])
    time_type = para["time_range"][2][-1]
    time_step = int(para["time_range"][2][0:-1])

    time1 = time0
    dtime_list = para["dtime"][0:-1]
    ob_sta_all = None
    #print(dtime_list)
    #判断每个维度类型文件是否为固定文件
    para_dim_type = para["dim_type"]
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
    dim_type_sta_all_dict = collections.OrderedDict()
    for i in range(dim_type_num):
        dim_type_sta_all_dict[i] = None

    fo_type_num = len(para["forecasts"])
    fo_sta_all_dict = collections.OrderedDict()
    for i in range(fo_type_num):
        fo_sta_all_dict[i] = None


    while time1 < end_time:
        #读取dim_type
        for i in range(dim_type_num):
            sta = None
            if para_dim_type[i]["fix"]:
                if len(dim_type_sta1_list) >i:
                    path = para_dim_type[i]["path"]
                    if para_dim_type[i]["type"] =="grid_data":
                        grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_nc(path)
                        if grd is not None:
                            sta = nmc_verification.nmc_vf_base.function.gxy_sxy.interpolation_nearest(grd,station)
                    else:
                        sta = nmc_verification.nmc_vf_base.io.read_stadata.read_from_micaps3(path,station)
                else:
                    sta = copy.deepcopy(dim_type_sta1_list[i])
                    dim_type_sta1_list.append(sta)
            else:
                dir = para_dim_type[i]["path"]
                path =nmc_verification.nmc_vf_base.tool.path_tools.get_path(dir,time1)
                if para_dim_type[i]["type"] == "grid_data":
                    grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_nc(path)
                    sta = nmc_verification.nmc_vf_base.function.gxy_sxy.interpolation_nearest(grd, station)
                else:
                    sta = nmc_verification.nmc_vf_base.io.read_stadata.read_from_micaps3(path, station)
            for dtime in dtime_list:
                sta1 = copy.deepcopy(sta)
                nmc_verification.nmc_vf_base.set_time_dtime_level_name(sta1,time = time1,dtime = dtime,level=0,data_name=para_dim_type[i]["name"])
                dim_type_sta_all_dict[i] = nmc_verification.nmc_vf_base.function.put_into_sta_data.join(dim_type_sta_all_dict[i],sta1)

        #print(dim_type_sta_all_dict[0])

        #读取观测
        path = nmc_verification.nmc_vf_base.tool.path_tools.get_path(para["observation"]["path"],time1)
        #print(path)
        ob_sta = nmc_verification.nmc_vf_base.io.read_stadata.read_from_micaps3(path,station=station,time = time1,dtime=[0,time_type],level=0,data_name="ob")

        if ob_sta is not None:
            ob_sta= nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_value_range(ob_sta, para["observation"]["valid"][0],
                                                                           para["observation"]["valid"][1])
            for dtime in dtime_list:
                ob_sta1 = copy.deepcopy(ob_sta)
                time_p = time1 - datetime.timedelta(hours=dtime)
                nmc_verification.nmc_vf_base.set_time_dtime_level_name(ob_sta1,time = time_p,dtime= dtime)
                ob_sta_all = nmc_verification.nmc_vf_base.function.put_into_sta_data.join(ob_sta_all,ob_sta1)

        #print(ob_sta_all)
        #print()
        #读取预报
        #print(fo_type_num)
        for i in range(fo_type_num):
            one_fo_para = para["forecasts"][i]
            dtime_read = one_fo_para["dtime_read"][0:-1]
            data_name = one_fo_para["name"]
            for dtime in dtime_read:
                path = nmc_verification.nmc_vf_base.tool.path_tools.get_path(one_fo_para["path"],time1,dtime)
                if os.path.exists(path):
                    if one_fo_para["type"] == "sta_data":
                        sta = nmc_verification.nmc_vf_base.io.read_stadata.read_from_micaps3(path, station,level=0,time = time1,dtime = [dtime,time_type],data_name=data_name)
                        if sta is not None:
                            sta = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_value_range(sta,one_fo_para["valid"][0],one_fo_para["valid"][1])
                    else:
                        grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_nc(path)
                        if grd is not None:
                            sta = nmc_verification.nmc_vf_base.function.gxy_sxy.interpolation_nearest(grd,station)
                            nmc_verification.nmc_vf_base.set_time_dtime_level_name(sta,level=0,time = time1,dtime = dtime,data_name = data_name)
                    if sta is not None:
                        if one_fo_para["copy"] is None:
                            fo_sta_all_dict[i] = nmc_verification.nmc_vf_base.function.put_into_sta_data.join(fo_sta_all_dict[i],sta)
                            #print(fo_sta_all_dict)
                        else:
                            for m in range(len(one_fo_para["copy"]["结束时刻向未来移动"])):
                                if one_fo_para["copy"]["预报时效增加"]:
                                    dtime_veri = dtime + one_fo_para["copy"]["预报时效增加"][m]
                                    time_mv = one_fo_para["copy"]["结束时刻向未来移动"][m]
                                    time_ob = time1 + datetime.timedelta(hours = dtime + time_mv)
                                    time_fo_veri = time_ob - datetime.timedelta(hours=dtime_veri)
                                else:
                                    dtime_veri = one_fo_para["copy"]["预报时效改变为"][m]
                                    time_mv = one_fo_para["copy"]["结束时刻向未来移动"][m]
                                    time_ob = time1 + datetime.timedelta(hours=dtime + time_mv)
                                    time_fo_veri = time_ob - datetime.timedelta(hours=dtime_veri)
                                sta1 = copy.deepcopy(sta)
                                nmc_verification.nmc_vf_base.set_time_dtime_level_name(sta1,time = time_fo_veri,dtime = dtime_veri)
                                fo_sta_all_dict[i]=nmc_verification.nmc_vf_base.function.put_into_sta_data.join(fo_sta_all_dict[i],sta1)
                                #print(fo_sta_all_dict[i])
                                #print()


        time_already = time1 - datetime.timedelta(hours=dtime_list[-1])
        #print(time_already)

        print(time1)
        if(time_type =="h"):
            time1 = time1 + datetime.timedelta(hours=time_step)
        else:
            time1 = time1 + datetime.timedelta(minutes=time_step)

        if time1 >= end_time or  len(ob_sta_all.index) > 300000 :
            #提取起报时间在现在或过期的数据部分
            #print(len(ob_sta_all.index))
            merge = None
            #提取dim_type中数据
            for key in dim_type_sta_all_dict.keys():
                sta_before, sta_after = cut_sta_not_after(dim_type_sta_all_dict[key],time_already)
                dim_type_sta_all_dict[key] = sta_after
                #print(sta_before)
                #print(dim_type_sta_all_dict[key])
                merge = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(merge,sta_before)

            #提取观测序列的数据
            all_has = True
            sta_before,sta_after = cut_sta_not_after(ob_sta_all,time_already)
            ob_sta_all = sta_after
            if sta_before is None:
                all_has = False
            #print(sta_before)
            #print(ob_sta_all)
            #print(dim_type_sta_all_dict[0])
            merge = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(merge, sta_before)

            #提取预报数据

            for key in fo_sta_all_dict.keys():
                sta_before,sta_after = cut_sta_not_after(fo_sta_all_dict[key],time_already)
                #print(sta_before)
                if sta_after is None:
                    all_has = False
                    break
                fo_sta_all_dict[key] = sta_after
                #print(fo_sta_all_dict[key])
                merge = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(merge,sta_before)
            #print(merge)
            if all_has:
                sta_set = group_sta(merge,para["group_set"])
                #print(sta_set.get_para_dict_list_list())
                for key in middle_veri.keys():
                    mpara = middle_veri[key]["para"]
                    #print(mpara)
                    methods = mpara["method"]
                    para1 = None
                    if "para1" in mpara.keys():
                        para1 = mpara["para1"]
                    para2 = None
                    if "para2" in mpara.keys():
                        para2 = mpara["para2"]
                    ver_set = nmc_verification.nmc_vf_product.perspective.veri_result_set(vmethod_list=mpara["method"],para1 = para1,para2= para2,sta_data_set=sta_set)
                    middle_result_part = nmc_verification.nmc_vf_product.perspective.get_middle_veri_result(sta_set,mpara)
                    middle_veri[key]["result"] = middle_veri_result_add(middle_veri[key]["result"],middle_result_part)
                    #print(middle_veri[key]["result"])
                #veri_result = get_veri_from_middle_result(para,middle_veri)
                #print()



    veri_result = get_veri_from_middle_result(para,middle_veri)

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

