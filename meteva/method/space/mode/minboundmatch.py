import time
import sys
import copy
import numpy as np
import pandas as pd
from scipy import ndimage
#sys.path.append(r'F:\Work\MODE\Submit')    #导入的函数路径
#from Spatialvx import make_spatialVx   
#from Spatialvx import feature_finder
from . import data_pre
from .centmatch import restructuring


def minsepfun(Id, dm0, dm1, indX, indXhat,nlat,nlon):
    #掩膜提取函数：data为原始数值数组，mask为获得掩码用的布尔数组f
    result_value = []
    Obs_value = []
    Fcst_value = []

    for i in range(len(Id[:, 0])):
        a = Id[i, 0]    #从id数组的第一列取值
        b = Id[i, 1]    #从id数组的第二列取值
       # print(a, b)
        Obsdata_mask = np.mat(dm0[a])    #需要掩膜的原始数据
        #print("labels_{}".format(b))
        Obs_mask = np.ones((nlat,nlon))
        Obs_mask[indXhat[b]] = 0
        #Obs_mask = indXhat["labels_{}".format(b)] < 1     #掩膜范围
        Obs_masked = np.ma.array(Obsdata_mask, mask = Obs_mask)    #返回值有三类masked_array，mask,fill_value
        Obs = np.min(Obs_masked)
        Obs_value.append(Obs)

        Fcstdata_mask = np.mat(dm1[b])
        Fcst_mask = np.ones((nlat,nlon))
        Fcst_mask[indX[a]] = 0
        #Fcst_mask = indX["labels_{}".format(a)] < 1
        Fcst = np.min(np.ma.array(Fcstdata_mask, mask = Fcst_mask))
        Fcst_value.append(Fcst)

        #print("a:" + str(a) + " b:"+str(b) + "  " + str(Obs)+" " + str(Fcst))

        result = min(Fcst, Obs)
        result_value.append(result)
    return result_value


