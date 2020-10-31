from meteva.base import *
from meteva.method import *
from meteva.product.program.fun import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def score(sta_ob_and_fos0,method,s = None,g = None,gll = None,group_name_list = None,plot = None,
          vmax = None,vmin = None,bar_width = None,save_path = None,show = False,dpi = 300,title = "",excel_path = None,**kwargs):


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

    if type(method) == str:
        method =  globals().get(method)
    if method == meteva.method.FSS_time:
        if g == "dtime":
            print("FSS_time 检验时，参数group_by不能选择dtime")
            return

    # get method_args and plot_args
    method_args = {}
    plot_args = {}
    method_para_list = method.__code__.co_varnames
    plot_mehod = None
    if plot == "bar":
        plot_mehod = meteva.base.plot_tools.bar
    elif plot == "line":
        plot_mehod = meteva.base.plot_tools.plot

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

    sta_ob_and_fos_list,group_list_list1 = group(sta_ob_and_fos,g,gll)
    group_num = len(sta_ob_and_fos_list)


    data_name = meteva.base.get_stadata_names(sta_ob_and_fos_list[0])
    if method.__name__.find("ob_fo")>=0:
        fo_name = data_name
    else:
        ensemble_score_method = [meteva.method.cr]
        if method in ensemble_score_method:
            fo_name = [""]
        else:
            fo_name = data_name[1:]
    fo_num = len(fo_name)


    #等级参数的确定
    if "grade_list" not in kwargs.keys():
        mutil_list = [meteva.method.ts_multi, meteva.method.bias_multi, meteva.method.ets_multi,
                      meteva.method.mr_multi, meteva.method.far_multi]
        if method in mutil_list:
        # 如果是多分类检验，但又没有设置分级方法，就需要从数据中获得全局的种类
            values = sta_ob_and_fos.iloc[:,6:].flatten()
            index_list = list(set(values))
            if len(index_list) > 30:
                print("自动识别的样本类别超过30种，判断样本为连续型变量，grade_list不能缺省")
                return
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

    if method == meteva.method.FSS_time:
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
                result2 = FSS_time(ob_array, fo_array, **kwargs)
                result1.append(result2)
            result.append(result1)
        result = np.array(result) #将数据转换成数组
        result = result.squeeze()

    else:
        result_list = []
        for i in range(group_num):
            sta = sta_ob_and_fos_list[i]
            #if(len(sta.index) == 0):
            #    result[i,:] = meteva.base.IV
            #else:
            ob = sta[data_name[0]].values
            fo = sta[data_name[1:]].values.T
            result1 = method(ob,fo,**method_args)
            result_list.append(result1)

        result = np.array(result_list)
    if plot is not None or excel_path is not None:
        result_plot = result.reshape((group_num,fo_num,grade_num))
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
            if not isinstance(group_list_list1,list):
                group_list_list1 = [group_list_list1]
            if (group_dict_name == "time" or group_dict_name == "ob_time")and gll is None:
                name_list_dict[group_dict_name] = group_list_list1
            else:
                name_list_dict[group_dict_name] = get_group_name(group_list_list1)

        #设置成员名称
        name_list_dict["member"] = fo_name
        #设置等级名称
        name_list_dict["grade"] = grade_names
        keys = list(name_list_dict.keys())
        if fo_num ==1:
            if grade_num > 1:
                print(keys)
                legend = keys[2]
                axis = keys[0]
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
            plot_args["ylabel"] = method.__name__.upper()


        bigthan0_method = [meteva.method.ts,meteva.method.ob_fo_hr,meteva.method.ob_fo_std,meteva.method.ts_multi,
                           meteva.method.s,meteva.method.pc_of_sun_rain,meteva.method.bias_multi,meteva.method.bias,
                           meteva.method.pc,meteva.method.mr,meteva.method.far,meteva.method.tc,
                           meteva.method.roc_auc,meteva.method.r,meteva.method.sr,meteva.method.cr,meteva.method.pod,
                           meteva.method.pofd,meteva.method.mse,meteva.method.rmse,meteva.method.mae]

        if vmin is None:
            if method in bigthan0_method:
                vmin = 0

        if plot is not None:
            if plot =="bar":
                meteva.base.plot_tools.bar(result_plot,name_list_dict,legend=legend,axis = axis,vmin =vmin,vmax = vmax,bar_width=bar_width,save_path=save_path,show=show,dpi =dpi,title = title,**plot_args)
            else:
                meteva.base.plot_tools.plot(result_plot,name_list_dict,legend=legend,axis = axis,vmin =vmin,vmax = vmax,save_path=save_path,show=show,dpi = dpi,title= title,**plot_args)
        if excel_path is not None:
            meteva.base.write_array_to_excel(result_plot,excel_path,name_list_dict,index= axis,columns=legend)
    result = result.squeeze()
    return result,group_list_list1



