import nmc_verification
import copy
import pandas as pd
import numpy as np
import math
import datetime

def between_value_range(sta,start_value,end_value,start_open = False,end_open = False):
    sta1 = sta
    data_names = nmc_verification.nmc_vf_base.basicdata.get_stadata_names(sta)
    for data_name in data_names:
        if start_open:
            if end_open:
                sta1 = sta1.loc[(sta1[data_name] > start_value) & (sta1[data_name] < end_value)]
            else:
                sta1 = sta1.loc[(sta1[data_name] > start_value) & (sta1[data_name] <= end_value)]
        else:
            if end_open:
                sta1 = sta1.loc[(sta1[data_name] >= start_value) & (sta1[data_name] < end_value)]
            else:
                sta1 = sta1.loc[(sta1[data_name] >= start_value) & (sta1[data_name] <= end_value)]
    return sta1
#为站点数据中dataframe重新赋列名

def not_IV(sta):
    data_names = nmc_verification.nmc_vf_base.get_stadata_names(sta)
    sta1 = sta.loc[sta[data_names[0]] != nmc_verification.nmc_vf_base.IV]
    for i in range(1,len(data_names),1):
        sta1 = sta1.loc[sta[data_names[i]] != nmc_verification.nmc_vf_base.IV]
    return sta1
def not_equal_to(sta,dele_value):
    data_names = nmc_verification.nmc_vf_base.get_stadata_names(sta)
    sta1 = sta.loc[sta[data_names[0]] != dele_value]
    for i in range(1,len(data_names),1):
        sta1 = sta1.loc[sta[data_names[i]] != dele_value]
    return sta1

#为拥有多元素值的站点数据，在最后依次增加要素值的列表名
def in_member_list(data,member_list,name_or_index = "name"):
    if isinstance(data, pd.DataFrame):
        member_name_list = []
        if name_or_index == "name":
            member_name_list = member_list
        else:
            data_names = nmc_verification.nmc_vf_base.get_stadata_names(data)
            for member in member_list:
                member_name_list.append(data_names[member])
        columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat'] + member_name_list
        sta1 = copy.deepcopy(data[columns])
        return sta1
    else:
        grid0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(data)
        num_list = []
        if name_or_index == "name":
            member_name_list = member_list
            for member_name in member_list:
                if member_name not in grid0.members:
                    print(member_name +" not exist in griddata's member_list")
                else:
                    for i in range(len(grid0.members)):
                        if member_name == grid0.members[i]:
                            num_list.append(i)
                            break

        else:
            member_name_list = []
            num_list = member_list
            for num in member_list:
                if num >= len(grid0.members):
                    print("网格数据member维度的size小于" + str(num))
                else:
                    member_name_list.append(grid0.members[num])
        dat = data.values[num_list, :, :, :, :, :]
        grid1 = nmc_verification.nmc_vf_base.basicdata.grid(grid0.glon, grid0.glat,
                                                            grid0.gtime, grid0.dtimes, grid0.levels,
                                                            member_list=member_name_list)
        grd1 = nmc_verification.nmc_vf_base.basicdata.grid_data(grid1, dat)
        return grd1

#为拥有多level层的站点数据，依次增加level层所表示的list列表
def in_level_list(sta,level_list):
    sta1 = sta.loc[sta['level'].isin(level_list)]
    return sta1

#为拥有多id的站点数据，依次增加id所表示的list列表
def in_id_list(sta,id_list):
    sta1 = sta.loc[sta['id'].isin(id_list)]
    return sta1


#为拥有多time层的站点数据，依次增加time层所表示的list列表
def in_time_list(sta,time_list):
    time_list1 = []
    for time0 in time_list:
        time_list1.append(nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_time64(time0))
    sta1 = sta.loc[sta['time'].isin(time_list1)]
    return sta1

#为拥有多year的站点数据，依次增加year所表示的list列表
def in_year_list(sta,year_list):
    years = sta['time'].map(lambda x: x.year)
    sta1 = sta.loc[years.isin(year_list)]
    return sta1

