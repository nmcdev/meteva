# -*-coding:utf-8-*-

import math
import sys
#sys.path.append(r'F:\Work\MODE\Submit')
from .distmap import *
import cv2
from scipy import ndimage
import meteva

def deltametric(a, b, p=2, c=float('inf')):
    if p == float('inf') or (type(p).__name__ != "str" and str(p).isnumeric() and p > 0):
        window = boundingbox(a, b)
        a = rebound(a, window)
        b = rebound(b, window)

        #dA = ndimage.morphology.distance_transform_edt(~(a['m'] == 1) + 0)
        # dB = ndimage.morphology.distance_transform_edt(~(b['m'] == 1) + 0)
        dA = cv2.distanceTransform(np.array(~(a['m'] == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
        dB = cv2.distanceTransform(np.array(~(b['m'] == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
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
