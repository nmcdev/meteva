import numpy as np
from . import mij
import math


def imomenter(x, loc=None):
    x = np.array(x)
    out = {}
    if loc is None:
        xdim = x.shape
        range0 = np.tile(np.arange(xdim[0]), xdim[1])
        range1 = (np.arange(xdim[1])).repeat(xdim[0])
        loc = np.stack((range0, range1), axis=-1)
    m00 = mij.mij(x, s=np.array(loc))
    m10 = mij.mij(x, s=np.array(loc), i=1)
    m01 = mij.mij(x, s=np.array(loc), j=1)
    m11 = mij.mij(x, s=np.array(loc), i=1, j=1)
    m20 = mij.mij(x, s=np.array(loc), i=2)
    m02 = mij.mij(x, s=np.array(loc), j=2)
    xbar = m10 / m00
    ybar = m01 / m00
    cen = {'x': xbar, 'y': ybar}
    mu11 = m11 / m00 - xbar * ybar
    mu20 = m20 / m00 - math.pow(xbar, 2)
    mu02 = m02 / m00 - math.pow(ybar, 2)
    theta = 0.5 * math.atan2(2 * mu11, mu20 - mu02)
    out["area"] = m00
    out["centroid"] = cen
    out["orientation_angle"] = theta
    raw = {"m00": m00, "m10": m10, "m01": m01, "m11": m11, "m20": m20, "m02": m02}
    out["raw.moments"] = raw
    out["cov"] = np.array([[mu20, mu11], [mu11, mu02]])
    out["class"] = "imomented"
    return out
