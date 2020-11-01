import meteva
import pandas as pd
import numpy as np
import math
import datetime
meteva.base.set_io_config(r"H:\test_data\ip_port.txt")

'''
#该模块将逐步包含业务规范中的短时强降水的检验规则
'''


def edition_2020_1_lightning_ob_to_cound(lightning_ob, station, dlon_dlat = 1):
    '''
    该模块实现的功能是先将不规则时间、空间发生的闪电，通过最近距离法记录到规则网格的闪电次数中。
    再采用临近点插值方法将规则网格的闪电次数插值到国家站和区域站

    :param lightning_ob:   sta_data 形式的闪电观测数据，它是一个DataFrame， 包含7列内容，分别为 level, time,dtime,id,lon,lat, 闪电强度。
                            其中time,lon,lat 是计算所需的内容，  level， dtime,id，闪电强度等列的内容可以为任意值。
    :param station:    网格插值到站点用的站点列表， sta_data 数据格式
    :param dlon_dlat ： 闪电次数网格化时用的网格距
    :return:  站点形式的闪电次数，数据格式为sta_data
    '''
    # 根据原始的闪电数据获取逐小时记录的闪电数据
    # 如果lightning_ob已经是逐小时的数据了，下面一行语句也可以正常工作不会导致的错误，但比直接赋值的方式计算略多
    sta_ob_lightning_hourly = meteva.base.time_ceilling(lightning_ob, 1)

    # 根据闪电数据获取网格化的闪电次数
    # 设置闪电次数网格化参数

    #设置网格范围
    min_lon1 = min(lightning_ob["lon"])
    min_lon2 = min(station["lon"])
    min_lon = min(min_lon1,min_lon2)
    min_lon = math.floor(min_lon / dlon_dlat) * dlon_dlat
    max_lon1 = max(lightning_ob["lon"])
    max_lon2 = max(station["lon"])
    max_lon = max(max_lon1,max_lon2)
    max_lon = math.ceil(max_lon / dlon_dlat) * dlon_dlat


    min_lat1 = min(lightning_ob["lat"])
    min_lat2 = min(station["lat"])
    min_lat = min(min_lat1, min_lat2)
    min_lat = math.floor(min_lat / dlon_dlat) * dlon_dlat
    max_lat1 = max(lightning_ob["lat"])
    max_lat2 = max(station["lat"])
    max_lat = max(max_lat1, max_lat2)
    max_lat = math.ceil(max_lat / dlon_dlat) * dlon_dlat
    grid = meteva.base.grid([min_lon, max_lon, dlon_dlat], [min_lat, max_lat, dlon_dlat])

    # 将闪电数据分解为逐小时数据
    sta_ob_lightning_hourly_list = meteva.base.group(sta_ob_lightning_hourly, g="time")
    sta_lightning_count_list = []  # 用于记录每个小时的闪电次数插值结果
    station1 = station.copy()
    station1.iloc[:,-1] = 0
    for sta1 in sta_ob_lightning_hourly_list[0]:
        # 根据站点形式的闪电数据，统计出网格形式的闪电次数
        #print(sta1)
        grid_lightning_count = meteva.base.add_stacount_to_nearest_grid(sta1, grid)
        # 将网格化闪电次数采用最邻近法插值到站点
        #print(grid_lightning_count)
        sta2 = meteva.base.interp_gs_nearest(grid_lightning_count, station1)
        #print(sta2)
        # 记录每小时的闪电次数插值结果。
        #meteva.base.scatter_sta(sta2)
        sta_lightning_count_list.append(sta2)
    sta_ob_linghtning_count = pd.concat(sta_lightning_count_list, axis=0)  # 将闪电次数观测数据拼接在一起。

    return sta_ob_linghtning_count



def edition_2020_1_lightning_cound_to_01(sta_ob_linghtning_count,station):
    '''
    该模块实现根据站点形式的闪电次数判断雷暴大风的第一个必要条件是否满足，满足就记为1，不满足就记为0.
    不同的站点类型可以设置不同的阈值条件
    :param sta_ob_linghtning_count:  sta_data形式的数据， 数据列为闪电次数，
    :param id_type_dict:   字典形式数据，用于标记每个站号对应站点类型， value = 1 代表 国家站
    :return:  sta_data 形式数据。
    '''
    # 业务标准相关的参数
    national_lightning_threshold = 1  # 国家站闪电数阈值
    regional_lightning_threshold = 4  # 国家站闪电数阈值
    # 设定每个站点对应的阈值
    #id_list = []
    #threshold_list = []
    #for id in id_type_dict:
    #    id_list.append(id)
    #    if id_type_dict[id] == 1:
            # 国家站
    #        threshold_list.append(national_lightning_threshold)
    #    else:
    #        threshold_list.append(regional_lightning_threshold)

    #id_threshold_dict = {"id": id_list, "thre": threshold_list}
    #id_threshold_sta = meteva.base.sta_data(pd.DataFrame(id_threshold_dict))
    id_threshold_sta = station.copy()
    id_threshold_sta.loc[station["data0"] ==1, "data0"] = 1  # 国家站阈值设置
    id_threshold_sta.loc[station["data0"] !=1, "data0"] = 4  # 非国家站阈值设置
    print(id_threshold_sta)
    id_threshold_sta[["level","time","dtime"]] = meteva.base.IV
    #根据闪电判断雷暴大风的第1个必要条件
    sta_ob_01 = meteva.method.point_to_area.p2p_vto01(sta_ob_linghtning_count,threshold= id_threshold_sta)
    return  sta_ob_01


