from nmc_verification.nmc_vf_report.verify.functions import *


def creat_middle_result(para):
    # 1#首先根据预报时效范围计算观测时效的范围,并且建立每个观测时间对应的多个起报时间和预报时效
    fo_start_time = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(para["fo_time_range"][0])
    fo_end_time = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(para["fo_time_range"][1])
    time_step = int(para["fo_time_range"][2][0:-1])
    time_type = para["fo_time_range"][2][-1]
    ob_time_dict = {}
    time1 = fo_start_time
    dtime_list = para["dtime"][0:-1]
    # 将观测时间与 （起报时+时效）通过字典 联系在一起   观测时间作为键  （起报时+时效）作为值
    # 放到ob_time_dict
    ob_time_and_fo_time_link(time1, fo_end_time, dtime_list, ob_time_dict, time_step)
    # ob_time_dict 结构 {实况时间：[[起报时间，dtime]]}
    # 设置中间检验结果
    # 2# 将检验标准分为两大类hmnf 与 pc_hmnf
    veri_group_num = len(para["veri_set"])  # 有几中检验标准 ，hmnf和 pc_hmnf#等
    middle_veri = {}
    for i in range(veri_group_num):
        middle_veri[i] = {}
        middle_veri[i]["para"] = get_middle_veri_para(para["veri_set"][i])
        middle_veri[i]["result"] = None  # 将改变后的字典赋值为 middle_veri
        # middle 结构为{i：{para：{name：veri_name，method:hfn/abcd,para1:grade_list,para1_Name:grade_name_list,plot_type:plot_type},result:value},,...........}
    # 3#划分区域 比如"新疆", "西北中东部", "华北", "东北", "黄淮江淮江南", "华南", "西南"
    # 区域之间对比   比如 实况新疆的数据 与预测新疆进行评分
    # 读取站点信息：
    station = nmc_verification.nmc_vf_base.io.read_stadata.read_from_micaps3(para["station"]["path"])
    station["data0"] = 9999
    ob_sta_all = None
    # 判断每个维度类型文件是否为固定文件
    para_dim_type = para["dim_type"]
    dim_type_num = 0
    dim_type_sta_all_dict = collections.OrderedDict()
    dim_type_sta1_list, dim_type_num = get_dim_type_info(para_dim_type, dim_type_sta_all_dict)

    fo_type_num = len(para["forecasts"])
    fo_sta_all_dict = collections.OrderedDict()
    for i in range(fo_type_num):
        # 存储所有预报站点数据的字典
        fo_sta_all_dict[i] = None
    # 筛选数据的阈值
    value_s = para["observation"]["valid"][0]  # 阈值开始值
    value_e = para["observation"]["valid"][1]  # 阈值结束值

    # 获取group_set 中hour的集合
    hour_list = get_time_set_in_group_set(para, 'hour')
    month_list = get_time_set_in_group_set(para, 'month')
    # 得到预报模式列表
    data_name_list = ["ob"]
    for model in para["forecasts"]:
        data_name_list.append(model["name"])
    time1 = fo_start_time - datetime.timedelta(hours=time_step)
    area_coords, area_shape = get_area_dims(para, is_fold_time=True)
    new_area_coords = copy.deepcopy(area_coords)
    area_coords['dim_type_region'] = ['、'.join(area_coord) for area_coord in new_area_coords['dim_type_region']]

    model_coords, model_shape = get_model_dims(data_name_list)
    wbl = 0
    # print(time1)
    while time1 <= fo_end_time:
        wbl += 1
        if (time_type == "h"):
            time1 = time1 + datetime.timedelta(hours=time_step)
        else:
            time1 = time1 + datetime.timedelta(minutes=time_step)
        # 判断时间是否在分析列表里
        if not time1.hour in hour_list:
            continue
        read_dim_type_data(dim_type_num, para_dim_type, dim_type_sta1_list, station, dtime_list, time1,
                           dim_type_sta_all_dict)
        # 读取观测
        # print(ob_time_dict)
        ob_sta_one_time_all, copy_ob_time_dict = read_ob_data(dtime_list, time1, ob_time_dict, para, station, value_s,
                                                              value_e)

        ob_time_dict = copy_ob_time_dict
        ob_sta_all = nmc_verification.nmc_vf_base.function.put_into_sta_data.join(ob_sta_all, ob_sta_one_time_all)
        # print(ob_sta_all)
        merge = None
        # 提取dim_type中数据
        for key in dim_type_sta_all_dict.keys():
            merge = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(merge,
                                                                                             dim_type_sta_all_dict[key])

        # 通过和dim数据merger来提取观测数据
        sta_before, sta_after = cut_sta_not_after(ob_sta_all, time1)
        ob_sta_all = sta_after

        if sta_before is None:
            continue
        merge = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(merge, sta_before)

        # 读取预报
        # print(merge)

        for dtime in dtime_list:
            new_merge = copy.deepcopy(merge)
            for i in range(fo_type_num):
                read_fo_data_on_one_time_and_one_dtime(para, i, time1, dtime, station, value_s, value_e,
                                                       fo_sta_all_dict)
            # print(fo_sta_all_dict)
            # 同一观测时间的数据
            # 通过和dim数据merger  来提取预报数据 # 将几种模式数据合并一起

            for key in fo_sta_all_dict.keys():
                new_merge = nmc_verification.nmc_vf_base.function.put_into_sta_data.merge_on_all_dim(new_merge,
                                                                                                     fo_sta_all_dict[
                                                                                                         key])
            group_set = copy.deepcopy(para["group_set"])
            group_set = close_time_grouping(group_set)
            # print(group_set)
            sta_list, para_list_dict_list = group_sta(new_merge, group_set)

            total_and_hmfn_and_abcd_dataset = xr.Dataset()

            for key in middle_veri.keys():

                mpara = middle_veri[key]["para"]

                one_veri_set_para_coords, one_veri_set_para_shape = get_one_veri_set_para_dims(mpara)
                confusion_matrix_coords, confusion_matrix_shape = get_confusion_matrix_dims(mpara)

                mpara["sample_must_be_same"] = para["sample_must_be_same"]
                methods = mpara["method"]
                para1 = None
                if "para1" in mpara.keys():
                    para1 = mpara["para1"]
                para2 = None
                if "para2" in mpara.keys():
                    para2 = mpara["para2"]

                total_and_hmfn_or_abcd_data_set = get_middle_veri_result(sta_list, mpara, area_coords, area_shape,
                                                                         model_coords, model_shape,
                                                                         one_veri_set_para_coords,
                                                                         one_veri_set_para_shape,
                                                                         confusion_matrix_coords,
                                                                         confusion_matrix_shape)

                total_and_hmfn_and_abcd_dataset.update(total_and_hmfn_or_abcd_data_set)
            dtime = str(dtime)
            dtime = dtime.zfill(3)
            path = time1.strftime("%Y%m%d%H") + '.' + str(dtime) + '.nc'
            total_and_hmfn_and_abcd_dataset.to_netcdf(path)
            # total_and_hmfn_and_abcd_dataset.close()

            print('已经写入完毕')


