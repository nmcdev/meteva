# -*- coding: utf-8 -*-
"""
Created on Thu Aug  6 10:53:50 2020

@author: 1
"""
import numpy as np
from scipy import ndimage
#import rpy2.robjects as robjects
import sys


def censqdelta(x, y, N, const, p):

    #检查x、y是否二值化
    
    xdim = np.shape(x)
    rep00_1 = np.arange(1, xdim[0] + 1, 1)
    rep00 = np.tile(rep00_1, xdim[1])
    rep0_1 = np.arange(1, xdim[1] + 1, 1)
    rep0 = rep0_1.repeat(xdim[0], axis = 0)    #按行进行元素重复
    loc = np.vstack((rep00, rep0)).T    #数组转置array.T

    if (N == None):
        N = max(xdim)
    if (N % 2 == 0):
        N = N + 1


    xy = (x>0)|(y>0)
    
    #计算x,y合并后的形心:目标区域的行列求和除以总的行列求和

    xyloc_x = np.argwhere(xy == 1)[:, 0]    #合并以后图形的x坐标
    xyloc_y = np.argwhere(xy == 1)[:, 1]    #合并以后图形的y坐标
    xycen = np.array([sum(xyloc_x)/len(xyloc_x), sum(xyloc_y)/len(xyloc_y)])    #两个object合并以后的形心坐标
    
    
    #robjects.r('''
    #       f <- function(N){cbind(rep(1:N, N), rep(1:N, each = N))}
    #       ''')
    #bigDloc = np.array(robjects.r['f'](int(N)))    # N必须是int
    bigDcen = np.array((N-1)/2 + 1).repeat(2,axis = 0).reshape(1, 2)
    cendiff = np.array(bigDcen - xycen).reshape(1, 2)
    xloc = np.argwhere(x == 1)
    yloc = np.argwhere(y == 1)
    idX = xloc + cendiff.repeat(len(xloc),axis = 0)    #将cendiff变为矩阵，len = len(xloc)
    idY = yloc + cendiff.repeat(len(yloc),axis = 0)
    #勿删
    #goodIDx = np.array([j for i in idX for j in i if j >= 1 and j <= N])
    #goodIDy = np.array([j for i in idY for j in i if j >= 1 and j <= N])
    goodIDx = np.where((idX >= 1)&(idX <= N),True,False)    #多条件查询，满足条件返回True,不满足条件返回False
    goodIDy = np.where((idY >= 1)&(idY <= N),True,False)    #多条件查询，满足条件返回True,不满足条件返回False

    if (goodIDx.any() == False):
        print("warning message:\ncensqdelta: centering pushes observed data outside of new domain.  Removing some data.  Maybe choose larger N?")
        if (goodIDx.all() == False):
            try:
                sys.exit(0)
            except:
                print("censqdelta: No observed data remains after centering in this domain.")
        idX = np.array([j for i in idX for j in i if j == True])

    if (goodIDy.any() == False):
        print("warning message:\ncensqdelta: centering pushes forecast data outside of new domain.  Maybe choose larger N?")
        if (goodIDy.all() == False):
            try:
                sys.exit(0)
            except:
                print("censqdelta: No forecast data remains after centering in this domain.")
        idY = np.array([j for i in idY for j in i if j == True])    

    X = np.zeros(shape = (N, N), dtype = float)    #大小为N的0矩阵
    Y = np.zeros(shape = (N, N), dtype = float)
    #print(idX.shape)
    idx1 = idX[:,0].astype(np.int16)
    idx1[idx1<0] = 0
    idx1[idx1 >= N-1] = N-1
    idx2 = idX[:,1].astype(np.int16)
    idx2[idx2<0] = 0
    idx2[idx2 >= N-1] = N-1
    X[idx2,idx2] = 1

    #for j in np.trunc(idX).astype(int).tolist():
        # 将计算后的索引位置重新赋值为1
    #    X[j[0],j[1]] = 1


    idy1 = idY[:,0].astype(np.int16)
    idy1[idy1<0] = 0
    idy1[idy1 >= N-1] = N-1
    idy2 = idY[:,1].astype(np.int16)
    idy2[idy2<0] = 0
    idy2[idy2 >= N-1] = N-1
    Y[idy2,idy2] = 1

    #for k in np.trunc(idY).astype(int).tolist():
        #print(k)
    #    Y[k[0],k[1]] = 1
        
    #deltametric函数
    dA = ndimage.morphology.distance_transform_edt(1-X)     #distmap函数
    dB = ndimage.morphology.distance_transform_edt(1-Y)     #distmap函数
    if float('inf') == p:
        Z = abs(dA - dB)
        delta = np.max(Z)
    else:
        Z = abs(dA - dB) ** p
        iZ = np.mean(Z)
        delta = iZ**(1/p)

    return delta
        









        
        
        
        