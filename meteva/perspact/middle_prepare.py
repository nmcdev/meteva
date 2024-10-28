import meteva
import numpy as np
import datetime
import copy
import time
import pandas as pd
import os
import math

method_coluns_dict = {
    "hfmc_of_sun_rain":["Hsr","Fsr","Msr","Csr"],
    "hfmc" :  ["H","F","M","C"],
    "hfmc_multi": ["H", "F", "M", "C"],
    "tase":["T", "E", "A", "S"],
    "tase_angle": ["T", "E_angle", "A_angle", "S_angle"],
    "tase_angle_uv": ["T", "E_angle", "A_angle", "S_angle"],
    "tasem":["T", "E", "A", "S","M"],
    "tc_count":["T", "C"],
    "tlfo":["T","LFO"],
    "toar":["T","OAR"],
    "tmmsss": ["T", "MX","MY","SX","SY","SXY"],
    "tbask":["T","BASK"],
    "nasws_uv": ["T", "ACS", "SCORE", "SEVERER", "WEAK"],
    "nas_uv": ["T", "ACS", "SCORE"],
    "na_uv":["T","ACZ","ACD","ACS"],
    "nasws_s": ["T", "ACS", "SPEEDSCORE", "SEVERER", "WEAK"],
    "na_s":["T","ACS"],
    "fss":["pob","pfo","fbs"],
    "tems":["T","E","MX","SX"],
    "cscs":["CX","SX","CY","SY"],
    "hnh": np.arange(20).tolist()

}

def get_score_method_with_mid(method):
    hfmc_list = [
        meteva.method.ts,meteva.method.bias,meteva.method.ets,meteva.method.mr,meteva.method.far,
        meteva.method.r,meteva.method.hss_yesorno,meteva.method.pofd,meteva.method.pod,
        meteva.method.dts,meteva.method.orss,meteva.method.pc,meteva.method.roc,meteva.method.sr,
        meteva.method.hk_yesorno,meteva.method.odds_ratio,meteva.method.ob_fo_hr,meteva.method.ob_fo_hc,
        meteva.method.false_alarm_count
    ]
    hfmc_multi_list = [
        meteva.method.ts_multi,meteva.method.bias_multi,meteva.method.ets_multi,meteva.method.mr_multi,meteva.method.far_multi,
        meteva.method.pofd_multi,meteva.method.pod_multi,meteva.method.sr_multi]

    hfmc_of_sum_rain_list = [meteva.method.pc_of_sun_rain]
    tase_list = [meteva.method.me, meteva.method.mae, meteva.method.mse, meteva.method.rmse]
    tase_angle_list = [meteva.method.me_angle, meteva.method.mae_angle, meteva.method.rmse_angle]
    tasem_list = [meteva.method.ob_fo_mean]
    tc_list = [meteva.method.correct_rate,meteva.method.wrong_rate]
    tmmsss_list = [meteva.method.residual_error, meteva.method.residual_error_rate,meteva.method.corr,
                    meteva.method.nse,meteva.method.ob_fo_mean,meteva.method.ob_fo_sum,meteva.method.ob_fo_std]
    tbask_list = [meteva.product.regulation.temperature.temp_forecaster_score]
    nasws_s_list = [meteva.method.acs, meteva.method.scs, meteva.method.wind_weaker_rate,
                     meteva.method.wind_severer_rate]
    nasws_uv_list = [meteva.method.acs_uv,meteva.method.scs_uv,meteva.method.wind_weaker_rate_uv,meteva.method.wind_severer_rate_uv]
    nas_uv_list = [meteva.method.acd_uv,meteva.method.scd_uv]
    na_uv_list = [meteva.method.acz_uv,meteva.method.acd_uv,meteva.method.acs_uv]
    toar_list = [meteva.method.mre]
    tlfo_list = [meteva.method.rmsf]
    fss_list = [meteva.method.fss]
    tems_list = [meteva.method.bs,meteva.method.bss]
    hnh_list = [meteva.method.roc_auc]
    cscs_list = [meteva.method.ob_fo_precipitation_strength]

    method_mid = []
    method_name = method.__name__

    if method in hfmc_of_sum_rain_list:
        method_mid.append(getattr(meteva.method, method_name + "_hfmc"))
    if method in hfmc_list:
        method_mid.append(getattr(meteva.method, method_name +"_hfmc"))
    if method in hfmc_multi_list:
        method_mid.append(getattr(meteva.method, method_name[:-6] +"_hfmc"))
    if method in tase_list:
        method_mid.append(getattr(meteva.method, method_name + "_tase"))
    if method in tase_angle_list:
        method_name1 = method_name.split("_")[0]
        method_mid.append(getattr(meteva.method, method_name1 + "_tase"))
    if method in tc_list:
        method_mid.append(getattr(meteva.method, method_name + "_tc"))
    if method in tmmsss_list:
        method_mid.append(getattr(meteva.method, method_name + "_tmmsss"))
    if method in toar_list:
        method_mid.append(getattr(meteva.method, method_name + "_toar"))
    if method in tlfo_list:
        method_mid.append(getattr(meteva.method, method_name + "_tlfo"))
    if method in tbask_list:
        method_mid.append(getattr(meteva.product, method_name + "_tbask"))
    if method in nasws_s_list:
        method_mid.append(getattr(meteva.method, method_name + "_nasws"))
    if method in tems_list:
        method_mid.append(getattr(meteva.method, method_name + "_tems"))
    if method in nasws_uv_list:
        method_name1 = method_name.replace("_uv","_nasws")
        method_mid.append(getattr(meteva.method, method_name1))
    if method in nas_uv_list:
        method_name1 = method_name.replace("_uv","_nas")
        method_mid.append(getattr(meteva.method, method_name1))
    if method in na_uv_list:
        method_name1 = method_name.replace("_uv","_na")
        method_mid.append(getattr(meteva.method, method_name1))
    if method in fss_list:
        method_mid.append(getattr(meteva.method, method_name + "_fof"))
    if method in hnh_list:
        method_mid.append(getattr(meteva.method, method_name + "_hnh"))
    if method in cscs_list:
        method_mid.append(getattr(meteva.method, method_name + "_cscs"))
    if method in tasem_list:
        method_mid.append(getattr(meteva.method,method_name+"_tasem"))
    #print(method_mid)
    return method_mid

