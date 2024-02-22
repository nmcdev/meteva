# -*-coding:utf-8-*-
import numpy as np
import pandas as pd
from .lib import loc_list_setup as lls
from meteva.method.space.hausdorff_metric.lib.distmap import *
from meteva.method.space.hausdorff_metric.lib.distfun import updateMatrix
from meteva.method.space.hausdorff_metric.lib.im import im
from meteva.method.space.hausdorff_metric.lib.solutionset import solutionset

def Mean_Error_Distance(x,y):
    res = location_performance(x,y,which_stats=["med"])
    return res

def Mean_Square_Error_Distance(x,y):
    res = location_performance(x,y,which_stats=["msd"])
    return res

def Minimum_Separation_Between_Boundaries(x,y):
    res = location_performance(x,y,which_stats=["minsep"])
    res = res["minsep"]
    return res


def Pratts_Figure_of_Merit(x,y):
    res = location_performance(x,y,which_stats=["fom"])
    return res["fom"]



def partial_Hausdorff_Measure(x,y,k=4):
    res = location_performance(x,y,which_stats=["ph"],k = k)
    return res["ph"]



def modified_Hausdorff_Measure(x,y,k=4):
    res = location_performance(x,y,which_stats=["qdmapdiff"],k = k)
    return res["qdmapdiff"]


def location_performance(x,y,which_stats = None,alpha=0.1, k=4, a=None):
    xm = im(x)
    ym = im(y)
    xs = solutionset(xm)
    ys = solutionset(ym)
    res = locperf(xs, ys,which_stats = which_stats,alpha=alpha, k=k, a=a)
    return res

def locperf(X, Y, which_stats=None, alpha=0.1, k=4, a=None):
    if which_stats is None:
        which_stats = ["qdmapdiff", "med", "msd", "ph", "fom", "minsep"]
    out = lls.loc_list_setup(a, which_stats, nthresh=1)
    window = boundingbox(X, Y)
    X = rebound(X, window)
    Y = rebound(Y, window)
    # dY = ndimage.morphology.distance_transform_edt(~(Y['m'] == 1) + 0)
    # dX = ndimage.morphology.distance_transform_edt(~(X['m'] == 1) + 0)
    # z = np.array(~(X['m'] == 1) + 0, np.uint8)
    dX = updateMatrix(np.array(~(X['m'] == 1) + 0))
    dY = updateMatrix(np.array(~(Y['m'] == 1) + 0))

    # dY = cv2.distanceTransform(np.array(~(Y['m'] == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
    # dX = cv2.distanceTransform(np.array(~(X['m'] == 1) + 0, np.uint8), cv2.DIST_L2, 3, dstType=cv2.CV_32F)
    if not Y['m'].max() == 1:
        dY = np.unique(np.array(dY))
        dYcheck = False
    else:
        dYcheck = True
    if not X['m'].max() == 1:
        dXcheck = False
    else:
        dXcheck = True
    if "med" in which_stats or "msd" in which_stats or "fom" in which_stats or "minsep" in which_stats or "ph" in which_stats:
        if dYcheck:
            Z = (np.array(dY))[(X["m"] == 1)]
        elif X['m'].max() == 1:
            Z = dY
        else:
            Z = 0
        if dXcheck:
            Zother = np.array(dX)[(Y["m"] == 1)]
        elif Y['m'].max() == 1:
            Zother = dX
        else:
            Zother = 0
    if "msd" in which_stats or "fom" in which_stats:
        Z2 = Z ** 2
        Zother2 = Zother ** 2
        if "fom" in which_stats:
            if dYcheck and dXcheck:
                N = max(np.sum(X["m"]), np.sum(Y["m"]))
            elif dYcheck and not dXcheck:
                N = np.sum(Y["m"])
            elif not dYcheck and dXcheck:
                N = np.sum(X["m"])
            else:
                N = 1e+16
    if "ph" in which_stats:
        if k < 1 or k < np.sum(X["m"]) or k < np.sum(Y["m"]):
            if dXcheck or dYcheck:
                if k >= 1:
                    if k > np.sum(X["m"]):
                        out['ph'] = np.sort(Zother.flatten())[::-1][k]
                    elif k > np.sum(Y["m"]):
                        out['ph'] = np.sort(Z.flatten())[::-1][k]
                    else:
                        out['ph'] = max(np.sort(Zother.flatten())[::-1][k], np.sort(Z.flatten())[::-1][k])
                elif 0 <= k < 1:
                    out['ph'] = max(np.percentile(Z, k), np.percentile(Zother, k))
                else:
                    out['ph'] = None
            else:
                out['ph'] = max((sorted(Z, reverse=True))[1], sorted(Zother, reverse=True)[1])
        else:
            out['ph'] = None
    if "qdmapdiff" in which_stats:
        diffXY = sorted(abs(dX - dY).T.flatten(), reverse=True)
        if "qdmapdiff" in which_stats:
            if dXcheck or dYcheck:
                if k >= 1:
                    out['qdmapdiff'] = diffXY[k]
                elif 0 <= k < 1:
                    out['qdmapdiff'] = pd.DataFrame(diffXY).quantile(k)
                else:
                    out['qdmapdiff'] = None
            else:
                out['qdmapdiff'] = diffXY[1]

    if "med" in which_stats:
        out['medMiss'] = np.mean(Z)
        out['medFalseAlarm'] = np.mean(Zother)
    if "msd" in which_stats:
        out['msdMiss'] = np.mean(Z2)
        out['msdFalseAlarm'] = np.mean(Zother2)
    if "fom" in which_stats:
        out['fom'] = sum(1 / (1 + alpha * Z2)) / N
    if "minsep" in which_stats:
        if Z.size != 0:
            out['minsep'] = np.min(Z)
        else:
            out['minsep'] = None
    return out


if __name__ == '__main__':
    x = np.zeros((10, 12))
    y = np.zeros((10, 12))
    x[3:5, 2:7] = 1
    y[2:4, 6:9] = 1
    res = location_performance(x,y)
    print(res)
