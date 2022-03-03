# -*- coding: utf-8 -*-
"""
Created on Sun Aug  2 16:55:54 2020

@author: 1
"""

#============================  deltammSqCen()  ==============================
import numpy as np
import pandas as pd
from . import censqdelta
from .centmatch import restructuring

#提取数据
def pick_labels(data):
    ret = {}
    for item, values in data.items():

        if isinstance(item,int):
            #print(item, values)
            ret0 = {item : values}
            ret.update(ret0)
    return ret

#以观测场为准，将预报场匹配到观测场
def bdFun(Id,nrow,ncol, OB, FC, p, const, N, show):
    #OB = X    #参数取值
    #FC = Xhat    #参数取值
    #一一对比计算预报场和观测场的delta结果
    #OB = pick_labels(OB)
    #FC = pick_labels(FC)
    res = np.array(())

    ob1 = np.zeros((nrow,ncol))
    fo1 = np.zeros((nrow,ncol))

    for j in range(1, len(OB) + 1):
        for k in range(1, len(FC) + 1):
            #print("观测目标：%d  ,"%j ,  "预报目标：%d"%k)
            ob1[:] = 0
            fo1[:] = 0
            ob1[OB[j]] = 1
            fo1[FC[k]] = 1
            res_0 = censqdelta.censqdelta(x = ob1,
                             y = fo1, N = N, const = const, p = p)
            res = np.append(res,res_0)
            if (show):
                print("Calculating Baddeley Delta Metric between forecast feature {0} and observed feature {1}\n".format(j, k))                
    return res

#以预报场为准，将观测场匹配到预报场
def foFun(Id,nrow,ncol, OB, FC, p, const, N, show):
    res = np.array(())

    ob1 = np.zeros((nrow,ncol))
    fo1 = np.zeros((nrow,ncol))

    for j in range(1, len(FC) + 1):
        for k in range(1, len(OB) + 1):
            #print("预报目标：%d  ,"%j ,  "观测目标：%d"%k)
            ob1[:] = 0
            fo1[:] = 0
            ob1[OB[k]] = 1
            fo1[FC[j]] = 1
            res_0 = censqdelta.censqdelta(x = fo1,
                             y = ob1, N = N, const = const, p = p)
            res = np.append(res,res_0)
            if (show):
                print("Calculating Baddeley Delta Metric between forecast feature {0} and observed feature {1}\n".format(j, k))                
    return res

#判断元素是否存在
def efun(x, ftr):
    for i in range(len(x)):
        if (x['%d'%i] in np.array(ftr)):
            x['%d'%i] = True
        else :
            x['%d'%i] = False
    return x

def mergeIdentifier(x):
    if any( np.shape(x)) == 0:
        return None
    matchlen = np.shape(x)[0]
    fuq = np.unique(x['Forecast'])
    ouq = np.unique(x['Observed'])
    flen = len(fuq)
    olen = len(ouq)
    out = []
    if matchlen == flen and matchlen > olen:
        for i in range(olen):
            if x[:, 'Observed'] == ouq[i]:
                out[i] = x
    elif matchlen > flen and matchlen == olen:
        for i in range (flen):
            if x['Forecast'] == fuq[i]:
                out[i] = x
    elif matchlen > flen and matchlen > olen:
        if matchlen > 1:
            idx = np.zeros(matchlen)
            idx[0] = 1
            for i in range(1, matchlen):
                idF = x.loc[0:i, 'Forecast'] == x.loc[i, 'Forecast']
                idO = x.loc[0:i, 'Observed'] == x.loc[i, 'Observed']
                if any(idF):
                    idx[i] = idx[0:i][0]
                elif any(idO):
                    idx[i] = idx[0:i][0]
                else:
                    idx[i] = max(idx[0:i]) + 1
        else:
            return (None)
        for j in range (0, max(idx).astype(int)):
            out = x[idx == j]
    elif matchlen == flen and matchlen == olen:
        return None
    return out 

