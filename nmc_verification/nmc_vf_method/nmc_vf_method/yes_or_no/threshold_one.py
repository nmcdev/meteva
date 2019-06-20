# _*_ coding: utf-8 _*_
# 提供Yes/No 类型的预报结果的检验

import numpy as np

def hit_rate(Ob,Fo,threshold):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一个命中率
    hit,mis,fal,_ = hmfn(Ob,Fo,threshold)
    return hit/(hit + mis + 0.0000001)

def fal_rate(Ob,Fo,threshold):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一个命中率
    hit,mis,fal,_ = hmfn(Ob,Fo,threshold)
    return fal/(hit + fal + 0.0000001)


def mis_rate(Ob,Fo,threshold):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一个漏报率
    hit,mis,fal,_ = hmfn(Ob,Fo,threshold)
    return mis/(hit + mis + 0.0000001)

def bias(Ob,Fo,threshold):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一个bias值
    hit, mis, fal, _ = hmfn(Ob, Fo, threshold)
    return (hit + fal) / (hit + mis + 0.0000001)

def ts(Ob,Fo,threshold):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一个ts评分值
    hit,mis,fal,_ = hmfn(Ob,Fo,threshold)
    return ts_hmfn(hit,mis,fal)

def ts_hmfn(hit,mis,fal):
    # 输入命中、空报、漏报数，返回ts评分值
    return hit/(hit+mis+fal+0.000001)

def ets(Ob,Fo,threshold):
    #输入观测Ob和预报Fo的预报数据（1维的numpy数组），以及判断事件是否发生的阈值threshold，
    # 返回一个ets评分值
    hit,mis,fal,cn = hmfn(Ob,Fo,threshold)
    return ets_hmfn(hit,mis,fal,cn)

def ets_hmfn(hit,mis,fal,cn):
    # 输入命中数、空报数、漏报数、正确否定数
    # 返回ets评分值
    total = hit + mis + fal + cn + 0.000001  # 加0.0000001 为防止出现除0情况
    hit_random = (hit + mis) * (hit + fal) / total
    return (hit - hit_random)/(hit + mis + fal - hit_random + 0.000001)

def hmfn(Ob,Fo,threshold):
    # 输入观测Ob和预报Fo的预报数据（1维的numpy数组）
    #返回命中数、空报数、漏报数、正确否定数
    num = np.size(Ob)
    obhap = np.zeros(num)
    obhap [Ob >= threshold] = 1
    fohap = np.zeros(num)
    fohap[Fo >= threshold] = 1

    hit = (obhap * fohap)
    mis = (obhap * (1 - fohap))
    fal = ((1 - obhap) * fohap)
    cn = ((1 - obhap) * (1-fohap))
    return hit.sum(),mis.sum(),fal.sum(),cn.sum()