def get_middle_method(method):
    hfmc_list = [
        meteva.method.ts,meteva.method.bias,meteva.method.ets,meteva.method.mr,meteva.method.far,
        meteva.method.r,meteva.method.hss_yesorno,meteva.method.pofd,meteva.method.pod,
        meteva.method.dts,meteva.method.orss,meteva.method.pc,meteva.method.roc,meteva.method.sr,
        meteva.method.hk_yesorno,meteva.method.odds_ratio,meteva.method.ob_fo_hr,meteva.method.ob_fo_hc,
        meteva.method.false_alarm_count
    ]
    hfmc_multi_list = [
        meteva.method.ts_multi,meteva.method.bias_multi,meteva.method.ets_multi,meteva.method.mr_multi,meteva.method.far_multi,
        meteva.method.pofd_multi,meteva.method.pod_multi,meteva.method.sr_multi]

    hfmc_of_sum_rain_list = [meteva.method.pc_of_sun_rain]
    tase_list = [meteva.method.me, meteva.method.mae, meteva.method.mse, meteva.method.rmse]
    tase_angle_list = [meteva.method.me_angle, meteva.method.mae_angle, meteva.method.rmse_angle]
    tasem_list = [meteva.method.ob_fo_mean]
    tc_list = [meteva.method.correct_rate,meteva.method.wrong_rate]
    tmmsss_list = [meteva.method.residual_error, meteva.method.residual_error_rate,meteva.method.corr,meteva.method.ob_fo_sum,meteva.method.ob_fo_mean,
                   meteva.method.nse,meteva.method.ob_fo_std]
    toar_list = [meteva.method.mre]
    tlfo_list = [meteva.method.rmsf]
    tbask_list = [meteva.product.regulation.temperature.temp_forecaster_score]
    nasws_s_list = [meteva.method.acs,meteva.method.scs,meteva.method.wind_weaker_rate,meteva.method.wind_severer_rate]
    nasws_uv_list = [meteva.method.acs_uv,meteva.method.scs_uv,meteva.method.wind_weaker_rate_uv,meteva.method.wind_severer_rate_uv]
    nas_uv_list = [meteva.method.acd_uv,meteva.method.scd_uv]
    na_uv_list = [meteva.method.acz_uv,meteva.method.acs_uv,meteva.method.acd_uv]
    fss_list = [meteva.method.fss]
    tems_list = [meteva.method.bs, meteva.method.bss]
    hnh_list = [meteva.method.roc_auc]
    cscs_list = [meteva.method.ob_fo_precipitation_strength]
    method_mid = []

    if method in hfmc_of_sum_rain_list:
        method_mid.append(meteva.method.hfmc_of_sun_rain)
    if method in hfmc_list:
        method_mid.append(meteva.method.hfmc)
    if method in hfmc_multi_list:
        method_mid.append(meteva.method.hfmc_multi)
    if method in tase_list:
        method_mid.append(meteva.method.tase)
    if method in tase_angle_list:
        method_mid.append(meteva.method.tase_angle)
    if method in tc_list:
        method_mid.append(meteva.method.tc_count)
    if method in tmmsss_list:
        method_mid.append(meteva.method.tmmsss)
    if method in toar_list:
        method_mid.append(meteva.method.toar)
    if method in tlfo_list:
        method_mid.append(meteva.method.tlfo)
    if method in tbask_list:
        method_mid.append(meteva.product.regulation.temperature.tbask)
    if method in nasws_s_list:
        method_mid.append(meteva.method.nasws_s)
    if method in nasws_uv_list:
        method_mid.append(meteva.method.nasws_uv)
    if method in nas_uv_list:
        method_mid.append(meteva.method.nas_uv)
    if method in na_uv_list:
        method_mid.append(meteva.method.na_uv)
    if method in fss_list:
        method_mid.append(meteva.method.fss)
    if method in tems_list:
        method_mid.append(meteva.method.tems)
    if method in hnh_list:
        method_mid.append(meteva.method.hnh)
    if method in cscs_list:
        method_mid.append(meteva.method.cscs)
    if method in tasem_list:
        method_mid.append(meteva.method.tasem)
    return method_mid

