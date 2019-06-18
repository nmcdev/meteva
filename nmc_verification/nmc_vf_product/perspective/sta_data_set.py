import copy
import nmc_verification
import pandas as pd
import numpy as np
import math
import collections


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


def get_sta_by_para(sta,para):
    sta1 = copy.deepcopy(sta)
    for key in para.keys():
        if key == "level":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_level_list(sta1,para[key])
        elif key == "time":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_time_list(sta1,para[key])
        elif key == "year":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_year_list(sta1,para[key])
        elif key == "month":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_month_list(sta1,para[key])
        elif key == "xun":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_xun_list(sta1,para[key])
        elif key == "hou":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_hou_list(sta1,para[key])
        elif key == "day":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_day_list(sta1,para[key])
        elif key == "hour":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_hour_list(sta1,para[key])
        elif key == "dtime":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dtime_list(sta1,para[key])
        elif key == "dday":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dday_list(sta1,para[key])
        elif key == "dhour":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dhour_list(sta1,para[key])
        elif key == "dminute":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_dminute_list(sta1,para[key])
        elif key == "id":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_id_list(sta1,para[key])
        elif key == 'lon':
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_lon_range(sta1,para[key][0],para[key][1])
        elif key == 'lat':
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_lat_range(sta1, para[key][0], para[key][1])
        elif key == "alt":
            sta1 = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_between_alt_range(sta1, para[key][0], para[key][1])
        else:
            print("参数关键词不支持")
    return sta1



