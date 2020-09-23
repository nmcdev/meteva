import meteva
import pandas as pd
import numpy as np
import math
import datetime

def between_value_range(sta,start_value,end_value,start_open = False,end_open = False):
    sta1 = sta
    data_names = meteva.base.basicdata.get_stadata_names(sta)
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
    data_names = meteva.base.get_stadata_names(sta)
    sta1 = sta.loc[sta[data_names[0]] != meteva.base.IV]
    for i in range(1,len(data_names),1):
        sta1 = sta1.loc[sta[data_names[i]] != meteva.base.IV]
    return sta1
def not_equal_to(sta,dele_value):
    data_names = meteva.base.get_stadata_names(sta)
    sta1 = sta.loc[sta[data_names[0]] != dele_value]
    for i in range(1,len(data_names),1):
        sta1 = sta1.loc[sta[data_names[i]] != dele_value]
    return sta1

#为拥有多元素值的站点数据，在最后依次增加要素值的列表名
def in_member_list(data,member_list,name_or_index = "name"):
    if not isinstance(member_list,list) and not isinstance(member_list,np.ndarray):
        member_list = [member_list]
    if isinstance(data, pd.DataFrame):
        data_names = meteva.base.get_stadata_names(data)
        member_name_list = []
        if name_or_index == "name":
            for member in member_list:
                if member not in data_names:
                    print("error infomation: "+member +" is not a data column")
                    return
            member_name_list = member_list
        else:
            data_names = meteva.base.get_stadata_names(data)
            for member in member_list:
                member_name_list.append(data_names[member])
        columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat'] + member_name_list
        sta1 = data.loc[:,columns]
        return sta1
    else:
        grid0 = meteva.base.basicdata.get_grid_of_data(data)
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
        grid1 = meteva.base.basicdata.grid(grid0.glon, grid0.glat,
                                                            grid0.gtime, grid0.dtimes, grid0.levels,
                                                            member_list=member_name_list)
        grd1 = meteva.base.basicdata.grid_data(grid1, dat)
        return grd1

#为拥有多level层的站点数据，依次增加level层所表示的list列表

#为拥有多level层的站点数据，依次增加level层所表示的list列表
def in_level_list(data,level_list):
    if not isinstance(level_list,list) and not isinstance(level_list,np.ndarray):
        level_list = [level_list]

    if isinstance(data, pd.DataFrame):
        sta1 = data.loc[data['level'].isin(level_list)]
        return sta1
    else:
        grid0 = meteva.base.basicdata.get_grid_of_data(data)
        num_list = []
        level_list1 = []
        for level in level_list:
            if level not in grid0.levels:
                print(level +" not exist in griddata's level_list")
            else:
                for i in range(len(grid0.levels)):
                    if level == grid0.levels[i]:
                        num_list.append(i)
                        level_list1.append(level)
                        break

        dat = data.values[:, num_list, :, :, :, :]

        grid1 = meteva.base.basicdata.grid(grid0.glon, grid0.glat,
                                                            grid0.gtime, grid0.dtimes,level_list = level_list1,
                                                            member_list = grid0.members)
        grd1 = meteva.base.basicdata.grid_data(grid1, dat)
        return grd1

#为拥有多id的站点数据，依次增加id所表示的list列表
def in_id_list(sta,id_list):
    if not isinstance(id_list,list) and not isinstance(id_list,np.ndarray):
        id_list = [id_list]
    sta1 = sta.loc[sta['id'].isin(id_list)]
    return sta1


#为拥有多time层的站点数据，依次增加time层所表示的list列表
def in_time_list(sta,time_list):
    if not isinstance(time_list,list) and not isinstance(time_list,np.ndarray):
        time_list = [time_list]
    time_list1 = []

    for time0 in time_list:
        time_list1.append(meteva.base.tool.time_tools.all_type_time_to_time64(time0))
    sta1 = sta.loc[sta['time'].isin(time_list1)]
    return sta1



#为拥有多year的站点数据，依次增加year所表示的list列表
def in_year_list(sta,year_list):
    if not isinstance(year_list,list) and not isinstance(year_list,np.ndarray):
        year_list = [year_list]
    fo_times = pd.Series(0, index=sta['time'])
    sta1 = sta.loc[fo_times.index.year.isin(year_list)]
    return sta1

#为拥有多month的站点数据，依次增加month所表示的list列表
def in_month_list(sta,month_list):
    if not isinstance(month_list,list) and not isinstance(month_list,np.ndarray):
        month_list = [month_list]
    fo_times = pd.Series(0, index=sta['time'])
    sta1 = sta.loc[fo_times.index.month.isin(month_list)]
    return sta1

