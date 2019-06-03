import datetime
import numpy as np

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
        print("输入日期有误，请检查！")

    # 统一将日期变为datetime类型
    time = datetime.datetime.strptime(str1, '%Y%m%d%H%M%S')
    time64 = np.datetime64(time)
    return time64

def time_to_str(time):
    if isinstance(time,np.datetime64):
        str1 = str(time).replace("-", "").replace(" ", "").replace(":", "").replace("T", "")[0:14]
    else:
        str1 = time.strftime("%Y%m%d%H%M%S")
    return str1