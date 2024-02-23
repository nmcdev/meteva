# coding: utf-8
import numpy as np
import math
import meteva

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


def angle_of_line(ax,ay,bx,by):
    u = bx - ax
    v = by - ay
    s = math.sqrt(u * u + v * v)
    if s ==0:
        angle = 0
    else:
        if v >=0:
            angle = 90 - math.asin(u / s) * 180 / math.pi
        else:
            angle = 270 + math.asin(u / s) * 180 / math.pi

    return angle

def cross_angle(lines1,linee1, lines2,linee2):
    delta1 = [linee1[0] - lines1[0],linee1[1]-lines1[1]]
    delta2 = [linee2[0] - lines2[0],linee2[1]-lines2[1]]
    length1 = math.sqrt(math.pow(delta1[0],2) + math.pow(delta1[1],2))
    length2 = math.sqrt(math.pow(delta2[0],2) + math.pow(delta2[1],2))
    cos1 = (delta1[0] * delta2[0] + delta1[1] * delta2[1])/(length1 * length2)
    angle = math.acos(cos1) *180/ math.PI
    return angle


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
    #ss_total = ss_old * count_old
    #ss_total += count_old * math.pow((1- rate1) * mean_old - rate2 * mean_new,2)
    #ss_total += ss_new * count_new
    #ss_total += count_new * math.pow((1- rate2) * mean_new - rate1 * mean_old,2)
    #ss_total /= count_total
    ss_total= rate1*(ss_old + math.pow(rate2 *(mean_old - mean_new),2))
    ss_total += rate2 * (ss_new + math.pow(rate1 * (mean_old - mean_new), 2))

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


def u_v_to_s_d(u,v):
    s = np.sqrt(np.power(u, 2) + np.power(v, 2))
    d = np.zeros(u.shape)
    index = np.where(s != 0)
    vd_n0 = v[index]
    ud_n0 = u[index]
    s_n0 = s[index]
    ag_n0 = 180 - np.arccos(vd_n0 / s_n0) * 180 / np.pi
    ag_n0[ud_n0 > 0] = 360 - ag_n0[ud_n0 > 0]
    d[index] = ag_n0
    s[u==meteva.base.IV] = meteva.base.IV
    d[u==meteva.base.IV] = meteva.base.IV
    return s,d



def tran_direction_to_8angle(direction):
    '''
    将0-360度的风向，转换成8个方位，分布用0,1,2，。。。7代表北风，东北风，东方，东南风，南风，西南风，西风，西北风
    :param direction: 风向角度， 0-360度。 任意维numpy数组
    :return: 风向方位，0-7，和direction的shape一致的numpy数组
    '''
    angles = np.zeros(direction.shape)
    for i in range(1,8):
        angles[np.abs(direction - i * 45) <= 22.5] = i
    return angles

def tran_speed_to_14grade(speeds):
    '''
    将风速（m/s)，转换成14个风速等级，分布用0,1,2，。。。13代表静风，1级、2级，。。。，12级和大于等于13级
    :param speeds: 风速（m/s)。 任意维numpy数组
    :return: 风速等级，和speeds的shape一致的numpy数组
    '''
    grades = np.zeros(speeds.shape)
    gs = [0,0.3,1.6,3.4,5.5,8.0,10.8,13.9,17.2,20.8,24.5,28.5,32.7,37,300]
    for i in range(1,14):
        gi = gs[i]
        grades[speeds>=gi] = i
    return grades

def s_d_to_u_v(speed,direction):
    u = -speed * np.sin(direction * 3.14 / 180)
    v = -speed * np.cos(direction * 3.14 / 180)
    return u,v



def ctl_proj(grid0,proj_para,dat):
    #投影中心点

    inter_i = meteva.base.ER * 1000 / proj_para["dx"]
    inter_j = meteva.base.ER * 1000 / proj_para["dy"]
    if proj_para["type"] == "lcc":
        mlon = proj_para["proj_mlon"]* math.pi/180

        #球面转扇形
        lats1 = (grid0.slat + np.arange(grid0.nlat) * grid0.dlat) * math.pi / 180
        lons1 = (grid0.slon + np.arange(grid0.nlon) * grid0.dlon) * math.pi / 180
        lons,lats = np.meshgrid(lons1,lats1)
        lons = lons.flatten()
        lats = lats.flatten()
        #根据lon 计算扇形fanR
        slat = proj_para["proj_slat"] * math.pi/180
        elat = proj_para["proj_elat"] * math.pi/180
        xs = math.cos(slat)
        ys = math.sin(slat)
        xe = math.cos(elat)
        ye = math.sin(elat)
        a = (ys - ye)/(xs - xe)  #在R方向投影线性系数
        b = (ye * xs - ys * xe)/(xs - xe)
        r = np.tan(lats)
        x_ar = b/(r-a)
        ac = math.sqrt(1 + a * a)
        fanR = x_ar * ac

        #计算角度比例
        dx_slat = math.cos(slat)
        fanR_slat = b/(math.tan(slat) - a) * ac
        angle_rate = dx_slat / fanR_slat


        dlons = (lons - mlon) * angle_rate

        fanX = fanR * np.sin(dlons)
        fanY = -fanR * np.cos(dlons)

        dmodel_lon = (proj_para["model_lon"] * math.pi/180 - mlon) * angle_rate
        model_lat = proj_para["model_lat"] * math.pi / 180
        model_fanR =b/(math.tan(model_lat)-a)* ac
        model_fanX = model_fanR * np.sin(dmodel_lon)
        model_fanY = -model_fanR * np.cos(dmodel_lon)

        fan_i = (fanX - model_fanX) * inter_i + proj_para["model_i"]
        fan_j = (fanY - model_fanY) * inter_j + proj_para["model_j"]
        nx_1 = proj_para["nx"] - 1
        ny_1 = proj_para["ny"] - 1
        in_grid_index = np.where((fan_i >= 0) & (fan_i < nx_1) & (fan_j >= 0) & (fan_j < ny_1))[0]
        fan_i_in = fan_i[in_grid_index]
        fan_j_in = fan_j[in_grid_index]
        ig = fan_i_in.astype(dtype = 'int16')
        jg = fan_j_in.astype(dtype = 'int16')
        dx = fan_i_in - ig
        dy = fan_j_in - jg
        c00 = (1 - dx) * (1 - dy)
        c01 = dx * (1 - dy)
        c10 = (1-dx) * dy
        c11 = dx * dy
        ig1 = ig + 1
        jg1 = jg + 1
        dat_sta = c00 * dat[jg, ig] + c01 * dat[jg, ig1] + c10 * dat[jg1, ig] + c11 * dat[jg1, ig1]
        data_re = np.zeros(grid0.nlat * grid0.nlon)
        data_re[in_grid_index] = dat_sta[:]
        grd = meteva.base.grid_data(grid0,data_re)
        return grd


