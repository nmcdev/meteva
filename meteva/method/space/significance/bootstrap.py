#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 12 00:05:09 2022

@author: tangbuxing
"""

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot
from sklearn.utils import resample
from matplotlib import pyplot as plt

# from statsmodels.base.model import GenericLikelihoodModelResults


# test_sample = np.array([1.865, 3.053, 1.401, 0.569, 4.132])
# r的结果
res_r = pd.read_csv(r"/Users/tangbuxing/Desktop/tra_test-SAL/fieldSignficance/data/booted003.csv")
# python重采样
test_sample = pd.read_csv(r"/Users/tangbuxing/Desktop/tra_test-SAL/fieldSignficance/data/booted001data.csv")
# boots_samples_01 = [np.mean(test_sample.sample(19, replace=True)) for _ in range(100000)]
boots_samples = [np.mean(resample(test_sample, n_samples=361)) for _ in range(10000)]  # n_samples是受tseries控制

# boots_samples = [np.mean(resample(test_sample, n_samples = 19)) for _ in range(500)]

# boot_var = [np.var(resample(test_sample)) for _ in range(19)]

# 画图
# a_r=pd.cut(res_r['t'],[-0.6,-0.5,-0.4,-0.3,-0.2,-0.1,0,0.1,0.2,0.3,0.4,0.5,0.6])
a_r = pd.cut(res_r['t'], [-1.0, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])

b_r = a_r.value_counts()
b_r2 = b_r.sort_index()

# 画柱状图
c = {'section': b_r2.index, 'frequency': b_r2.values}
e = pd.DataFrame(c)
plt.rcParams['font.sans-serif'] = ['SimHei']
ax = plt.figure(figsize=(10, 5)).add_subplot(111)
sns.barplot(x="section", y="frequency", data=e, palette="Set3")  # palette设置颜色

aa = np.array(boots_samples).reshape(10000, )
a_p = pd.cut(aa, [-1.0, -0.9, -0.8, -0.7, -0.6, -0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6])
b_p = a_p.value_counts()
b_p2 = b_p.sort_index()
c = {'section': b_p2.index, 'frequency': b_p2.values}
e = pd.DataFrame(c)
plt.rcParams['font.sans-serif'] = ['SimHei']
ax = plt.figure(figsize=(10, 5)).add_subplot(111)
sns.barplot(x="section", y="frequency", data=e, palette="Set3")  # palette设置颜色

names = range(8, 21)
names = [str(x) for x in list(names)]

x = range(len(names))
y_train = [-0.5, -0.4, -0.3, -0.2, -0.1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
y_test = [0.838, 0.840, 0.840, 0.834, 0.828, 0.814, 0.812, 0.822, 0.818, 0.815, 0.807, 0.801, 0.796]

plt.plot(y_train, b_p2, marker='o', mec='r', mfc='w', label='python')
plt.plot(y_train, b_r2, marker='*', ms=10, label='r')
plt.legend()  # 让图例生效
plt.xticks(y_train, names, rotation=1)

res_r = pd.read_csv(r"/Users/tangbuxing/Desktop/tra_test-SAL/fieldSignficance/data/rnorm00.csv")
a_r = pd.cut(res_r['x'], [-3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0])

b_r = a_r.value_counts()
b_r2 = b_r.sort_index()
c = {'section': b_r2.index, 'frequency': b_r2.values}
e = pd.DataFrame(c)
plt.rcParams['font.sans-serif'] = ['SimHei']
ax = plt.figure(figsize=(10, 5)).add_subplot(111)
sns.barplot(x="section", y="frequency", data=e, palette="Set3")  # palette设置颜色

mu, sigma = 0, 1  # mean and standard deviation
# z = np.random.normal(mu, sigma, 361)    #正态分布存在差异
z = np.random.randn(361)  # 均匀分布
aa = np.array(z).reshape(361, )
a_p = pd.cut(aa, [-3.5, -3.0, -2.5, -2.0, -1.5, -1.0, -0.5, 0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5])
b_p = a_p.value_counts()
b_p2 = b_p.sort_index()
c = {'section': b_p2.index, 'frequency': b_p2.values}
e = pd.DataFrame(c)
plt.rcParams['font.sans-serif'] = ['SimHei']
ax = plt.figure(figsize=(10, 5)).add_subplot(111)
sns.barplot(x="section", y="frequency", data=e, palette="Set3")  # palette设置颜色