def get_middle_columns(method):

    method_name = method.__name__
    if method_name in method_coluns_dict.keys():
        return method_coluns_dict[method_name]
    else:
        print("暂无支持")
        pass

def middle_df_sta(sta_all,method,grade_list = None,compare = None,gid = None):
    '''

    :param sta_all:
    :param method:
    :param grade_list:
    :param compare:
    :param gid:
    :return:
    '''

    need_g = False
    if gid is not None:
        need_g = True

    mid_columns = get_middle_columns(method)
    method_args = {}
    if grade_list is not None:
        method_args["grade_list"] = grade_list
    if compare is not None:
        method_args["compare"] = compare
    grade_exp = None
    names_exp = None
    group_name = None
    if need_g:
        #may be some id in gid is not in sta_all,valid group is not same as group in grid
        sta_all_id = copy.deepcopy(sta_all[["id"]])
        sta_all_id.drop_duplicates()
        sta = meteva.base.combine_on_id(gid,sta_all_id,how="inner")
        gid = sta
        group_name = gid.columns[1]
        groups = gid[group_name]
        groups = groups.drop_duplicates(keep = "first")
        names = groups.values
        gll = []
        for i in range(len(names)):
            ids = gid.loc[gid[group_name] == names[i]].values[:, 0]
            gll.append(ids.tolist())

        method_args["g"] = "id"
        method_args["gll"] = gll
        if grade_list is not None:
            if method == meteva.method.hfmc_multi:
                grade_list_name = ["<" + str(grade_list[0])]
                ng = len(grade_list)
                for kk in range(ng - 1):
                    grade_list_name.append("[" + str(grade_list[kk]) + "," + str(grade_list[kk + 1]) + ")")
                grade_list_name.append(">" + str(grade_list[ng - 1]))
                grade_exp, names_exp = np.meshgrid(grade_list, names)
            else:
                grade_exp, names_exp = np.meshgrid(grade_list, names)
            grade_exp = grade_exp.flatten().tolist()
            names_exp = names_exp.flatten().tolist()
        else:
            names_exp = names

        #sta_all_gid = meteva.base.combine_expand(sta_all,gid)
    else:
        #sta_all_gid = sta_all
        if grade_list is not None:
            if method == meteva.method.hfmc_multi:
                grade_list_name = ["<" + str(grade_list[0])]
                ng = len(grade_list)
                for kk in range(ng- 1):
                    grade_list_name.append("[" + str(grade_list[kk]) + "," + str(grade_list[kk + 1]) + ")")
                grade_list_name.append(">" + str(grade_list[ng-1]))
                grade_exp = grade_list_name
            else:
                grade_exp = grade_list
        else:
            pass

    sta_list = meteva.base.split(sta_all,used_coords=["level","time","dtime"])
    df_list = []
    for k in range(len(sta_list)):
        sta = sta_list[k]

        not_all_iv = [True]
        if method.__name__.find("_uv") >= 0 or method.__name__.find("distance") >= 0:
            col_step = 2
            valid_index = [0, 1]
        else:
            col_step = 1
            valid_index = [0]

        len_ = len(sta.columns)
        for nv in range(6 + col_step, len_, col_step):
            not_all_iv1 = np.any(sta.iloc[:, nv].values != meteva.base.IV)
            not_all_iv.append(not_all_iv1)
            if not_all_iv1:
                valid_index.append(nv - 6)
                if col_step == 2: valid_index.append(nv - 5)

        sta = meteva.base.in_member_list(sta, member_list=valid_index, name_or_index="index")
        sta1 = meteva.base.not_IV(sta)
        if len(sta1.index)==0:continue
        data_names = meteva.base.get_stadata_names(sta1)
        member_count =int(len(data_names)/col_step)
        if method.__name__=="tbask":
            mid_array, _ = meteva.product.score(sta1, method)
            dict1 = {"time": sta["time"].values[0], "dtime": sta["dtime"].values[0],"T":mid_array[0],"BASK":mid_array[1]}
            tbask_df = pd.DataFrame(dict1,index = [k])
            df_list.append(tbask_df)
        elif method.__name__ =="hnh":
            for m in range(1, member_count):
                sta2 = meteva.base.sele_by_para(sta1, member=[data_names[0], data_names[m]])
                data_name  = data_names[m]
                mid_array, _ = meteva.product.score(sta2, method)
                mid_array1 = mid_array.flatten()
                #print(mid_array)
                dict1 = {"time": sta["time"].values[0], "dtime": sta["dtime"].values[0],"member":data_name}
                for i in range(20):
                    dict1[i] = mid_array1[i]
                hnh_df = pd.DataFrame(dict1, index=[k])
                #print(hnh_df)
                df_list.append(hnh_df)

        else:
            for m in range(1, member_count):
                if col_step==1:
                    sta2 = meteva.base.sele_by_para(sta1, member=[data_names[0], data_names[m]])
                    data_name  = data_names[m]
                else:
                    sta2 = meteva.base.sele_by_para(sta1, member=[data_names[0],data_names[1], data_names[m*2],data_names[m*2+1]])
                    data_name = data_names[m*2]
                    data_name = data_name[data_name.find("_")+1:]
                mid_array, gll_valid = meteva.product.score(sta2, method,**method_args,drop_g_column=True)
                if mid_array is None: continue

                index_names = ["time","dtime","member"]
                dict1 = {"time":sta2["time"].values[0],"dtime":  sta2["dtime"].values[0],"member":data_name}
                if names_exp is not None:
                    index_names.append(group_name)
                    dict1[group_name] = names_exp
                if grade_exp is not None:
                    index_names.append("grade")
                    dict1["grade"] = grade_exp

                if method == meteva.method.tc_count:
                    if grade_list is None:
                        dat1 = mid_array[..., 0]
                    else:
                        dat1 = np.repeat([mid_array[..., 0]],len(grade_list))
                    dict1[mid_columns[0]] = dat1.flatten()
                    dict1[mid_columns[1]] = mid_array[..., 1:].flatten()
                else:
                    for c in range(len(mid_columns)):
                        dict1[mid_columns[c]] = mid_array[...,c].flatten()
                try:
                    hfmc_df = pd.DataFrame(dict1)
                    df_list.append(hfmc_df)
                except:
                    ob_time = meteva.base.all_type_time_to_datetime(sta2["time"].values[0]) + datetime.timedelta(hours=int(sta2["dtime"].values[0]))
                    time_str = meteva.base.all_type_time_to_str(sta2["time"].values[0])
                    time_str_ob = meteva.base.all_type_time_to_str(ob_time)
                    print(data_names[m] + "的" + time_str+"起报的"+str(sta2["dtime"].values[0])+"时效预报的空间范围不完整,对应的实况时间为："+time_str_ob)
    df_all = pd.concat(df_list, axis=0)
    return df_all