#为拥有多xun的站点数据，依次增加xun所表示的list列表
def in_xun_list(sta,xun_list):
    if not isinstance(xun_list,list) and not isinstance(xun_list,np.ndarray):
        xun_list = [xun_list]
    fo_times = pd.Series(0, index=sta['time'])
    mons = fo_times.index.month.astype(np.int16)
    days = fo_times.index.day.astype(np.int16)
    xuns = np.ceil(days / 10).values.astype(np.int16)
    xuns[xuns>3] = 3
    xuns += (mons - 1) * 3
    xuns = pd.Series(xuns)
    sta1 = sta.loc[xuns.isin(xun_list)]
    return sta1

#为拥有多hou的站点数据，依次增加hou所表示的list列表
def in_hou_list(sta,hou_list):
    if not isinstance(hou_list,list) and not isinstance(hou_list,np.ndarray):
        hou_list = [hou_list]
    fo_times = pd.Series(0, index=sta['time'])
    mons = fo_times.index.month.astype(np.int16)
    days = fo_times.index.day.astype(np.int16)
    hous = np.ceil(days / 5).values.astype(np.int16)
    hous[hous>6] = 6
    hous += (mons - 1) * 6
    hous = pd.Series(hous)
    sta1 = sta.loc[hous.isin(hou_list)]
    return sta1

#为拥有多day的站点数据，依次增加day所表示的list列表
def in_day_list(sta,day_list):
    if not isinstance(day_list,list) and not isinstance(day_list,np.ndarray):
        day_list = [day_list]
    days_list = []
    time0 = datetime.datetime(1900,1,1,0,0)
    seconds = 3600*24
    for day0 in day_list:
        if isinstance(day0,str):
            day0 = meteva.base.tool.time_tools.all_type_time_to_datetime(day0)
        day = (day0 - time0).total_seconds()//seconds
        days_list.append(day)
    indexs = (sta['time'] - time0)//np.timedelta64(1,"D")
    sta1 = sta.loc[indexs.isin(days_list)]
    return sta1

def in_dayofyear_list(sta,dayofyear_list):
    if not isinstance(dayofyear_list,list) and not isinstance(dayofyear_list,np.ndarray):
        dayofyear_list = [dayofyear_list]
    fo_times = pd.Series(0, index=sta['time'])
    sta1 = sta.loc[fo_times.index.dayofyear.isin(dayofyear_list)]
    return sta1

#为拥有多hour的站点数据，依次增加hour所表示的list列表
def in_hour_list(sta,hour_list):
    if not isinstance(hour_list,list) and not isinstance(hour_list,np.ndarray):
        hour_list = [hour_list]
    fo_times = pd.Series(0, index=sta['time'])
    sta1 = sta.loc[fo_times.index.hour.isin(hour_list)]
    return sta1


def between_time_range(sta,start_time,end_time):
    start_time = meteva.base.all_type_time_to_time64(start_time)
    end_time = meteva.base.all_type_time_to_time64(end_time)
    sta1 = sta.loc[(sta['time'] >= start_time) & (sta['time'] <= end_time)]
    return sta1

############
#为拥有多time层的站点数据，依次增加time层所表示的list列表
def in_ob_time_list(sta,time_list):
    if not isinstance(time_list,list) and not isinstance(time_list,np.ndarray):
        time_list = [time_list]
    time_list1 = []
    for time0 in time_list:
        time_list1.append(meteva.base.tool.time_tools.all_type_time_to_time64(time0))
    dtimes = sta["dtime"] * np.timedelta64(1, 'h')
    obtimes = sta['time'] + dtimes
    sta1 = sta.loc[obtimes.isin(time_list1)]
    return sta1

#为拥有多year的站点数据，依次增加year所表示的list列表
def in_ob_year_list(sta,year_list):
    if not isinstance(year_list,list) and not isinstance(year_list,np.ndarray):
        year_list = [year_list]
    dtimes = sta["dtime"] * np.timedelta64(1, 'h')
    obtimes = pd.Series(0,index = sta['time'] + dtimes)
    sta1 = sta.loc[obtimes.index.year.isin(year_list)]
    return sta1

#为拥有多month的站点数据，依次增加month所表示的list列表
def in_ob_month_list(sta,month_list):
    if not isinstance(month_list,list) and not isinstance(month_list,np.ndarray):
        month_list = [month_list]
    dtimes = sta["dtime"] * np.timedelta64(1, 'h')
    obtimes = pd.Series(0,index = sta['time'] + dtimes)
    sta1 = sta.loc[obtimes.index.month.isin(month_list)]
    return sta1


