#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May  1 19:01:40 2023

@author: tangbuxing
"""
import numpy as np
import meteva.method as mem

#import locperf


def distob(X, Y, distfun = "distmapfun"):
    out = {}
    nX = np.sum(np.sum(X, axis = 0))
    nY = np.sum(np.sum(Y, axis = 0))
    
    if nX == 0 and nY == 0:
        return 0 
    elif nX == 0 or nY == 0:
        return np.max(np.shape(np.matrix(X)))
    else:
        out = mem.mode.locperf.locperf(X = X, Y = Y, which_stats = "med")["medMiss"]
        
    return out