def merge_or_label_index(nlat,nlon,label_index1,label_index2):
    label = np.zeros((nlat,nlon))
    label[label_index1] = 1
    label[label_index2] = 1
    return np.where(label == 1)

def deltammSqcen(x, p, max_delta, const, N, show):

    #a = look    #look为featureFinder生成的结果
    out = {}
    X = x['grd_ob_features']    #R:引用的为单独标记的连通域
    Xhat = x['grd_fo_features']    #R:引用的为单独标记的连通域
    x['ob'] = x['grd_ob']
    x['fo'] = x['grd_fo']
    grid0 = x["grid"]
    #单独提取被标记的对象
    X = pick_labels(X)
    Xhat = pick_labels(Xhat)
    xdim = np.shape(x['ob'])     #R:引用属性里面的维度(shape)。观测场和预报场的要素数量一致
    if (N == None):
        N = max(xdim)
        if (N % 2 == 0):
            N = N + 1
    #R:函数内部定义bdFun函数，python：在函数外部单独定义
    n = len(X)    
    m = len(Xhat)
    no_X = np.all(X) == None or n == 0
    no_Xhat = np.all(Xhat) == None or m == 0

    if (no_X or no_Xhat):
        if (no_X and no_Xhat and show):
            print("No identified features in either field.  Therefore, no matches/merges made.\n")
        elif (no_X and show):
            print("No identified observed features.  Therefore, no matches/merges made.\n")
        elif (no_Xhat and show):
            print("No identified model features.  Therefore, no matches/merges made.\n")
        funmatched = np.arange(1, m + 1, 1)    #python下标从0开始
        vxunmatched = np.arange(1, n + 1, 1)
        #matches = np.array(robjects.r('''
        #                     cbind(integer(0), integer(0))
        #                     '''))
        matches = np.array([])
        merges = None
        unmatched = {"X":vxunmatched, "Xhat":funmatched}
        out.update({"unmatched":unmatched, "matches":matches, "merges":merges, "class_":"matched"})
        return out 

    if (show):
        print("Step 1: Finding Upsilon matrix containing the Baddeley delta between each individual feature across fields.\n")
    #ind = np.array(robjects.r('''cbind(rep(1:n, m), rep(1:m, each = n))'''))    #传参有问题
    rep00_1 = np.arange(1, n + 1, 1)
    rep00 = np.tile(rep00_1, m)
    rep0_1 = np.arange(1, m + 1, 1)
    rep0 = rep0_1.repeat(n, axis = 0)    #按行进行元素重复
    ind = np.vstack((rep00, rep0)).T    #数组的形状未转置
    #第一步：一一对比观测场和预报场,观测场(列号)→预报场(行号)
    Upsilon = bdFun(Id = ind,nrow=grid0.nlat,ncol=grid0.nlon, OB = X, FC = Xhat, p = p, const = const, N = N, show = show)
    Upsilon = Upsilon.reshape(len(X), len(Xhat))
    #一一对比预报场→观测场
    Upsilon_fo = foFun(Id = ind,nrow=grid0.nlat,ncol=grid0.nlon, OB = X, FC = Xhat, p = p, const = const, N = N, show = show)
    Upsilon_fo = Upsilon_fo.reshape(len(Xhat), len(X))

    #对Upsilon二维数组排序
    o_Ksi = np.argsort(Upsilon, axis=1)    #按行排序,返回的是观测场的序号
    o_Psi = np.argsort(Upsilon, axis=0)    #按列排序,返回的是预报场的序号
    Ksi = np.sort(Upsilon, axis=1)    #按列排序,不改变数值
    Psi = np.sort(Upsilon, axis=0)    #按行排序,不改变数值

    if(show):
        print("Finding {0} potential forecast merges for each of the {1} observed features.\n".format(m - 1, n))
    
    #以观测场为准，合并预报场    
    for j in range (len(X)):
        #猜测：因为Ksi是对列调整，取值是观测场X；Psi是对行调整，取值是预报场Xhat
        #o <- (1:m)[o.Ksi[j, ]]
        o = o_Ksi[j, :]
        #print("预报场目标序号：", o)
        #外层循环观测场，控制合并的次数；内层循环取预报场的目标序号，控制合并的内容
        if (len(X) >= 2) and len(o)>1:
            #R:union.owin合并两个图像
            newobj = {1: merge_or_label_index(grid0.nlat,grid0.nlon,Xhat[o[0] + 1],Xhat[o[1] + 1])}
            #newobj = {'labels_%d'%1:Xhat['labels_%d'%(o[0] + 1)] | Xhat['labels_%d'%(o[1] + 1)] }
        else :
            newobj = Xhat
        if (len(X) >= 3) and len(o)>1:
            #for (i in 3:length(Xhat)) newobj[[i - 1]] <- union.owin(newobj[[i - 2]], Xhat[[o[i]]])
            for i in range(3, len(Xhat) + 1):    #取预报场的目标序号
                #print("预报场目标序号：", i)
                newobj_0 = {(i - 1): merge_or_label_index(grid0.nlat,grid0.nlon,newobj[i - 2] , Xhat[o[i - 1] + 1])}
                #newobj_0 = {'labels_%d'%(i - 1):newobj['labels_%d'%(i - 2)] | Xhat['labels_%d'%(o[i - 1] + 1)]}
                newobj.update(newobj_0)

    if (m > 1):
        if (show):
            print("Calculating delta metrics for forecast merges.\n")
        rep00_1 = np.arange(1, n + 1, 1)
        rep00 = np.tile(rep00_1, m -1)
        rep0_1 = np.arange(1, m, 1)
        rep0 = rep0_1.repeat(n, axis = 0)    #按行进行元素重复
        ind = np.vstack((rep00, rep0)).T 
        look = []
        for i in range(len(ind)):
            look_0 = str(ind[i, 0]) + '-' + str(ind[i, 1])
            look.append(look_0)
        #look = set(look)    #去掉重复的匹配
        tmp = bdFun(Id = ind,nrow=grid0.nlat,ncol=grid0.nlon, OB = X, FC = newobj, p = p, const = const, N = N, show = show)
        tmp = tmp.reshape(len(X), len(newobj))
        Ksi[:, 1:len(Xhat)] = tmp
    else:
        Ksi = Upsilon
    if (show):
        print("\nFinding {0} potential observed merges for each of the {1} forecast features.\n".format((n - 1), m))


    #以预报场为准，合并观测场    
    for k in range(len(Xhat)):
        if (show):
            print(k)
        #o <- (1:n)[o.Psi[, k]]
        o = o_Psi[:, k] 
        #print("观测场目标序号：", o)
        if (n >= 2):
            #newobj = {'labels_%d'%1:X['labels_%d'%(o[0] + 1)] | X['labels_%d'%(o[1] + 1)]}
            newobj = {1: merge_or_label_index(grid0.nlat,grid0.nlon,X[o[0] + 1] , X[o[1] + 1])}
        else:
            newobj = X
        if (n >= 3):
            for i in range(2, n):
                #newobj_0 = {'labels_%d'%(i):newobj['labels_%d'%(i - 1)] | X['labels_%d'%(o[i - 1] + 1)]}
                newobj_0 = {i: merge_or_label_index(grid0.nlat,grid0.nlon,newobj[i - 1] , X[o[i - 1] + 1])}
                newobj.update(newobj_0)
    if (n > 1):
        if (show):
            print("\nAll metrics for forecast merges found.  Calculating delta metrics for observed merges.\n")
        rep00_1 = np.arange(1, n , 1)
        rep00 = np.tile(rep00_1, m)
        rep0_1 = np.arange(1, m + 1, 1)
        rep0 = rep0_1.repeat(n - 1, axis = 0)    #按行进行元素重复
        ind = np.vstack((rep00, rep0)).T 
        look = []
        for i in range(len(ind)):
            look_0 = str(ind[i, 0]) + '-' + str(ind[i, 1])
            look.append(look_0)
        #look = set(look)    #去掉重复的匹配
        tmp = bdFun(Id = ind,nrow=grid0.nlat,ncol=grid0.nlon, OB = newobj, FC = Xhat, p = p, const = const, N = N, show = show)
        tmp = tmp.reshape(len(newobj), len(Xhat))
        Psi[1:, 0:m] = tmp
    else:
        Psi  = Upsilon
    bigQ = np.zeros((3, n, m))    #三维数组:m*n,与Upsilon/Ksi/Psi的shape一致
    bigQ[0, :, :] = Upsilon
    bigQ[1, :, :] = Psi
    bigQ[2, :, :] = Ksi
    out.update({'Q':bigQ})
    if (np.all(bigQ > max_delta)):
        if (show):
            print("\nAll delta metrics are larger than max.delta, no merges/matches.\n")
        funmatched = np.arange(m)
        vxunmatched = np.arange(n)
        unmatched = {'ob':vxunmatched, 'fo':funmatched}
        matches = np.array([])
        out.update({'unmatched':unmatched, 'matches':matches, 'merges':"NULL"})
        return out
    else:
        if (show):
            print("Psi:\n")
            print(Psi)
            print("Ksi:\n")
            print(Ksi)
            print("\nAll Baddeley metrics found.  Book keeping ...\n")

        
        '''
        J = {}
        K = {}
        j_0 = []
        k_0 = []
        for jk in range( 3 * n * m):
            if (jk < n*m):
                j_0 = ind[jk, 0]
                k_0 = ind[jk, 1]
                J.update({'%d'%(jk): j_0})
                K.update({'%d'%(jk): k_0})
            elif ((jk > n * m) and (jk <= 2 * n * m)):
                k_0 = ind[jk, 1]
                jj = np.arange(ind[jk, 0])
                J.update({'%d'%(jk): jj})
                j_0 = o_Psi[:n, ind[jk, 1] - 1]
                J.update({'%d'%(jk): j_0})
            else :
                j_0 = ind[jk, 0]
                kk = np.arange(ind[jk, 1])
                J.update({'%d'%(jk): kk})
                k_0 = o_Ksi[ind[jk, 0] - 1, :m]
                K.update({'%d'%(jk): k_0})
                
        Iter = 1
        matches = np.zeros((1,2))
        nn = np.arange(n)
        mm = np.arange(m)
        bigQ[bigQ > max_delta] = None
        bigQ_arr = bigQ.reshape(bigQ.size, ).copy()    #将三维数组展开成一维
        
        while (len(nn) > 0 and len(mm) > 0 and Iter < 3 * n * m + 1):
            if ((bigQ != None).any()):    #R: if (any(!is.na(bigQ)))
                #R:bigQ存为list形式
                #bigQ_list = [item for sublist in bigQ for item in sublist]
                #bigQ_list = [item for sublist in bigQ_list for item in sublist]
                #minQ = min(bigQ_arr)    #获取bigQ_list列表中的最小值
                Id = np.argmin(bigQ_arr)    #获取bigQ_list列表中的最小值的索引
                #Id = ind[minQ_index -1, 3]    #ind是调用R生成的，是从1开始
                if Id != None :
                    Id = Id
                #Id = Id[Id != None]
                #R: Id = Id[1]
                vx = J[str(Id)]
                fc = K[str(Id)]
                newmatch = np.vstack((vx, fc)).T
                matches = np.vstack((matches, newmatch))
                bigQ_arr[int(Id)] = None
                Id1 = efun(x = J.copy(), ftr = vx)
                Id2 = efun(x = K.copy(), ftr = fc)
                Id0 = np.array(list(Id1.values()))|np.array(list(Id2.values()))
                bigQ_arr[np.argwhere(Id0 == True)] = None
                vx = np.array(J[str(Id)])
                fc = np.array(K[str(Id)])
                nn[nn not in vx] = nn
                mm[mm not in fc] = fc
                Iter += 1
            else :
                Iter = float('inf')
        '''
        #out$unmatched <- list(X = nn, Xhat = mm)
        #colnames(matches) <- c("Forecast", "Observed")
        #out$matches <- matches
        #merges <- MergeIdentifier(matches)
        #out$merges <- merges
        
        #以观测场为准，匹配结果为：
        X_number = np.arange(len(X))
        #print(o_Ksi.shape)
        #print(o_Ksi)
        Xhat_number = o_Ksi[:, 0]
        Xmatches_number = pd.DataFrame(np.array((X_number+1, Xhat_number+1)).T, columns = ['Ob', 'Fcst'])
        #print(Xmatches_number)
        
        #(矩阵排列暂时存在问题)以预报场为准，匹配结果为：
        Xhat_number = np.arange(len(Xhat))
        X_number = o_Ksi[0, :]
        Xhatmatches_number = pd.DataFrame(np.array((Xhat_number+1, X_number+1)).T, columns = ['Fcst', 'Ob'])
        
        #调整unmatched存放结构
        a_obs = set(Xmatches_number['Ob'])
        a_fcst = set(Xmatches_number['Fcst'])
        if len(a_fcst) != len(Xhat):
            unmatched_X = set(np.arange(1,m+1)) - set(a_fcst)    #X未匹配的目标
            #print(unmatched_X)    
        else :
            unmatched_X = 'NULL'

        if len(a_obs) != len(X) :
            unmatched_Xhat = set(np.arange(1,n+1)) - set(a_obs)    #Xhat未匹配的目标
            #print(unmatched_Xhat)    
        else :
            unmatched_Xhat = 'NULL'
        unmatched = {'ob':unmatched_Xhat, 'fo':unmatched_X}


        matches = np.array([list(Xmatches_number['Fcst']), list(Xmatches_number['Ob'])])

        #unmatched = pd.DataFrame(unmatched, columns = ["Forecast", "Observed"])
        merges = restructuring(list(Xmatches_number['Fcst']), list(Xmatches_number['Ob']))
        out.update({'unmatched':unmatched, 'matches':matches, 'merges':merges, 'Xmatches_number':Xmatches_number,
                    'Xhatmatches_number':Xhatmatches_number})
        out.update({'identifier_function':"convthresh", 'identifier_label':"Convolution Threshold"})
            
    return out
    
