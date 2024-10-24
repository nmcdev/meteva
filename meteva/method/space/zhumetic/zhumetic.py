#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 23:36:09 2023

"""
#import pyreadr
import numpy as np
import pandas as pd
import sys
import meteva

sys.path.append(r'/Users/tangbuxing/Desktop/tra_test-SAL/ZhuMetic/lib')
# from lib import im,distob,solutionset


def metrV(ob, fo, thresholds, lam1=0.5, lam2=0.5,show=False):
    out = {}

    if (isinstance(ob, np.ndarray) is not True) or (isinstance(fo, np.ndarray) is not True):
        raise Exception("metrV.default: invalid x and/or fo argument.")

    q = len(thresholds)
    out["thresholds"] = thresholds
    OvsM1 = np.zeros((q, 3))


    for threshold in range(q):
        M1im = meteva.method.space.zhumetic.im(fo)
        Oim = meteva.method.space.zhumetic.im(ob)
        Oim['v'] = Oim['v'] >= thresholds[threshold]
        M1im['v'] = M1im['v'] >= thresholds[threshold]
        # Ix = solutionset.solutionset(Oim['v'] >= thresholds[threshold])
        # Im1 = solutionset.solutionset(M1im['v'] >= thresholds[threshold])
        Ix = meteva.method.space.zhumetic.solutionset(Oim)
        Im1 = meteva.method.space.zhumetic.solutionset(M1im)

        # out["OvsM1"][threshold,1] = np.sqrt(np.sum(np.sum((Ix["m"] - Im1["m"])**2, axis = 1)))
        a1 = np.logical_xor(Ix["m"], Im1["m"])  # 逻辑运算
        b1 = np.power(a1, 2)
        c1 = np.sum(b1, axis=0)
        d1 = np.sum(c1)
        OvsM1[threshold, 0] = np.sqrt(d1)
        # out["OvsM1"][threshold,2] = distob(Ix['m'], Im1['m'], distfun = distfun)
        OvsM1[threshold, 1] = meteva.method.space.zhumetic.distob(X=Ix, Y=Im1)
        OvsM1[threshold, 2] = lam1 * OvsM1[threshold, 0] + lam2 * OvsM1[threshold, 1]
        if show:
            print("O vs M1 distOV for thresholds: ", thresholds[threshold,], " = ", OvsM1[threshold,], "\n")



        if show:
            print("M1 vs M2 distOV for thresholds: ", thresholds[threshold,], " = ", OvsM1[threshold,], "\n")
        #out["OvsM1"] = pd.DataFrame(out["OvsM1"], columns=["distOV", "distob", "metrV"])

    out["distOV"] = OvsM1[:,0].tolist()
    out["distDV"] = OvsM1[:, 1].tolist()
    out["metrV"] = OvsM1[:,2].tolist()

    return out


if __name__ == '__main__':

    A = np.zeros((10,12))
    B = np.zeros((10,12))
    B2 = np.zeros((10,12))
    A[1,2] = 3
    B[3,6] = 400
    B2[9,7] = 17
    thresholds = np.array([0.1, 3.1, 500])

    x = A
    fo = B
    thresholds = thresholds
    fo2 = B2
    lam1 = 0.5
    distfun = "distmapfun"
    lam2 = 0.5
    a = None
    show = False
    test_metrV = metrV(ob = A, fo = B, thresholds = np.array([0.1, 3.1, 500]))
    print(test_metrV)


    # data1 = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/ZhuMetic/data/geom000.rda')
    # data2 = pyreadr.read_r(r'/Users/tangbuxing/Desktop/tra_test-SAL/ZhuMetic/data/geom001.rda')
    # # testobj = mem.space.make_spatialVx(grd_ob=geom000, grd_fo=geom001, loc)
    # look_metrV = metrV_default(x=data1['geom000'].values, fo=data2['geom001'].values, thresholds=np.array([0.1, 3.1]))
    #







