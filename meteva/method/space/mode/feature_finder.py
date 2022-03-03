# -*- coding: utf-8 -*-
"""
Created on Fri Jul 10 14:58:07 2020

@author: 1
"""

#============================  FeatureFinder()  ==============================
#Function:Identify spatial features within a verification set using a threshold-based method.

#from skimage import measure,color
import numpy as np
import sys
import meteva
import math
from scipy.ndimage import convolve
from queue import Queue

def measure_label(arr0):
    arr = np.zeros((arr0.shape[0]+2,arr0.shape[1]+2)) > 1
    arr[1:-1,1:-1] = arr0[:,:]
    nx = arr.shape[1]
    ny = arr.shape[0]
    label = np.zeros(arr.shape)
    num = 0
    for j in range(1, ny - 1):
        for i in range(1,nx-1):
            if arr[j,i] and label[j,i] == 0:
                num = num + 1
                label[j,i] = num
                qu = Queue(maxsize=0)
                qu.put([j,i])
                while not qu.empty():
                    ji = qu.get()
                    for p in range(-1,2):
                        for q in range(-1,2):
                            if label[ji[0]+p,ji[1]+q] ==0 and arr[ji[0]+p,ji[1]+q]:
                                qu.put([ji[0]+p,ji[1]+q])
                                label[ji[0] + p, ji[1] + q] = num

    label_c = label[1:-1,1:-1]

    return label_c


def get_disk_kernel(r):
    r2 = r * r
    rint = math.ceil(r - 0.5)
    diskg = np.arange(-rint, rint + 1, 1)
    n = len(diskg)
    x, y = np.meshgrid(diskg, diskg)
    xy = np.array([x, y])
    abmax = np.max(np.abs(xy), axis=0)
    abmin = np.min(np.abs(xy), axis=0)
    hold = np.full((n, n), np.nan)
    tmp1 = np.full((n, n), np.nan)
    tmp2 = np.full((n, n), np.nan)
    val = (abmax + 0.5) ** 2 + (abmin - 0.5) ** 2
    id1 = (r2 < val)
    id2 = (r2 >= val)

    tmp1[id1] = abmin[id1] - 0.5
    tmp1[id2] = np.sqrt(r2 - (abmax[id2] + 0.5) ** 2)
    val = (abmax - 0.5) ** 2 + (abmin + 0.5) ** 2

    id1 = r2 < val
    id2 = r2 >= val

    tmp2[id1] = abmin[id1] + 0.5
    tmp2[id2] = np.sqrt(r2 - (abmax[id2] - 0.5) ** 2)

    val1 = (abmax + 0.5) ** 2 + (abmin + 0.5) ** 2
    hold_id1 = (r2 < val1) & (r2 > ((abmax - 0.5) ** 2 + (abmin - 0.5) ** 2))
    hold_id2 = ((abmin == 0) & (abmax - 0.5 < r) & (abmax + 0.5 >= r))
    hold_id = hold_id1 | hold_id2

    hold[hold_id] = (r2 * (0.5 * (np.arcsin(tmp2[hold_id] / r) - np.arcsin(tmp1[hold_id] / r))
                           + 0.25 * (np.sin(2 * np.arcsin(tmp2[hold_id] / r)) - np.sin(
                2 * np.arcsin(tmp1[hold_id] / r)))
                           )
                     - (abmax[hold_id] - 0.5) * (tmp2[hold_id] - tmp1[hold_id])
                     + (tmp1[hold_id] - abmin[hold_id] + 0.5))

    hold[np.isnan(hold)] = 0
    hold = hold + (val1 < r2)
    hold[rint, rint] = min(math.pi * r2, math.pi / 2)
    rc2 = rint - 0.5
    if (rint > 0) and (r > rc2) and (r2 < (rc2 ** 2 + 0.25)):
        tmp1 = math.sqrt(r2 - rc2 ** 2)
        tmp1n = tmp1 / r
        hold0 = 2 * (r2 * (0.5 * np.arcsin(tmp1n) + 0.25 * np.sin(2 * np.arcsin(tmp1n))) - tmp1 * (rint - 0.5))
        hold[2 * rint, rint] = hold0
        hold[rint, 2 * rint] = hold0
        hold[rint, 0] = hold0
        hold[0, rint] = hold0
        hold[2 * rint - 1, rint] = hold[2 * rint - 1, rint] - hold0
        hold[rint, 2 * rint - 1] = hold[rint, 2 * rint - 1] - hold0
        hold[rint, 1] = hold[rint, 1] - hold0
        hold[1, rint] = hold[1, rint] - hold0
    hold[rint, rint] = min(hold[rint, rint], 1)
    sn = np.sum(hold)
    kernel = hold/sn
    return kernel

