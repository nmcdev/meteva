import nmc_verification.nmc_vf_base.method.time_tools as time_tools

def get_by_data_name(sta,data_name):
    columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt',data_name]
    sta1 = sta[columns]
    return sta1
def get_by_data_name_list(sta,data_name_list):
    columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', 'alt'] + data_name_list
    sta1 = sta[columns]
    return sta1

def get_by_level(sta,level):
    sta1 = sta.loc[sta['level']==level]
    return sta1

def get_by_level_list(sta,level_list):
    sta1 = sta.loc[sta['level'].isin(level_list)]
    return sta1

def get_by_id(sta,id):
    sta1 = sta.loc[sta['id']==id]
    return sta1

def get_by_id_list(sta,id_list):
    sta1 = sta.loc[sta['id'].isin(id_list)]
    return sta1

def get_by_time(sta,time):
    time1= time_tools.all_type_time_to_time64(time)
    sta1 = sta.loc[sta['time'] == time1]
    return sta1

def get_by_time_list(sta,time_list):
    time_list1 = []
    for time0 in time_list:
        time_list1.append(time_tools.all_type_time_to_time64(time0))
    sta1 = sta.loc[sta['time'].isin(time_list1)]
    return sta1

def get_by_time_range(sta,start_time,end_time,dtime = None):
    #空函数，待完善
    return sta

def get_by_dtime(sta,dtime):
    dtime1 = time_tools.all_type_time_to_time64(dtime)
    sta1 = sta.loc[sta['dtime']==dtime1]
    return sta1

def get_by_dtime_list(sta,dtime_list):
    dtime_list1 = []
    for time0 in dtime_list:
        dtime_list1.append(time_tools.all_type_time_to_time64(time0))
    sta1 = sta.loc[sta['dtime'].isin(dtime_list1)]
    return sta1

def get_by_dtime_range(sta,start_dtime,end_dtime,d_dtime):
    #空函数，待完善
    return sta


