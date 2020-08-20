import datetime
import numpy as np
import re

#所有类型的时间转换为time64
def all_type_time_to_time64(time0):
    if isinstance(time0,np.datetime64):
        return time0
    elif isinstance(time0,datetime.datetime):
        return np.datetime64(time0)
    elif type(time0) == str:
        return str_to_time64(time0)
    elif isinstance(time0,int):
        time1 = datetime.datetime.utcfromtimestamp(time0 / 1000000000)
        np.datetime64(time1)
        return np.datetime64(time1)
    else:
        print("时间类型不识别")
        return None

def all_type_time_to_datetime(time0):
    if isinstance(time0,int):
        time1 = datetime.datetime.utcfromtimestamp(time0 / 1000000000)
        return time1
    time64 = all_type_time_to_time64(time0)
    time1 = time64.astype(datetime.datetime)
    if isinstance(time1,int):
        time1 = datetime.datetime.utcfromtimestamp(time1/1000000000)
    return time1

def all_type_time_to_str(time0):
    time1 = all_type_time_to_time64(time0)
    return time_to_str(time1)


#所有的timedelta类型的数据转为timedelta64类型的时间格式
def all_type_timedelta_to_timedelta64(timedelta0):
    if isinstance(timedelta0,np.timedelta64):
        return timedelta0
    elif isinstance(timedelta0,datetime.timedelta):
        return np.timedelta64(timedelta0)
    elif type(timedelta0) == str:
        timedelta1 = str_to_timedelta(timedelta0)
        return np.timedelta64(timedelta1)
    else:
        print("时效类型不识别")
        return None

def all_type_timedelta_to_timedelta(timedelta0):
    if isinstance(timedelta0,datetime.timedelta):
        return timedelta0
    elif isinstance(timedelta0,np.timedelta64):
        seconds = int(timedelta0 / np.timedelta64(1, 's'))
        timedelta1 = datetime.timedelta(seconds = seconds)
        return timedelta1
    elif type(timedelta0) == str:
        timedelta1 = str_to_timedelta(timedelta0)
        return timedelta1
    else:
        print("时效类型不识别")
        return None

#str类型的时间转换为timedelta64类型的时间
def str_to_timedelta(timedalta_str):
    num_str = ''.join([x for x in timedalta_str if x.isdigit()])
    num = int(num_str)
    # 提取出dtime_type类型
    TIME_type = re.findall(r"\D+", timedalta_str)[0].lower()
    if TIME_type == 'h':
        return datetime.timedelta(hours=num)
    elif TIME_type == 'd':
        return datetime.timedelta(days=num)
    elif TIME_type == 'm':
        return datetime.timedelta(minutes=num)
    else:
        print("输入的时效格式不识别")
        return None

#str类型的时间转换为time64类型的时间
def str_to_time64(time_str):
    str1 = ''.join([x for x in time_str if x.isdigit()])
    # 用户输入2019041910十位字符，后面补全加0000，为14位统一处理
    if len(str1) == 4:
        str1 += "0101000000"
    elif len(str1) == 6:
        str1 +="01000000"
    elif len(str1) == 8:
        str1 +="000000"
    elif len(str1) == 10:
        str1 +="0000"
    elif len(str1) == 12:
        str1 +="00"
    elif len(str1) > 12:
        str1 = time_str[0:12]
    else:
        print("输入日期格式不识别，请检查！")

    # 统一将日期变为datetime类型
    time = datetime.datetime.strptime(str1, '%Y%m%d%H%M%S')
    time64 = np.datetime64(time)
    return time64



#datetime64类型的数据转换为str类型
def time_to_str(time):
    if isinstance(time,np.datetime64):
        str1 = str(time).replace("-", "").replace(" ", "").replace(":", "").replace("T", "")[0:14]
    else:
        str1 = time.strftime("%Y%m%d%H%M%S")
    return str1


#字符转换为datetime
def str_to_time(str0):
    num = ''.join([x for x in str0 if x.isdigit()])
    # 用户输入2019041910十位字符，后面补全加0000，为14位统一处理
    if len(num) == 4:
        num += "0101000000"
    elif len(num) == 6:
        num += "01000000"
    elif len(num) == 8:
        num += "000000"
    elif len(num) == 10:
        num += "0000"
    elif len(num) == 12:
        num += "00"
    elif len(num) > 12:
        num = num[0:12]
    else:
        print("输入日期有误，请检查！")
    # 统一将日期变为datetime类型
    return datetime.datetime.strptime(num, '%Y%m%d%H%M%S')


def get_dtime_of_path(path_model,path):
    ttt_index = path_model.find("TTT")
    if (ttt_index >= 0):
        ttt = int(path[ttt_index:ttt_index + 3])
    else:
        ttt = 0
    return ttt
def get_time_of_path(path_model,path):
    yy_index = path_model.find("YYYY")
    if  yy_index < 0:
        yy_index = path_model.find("YY")
        if(yy_index <0):
            yy = 2000
        else:
            yy = int(path[yy_index: yy_index + 2])
    else:
        yy = int(path[yy_index: yy_index+4])

    mm_index = path_model.find("MM")
    if(mm_index >=0):
        mm = int(path[mm_index:mm_index+2])
    else:
        mm = 1

    dd_index = path_model.find("DD")
    if(dd_index>=0):
        dd = int(path[dd_index:dd_index + 2])
    else:
        dd = 1
    hh_index = path_model.find("HH")
    if(hh_index>=0):
        hh = int(path[hh_index:hh_index + 2])
    else:
        hh = 0
    ff_index = path_model.find("FF")
    if(ff_index>=0):
        ff = int(path[ff_index:ff_index + 2])
    else:
        ff = 0
    ss_index = path_model.find("SS")
    if(ss_index>=0):
        ss = int(path[ss_index:ss_index + 2])
    else:
        ss = 0
    return datetime.datetime(yy,mm,dd,hh,ff,ss)

