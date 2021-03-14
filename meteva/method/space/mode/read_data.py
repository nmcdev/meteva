# -*- coding: utf-8 -*-
"""
Created on Thu Dec 31 16:20:21 2020

@author: 1
"""

import meteva.base as meb
import numpy as np
import pandas as pd
import math
import copy
import datetime
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
import sys
sys.path.append(r'F:\Work\MODE\Submit')
from . import feature_finder, centmatch, merge_force, plot
from . import minboundmatch, feature_axis,feature_match_analyzer, interester, deltamm
from . import feature_match_analyzer, feature_props, feature_comps, utils, feature_table

if __name__ == "__main__":
    #读观测数据
    print('******************* start ******************* \n')
    filename_ob = r'F:\\Work\\MODE\\Submit\\mode_data\\ob\\rain03\\20070111.000.nc'    #i = 0, j = 27
    filename_fo = r'F:\\Work\\MODE\\Submit\\mode_data\\ec\\rain03\\20070108.003.nc'

    grd_ob = meb.read_griddata_from_nc(filename_ob)
    grd_fo = meb.read_griddata_from_nc(filename_fo)

    #当smoothpar平滑次数较小时，thresh的值扩大的倍数小,小于1，如果平滑次数较大，则thresh阈值扩大了30倍左右
    look_featureFinder = feature_finder.feature_finder(grd_ob = grd_ob,
                                                       grd_fo = grd_fo,
                                                       smooth = [6, 5],
                                                       threshold = [5*9, 4*7],
                                                       minsize = [5, 5])


    look_centmatch = centmatch.centmatch(look_ff = look_featureFinder.copy())


    #deltamm函数调用好几个函数计算，所以占用整个运行时间最多
    #look_deltamm = deltamm.deltamm(look_ff = look_featureFinder.copy())


    look_minboundmatch = minboundmatch.minboundmatch(look_ff = look_featureFinder.copy())


    look_mergeforce = merge_force.merge_force(look_match = look_centmatch.copy())


    grd_ob_feature= {"m": look_featureFinder['grd_ob_features']['labels_1']}
    grd_fo_feature = {"m": look_featureFinder['grd_fo_features']['labels_1']}
    look_featureaxis = feature_axis.feature_axis(grd_feature = grd_ob_feature)


    look_featureMatcanalyzer = feature_match_analyzer.feature_match_analyzer(look_match = look_centmatch.copy())


    look_featureprops = feature_props.feature_props(grd_feature = grd_ob_feature, which_comps = ["centroid", "area", "axis"])

    #需要移除属性，仅保留格点数据参与计算
    remove_list = ['Type', 'xrange', 'yrange', 'dim', 'xstep', 'ystep', 'warnings', 'xcol', 'yrow', 'area']

    grd_ob_featureAttributes = utils.get_attributes_for_feat(look_featureFinder['grd_ob_features'])
    xkeys = utils.remove_key_from_list(list(look_featureFinder['grd_ob_features'].keys()), remove_list)
    grd_ob_feature.update(grd_ob_featureAttributes)

    grd_fo_featureAttributes = utils.get_attributes_for_feat(look_featureFinder['grd_fo_features'])
    ykeys = utils.remove_key_from_list(list(look_featureFinder['grd_fo_features'].keys()), remove_list)
    grd_fo_feature = {"m": look_featureFinder['grd_fo_features']['labels_1']}
    grd_fo_feature.update(grd_fo_featureAttributes)

    #feature_comps函数默认的是预报放在前，观测放在后
    look_featurecomps = feature_comps.feature_comps(grd_ob = grd_ob_feature, grd_fo = grd_fo_feature)


    look_featuretable = feature_table.feature_table(grd_features = look_centmatch.copy())


    look_interester = interester.interester(grd_features = look_featureFinder.copy())


    #原始场
    dataset_ob = xr.open_dataset(filename_ob)
    plot.plot_values(dataset_ob, grd_ob = look_featureFinder['grd_ob'], grd_fo = look_featureFinder['grd_fo'], cmap = "rain_3h")
    plot.plot_ids(dataset_ob, grd_ob = look_featureFinder['grd_ob_labeled'], grd_fo = look_featureFinder['grd_fo_labeled'])
    plot.plot_ids(dataset_ob, grd_ob = look_mergeforce['grd_ob_labeled'], grd_fo = look_mergeforce['grd_fo_labeled'])
