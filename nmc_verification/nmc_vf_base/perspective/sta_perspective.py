import copy
import nmc_verification.nmc_vf_base.function as fun

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

def perspective(sta,para_array):
    para_list = para_array_to_list(0,para_array)
    sta_list = []
    for para in para_list:
        sta1 = get_sta_by_para(sta,para)
        print(para)
        print(sta1)
        sta_list.append(sta1)
    return sta_list

def get_sta_by_para(sta,para):

    sta1 = copy.deepcopy(sta)
    for key in para.keys():
        if key == "level":
            sta1 = fun.get_from_sta_data.sta_in_level_list(sta1,para[key])
        elif key == "time":
            sta1 = fun.get_from_sta_data.sta_in_time_list(sta1,para[key])
        elif key == "year":
            sta1 = fun.get_from_sta_data.sta_in_year_list(sta1,para[key])
        elif key == "month":
            sta1 = fun.get_from_sta_data.sta_in_month_list(sta1,para[key])
        elif key == "xun":
            sta1 = fun.get_from_sta_data.sta_in_xun_list(sta1,para[key])
        elif key == "hou":
            sta1 = fun.get_from_sta_data.sta_in_hou_list(sta1,para[key])
        elif key == "day":
            sta1 = fun.get_from_sta_data.sta_in_day_list(sta1,para[key])
        elif key == "hour":
            sta1 = fun.get_from_sta_data.sta_in_hour_list(sta1,para[key])
        elif key == "dtime":
            sta1 = fun.get_from_sta_data.sta_in_dtime_list(sta1,para[key])
        elif key == "dday":
            sta1 = fun.get_from_sta_data.sta_in_dday_list(sta1,para[key])
        elif key == "dhour":
            sta1 = fun.get_from_sta_data.sta_in_dhour_list(sta1,para[key])
        elif key == "dminute":
            sta1 = fun.get_from_sta_data.sta_in_dminute_list(sta1,para[key])
        elif key == "id":
            sta1 = fun.get_from_sta_data.sta_in_id_list(sta1,para[key])
        elif key == 'lon':
            sta1 = fun.get_from_sta_data.sta_between_lon_range(sta1,para[key][0],para[key][1])
        elif key == 'lat':
            sta1 = fun.get_from_sta_data.sta_between_lat_range(sta1, para[key][0], para[key][1])
        elif key == "alt":
            sta1 = fun.get_from_sta_data.sta_between_alt_range(sta1, para[key][0], para[key][1])
        else:
            print("参数关键词不支持")
    return sta1

