import numpy as np
#import cv2
import math
#import pyreadr
from scipy.ndimage import convolve
import meteva
import copy

def count_index(grd_ob,grd_fo,thresholds):
    '''

    :param grd_ob: 观测网格数据
    :param grd_fo: 预报网格数据
    :param threholds: 等级阈值
    :return:
    '''
    x = copy.deepcopy(grd_ob.values.squeeze())
    aindex_x = cindex(x,thresh=thresholds)
    y = copy.deepcopy(grd_fo.values.squeeze())
    aindex_y = cindex(y, thresh=thresholds)
    resulut = {"count_index":[aindex_x["count_index"],aindex_y["count_index"]],
               "count_nonzero":[aindex_x["count_nonzero"],aindex_y["count_nonzero"]],
               "count_connect":[aindex_x["count_connect"],aindex_y["count_connect"]]}
    return resulut


def cindex(x, thresh=None):
    if thresh is None:
        thresh = 1e-08

    sx = np.zeros(x.shape)
    sx[x >= thresh] = 1
    kernel =    np.array([[1, 1, 1],
                         [1, 1, 1],
                        [1, 1, 1]])/9
    sm =  convolve(sx, kernel) #均值滤波
    #sm = sx
    thresh1 = 50/255   #平滑后亮度大于50
    sm1 = sm >= thresh1
    NP = np.count_nonzero(sx)   #所有的非0格点
    label_array = meteva.method.mode.measure_label(sm1)  #转换成label矩阵
    num_obj =int(np.max(label_array))  #连通域的数量
    NC = num_obj - 1
    c =  1 - (NC - 1) / (math.sqrt(NP) + NC)
    result = {"count_index":c,"count_nonzero":NP,"count_connect":num_obj}

    return result

# def cindex_with_cv(x, thresh=None):
#     if thresh is None:
#         thresh = 1e-08
#     sx = x
#     sx[sx >= thresh] = 255
#     sx[sx < thresh] = 0
#     cv2.imwrite("pic/cindex/data.png", sx)
#     img = cv2.imread("pic/cindex/data.png")
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 将图像转换成灰度
#     blur = cv2.blur(gray, (3, 3))  # 均值滤波
#     ret, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)
#     NP = np.count_nonzero(sx)
#     num_obj, labels = cv2.connectedComponents(thresh)
#     NC = num_obj - 1
#     return 1 - (NC - 1) / (math.sqrt(NP) + NC)


if __name__ == '__main__':
    import meteva.base as meb
    import meteva.method as mem
    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    path_fo = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo = meb.read_griddata_from_nc(path_fo, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")
    result = mem.space.count_index(grd_ob,grd_fo,thresholds=5)

    print(result)