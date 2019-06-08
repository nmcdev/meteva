import copy
import nmc_verification.nmc_vf_base.method.time_tools as time_tools
import pandas as pd
import numpy as np
class plot_group:
    picture = "picture"
    subplot = "subplot"
    legend = "legend"
    axis_x = "axis_x"


class data_para:
    def __init__(self):
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
        self.id = "fold"
        self.lon = "fold"
        self.lat = "fold"
        self.alt = "fold"

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
                time_start = time_tools.all_type_time_to_time64(time_range[0])
                time_end = time_tools.all_type_time_to_time64(time_range[1])
                dtime = time_tools.all_type_timedelta_to_timedelta64(time_range[2])
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
        if month_list_list is None:
            self.month = "unfold"
        else:
            self.month = copy.deepcopy(month_list_list)

    def set_xun_unfold(self,xun_list_list = None):
        self.time = "fold"
        if xun_list_list is None:
            self.xun = "unfold"
        else:
            self.xun = copy.deepcopy(xun_list_list)

    def set_hou_unfold(self,hou_list_list = None):
        self.time = "fold"
        if hou_list_list is None:
            self.hou = "unfold"
        else:
            self.hou = copy.deepcopy(hou_list_list)

    def set_day_unfold(self,day_list_list = None):
        self.time = "fold"
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
        self.dhou = "fold"
        if dtime_list_list is not None:
            self.dtime = copy.deepcopy(dtime_list_list)
        elif dtime_range_list is not None:
            list_list = []
            for dtime_range in dtime_range_list:
                sdtime = time_tools.all_type_timedelta_to_timedelta64(dtime_range_list[0])
                edtime = time_tools.all_type_timedelta_to_timedelta64(dtime_range_list[1])
                ddtime = time_tools.all_type_timedelta_to_timedelta64(dtime_range_list[2])

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
        if dhour_list_list is None:
            self.dhour = "unfold"
        else:
            self.dhour = copy.deepcopy(dhour_list_list)

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
            self.lon = list_list
        elif lat_range_list is not None:
            self.alt = copy.deepcopy(lat_range_list)
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



    def get_dict_list_list(self,sta):

        para_dict = {}
        #
        if self.level == "fold":
            pass
        elif self.level=='unfold':
            level_list = list(set(sta['level'].tolist()))
            level_list.sort()
            level_list2 = []
            for level in level_list:
                level_list2.append([level])
            para_dict['level'] = level_list2
        else:
            para_dict['level'] = copy.deepcopy(self.level)

        #
        if self.time == 'fold':
            pass
        elif self.time == 'unfold':
            time_list = list(set(sta['time'].tolist()))
            time_list.sort()
            time_list2 = []
            for time in time_list:
                time_list2.append([time])
            para_dict['time'] = time_list2
        else:
            para_dict['time'] = copy.deepcopy(self.time)

        #
        if self.year == "fold":
            pass
        elif self.year =="unfold":
            time_list = list(set(sta['time'].tolist()))
            year_list = []
            for time in time_list:
                year_list.append(time.year)
            year_list.sort()
            para_dict['year'] = []
            for year in year_list:
                para_dict['year'].append([year])
        else:
            para_dict['year'] = copy.deepcopy(self.year)

        #
        if self.month == "fold":
            pass
        elif self.month =="unfold":
            time_list = list(set(sta['time'].tolist()))
            month_list = []
            for time in time_list:
                month_list.append(time.month)
            month_list.sort()
            para_dict['month'] = []
            for month in month_list:
                para_dict['month'].append([month])
        else:
            para_dict['month'] = copy.deepcopy(self.month)

        #
        if self.dtime == 'fold':
            pass
        elif self.dtime == 'unfold':
            dtime_list = list(set(sta['dtime'].tolist()))
            dtime_list.sort()
            dtime_list2 = []
            for dtime in dtime_list:
                dtime_list2.append([dtime])
            para_dict['dtime'] = dtime_list2
        else:
            para_dict['dtime'] = copy.deepcopy(self.dtime)

        if self.id == 'fold':
            pass
        elif self.id == 'unfold':
            id_list = list(set(sta['id'].tolist()))
            id_list.sort()
            id_list2 = []
            for id in id_list:
                id_list2.append([id])
            para_dict['id'] = id_list2
        else:
            para_dict['id'] = copy.deepcopy(self.dtime)

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
            para_dict['lon'] = list_list
        else:
            para_dict['lon'] = copy.deepcopy(self.lon)

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
            para_dict['lat'] = list_list
        else:
            para_dict['lat'] = copy.deepcopy(self.lat)

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
            para_dict['alt'] = list_list
        else:
            para_dict['alt'] = copy.deepcopy(self.alt)


        return para_dict