#为拥有多month的站点数据，依次增加month所表示的list列表
def in_month_list(sta,month_list):
    months = sta['time'].map(lambda x: x.month)
    sta1 = sta.loc[months.isin(month_list)]
    return sta1

#为拥有多xun的站点数据，依次增加xun所表示的list列表
def in_xun_list(sta,xun_list):
    mons = sta['time'].map(lambda x: x.month).values.astype(np.int16)
    days = sta['time'].map(lambda y: y.day).values
    xuns = np.ceil(days / 10).astype(np.int16)
    xuns[xuns>3] = 3
    xuns += (mons - 1) * 3
    xuns = pd.Series(xuns)
    sta1 = sta.loc[xuns.isin(xun_list)]
    return sta1

#为拥有多hou的站点数据，依次增加hou所表示的list列表
def in_hou_list(sta,hou_list):
    mons = sta['time'].map(lambda x: x.month).values.astype(np.int16)
    days = sta['time'].map(lambda y: y.day).values
    hous = np.ceil(days / 5).astype(np.int16)
    hous[hous>6] = 6
    hous += (mons - 1) * 6
    hous = pd.Series(hous)
    sta1 = sta.loc[hous.isin(hou_list)]
    return sta1

#为拥有多day的站点数据，依次增加day所表示的list列表
def in_day_list(sta,day_list):
    day_list1 = []
    for day0 in day_list:
        day1 = datetime.datetime(day0.year,day0.month,day0.day,0,0)
        day_list1.append(nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_time64(day1))
    days = sta['time'].map(lambda x: datetime.datetime(x.year,x.month,x.day,0,0))
    sta1 = sta.loc[days.isin(day_list)]
    return sta1

def in_dayofyear_list(sta,dayofyear_list):
    days = sta['time'].map(lambda x: x.dayofyear)
    sta1 = sta.loc[days.isin(dayofyear_list)]
    return sta1

#为拥有多hour的站点数据，依次增加hour所表示的list列表
def in_hour_list(sta,hour_list):
    hours = sta['time'].map(lambda x: x.hour)
    sta1 = sta.loc[hours.isin(hour_list)]
    return sta1


def between_time_range(sta,start_time,end_time):
    sta1 = sta.loc[(sta['time'] >= start_time) & (sta['time'] <= end_time)]
    return sta1

############
#为拥有多time层的站点数据，依次增加time层所表示的list列表
def in_ob_time_list(sta,time_list):
    time_list1 = []
    for time0 in time_list:
        time_list1.append(nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_time64(time0))
    dtimes = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
    obtimes = sta['time'] + dtimes
    sta1 = sta.loc[obtimes.isin(time_list1)]
    return sta1

#为拥有多year的站点数据，依次增加year所表示的list列表
def in_ob_year_list(sta,year_list):
    dtimes = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
    obtimes = sta['time'] + dtimes
    years = obtimes.map(lambda x: x.year)
    sta1 = sta.loc[years.isin(year_list)]
    return sta1

#为拥有多month的站点数据，依次增加month所表示的list列表
def in_ob_month_list(sta,month_list):
    dtimes = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
    obtimes = sta['time'] + dtimes
    months = obtimes.map(lambda x: x.month)
    sta1 = sta.loc[months.isin(month_list)]
    return sta1


#为拥有多xun的站点数据，依次增加xun所表示的list列表
def in_ob_xun_list(sta,xun_list):
    dtimes = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
    obtimes = sta['time'] + dtimes
    mons = obtimes.map(lambda x: x.month).values.astype(np.int16)
    days = obtimes.map(lambda y: y.day).values
    xuns = np.ceil(days / 10).astype(np.int16)
    xuns[xuns>3] = 3
    xuns += (mons - 1) * 3
    xuns = pd.Series(xuns)
    sta1 = sta.loc[xuns.isin(xun_list)]
    return sta1