class sta_data_set:
    def __init__(self,sta = None):
        self.level = "fold"
        self.time = "fold"
        self.year = "fold"
        self.month = "fold"
        self.xun = "fold"
        self.hou = "fold"
        self.day = "fold"
        self.hour = "fold"
        self.dtime = "fold"
        self.dhour = "fold"
        self.dday = "fold"
        self.dminute = "fold"
        self.id = "fold"
        self.lon = "fold"
        self.lat = "fold"
        self.alt = "fold"
        self.sta_data = sta

    def set_sta(self,sta):
        self.sta_data = sta

    def set_level_unfold(self,level_list_list = None):
        if(level_list_list is None):
            self.level = "unfold"
        else:
            self.level = copy.deepcopy((level_list_list))

    def set_time_unfold(self,time_list_list = None,time_range_list = None):
        self.month = "fold"
        self.xun = "fold"
        self.year = "fold"
        self.hou = "fold"
        self.day = "fold"
        self.hour = "fold"
        if time_list_list is not None:
            self.time = copy.deepcopy(time_list_list)
        elif time_range_list is not None:
            list_list = []
            for time_range in time_range_list:
                time_start = nmc_verification.nmc_vf_base.method.time_tools.all_type_time_to_time64(time_range[0])
                time_end = nmc_verification.nmc_vf_base.method.time_tools.all_type_time_to_time64(time_range[1])
                dtime = nmc_verification.nmc_vf_base.method.time_tools.all_type_timedelta_to_timedelta64(time_range[2])
                time_list = pd.date_range(time_start, time_end, freq=dtime).to_list()
                list_list.append(time_list)
            self.time = list_list
        else:
            self.time = "unfold"


    def set_year_unfold(self,year_list_list = None):
        self.time = "fold"
        if year_list_list is None:
            self.year = "unfold"
        else:
            self.year = copy.deepcopy(year_list_list)


    def set_month_unfold(self,month_list_list = None):
        self.time = "fold"
        self.xun = "fold"
        self.hou = "fold"
        self.day = "fold"
        if month_list_list is None:
            self.month = "unfold"
        else:
            self.month = copy.deepcopy(month_list_list)

    def set_xun_unfold(self,xun_list_list = None):
        self.time = "fold"
        self.month = "fold"
        self.hou = "fold"
        self.day = "fold"
        if xun_list_list is None:
            self.xun = "unfold"
        else:
            self.xun = copy.deepcopy(xun_list_list)

    def set_hou_unfold(self,hou_list_list = None):
        self.time = "fold"
        self.month = "fold"
        self.xun = "fold"
        self.day = "fold"
        if hou_list_list is None:
            self.hou = "unfold"
        else:
            self.hou = copy.deepcopy(hou_list_list)

    def set_day_unfold(self,day_list_list = None):
        self.time = "fold"
        self.month = "fold"
        self.xun = "fold"
        self.hou = "fold"
        if day_list_list is None:
            self.day = "unfold"
        else:
            self.day = copy.deepcopy(day_list_list)


    def set_hour_unfold(self,hour_list_list = None):
        self.time = "fold"
        if hour_list_list is None:
            self.hour = "unfold"
        else:
            self.hour = copy.deepcopy(hour_list_list)

    def set_dtime_unfold(self,dtime_list_list = None,dtime_range_list = None):
        self.dday = "fold"
        self.dhour = "fold"
        if dtime_list_list is not None:
            self.dtime = copy.deepcopy(dtime_list_list)
        elif dtime_range_list is not None:
            list_list = []
            for dtime_range in dtime_range_list:
                sdtime = nmc_verification.nmc_vf_base.method.time_tools.all_type_timedelta_to_timedelta64(dtime_range_list[0])
                edtime = nmc_verification.nmc_vf_base.method.time_tools.all_type_timedelta_to_timedelta64(dtime_range_list[1])
                ddtime = nmc_verification.nmc_vf_base.method.time_tools.all_type_timedelta_to_timedelta64(dtime_range_list[2])

                ndt = int((edtime - sdtime) / ddtime) + 1
                dt_list = []
                for i in range(ndt):
                    dt_list.append(sdtime + ddtime * i)
                list_list.append(dt_list)
            self.dtime = list_list
        else:
            self.dtime = "unfold"



    def set_dhour_unfold(self,dhour_list_list = None):
        self.dtime = "fold"
        self.dminute = "fold"
        if dhour_list_list is None:
            self.dhour = "unfold"
        else:
            self.dhour = copy.deepcopy(dhour_list_list)

    def set_dminute_unfold(self,dminute_list_list = None):
        self.dtime = "fold"
        self.dhour = "fold"
        if dminute_list_list is None:
            self.dminute = "unfold"
        else:
            self.dminute = copy.deepcopy(dminute_list_list)


    def set_dday_unfold(self,dday_list_list = None):
        self.dtime = "fold"
        if dday_list_list is None:
            self.dday = "unfold"
        else:
            self.dday = copy.deepcopy(dday_list_list)


    def set_id_unfold(self,id_list_list = None):
        if id_list_list is None:
            self.id = "unfold"
        else:
            self.id = copy.deepcopy(id_list_list)

    def set_lon_unfold(self,lon_range = None,lon_range_list = None):
        if lon_range is not None:
            slon = lon_range[0]
            elon = lon_range[1]
            dlon = lon_range[2]
            if lon_range[0] > lon_range[1] | lon_range[2] <= 0:
                print("lon 范围格式不正确")
                return
            slon1 = slon
            elon1 = slon + dlon
            list_list = []
            while slon1 < elon:
                list_list.append([slon1, elon1])
                slon1 += dlon
                elon1 += dlon
            self.lon = list_list
        elif lon_range_list is not None:
            self.lon = copy.deepcopy(lon_range_list)
        else:
            self.lon = "unfold"

    def set_lat_unfold(self,lat_range = None,lat_range_list = None):
        if lat_range is not None:
            slat = lat_range[0]
            elat = lat_range[1]
            dlat = lat_range[2]
            if lat_range[0] > lat_range[1] | lat_range[2] <= 0:
                print("lon 范围格式不正确")
                return
            slat1 = slat
            elat1 = slat + dlat
            list_list = []
            while slat1 < elat:
                list_list.append([slat1, elat1])
                slat1 += dlat
                elat1 += dlat
            self.lat = list_list
        elif lat_range_list is not None:
            self.lat = copy.deepcopy(lat_range_list)
        else:
            self.lat = "unfold"

    def set_alt_unfold(self,alt_range = None,alt_range_list = None):
        if alt_range is not None:
            salt = alt_range[0]
            ealt = alt_range[1]
            dalt = alt_range[2]
            if alt_range[0] > alt_range[1] | alt_range[2] <= 0:
                print("lon 范围格式不正确")
                return
            salt1 = salt
            ealt1 = salt + dalt
            list_list = []
            while salt1 < ealt:
                list_list.append([salt1, ealt1])
                salt1 += dalt
                ealt1 += dalt
            self.alt = list_list
        elif alt_range_list is not None:
            self.alt = copy.deepcopy(alt_range_list)
        else:
            self.alt = "unfold"


    def set_para_dict_list_list(self):
        sta = self.sta_data
        para_array = collections.OrderedDict()
        #
        if self.level == "fold":
            pass
        elif self.level=='unfold':
            level_list = list(set(sta['level'].tolist()))
            level_list.sort()
            level_list2 = []
            for level in level_list:
                level_list2.append([level])
            para_array['level'] = level_list2
        else:
            para_array['level'] = copy.deepcopy(self.level)

        #
        if self.time == 'fold':
            pass
        elif self.time == 'unfold':
            time_list = list(set(sta['time'].tolist()))
            time_list.sort()
            time_list2 = []
            for time in time_list:
                time_list2.append([time])
            para_array['time'] = time_list2
        else:
            para_array['time'] = copy.deepcopy(self.time)

        #
        if self.year == "fold":
            pass
        elif self.year =="unfold":
            time_list = list(set(sta['time'].tolist()))
            year_list = []
            for time in time_list:
                year_list.append(time.year)
            year_list.sort()
            para_array['year'] = []
            for year in year_list:
                para_array['year'].append([year])
        else:
            para_array['year'] = copy.deepcopy(self.year)

        #
        if self.month == "fold":
            pass
        elif self.month =="unfold":
            time_list = list(set(sta['time'].tolist()))
            month_list = []
            for time in time_list:
                month_list.append(time.month)
            month_list.sort()
            para_array['month'] = []
            for month in month_list:
                para_array['month'].append([month])
        else:
            para_array['month'] = copy.deepcopy(self.month)


        #
        if self.month == "fold":
            pass
        elif self.month =="unfold":
            time_list = list(set(sta['time'].tolist()))
            month_list = []
            for time in time_list:
                month_list.append(time.month)
            month_list.sort()
            para_array['month'] = []
            for month in month_list:
                para_array['month'].append([month])
        else:
            para_array['month'] = copy.deepcopy(self.month)


        #
        if self.xun == "fold":
            pass
        elif self.xun =="unfold":
            time_list = list(set(sta['time'].tolist()))
            xun_list = []
            for time in time_list:
                month = time.month
                day = time.day
                xun1 = (month-1) * 3 + min(int(math.ceil(day / 10)),3)
                xun_list.append(xun1)
            xun_list.sort()
            para_array['xun'] = []
            for xun1 in xun_list:
                para_array['xun'].append([xun1])
        else:
            para_array['xun'] = copy.deepcopy(self.xun)

        #
        if self.hou == "fold":
            pass
        elif self.hou=="unfold":
            time_list = list(set(sta['time'].tolist()))
            hou_list = []
            for time in time_list:
                month = time.month
                day = time.day
                hou1 = (month-1) * 6 + min(int(math.ceil(day / 5)),6)
                hou_list.append(hou1)
            hou_list.sort()
            para_array['hou'] = []
            for hou1 in hou_list:
                para_array['hou'].append([hou1])
        else:
            para_array['hou'] = copy.deepcopy(self.hou)

        if self.day == "fold":
            pass
        elif self.day == "unfold":
            time_list = list(set(sta['time'].tolist()))
            day_list = []
            for time in time_list:
                day_list.append(time.dayofyear)
            day_list.sort()
            para_array['day'] = []
            for day1 in day_list:
                para_array['day'].append([day1])
        else:
            para_array['day'] = copy.deepcopy(self.day)



        #

        if self.dtime == 'fold':
            pass
        elif self.dtime == 'unfold':
            dtime_list = list(set(sta['dtime'].tolist()))
            dtime_list.sort()
            dtime_list2 = []
            for dtime in dtime_list:
                dtime_list2.append([dtime])
            para_array['dtime'] = dtime_list2
        else:
            para_array['dtime'] = copy.deepcopy(self.dtime)

        if self.dday == 'fold':
            pass
        elif self.dday == 'unfold':
            dtime_list = list(set(sta['dtime'].tolist()))
            dtime_list.sort()
            dtime_list2 = []
            for dtime in dtime_list:
                seconds = dtime/np.timedelta64(1, 's')
                days = math.ceil(seconds/(24*3600))
                dtime_list2.append([days])
            para_array['dday'] = dtime_list2
        else:
            para_array['dday'] = copy.deepcopy(self.dday)

        if self.dhour == 'fold':
            pass
        elif self.dhour == 'unfold':
            dtime_list = list(set(sta['dtime'].tolist()))
            dtime_list.sort()
            dtime_list2 = []
            for dtime in dtime_list:
                dtime = nmc_verification.nmc_vf_base.method.time_tools.all_type_timedelta_to_timedelta64(dtime)
                seconds = dtime/np.timedelta64(1, 's')
                hours = math.ceil(seconds/(3600))
                dtime_list2.append([hours])
            para_array['dhour'] = dtime_list2
        else:
            para_array['dhour'] = copy.deepcopy(self.dhour)

        if self.dminute == 'fold':
            pass
        elif self.dminute == 'unfold':
            dtime_list = list(set(sta['dtime'].tolist()))
            dtime_list.sort()
            dtime_list2 = []
            for dtime in dtime_list:
                seconds = dtime/np.timedelta64(1, 's')
                minutes = math.ceil(seconds/(60))
                dtime_list2.append([minutes])
            para_array['dminute'] = dtime_list2
        else:
            para_array['dminute'] = copy.deepcopy(self.dminute)
        #
        if self.id == 'fold':
            pass
        elif self.id == 'unfold':
            id_list = list(set(sta['id'].tolist()))
            id_list.sort()
            id_list2 = []
            for id in id_list:
                id_list2.append([id])
            para_array['id'] = id_list2
        else:
            para_array['id'] = copy.deepcopy(self.dtime)

        if self.lon == "fold":
            pass
        elif self.lon =="unfold":
            lons = sta['lon'].values
            slon = np.min(lons) - 0.001
            elon = np.max(lons) + 0.001
            dlon = (elon - slon)/10.0
            slon1 = slon
            elon1 = slon + dlon
            list_list = []
            while slon1 < elon:
                list_list.append([slon1, elon1])
                slon1 += dlon
                elon1 += dlon
            para_array['lon'] = list_list
        else:
            para_array['lon'] = copy.deepcopy(self.lon)

        #
        if self.lat == "fold":
            pass
        elif self.lat =="unfold":
            lats = sta['lat'].values
            slat = np.min(lats) - 0.001
            elat = np.max(lats) + 0.001
            dlat = (elat - slat)/10.0
            slat1 = slat
            elat1 = slat + dlat
            list_list = []
            while slat1 < elat:
                list_list.append([slat1, elat1])
                slat1 += dlat
                elat1 += dlat
            para_array['lat'] = list_list
        else:
            para_array['lat'] = copy.deepcopy(self.lat)

        #
        if self.alt == "fold":
            pass
        elif self.alt =="unfold":
            alts = sta['alt'].values
            salt = np.min(alts) - 0.001
            ealt = np.max(alts) + 0.001
            dalt = (ealt - salt)/10.0
            salt1 = salt
            ealt1 = salt + dalt
            list_list = []
            while salt1 < ealt:
                list_list.append([salt1, ealt1])
                salt1 += dalt
                ealt1 += dalt
            para_array['alt'] = list_list
        else:
            para_array['alt'] = copy.deepcopy(self.alt)
        self.para_dict_list_list = para_array

    def set_para_dict_list_string(self):
        # para_array 里 para_array[key] 里是一个[[]]结构，为了后续绘图等需求，需将内层[] 转换成string，
        # 例如 para_array['month'] = [[1,2,3],[4,5,6],[7,8,9],[10,11,12]] 需将[1,2,3] 转换为"1,2,3月"
        para_dict_list_string = {}
        for key in self.para_dict_list_list.keys():
            para_dict_list_string[key] = []
            list_list = self.para_dict_list_list[key]
            for list in list_list:
                if key == "dhour":
                    str1 = ""
                    for i in range(len(list)-1):
                        str1 += str(list[i]) + ","
                    str1 += str(list[-1])+"H"
                elif key == "":
                    pass
                else:
                    pass
                para_dict_list_string[key].append(str1)
        self.para_dict_list_string = para_dict_list_string


    def get_para_dict_list_list(self):
        self.set_para_dict_list_list()
        return self.para_dict_list_list

    def get_para_dict_list_string(self):
        self.set_para_dict_list_list()
        self.set_para_dict_list_string()
        return self.para_dict_list_string

    def get_sta_list(self):
        self.set_para_dict_list_list()
        self.set_para_dict_list_string()
        para_list = para_array_to_list(0, self.para_dict_list_list)
        sta_list = []
        for para in para_list:
            sta1 = get_sta_by_para(self.sta_data, para)
            #print(para)
            #print(sta1)
            sta_list.append(sta1)
        self.sta_list = sta_list
        return sta_list,self.para_dict_list_list,self.para_dict_list_string