#为拥有多xun的站点数据，依次增加xun所表示的list列表
def in_ob_xun_list(sta,xun_list):
    if not isinstance(xun_list,list) and not isinstance(xun_list,np.ndarray):
        xun_list = [xun_list]
    dtimes = sta["dtime"] * np.timedelta64(1, 'h')
    obtimes = pd.Series(0,index = sta['time'] + dtimes)
    mons = obtimes.index.month.astype(np.int16)
    days = obtimes.index.day.astype(np.int16)
    xuns = np.ceil(days / 10).values.astype(np.int16)
    xuns[xuns>3] = 3
    xuns += (mons - 1) * 3
    xuns = pd.Series(xuns)
    sta1 = sta.loc[xuns.isin(xun_list)]
    return sta1

#为拥有多hou的站点数据，依次增加hou所表示的list列表
def in_ob_hou_list(sta,hou_list):
    if not isinstance(hou_list,list) and not isinstance(hou_list,np.ndarray):
        hou_list = [hou_list]
    dtimes = sta["dtime"] * np.timedelta64(1, 'h')
    obtimes = pd.Series(0,index = sta['time'] + dtimes)
    mons = obtimes.index.month.astype(np.int16)
    days = obtimes.index.day.astype(np.int16)
    hous = np.ceil(days / 5).values.astype(np.int16)
    hous[hous>6] = 6
    hous += (mons - 1) * 6
    hous = pd.Series(hous)
    sta1 = sta.loc[hous.isin(hou_list)]
    return sta1

#为拥有多day的站点数据，依次增加day所表示的list列表
def in_ob_dayofyear_list(sta,dayofyear_list):
    if not isinstance(dayofyear_list,list) and not isinstance(dayofyear_list,np.ndarray):
        dayofyear_list = [dayofyear_list]
    dtimes = sta["dtime"] * np.timedelta64(1, 'h')
    obtimes = pd.Series(0,index = sta['time'] + dtimes)
    sta1 = sta.loc[obtimes.index.dayofyear.isin(dayofyear_list)]
    return sta1

def in_ob_day_list(sta,day_list):
    if not isinstance(day_list,list) and not isinstance(day_list,np.ndarray):
        day_list = [day_list]
    dtimes = sta["dtime"] * np.timedelta64(1, 'h')
    obtimes = sta['time'] + dtimes
    days_list = []
    time0 = datetime.datetime(1900, 1, 1, 0, 0)
    seconds = 3600 * 24
    for day0 in day_list:
        if isinstance(day0,str):
            day0 = meteva.base.tool.time_tools.all_type_time_to_datetime(day0)
        day = (day0 - time0).total_seconds() // seconds
        days_list.append(day)
    indexs = (obtimes - time0) // np.timedelta64(1, "D")
    sta1 = sta.loc[indexs.isin(days_list)]
    return sta1



#为拥有多hour的站点数据，依次增加hour所表示的list列表
def in_ob_hour_list(sta,hour_list):
    if not isinstance(hour_list,list) and not isinstance(hour_list,np.ndarray):
        hour_list = [hour_list]
    dtimes = sta["dtime"] * np.timedelta64(1, 'h')
    obtimes = pd.Series(0,index = sta['time'] + dtimes)
    sta1 = sta.loc[obtimes.index.hour.isin(hour_list)]
    return sta1


def between_ob_time_range(sta,start_time,end_time):
    start_time = meteva.base.tool.time_tools.all_type_time_to_time64(start_time)
    end_time = meteva.base.tool.time_tools.all_type_time_to_time64(end_time)

    dtimes = sta["dtime"] * np.timedelta64(1, 'h')
    obtimes = sta['time'] + dtimes
    sta1 = sta.loc[(obtimes  >= start_time) & (obtimes  <= end_time)]
    return sta1
############

#为拥有多dtime的站点数据，依次增加dtime所表示的list列表
def in_dtime_list(data,dtime_list):
    if not isinstance(dtime_list,list) and not isinstance(dtime_list,np.ndarray):
        dtime_list = [dtime_list]
    if isinstance(data, pd.DataFrame):
        sta1 = data.loc[data['dtime'].isin(dtime_list)]
        return sta1
    else:
        grid0 = meteva.base.basicdata.get_grid_of_data(data)
        num_list = []
        dtime_list1 = []
        for dtime in dtime_list:
            if dtime not in grid0.dtimes:
                print(dtime +" not exist in griddata's dtime_list")
            else:
                for i in range(len(grid0.dtimes)):
                    if dtime == grid0.levels[i]:
                        num_list.append(i)
                        dtime_list1.append(dtime)
                        break

        dat = data.values[:, :, :, num_list, :, :]

        grid1 = meteva.base.basicdata.grid(grid0.glon, grid0.glat,
                                                            grid0.gtime, dtime_list=dtime_list1,level_list = grid0.levels,
                                                            member_list = grid0.members)
        grd1 = meteva.base.basicdata.grid_data(grid1, dat)
        return grd1

