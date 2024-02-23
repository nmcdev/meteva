# -*-coding:utf-8-*-
import numpy as np
import copy


def loc_list_setup(a, which_stats=None, nthresh=1, n_p=1, nk=1, nalpha=1):
    if which_stats is None:
        which_stats = ["bdelta", "haus", "qdmapdiff", "med", "msd", "ph", "fom", "minsep"]
    if a is not None:
        out = a
    else:
        out = {}
    q = nthresh
    outvec = []
    for i in range(q):
        outvec.append(None)
    if "bdelta" in which_stats:
        if q == 1:
            out['bdelta'] = np.full(n_p, None)
        else:
            out['bdelta'] = np.full((n_p, q), None)
    if "haus" in which_stats:
        out['haus'] = copy.deepcopy(outvec)
    if "qdmapdiff" in which_stats:
        if q == 1:
            out['qdmapdiff'] = np.full(nk, None)
        else:
            out['qdmapdiff'] = np.full((nk, q), None)
    if "med" in which_stats:
        out['medMiss'] = copy.deepcopy(outvec)
        out['medFalseAlarm'] = copy.deepcopy(outvec)
    if "msd" in which_stats:
        out['msdMiss'] = copy.deepcopy(outvec)
        out['msdFalseAlarm'] = copy.deepcopy(outvec)
    if "ph" in which_stats:
        if q == 1:
            out['ph'] = np.full(nk, None)
        else:
            out['ph'] = np.full((nk, q), None)
    if "fom" in which_stats:
        if q == 1:
            out['fom'] = np.full(nalpha, None)
        else:
            out['fom'] = np.full((nalpha, q), None)
    if "minsep" in which_stats:
        out['minsep'] = copy.deepcopy(outvec)
    return out