def get_disk_kernel_1(r):
    x = np.arange(-r,r+1)
    y = np.arange(-r,r+1)
    xx,yy = np.meshgrid(x,y)
    DD = r**2 - xx**2 - yy**2+1
    DD[DD<0] = 0
    DD[DD>0] = 1
    sum1 = np.sum(DD)
    kernel = DD/sum1
    return kernel


#start = time.clock()    #开始时间

#连通域标记
# def labelsConnection(data):
#     labels=measure.label(data,connectivity=2)  #connectivity表示连接的模式，1代表4连通，2代表8连通
#     meteva.base.mesh(labels,save_path=r"H:\test_data\output\method\space\mode\label.png")
#     dst=color.label2rgb(labels)  #根据不同的标记显示不同的颜色
#     #print('regions number:',labels.max()+1)  #显示连通区域块数(从0开始标记)
#
#     return dst

#每个连通域内格点数统计,并且判断格点数量是否在阈值范围内
def propCounts(data_2, minsize, maxsize):
    labels = measure_label(data_2)
    #labels = measure.label(data_2,connectivity=2)

    valid_label = []
    area = []
    current_bw = np.array(())
    max_label = int(np.max(labels))
    labelsfeature = {}
    # for prop in properties:
    #     nums.append(prop.area)    #统计连通域内的格点数
    #
    # numsID = list(map(lambda x :any(x > [minsize]) and any(x < [maxsize]), nums))    #比较格点数是否在阈值范围内

    nums = []
    numsID = []
    for i in range(1,max_label+1):
        index = np.where(labels ==i)
        count = len(index[0])
        nums.append(count)
        numsID.append(count>minsize and count<maxsize)
    for i in range(len(numsID)):
        if numsID[i]:
            valid_label_0 = i
            area_0 = nums[i]
            area.append(area_0)
            #print(numsID[i], valid_label_0)
            valid_label.append(valid_label_0)
            current_bw = np.in1d(labels, list(valid_label)).reshape(labels.shape)
            #labels = prop._label_image    #读取的prop._label_image数据是已经进行过旋转的结果


    for i in range(len(valid_label)):
        n = valid_label[i]
        #print(n)
        #f = np.where(labels, labels == n + 1, 0)
        #print(f.size)
        f = np.where(labels == n+1)
        f = {(i + 1):f}
        labelsfeature.update(f)
        #添加属性
        xrange = [0.5, np.shape(data_2)[1] + 0.5]
        yrange = [0.5, np.shape(data_2)[0] + 0.5]
        dim = np.shape(data_2)
        xcol = np.arange(1, np.shape(data_2)[1] + 1, 1)
        yrow = np.arange(1, np.shape(data_2)[0] + 1, 1)

        warnings = ["Row index corresponds to increasing y coordinate; column to increasing x",
                    "Transpose matrices to get the standard presentation in R",
                    "Example: image(result$xcol,result$yrow,t(result$d))"]
        labelsfeature.update({'Type':'mask', 'xrange': xrange, 'yrange': yrange,
                              'dim': dim, 'xstep': 1, 'ystep': 1, 'area': area, 
                              'warnings': warnings, 'xcol':xcol, 'yrow':yrow})
    labelsfeature["label_count"]=len(valid_label)
    #print(labelsfeature)
    properties = None
    return nums, numsID, current_bw, properties, labelsfeature