#为拥有多dday的站点数据，依次增加dday所表示的list列表
def in_dday_list(sta,dday_list):
    if not isinstance(dday_list,list) and not isinstance(dday_list,np.ndarray):
        dday_list = [dday_list]
    days = np.ceil(sta['dtime'] / 24)
    sta1 = sta.loc[days.isin(dday_list)]
    return sta1

#为拥有多dhour的站点数据，依次增加dhour所表示的list列表
def in_dhour_list(sta,dhour_list):
    if not isinstance(dhour_list,list) and not isinstance(dhour_list,np.ndarray):
        dhour_list = [dhour_list]
    hours = sta['dtime']% 24
    sta1 = sta.loc[hours.isin(dhour_list)]
    return sta1

#为拥有多dminute的站点数据，依次增加minute所表示的list列表
def in_dminute_list(sta,dminute_list):
    if not isinstance(dminute_list,list) and not isinstance(dminute_list,np.ndarray):
        dminute_list = [dminute_list]
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

def in_grid(sta,grid):
    sta1 = sta
    if grid.stime != grid.etime:
        sta1 = between_time_range(sta1,grid.stime,grid.etime)
    if len(grid.levels)>1:
        levels = np.array(grid.levels)
        levels.sort()
        sta1 = between_level_range(sta1, levels[0], levels[-1])
    if len(grid.dtimes)>1:
        dtimes = np.array(grid.dtimes)
        dtimes.sort()
        sta1 = between_dtime_range(sta1, dtimes[0], dtimes[-1])

    if grid.nlon>1:
        sta1 = between_lon_range(sta1, grid.slon, grid.elon)
    if grid.nlat>1:
        sta1 = between_lat_range(sta1, grid.slat, grid.elat)

    return sta1


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


def in_last_list(sta,last_list,drop_last = True):
    if not isinstance(last_list,list) and not isinstance(last_list,np.ndarray):
        last_list = [last_list]
    columns = list(sta.columns)
    sta1 = sta.loc[sta[columns[-1]].isin(last_list)]
    if drop_last:
        sta1 = sta1.loc[:, columns[0:-1]]
    return sta1

def between_last_range(sta,last_min,last_max,drop_last = True):
    columns = list(sta.columns)
    sta1 = sta.loc[(sta[columns[-1]] >= last_min) & (sta[columns[-1]] <= last_max)]
    if drop_last:
        sta1 = sta1.loc[:, columns[0:-1]]
    return  sta1
def by_stadata(sta,loc_sta):
    '''

    :param sta:
    :param loc_sta:
    :return:
    '''
    sta_combine = meteva.base.combine_expand_IV(sta,loc_sta)
    columns = list(sta_combine.columns)
    sta_sele = sta_combine.loc[:,columns[0:-1]]
    return sta_sele

def in_province_list(sta,province_name_list):
    if not isinstance(province_name_list,list):
        province_name_list = [province_name_list]
    ids = list(set(sta["id"].values))
    sta_province_name = meteva.base.tool.get_station_format_province_set(ids)
    sta_with_province_name = meteva.base.combine_expand_IV(sta, sta_province_name)
    sta1 = sta_with_province_name.loc[sta_with_province_name['province_name'].isin(province_name_list)]
    sta1 = sta1.drop(['province_name'], axis=1)

    return sta1



