import nmc_verification
import copy
import pandas as pd
import numpy as np

def sta_of_name(sta,data_name):
    columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt',data_name]
    sta1 = sta[columns]
    return sta1
def sta_in_name_list(sta,data_name_list):
    columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt'] + data_name_list
    sta1 = sta[columns]
    return sta1

def sta_of_level(sta,level):
    sta1 = sta.loc[sta['level']==level]
    return sta1

def sta_in_level_list(sta,level_list):
    sta1 = sta.loc[sta['level'].isin(level_list)]
    return sta1

def sta_of_id(sta,id):
    sta1 = sta.loc[sta['id']==id]
    return sta1

def sta_in_id_list(sta,id_list):
    sta1 = sta.loc[sta['id'].isin(id_list)]
    return sta1

def sta_of_time(sta,time):
    time1= nmc_verification.nmc_vf_base.method.time_tools.all_type_time_to_time64(time)
    sta1 = sta.loc[sta['time'] == time1]
    return sta1

def sta_in_time_list(sta,time_list):
    time_list1 = []
    for time0 in time_list:
        time_list1.append(nmc_verification.nmc_vf_base.method.time_tools.all_type_time_to_time64(time0))
    sta1 = sta.loc[sta['time'].isin(time_list1)]
    return sta1

def sta_in_year_list(sta,year_list):
    years = sta['time'].map(lambda x: x.year)
    sta1 = sta.loc[years.isin(year_list)]
    return sta1

def sta_in_month_list(sta,month_list):
    months = sta['time'].map(lambda x: x.month)
    sta1 = sta.loc[months.isin(month_list)]
    return sta1

def sta_in_xun_list(sta,xun_list):
    mons = sta['time'].map(lambda x: x.month).values.astype(np.int16)
    days = sta['time'].map(lambda y: y.day).values
    xuns = np.ceil(days / 10).astype(np.int16)
    xuns[xuns>3] = 3
    xuns += (mons - 1) * 3
    xuns = pd.Series(xuns)
    sta1 = sta.loc[xuns.isin(xun_list)]
    return sta1


def sta_in_hou_list(sta,hou_list):
    mons = sta['time'].map(lambda x: x.month).values.astype(np.int16)
    days = sta['time'].map(lambda y: y.day).values
    hous = np.ceil(days / 5).astype(np.int16)
    hous[hous>6] = 6
    hous += (mons - 1) * 6
    hous = pd.Series(hous)
    sta1 = sta.loc[hous.isin(hou_list)]
    return sta1

def sta_in_day_list(sta,day_list):
    days = sta['time'].map(lambda x: x.dayofyear)
    sta1 = sta.loc[days.isin(day_list)]
    return sta1

def sta_in_hour_list(sta,hour_list):
    hours = sta['time'].map(lambda x: x.hour)
    sta1 = sta.loc[hours.isin(hour_list)]
    return sta1

def sta_between_time_range(sta,start_time,end_time,dtime = None):
    #空函数，待完善
    return sta

def sta_of_dtime(sta,dtime):
    dtime1 = nmc_verification.nmc_vf_base.method.time_tools.all_type_time_to_time64(dtime)
    sta1 = sta.loc[sta['dtime']==dtime1]
    return sta1

def sta_in_dtime_list(sta,dtime_list):
    dtime_list1 = []
    for time0 in dtime_list:
        dtime_list1.append(nmc_verification.nmc_vf_base.method.time_tools.all_type_timedelta_to_timedelta64(time0))
    sta1 = sta.loc[sta['dtime'].isin(dtime_list1)]
    return sta1

def sta_in_dday_list(sta,dday_list):
    seconds = sta['dtime'].map(lambda x: x/np.timedelta64(1, 's')).values
    days = np.ceil(seconds/(24*3600))
    days = pd.Series(days)
    sta1 = sta.loc[days.isin(dday_list)]
    return sta1

def sta_in_dhour_list(sta,dhour_list):
    seconds = sta['dtime'].map(lambda x: x/np.timedelta64(1, 's')).values
    hours = np.ceil(seconds/(3600)).astype(np.int16)
    hours = pd.Series(hours)
    sta1 = sta.loc[hours.isin(dhour_list)]
    return sta1

def sta_in_dminute_list(sta,dminute_list):
    seconds = sta['dtime'].map(lambda x: x/np.timedelta64(1, 's')).values
    minutes = np.ceil(seconds/(60))
    minutes = pd.Series(minutes)
    sta1 = sta.loc[minutes.isin(dminute_list)]
    return sta1


def sta_between_dtime_range(sta,start_dtime,end_dtime,d_dtime):
    #空函数，待完善
    return sta



def sta_between_lon_range(sta,slon,elon):
    sta1 = sta.loc[(sta['lon']>=slon) & (sta['lon']<= elon)]
    return sta1

def sta_between_lat_range(sta,slat,elat):
    sta1 = sta.loc[(sta['lat']>=slat) & (sta['lat']<= elat)]
    return sta1

def sta_between_alt_range(sta,salt,ealt):
    sta1 = sta.loc[(sta['alt']>=salt) & (sta['alt']<= ealt)]
    return sta1

def sta_in_grid_xy(sta,grid):
    sta1 = sta_between_lon_range(sta,grid.slon,grid.elon)
    sta2 = sta_between_lat_range(sta1,grid.slat,grid.elat)
    return sta2


def get_by_para_dict(sta,para_dict):
    '''
    para_dict 应具备如下样式
    para_dict = {'level' :[850,700],  列表形式
                'time' : ['2018010108','2018010208'], 列表形式
                'dtime':['24h','36h']，列表形式
                'id':[54511]， 列表形式
                'lon': [70,140], 闭区间
                'lat' :[10,60], 闭区间
                'alt’: [ 0,9999] 闭区间
    }
    '''
    sta1 = sta_in_level_list(sta,para_dict['level'])
    sta1 = sta_in_time_list(sta1,para_dict['time'])
    sta1 = sta_in_dtime_list(sta1, para_dict['dtime'])
    sta1 = sta_in_id_list(sta1, para_dict['id'])
    sta1 = sta_between_lon_range(sta1,para_dict['lon'][0],para_dict['lon'][1])
    sta1 = sta_between_lat_range(sta1, para_dict['lat'][0], para_dict['lat'][1])
    sta1 = sta_between_alt_range(sta1, para_dict['alt'][0], para_dict['alt'][1])
    return sta1


