import meteva
import pandas as pd
import numpy as np
'''
#该模块将逐步包含业务规范中的短时强降水的检验规则
'''

def edition_2020_1(sta_ob,sta_fo_list,pcapital_fo_list, id_province_dict):
    '''

    :param sta_ob: 观测降水站点数据合集,其中站点值为具体的降水量值
    :param sta_fo_list:列表，其中第0个元素为中央台的预报插值到站点得到的站点数据的合集，第1个元素为省台预报对应结果.
     其中的站点值为0或1,0代表预报短时强降水不发生，1代表预报短时强降水发生
    :param pcapital_fo_list:列表，其中第0个元素为中央台的预报插值到省会城市得到的站点数据的合集，第1个元素为省台省会预报.
     其中的站点值为0或1,0代表预报短时强降水不发生，1代表预报短时强降水发生
    :param id_provice_dict: 字典形式数据，用于标记每个站号对应的省份
    :return:
    '''
    # 业务标准相关的参数
    west_province_list = ["内蒙古","西藏","青海","宁夏","新疆"]
    west_threshold = 10  #西部省份短时强降水阈值
    other_threshold = 2 #其它省份短时强降水阈值
    R = 40               #邻域半径

    # 设定每个站点对应的阈值
    id_list = []
    threshold_list = []

    for id in id_province_dict:
        id_list.append(id)
        if id_province_dict[id] in west_province_list:
            threshold_list.append(west_threshold)
        else:
            threshold_list.append(other_threshold)
    id_threshold_dict = {"id":id_list,"thre":threshold_list}
    id_threshold_sta = meteva.base.sta_data(pd.DataFrame(id_threshold_dict))


    #根据邻域算法根据包含具体降水量的观测数据，计算出每个站点邻域内是否发生了短时强降水，0代表没发生，1代表发生了；
    sta_ob_01 = meteva.method.p2a_vto01(sta_ob,r = R,threshold= id_threshold_sta)

    #在将观测和预报数据进行匹配对齐以及合并,其中观测值缺省的样本会被删除
    sta_all_01 = meteva.base.combine_on_obTime_id(sta_ob_01,sta_fo_list,need_match_ob=True)

    #在将观测和省会预报数据进行匹配对齐以及合并,其中观测值缺省的样本会被删除
    sta_all_01_pcapital = meteva.base.combine_on_obTime_id(sta_ob_01,pcapital_fo_list,need_match_ob=True)


    #按时效分类检验，所有站点
    pod_results = meteva.product.score(sta_all_01,meteva.method.pod,g = "dtime")[0]
    far_results = meteva.product.score(sta_all_01,meteva.method.far,g = "dtime")[0]

    #按时效分类检验，针对省会城市预报
    pod_results_pcapital = meteva.product.score(sta_all_01_pcapital,meteva.method.pod,g = "dtime")[0]
    far_results_pcapital = meteva.product.score(sta_all_01_pcapital,meteva.method.far,g = "dtime")[0]


    #计算预报技巧
    spo = np.zeros(12)  # 格点1小时命中率预报技巧(所有站点 )
    sfa = np.zeros(12)  # 格点1小时空报率预报技巧(所有站点 )
    spo_pcapital = np.zeros(12)   # 单站1小时命中率预报技巧(省会城市)
    sfa_pcapital = np.zeros(12)    # 单站1小时空报率预报技巧(省会城市)
    #循环12个时效
    for i in range(12):
        spo[i] = meteva.method.spo(pod_results[i, 1], pod_results[i, 0])    # meteva.method.yes_or_no.skill.spo()
        sfa[i] = meteva.method.sfa(far_results[i, 1], far_results[i, 0])    # meteva.method.yes_or_no.skill.sfa()
        spo_pcapital[i] = meteva.method.spo(pod_results_pcapital[i, 1], pod_results_pcapital[i, 0])
        sfa_pcapital[i] = meteva.method.sfa(far_results_pcapital[i, 1], far_results_pcapital[i, 0])

    return spo,sfa,spo_pcapital,sfa_pcapital