def minboundmatch_bak(look_ff, mindist=float('inf'), show=False):
    mindist =10
    fun_type = "multiple"
    x = copy.deepcopy(look_ff)
    if show:
        begin_tiid = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    if (type(x) != dict):  # R判断x是否为features,python 暂时判断x是否为dict
        try:
            sys.exit(0)
        except:
            print("minboundmatch: invalid x argument.")
    # if (x['Xlabelsfeature'] == None and x['Ylabelsfeature'] == None):
    if (x['grd_ob_features'] == None and x['grd_fo_features'] == None):
        try:
            sys.exit(0)
        except:
            print("minboundmatch: no features to match!")
    if (x['grd_ob_features'] == None):
        try:
            sys.exit(0)
        except:
            print("minboundmatch: no verification features to match.")
    if (x['grd_fo_features'] == None):
        try:
            sys.exit(0)
        except:
            print("minboundmatch: no model features to match.")
    fun_type = fun_type.lower()  # str.lower(),将type中的字母变为小写
    # type <- match.arg(type)    #未译
    out = x.copy()
    # a <- attributes(x)    #获取x中的属性
    out.update({'match_type': "minboundmatch"})
    match_message = {'match_message': "Matching based on minimum boundary separation using {} match".format(fun_type)}
    out.update({'match_message': match_message})
    # Xfeats = x['Xlabelsfeature']
    # Yfeats = x['Ylabelsfeature']
    Xfeats = x['grd_ob_features']
    Yfeats = x['grd_fo_features']
    Xfeats = data_pre.pick_labels(Xfeats)
    Yfeats = data_pre.pick_labels(Yfeats)
    if Xfeats != {}:
        n = len(Xfeats)
    else:
        n = 0
    if Yfeats != {}:
        m = len(Yfeats)
    else:
        m = 0
    if (m == 0 and n == 0):
        if show:
            print("\n", 'No features detected in either field.  Returning NULL.\n')
        return None
    elif (m == 0):
        if show:
            print("\n", 'No features detected in forecast field.  Returning NULL.\n')
        return None
    elif (n == 0):
        if show:
            print("\n", "No features detected in observed field.  Returning NULL.\n")
        return None
    rep00_1 = np.arange(1, n + 1, 1)
    rep00 = np.tile(rep00_1, m)
    rep0_1 = np.arange(1, m + 1, 1)
    rep0 = rep0_1.repeat(n, axis=0)  # 按行进行元素重复
    ind = np.vstack((rep00, rep0)).T  # 数组转置
    grid0 = look_ff["grid"]
    Xdmaps = {}
    Ydmaps = {}
    for i in range(1, n + 1):
        lable_index = np.zeros((grid0.nlat,grid0.nlon))
        lable_index[Xfeats[i]] = 1
        xdmaps = ndimage.morphology.distance_transform_edt(1 - lable_index)
        Xdmaps[i] = xdmaps
    for i in range(1, m + 1):
        lable_index = np.zeros((grid0.nlat,grid0.nlon))
        lable_index[Yfeats[i]] = 1
        ydmaps = ndimage.morphology.distance_transform_edt(1 - lable_index)
        Ydmaps[i] = ydmaps
    res = np.array(minsepfun(Id=ind, dm0=Xdmaps, dm1=Ydmaps, indX=Xfeats, indXhat=Yfeats,nlat=grid0.nlat,nlon=grid0.nlon))
    res = np.column_stack((ind, res))
    good = res[:, 2] <= mindist
    res = res[good]
    out.update({'values': pd.DataFrame(res, columns=["Observed Feature No.", "Forecast Feature No.",
                                                     "Minimum Boundary Separation"])})
    o = np.argsort(res[:, 2])
    res = res[o]
    # res = res_o.sort_values(by = "Minimum Boundary Separation").reset_index(drop = True)    #dataframe排序，默认升序，并更新index
    if (fun_type == "single"):
        N = len(res)
        Id = np.arange(N)
        Id = Id[o]
        # matches = res[res["Observed Feature No."] == res["Forecast Feature No."]].reset_index(drop = True)
        # matches = res_o[:len(Yfeats)]
        matches = np.array([])
        for i in range(N):
            matches0 = np.flipud(res[0, 0:2])  # 注意这个R里面取值以后，将预报放在前面，观测放在后面
            # res = res.reset_index(drop = True)     #res排序后，更新index，并且原来的index值不保存
            Id2 = (res[:, 0] == res[0, 0]) | (res[:, 1] == res[0, 1])
            res = res[~Id2]
            Id = Id[~Id2]
            matches = np.append(matches, matches0)
            if len(Id) == 0:
                break
        matches = matches.reshape(int(len(matches) / 2), 2)
    else:
        matches = np.fliplr(res[:, 0:2])
        matchlen = matches.shape[0]
        fuq = np.unique(matches[:, 0])
        flen = len(fuq)
        ouq = np.unique(matches[:, 1])
        olen = len(ouq)
        if (matchlen > 0):
            if (matchlen == flen and matchlen > olen):
                if (show):
                    print(
                        "Multiple observed features are matched to one or more forecast feature(s).  Determining implicit merges.\n")
            elif (matchlen > flen and matchlen == olen):
                if (show):
                    print(
                        "Multiple forecast features are matched to one or more observed feature(s).  Determining implicit merges.\n")
            elif (matchlen > flen and matchlen > olen):
                if (show):
                    print(
                        "Multiple matches have been found between features in each field.  Determining implicit merges.\n")
            elif (matchlen == flen and matchlen == olen):
                if (show):
                    print("No multiple matches were found.  Thus, no implicit merges need be considered.\n")
            out['implicit_merges'] = restructuring(matches[:, 0].astype(int) - 1,
                                                             matches[:, 1].astype(int) - 1)
        else:
            if (show):
                print("No objects matched.\n")
            out.update({"implicit_merges": None})

    # matches.insert(0, "Forecast Feature No.", matches.pop("Forecast Feature No."))    #先删除"Forecast Feature No."列，然后在原表中第0列插入被删掉的列,并重新命名
    matches = pd.DataFrame(matches, columns=(["Forecast", "Observed"]))
    matches = matches.sort_values(by=["Forecast"])  # R：将Forecast放在第一列，并以Forecast进行升序排列，python里面Forecast依然放在第二列
    out.update({"matches": matches})

    unmatched_X = set(ind[:, 0]) - set(matches["Observed"])  # 判断ind的值是否在matches里面，输出ind不在matches里面的值
    unmatched_Xhat = set(ind[:, 1]) - set(matches["Forecast"])
    unmatched = {"X": unmatched_X, "Xhat": unmatched_Xhat}
    out.update({"unmatched": unmatched})
    if (show):
        print(begin_tiid, '- begin.tiid')
    out.update({"MergeForced": False})
    out.update({"class": "matched"})

    return out


