# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 15:50:13 2020

@author: 1
"""

#============================  centmatch()  ==============================
import numpy as np

import math
import sys
import copy
from . import data_pre
from .feature_props import feature_props



def rdistEarth(x1, x2, miles, R):
    #计算球面距离，这个函数目前没用到
    if (R is None):
        if (miles):
            R = 3963.34
        else :
            R = 6378.388
    coslat1 = math.cos((x1[:, 1] * math.pi)/180)
    sinlat1 = math.sin((x1[:, 1] * math.pi)/180)
    coslon1 = math.cos((x1[:, 0] * math.pi)/180)
    sinlon1 = math.sin((x1[:, 0] * math.pi)/180)
    if (x2 is None):
        cbind = np.mat((coslat1 * coslon1, coslat1 * sinlon1, sinlat1))
        t_cbind = np.mat((coslat1 * coslon1, coslat1 * sinlon1, sinlat1)).T
        pp = np.dot(cbind, t_cbind)
        if (abs(pp) > 1):
            return R * math.acos(1 * np.sign(pp))
        else :
            return R * math.acos(pp)
        
    else :
        coslat2 = math.cos((x2[:, 1] * math.pi)/180)
        sinlat2 = math.sin((x2[:, 1] * math.pi)/180)
        coslon2 = math.cos((x2[:, 0] * math.pi)/180)
        sinlon2 = math.sin((x2[:, 0] * math.pi)/180)
        cbind = np.mat((coslat1 * coslon1, coslat1 * sinlon1, sinlat1))
        t_cbind = np.mat((coslat2 * coslon2, coslat2 * sinlon2, sinlat2)).T
        pp = np.dot(cbind, t_cbind)
        if (abs(pp) > 1):
            return R * math.acos(1 * np.sign(pp))
        else :
            return R * math.acos(pp)
        
def rdist(x1, x2):
    #计算两点间欧式距离
    return np.sqrt(np.sum(np.square(x1 - x2)))

#调整implicit_merges存放结构
def restructuring(fo_id_list,ob_id_list):

    n_row = len(ob_id_list)
    ob_index_dict = {}
    fo_index_dict = {}
    index_list_dict = {}
    index = 0

    for i in range(n_row):
        if ob_id_list[i] in ob_index_dict.keys() or fo_id_list[i] in fo_index_dict.keys():
            if ob_id_list[i] in ob_index_dict.keys():
                index1 = ob_index_dict[ob_id_list[i]]
                fo_index_dict[fo_id_list[i]] = index1
            elif fo_id_list[i] in fo_index_dict.keys():
                index1 = fo_index_dict[fo_id_list[i]]
                ob_index_dict[ob_id_list[i]] = index1
        else:
            ob_index_dict[ob_id_list[i]] = index
            fo_index_dict[fo_id_list[i]] = index
            index1 = index
            index_list_dict[index1] = []
            index = index + 1
        index_list_dict[index1].append([fo_id_list[i],ob_id_list[i]])

    list_list = list(index_list_dict.values())

    #将ob,或fo id有重复的列表进行合并
    while True:
        len0 = len(list_list)
        changed = False
        for i in range(len0-1):
            dat_i = np.array(list_list[i])
            ob_seti = set(dat_i[:,0])
            fo_seti = set(dat_i[:,1])
            for j in range(i+1,len0):
                dat_j = np.array(list_list[j])
                ob_setj = set(dat_j[:,0])
                fo_setj = set(dat_j[:,1])
                if len(ob_seti&ob_setj) >0 or  len(fo_seti&fo_setj) >0:
                    list_list[i].extend(list_list[j])
                    list_list.pop(j)
                    changed = True
                    break
            if changed:
                break
        if not changed:
            break
    return list_list

def centmatch(look_ff, criteria = 1, const = 14,  show = False):
    #centmatch(look_ff, criteria=1, const=14, areafac=1, show=False):
    x = copy.deepcopy(look_ff)
    distfun = "rdist"
    out = x.copy()
    out.update({'match_message':"Matching based on centroid distances using centmatch function.",
                      'match_type':"centmatch", 'criteria':criteria})
    X = x['grd_ob']
    Xhat = x['grd_fo']
    if (criteria == 3):
        out.update({'const':const})
    else :
        out.update({'const':str(' NULL ')})
    if (distfun == "rdist.earth"):
        #loc <- a$loc    #直接读取文件，不用引用
        if (x['loc'].all() == None):
            print("warning:Using rdist.earth, but lon/lat coords are not available. Can pass them as an attribute to x called loc.")
    else :
        loc = None
    #xdim = np.shape(x['ob'])    #look['Xlabeled']在python里面进行连通域分析以后变为三维，但是数据shape与原来的field没变
    xdim = np.shape(X)
    #Y = x['Ylabelsfeature']    #x['Ylabelsfeature']对应x$Y.feats：被标记的连通域单独存放
    Y = x['grd_fo_features']
    #X = x['Xlabelsfeature']
    X = x['grd_ob_features']

    Y = data_pre.pick_labels(Y)
    X = data_pre.pick_labels(X)
    m = len(Y)
    n = len(X)
    if (criteria != 3):
        Ax = np.zeros((n))
        Ay = np.zeros((m))
    Dcent = np.repeat(None, m*n).reshape(m, n)
    if (show):
        if (criteria != 3):
            print("\n", "Looping through each feature in each field to find the centroid differences.\n")
        else :
            print("\n", "Looping through each feature in each field to find the areas and centroid differences.\n")

    tmpy = {}
    Ay = np.array([])
    ycen = []
    Dcent = np.array([])
    for i in range(m) :
        if (show):
            print(i,'\n')
        if (criteria != 3):
            #tmpy = featureProps(x = Y['labels_{}'.format(i)], whichprops = ["centroid","area"])
            #Ytmp = {"m": out['Ylabelsfeature']['labels_%d'%(i+1)]}
            #Ytmp = out['grd_fo_features']['labels_%d'%(i+1)]
            tmpy_i = feature_props(out,i+1,ob_or_fo = "fo", which_comps = ["centroid","area"])
            tmpy_num = {'{}'.format(i):tmpy_i}
            tmpy.update(tmpy_num)
            Ay_i = math.sqrt(tmpy[str(i)]['area'])
            Ay = np.append(Ay, Ay_i)
        else:
            #Ytmp = out['grd_fo_features']['labels_%d' % (i + 1)]
            tmpy = feature_props(out,i+1,ob_or_fo = "fo", which_comps = ["centroid"])
        ycen_i = tmpy[str(i)]['centroid']
        ycen.append(ycen_i)

        tmpx = {}
        Ax = np.array([])
        xcen = []
        for j in range(n):
            if (show):
                print(j)
            if (criteria != 3):
                #Xtmp = out['grd_ob_features']['labels_%d'%(j+1)]
                tmpx_j = feature_props(out,j+1,ob_or_fo = "ob", which_comps = ["centroid","area"])
                tmpx_num = {'{}'.format(j):tmpx_j}
                tmpx.update(tmpx_num)
                Ax_j = math.sqrt(tmpx[str(j)]['area'])
                Ax = np.append(Ax, Ax_j)
            else:
                #Xtmp = out['grd_ob_features']['labels_%d' % (j + 1)]
                tmpx = feature_props(out,j+1,ob_or_fo = "ob",  which_comps = ["centroid"])
            #xcen_j = np.mat(tmpx[str(j)]['centroid'])
            xcen_j = tmpx[str(j)]['centroid']
            xcen.append(xcen_j)
            #print('length:',len(xcen),'i:',i)
            Dcent_ij = rdist(x1 = np.array((xcen[j]['x'], xcen[j]['y'])), x2 = np.array((ycen[i]['x'], ycen[i]['y'])))    #miles/R为默认参数
            Dcent = np.append(Dcent, Dcent_ij)
        if (show):
            print('\n')
    Dcent = Dcent.reshape(m, n)
    if (criteria != 3):
        Ay = np.repeat(Ay, n).reshape(m, n)
        Ax = np.tile(Ax, m).reshape(m, n)
    if (criteria == 1):
        Dcomp = Ay + Ax
    elif (criteria == 2):
        Dcomp = (Ay + Ax)/2
    elif (criteria == 3):
        Dcomp = np.repeat(const, n*m ).reshape(m, n)
    else:
        try:
            sys.exit(0)
        except:
            print("centmatch: criteria must be 1, 2 or 3.")
    DcompID = Dcent < Dcomp    #Dcent为两点间的欧式距离，Dcomp = 观测场面积的开方+预报场面积的开方
    any_matched = np.any(DcompID)
    FobjID = np.repeat(np.arange(m),n).reshape(m, n)
    OobjID = np.tile(np.arange(n),m).reshape(n, m)
    fmatches = np.argwhere(DcompID)    #获取True的索引
    if (len(fmatches[:, 0]) > 1):
        pcheck = []
        for k in range(len(fmatches[:, 0])):
            pcheck_k = '{0} - {1}'.format(fmatches[k-1, 0], fmatches[k-1, 1])
            pcheck.append(pcheck_k)
        dupID = set(pcheck)    #集合自动去重，但是原函数是判断是否重复后，从fmatches里面删除重复
        if (len(dupID) != len(fmatches)):
            print("提示：存在一模一样的配对，需要从fmatches里面删除。")
    if (np.shape(fmatches) is None and len(fmatches) == 2):
        fmatches = np.mat(fmatches)
    fmatches += 1
    out.update({'matches':fmatches})
    if (any_matched):
        f_comped = set(np.arange(m))
        funmatched = f_comped - set(fmatches[:, 0])     #返回观测场中没有匹配到的object
        vxunmatched = f_comped - set(fmatches[:, 1])    #返回预报场中没有匹配到的object
        matchlen = len(fmatches[:,0])
        fuq = set(fmatches[:, 0])     #使得fmatches第一列没有重复的值
        flen = len(fuq)
        ouq = set(fmatches[:, 1])
        olen = len(ouq)
        if (matchlen == flen and matchlen > olen):    #注意：这一步的结果与R语言判断有出入
            if (show):
                print("Multiple observed features are matched to one or more forecast feature(s).  Determining implicit merges.\n")
        elif (matchlen > flen and matchlen > olen):
            if (show):
                print("Multiple forecast features are matched to one or more forecast feature(s).  Determining implicit merges.\n")
        elif (matchlen > flen and matchlen > olen):
            if (show):
                print("Multiple matches have been found between features in each field.  Determining implicit merges.\n")
        elif (matchlen == flen and matchlen == olen):
            if (show):
                print("No multiple matches were found.  Thus, no implicit merges need be considered.\n")
        implicit_merges = fmatches    #R:调用MergeIdentifier
    else :
        if (show):
            print("No objects matched.\n")
        implicit_merges = 'NULL'
        funmatched = np.arange(m)
        vxunmatched = np.arange(n)
    unmatched = {'ob':vxunmatched, 'fo':funmatched}

    #调整unmatched存放结构
    a_obs = set(fmatches[:, 0])
    a_fcst = set(fmatches[:, 1])
    if len(a_fcst) != n :
        #unmatched_X = set(np.arange(n)) - set(a_fcst)    #X未匹配的目标
        unmatched_X = set(np.arange(1,n+1)) - set(a_fcst)  # X未匹配的目标
        #print(unmatched_X)
    else :
        unmatched_X = 'NULL'
    if len(a_obs) != m :
        #unmatched_Xhat = set(np.arange(m)) - set(a_obs)    #Xhat未匹配的目标
        unmatched_Xhat = set(np.arange(1,m+1)) - set(a_obs)  # Xhat未匹配的目标
        #print(unmatched_Xhat)
    else :
        unmatched_Xhat = 'NULL'
    unmatched = {'ob':unmatched_X, 'fo':unmatched_Xhat}
    
    #调整implicit_merges的存放结构
    if implicit_merges == 'NULL' or implicit_merges.all() == None :
        implicit_merges = None
    else:
        implicit_merges = restructuring(implicit_merges[:, 0], implicit_merges[:, 1])
    out.update({'unmatched':unmatched, 'implicit_merges':implicit_merges, 
                      'criteria_values':Dcomp, 'centroid_distances':Dcent, 
                      'MergeForced':False, 'class(out)':"matched", 
                      'unmatched': unmatched })
    out["grid"] = copy.deepcopy(look_ff["grid"])

    return out
'''
hold = make_SpatialVx_PA1.makeSpatialVx(X = pd.read_csv("F:\\Work\\MODE\\tra_test\\FeatureFinder\\pert000.csv"), \
                    Xhat = pd.read_csv(r"F:\Work\MODE\tra_test\FeatureFinder\pert004.csv"), \
                    loc = pd.read_csv(r"F:\Work\MODE\tra_test\FeatureFinder\ICPg240Locs.csv"), \
                    thresholds = [0.01, 20.01], projection = True, subset = None, timevals = None, reggrid = True,\
                    Map = True, locbyrow = True, fieldtype = "Precipitation", units = ("mm/h"), dataname = "ICP Perturbed Cases", obsname = "pert000", \
                    modelname = "pert004" , q = (0, 0.1, 0.25, 0.33, 0.5, 0.66, 0.75, 0.9, 0.95), qs = None)

look_FeatureFinder = FeatureFinder_test_PA3.featureFinder(Object = hold.copy(), smoothfun = "disk2dsmooth", \
                     dosmooth = True, smoothpar = 17, smoothfunargs = None,\
                     thresh = 310, idfun = "disjointer", minsize = np.array([1]),\
                     maxsize = float("Inf"), fac = 1, zerodown = False, timepoint = 1,\
                     obs = 1, model = 1)
'''
#centmatch参数：
#经纬度信息
'''
loc = pd.read_csv("F:\\Work\\MODE\\tra_test\\makeSpatialVx\\UKloc.csv")
x = lookFeatureFinder.copy()
criteria = 1
const = 14
distfun = "rdist"
areafac = 1
show = False

look_centmatch = centmatch(x = look_featureFinder.copy(), criteria = 1, const = 14, distfun = "rdist", areafac = 1, show = False)

'''