#返回站点参数字典列表
def by_loc_dict(data,s):
    '''
    s 应具备如下样式
    s = {'member':["ecmwf","grapes"],列表形式
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
                "stadata": 站点形式数据
    }
    '''
    if isinstance(data,pd.DataFrame):
        if s is None:return data
        sta1 = data
        if "member" in s.keys():
            sta1 = in_member_list(sta1,s["member"])
        if "level" in s.keys():
            sta1 = in_level_list(sta1,s['level'])
        if "time" in s.keys():
            sta1 = in_time_list(sta1, s['time'])
        if "time_range" in s.keys():
            if not isinstance(s['time_range'],list):
                print("time_range参数需为列表形式的包含起始时刻和结束时刻的时间参数，时间可以是datetime格式，datetime64或者字符串形式（例如2019010108）")
            sta1 = between_time_range(sta1, s['time_range'][0],s['time_range'][1])
        if "year" in s.keys():
            sta1 = in_year_list(sta1,s["year"])
        if "month" in s.keys():
            sta1 = in_month_list(sta1,s["month"])
        if "day" in s.keys():
            sta1 = in_day_list(sta1,s["day"])
        if "date" in s.keys():
            sta1 = in_day_list(sta1,s["date"])
        if "dayofyear" in s.keys():
            sta1 = in_dayofyear_list(sta1,s["dayofyear"])
        if "hour" in s.keys():
            sta1 = in_hour_list(sta1, s["hour"])

        if "ob_time" in s.keys():
            sta1 = in_ob_time_list(sta1, s['ob_time'])
        if "ob_time_range" in s.keys():
            if not isinstance(s['ob_time_range'], list):
                print("ob_time_range参数需为列表形式的包含起始时刻和结束时刻的时间参数，时间可以是datetime格式，datetime64或者字符串形式（例如2019010108）")
            sta1 = between_ob_time_range(sta1, s['ob_time_range'][0],s['ob_time_range'][1])
        if "ob_year" in s.keys():
            sta1 = in_ob_year_list(sta1,s["ob_year"])
        if "ob_month" in s.keys():
            sta1 = in_ob_month_list(sta1,s["ob_month"])
        if "ob_day" in s.keys():
            sta1 = in_ob_day_list(sta1,s["ob_day"])
        if "ob_dayofyear" in s.keys():
            sta1 = in_ob_dayofyear_list(sta1,s["ob_dayofyear"])
        if "ob_hour" in s.keys():
            sta1 = in_ob_hour_list(sta1, s["ob_hour"])

        if "dtime" in s.keys():
            sta1 = in_dtime_list(sta1,s["dtime"])
        if "dtime_range" in s.keys():
            sta1 = between_dtime_range(sta1, s["dtime_range"][0],s["dtime_range"][1])
        if "dday" in s.keys():
            sta1 = in_dday_list(sta1,s["dday"])
        if "dhour" in s.keys():
            sta1 = in_dday_list(sta1,s["dhour"])
        if "lon" in s.keys():
            sta1 = between_lon_range(sta1,s["lon"][0],s["lon"][1])
        if "lat" in s.keys():
            sta1 = between_lat_range(sta1,s["lat"][0],s["lat"][1])
        if "id" in s.keys():
            sta1 = in_id_list(sta1,s["id"])


        return sta1



