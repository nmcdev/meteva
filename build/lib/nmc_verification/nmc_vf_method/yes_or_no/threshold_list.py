# _*_ coding: utf-8 _*_
# 提供Yes/No 类型的预报结果的检验

import numpy as np



def hit_rate(Ob,Fo,threshold_list):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一维命中率评分值数组，数组中的每个值对应一个等级
    hit,mis,fal,_ = hmfn(Ob,Fo,threshold_list)
    return hit/(hit + mis + 0.0000001)

def fal_rate(Ob,Fo,threshold_list):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一维空报率评分值数组，数组中的每个值对应一个等级
    hit,mis,fal,_ = hmfn(Ob,Fo,threshold_list)
    return fal/(hit + fal + 0.0000001)


def mis_rate(Ob,Fo,threshold_list):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一维漏报率评分值数组，数组中的每个值对应一个等级
    hit,mis,fal,_ = hmfn(Ob,Fo,threshold_list)
    return mis/(hit + mis + 0.0000001)

def bias(Ob,Fo,threshold_list):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一维bias评分值数组，数组中的每个值对应一个等级
    hit, mis, fal, _ = hmfn(Ob, Fo, threshold_list)
    return (hit + fal) / (hit + mis + 0.0000001)

def ts(Ob,Fo,threshold_list):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值value，
    # 返回一维ts评分值数组，数组中的每个值对应一个等级
    hit,mis,fal,_ = hmfn(Ob,Fo,threshold_list)
    return ts_hmfn(hit,mis,fal)

def ts_hmfn(hit,mis,fal):
    # 输入命中、空报、漏报数
    # 返回一维ts评分值数组，数组中的每个值对应一个等级
    return hit/(hit+mis+fal+0.000001)

def ets(Ob,Fo,threshold_list):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值value，
    # 返回一维ets评分值数组，数组中的每个值对应一个等级
    hit,mis,fal,cn = hmfn(Ob,Fo,threshold_list)
    return ets_hmfn(hit,mis,fal,cn)

def ets_hmfn(hit,mis,fal,cn):
    # 输入命中数、空报数、漏报数、正确否定数
    # 返回一维ets评分值数组，数组中的每个值对应一个等级
    total = hit + mis + fal + cn + 0.000001  # 加0.0000001 为防止出现除0情况
    hit_random = (hit + mis) * (hit + fal) / total
    return (hit - hit_random)/(hit + mis + fal - hit_random + 0.000001)

def hmfn(Ob,Fo,threshold_list):
    # 输入观测Ob和预报Fo的预报数据（1维的numpy数组）
    #返回命中数、空报数、漏报数、正确否定数共4个数组，数组中的每个值对应一个等级
    hit = np.zeros(len(threshold_list))
    mis = np.zeros(len(threshold_list))
    fal = np.zeros(len(threshold_list))
    cn = np.zeros(len(threshold_list))
    for i in range(len(threshold_list)):
        threshold = threshold_list[i]
        num = np.size(Ob)
        obhap = np.zeros(num)
        obhap [Ob >= threshold] = 1
        fohap = np.zeros(num)
        fohap[Fo >= threshold] = 1

        hit_threshold = (obhap * fohap)
        mis_threshold = (obhap * (1 - fohap))
        fal_threshold = ((1 - obhap) * fohap)
        cn_threshold = ((1 - obhap) * (1-fohap))
        hit[i] = hit_threshold.sum()
        mis[i] = mis_threshold.sum()
        fal[i] = fal_threshold.sum()
        cn[i] = cn_threshold.sum()
    return hit,mis,fal,cn