#=============================  Example  ===================================
'''
#makeSpatialVx参数
hold = tra_makeSpatialVx_test.makeSpatialVx(X = pd.read_csv("F:\\Work\\MODE\\tra_test\\FeatureFinder\\pert000.csv"), \
                    Xhat = pd.read_csv("F:\\Work\\MODE\\tra_test\\FeatureFinder\\pert004.csv"), \
                    loc = pd.read_csv("F:\\Work\\MODE\\tra_test\\FeatureFinder\\ICPg240Locs.csv"), \
                    thresholds = [0.01, 20.01], projection = True, subset = None, timevals = None, reggrid = True,\
                    Map = True, locbyrow = True, fieldtype = "Precipitation", units = ("mm/h"), dataname = "ICP Perturbed Cases", obsname = "pert000", \
                    modelname = "pert004" , q = (0, 0.1, 0.25, 0.33, 0.5, 0.66, 0.75, 0.9, 0.95), qs = None)
#FeatureFinder参数
look = FeatureFinder_test_PA3.featureFinder(Object = hold, smoothfun = "disk2dsmooth", \
                     dosmooth = True, smoothpar = 17, smoothfunargs = None,\
                     thresh = 310, idfun = "disjointer", minsize = np.array([1]),\
                     maxsize = float("Inf"), fac = 1, zerodown = False, timepoint = 1,\
                     obs = 1, model = 1)


#deltaSqcen参数
x = lookFeatureFinder.copy()
p = 2
max_delta = float("Inf")
const = float("Inf")
N = 701    #设定矩形大小,需要设定比行列数大至少100，否则坐标经过变化以后会超出范围，程序报错
show = False    #选择是否需要在屏幕打印

lookdeltammSqcen = deltammSqcen(x = look.copy(), p = 2, max_delta = float("Inf"), const = float("Inf"), N = 701, show = False)
'''







