import  numpy as np
import pandas as pd
def get_from(grd_from, grd_to):
    '''
    格点网格的切分、分片
    :param grd_from:源网格信息
    :param grd_to:需要映射的目标网格信息
    :return:两个网格的重合部分，并赋值返回。
    # 首先根据grid_to定一个初始的网格场grd_to，并且将取值都设为缺省
    # 然后从grd_from里面找到两个网格重合的区域的那部分取值，将其赋值到grd_to
    
    '''
    gf = grd_from.to_dataframe(name="")
    fslat = float(gf.index.get_level_values(4)[0])
    felat = float(gf.index.get_level_values(4)[-1])
    fslon = float(gf.index.get_level_values(5)[0])
    felon = float(gf.index.get_level_values(5)[-1])
    gt = grd_to.to_dataframe(name="")
    tslat = float(gt.index.get_level_values(4)[0])
    tslat2 = float(gt.index.get_level_values(4)[1])
    telat = float(gt.index.get_level_values(4)[-1])
    tslon = float(gt.index.get_level_values(5)[0])
    tslon2 = float(gt.index.get_level_values(5)[1])
    telon = float(gt.index.get_level_values(5)[-1])
    tdlat = tslat2 - tslat
    tdlon = tslon2 - tslon
    #根据grid_to定一个初始的网格场grd_to，并且将取值都设为缺省
    gt_data = pd.DataFrame(columns=np.arange(tslon, telon + tdlon, tdlon), index=np.arange(tslat, telat + tdlon, tdlat))
    print(gt_data.values)
    #求出两个网格的公共区域
    slon = np.max([int(fslon * 100), int(tslon * 100)]) / 100
    elon = np.min([int(felon * 100), int(telon * 100)]) / 100
    slat = np.max([int(fslat * 100), int(tslat * 100)]) / 100
    elat = np.min([int(felat * 100), int(telat * 100)]) / 100
    print("起始范围：{}--{} {}--{}".format(slon, elon, slat, elat))
    if slon >=elon or slat >=elat:
        print("两者不存在公共区域！")
        return 0
    else:
        data = grd_from.values()
        dat = np.squeeze(data)
        print(dat.shape)
        #切分出两个网格公共区域部分的值
        fill_data = dat[fslat - slat:felat - slat,fslon - slon:felon -slon ]
        #从grd_from中求出公共区域的值，并进行填充
        gt_data = gt_data.iloc[fslat - tslat:felat - tslat, fslon - tslon:felon - tslon] = fill_data
        gt_data.fillna(9999, inplace=True)
        grd_to.values = gt_data
        return grd_to
