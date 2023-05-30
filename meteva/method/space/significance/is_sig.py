#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 24 16:39:08 2022

"""
import numpy as np
from scipy import stats
import sys

#sys.path.append(r'/Users/tangbuxing/Desktop/tra_test-SAL/fieldSignficance/lib')
from meteva.method.space.field_significance import sig_coverage
#import sig_coverage


def sig_cor_t(r, Len=40):
    t = abs(r) * np.sqrt((Len - 2) / (1 - r ** 2))
    # qt -> stats.t(df=359).ppf((0.84473448, 0.15382939))
    palpha_cor = 1 - stats.t.cdf(t, df=Len - 2)  # t分布的分布函数
    return palpha_cor


def MCdof(x, ntrials=1000, field_sig=0.05, zfun="rnorm", zfun_args='NULL',
          which_test=["t", "Z", "cor.test"], show=False):

    output = {}
    if len(which_test) > 1:
        which_test = "t"
    x = np.array(x)
    xdim = x.shape
    tlen = xdim[0]
    B_dof_test = np.zeros(ntrials)
    if show:
        print("\n", "Looping through ", ntrials, " times to simulate data and take correlations.  Enjoy!\n")
    for i in range(1, ntrials):
        if show and (i < 100 or i % 100 == 0):
            print(i, " ")
        # rnorm(n, mean = 0, sd = 1)返回值是n个正态分布随机数构成的向量。
        mu, sigma = 0, 1  # mean and standard deviation
        z = np.random.normal(mu, sigma, tlen)  # 正态分布存在差异
        '''
        #绘制正态分布图
        count, bins, ignored = plt.hist(s, 30, density=True)
        plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ),
                 linewidth=2, color='r')
        plt.show()
        '''
        # 判断为否，不执行
        tmp = np.array([])
        if which_test == "cor.test":
            # tmp = apply(x, 2, cortester, y = z)
            tmp = np.corrcoef(x)[1, 0]
        else:
            #默认进行t检验
            # 计算pearson相关系数
            cor = np.array([])
            for j in range(x.shape[1]):  # 循环变量有问题
                x_j = x[:, j]
                xz = np.array([x_j, z])
                cor_0 = np.corrcoef(xz)[1, 0]  # 目前存在偏差是由于z的结果不一致导致，方法本身经过验证是没问题的
                cor = np.append(cor, cor_0)
            cor_value = np.abs(cor)
            # 只翻译默认的第一个参数
            if which_test == "t":
                tmp = sig_cor_t(r=cor_value, Len=tlen)  # 输出结果
            '''
            else if (which.test == "Z") 
                tmp <- sig.cor.Z(cor.value, len = tlen, ...)
            '''
        tmp_small = tmp[field_sig>tmp] #提取显著性超阈值那部分显著性

        # if tmp_small.size == 0:
        #     B_dof_test[i] = 1
        # else:
        #     B_dof_test[i] = np.mean(tmp_small)  # 显著性超阈值部分的均值
        B_dof_test[i] = tmp_small.size / tmp.size

    minsigcov_val = np.quantile(a=B_dof_test, q=1 - field_sig)
    output = {'MCprops': B_dof_test, 'minsigcov': minsigcov_val}
    return output


def is_sig(X, blockboot_result_df, n=1000, fld_sig=0.05, show=False):
    output = {}
    '''
    X = errfield
    blockboot_result_df = hold
    n = ntrials
    fld_sig = field_sig
    '''

    # sig_result 表示利用蒙特卡罗方法测试所有格点和随机数求相关后，表现为具有显著性的格点数占比。
    sig_result = MCdof(X, ntrials=n, field_sig=0.05, show=show)['minsigcov']

    #actual_coverage表示平均值具有显著性的格点数占比。
    actual_coverage = sig_coverage.sig_coverage(DF=blockboot_result_df)
    sig = actual_coverage > sig_result  #输出结果
    '''
    output <- list(name = as.character(deparse(substitute(X))), 
                   required = as.numeric(sig.results), actual = as.numeric(actual.coverage), 
                   issig = as.logical(sig))
    '''
    output = {"name": X, "required": sig_result, "actual": actual_coverage, "issig": sig}

    return output