def verificate_with_middle_result(para):
    fo_start_time = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(para["fo_time_range"][0])
    fo_end_time = nmc_verification.nmc_vf_base.tool.time_tools.str_to_time(para["fo_time_range"][1])
    time_step = int(para["fo_time_range"][2][0:-1])
    time_type = para["fo_time_range"][2][-1]

    ob_time_dict = {}
    time1 = fo_start_time
    dtime_list = para["dtime"][0:-1]
    ob_time_and_fo_time_link(time1, fo_end_time, dtime_list, ob_time_dict, time_step)
    time1 = fo_start_time - datetime.timedelta(hours=time_step)
    # 获取时间维度的信息
    veri_group_num = len(para["veri_set"])
    # print(veri_group_num)# 有几中检验标准 ，hmnf和 pc_hmnf#等
    middle_veri = {}
    for i in range(veri_group_num):
        middle_veri[i] = {}
        middle_veri[i]["para"] = get_middle_veri_para(para["veri_set"][i])

    time_series = get_time_Series(time1, fo_end_time, time_type, time_step)
    para = time_unfold(para, time_series)
    dims, shape = get_time_dims(para, is_fold_area=True)
    # 获取时间分组
    group_dict = copy.deepcopy(para['group_set'])
    time_name_list = ['time', 'year', "month", "xun", "hou", "day", "hour"]
    for key in group_dict:
        if key not in time_name_list:
            group_dict[key] = 'fold'
    para_dict_list_list = group_para(group_dict)
    if para_dict_list_list is None:
        para_dict_list_list = [0]
    final_result_dict_list_array, coords_dict, indexes_dict = create_empty_data_and_coords_and_indexes_dict(para)

    all_path, shape = get_all_path(para_dict_list_list, time_series, dtime_list, shape)

    final_result_dict_list_array, coords_dict, indexes_dict = calculate_score(para, all_path,
                                                                              final_result_dict_list_array,
                                                                              indexes_dict, coords_dict)

    # 读取数据，计算出评分 并且将对应的数据按照vari_set的长度组成字典。 获取区域的dim和indexes

    # 得到转化DataArray所需要的coords和indexes和shape
    new_indexes_dict, new_coords_dict, new_shape_dict = get_dims_and_coords_and_shape(para, shape, dims, indexes_dict,
                                                                                      coords_dict,
                                                                                      final_result_dict_list_array)

    # 将数据通过上文得到的indexes 和coords和shape和grades转化为DataArray
    all_catrgory_grades_data_array_dict = create_DataArray_dict(para, final_result_dict_list_array, new_shape_dict,
                                                                new_coords_dict, new_indexes_dict)

    # 画图，将检验结果保存到excel中
    for key in all_catrgory_grades_data_array_dict.keys():
        veri_name = para["veri_set"][key]["name"]
        save_dir = para["save_dir"] + "/" + veri_name + "/"
        path = para["save_dir"] + "/" + veri_name + ".nc"
        result = all_catrgory_grades_data_array_dict[key]
        result.to_netcdf(path)
        plot_set = nmc_verification.nmc_vf_report.perspective.veri_plot_set(subplot=para["plot_set"]["subplot"],
                                                                            legend=para["plot_set"]["legend"],
                                                                            axis=para["plot_set"]["axis"],
                                                                            save_dir=save_dir)
        plot_set.bar(all_catrgory_grades_data_array_dict[key])
        excel_set = nmc_verification.nmc_vf_report.perspective.veri_excel_set.veri_excel_set(
            sheet=para["plot_set"]["subplot"], row=para["plot_set"]["legend"],
            column=para["plot_set"]["axis"], save_dir=save_dir)
        excel_set.excel(all_catrgory_grades_data_array_dict[key])


def verificate(para):
    creat_middle_result(para)
    verificate_with_middle_result(para)