#为拥有多hou的站点数据，依次增加hou所表示的list列表
def in_ob_hou_list(sta,hou_list):
    dtimes = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
    obtimes = sta['time'] + dtimes
    mons = obtimes.map(lambda x: x.month).values.astype(np.int16)
    days = obtimes.map(lambda y: y.day).values
    hous = np.ceil(days / 5).astype(np.int16)
    hous[hous>6] = 6
    hous += (mons - 1) * 6
    hous = pd.Series(hous)
    sta1 = sta.loc[hous.isin(hou_list)]
    return sta1

#为拥有多day的站点数据，依次增加day所表示的list列表
def in_ob_dayofyear_list(sta,dayofyear_list):
    dtimes = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
    obtimes = sta['time'] + dtimes
    days = obtimes.map(lambda x: x.dayofyear)
    sta1 = sta.loc[days.isin(dayofyear_list)]
    return sta1

def in_ob_day_list(sta,day_list):
    dtimes = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
    obtimes = sta['time'] + dtimes
    day_list1 = []
    for day0 in day_list:
        day1 = datetime.datetime(day0.year,day0.month,day0.day,0,0)
        day_list1.append(nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_time64(day1))
    days = obtimes.map(lambda x: datetime.datetime(x.year,x.month,x.day,0,0))
    sta1 = sta.loc[days.isin(day_list)]
    return sta1

#为拥有多hour的站点数据，依次增加hour所表示的list列表
def in_ob_hour_list(sta,hour_list):
    dtimes = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
    obtimes = sta['time'] + dtimes
    hours = obtimes.map(lambda x: x.hour)
    sta1 = sta.loc[hours.isin(hour_list)]
    return sta1


def between_ob_time_range(sta,start_time,end_time):
    dtimes = sta['dtime'].map(lambda x: datetime.timedelta(hours=x))
    obtimes = sta['time'] + dtimes
    sta1 = sta.loc[(obtimes  >= start_time) & (obtimes  <= end_time)]
    return sta1
############

#为拥有多dtime的站点数据，依次增加dtime所表示的list列表
def in_dtime_list(sta,dtime_list):
    sta1 = sta.loc[sta['dtime'].isin(dtime_list)]
    return sta1

#为拥有多dday的站点数据，依次增加dday所表示的list列表
def in_dday_list(sta,dday_list):
    days = sta['dtime'].map(lambda x: math.ceil(x/24))
    sta1 = sta.loc[days.isin(dday_list)]
    return sta1

#为拥有多dhour的站点数据，依次增加dhour所表示的list列表
def in_dhour_list(sta,dhour_list):
    hours = sta['dtime'].map(lambda x:  x % 24)
    sta1 = sta.loc[hours.isin(dhour_list)]
    return sta1

#为拥有多dminute的站点数据，依次增加minute所表示的list列表
def in_dminute_list(sta,dminute_list):
    minutes = sta['dtime'].map(lambda x: x - 10000)
    sta1 = sta.loc[minutes.isin(dminute_list)]
    return sta1

#返回的dtime在start_dtime和end_dtime之间
def between_dtime_range(sta,start_dtime,end_dtime):
    sta1 = sta.loc[(sta['dtime']>=start_dtime) & (sta['dtime']<= end_dtime)]
    return sta1

#返回的lon在slon和elon之间
def between_lon_range(sta,slon,elon):
    sta1 = sta.loc[(sta['lon']>=slon) & (sta['lon']<= elon)]
    return sta1


#返回的lat在slat和elat之间
def between_lat_range(sta,slat,elat):
    sta1 = sta.loc[(sta['lat']>=slat) & (sta['lat']<= elat)]
    return sta1

#返回的alt在salt和ealt之间
def between_level_range(sta,slevel,elevel):
    sta1 = sta.loc[(sta['level']>=slevel) & (sta['level']<= elevel)]
    return sta1

#返回站点经纬度正好落在格点中的站点信息
def in_grid_xy(sta,grid):
    sta1 = between_lon_range(sta,grid.slon,grid.elon)
    sta2 = between_lat_range(sta1,grid.slat,grid.elat)
    return sta2

def in_grid_xyz(sta,grid):
    sta1 = in_grid_xy(sta,grid)
    levels = np.array(grid.levels)
    levels.sort()
    sta2 = between_level_range(sta1,levels[0],levels[-1])
    return sta2