def minboundmatch(look_ff, mindist = float('inf'), show = False):
    fun_type = "single"
    #mindist =10
    #fun_type = "multiple" # 另一种匹配方式，设置该选项是，mindist需设置为一个有限值
    x = copy.deepcopy(look_ff)
    if show:
        begin_tiid = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
    if (type(x) != dict):    #R判断x是否为features,python 暂时判断x是否为dict
        try:
            sys.exit(0)
        except:
            print("minboundmatch: invalid x argument.")
    #if (x['Xlabelsfeature'] == None and x['Ylabelsfeature'] == None):
    if (x['grd_ob_features'] == None and x['grd_fo_features'] == None):
        try:
            sys.exit(0)
        except:
            print("minboundmatch: no features to match!")
    if (x['grd_ob_features'] == None):
        try:
            sys.exit(0)
        except:
            print("minboundmatch: no verification features to match.")        
    if (x['grd_fo_features'] == None):
        try:
            sys.exit(0)
        except:
            print("minboundmatch: no model features to match.")     
    fun_type = fun_type.lower()     # str.lower(),将type中的字母变为小写
    #type <- match.arg(type)    #未译
    out = x.copy()
    #a <- attributes(x)    #获取x中的属性
    out.update({'match_type':"minboundmatch"})
    #match_message = {'match_message' :"Matching based on minimum boundary separation using {} match".format(fun_type)}
    out.update({'match_message':"Matching based on minimum boundary separation using {} match".format(fun_type)})
    #Xfeats = x['Xlabelsfeature']
    #Yfeats = x['Ylabelsfeature']
    Xfeats = x['grd_ob_features']
    Yfeats = x['grd_fo_features']
    Xfeats = data_pre.pick_labels(Xfeats)
    Yfeats = data_pre.pick_labels(Yfeats)
    if Xfeats != {}:
        n = len(Xfeats)
    else:
        n = 0
    if Yfeats != {}:
        m = len(Yfeats)
    else:
        m = 0
    if (m == 0 and n == 0):
        if show:    
            print("\n",'No features detected in either field.  Returning NULL.\n')
        return None
    elif (m == 0):
        if show:
            print("\n",'No features detected in forecast field.  Returning NULL.\n')
        return None
    elif (n == 0):
        if show:
            print("\n", "No features detected in observed field.  Returning NULL.\n")
        return None
    rep00_1 = np.arange(1, n + 1, 1)
    rep00 = np.tile(rep00_1, m)
    rep0_1 = np.arange(1, m + 1, 1)
    rep0 = rep0_1.repeat(n, axis = 0)    #按行进行元素重复
    ind = np.vstack((rep00, rep0)).T    #数组转置
    
    Xdmaps = {}
    Ydmaps = {}
    grid0 = look_ff["grid"]
    for i in range(1, n + 1):
        lable_index = np.zeros((grid0.nlat,grid0.nlon))
        lable_index[Xfeats[i]] = 1
        xdmaps = ndimage.morphology.distance_transform_edt(1 - lable_index)
        Xdmaps[i] = xdmaps
    for i in range(1, m + 1):
        lable_index = np.zeros((grid0.nlat,grid0.nlon))
        lable_index[Yfeats[i]] = 1
        ydmaps = ndimage.morphology.distance_transform_edt(1 - lable_index)
        Ydmaps[i] = ydmaps

    #print(Xdmaps)
    res = np.array(minsepfun(Id = ind, dm0 = Xdmaps, dm1 = Ydmaps, indX = Xfeats, indXhat = Yfeats,nlat=grid0.nlat,nlon=grid0.nlon))
    #o = res.rank()

    res_o = np.column_stack((ind,res))
    res_o = pd.DataFrame(res_o, columns = ["ob", "fo", "Minimum Boundary Separation"])

    res_o["ob"] = res_o["ob"].astype(np.int16)
    res_o["fo"] = res_o["fo"].astype(np.int16)
    #print(res_o)
    #o = res.rank()
    #横轴是观测的目标序号，纵轴是预报的目标序号
    res = res.reshape(len(Yfeats), len(Xfeats))
    #以观测为准：观测→预报
    res_OF = np.argsort(res, axis = 0)
    A = np.arange(len(Xfeats))
    B = res_OF[0,:]    
    C = np.array((A, B)).T
    res_OF = pd.DataFrame(C, columns = ['ob', 'fo'])
    #以预报为准：预报→观测,R里面应该是以预报为准
    res_FO = np.argsort(res, axis = 1)
    A = np.arange(len(Yfeats))
    B = res_FO[:,0]    
    C = np.array((A,B)).T+1
    res_FO = pd.DataFrame(C, columns = ['ob', 'fo'])

    
    #good = res["Minimum Boundary Separation"] <= mindist    #判断计算结果是否小于设置的参数mindist
    #res <- res[good, , drop = False]    #如果res中存在异常值，删除
    res_o = res_o[res_o["Minimum Boundary Separation"] <= mindist].reset_index(drop = True)
    out.update({'values': res_o})
    
    #获取所有匹配中，值最小的前几个(不以观测或者预报为准)
    o = res_o["Minimum Boundary Separation"].rank()    #dataframe排序，不改变数值的位置，标记排名
    res_o = res_o.sort_values(by = "Minimum Boundary Separation").reset_index(drop = True)    #dataframe排序，默认升序，并更新index

    if (fun_type == "single"):
        N = len(res)
        Id = np.arange(N)
        Id = o
        #matches = res[res["ob"] == res["fo"]].reset_index(drop = True)
        matches = res_o[:len(Yfeats)]
        '''
        #逻辑走得通，但是没循环到
        matches = np.zeros((1,2))
        for i in N:
            matches = res[:1]    #选取res的第一行，也是值最小的配对
            res = res.reset_index(drop = True)     #res排序后，更新index，并且原来的index值不保存
            Id2 = res[(res["ob"] == res["ob"][0]) | \
                    (res["fo"] == res["fo"][0])]
            Id = Id2[Id2 != True].index    #Id2[Id2 != True].index.tolist #获取index值
            if len(Id) == 0 :
                break
        '''
    else:

        matches = res_o[["ob","fo"]]    #获取dataframe前两列
        matchlen = matches.shape[0]
        fuq =  set((matches["fo"]))   #预报场set存放,使得元素不重复
        flen = len(fuq)
        ouq = set((matches["ob"]))    #观测场set存放,使得元素不重复
        olen = len(ouq)
        if (matchlen > 0):
            if (matchlen == flen and matchlen > olen):
                if (show):
                    print("Multiple observed features are matched to one or more forecast feature(s).  Determining implicit merges.\n")
            elif (matchlen > flen and matchlen == olen):
                if (show):
                    print("Multiple forecast features are matched to one or more observed feature(s).  Determining implicit merges.\n")
            elif (matchlen > flen and matchlen > olen):
                if (show):
                    print("Multiple matches have been found between features in each field.  Determining implicit merges.\n")
            elif (matchlen == flen and matchlen == olen):
                if (show):
                    print("No multiple matches were found.  Thus, no implicit merges need be considered.\n")
        else :
            if (show):
                print("No objects matched.\n")
            out.update({"implicit_merges": None})

    #matches.insert(0, "fo", matches.pop("fo"))    #先删除"fo"列，然后在原表中第0列插入被删掉的列,并重新命名
    #matches[["ob", "fo"]] = matches[["fo", "ob"]]    #R:res[, 2:1]表示先去第二列，再取第一列，所以重新命名，python此处调换两列顺序
    #matches.columns = ["fo", "ob", "Minimum Boundary Separation"]    #列名调换
    matches = matches.sort_values(by = ["fo"])    #R：将Forecast放在第一列，并以Forecast进行升序排列，python里面Forecast依然放在第二列


    unmatched_X = set(ind[:, 0]) - set(matches["ob"])    #判断ind的值是否在matches里面，输出ind不在matches里面的值
    unmatched_Xhat = set(ind[:, 1]) - set(matches["fo"])
    unmatched = {"ob":unmatched_X, "fo":unmatched_Xhat}
    out.update({"unmatched": unmatched})
    if (show):
        print(begin_tiid,'- begin.tiid')
    out.update({"MergeForced": False})
    out.update({"class":"matched"})
    #print(matches)
    out.update({"matches":matches[["fo","ob"]].values})
    merges = restructuring(matches['fo'], matches['ob'])
    out.update({"merges":merges})

    return out