if __name__ == "__main__":

    station_file = r"H:\test_data\station_pta.txt"  #  读取自动站的站号和经纬度信息
    station = meteva.base.read_station(station_file)
    station.iloc[:,-1] = meteva.base.IV

    dict0 = meteva.base.station_id_name_dict
    dict1 = {}
    for id in dict0.keys():
        str0 = dict0[id]
        strss = str0.split("_")
        str1 = strss[0]
        dict1[id] = str1

    import datetime

    time_start = datetime.datetime(2020,8,18,8,0)
    time_end = datetime.datetime(2020,8,19,8,0)

    ###读取收集观测数据
    dir_ob = r"Y:\qpe\autorun\data_all\001h\YYYYMMDDHH.000.001h"
    sta_list = []
    time0 = time_start
    while time0 <= time_end:
        path = meteva.base.get_path(dir_ob,time0)
        #meteva.base.print_gds_file_values_names(path)
        sta = meteva.base.read_stadata_from_micaps3(path,station = station,time = time0,dtime = 0,level = 0,data_name = "ob",show = True)
        sta_list.append(sta)
        time0 += datetime.timedelta(hours = 1)
    ob_sta_all = pd.concat(sta_list,axis = 0)  #数据拼接

    # scmoc
    dir_scmoc = r"O:\data\grid\NWFD_SCMOC_1H\RAIN01\YYYYMMDD\YYMMDDHH.TTT.nc"
    sta_list = []
    time0 = time_start
    while time0 < time_end:
        for dh in range(1, 13):
            path = meteva.base.get_path(dir_scmoc, time0, dh)
            grd = meteva.base.read_griddata_from_nc(path,time=time0,dtime = dh,level = 0,data_name="scmoc",show=True)
            if grd is not None:
                sta = meteva.base.interp_gs_linear(grd, station)
                sta_list.append(sta)
        time0 += datetime.timedelta(hours=12)  # 此处跳着读是为了减少测试用时
    scmoc_sta_all = pd.concat(sta_list, axis=0)  # 数据拼接
    scmoc_sta_all.iloc[:,-1] = 0 + (scmoc_sta_all.iloc[:,-1] >= 2)  # 将预报转换成0-1形式

    # scmoc
    dir_gmosrr = r"O:\data\grid\GMOSRR\ROLLING_UPDATE\RAIN01\YYYYMMDD\YYMMDDHH.TTT.nc"
    sta_list = []
    time0 = time_start
    while time0 < time_end:
        for dh in range(1, 13):
            path = meteva.base.get_path(dir_gmosrr, time0, dh)
            grd = meteva.base.read_griddata_from_nc(path,time=time0,dtime = dh,level = 0,data_name="gmosrr",show=True)
            if grd is not None:
                sta = meteva.base.interp_gs_linear(grd, station)
                sta_list.append(sta)
        time0 += datetime.timedelta(hours=12)  # 此处跳着读是为了减少测试用时
    gmosrr_sta_all = pd.concat(sta_list, axis=0)  # 数据拼接
    gmosrr_sta_all.iloc[:, -1] = 0 + (gmosrr_sta_all.iloc[:, -1] >= 3)  # 将预报转换成0-1形式

    #读取城镇预报，原则上从其它文件中读取，但为了简化问题，此处从网格预报中提取

    pcapital_id = [54511]

    scmoc_sta_pcapital = meteva.base.in_id_list(scmoc_sta_all,pcapital_id)
    gmosrr_sta_pcapital = meteva.base.in_id_list(gmosrr_sta_all,pcapital_id)

    #

    spo, sfa, spo_pcapital, sfa_pcapital = edition_2020_1(ob_sta_all,[scmoc_sta_all,gmosrr_sta_all],
                                                     [scmoc_sta_pcapital,gmosrr_sta_pcapital],id_province_dict=dict1)


    print(spo)
    print(sfa)
    print(spo_pcapital)
    print(sfa_pcapital)