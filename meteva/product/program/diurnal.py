import meteva
from meteva.base import *
from meteva.method import *
from meteva.product.program.fun import *
import pandas as pd
import numpy as np




def diunal_max_hour(sta_ob_and_fos0,method,s = None,g = None,gll = None,group_name_list = None,plot = None,
          vmax = 24,vmin = 0,bar_width = None,save_path = None,show = False,dpi = 300,title = "",excel_path = None,**kwargs):
    '''
    对于每个分组的样本，先统计日变化的曲线，再求日变化曲线的顶点
    :param sta_ob_and_fos0:
    :param method:
    :param s:
    :param g:
    :param gll:
    :param group_name_list:
    :param plot:
    :param vmax:
    :param vmin:
    :param bar_width:
    :param save_path:
    :param show:
    :param dpi:
    :param title:
    :param excel_path:
    :param kwargs:
    :return:
    '''
    if g=="ob_hour":
        print("日变化分析模块已经包含了按ob_hour分类统计功能，不能再设置g = ob_hour")
    if s is not None:
        if g is not None:
            if g == "last_range" or g == "last_step":
                s["drop_last"] = False
            else:
                s["drop_last"] = True
    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s=s)
    if (len(sta_ob_and_fos1.index) == 0):
        print("there is no data to verify")
        return

    dtimes = sta_ob_and_fos1["dtime"] * np.timedelta64(1, 'h')
    obtimes = pd.Series(0,index = sta_ob_and_fos1['time'] + dtimes)
    ob_hours_list = list(set(obtimes.index.hour))
    ob_hours_list.sort()
    ob_hour_count = len(ob_hours_list)

    method_args = {}
    plot_args = {}
    method_para_list = method.__code__.co_varnames
    plot_mehod = None
    if plot == "bar":
        plot_mehod = meteva.base.plot_tools.bar
    elif plot == "line" or plot == "plot":
        plot_mehod = meteva.base.plot_tools.plot

    plot_para_list = []
    if plot_mehod is not None:
        plot_para_list = plot_mehod.__code__.co_varnames

    for key in kwargs.keys():
        if key in method_para_list and key not in plot_para_list:
            method_args[key] = kwargs[key]
        elif key not in method_para_list and key in plot_para_list:
            plot_args[key] = kwargs[key]
        elif key in method_para_list and key in plot_para_list:
            msg = method.__name__ + " and " + plot_mehod.__name__ + " have same args:" + key
            print(msg)
            return None, msg
        else:
            if plot_mehod is None:
                msg = key + " is not args of " + method.__name__
            else:
                msg = key + " is not args of " + method.__name__ + " or " + plot_mehod.__name__
            print(msg)
            return None, msg

    #等级参数的确定
    if "grade_list" not in kwargs.keys():
        mutil_list = [meteva.method.ts_multi, meteva.method.bias_multi, meteva.method.ets_multi,
                      meteva.method.mr_multi, meteva.method.far_multi]
        if method in mutil_list:
        # 如果是多分类检验，但又没有设置分级方法，就需要从数据中获得全局的种类
            values = sta_ob_and_fos1.iloc[:,6:].flatten()
            index_list = list(set(values))
            if len(index_list) > 30:
                msg = "自动识别的样本类别超过30种，判断样本为连续型变量，grade_list不能缺省"
                print(msg)
                return None,msg
            index_list.sort()
            grade_list = []
            for i in range(len(index_list)-1):
                grade_list.append((index_list[i]+index_list[i+1])/2)
            kwargs["grade_list"] = grade_list

    if "grade_list" in kwargs.keys():
        grades = kwargs["grade_list"]
        grade_names = []
        mutil_list1 = [meteva.method.ts_multi, meteva.method.bias_multi, meteva.method.ets_multi,
                       meteva.method.mr_multi, meteva.method.far_multi,
                       meteva.method.ts_grade, meteva.method.bias_grade, meteva.method.ets_grade,
                       meteva.method.mr_grade, meteva.method.far_grade]
        mutil_list2 = [meteva.method.accuracy,meteva.method.hk,meteva.method.hss]
        if method in mutil_list1:
            grade_names = ["<" +  str(grades[0])]
            for i in range(len(grades)-1):
                grade_names.append("["+str(grades[i]) + ","+str(grades[i+1])+")")
            grade_names.append(">=" + str(grades[-1]))
        elif method in mutil_list2:
            grade_names = ["0"]
        else:
            for i in range(len(grades)):
                grade_names.append(grades[i])
    else:
        grade_names = ["0"]
    grade_num = len(grade_names)


    sta_ob_and_fos_list,gll1 = meteva.base.group(sta_ob_and_fos1,g = g,gll=gll)
    if gll1 is None:gll1 = [None]
    data_name = meteva.base.get_stadata_names(sta_ob_and_fos_list[0])
    if method.__name__.find("ob_fo")>=0:
        fo_name = data_name
    elif method.__name__.find("_uv")>=0:
        fo_name = []
        for i in range(2,len(data_name),2):
            strs = data_name[i]
            strs = strs.replace("u_","")
            fo_name.append(strs)
    else:
        ensemble_score_method = [meteva.method.cr,variance_divide_by_mse]
        if method in ensemble_score_method:
            fo_name = [""]
        elif method ==meteva.method.variance_mse:
            fo_name = ["variance","MSE"]
        elif method ==meteva.method.std_rmse:
            fo_name = ["STD","RMSE"]
        else:
            fo_name = data_name[1:]

    fo_num = len(fo_name)

    gll_valid = []
    result_list =[]
    for i in range(len(gll1)):
        result_all,hour_list = meteva.product.program.score(sta_ob_and_fos_list[i],method,g = "ob_hour",gll = ob_hours_list,**method_args)
        hours = np.array(hour_list)
        if len(hour_list) == ob_hour_count:
            gll_valid.append(gll1[i])
            result_max_index = np.argmax(result_all,axis=0)
            result_max = hours[result_max_index]
            result_list.append(result_max)

    result = np.array(result_list)
    group_num = len(gll_valid)

    if plot is not None or excel_path is not None:

        name_list_dict = {}
        if g is None:
            group_dict_name = "group_name"
        else:
            group_dict_name = g
        #设置分组名称
        if group_name_list is not None:
            if group_num == len(group_name_list):
                name_list_dict[group_dict_name] =group_name_list
            else:
                print("group_name_list参数中包含的分组名称个数和实际分组个数不匹配")
        else:
            if not isinstance(gll_valid,list):
                group_list_list1 = [gll_valid]

            if (group_dict_name == "time" or group_dict_name == "ob_time")and gll is None:
                name_list_dict[group_dict_name] = gll_valid
            else:
                name_list_dict[group_dict_name] = get_group_name(gll_valid)

        #设置成员名称

        name_list_dict["member"] = fo_name
        if fo_num==0:
            fo_num = 1
            name_list_dict["member"] = ["OBS"]
        result_plot = result.reshape((group_num,fo_num,grade_num))

        #设置等级名称
        name_list_dict["grade"] = grade_names
        keys = list(name_list_dict.keys())
        if fo_num ==1:
            if grade_num > 1:
                if group_num>1:
                    legend = keys[2]
                    axis = keys[0]
                else:
                    axis = keys[2]
                    legend = keys[1]
            else:
                axis = keys[0]
                legend = keys[1]
        else:
            if group_num == 1 :
                if grade_num >1:
                    legend = keys[1]
                    axis = keys[2]
                else:
                    legend = keys[2]
                    axis = keys[1]
            else:
                legend = keys[1]
                axis = keys[0]
        if "ylabel" not in plot_args.keys():
            plot_args["ylabel"] = "峰值时间"



        bigthan0_method = [meteva.method.ts,meteva.method.ob_fo_hr,meteva.method.ob_fo_std,meteva.method.ts_multi,
                           meteva.method.s,meteva.method.pc_of_sun_rain,meteva.method.bias_multi,meteva.method.bias,
                           meteva.method.pc,meteva.method.mr,meteva.method.far,meteva.method.tc,
                           meteva.method.roc_auc,meteva.method.r,meteva.method.sr,meteva.method.cr,meteva.method.pod,
                           meteva.method.pofd,meteva.method.mse,meteva.method.rmse,meteva.method.mae]

        if vmin is None:
            if method in bigthan0_method:
                vmin = 0
        if "hline" not in plot_args.keys():
            if method in [meteva.method.me]:
                plot_args["hline"] = 0
            elif method in [meteva.method.bias]:
                plot_args["hline"] = 1


        if plot is not None:
            if plot =="bar":
                meteva.base.plot_tools.bar(result_plot,name_list_dict,legend=legend,axis = axis,vmin =vmin,vmax = vmax,bar_width=bar_width,save_path=save_path,show=show,dpi =dpi,title = title,**plot_args)
            else:
                meteva.base.plot_tools.plot(result_plot,name_list_dict,legend=legend,axis = axis,vmin =vmin,vmax = vmax,save_path=save_path,show=show,dpi = dpi,title= title,**plot_args)
        if excel_path is not None:
            meteva.base.write_array_to_excel(result_plot,excel_path,name_list_dict,index= axis,columns=legend)

    return result,gll_valid