#R里面新定义的Nfun函数，求和函数,实际函数功能是统计连通域内面积大小,python用prop.area代替
def newFun(Obj):
    #axis为:1：计算每一行的和，axis为0：计算每一列的和,keepdims为保持原有维度
    return np.sum(np.sum(Obj, axis=0, keepdims=True))

#
# def feature_finder_bak(grd_ob, grd_fo, smooth, threshold, minsize, maxsize=float("Inf"),
#                    do_smooth=True):
#     # 读观测数据
#     # dataset_ob = xr.open_dataset(filename_ob)  #通过xarray程序库读取nc文件中的所有内容
#     # X = np.squeeze(grd_ob.variables['data0'])
#
#     # 读预报数据
#     # dataset_fcst = xr.open_dataset(filename_fo)  #通过xarray程序库读取nc文件中的所有内容
#     # Xhat = np.squeeze(grd_fo.variables['data0'])
#
#     X = np.squeeze(np.array(grd_ob))
#     Xhat = np.squeeze(np.array(grd_fo))
#
#     # 读经纬度，并形成R里面的格式
#     lon = grd_ob['lon']
#     lat = grd_ob['lat']
#     X_lon, Y_lat = np.meshgrid(lon, lat)
#     loc1 = X_lon.reshape(X_lon.size, order='F')
#     loc2 = Y_lat.reshape(Y_lat.size, order='F')
#     loc = np.vstack((loc1, loc2)).T
#
#     Object = {"grd_ob": X, "grd_fo": Xhat, "loc": loc}  # hold是make_saptialVx的计算结果
#     thresh = threshold
#     smoothpar = smooth
#     smoothfun = "disk2dsmooth"
#     smoothfunargs = None
#     idfun = "disjointer"
#     zerodown = False
#     timepoint = 1
#     obs = 1
#     model = 1
#     fac = 1
#
#     if type(minsize) == list:
#         minsize = np.array(minsize)
#     if type(maxsize) == list:
#         maxsize = np.array(maxsize)
#     if type(smooth) == list:
#         smooth = np.array(smooth)
#     if type(thresh) == list:
#         thresh = np.array(thresh)
#
#         # theCall <- match.call()    #调用match函数
#
#     if (np.size(minsize) == 1):
#         minsize = np.tile(minsize, 2)  # 输入观测和预报数据，因而将最小值和最大值展开为两个数
#     if (np.size(maxsize) == 1):  # error:object of type 'float' has no len()
#         maxsize = np.tile(maxsize, 2)
#
#     if (len(minsize) != 2):
#         try:
#             sys.exit(0)
#         except:
#             print("FeatureFinder: invalid min.size argument.  Must have length one or two.")
#     if (len(maxsize) != 2):
#         try:
#             sys.exit(0)
#         except:
#             print("FeatureFinder: invalid max.size argument.  Must have length one or two.")
#     if (any(minsize) < 1):  # a为list
#         try:
#             sys.exit(0)
#         except:
#             print("FeatureFinder: invalid min.size argument.  Must be >= 1.")
#     if (any(maxsize) < any(minsize)):
#         try:
#             sys.exit(0)
#         except:
#             print("FeatureFinder: invalid max.size argument.  Must be >= min.size argument.")
#     a = Object.copy()
#     dat = {'ob': Object['grd_ob'], 'fo': Object['grd_fo']}  # 引用hold里的X,Xhat要素并赋值
#     X = dat['ob']
#     Y = dat['fo']
#     xdim = X.shape
#
#     if (do_smooth):
#         if (np.size(smoothpar) == 1):
#             smoothpar = np.tile(smoothpar, 2)  # 观测场和预报场的平滑参数一致
#         elif (len(smoothpar) > 2):
#             try:
#                 sys.exit(0)
#             except:
#                 print("FeatureFinder: invalid smoothpar argument.  Must have length one or two.")
#
#         # 调用disk2dsmooth中的kernel2dsmooth卷积平滑，python里面目前用2D卷积平滑替代
#         kernel_X = np.ones((smoothpar[0], smoothpar[0]), np.float32) / 5  # X的卷积核
#         kernel_Y = np.ones((smoothpar[1], smoothpar[1]), np.float32) / 5  # Y的卷积核
#         #Xsm = cv.filter2D(np.rot90(X, 4), -1, kernel_X)  # 对X做2D卷积平滑,旋转4次=没有旋转，不做旋转会报错（opencv版本问题）
#         Xsm = convolve(X, kernel_X)
#         #Ysm = cv.filter2D(np.rot90(Y, 4), -1, kernel_Y)  # 对Y做2D卷积平滑,旋转4次=没有旋转，不做旋转会报错（opencv版本问题）
#         Ysm = convolve(Y, kernel_Y)
#         if (zerodown):
#             Xsm = np.where(Xsm > 0, Xsm, 0)  # Xsm中大于0的值被0代替
#             Ysm = np.where(Ysm > 0, Ysm, 0)  # Ysm中大于0的值被0代替
#     else:
#         Xsm = X
#         Ysm = Y
#
#     if (np.size(thresh) == 1):
#         thresh = np.tile(thresh, 2)
#     thresh = thresh * fac
#     # 二值化，首先生成0矩阵，然后将大于阈值的部分赋值为1
#     # 但是python里面在进行连通域分析的时候已经进行过二值化，不必单独进行二值化
#     # sIx = np.zeros((xdim[0], xdim[1]))
#     # sIy = np.zeros((xdim[0], xdim[1]))
#     # sIx = np.where(Xsm < thresh[0], Xsm, 1)
#     # sIy = np.where(Ysm < thresh[1], Xsm, 1)
#
#     # 连通域分析
#     # 连通域分析的时候，分析的是经过模糊处理的图像
#     # R里面的阈值为5,2D卷积平滑时增强图像，阈值设为310才能结果对应
#     Xfeats = labelsConnection(Xsm > thresh[0])
#     Yfeats = labelsConnection(Ysm > thresh[1])
#     if (len(Xfeats) == 0):
#         Xfeats = None
#     if (len(Yfeats) == 0):
#         Yfeats = None
#     # 如果对连通域的面积大小做限制，则需要执行下面的判断
#     if (any(minsize > 1) or any(maxsize < X.size)):
#         # 统计每个连通域内的格点数
#         if (np.all(Xfeats) != None):
#             Xnums = propCounts(np.rot90(Xsm > thresh[0], 4), minsize[0], maxsize[0])[0]
#             XnumsID = propCounts(np.rot90(Xsm > thresh[0], 4), minsize[0], maxsize[0])[1]
#             Xfeats = propCounts(np.rot90(Xsm > thresh[0], 4), minsize[0], maxsize[0])[2]
#             Xprop = propCounts(np.rot90(Xsm > thresh[0], 4), minsize[0], maxsize[0])[3]
#
#         if (np.all(Yfeats) != None):
#             Ynums = propCounts(np.rot90(Ysm > thresh[1], 4), minsize[1], maxsize[1])[0]
#             YnumsID = propCounts(np.rot90(Ysm > thresh[1], 4), minsize[1], maxsize[1])[1]
#             Yfeats = propCounts(np.rot90(Ysm > thresh[1], 4), minsize[1], maxsize[1])[2]
#             Yprop = propCounts(np.rot90(Ysm > thresh[1], 4), minsize[1], maxsize[1])[3]
#
#     # Xlab = np.zeros(xdim[0], xdim[1])
#     # Ylab = np.zeros(xdim[0], xdim[1])
#
#     if (np.all(Xfeats) != None):
#         Xlab = Xfeats
#     else:
#         Xfeats = None
#
#     if (np.all(Yfeats) != None):
#         Ylab = Yfeats
#     else:
#         Yfeats = None
#
#         # 返回的out列表里面包括:观测数据（X）,预报数据（Xhat），连通域分析后单个区域（X.feats,Yfeats）并包括了很多的属性信息
#     # X.feats,Yfeats包括了很多的属性信息：x,y的范围xrange,yrange，维度dim,步长xstep,ystep,行列信息等；标记后的连通域（Xlab,Ylab）；
#     # 识别函数、标记函数名称：Convolution Threshold。
#     Xprop = propCounts(Xsm > thresh[0], minsize[0], maxsize[0])[3]
#     Yprop = propCounts(Ysm > thresh[1], minsize[1], maxsize[1])[3]
#     Xlabelsfeature = propCounts(Xsm > thresh[0], minsize[0], maxsize[0])[4]
#     Ylabelsfeature = propCounts(Ysm > thresh[1], minsize[1], maxsize[1])[4]
#
#     '''
#     out = {'ob':Object['ob'], 'fo':Object['fo'], 'loc':Object['loc'], "Xlabeled":Xfeats, "Ylabeled":Yfeats,
#            "identifier_function" : "convthresh", "identifier_label" : "Convolution Threshold",
#            "attr_timepoint" : "time_point", "attr_model": "model", "attr_call": "theCall",
#            "Xprop":Xprop, "Yprop":Yprop, "Xlabelsfeature":Xlabelsfeature, "Ylabelsfeature":Ylabelsfeature}
#     '''
#     out = {'grd_ob': Object['grd_ob'], 'grd_fo': Object['grd_fo'], 'loc': Object['loc'],
#            "grd_ob_labeled": Xfeats, "grd_fo_labeled": Yfeats,
#            "identifier_label": "Convolution Threshold",
#            "grd_ob_prop": Xprop, "grd_fo_prop": Yprop,
#            "grd_ob_features": Xlabelsfeature, "grd_fo_features": Ylabelsfeature}
#
#     Xlabels = data_pre.pick_labels(copy.deepcopy(Xlabelsfeature))
#     xtmp = Xlabels.copy()
#     Xlabeled = data_pre.relabeled(xtmp)
#     Ylabels = data_pre.pick_labels(copy.deepcopy(Ylabelsfeature))
#     ytmp = Ylabels.copy()
#     Ylabeled = data_pre.relabeled(ytmp)
#     out.update({"grd_ob_labeled": Xlabeled, "grd_fo_labeled": Ylabeled})
#     # 每个格点的长、宽
#     a = np.unique(out['loc'][:, 0])[1] - np.unique(out['loc'][:, 0])[0]  # 第一列为经度间隔
#     b = np.unique(out['loc'][:, 1])[1] - np.unique(out['loc'][:, 1])[0]  # 第二列为维度间隔
#     S = a * b
#     ob_area = (np.array(out['grd_ob_features']['area']) * S).tolist()
#     out['grd_ob_features']['area'] = ob_area
#
#     print(out['grd_fo_features'])
#     fo_area = (np.array(out['grd_fo_features']['area']) * S).tolist()
#     out['grd_fo_features']['area'] = fo_area
#     out["grid"] = meteva.base.get_grid_of_data(grd_ob)
#     return out