#返回站点参数字典列表
def sele_by_dict(data,s):
    '''
    :param data: [站点数据](https://www.showdoc.cc/nmc?page_id=3744334022014027)
    :param s:用于选择的数据的参数字典，它具备如下形式
    s = {    "member":成员的名称，同时提取多个时采用列表形式
                    "level":层次的名称，同时提取多个时采用列表形式
                    "time":时间（以起报时刻为准），可以是datetime,datetime64或“2019010108”类似的字符串形式，同时提取多个时采用列表形式
                    "time_range":时间范围，列表形式，第一个元素为起始时间，第二个为结束时间，时间可以是datetime,datetime64或“2019010108”类似的字符串形式
                    "year":要提取的数据的年份（以起报时刻为准），同时提取多个时采用列表形式
                    "month":要提取的数据的月份（以起报时刻为准），同时提取多个时采用列表形式
                    "day":要提取的数据的日期（以起报时刻为准），可以是datetime,datetime64或“20190101”类似的字符串形式，同时提取多个时采用列表形式
                    "dayofyear":要提取的数据在一年中的排序（以起报时刻为准），整数形式，同时提取多个时采用列表形式
                    "hour":要提取的数据的小时数（以起报时刻为准），0-23的整数，同时提取多个时采用列表形式
                    "ob_time":时间（以观测时刻为准），可以是datetime,datetime64或“2019010108”类似的字符串形式，同时提取多个时采用列表形式
                    "ob_time_range":时间范围，列表形式，第一个元素为起始时间，第二个为结束时间，时间可以是datetime,datetime64或“2019010108”类似的字符串形式
                    "ob_year":要提取的数据的年份（以观测时刻为准），同时提取多个时采用列表形式
                    "ob_month":要提取的数据的月份（以观测时刻为准），同时提取多个时采用列表形式
                    "ob_day":要提取的数据的日期（以观测时刻为准），可以是datetime,datetime64或“20190101”类似的字符串形式，同时提取多个时采用列表形式
                    "ob_dayofyear":要提取的数据在一年中的排序（以观测时刻为准），整数形式，同时提取多个时采用列表形式
                    "ob_hour":要提取的数据的小时数（以观测时刻为准），0-23的整数，同时提取多个时采用列表形式
                    "dtime":要提取的数据的时效，整数形式，同时提取多个是采用列表形式
                    "dtime_range":时间范围，列表形式，第一个元素为起始时效，第二个为结束时效
                    "dday":  要提取的数据的时效dtime整除以24的值，整数形式，同时提取多个时采用列表形式
                    "dhour":要提取的数据的时效dtime除24的余数，整数形式，同时提取多个时采用列表形式
                    "lon":要提取的数据的经度范围，列表形式，第一个元素为起始经度，第二个为结束经度
                    "lat":要提取的数据的纬度范围，列表形式，第一个元素为起始经度，第二个为结束经度
                    "id": 要提取的数据的站号，同时提取多个是采用列表形式
                    "gxy": 提取某个平面网格范围内的数据
                    "gxyz": 提取某个三维网格范围内的数据
                    "stadata": 对于stadata中level，time，dtime，id四个坐标中非缺省的部分，从data中提取和stadata坐标一致的站点数据
                    "value": 提取所有数据列都在给定取值范围的数据，列表形式第一个元素为数据最低值，第二个为数据最高值
                    "drop_IV": 该参数为True时，删除包含缺省值的行
                    "last_range":包含起始值和结束值的列表，取出最后一列取值在该取值范围的数据，并删除最后一列的数据
                    "last": 取出最后一列包含lastL的行，如何选择多个类型，lastL采用列表形式，并删除最后一列的数据

    }
    '''
    if s is None:return data

    p_set = {"member","level","time","time_range","year","month","day","dayofyear","hour", "ob_time","ob_time_range" ,"ob_year",
              "ob_month", "ob_day","ob_dayofyear","ob_hour","dtime","dtime_range","dday","dhour" ,
              "lon","lat", "id","grid","gxy", "gxyz" ,"stadata","value","drop_IV","last" , "last_range","drop_last","province_name"}

    key_set = s.keys() #set(list(s.keys()))
    if(not p_set >= key_set):
        print("参数s的字典中包含本程序不能识别的关键词")
        return None

    member = None
    if "member" in s.keys():
        member = s["member"]
        
    level = None
    if "level" in s.keys():
        level = s['level']
    
    time = None
    if "time" in s.keys():
        time = s['time']

    time_range = None
    if "time_range" in s.keys():
        time_range = s["time_range"]

    year = None
    if "year" in s.keys():
        year = s["year"]

    month = None
    if "month" in s.keys():
        month = s["month"]

    day = None
    if "day" in s.keys():
        day = s["day"]

    dayofyear = None
    if "dayofyear" in s.keys():
        dayofyear = s["dayofyear"]

    hour = None
    if "hour" in s.keys():
        hour = s["hour"]

    ob_time = None
    if "ob_time" in s.keys():
        ob_time = s['ob_time']

    ob_time_range = None
    if "ob_time_range" in s.keys():
        ob_time_range = s['ob_time_range']

    ob_year = None
    if "ob_year" in s.keys():
        ob_year = s["ob_year"]

    ob_month = None
    if "ob_month" in s.keys():
        ob_month = s["ob_month"]

    ob_day = None
    if "ob_day" in s.keys():
        ob_day = s["ob_day"]

    ob_dayofyear = None
    if "ob_dayofyear" in s.keys():
        ob_dayofyear = s["ob_dayofyear"]

    ob_hour = None
    if "ob_hour" in s.keys():
        ob_hour = s["ob_hour"]

    dtime = None
    if "dtime" in s.keys():
        dtime = s["dtime"]

    dtime_range = None
    if "dtime_range" in s.keys():
        dtime_range = s["dtime_range"]

    dday = None
    if "dday" in s.keys():
        dday = s["dday"]

    dhour = None
    if "dhour" in s.keys():
        dhour = s["dhour"]

    lon = None
    if "lon" in s.keys():
        lon = s["lon"]

    lat = None
    if "lat" in s.keys():
        lat = s["lat"]

    id = None
    if "id" in s.keys():
        id = s["id"]

    stadata = None
    if "stadata" in s.keys():
        stadata = s["stadata"]


    grid = None
    if "grid" in s.keys():
        grid = s["grid"]

    gxy = None
    if "gxy" in s.keys():
        gxy = s["gxy"]

    gxyz = None
    if "gxyz" in s.keys():
        gxyz = s["gxyz"]

    value = None
    if "value" in s.keys():
        value = s["value"]

    drop_IV = False
    if "drop_IV" in s.keys():
        drop_IV = s["drop_IV"]

    last = None
    if "last" in s.keys():
        last = s["last"]

    last_range = None
    if "last_range" in s.keys():
        last_range = s["last_range"]

    province_name = None
    if "province_name" in s.keys():
        province_name = s["province_name"]

    drop_last = True
    if "drop_last" in s.keys():
        drop_last = s["drop_last"]






    sta1 = sele_by_para(data,member,level,time,time_range,year,month,day,dayofyear,hour,ob_time,ob_time_range,ob_year,ob_month,ob_day,ob_dayofyear,
                 ob_hour,dtime,dtime_range,dday,dhour,lon,lat,id,grid,gxy,gxyz,stadata,value,drop_IV,last,last_range,province_name,drop_last)
    return sta1