def score_id(sta_ob_and_fos0,method,s = None,g = None,gll = None,group_name_list = None,plot = None,save_dir = None,save_path = None,show = False,
             add_county_line = False,map_extend= None,print_max=0,print_min=0,dpi = 300,title = None,sort_by = None,**kwargs):

    if s is not None:
        if g is not None:
            if g == "last_range" or g == "last_step":
                s["drop_last"] = False
            else:
                s["drop_last"] = True

    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0,s = s)
    if(len(sta_ob_and_fos1.index) == 0):
        print("there is no data to verify")
        return

    sta_ob_and_fos_list, gll1 = meteva.base.group(sta_ob_and_fos1, g = g, gll = gll)

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

    g_num = len(sta_ob_and_fos_list)
    if(g_num == 1):gll1 = [None]
    if group_name_list is None:
        group_name_list = meteva.product.program.get_group_name(gll1)


    data_names = meteva.base.get_stadata_names(sta_ob_and_fos_list[0])

    if method.__name__.find("ob_fo")>=0:
        fo_name = data_names
    elif method.__name__ == "sample_count":
        fo_name = [data_names[0]]
    else:
        fo_name = data_names[1:]
    fo_num = len(fo_name)


    if title is not None:
        if isinstance(title, list):
            if fo_num * g_num * grade_num != len(title):
                print("手动设置的title数目和要绘制的图形数目不一致")
                return

    if save_path is not None:
        if isinstance(save_path, str):
            save_path = [save_path]
        if fo_num * g_num * grade_num != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return




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

    if "fix_size" not in plot_args.keys():
        plot_args["fix_size"] = False

    result_all = []
    for k in range(g_num):
        g_id = "id"
        result,id_list= score(sta_ob_and_fos_list[k],method,g = g_id,**method_args)
        station = sta_ob_and_fos1.drop_duplicates(['id'],inplace=False)
        station1 = meteva.base.in_id_list(station,id_list)
        id_s = pd.Series(id_list)
        id_s.name = "id"
        sta_merge = pd.merge(id_s,station1, on='id', how='left')
        sta_merge = meteva.base.sta_data(sta_merge)
        coord_names = meteva.base.get_coord_names()

        if len(result.shape) == 1:
            #没有等级，只有一个预报成员
            coord_names.append(data_names[-1])
            sta_result = sta_merge.loc[:,coord_names]
            sta_result.iloc[:,-1] = result[:]
            sta_result = [sta_result]
        elif len(result.shape) == 2:
            if len(fo_name) >1:
                #没有等级，但有多个预报成员
                member_num = result.shape[1]
                coord_names.extend(fo_name)
                sta_result = sta_merge.loc[:, coord_names]
                sta_result.iloc[:, -member_num:] = result[:,:]
                sta_result = [sta_result]
            else:
                #有多个等级，但只有一个预报成员
                sta_result = []
                coord_names.append(data_names[-1])
                for i in range(result.shape[1]):
                    sta_result1 = sta_merge.loc[:, coord_names]
                    sta_result1.iloc[:, -1] = result[:,i]
                    sta_result.append(sta_result1)
        else:
            #有多个等级，同时有多个预报成员
            sta_result = []
            coord_names.extend(fo_name)
            member_num = result.shape[1]
            for i in range(result.shape[2]):
                sta_result1 = sta_merge.loc[:, coord_names]
                sta_result1.iloc[:, -member_num:] = result[:,:,i]
                sta_result.append(sta_result1)
        for i in range(len(sta_result)):
            sta_result1 = sta_result[i]
            if plot == "scatter":

                if isinstance(title, list):
                    kk = k * grade_num + i
                    title1_list = title[kk * fo_num: (kk + 1) * fo_num]
                else:
                    title1_list = []
                    for ii in range(fo_num):
                        if title is not None:
                            title1 =meteva.product.program.get_title_from_dict(title, s, g, group_name_list[k],
                                                                                 fo_name[ii])
                        else:
                            title1 = meteva.product.program.get_title_from_dict(method, s, g,
                                                                                group_name_list[k], fo_name[ii])
                        if grade_num>1:
                            title1 += "(grade_" + str(grade_names[i])+")"
                        title1_list.append(title1)



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
                    save_path1 = save_path[k * fo_num: (k + 1) * fo_num]

                meteva.base.tool.plot_tools.scatter_sta(sta_result1, save_path=save_path1, show=show,
                                                        title=title1_list, print_max=print_max,
                                                        print_min=print_min
                                                        , add_county_line=add_county_line,
                                                         map_extend=map_extend, dpi=dpi,**plot_args)


        if len(sta_result) == 1:
            sta_result = sta_result[0]
        if sort_by is not None:
            sta_result.sort_values(by = sort_by,axis = 0,ascending = False,inplace=True)
        result_all.append(sta_result)

    if len(result_all)==1:
        result_all = result_all[0]

    return result_all,gll1



