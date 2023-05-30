#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan  7 23:46:15 2022

@author: tangbuxing
"""
import numpy as np
import sys


def tsboot(tseries, statistic, R, n_sim, l='NULL', sim='model',
           endcorr=True, orig_t=True, parallel=np.array(["no", "multicore", "snow"]),
           ncpus=["boot.ncpus"]):
    out = {}
    have_mc = False
    have_snow = False
    if parallel != "no" and len(ncpus) > 1:

        if (parallel == "multicore"):
            have_mc = True
        elif (parallel == "snow"):
            have_snow = True
        if (not have_mc) and (not have_snow):
            ncpus = 1

    # tscl = class(tseries)
    R = np.floor(R)
    if (R <= 0):
        sys.exit("'R' must be positive")
    call = 'match.call()'
    '''
    if (!exists(".Random.seed", envir = .GlobalEnv, inherits = FALSE))：#False
        runif(1)
    seed = get(".Random.seed", envir = .GlobalEnv, inherits = FALSE)
    t0 <- if (orig.t) 
    statistic(tseries, ...)    #暂未找到statistics函数
    else:
    none
    '''
    # ts.orig < - if (! is.matrix(tseries))
    # as.matrix(tseries)
    # if tseries is not None:
    #     ts_orig = tseries
    # n = ts_orig.shape[0]
    # if n_sim is None:
    #     n_sim = n
    #
    # # class(ts.orig) <- tscl
    #
    # if sim == "model" or sim == "scramble":
    #     l == 'NULL'
    # elif l is not 'NULL' or l <= 0 or l > n:
    #     sys.exit("invalid value of 'l'")
    #
    # fn < - if (sim == "scramble")
    # {
    #     rm(ts.orig)
    # function(r)
    # statistic(scramble(tseries, norm), ...)
    # }
    # if sim == "scramble":
    #     del (ts_orig)
    #
    #     def fn(r):

    return out