#=============================  Example  ===================================
'''
hold = make_SpatialVx_PA1.makeSpatialVx(X = pd.read_csv("F:\\Work\\MODE\\tra_test\\FeatureFinder\\pert000.csv"), \
                    Xhat = pd.read_csv(r"F:\Work\MODE\tra_test\FeatureFinder\pert004.csv"), \
                    loc = pd.read_csv(r"F:\Work\MODE\tra_test\FeatureFinder\ICPg240Locs.csv"), \
                    thresholds = [0.01, 20.01], projection = True, subset = None, timevals = None, reggrid = True,\
                    Map = True, locbyrow = True, fieldtype = "Precipitation", units = ("mm/h"), dataname = "ICP Perturbed Cases", obsname = "pert000", \
                    modelname = "pert004" , q = (0, 0.1, 0.25, 0.33, 0.5, 0.66, 0.75, 0.9, 0.95), qs = None)

look_FeatureFinder = FeatureFinder_test_PA3.featureFinder(Object = hold, smoothfun = "disk2dsmooth", \
                     dosmooth = True, smoothpar = 17, smoothfunargs = None,\
                     thresh = 310, idfun = "disjointer", minsize = np.array([1]),\
                     maxsize = float("Inf"), fac = 1, zerodown = False, timepoint = 1,\
                     obs = 1, model = 1)
'''
'''
x = look.copy()    #FeatureFinder函数结果
#fun_type = str(["single", "multiple"])     
fun_type = "single"    #类型只能为"single"或者 "multiple"，如果是single,matches结果为一对一（长度为5），multiple的结果为一对多（长度为5*5）
mindist = 20
show = False

look_minboundmatch = minboundmatch(x = look_FeatureFinder.copy(), fun_type = "single", mindist = 20, show = False)

'''