def edition_2020_1_light01_maxwind_to_ob01(sta_lightning_01,sta_ob_max_wind):
    '''
    根据站点形式的闪电次数达标情况， 和 站点形式的最大风速 判断单个站是否出现雷暴大风
    :param sta_lightning_01:   站点形式的闪电次数达标情况，根据lightning_cound_to_01 函数生成
    :param sta_ob_max_wind:   站点形式的最大风速（过去1小时内）
    :return:  站点形式数据，数据列为 各个站雷暴大风是否发生，1代表发生，0代表维发生
    '''
    #根据最大风速判断雷暴大风的第2个必要条件
    print(sta_ob_max_wind)
    sta_ob_c2 = meteva.method.point_to_area.p2p_vto01(sta_ob_max_wind,threshold= 0.7)
    print(sta_ob_c2)
    sta_ob01 = meteva.base.mutiply_on_level_time_dtime_id(sta_lightning_01,sta_ob_c2,default=meteva.base.IV)
    print(sta_ob01)
    return sta_ob01


def edition_2020_1_skill_caculation(sta_ob01,sta_fo_list,pcapital_fo_list):
    '''
    :param sta_ob: 观测降水站点数据合集,其中站点值为具体的降水量值
    :param sta_fo_list:列表，其中第0个元素为中央台的预报插值到站点得到的站点数据的合集，第1个元素为省台预报对应结果.
     其中的站点值为0或1,0代表预报短时强降水不发生，1代表预报短时强降水发生
    :param pcapital_fo_list:列表，其中第0个元素为中央台的预报插值到省会城市得到的站点数据的合集，第1个元素为省台省会预报.
     其中的站点值为0或1,0代表预报短时强降水不发生，1代表预报短时强降水发生
    :param id_provice_dict: 字典形式数据，用于标记每个站号对应的省份
    :return:
    '''

    R = 40  # 邻域半径
    #根据邻域算法判断站点附近邻域范围内是否发生雷暴大风，0代表没发生，1代表发生了；
    print(sta_ob01)
    sta_ob_neared = meteva.method.p2a_vto01(sta_ob01,r = R,threshold= 0.5)  # sta_ob 里的数据取值只有0和1， 所以取threshold = 0.5 可以区分单点是否发生雷暴大风

    #在将观测和预报数据进行匹配对齐以及合并,其中观测值缺省的样本会被删除
    print(sta_ob_neared)
    print(sta_fo_list)
    sta_all_01 = meteva.base.combine_on_obTime_id(sta_ob_neared,sta_fo_list,need_match_ob=True)

    #在将观测和省会预报数据进行匹配对齐以及合并,其中观测值缺省的样本会被删除
    sta_all_01_pcapital = meteva.base.combine_on_obTime_id(sta_ob_neared,pcapital_fo_list,need_match_ob=True)

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
    print(pod_results)
    for i in range(12):
        spo[i] = meteva.method.spo(pod_results[i, 1], pod_results[i, 0])    # meteva.method.yes_or_no.skill.spo()
        sfa[i] = meteva.method.sfa(far_results[i, 1], far_results[i, 0])    # meteva.method.yes_or_no.skill.sfa()
        spo_pcapital[i] = meteva.method.spo(pod_results_pcapital[i, 1], pod_results_pcapital[i, 0])
        sfa_pcapital[i] = meteva.method.sfa(far_results_pcapital[i, 1], far_results_pcapital[i, 0])

    return spo,sfa,spo_pcapital,sfa_pcapital

def edtion_2020_1(lightning_ob,station,sta_ob_max_wind,sta_fo_list,pcapital_fo_list):
    '''
    将各模块串成一个整体
    :param lightning_ob:
    :param station:
    :param id_type_dict:
    :param sta_ob_max_wind:
    :param sta_fo_list:
    :param pcapital_fo_list:
    :return:
    '''
    sta_ob_linghtning_count = edition_2020_1_lightning_ob_to_cound(lightning_ob,station)
    sta_lightning_01 = edition_2020_1_lightning_cound_to_01(sta_ob_linghtning_count, station)
    sta_ob01 = edition_2020_1_light01_maxwind_to_ob01(sta_lightning_01,sta_ob_max_wind)
    print(sta_ob01)
    #meteva.base.scatter_sta(sta_ob01)
    return edition_2020_1_skill_caculation(sta_ob01,sta_fo_list,pcapital_fo_list)


