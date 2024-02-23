import numpy as np
import math
import pandas as pd
import copy

def surround_index(grd_ob,grd_fo,thresholds):
    '''

    :param grd_ob: 观测网格数据
    :param grd_fo: 预报网格数据
    :param threholds: 等级阈值
    :return:
    '''
    x = copy.deepcopy(grd_ob.values.squeeze())
    aindex_x = sindex(x,thresh=thresholds)
    y = copy.deepcopy(grd_fo.values.squeeze())
    aindex_y = sindex(y, thresh=thresholds)
    resulut = {"surround_index":[aindex_x["surround_index"],aindex_y["surround_index"]],
               "perimeter_min":[aindex_x["perimeter_min"],aindex_y["perimeter_min"]],
               "perimeter":[aindex_x["perimeter"],aindex_y["perimeter"]]}
    return resulut



def sindex(x, thresh=None, loc=None):

    if thresh is None:
        thresh = 1e-08
    t = copy.deepcopy(x)
    t[t <= thresh] = 0       #低于阈值的置为0
    n = np.count_nonzero(t)   #非0的格点数
    n2 = math.sqrt(n)
    if math.floor(n2) == n2:
        #正方形网格
        p_min = 4 * n2  #周长
    else:
        #长方形网格， 例如 n=4*5 = 20, n2 = 4.47, math.floor(2 * n2)=8,p_min = 18
        p_min = 2 * (math.floor(2 * n2) + 1)   #周长

    if loc is None:
        x_dim = x.shape[0]
        y_dim = x.shape[1]
        range0 = np.tile(np.arange(1, x_dim + 1), y_dim)
        range1 = (np.arange(1, y_dim + 1)).repeat(x_dim)
        loc = np.stack((range0, range1), axis=-1)

    index = t != 0
    i = np.tile(index.reshape(index.size, 1), 2)
    ft = loc[i]
    ft = ft.reshape(((int)(ft.size/2), 2))
    ft = np.array(np.where(t>0)).T
    ft_max = np.max(ft, axis=0)
    ft_min = np.min(ft, axis=0)
    p = 2 * (ft_max[0] - ft_min[0] + 1) + 2 * (ft_max[1] - ft_min[1] + 1)
    #res = pd.DataFrame({"surround_index": p_min / p, "perimeter_min": p_min, "perimeter": p}, index=[0])
    res = {"surround_index": p_min / p, "perimeter_min": p_min, "perimeter": p}
    return res


if __name__ == '__main__':
    # x = np.zeros((8, 8))
    # x[2, 1:4] = 2
    # x[4, 3:6] = 1
    # x[6, 5:7] = 1
    # res = sindex(x)
    # print(res)
    import meteva.base as meb
    import meteva.method as mem
    grid2 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    dat_ob2 = np.zeros((grid2.nlat, grid2.nlon))
    for j in range(grid2.nlat):
        for i in range(grid2.nlon):
            dat_ob2[j, i] = 20 * math.exp(-0.001 * (i - 200) ** 2 - 0.001 * (j - 200) ** 2)
    grd_ob2 = meb.grid_data(grid2, dat_ob2)

    grid2 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    dat_fo2 = np.zeros((grid2.nlat, grid2.nlon))
    for j in range(grid2.nlat):
        for i in range(grid2.nlon):
            dat_fo2[j, i] = 10 * math.exp(-0.001 * (i - 230) ** 2 - 0.0003 * (j - 230) ** 2)
            dat_fo2[j, i] += 10 * math.exp(-0.001 * (i - 170) ** 2 - 0.0003 * (j - 170) ** 2)
    grd_fo2 = meb.grid_data(grid2, dat_fo2)
    result = mem.space.surround_index(grd_ob2, grd_fo2, thresholds=5)
    print(result)