def diunal_max_hour_id(sta_ob_and_fos0,method,s = None,plot = "scatter",save_dir = None,save_path = None,show = False,
             add_county_line = False,map_extend= None,print_max=0,print_min=0,dpi = 300,title = None,sort_by = None,
             **kwargs):
    '''

    :param sta_ob_and_fos0:
    :param method:
    :param s:
    :param plot:
    :param save_dir:
    :param save_path:
    :param show:
    :param add_county_line:
    :param map_extend:
    :param print_max:
    :param print_min:
    :param dpi:
    :param title:
    :param sort_by:
    :param kwargs:
    :return:
    '''
    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s=s)
    diunal_max_hour(sta_ob_and_fos1,method)
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos1)
    ensemble_score_method = [meteva.method.cr, variance_divide_by_mse]

    # get method_args and plot_args
    method_args = {}
    plot_args = {}
    method_para_list = method.__code__.co_varnames
    plot_mehod = None
    if plot == "scatter":
        plot_mehod = meteva.base.plot_tools.scatter_sta

    plot_para_list = []
    if plot_mehod is not None:
        plot_para_list = plot_mehod.__code__.co_varnames


    for key in kwargs.keys():
        if key in method_para_list and key not in plot_para_list:
            method_args[key] = kwargs[key]
        elif key not in method_para_list and key  in plot_para_list:
            plot_args[key] = kwargs[key]
        elif key  in method_para_list and key  in plot_para_list:
            print(method.__name__ + " and " + plot_mehod.__name__ + " have same args:" + key)
            return
        else:
            print(key + " is not args of " + method.__name__ + " or " + plot_mehod.__name__)
            return

    #plot_args["subplot"] = "member"

    if method.__name__.find("ob_fo") >= 0:
        fo_name = data_names

    elif method.__name__.find("_uv") >= 0:
        fo_name = []
        for i in range(2, len(data_names), 2):
            strs = data_names[i]
            strs = strs.replace("u_", "")
            fo_name.append(strs)

    elif method.__name__ == "sample_count":
        fo_name = [data_names[0]]
    elif method in ensemble_score_method:
        fo_name = [""]
    elif method == meteva.method.variance_mse:
        fo_name = ["variance", "MSE"]
    elif method == meteva.method.std_rmse:
        fo_name = ["STD", "RMSE"]
    else:
        fo_name = data_names[1:]
    fo_num = len(fo_name)
    if "grade_list" in kwargs.keys():
        grades = kwargs["grade_list"]
        grade_names = []
        mutil_list1 = [meteva.method.ts_multi, meteva.method.bias_multi, meteva.method.ets_multi,
                       meteva.method.mr_multi, meteva.method.far_multi,
                       meteva.method.ts_grade, meteva.method.bias_grade, meteva.method.ets_grade,
                       meteva.method.mr_grade, meteva.method.far_grade]
        mutil_list2 = [meteva.method.accuracy,meteva.method.hk,meteva.method.hss]
        if method in mutil_list1:
            grade_names = ["<" +  str(grades[0])]
            for i in range(len(grades)-1):
                grade_names.append("["+str(grades[i]) + ","+str(grades[i+1])+")")
            grade_names.append(">=" + str(grades[-1]))
        elif method in mutil_list2:
            grade_names = ["0"]
        else:
            for i in range(len(grades)):
                grade_names.append(grades[i])
    else:
        grade_names = ["0"]
    grade_num = len(grade_names)

    if save_path is not None:
        if isinstance(save_path, str):
            save_path = [save_path]


    result, id_list = diunal_max_hour(sta_ob_and_fos1, method, g="id", **method_args,plot = None)
    station = sta_ob_and_fos1.drop_duplicates(['id'], inplace=False)
    station.iloc[:, 1] = station.iloc[0, 1]
    station.iloc[:, 2] = station.iloc[0, 2]
    station.iloc[:, 0] = station.iloc[0, 0]
    station1 = meteva.base.in_id_list(station, id_list)
    id_s = pd.Series(id_list)
    id_s.name = "id"
    sta_merge = pd.merge(id_s, station1, on='id', how='left')
    sta_merge = meteva.base.sta_data(sta_merge)
    coord_names = meteva.base.get_coord_names()

    if len(result.shape) == 1:
        # 没有等级，只有一个预报成员
        coord_names.append(data_names[-1])
        sta_result = sta_merge.loc[:, coord_names]
        sta_result.iloc[:, -1] = result[:]
        sta_result = [sta_result]
    elif len(result.shape) == 2:
        if len(fo_name) > 1:
            # 没有等级，但有多个预报成员
            if method.__name__.find("_uv") >= 0:
                # member_num = result.shape[1]
                # coord_names.extend(fo_name)
                sta_result = sta_merge.loc[:, coord_names]
                for ff in range(len(fo_name)):
                    sta_result[fo_name[ff]] = result[:, ff]
                sta_result = [sta_result]
            elif method == meteva.method.variance_mse:
                member_num = result.shape[1]
                # coord_names.extend(fo_name)
                sta_result = sta_merge.loc[:, coord_names]
                sta_result["variance"] = result[:, 0]
                sta_result["MSE"] = result[:, 1]
                sta_result = [sta_result]
            elif method == meteva.method.std_rmse:
                member_num = result.shape[1]
                # coord_names.extend(fo_name)
                sta_result = sta_merge.loc[:, coord_names]
                sta_result["STD"] = result[:, 0]
                sta_result["RMSE"] = result[:, 1]
                sta_result = [sta_result]
            else:
                member_num = result.shape[1]
                coord_names.extend(fo_name)
                sta_result = sta_merge.loc[:, coord_names]
                sta_result.iloc[:, -member_num:] = result[:, :]
                sta_result = [sta_result]
        else:
            # 有多个等级，但只有一个预报成员
            sta_result = []
            coord_names.append(data_names[-1])
            for i in range(result.shape[1]):
                sta_result1 = sta_merge.loc[:, coord_names]
                sta_result1.iloc[:, -1] = result[:, i]
                sta_result.append(sta_result1)
    else:
        # 有多个等级，同时有多个预报成员
        sta_result = []
        coord_names.extend(fo_name)
        member_num = result.shape[1]
        for i in range(result.shape[2]):
            sta_result1 = sta_merge.loc[:, coord_names]
            sta_result1.iloc[:, -member_num:] = result[:, :, i]
            sta_result.append(sta_result1)
    for i in range(len(sta_result)):
        sta_result1 = sta_result[i]
        if "var_name" in sta_ob_and_fos0.attrs.keys():
            sta_result1.attrs["var_name"] = sta_ob_and_fos0.attrs["var_name"]
        else:
            sta_result1.attrs["var_name"] = ""
        sta_result1.attrs["data_source"] = "meteva." + method.__name__
        if plot == "scatter" or plot == "micaps":
            if isinstance(title, list):
                title1_list = title[i: (i + 1) * fo_num]
            else:
                title1_list = []
                for ii in range(fo_num):
                    if title is not None:
                        title1 = meteva.product.program.get_title_from_dict(title, s, None, None,
                                                                            fo_name[ii])
                    else:
                        title1 = meteva.product.program.get_title_from_dict("", s, None,
                                                                           None, fo_name[ii])
                    if grade_num > 1:
                        title1 += "(grade_" + str(grade_names[i]) + ")"
                    title1_list.append(title1)

            if plot == "scatter":
                save_path1 = None
                if save_path is None:
                    if save_dir is None:
                        show = True
                    else:
                        save_path1 = []
                        for i in range(len(title1_list)):
                            fileName = title1_list[i].replace("\n", "").replace(":", "")
                            save_path1.append(save_dir + "/" + fileName + ".png")
                else:
                    save_path1 = save_path[i]

                meteva.base.tool.plot_tools.scatter_sta(sta_result1, save_path=save_path1, show=show,
                                                        title=title1_list, print_max=print_max,
                                                        print_min=print_min
                                                        , add_county_line=add_county_line,
                                                        map_extend=map_extend, dpi=dpi, **plot_args,cmap="hour")
            if plot == "micaps":
                meteva.base.put_stadata_to_micaps(sta_result1, layer_description=title1_list)

    if len(sta_result) == 1:
        sta_result = sta_result[0]
    if sort_by is not None:
        sta_result.sort_values(by=sort_by, axis=0, ascending=False, inplace=True)

    return sta_result, None