def score_tdt(sta_ob_and_fos0,method,s = None,g = None,gll = None,group_name_list = None,
              x_y = "obtime_time",annot = 0,save_dir = None,save_path = None,show = False,
        dpi = 300,title = None,**kwargs):
    if s is not None:
        if g is not None:
            if g == "last_range" or g == "last_step":
                s["drop_last"] = False
            else:
                s["drop_last"] = True

    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s=s)
    if(len(sta_ob_and_fos1.index) == 0):
        print("there is no data to verify")
        return
    sta_ob_and_fos_list, gll1 = meteva.base.group(sta_ob_and_fos1, g=g, gll=gll)

    if "grade_list" in kwargs.keys():
        grades = kwargs["grade_list"]
        grade_names = []
        mutil_list1 = [meteva.method.ts_multi, meteva.method.bias_multi, meteva.method.ets_multi,
                       meteva.method.mr_multi, meteva.method.far_multi,
                       meteva.method.ts_grade, meteva.method.bias_grade, meteva.method.ets_grade,
                       meteva.method.mr_grade, meteva.method.far_grade]
        mutil_list2 = [meteva.method.accuracy, meteva.method.hk, meteva.method.hss]
        if method in mutil_list1:
            grade_names = ["<" + str(grades[0])]
            for i in range(len(grades) - 1):
                grade_names.append("[" + str(grades[i]) + "," + str(grades[i + 1]) + ")")
            grade_names.append(">=" + str(grades[-1]))
        elif method in mutil_list2:
            grade_names = ["0"]
        else:
            for i in range(len(grades)):
                grade_names.append(str(grades[i]))
    else:
        grade_names = ["0"]
    grade_num = len(grade_names)

    g_num = len(sta_ob_and_fos_list)
    if (g_num == 1): gll1 = [None]
    if group_name_list is None:
        group_name_list = meteva.product.program.get_group_name(gll1)

    data_names = meteva.base.get_stadata_names(sta_ob_and_fos_list[0])

    if method.__name__.find("ob_fo") >= 0:
        fo_name = data_names
    elif method.__name__ == "sample_count":
        fo_name = [data_names[0]]
    else:
        fo_name = data_names[1:]
    fo_num = len(fo_name)


    if title is not None:
        if isinstance(title, list):
            if fo_num * g_num * grade_num != len(title):
                print("手动设置的title数目和要绘制的图形数目不一致")
                return


    if save_path is not None:
        if isinstance(save_path, str):
            save_path = [save_path]
        if fo_num * g_num * grade_num != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return


    # get method_args and plot_args
    method_args = {}
    plot_args = {}
    method_para_list = method.__code__.co_varnames
    plot_mehod = None
    if x_y == "obtime_dtime":
        plot_mehod = meteva.base.plot_tools.mesh_time_dtime
    elif x_y == "obtime_time":
        plot_mehod = meteva.base.plot_tools.mesh_obtime_time
    elif x_y == "time_dtime":
        plot_mehod = meteva.base.plot_tools.mesh_time_dtime

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

    result_all = []
    for k in range(g_num):
        sta_time_list,time_list = meteva.base.group(sta_ob_and_fos_list[k],g ="time")

        sta_result_list_dict = {}
        for gg in range(grade_num):
            sta_result_list_dict[gg] = []

        for st in range(len(sta_time_list)):
            sta_time = sta_time_list[st]
            result, dtime_list = score(sta_time, method, g="dtime", **method_args)

            if len(result.shape) <=1:
                # 没有等级，只有一个预报成员
                if len(result.shape) ==0:
                    result = [float(result)]
                dict_data = {"dtime":dtime_list,fo_name[0]:result}
                sta_result = pd.DataFrame(dict_data)
                sta_result["time"] = time_list[st]
                sta_result_list_dict[0].append(sta_result)
            elif len(result.shape) ==2:
                if len(fo_name) > 1:
                    # 没有等级，但有多个预报成员
                    dict_result = {}
                    dict_result["dtime"] = dtime_list
                    for f in range(fo_num):
                        dict_result[fo_name[f]] = result[:,f]
                    sta_result = pd.DataFrame(dict_result)
                    sta_result["time"] = time_list[st]
                    sta_result_list_dict[0].append(sta_result)
                else:
                    # 有多个等级，但只有一个预报成员
                    for gg in range(grade_num):
                        dict_result = {}
                        dict_result["dtime"] = dtime_list
                        print(fo_name)
                        dict_result[fo_name[0]] = result[:,gg]
                        sta_result = pd.DataFrame(dict_result)
                        sta_result["time"] = time_list[st]
                        sta_result_list_dict[gg].append(sta_result)
            else:
                for gg in range(grade_num):
                    dict_result = {}
                    dict_result["dtime"] = dtime_list
                    for f in range(fo_num):
                        dict_result[fo_name[f]] = result[:,f,gg]
                    sta_result = pd.DataFrame(dict_result)
                    sta_result["time"] = time_list[st]

                    sta_result_list_dict[gg].append(sta_result)

        sta_all_g_list = []
        for gg in range(grade_num):
            sta_all_g = pd.concat(sta_result_list_dict[gg])
            sta_all_g["level"] = meteva.base.IV
            sta_all_g["id"] = meteva.base.IV
            sta_all_g["lon"] = meteva.base.IV
            sta_all_g["lat"] = meteva.base.IV
            #print(sta_all_g)
            sta_all_g1 = meteva.base.sta_data(sta_all_g)
            sta_all_g_list.append(sta_all_g1)

        #print(sta_all_g_list)

        for i in range(len(sta_all_g_list)):
            sta_result1 = sta_all_g_list[i]

            title1_list = None
            if isinstance(title, list):
                kk = k * grade_num + i
                title1_list = title[kk * fo_num: (kk + 1) * fo_num]
            else:
                title1_list = []
                for ii in range(fo_num):
                    if title is not None:
                        title1 = meteva.product.program.get_title_from_dict(title, s, g, group_name_list[k],
                                                                            fo_name[ii])
                    else:
                        title1 = meteva.product.program.get_title_from_dict(method, s, g,
                                                                            group_name_list[k], fo_name[ii])
                    if grade_num > 1:
                        title1 += "(grade_" + str(grade_names[i]) + ")"
                    title1_list.append(title1)

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
                save_path1 = save_path[k * fo_num: (k + 1) * fo_num]

            #绘制图形
            #print("start plot")
            if x_y == "obtime_time":
                meteva.base.tool.plot_tools.mesh_obtime_time(sta_result1,save_dir=save_dir,save_path=save_path1,show = show,dpi = dpi,title = title1_list,annot = annot,**plot_args)
            elif x_y == "obtime_dtime":
                meteva.base.tool.plot_tools.mesh_obtime_dtime(sta_result1, save_dir=save_dir,save_path=save_path1,show = show,dpi = dpi, title=title1_list,annot = annot,**plot_args)
            elif x_y == "time_dtime":
                #print(sta_result1)
                meteva.base.tool.plot_tools.mesh_time_dtime(sta_result1, save_dir=save_dir,save_path=save_path1,show = show,dpi = dpi, title=title1_list,annot = annot,**plot_args)
            else:
                print("目前绘图样式参数 x_y仅支持 obtime_time, obtime_dtime, time_dtime三种形式")
        if len(sta_all_g_list) == 1:
            sta_all_g_list = sta_all_g_list[0]


        result_all.append(sta_all_g_list)

    if len(result_all) == 1:
        result_all = result_all[0]
    return result_all, gll1


def score_obhour_dtime(sta_ob_and_fos0,method,s = None,g = None,gll = None,group_name_list = None,
              x_y = "obtime_time",annot = 0,save_dir = None,save_path = None,show = False,
        dpi = 300,title = None,**kwargs):
    pass