#返回站点参数字典列表
def by_loc_dict(sta,loc_dict):
    '''
    loc_dict 应具备如下样式
    loc_dict = {'member':["ecmwf","grapes"],列表形式
                'level' :[850,700],  列表形式,
                'time' : [datetime(2020,1,1,8,0)], 列表形式,
                "time_range":[datetime(2020,1,1,8,0),datetime(2020,1,2,8,0)], 闭区间,
                "year":[2020,2021],列表形式，
                "month": [1,2,3]，列表形式，
                "day": [datetime(2020,1,1,0,0)]列表形式，
                "dayofyear":[1,2,365,366] 列表形式，
                "hour":[0,1,23],列表形式，

                'ob_time' : [datetime(2020,1,1,8,0)], 列表形式,
                "ob_time_range":[datetime(2020,1,1,8,0),datetime(2020,1,2,8,0)], 闭区间,
                "ob_year":[2020,2021],列表形式，
                "ob_month": [1,2,3]，列表形式，
                "ob_day": [datetime(2020,1,1,0,0)]列表形式，
                "ob_dayofyear":[1,2,365,366] 列表形式，
                "ob_hour":[0,1,23],列表形式，

                'dtime':[24,36]，列表形式,
                'ddya': [0,1,2]，列表形式，
                "dhour":[0,1,23],列表形式，

                'id':[54511]， 列表形式,
                'lon': [70,140], 闭区间,
                'lat' :[10,60], 闭区间,
    }
    '''
    sta1 = sta
    if "member" in loc_dict.keys():
        sta1 = in_member_list(sta1,loc_dict["member"])
    if "level" in loc_dict.keys():
        sta1 = in_level_list(sta1,loc_dict['level'])
    if "time" in loc_dict.keys():
        sta1 = in_time_list(sta1, loc_dict['time'])
    if "time_range" in loc_dict.keys():
        sta1 = between_time_range(sta1, loc_dict['time_range'][0],loc_dict['time_range'][1])
    if "year" in loc_dict.keys():
        sta1 = in_year_list(sta1,loc_dict["year"])
    if "month" in loc_dict.keys():
        sta1 = in_month_list(sta1,loc_dict["month"])
    if "day" in loc_dict.keys():
        sta1 = in_day_list(sta1,loc_dict["day"])
    if "dayofyear" in loc_dict.keys():
        sta1 = in_dayofyear_list(sta1,loc_dict["dayofyear"])
    if "hour" in loc_dict.keys():
        sta1 = in_hour_list(sta1, loc_dict["hour"])

    if "ob_time" in loc_dict.keys():
        sta1 = in_ob_time_list(sta1, loc_dict['ob_time'])
    if "ob_time_range" in loc_dict.keys():
        sta1 = between_ob_time_range(sta1, loc_dict['ob_time_range'][0],loc_dict['ob_time_range'][1])
    if "ob_year" in loc_dict.keys():
        sta1 = in_ob_year_list(sta1,loc_dict["ob_year"])
    if "ob_month" in loc_dict.keys():
        sta1 = in_ob_month_list(sta1,loc_dict["ob_month"])
    if "ob_day" in loc_dict.keys():
        sta1 = in_ob_day_list(sta1,loc_dict["ob_day"])
    if "ob_dayofyear" in loc_dict.keys():
        sta1 = in_ob_dayofyear_list(sta1,loc_dict["ob_dayofyear"])
    if "ob_hour" in loc_dict.keys():
        sta1 = in_ob_hour_list(sta1, loc_dict["ob_hour"])

    if "lon" in loc_dict.keys():
        sta1 = between_lon_range(sta1,loc_dict["lon"][0],loc_dict["lon"][1])
    if "lat" in loc_dict.keys():
        sta1 = between_lat_range(sta1,loc_dict["lat"][0],loc_dict["lat"][1])
    if "id" in loc_dict.keys():
        sta1 = in_id_list(sta1,loc_dict["id"])
    return sta1