def isRayIntersectsSegment(poi,s_poi,e_poi): #[x,y] [lng,lat]
    #输入：判断点，边起点，边终点，都是[lng,lat]格式数组
    if s_poi[1]==e_poi[1]: #排除与射线平行、重合，线段首尾端点重合的情况
        return False
    if s_poi[1]>poi[1] and e_poi[1]>poi[1]: #线段在射线上边
        return False
    if s_poi[1]<poi[1] and e_poi[1]<poi[1]: #线段在射线下边
        return False
    if s_poi[1]==poi[1] and e_poi[1]>poi[1]: #交点为下端点，对应spoint
        return False
    if e_poi[1]==poi[1] and s_poi[1]>poi[1]: #交点为下端点，对应epoint
        return False
    if s_poi[0]<poi[0] and e_poi[1]<poi[1]: #线段在射线左边
        return False

    xseg=e_poi[0]-(e_poi[0]-s_poi[0])*(e_poi[1]-poi[1])/(e_poi[1]-s_poi[1]) #求交
    if xseg<poi[0]: #交点在射线起点的左侧
        return False
    return True  #排除上述情况之后

def isPoiWithinPoly(poi,poly):
    #输入：点，多边形三维数组
    #poly=[[[x1,y1],[x2,y2],……,[xn,yn],[x1,y1]],[[w1,t1],……[wk,tk]]] 三维数组

    #可以先判断点是否在外包矩形内
    #if not isPoiWithinBox(poi,mbr=[[0,0],[180,90]]): return False
    #但算最小外包矩形本身需要循环边，会造成开销，本处略去
    sinsc=0 #交点个数
    for epoly in poly: #循环每条边的曲线->each polygon 是二维数组[[x1,y1],…[xn,yn]]
        np = len(epoly)
        for i in range(np-1): #[0,len-1]
            s_poi=epoly[i]
            e_poi=epoly[i+1]
            if isRayIntersectsSegment(poi,s_poi,e_poi):
                sinsc+=1 #有交点就加1
        if epoly[np-1][0] != epoly[0][0] or  epoly[np-1][1] != epoly[0][1]:
            s_poi = epoly[np-1]
            e_poi = epoly[0]
            if isRayIntersectsSegment(poi, s_poi, e_poi):
                sinsc += 1  # 有交点就加1

    return True if sinsc%2==1 else  False


def distance_in_a_straight_line(lon1,lat1,lon2,lat2):
    '''
    计算地球表面两个点之间的直线距离
    :param lon1:
    :param lat1:
    :param lon2:
    :param lat2:
    :return:
    '''
    xyz1 = lon_lat_to_cartesian(lon1, lat1, R=meteva.base.ER)
    xyz2 = lon_lat_to_cartesian(lon2,lat2,R = meteva.base.ER)
    dxyz = xyz2 - xyz1
    dis2 = np.sum(dxyz*dxyz,axis=1)
    dis1 = np.sqrt(dis2)
    return dis1


def distance_on_earth_surface(lon1,lat1,lon2,lat2):
    '''
    计算地球表明两个点之间的球面距离
    :param lon1:
    :param lat1:
    :param lon2:
    :param lat2:
    :return:
    '''

    a1 = lon1 * math.pi/180
    b1 = lat1 * math.pi/180
    a2 = lon2 * math.pi/180
    b2 = lat2 * math.pi/180

    dis = meteva.base.ER * np.arccos(np.cos(b1)*np.cos(b2)*np.cos(a1-a2) + np.sin(b1)*np.sin(b2))

    if isinstance(dis,np.ndarray):
        dis[np.isnan(dis)] =0
    else:
        if np.isnan(dis):
            dis = 0
    return dis