def feature_finder(grd_ob0, grd_fo0, smooth, threshold, minsize, maxsize = float("Inf")):
    
    #读观测数据
    #dataset_ob = xr.open_dataset(filename_ob)  #通过xarray程序库读取nc文件中的所有内容
    #X = np.squeeze(grd_ob.variables['data0'])
    
    #读预报数据
    #dataset_fcst = xr.open_dataset(filename_fo)  #通过xarray程序库读取nc文件中的所有内容
    #Xhat = np.squeeze(grd_fo.variables['data0'])

    grd_ob = grd_ob0.copy()
    grd_ob.attrs["var_name"] = "原始场"
    grd_fo = grd_fo0.copy()
    grd_fo.attrs["var_name"] = "原始场"

    X = np.squeeze(np.array(grd_ob)).astype(np.float32)
    Xhat = np.squeeze(np.array(grd_fo)).astype(np.float32)
    
    #读经纬度，并形成R里面的格式
    lon = grd_ob['lon']
    lat = grd_ob['lat']    
    X_lon, Y_lat = np.meshgrid(lon, lat)
    loc1 = X_lon.reshape(X_lon.size, order = 'F')
    loc2 = Y_lat.reshape(Y_lat.size, order = 'F')
    loc = np.vstack((loc1, loc2)).T    
    
    Object = {"grd_ob": X, "grd_fo": Xhat, "loc":loc}    #hold是make_saptialVx的计算结果
    thresh = threshold


    smoothfun = "disk2dsmooth"
    smoothfunargs = None
    idfun = "disjointer"
    zerodown = False
    timepoint = 1
    obs = 1
    model = 1
    fac = 1

    if not isinstance(smooth,list):
        smooth = [smooth,smooth]

    if not isinstance(minsize,list):
        minsize = [minsize,minsize]

    if not isinstance(maxsize,list):
        maxsize = [maxsize,maxsize]

    if not isinstance(thresh,list):
        thresh = [thresh,thresh]


    
    #theCall <- match.call()    #调用match函数

    if (np.size(minsize) == 1):
        minsize = np.tile(minsize, 2)        #输入观测和预报数据，因而将最小值和最大值展开为两个数
    if (np.size(maxsize) == 1):    #error:object of type 'float' has no len()
        maxsize = np.tile(maxsize, 2)
        
    if (len(minsize) != 2):
        try:
            sys.exit(0)
        except:
            print("FeatureFinder: invalid min.size argument.  Must have length one or two.")
    if (len(maxsize) != 2):
        try:
            sys.exit(0)
        except:
            print("FeatureFinder: invalid max.size argument.  Must have length one or two.")
    if (any(minsize) < 1):    #a为list
        try:
            sys.exit(0)
        except:
            print("FeatureFinder: invalid min.size argument.  Must be >= 1.")
    if (any(maxsize) < any(minsize)):
        try:
            sys.exit(0)
        except:
            print("FeatureFinder: invalid max.size argument.  Must be >= min.size argument.")
    a = Object.copy() 
    dat = {'ob':Object['grd_ob'], 'fo':Object['grd_fo']}    #引用hold里的X,Xhat要素并赋值
    X = dat['ob']
    Y = dat['fo']
    xdim = X.shape

    if not isinstance(smooth,list):
        smooth = [smooth,smooth]

    if smooth[0]>0:

        kernel_X = get_disk_kernel(smooth[0])
        #Xsm = cv.filter2D(np.rot90(X, 4), -1, kernel_X)    #对X做2D卷积平滑,旋转4次=没有旋转，不做旋转会报错（opencv版本问题）
        #Xsm = cv.filter2D(X, -1, kernel_X)  # 对X做2D卷积平滑,旋转4次=没有旋转，不做旋转会报错（opencv版本问题）

        Xsm = convolve(X, kernel_X)
        if (zerodown):
             Xsm = np.where(Xsm > 0, Xsm, 0)    #Xsm中大于0的值被0代替
    else:
        Xsm = X

    grd_ob_smooth = grd_ob.copy()
    grd_ob_smooth.attrs["var_name"] = "平滑场"
    grd_ob_smooth[:] = Xsm[:]


    if smooth[1] >0:
        kernel_Y = get_disk_kernel(smooth[1])
        #Ysm = cv.filter2D(np.rot90(Y, 4), -1, kernel_Y)  # 对Y做2D卷积平滑,旋转4次=没有旋转，不做旋转会报错（opencv版本问题）
        Ysm = convolve(Y, kernel_Y)
        if (zerodown):
            Ysm = np.where(Ysm > 0, Ysm, 0)  # Ysm中大于0的值被0代替
    else:
        Ysm = Y

    grd_fo_smooth = grd_fo.copy()
    grd_fo_smooth.attrs["var_name"] = "平滑场"
    grd_fo_smooth[:] = Ysm[:]

    if (np.size(thresh) == 1):
        thresh = np.tile(thresh, 2)
    thresh = thresh * fac
    #二值化，首先生成0矩阵，然后将大于阈值的部分赋值为1
    #但是python里面在进行连通域分析的时候已经进行过二值化，不必单独进行二值化
    #sIx = np.zeros((xdim[0], xdim[1]))
    #sIy = np.zeros((xdim[0], xdim[1]))
    #sIx = np.where(Xsm < thresh[0], Xsm, 1)
    #sIy = np.where(Ysm < thresh[1], Xsm, 1)
    
    #连通域分析
    #连通域分析的时候，分析的是经过模糊处理的图像
    #R里面的阈值为5,2D卷积平滑时增强图像，阈值设为310才能结果对应
    # Xfeats = labelsConnection(Xsm > thresh[0])
    # Yfeats = labelsConnection(Ysm > thresh[1])
    # if (len(Xfeats) == 0):
    #     Xfeats = None
    # if (len(Yfeats) == 0):
    #     Yfeats = None
    #如果对连通域的面积大小做限制，则需要执行下面的判断


    # if minsize[0] > 1 or maxsize[0] < X.size:
    #     #统计每个连通域内的格点数
    #     if (np.all(Xfeats) != None):
    #         Xnums = propCounts(np.rot90(Xsm > thresh[0], 4), minsize[0], maxsize[0])[0]
    #         XnumsID = propCounts(np.rot90(Xsm > thresh[0], 4), minsize[0], maxsize[0])[1]
    #         Xfeats = propCounts(np.rot90(Xsm > thresh[0], 4), minsize[0], maxsize[0])[2]
    #         Xprop = propCounts(np.rot90(Xsm > thresh[0], 4), minsize[0], maxsize[0])[3]
    #
    # if minsize[1] > 1 or minsize[1] < X.size:
    #     if (np.all(Yfeats) != None):
    #         Ynums = propCounts(np.rot90(Ysm > thresh[1], 4), minsize[1], maxsize[1])[0]
    #         YnumsID = propCounts(np.rot90(Ysm > thresh[1], 4), minsize[1], maxsize[1])[1]
    #         Yfeats = propCounts(np.rot90(Ysm > thresh[1], 4), minsize[1], maxsize[1])[2]
    #         Yprop = propCounts(np.rot90(Ysm > thresh[1], 4), minsize[1], maxsize[1])[3]

    
    #Xlab = np.zeros(xdim[0], xdim[1])
    #Ylab = np.zeros(xdim[0], xdim[1])
    
    # if (np.all(Xfeats) != None):
    #     Xlab = Xfeats
    # else:
    #     Xfeats = None
    #
    # if (np.all(Yfeats) != None):
    #     Ylab = Yfeats
    # else:
    #     Yfeats = None
    
    #返回的out列表里面包括:观测数据（X）,预报数据（Xhat），连通域分析后单个区域（X.feats,Yfeats）并包括了很多的属性信息
    #X.feats,Yfeats包括了很多的属性信息：x,y的范围xrange,yrange，维度dim,步长xstep,ystep,行列信息等；标记后的连通域（Xlab,Ylab）；
    #识别函数、标记函数名称：Convolution Threshold。
    Xprop = propCounts(Xsm > thresh[0], minsize[0], maxsize[0])[3]
    Yprop = propCounts(Ysm > thresh[1], minsize[1], maxsize[1])[3]
    Xlabelsfeature = propCounts(Xsm > thresh[0], minsize[0], maxsize[0])[4]
    Ylabelsfeature = propCounts(Ysm > thresh[1], minsize[1], maxsize[1])[4]

    out = {'grd_ob':grd_ob, 'grd_fo':grd_fo,
           "grd_ob_smooth":grd_ob_smooth,"grd_fo_smooth":grd_fo_smooth,
           "grd_ob_label":None, "grd_fo_label":None,
           "identifier_label" : "Convolution Threshold",
           "grd_ob_prop":Xprop, "grd_fo_prop":Yprop,
           "grd_ob_features":Xlabelsfeature, "grd_fo_features":Ylabelsfeature}

    #print(Xlabelsfeature)
    #Xlabels = data_pre.pick_labels(copy.deepcopy(Xlabelsfeature))
    grid0 = meteva.base.get_grid_of_data(grd_ob)


    grd_ob_labeled = grd_ob.copy()
    grd_ob_labeled.attrs["var_name"] = "目标编号"
    label_value = np.zeros((grid0.nlat,grid0.nlon))
    for i in range(Xlabelsfeature["label_count"]):
        label = Xlabelsfeature[i + 1]
        label_value[label] = i+1
    grd_ob_labeled.values[:] = label_value[:]

    grd_fo_labeled = grd_fo.copy()
    grd_fo_labeled.attrs["var_name"] = "目标编号"
    label_value = np.zeros((grid0.nlat,grid0.nlon))
    for i in range(Ylabelsfeature["label_count"]):
        label = Ylabelsfeature[i + 1]
        label_value[label] = i+1
    grd_fo_labeled.values[:] = label_value[:]
    #grd_fo_labeled.values[:] = Ylabeled[:]

    out.update({ "grd_ob_label":grd_ob_labeled, "grd_fo_label":grd_fo_labeled})
    #每个格点的长、宽

    #a = np.unique(out['loc'][:, 0])[1]-np.unique(out['loc'][:, 0])[0]    #第一列为经度间隔
    #b = np.unique(out['loc'][:, 1])[1]-np.unique(out['loc'][:, 1])[0]    #第二列为维度间隔
    a = grid0.dlon
    b = grid0.dlat
    S = a * b
    #if len(out["grd_ob_features"].keys())>0:
    if out["grd_ob_features"]["label_count"] >0:
            ob_area = (np.array(out['grd_ob_features']['area'])*S).tolist()
            out['grd_ob_features']['area'] = ob_area
    #if len(out["grd_fo_features"].keys())>0:
    if out["grd_fo_features"]["label_count"] > 0:
            fo_area = (np.array(out['grd_fo_features']['area'])*S).tolist()
            out['grd_fo_features']['area'] = fo_area
    out["grid"] = grid0

    return out
        
        
    
    
    
    