if __name__ == "__main__":

    station_file = r"H:\resource\infomation-dat\sta30240.dat"  #  读取自动站的站号和经纬度信息
    station_all = meteva.base.read_station(station_file)
    station_all.iloc[:,-1] = 2  # 将站点类型都设置为2
    station_nation = meteva.base.read_station(meteva.base.station_国家站)
    station_nation.iloc[:,-1] = 1  #将国家站点类型设置为1
    station_all = meteva.base.put_stadata_on_station(station_nation,station_all)  # 将station_all中国家站的类型用 station_nation变量中的值取代
    #meteva.base.scatter_sta(station_all)  绘图查看站点类型设置是否正确


    time_start = datetime.datetime(2020,10,31,8,0)
    time_end = datetime.datetime(2020,10,31,20,0)

    ###读取收集闪电观测数据
    dir_ob = r"mdfs:///SURFACE/LIGHTNING_1H/YYYYMMDDHH0000.000"
    sta_list = []
    time0 = time_start
    while time0 <= time_end:
        path = meteva.base.get_path(dir_ob,time0)
        meteva.base.print_gds_file_values_names(path)
        sta = meteva.base.read_stadata_from_gds(path,meteva.base.gds_element_id.电流强度_闪电定位,
                                                time = time0,dtime = 0,level = 0,data_name = "lightning",show = True)
        sta_list.append(sta)
        time0 += datetime.timedelta(hours = 1)
    lightning_ob = pd.concat(sta_list,axis = 0)  #数据拼接


    ###读取收集大风观测数据
    dir_ob = r"mdfs:///SURFACE/MAX_WIND/YYYYMMDDHH0000.000"
    sta_list = []
    time0 = time_start
    while time0 <= time_end:
        path = meteva.base.get_path(dir_ob,time0)
        meteva.base.print_gds_file_values_names(path)
        sta = meteva.base.read_stadata_from_gds(path,meteva.base.gds_element_id.极大风速,
                                                time = time0,dtime = 0,level = 0,data_name = "maxwind",show = True)
        sta_list.append(sta)
        time0 += datetime.timedelta(hours = 1)
    max_wind_ob = pd.concat(sta_list,axis = 0)  #数据拼接


    # national
    dir_na = r"O:\data\grid\scmoc\YYYYMMDD\YYMMDDHH.TTT.nc"
    sta_list = []
    time0 = time_start
    while time0 < time_end:
        for dh in range(1, 13):
            path = meteva.base.get_path(dir_na, time0, dh)
            grd = meteva.base.read_griddata_from_nc(path,time=time0,dtime = dh,level = 0,data_name="scmoc",show=True)
            if grd is not None:
                sta = meteva.base.interp_gs_linear(grd, station_all)
                sta_list.append(sta)
        time0 += datetime.timedelta(hours=12)
    scmoc_sta_all = pd.concat(sta_list, axis=0)  # 数据拼接
    #scmoc_sta_all.iloc[:,-1] = 0 + (scmoc_sta_all.iloc[:,-1] >= 1)  # 将预报转换成0-1形式
    #print(scmoc_sta_all)

    # province
    dir_pr = r"O:\data\grid\smerge\YYYYMMDD\YYMMDDHH.TTT.nc"
    sta_list = []
    time0 = time_start
    while time0 < time_end:
        for dh in range(1, 13):
            path = meteva.base.get_path(dir_pr, time0, dh)
            grd = meteva.base.read_griddata_from_nc(path,time=time0,dtime = dh,level = 0,data_name="smerge",show=True)
            if grd is not None:
                sta = meteva.base.interp_gs_linear(grd, station_all)
                sta_list.append(sta)
        time0 += datetime.timedelta(hours=12)  #
    smerge_sta_all = pd.concat(sta_list, axis=0)  # 数据拼接
    #gmosrr_sta_all.iloc[:, -1] = 0 + (gmosrr_sta_all.iloc[:, -1] >= 2)  # 将预报转换成0-1形式

    #print(gmosrr_sta_all)

    #读取城镇预报，原则上从其它文件中读取，但为了简化问题，此处从网格预报中提取
    pcapital_id = [54511]
    scmoc_sta_pcapital = meteva.base.in_id_list(scmoc_sta_all,pcapital_id)
    smerge_sta_pcapital = meteva.base.in_id_list(smerge_sta_all,pcapital_id)

    spo, sfa, spo_pcapital, sfa_pcapital = edtion_2020_1(lightning_ob,station_all,max_wind_ob,[scmoc_sta_all,smerge_sta_all],
                                                     [scmoc_sta_pcapital,smerge_sta_pcapital])
    #print(spo)
    #print(sfa)
    #print(spo_pcapital)
    #print(sfa_pcapital)