def tran_middle_df_to_ds(df_all,mid_columns = None):
    '''

    :param df_all:
    :param mid_columns: 中间数据对应的列名称，列表形式
    :return:
    '''
    print("该函数有bug，在相邻格点取值完全相同时，会产生nan")
    all_columns = df_all.columns
    if mid_columns is None:

        list_list = method_coluns_dict.values()
        for list1 in list_list:
            eq = True
            for c in range(1,len(list1)+1):
                if all_columns[-c] != list1[-c]:
                    eq = False
            if eq:
                mid_columns = list1
                break

    index_columns = []
    for name in all_columns:
        if name not in mid_columns:
            index_columns.append(name)
    index = []
    for i in range(len(index_columns)):
        index.append(df_all[index_columns[i]].values)
    df_new = pd.DataFrame(df_all[mid_columns].values, index=index, columns=mid_columns)
    df_new.index.names = index_columns
    df_new.drop_duplicates(subset=None, keep='first', inplace=True)
    mid_xr = df_new.to_xarray()
    return mid_xr

def tran_middle_ds_to_df(ds_all):

    values = list(ds_all.data_vars)
    df1 = ds_all[values[0]].to_dataframe()
    df1 = df1.reset_index()
    for i in range(1,len(values)):
        df2 = ds_all[values[i]].to_dataframe()
        df2 = df2.reset_index()
        df1 = pd.merge(df1,df2)
    df_all = df1.dropna()
    return df_all

