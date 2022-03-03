# -*-coding:utf-8-*-

from .distmap import *
from scipy.spatial import cKDTree

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
    if p == float('inf') or (type(p).__name__ != "str" and str(p).isnumeric() and p > 0):
        window = boundingbox(a, b)
        a = rebound(a, window)
        b = rebound(b, window)

        #dA = cv2.distanceTransform(np.array(~(a['m'] == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
        am = np.array(~(a['m'] == 1) + 0, np.uint8)
        dA= cv2_distanceTransform(am)

        #dB = cv2.distanceTransform(np.array(~(b['m'] == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
        bm = np.array(~(b['m'] == 1) + 0, np.uint8)
        dB = cv2_distanceTransform(bm)

        if not math.isinf(c):
            dA = np.minimum(dA, c)
            dB = np.minimum(dB, c)
        if math.isinf(p):
            Z = np.abs(dA - dB)
            delta = np.max(Z)
        else:
            Z = np.abs(dA - dB) ** p
            iZ = np.mean(Z)
            delta = iZ ** (1.0 / p)
        return float(delta)
    else:
        print("p类型错误")
        raise Exception("p类型错误")
