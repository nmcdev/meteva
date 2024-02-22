# -*- coding: utf-8 -*-
"""
Created on Mon Mar  1 18:34:06 2021
"""
import numpy as np


def thresholder(x, th, func_type=None, rule=">=", replace_with=0, **args):
    if func_type is None:
        func_type = ['binary', 'replace_below']
    if rule == ">=":
        bool_value = x >= th
    elif rule == ">":
        bool_value = x > th
    elif rule == "<=":
        bool_value = x <= th
    elif rule == "<":
        bool_value = x < th
    xdim = x.shape
    if xdim is None:
        out = np.full(len(x), replace_with)
    else:
        out = np.full(xdim, replace_with)
    if func_type == "binary":
        out[bool_value] = 1
    else:
        out = x[bool_value]
    return out


