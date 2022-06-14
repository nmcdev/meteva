import meteva
import numpy as np

def tran_typhoon_report(sta_all):
    '''
    将台风报文的数据排列方式转换成按观测预报匹配方式排列的数据
    :param sta_all:
    :return:
    '''

    sta0_list,ids = meteva.base.group(sta_all,g = "id")
    sta_list_speed = []
    sta_list_position = []
    sta_value_columns = sta_all.iloc[:, 6:].columns.values.tolist()
    for i in range(len(ids)):
        sta0 = sta0_list[i]
        sta0_ob = meteva.base.sele_by_para(sta0,dtime = 0)
        sta0_ob.sort_values(by = ["time"],inplace = True)
        value = sta0_ob.iloc[:,-1]
        index = np.where(value>=17.2)
        sta1_ob = sta0_ob.iloc[:,index[0][0]:]
        sta1_fo = meteva.base.sele_by_para(sta0,dtime_range = [1,720])
        sta_all_s = meteva.base.combine_on_obTime_id(sta1_ob,[sta1_fo],need_match_ob=True)
        sta_list_speed.append(sta_all_s)
        sta1_ob_p = sta1_ob.drop(sta_value_columns, axis=1, inplace=False)
        sta1_ob_p["x"] = sta1_ob_p["lon"]
        sta1_ob_p["y"] = sta1_ob_p["lat"]
        sta1_fo_p = sta1_fo.drop(sta_value_columns, axis=1, inplace=False)
        sta1_fo_p["x"] = sta1_fo_p["lon"]
        sta1_fo_p["y"] = sta1_fo_p["lat"]
        sta_all_p =  meteva.base.combine_on_obTime_id(sta1_ob_p,[sta1_fo_p],need_match_ob=True)
        sta_list_position.append(sta_all_p)

    sta_all_speed = meteva.base.concat(sta_list_speed)
    meteva.base.set_stadata_names(sta_all_speed,data_name_list=["obs","fst"])
    sta_all_position = meteva.base.concat(sta_list_position)
    meteva.base.set_stadata_names(sta_all_position, data_name_list=["lon_obs", "lat_obs","lon_fo","lat_fo"])

    return sta_all_speed,sta_all_position




if __name__ == "__main__":


    filename = r"H:\test_data\input\meb\cyclone\babj_2201.dat"  # 设置台风路径文件
    sta1 = meteva.base.read_cyclone_trace(filename, id_cyclone=2201, column=meteva.base.m7_element_column.最大风速)  # 读取台风路径数据（包括定位和预报）
    sta_all_speed,sta_all_position = tran_typhoon_report(sta1)

    #result = meteva.product.score(sta_all_speed,meteva.method.rmse,g = "dtime")
    sta_part = meteva.base.sele_by_para(sta_all_position,time = "2022040808")
    print(sta_part)
    result = meteva.product.score(sta_part,meteva.method.distance,on_earth_surface= True,g = "dtime")
    print(result)