#=============================  Example  ===================================
'''
#make.SpatialVx参数
hold = make_SpatialVx_PA1.makeSpatialVx(X = pd.read_csv(r'F:\Work\MODE\tra_test\QPEF\QPE\0802.csv'),
                     Xhat = pd.read_csv(r'F:\Work\MODE\tra_test\QPEF\QPF\0801.csv'),
                     thresholds = [0.01, 20.01], loc = pd.read_csv("F:\\Work\\MODE\\tra_test\\FeatureFinder\\ICPg240Locs.csv"),
                     projection = True, subset = None, timevals = None, reggrid = True, 
                     Map = True, locbyrow = True, fieldtype = "Precipitation", units = ("mm/h"), 
                     dataname = "ICP Perturbed Cases", obsname = "pert000" ,modelname = "pert004",
                     q = (0, 0.1, 0.25, 0.33, 0.5, 0.66, 0.75, 0.9, 0.95) ,qs = None)
'''                    
#FeatureFinder参数
'''
Object = hold.copy()    #make.SpatialVx生成的结果
smoothfun = "disk2dsmooth"
dosmooth = True
smoothpar = 17    #卷积核的大小
smoothfunargs = None
thresh = 310    #R里面的阈值为5,2D卷积平滑增强图像，阈值设为310才能结果对应
idfun = "disjointer"
minsize = np.array([10, 5])    #判断连通域大小的下限，超过两个值的话用数组
maxsize = float("Inf")    #判断连通域大小的上限，默认无穷大,如果是数值的话，可以直接赋值，超过两个值的话用数组
fac = 1
zerodown = False
timepoint = 1
obs = 1
model = 1

look = featureFinder(Object, smoothfun, dosmooth, smoothpar, smoothfunargs,\
                     thresh, idfun, minsize, maxsize, fac, zerodown, timepoint, obs, model)
'''

'''
#thresh是阈值，翻译后是扩大了约60倍的数据
look_FeatureFinder = featureFinder(Object = hold.copy(), smoothfun = "disk2dsmooth", 
                     dosmooth = True, smoothpar = 17, smoothfunargs = None,
                     thresh = 1800, idfun = "disjointer", minsize = np.array([1]),
                     maxsize = float("Inf"), fac = 1, zerodown = False, timepoint = 1,
                     obs = 1, model = 1)

look = featureFinder(Object = hold.copy(), smoothpar = 17, thresh = 25)
'''
#计算程序运行时间
#end = time.clock()
#print('Running time: %s s'%(end-start))


















