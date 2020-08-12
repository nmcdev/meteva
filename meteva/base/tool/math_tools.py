# coding: utf-8
import numpy as np
import math

def reset_max_min(vmax,vmin):
    dif = (vmax - vmin) / 10.0
    if dif ==0:
        inte = 1
    else:
        inte = math.pow(10, math.floor(math.log10(dif)))
    # 用基本间隔，将最大最小值除于间隔后小数点部分去除，最后把间隔也整数化
    r = dif / inte
    if r < 3 and r >= 1.5:
        inte = inte * 2
    elif r < 4.5 and r >= 3:
        inte = inte * 4
    elif r < 5.5 and r >= 4.5:
        inte = inte * 5
    elif r < 7 and r >= 5.5:
        inte = inte * 6
    elif r >= 7:
        inte = inte * 8
    vmin = inte * ((int)(vmin / inte) - 1)
    vmax = inte * ((int)(vmax / inte) + 1)
    return vmax,vmin,inte

def sigmoid(inputX):
    return 1.0/(1+np.exp(-inputX))

#根据经纬度计算距离，然后开平方根
def earth_surface_dis(ax,ay,bx,by):
    sr=math.cos(ay*math.pi/180)
    d1=(ax-bx)*sr
    d2=ay-by
    dis1=math.sqrt(d1*d1+d2*d2)
    return dis1

#根据经纬度计算距离
def earth_surface_dis2(ax,ay,bx,by):
    sr=math.cos(ay*math.pi/180)
    d1=(ax-bx)*sr
    d2=ay-by
    dis2=d1*d1+d2*d2
    return dis2

#经度纬度信息转换为直角坐标系
def lon_lat_to_cartesian(lon, lat, R=1):
    """
    calculates lon, lat coordinates of a point on a sphere with
    radius R
    """
    lon_r = np.radians(lon)
    lat_r = np.radians(lat)
    xyz = np.zeros((len(lon), 3))
    xyz[:, 0] = R * np.cos(lat_r) * np.cos(lon_r)
    xyz[:, 1] = R * np.cos(lat_r) * np.sin(lon_r)
    xyz[:, 2] = R * np.sin(lat_r)
    return xyz


def mean_iteration(count_old,mean_old,count_new,mean_new):
    count_total = count_new + count_old
    rate1 = count_old/count_total
    rate2 = count_new/count_total
    mean = rate1 * mean_old + rate2 * mean_new
    return mean

def ss_iteration(count_old,mean_old,ss_old,count_new,mean_new,ss_new):
    count_total = count_new + count_old
    rate1 = count_old/count_total
    rate2 = count_new/count_total
    mean_total = rate1 * mean_old + rate2 * mean_new
    ss_total = ss_old * count_old
    ss_total += count_old * math.pow((1- rate1) * mean_old - rate2 * mean_new,2)
    ss_total += ss_new * count_new
    ss_total += count_new * math.pow((1- rate2) * mean_new - rate1 * mean_old,2)
    ss_total /= count_total
    return count_total,mean_total,ss_total

def sxy_iteration(count_old,meanx_old,meany_old,sxy_old,count_new,meanx_new,meany_new,sxy_new):
    import math
    count_total = count_new + count_old
    rate1 = count_old/count_total
    rate2 = count_new/count_total
    meanx_total = rate1 * meanx_old + rate2 * meanx_new
    meany_total = rate1 * meany_old + rate2 * meany_new
    sxy_total = sxy_old * count_old
    sxy_total += count_old * ((1- rate1) * meanx_old - rate2 * meanx_new) * ((1- rate1) * meany_old - rate2 * meany_new)
    sxy_total += sxy_new * count_new
    sxy_total += count_new * ((1- rate2) * meanx_new - rate1 * meanx_old) * ((1- rate2) * meany_new - rate1 * meany_old)
    sxy_total /= count_total
    return count_total, meanx_total, meany_total,sxy_total

def get_index(X,level_list):
    levels = np.array(level_list)
    levels.sort()
    index = np.zeros_like(X)
    index[...] = len(levels)
    for i in range(len(levels)):
        level = levels[i]
        index[X < level] = i - 1
    return index


def greatest_common_divisor(value_list):

    value_set = np.array(list(set(value_list))).astype(np.int32)

    # 获取最小值
    x = value_set[0]
    value_set1 = value_set[1:]
    for i in range(len(value_set1)):
        y = value_set1[i]
        if x > y:
            smaller = y
        else:
            smaller = x
        for i in range(1, smaller + 1):
            if ((x % i == 0) and (y % i == 0)):
                hcf = i
        x = hcf
    return x