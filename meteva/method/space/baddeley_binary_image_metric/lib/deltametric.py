# -*-coding:utf-8-*-

import math
import sys
from scipy.spatial import cKDTree
from meteva.method.space.baddeley_binary_image_metric.lib.distmap import *


def cv2_distanceTransform(array_01):
    #计算每个格点到目标的最近距离
    nx = array_01.shape[1]
    ny = array_01.shape[0]
    index = np.where(array_01 ==0)
    xy = np.array(index).T
    tree = cKDTree(xy)
    xy_g = np.array(np.meshgrid(np.arange(ny),np.arange(nx))).T
    d,_ = tree.query(xy_g, k=1)
    d_g = d.reshape(ny,nx)
    return d_g


def deltametric(a, b, p=2, c=float('inf')):
    import cv2
    if p == float('inf') or (type(p).__name__ != "str" and str(p).isnumeric() and p > 0):
        window = boundingbox(a, b)
        a = rebound(a, window)
        b = rebound(b, window)
        # dA = ndimage.morphology.distance_transform_edt(~(a['m'] == 1) + 0)
        # dB = ndimage.morphology.distance_transform_edt(~(b['m'] == 1) + 0)
        d_a = cv2.distanceTransform(np.array(~(a['m'] == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
        d_b = cv2.distanceTransform(np.array(~(b['m'] == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
        if not math.isinf(c):
            d_a = np.minimum(d_a, c)
            d_b = np.minimum(d_b, c)
        if math.isinf(p):
            z = np.abs(d_a - d_b)
            delta = np.max(z)
        else:
            z = np.abs(d_a - d_b) ** p
            i_z = np.mean(z)
            delta = i_z ** (1.0 / p)
        return delta
    else:
        print("p类型错误")
        raise Exception("p类型错误")
