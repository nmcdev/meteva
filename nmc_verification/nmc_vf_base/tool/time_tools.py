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
    else:
        print("时间类型不识别")
        return None

#所有的timedelta类型的数据转为timedelta64类型的时间格式
def all_type_timedelta_to_timedelta64(timedelta0):
    if isinstance(timedelta0,np.timedelta64):
        return timedelta0
    elif isinstance(timedelta0,datetime.timedelta):
        return np.timedelta64(timedelta0)
    elif type(timedelta0) == str:
        return str_to_timedelta64(timedelta0)
    else:
        print("时效类型不识别")
        return None

#str类型的时间转换为timedelta64类型的时间
def str_to_timedelta64(timedalta_str):
    num_str = ''.join([x for x in timedalta_str if x.isdigit()])
    num = int(num_str)
    # 提取出dtime_type类型
    TIME_type = re.findall(r"\D+", timedalta_str)[0].lower()
    if TIME_type == 'h':
        return np.timedelta64(num, 'h')
    elif TIME_type == 'd':
        return np.timedelta64(num, 'D')
    elif TIME_type == 'm':
        return np.timedelta64(num, 'm')
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
