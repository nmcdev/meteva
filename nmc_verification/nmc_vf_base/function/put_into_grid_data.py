import numpy as np
import pandas as pd
import xarray as xr

def put_into(grd_from, grd_to):
    '''
    两个格点网格信息的切片
    :param ged_from:源网格信息
    :param grd_to:目标网格信息
    :return:返回一个带有grd_to信息的多维xarray数据结构的网格信息
    比如grd_from 的网格范围是 10-20,110-150,
    grd_to的网格范围是 0-30,70-120，这时后者的网格范围就不能覆盖前者，
    如果后者范围是 0-30,70-150，则后者就能够覆盖前者。
    这是一比方，具体的问题包含6个维度，每个纬度都要判断一下后者的最大最小值是否能包含前者。
    如果不能包含就扩大到能包含，扩出来的部分先赋缺省值
    如果原来就能包含，就直接把那一块区域的值用grd_from代替
    根据grd_form中的坐标信息,判断grd_to 的坐标系能否覆盖前者
    如果能：
    把grd_from 中的数据覆盖掉grd_to中相同的网格部分
    如果不能：
    在grd_to中将坐标范围扩展成能覆盖前者，扩展出来的网格区域先设置为9999
    再将grd_from中的值覆盖掉grd_to中相同的网格部分
    '''
    #grd_from 的网格范围信息
    gf = grd_from.to_dataframe(name="")
    fslat = float(gf.index.get_level_values(4)[0])
    felat = float(gf.index.get_level_values(4)[-1])
    fslon = float(gf.index.get_level_values(5)[0])
    felon = float(gf.index.get_level_values(5)[-1])
    # grd_to 的网格范围信息
    gt = grd_to.to_dataframe(name="")
    tslat = float(gt.index.get_level_values(4)[0])
    tslat2 = float(gt.index.get_level_values(4)[1])
    telat = float(gt.index.get_level_values(4)[-1])
    tslon = float(gt.index.get_level_values(5)[0])
    tslon2 = float(gt.index.get_level_values(5)[1])
    telon = float(gt.index.get_level_values(5)[-1])
    tdlat = tslat2 - tslat
    tdlon = tslon2 - tslon

    #判断grd_from是否包含在grd_to范围内
    if fslat >= tslat and felat <=telat and fslon >= tslon and felon <= telon:
        gt_data = gt.iloc[fslat-tslat:felat-tslat, fslon-tslon:felon-tslon] = gf.values
    else:
        #grd_from的纬度起始范围在grd_to的范围内不处理，不在就扩充到包含这个范围内。
        if fslat >= tslat:
            if felat <= telat:
                pass
            else:
                telat = felat
        else:
            tslat = fslat
        # grd_from的经度起始范围在grd_to的范围内不处理，不在就扩充到包含这个范围内。
        if fslon >= tslon:
            if felon <= telon:
                pass
            else:
                telon = felon
        else:
            tslon = fslon
        #经过转换之后，grd_to变成了一个扩展之后的最大的一个网格。
        gt_data = pd.DataFrame(columns=np.arange(tslon, telon+tdlon, tdlon), index=np.arange(tslat, telat+tdlon, tdlat))
        print(gt_data.values)
        gt_data = gt_data.iloc[fslat - tslat:felat - tslat, fslon - tslon:felon - tslon] = gf.values
        gt_data.fillna(9999, inplace=True)
    tnlon = (telon - tslon)/tdlon + 1
    tnlat = (telat - tslat) /tdlat + 1
    lon = np.arange(tnlon) * tdlon + tslon
    lat = np.arange(tnlat) * tdlat + tslat
    fmember_list = list(gf.index.get_level_values(0).unique())
    flevel_list = list(gf.index.get_level_values(1).unique())
    ftime_list = list(gf.index.get_level_values(2).unique())
    fdt_list = list(gf.index.get_level_values(3).unique())
    tmember_list = list(gt.index.get_level_values(0).unique())
    tlevel_list = list(gt.index.get_level_values(1).unique())
    ttime_list = list(gt.index.get_level_values(2).unique())
    tdt_list = list(gt.index.get_level_values(3).unique())
    new_member_list =tmember_list
    new_level_list = tlevel_list
    new_time_list = ttime_list
    new_dt_list = tdt_list
    for i in fmember_list:
        if i not in tmember_list:
            new_member_list.append(i)
    for i in flevel_list:
        if i not in tlevel_list:
            new_level_list.append(i)
    for i in ftime_list:
        if i not in ttime_list:
            new_time_list.append(i)
    for i in fdt_list:
        if i not in tdt_list:
            new_dt_list.append(i)
    data = gt_data.reshape(len(new_member_list), len(new_level_list), len(new_time_list), len(new_dt_list), tnlat, tnlon)
    return (xr.DataArray(data, coords={'member': new_member_list, 'level': new_level_list, 'time': new_time_list, 'dt': new_dt_list,
                                       'lat': lat, 'lon': lon},
                         dims=['member', 'level', 'time', 'dt', 'lat', 'lon']))
