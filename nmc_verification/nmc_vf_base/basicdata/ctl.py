#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
import math
from copy import deepcopy
class ctl:
    def __init__(self):
        self.slon = 0
        self.dlon = 1
        self.elon = 0
        self.slat = 0
        self.dlat = 1
        self.elat = 0
        self.nlon = 1
        self.nlat = 1
        self.nlevel = 1
        self.ntime = 1
        self.nvar = 1
        self.nensemble = 1
        self.data_Path = ""

    def copy(self):
        return deepcopy(self)