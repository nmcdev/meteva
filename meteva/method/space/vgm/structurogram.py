# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 18:12:20 2021
"""
import numpy as np
import math
import matplotlib.pyplot as plt
import meteva

def rdist(Id, loc):
    # 计算两点间欧式距离
    a = Id[:,0]
    b = Id[:,1]
    lat_lon0 = loc[a]
    lat_lon1 = loc[b]
    sr=np.cos(0.5*(lat_lon0[:,0]+lat_lon1[:,0])*math.pi/180)
    d1=(lat_lon0[:,1] - lat_lon1[:,1])*sr
    d2=(lat_lon0[:,0] - lat_lon1[:,0])
    dd = np.sqrt(d1*d1+d2*d2)
    dd *= meteva.base.dis_1_degree
    return dd


def dv(sta,dmax = None, q = 1):
    '''

    :param sta: 输入单个层次、单个时刻、单个时效的站点数据
    :param q:  q=1对应误差绝对值，q=2对应误差的平方
    :param dmax:  距离大于dmax的样本将被滤除
    :return:  N×（站点数据列数+1）  的二维数组，第1列为距离值，之后为sta中每个数据列中样本的
    '''
    sta1 = meteva.base.not_IV(sta)
    loc =sta1[["lat","lon"]].values
    n = len(loc)
    names = meteva.base.get_stadata_names(sta)
    aa = np.tile(np.arange(0, n), n)
    bb = np.repeat(np.arange(0, n), n)
    ind = aa > bb
    Id = np.vstack((aa, bb)).T[ind, :]
    d = rdist(Id,loc)
    od = np.argsort(d)
    d = d[od]
    index = None
    if dmax is not None:
        index = np.where(d<dmax)
        d = d[index]
    dv_list = [d]

    for name in names:
        y = sta1[name].values
        if q == 1:
            v = np.abs(y[Id[:, 0]] - y[Id[:, 1]])
        else:
            v = (y[Id[:, 0]] - y[Id[:, 1]]) ** q
        v = v[od]
        if index is not None:
            v = v[index]
        dv_list.append(v)
    dv_array = np.vstack(tuple(dv_list)).T
    return dv_array

def dv_merge(dv_array1,dv_array2):
    '''
    将两个变率样本结果合并
    :param dv_array1: 变率样本矩阵2
    :param dv_array2: 变率样本矩阵2
    :return:
    '''
    dv_array = np.vstack((dv_array1,dv_array2))
    return dv_array

def plot_dv(dv_array,dmax = None,grade_count = 10
            , member_list=None, width=None, height=None, xlabel="距离（km）",ylabel1="变化幅度(统计值）",ylabel2="变化幅度(箱须图）"
            ,title = "Variogram(变差图)",
            dpi=300, show=False, save_path=None, sup_fontsize=10
            ):

    '''
    将变率样本矩阵绘制成图形产品
    :param dv_array: 变率样本矩阵
    :param grade_count: 绘图时，将样本按距离分为 grade_count组进行统计
    :param dmax:         统计的最大距离值，超出的部分会被剔除
    :param member_list:    legend 的名称内容
    :param width:         画面的宽度
    :param height:        画面的高度
    :param xlabel:
    :param ylabel1:
    :param ylabel2:
    :param dpi:
    :param show:
    :param save_path:
    :param sup_fontsize:
    :return:
    '''
    if dmax is None:
        dmax = np.max(dv_array[:,0])
    grade = dmax / grade_count
    grade_list = (grade * (np.arange(grade_count)+1)).astype(np.int16)
    if height is None:
        height = 4
    if width is None:
        width = meteva.base.tool.plot_tools.caculate_axis_width(grade_list,sup_fontsize*1.5,legend_num=1)
    fig = plt.figure(figsize=(width, height),dpi = dpi)

    grid_plt = plt.GridSpec(9, 1, hspace=0)
    cmv_array, dmax = dv_statistic(dv_array, dmax, grade_count)

    ax0 = plt.subplot(grid_plt[0:4, 0])
    plt.title(title,fontsize = sup_fontsize)
    v_count = dv_array.shape[-1] - 1
    label = []
    if member_list is None:

        label = ["观测"]
        for i in range(1, v_count):
            label.append('预报' + str(i))
    else:
        label.extend(member_list)

    color_list = meteva.base.color_tools.get_color_list(v_count)
    x = np.arange(0.5, grade_count)

    plt.yticks(fontsize=sup_fontsize * 0.8)
    plt.ylabel(ylabel1, fontsize=sup_fontsize * 0.9)
    max_list = []
    for v in range(v_count):
        plt.plot(x, cmv_array[1, :, v], c=color_list[v], label=label[v])
        var = np.sqrt(cmv_array[2, :, v])
        plt.plot(x, cmv_array[1, :, v] - var, "--", c=color_list[v], linewidth=0.7)
        max_list.append(np.max(cmv_array[1, :, v] + var))
        plt.plot(x, cmv_array[1, :, v] + var, "--", c=color_list[v], linewidth=0.7)
    maxv = np.max(np.array(max_list))
    plt.ylim(0, maxv * 1.2)
    plt.legend(loc=2, ncol=4, fontsize=sup_fontsize * 0.8)

    d = dv_array[:, 0]
    boxgroup = []
    combineData = []

    tcount = []


    for i in range(grade_count):
        index = np.where((d> i*grade) & (d<=(i+1)* grade))
        count = len(index[0])
        tcount.append(count)
        for v in range(1,v_count+1):
            dat = dv_array[index,v].squeeze()
            combineData.append(dat)
            bg = np.ones(count) * i + 0.5
            boxgroup.append(bg)



    ax1 = plt.subplot(grid_plt[4:8, 0])

    red_square = dict(markerfacecolor='k',markeredgecolor = "k", markersize = 0.5)
    medianprops = dict(color = "k")
    bplot = ax1.boxplot(combineData,boxgroup, showfliers=True, patch_artist=True, sym='.',flierprops=red_square,medianprops = medianprops)
    color_list =meteva.base.color_tools.get_color_list(v_count)

    for i, item in enumerate(bplot["boxes"]):
        ci  = i%v_count
        item.set_facecolor(color_list[ci])
        item.set_edgecolor(color_list[ci])




    plt.subplots_adjust(left=0.5 / width, right=1 - 0.1 / width)
    plt.ylabel(ylabel2, fontsize=sup_fontsize * 0.9)
    plt.yticks(fontsize=sup_fontsize * 0.8)
    #plt.legend(fontsize=sup_fontsize * 0.8, ncol=3, loc="upper center")
    #plt.xlim(0,0.1)
    maxv = np.max(dv_array[:,1:])
    plt.ylim(0,maxv*1.2)
    #plt.legend(loc =2,ncol = 4,fontsize = sup_fontsize * 0.8)
    ax2 = plt.subplot(grid_plt[8, 0])
    plt.bar(x, tcount, width=0.5, label="样本数",color = "grey")
    plt.xlabel(xlabel, fontsize=sup_fontsize * 0.9)
    plt.xticks(x+0.5,grade_list)
    plt.xlim(0, len(tcount))
    plt.ylim(0, np.max(tcount) * 1.5)
    plt.ylabel("样本数",fontsize = sup_fontsize * 0.9)
    plt.grid()

    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()



def dv_statistic(dv_array,dmax = None,grade_count=10):
    '''
    从变率样本矩阵中，统计出每一段距离范围内，平均的变率，以及变率值本身的方差
    :param dv_array:
    :param dmax:
    :param grade_count:
    :return:
    '''
    if dmax is None:
        dmax = np.max(dv_array[:,0])
    d_step = dmax/grade_count
    v_count = dv_array.shape[1] - 1

    #c：count, m ：mean， v :var
    cmv_array = np.zeros((3,grade_count,v_count))
    d = dv_array[:, 0]
    for i in range(grade_count):
        index = np.where((d> i*d_step) & (d<=(i+1)* d_step))
        count = len(index[0])
        if count>0:
            for j in range(v_count):
                cmv_array[0,i,j] = count
                v = dv_array[index,j+1]
                cmv_array[1,i,j] = np.mean(v)
                cmv_array[2,i, j] = np.var(v)

    #返回dmax，是方便后续程序确切了解组成采用dmax参数值
    return cmv_array,dmax

def merge_dv_statistic(cmv_array1,cmv_array2):
    '''
    将统计结果合并
    :param cmv_array1:
    :param cmv_array2:
    :return:
    '''
    count_array,mean_array,var_array = meteva.base.math_tools.ss_iteration(cmv_array1[0,...],cmv_array1[1,...],cmv_array1[2,...],
                                                                           cmv_array2[0,...],cmv_array2[1,...],cmv_array2[2,...])

    cmv_array = np.vstack((count_array,mean_array,var_array))
    return cmv_array


def plot_dv_statistic(cmv_array,dmax,member_list = None,width = None,height = None,xlabel = "距离（km）",ylabel = "变化幅度",
                      title = "Variogram(变差图)",
                      dpi = 300,show =False,save_path = None,sup_fontsize = 12):
    '''
    绘制变率统计结果
    :param cmv_array:
    :param dmax:
    :param member_list:
    :param width:
    :param height:
    :param xlabel:
    :param ylabel:
    :param dpi:
    :param show:
    :param save_path:
    :param sup_fontsize:
    :return:
    '''
    if height is None:
        height = 3

    grade_count = cmv_array.shape[-2]
    grade = dmax / grade_count

    grade_list = (grade * (np.arange(grade_count)+1)).astype(np.int16)
    grade_list_mid = (grade * (np.arange(grade_count)+0.5)).astype(np.int16)
    if width is None:
        width = meteva.base.tool.plot_tools.caculate_axis_width(grade_list,sup_fontsize*1.5,legend_num=1)
    fig = plt.figure(figsize=(width, height),dpi = dpi)

    v_count = cmv_array.shape[-1]
    label = []
    if member_list is None:

        label = ["观测"]
        for i in range(1,v_count):
            label.append('预报' + str(i))
    else:
        label.extend(member_list)

    color_list =meteva.base.color_tools.get_color_list(v_count)

    grid_plt = plt.GridSpec(5, 1, hspace=0)
    ax1 = plt.subplot(grid_plt[0:4, 0])
    plt.title(title,fontsize = sup_fontsize)
    plt.yticks(fontsize = sup_fontsize * 0.8)
    plt.ylabel(ylabel,fontsize = sup_fontsize * 0.9)
    max_list =[]
    for v in range(v_count):
        plt.plot(grade_list_mid,cmv_array[1,:,v],c = color_list[v],label= label[v])
        var = np.sqrt(cmv_array[2,:,v])
        plt.plot(grade_list_mid,cmv_array[1,:,v] - var,"--",c = color_list[v],linewidth =0.5)
        max_list.append(np.max(cmv_array[1,:,v] + var))
        plt.plot(grade_list_mid,cmv_array[1,:,v] + var,"--",c = color_list[v],linewidth =0.5)


    plt.xlim(0,grade_list[-1])
    maxv = np.max(np.array(max_list))
    plt.ylim(0,maxv*1.2)
    plt.legend(loc =2,ncol = 4,fontsize = sup_fontsize * 0.8)
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax2 = plt.subplot(grid_plt[4, 0], sharex=ax1)
    plt.yticks(fontsize=sup_fontsize * 0.8)
    plt.ylabel("样本数",fontsize = sup_fontsize * 0.9)
    plt.xlim(0,grade_list[-1])
    plt.xlabel(xlabel,fontsize = sup_fontsize * 0.9)
    plt.bar(grade_list_mid, cmv_array[0,:,0], width=grade * 0.5,color = "grey")
    #plt.xlabel(xlabel=grade_list)

    plt.xticks(grade_list,fontsize = sup_fontsize * 0.8)
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()


def vgm_sta(sta,dmax,grade_count = 10,q = 1,xlabel = "距离（km）",ylabel = "变化幅度",title = "Variogram(变差图)",
                  dpi = 300,show =False,save_path = None,sup_fontsize  = 10,width = None,height = None):
    '''
    统计函数的主入口，    统计并绘制要素值随距离变化的程度，只包括统计值曲线
    :param sta:
    :param q:
    :param dmax:
    :param grade_count:
    :param width:
    :param height:
    :param xlabel:
    :param ylabel:
    :param dpi:
    :param show:
    :param save_path:
    :param sup_fontsize:
    :return:
    '''
    data_names = meteva.base.get_stadata_names(sta)
    sta_list = meteva.base.split(sta)

    dv_array = dv(sta_list[0],dmax = dmax,q = q)
    cmv_array,dmax  = dv_statistic(dv_array,dmax = dmax,grade_count=grade_count)
    n_sta = len(sta_list)
    if n_sta >1:
        dv_array1 = dv(sta_list[0], dmax=dmax, q=q)
        cmv_array1, _ = dv_statistic(dv_array1, dmax=dmax, grade_count=grade_count)
        cmv_array= merge_dv_statistic(cmv_array,cmv_array1)

    plot_dv_statistic(cmv_array,dmax,member_list=data_names,width=width,height=height,
                      xlabel = xlabel,ylabel = ylabel,
                      dpi = dpi,show = show,title = title,save_path=save_path,sup_fontsize=sup_fontsize)
    return cmv_array


def vgm_sta_box(sta,dmax,grade_count = 10,q = 1,xlabel = "距离（km）",ylabel1="变化幅度(统计值）",ylabel2="变化幅度(箱须图）",title = "Variogram(变差图)",
                  dpi = 300,show =False,save_path = None,sup_fontsize  = 10,width = None,height = None):
    '''
    统计并绘制要素值随距离变化的程度，包括统计值和箱须图
    :param sta:
    :param dmax:
    :param q:
    :param grade_count:
    :param width:
    :param height:
    :param xlabel:
    :param ylabel1:
    :param ylabel2:
    :param dpi:
    :param show:
    :param save_path:
    :param sup_fontsize:
    :return:
    '''
    data_names = meteva.base.get_stadata_names(sta)
    sta_list = meteva.base.split(sta)
    dv_array = dv(sta_list[0],dmax = dmax,q = q)

    n_sta = len(sta_list)
    if n_sta >1:
        dv_array1 = dv(sta_list[0], dmax=dmax, q=q)
        dv_array = dv_merge(dv_array,dv_array1)
    plot_dv(dv_array,dmax,grade_count,member_list=data_names,width=width,height=height,
                      xlabel = xlabel,ylabel1 = ylabel1,ylabel2= ylabel2,title = title,
                      dpi = dpi,show = show,save_path=save_path,sup_fontsize=sup_fontsize)

    return dv_array