def middle_ds_sta(sta_all,method,grade_list = None,compare = None,gid = None):
    '''

    :param sta_all:
    :param method:
    :param grade_list:
    :param compare:
    :param gid:
    :return:
    '''
    mid_columns = get_middle_columns(method)
    df_all = middle_df_sta(sta_all,method,grade_list,compare = compare,gid = gid)
    ds_all = tran_middle_df_to_ds(df_all,mid_columns)
    return ds_all


def middle_df_grd(grd_ob, grd_fo, method, grade_list=None, compare=None, marker=None, marker_name=None):
    mid_columns = get_middle_columns(method)
    level_fo = grd_fo["level"].values[0]
    time_fo = grd_fo["time"].values[0]
    dtime = grd_fo["dtime"].values[0]
    fo_name = grd_fo["member"].values[0]

    lats = grd_ob["lat"].values
    lons = grd_ob["lon"].values
    xx,yy = np.meshgrid(lons,lats)
    weight = np.cos(yy*math.pi / 180)
    grid0 = meteva.base.get_grid_of_data(grd_ob)
    grid_fo = meteva.base.get_grid_of_data(grd_fo)
    if grid0.slon != grid_fo.slon or grid0.slat != grid_fo.slat or grid0.dlon != grid_fo.dlon or grid0.dlat != grid_fo.dlat or grid0.nlon != grid_fo.nlon or grid0.nlat != grid_fo.nlat:
        print("the grid of grd_ob is :")
        print("lon:" + str(grid0.glon))
        print("lat:" + str(grid0.glat))
        print("the grid of grd_fo is :")
        print("lon:" + str(grid_fo.glon))
        print("lat:" + str(grid_fo.glat))
        print("the grid of grd_ob is different from the grid of  grd_fo")
        return None

    grid0_ = meteva.base.grid(grid0.glon,grid0.glat)
    grd_weight = meteva.base.grid_data(grid0_,weight)
    #meteva.base.pcolormesh_2d_grid(grd_weight,save_path="a.png")
    if method.__name__.find("_uv") >= 0:
        fo_name = fo_name[2:]

    method_args = {}
    if grade_list is not None:
        method_args["grade_list"] = grade_list

    if compare is not None:
        method_args["compare"] = compare
    if marker is None:

        ob = grd_ob.values
        fo = grd_fo.values

        if method.__name__.find("_uv")>=0:
            mid_array = method(ob[0,...],fo[0,...], ob[1,...],fo[1,...], **method_args)
        else:
            mid_array = method(ob, fo, **method_args)
            if method.__name__ == "hnh":
                mid_array = mid_array.flatten()
        index_names = ["level","time", "dtime", "member"]
        dict1 = {"level":level_fo,"time": time_fo, "dtime": dtime, "member": fo_name}


        if grade_list is not None:
            index_names.append("grade")
            dict1["grade"] = grade_list

        if method == meteva.method.tc_count:
            if grade_list is None:
                dat1 = mid_array[..., 0]
            else:
                dat1 = np.repeat([mid_array[..., 0]], len(grade_list))
            dict1[mid_columns[0]] = dat1.flatten()
            dict1[mid_columns[1]] = mid_array[..., 1:].flatten()
        else:
            for c in range(len(mid_columns)):
                dict1[mid_columns[c]] = mid_array[..., c].flatten()

        mid_df = pd.DataFrame(dict1)
        return mid_df

    else:
        if method.__name__ == "tase":
            total_count = grd_weight.values.flatten()
            error = ((grd_fo.values - grd_ob.values) * grd_weight.values).flatten()
            abs_error = (np.abs(grd_ob.values - grd_fo.values) * grd_weight.values).flatten()
            squere_error = (np.square(grd_ob.values - grd_fo.values) * grd_weight.values).flatten()
            mean_obs = (grd_ob.values* grd_weight.values).flatten()
            df = pd.DataFrame( {"T":total_count,"E":error,"A":abs_error,"S":squere_error,"M":mean_obs,"id":marker.values.flatten()})
            df.dropna(inplace=True)
            # 使用 agg 方法进行聚合计算
            result_df = df.groupby('id').agg({
                'T': 'sum',  # 权重和
                'E': 'sum',  # 误差权重和
                'A': "sum",  # 绝对误差权重和
                "S": "sum",  # 误差平方权重和
                "M":"sum"    #观测平均
            }).reset_index()

            # 重命名列以匹配您的期望输出
            result_df.columns = ['id', 'T', 'E', 'A', 'S', 'M']
            result_df.insert(0,"level",level_fo)
            result_df.insert(1, "time", time_fo)
            result_df.insert(2, "dtime", dtime)
            result_df.insert(3, "member", fo_name)
            return result_df
        else:
            df_list = []
            mark_set = list(set(marker.values.flatten().tolist()))
            mark_name = marker["member"].values[0]
            marker_name_dict = {}
            if marker_name is None:
                for mark in mark_set:
                    marker_name_dict[mark] = mark
            else:
                for i in range(len(marker_name.index)):
                    marker_name_dict[marker_name.iloc[i, 0]] = marker_name.iloc[i, 1]

            for mark in mark_set:
                if method.__name__.find("_uv") >= 0:
                    index = np.where(marker.values[0, ...] == mark)
                    u_ob = grd_ob.values[0, ...]
                    u_ob = u_ob[index]
                    v_ob = grd_ob.values[1, ...]
                    v_ob = v_ob[index]
                    u_fo = grd_fo.values[0, ...]
                    u_fo = u_fo[index]
                    v_fo = grd_fo.values[1, ...]
                    v_fo = v_fo[index]
                    mid_array = method(u_ob, u_fo, v_ob, v_fo, **method_args)
                else:
                    index = np.where(marker.values == mark)
                    ob = grd_ob.values[index]
                    fo = grd_fo.values[index]
                    if method.__name__ in ["tase", "tmmsss"]:
                        # 目前暂时只支持tase和tmmsss相关的指标的带权重
                        w = grd_weight.values[index]
                        method_args["weight"] = w
                    mid_array = method(ob, fo, **method_args)
                    if method.__name__ == "hnh":
                        mid_array = mid_array.flatten()

                index_names = ["level", "time", "dtime", "member"]
                dict1 = {"level": level_fo, "time": time_fo, "dtime": dtime, "member": fo_name}
                if mark in marker_name_dict.keys():
                    dict1[mark_name] = marker_name_dict[mark]
                else:
                    dict1[mark_name] = "other"

                if grade_list is not None:
                    index_names.append("grade")
                    dict1["grade"] = grade_list

                if method == meteva.method.tc_count:
                    if grade_list is None:
                        dat1 = mid_array[..., 0]
                    else:
                        dat1 = np.repeat([mid_array[..., 0]], len(grade_list))
                    dict1[mid_columns[0]] = dat1.flatten()
                    dict1[mid_columns[1]] = mid_array[..., 1:].flatten()
                else:
                    for c in range(len(mid_columns)):
                        dict1[mid_columns[c]] = mid_array[..., c].flatten()

                mid_df = pd.DataFrame(dict1)
                df_list.append(mid_df)
        df_all = pd.concat(df_list, axis=0)
        return df_all