def sele_by_para(data,member = None,level = None,time = None,time_range = None,year = None,month = None,day = None,dayofyear = None,hour = None,
           ob_time=None, ob_time_range=None, ob_year=None, ob_month=None, ob_day=None, ob_dayofyear=None, ob_hour=None,
           dtime = None,dtime_range = None,dday = None, dhour = None,lon = None,lat = None,id = None,grid = None,gxy = None,gxyz = None,stadata = None,
                 value = None,drop_IV = False,last = None,last_range = None,province_name = None,drop_last = True):
    '''
    :param data: [站点数据](https://www.showdoc.cc/nmc?page_id=3744334022014027)
    :param member:成员的名称，同时提取多个时采用列表形式
    :param level:层次的名称，同时提取多个时采用列表形式
    :param time:时间（以起报时刻为准），可以是datetime,datetime64或“2019010108”类似的字符串形式，同时提取多个时采用列表形式
    :param time_range:时间范围，列表形式，第一个元素为起始时间，第二个为结束时间，时间可以是datetime,datetime64或“2019010108”类似的字符串形式
    :param year:要提取的数据的年份（以起报时刻为准），同时提取多个时采用列表形式
    :param month:要提取的数据的月份（以起报时刻为准），同时提取多个时采用列表形式
    :param day:要提取的数据的日期（以起报时刻为准），可以是datetime,datetime64或“20190101”类似的字符串形式，同时提取多个时采用列表形式
    :param dayofyear:要提取的数据在一年中的排序（以起报时刻为准），整数形式，同时提取多个时采用列表形式
    :param hour:要提取的数据的小时数（以起报时刻为准），0-23的整数，同时提取多个时采用列表形式
    :param ob_time:时间（以观测时刻为准），可以是datetime,datetime64或“2019010108”类似的字符串形式，同时提取多个时采用列表形式
    :param ob_time_range:时间范围，列表形式，第一个元素为起始时间，第二个为结束时间，时间可以是datetime,datetime64或“2019010108”类似的字符串形式
    :param ob_year:要提取的数据的年份（以观测时刻为准），同时提取多个时采用列表形式
    :param ob_month:要提取的数据的月份（以观测时刻为准），同时提取多个时采用列表形式
    :param ob_day:要提取的数据的日期（以观测时刻为准），可以是datetime,datetime64或“20190101”类似的字符串形式，同时提取多个时采用列表形式
    :param ob_dayofyear:要提取的数据在一年中的排序（以观测时刻为准），整数形式，同时提取多个时采用列表形式
    :param ob_hour:要提取的数据的小时数（以观测时刻为准），0-23的整数，同时提取多个时采用列表形式
    :param dtime:要提取的数据的时效，整数形式，同时提取多个是采用列表形式
    :param dtime_range:时间范围，列表形式，第一个元素为起始时效，第二个为结束时效
    :param dday:  要提取的数据的时效dtime整除以24的值，整数形式，同时提取多个时采用列表形式
    :param dhour: 要提取的数据的时效dtime除24的余数，整数形式，同时提取多个时采用列表形式
    :param lon:要提取的数据的经度范围，列表形式，第一个元素为起始经度，第二个为结束经度
    :param lat:要提取的数据的纬度范围，列表形式，第一个元素为起始经度，第二个为结束经度
    :param id: 要提取的数据的站号，同时提取多个是采用列表形式
    :param grid: 网格信息类变量，提取多维矩形网格范围内的数据，grid中size>1的维度的坐标范围会被用作选择的已经，size=1的维度会被忽略
    :param gxy: 网格信息类变量，采用其中经纬度范围提取水平矩形网格范围内的数据
    :param gxyz: 网格信息类变量，采用其中经纬度和层次范围提取三维矩形网格范围内的数据
    :param stadata: 站点数据类变量，对于stadata中level，time，dtime，id四个坐标中非缺省的部分，从data中提取和stadata坐标一致的站点数据
    :param value: 提取所有数据列都在给定取值范围的数据，列表形式，第一个元素为数据最低值，第二个为数据最高值
    :param drop_IV: 该参数为True时，删除包含缺省值的行
    :param last_range: 包含起始值和结束值的列表，取出最后一列取值在该取值范围的数据，并删除最后一列的数据
    :param last: 取出最后一列包含lastL的行，如何选择多个类型，lastL采用列表形式，并删除最后一列的数据
    :return:  [站点数据](https://www.showdoc.cc/nmc?page_id=3744334022014027)
    '''
    sta1 = data
    if member is not None:
        sta1 = in_member_list(sta1,member)
    if level is not None:
        sta1 = in_level_list(sta1,level)
    if time is not None:
        sta1 = in_time_list(sta1, time)
    if time_range is not None:
        if not isinstance(time_range,list):
            print("time_range参数需为列表形式的包含起始时刻和结束时刻的时间参数，时间可以是datetime格式，datetime64或者字符串形式（例如2019010108）")
        sta1 = between_time_range(sta1, time_range[0],time_range[1])
    if year is not None:
        sta1 = in_year_list(sta1,year)
    if month is not None:
        sta1 = in_month_list(sta1,month)
    if day is not None:
        sta1 = in_day_list(sta1,day)
    if dayofyear is not None:
        sta1 = in_dayofyear_list(sta1,dayofyear)
    if hour is not None:
        sta1 = in_hour_list(sta1, hour)
    if ob_time is not None:
        sta1 = in_ob_time_list(sta1, ob_time)
    if ob_time_range is not None:
        if not isinstance(ob_time_range,list):
            print("ob_time_range参数需为列表形式的包含起始时刻和结束时刻的时间参数，时间可以是datetime格式，datetime64或者字符串形式（例如2019010108）")
        sta1 = between_ob_time_range(sta1, ob_time_range[0],ob_time_range[1])
    if ob_year is not None:
        sta1 = in_ob_year_list(sta1,ob_year)
    if ob_month is not None:
        sta1 = in_ob_month_list(sta1,ob_month)
    if ob_day is not None:
        sta1 = in_ob_day_list(sta1,ob_day)
    if ob_dayofyear is not None:
        sta1 = in_ob_dayofyear_list(sta1,ob_dayofyear)
    if ob_hour is not None:
        sta1 = in_ob_hour_list(sta1, ob_hour)
    if dtime is not None:
        sta1 = in_dtime_list(sta1,dtime)
    if dtime_range is not None:
        if not isinstance(dtime_range,list):
            print("dtime_range参数需为列表形式的包含起始时效（整数）和结束时效（整数）的参数")
        sta1 = between_dtime_range(sta1, dtime_range[0],dtime_range[1])
    if dday is not None:
        sta1 = in_dday_list(sta1,dday)
    if dhour is not None:
        sta1 = in_dhour_list(sta1,dhour)
    if lon is not None:
        if not isinstance(lon,list):
            print("lon参数需为列表形式的包含起始经度（浮点数）和结束经度（浮点）的参数")
        sta1 = between_lon_range(sta1,lon[0],lon[1])
    if lat is not None:
        if not isinstance(lat,list):
            print("lat参数需为列表形式的包含起始纬度（浮点数）和结束纬度（浮点）的参数")
        sta1 = between_lat_range(sta1,lat[0],lat[1])
    if id is not None:
        sta1 = in_id_list(sta1,id)
    if grid is not None:
        sta1 = in_grid(sta1,grid)
    if gxy is not None:
        sta1 = in_grid_xy(sta1,gxy)
    if gxyz is not None:
        sta1 = in_grid_xyz(sta1,gxyz)
    if stadata is not None:
        sta1 = by_stadata(sta1,stadata)
    if value is not None:
        if not isinstance(value, list):
            print("value参数需为列表形式的包含起始值和结束值的参数")
        sta1 = between_value_range(sta1,value[0],value[1])
    if drop_IV is True:
        sta1 = not_IV(sta1)
    if last_range is not None:
        sta1 = between_last_range(sta1,last_range[0],last_range[1],drop_last)
    if last is not None:
        sta1 = in_last_list(sta1,last,drop_last)

    if province_name is not None:
        sta1 = in_province_list(sta1,province_name)

    return sta1



