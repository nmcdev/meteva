import numpy as np
import meteva
from scipy.ndimage import convolve
from meteva.method.space.mode.distmap import getRedDotsCoordinatesFromLeftToRight
from meteva.method.space.mode.feature_axis import convexHull
from shapely.geometry import Polygon
import copy

def area_index(grd_ob,grd_fo,thresholds):
    '''

    :param grd_ob: 观测网格数据
    :param grd_fo: 预报网格数据
    :param threholds: 等级阈值
    :return:
    '''
    x = copy.deepcopy(grd_ob.values.squeeze())
    aindex_x = aindex(x,thresh=thresholds)
    y = copy.deepcopy(grd_fo.values.squeeze())
    aindex_y = aindex(y, thresh=thresholds)
    resulut = {"area_index":[aindex_x["area_index"],aindex_y["area_index"]],
               "total_area":[aindex_x["total_area"],aindex_y["total_area"]],
               "total_convex_area":[aindex_x["total_convex_area"],aindex_y["total_convex_area"]]}
    return resulut

def aindex(x, thresh=None,dx = 1,dy = 1):
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
    sm1 = np.zeros(x.shape)
    sm1[sm >= thresh1] = 1
    area_all = np.count_nonzero(sx) * dx * dy
    label_array = meteva.method.mode.measure_label(sm1)  #转换成label矩阵
    num_obj =int(np.max(label_array))  #连通域的数量
    area_list = []
    for i in range(1,num_obj+1):
        label_one = np.zeros(x.shape)
        label_one[label_array==i] = 1
        rx = getRedDotsCoordinatesFromLeftToRight(label_one)   #所以label的格点坐标
        pts = convexHull(rx)     #求凸包络线
        polygon = Polygon(pts)          #计算包络线面积
        area_list.append(polygon.area)
    area_array = np.array(area_list)
    #a_convex = np.max(area_array)  # 获取包络线面积最大值
    a_convex = np.sum(area_array) # 获取包络线面积和
    area_index = area_all / a_convex   # 所有目标的格点面积和 与最大包络面积之比
    #res = pd.DataFrame({"area_index": area_index, "area_all": area_all, "Aconvex": a_convex, "dx": dx, "dy": dy}, index=[0])
    res = {"area_index": area_index, "total_area": area_all, "total_convex_area": a_convex}
    return res





# def aindex_cv(x, thresh=None, dx=1, dy=1):
#     if thresh is None:
#         thresh = 1e-08
#     sx = x
#     sx[sx >= thresh] = 255
#     sx[sx < thresh] = 0
#     cv2.imwrite("pic/aindex/data.png", sx)
#     img = cv2.imread("pic/aindex/data.png")
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#     blur = cv2.blur(gray, (3, 3))
#     ret, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)
#     contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)  #
#     hull = []
#     for i in range(len(contours)):
#         hull.append(cv2.convexHull(contours[i], False))
#     drawing = np.zeros((thresh.shape[0], thresh.shape[1], 3), np.uint8)
#     for i in range(len(contours)):
#         color_contours = (0, 255, 0)  # green - color for contours
#         color = (255, 0, 0)  # blue - color for convex hull
#         cv2.drawContours(drawing, hull, i, color, 1, 8)
#     cv2.imwrite("pic/aindex/mask.png", drawing)
#     cv2.imwrite("pic/aindex/all.png", cv2.add(drawing, img))
#     a = np.count_nonzero(sx) * dx * dy
#     a_convex = cv2.contourArea(hull[0]) * dx * dy  # 面积最大的目标的包络线内的面积
#     a_index = a / a_convex
#     res = pd.DataFrame({"Aindex": a_index, "A": a, "Aconvex": a_convex, "dx": dx, "dy": dy}, index=[0])
#     return res


if __name__ == '__main__':
    #geom000 = pyreadr.read_r('./data/geom000.Rdata')['geom000']
    # sns.heatmap(pd.DataFrame(geom000))
    # plt.show()
    # sx = geom000.values
    # thresh = 1e-08
    # sx[sx >= thresh] = 255
    # sx[sx < thresh] = 0
    # image = Image.fromarray(sx)
    # image.show()

    import meteva.base as meb
    import math
    import meteva.method as mem
    # grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    # path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    # grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    # obs_array = grd_ob.values.squeeze()
    # res = aindex(obs_array)
    # print(res)

    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    dat_ob = np.zeros((grid1.nlat, grid1.nlon))
    for j in range(grid1.nlat):
        for i in range(grid1.nlon):
            dat_ob[j, i] = 20 * math.exp(-0.001 * (i - 200) ** 2 - 0.001 * (j - 200) ** 2)
    grd_ob = meb.grid_data(grid1, dat_ob)

    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    dat_fo = np.zeros((grid1.nlat, grid1.nlon))
    for j in range(grid1.nlat):
        for i in range(grid1.nlon):
            dat_fo[j, i] = 10 * math.exp(-0.001 * (i - 240) ** 2 - 0.0003 * (j - 240) ** 2)
            dat_fo[j, i] += 10 * math.exp(-0.001 * (i - 170) ** 2 - 0.0003 * (j - 170) ** 2)
    grd_fo = meb.grid_data(grid1, dat_fo)

    result = mem.space.area_index(grd_ob,grd_fo,thresholds=5)
    print(result)