def middle_ds_grd(grd_ob, grd_fo, method, grade_list=None, compare=None, marker=None, marker_name=None):
    '''

    :param sta_all:
    :param method:
    :param grade_list:
    :param compare:
    :param gid:
    :return:
    '''
    mid_columns = get_middle_columns(method)
    df_all = middle_df_grd(grd_ob,grd_fo,method,grade_list,compare = compare,marker=marker,marker_name=marker_name)
    ds_all = tran_middle_df_to_ds(df_all,mid_columns)
    return ds_all


def get_grid_marker(grid,step = 10):

    marker = meteva.base.grid_data(grid)
    lon = marker["lon"].values
    lat = marker["lat"].values
    if step >=1:
        lon_step = (np.ceil(lon/step)*step).astype(np.int32)
        lat_step = (np.ceil(lat/step)*step).astype(np.int32)
    else:
        lon_step = (np.ceil(lon / step) * step*10).astype(np.int32)
        lat_step = (np.ceil(lat / step) * step*10).astype(np.int32)
    xx,yy = np.meshgrid(lon_step,lat_step)
    if step >= 1:
        zz = yy*1000+xx
    else:
        zz = yy * 10000 + xx
    marker = meteva.base.grid_data(grid,zz)
    meteva.base.set_griddata_coords(marker,member_list=["id"])
    return marker

if __name__ =="__main__":
    pass
    # import pandas as pd
    # path = r"O:\data\hdf\gongbao\rain24h_update12h_station2k\rain24h_update12h_station2k.h5"
    #
    # # #path = r"H:/a.h5"
    # sta_all = pd.read_hdf(path)
    # sta_all = meteva.base.sele_by_para(sta_all, time_range=["2023123108", "2024010208"], dtime_range=[24, 72])
    # print(sta_all)
    # import meteva.product as mpd
    # import meteva.method as mem
    # result = mpd.score(sta_all,mem.ob_fo_precipitation_strength,g = "dtime",plot = "bar",tag = 3,save_path = r"H:\task\a.png")
    # print(result)
    # dfmid = meteva.perspact.middle_df_sta(sta_all,mem.cscs)
    # print(dfmid)
    # result = meteva.perspact.score_df(dfmid,mem.ob_fo_precipitation_strength,g = ["member","dtime"],plot = "bar",tag = 3,save_path = r"H:\task\b.png")
    # print(result)
    # print()


    # sta_all = meteva.base.sele_by_para(sta_all,time_range = ["2023062008","2023062408"],dtime_range = [24,72])
    #
    # print(sta_all.iloc[:,6].values)
    # sta_all1 = sta_all.copy()
    # sta_all1.iloc[:,6] = 0
    # sta_all1.iloc[sta_all.iloc[:,6].values >=10 , 6] = 1
    # sta_all1.iloc[:, 7:] = sta_all.iloc[:, 7:].values /50
    # values = sta_all1.iloc[:,7:].values
    # values[values>1] = 1
    # sta_all1.iloc[:,7:] = values
    # sta_all1.to_hdf(r"H:\test_data\input\mps\rain24_10m_probability.h5","df")

    #method = get_middle_columns(meteva.method.nasws_uv)
    #print(method)

    # sta_all1 = pd.read_hdf(r"H:\test_data\input\mps\rain24_10m_probability.h5")
    # df = middle_df_sta(sta_all1,meteva.method.hfmc_multi,grade_list=[0.3,0.5])
    # print(df)
    # score = meteva.perspact.score_df(df,meteva.method.ts_multi,g = ["member","grade"],plot="line",
    #                                   save_path=r"H:\test_data\output\mps\ts.png")
    # print(score)
    # score = meteva.product.score(sta_all1,meteva.method.ts_multi,grade_list=[0.3,0.5])
    # print(score)