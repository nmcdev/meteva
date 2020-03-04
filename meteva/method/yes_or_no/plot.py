import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
from meteva.method.yes_or_no.score import *
import math

def performance(ob,fo,grade_list = [1e-30],save_path = None,title = "综合表现图"):
    '''

    :param ob:
    :param fo:
    :param grade_list:
    :return:
    '''

    hfmc_array = hfmc(ob, fo, grade_list)
    pod = pod_hfmc(hfmc_array)
    sr = sr_hfmc(hfmc_array)
    leftw = 0.6
    rightw = 0.6
    uphight = 1.2
    lowhight = 1.2
    axis_size_x = 3.7
    axis_size_y = 3.5
    width = axis_size_x + leftw + rightw
    hight = axis_size_y + uphight + lowhight

    fig = plt.figure(figsize=(width, hight))
    ax1 = fig.add_axes([leftw/width, lowhight/width, axis_size_x/width, axis_size_y/hight])


    x = np.arange(0.0001, 1, 0.0001)
    bias_list = [0.2, 0.4,0.6,0.8, 1,1.25, 1.67, 2.5,5]
    ts_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for i in range(len(bias_list)):
        bias = bias_list[i]
        y1 = bias * x
        x2 = x[y1<1]
        y2 = y1[y1<1]
        if bias < 1:
            ax1.plot(x2, y2, '--', color='k', linewidth=0.5)
            ax1.text(1.01, bias, "bias=" + str(bias))
        elif bias > 1:
            ax1.plot(x2, y2, '--', color='k', linewidth=0.5)
            ax1.text(1.0 / bias - 0.05, 1.02, "bias=" + str(bias))
        else:
            ax1.plot(x2, y2, '-', color='k', linewidth=0.5)

    for i in range(len(ts_list)):
        ts = ts_list[i]
        hf = 1
        x2 = np.arange(ts, 1, 0.001)
        hit = hf * x2
        hfm = hit / ts
        m = hfm - hf
        y2 = hit / (hit + m)
        plt.plot(x2, y2, "--", color="y", linewidth=0.5)
        error = np.abs(y2 - x2)
        index = np.argmin(error)
        sx = x2[index] + 0.02
        sy = y2[index] - 0.02
        ax1.text(sx, sy, "ts=" + str(ts))

    colors = cm.get_cmap('rainbow', 128)
    for i in range(len(grade_list)):
        color_grade = (i +0.5) /len(grade_list)
        ax1.plot(sr[i], pod[i], 'o', color=colors(color_grade),markersize=12,label = ("grade:" + str(grade_list[i])))

    nline = math.ceil(len(grade_list)/3)
    ax1.legend(loc = "lower left",bbox_to_anchor=(0, -(0.18 + 0.05 * nline)),ncol=3,fontsize = 10)
    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    ax1.set_xlabel("成功率",fontsize = 14)
    ax1.set_ylabel("命中率",fontsize = 14)
    title = title +"\n"
    ax1.set_title(title)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        print("检验结果已以图片形式保存至" + save_path)
    plt.close()


def performance_hfmc(hfmc_array,axis_list_list,suplot_lengend = [1,0],save_dir = None):
    '''
    :param ob:
    :param fo:
    :param grade_list:
    :return:

    grade_count = len(grade_list)
    group_count = len(group_list)
    if grade_count == 1:
        #只有一种等级的
        pass
    elif group_list == 1:
        pass
    else:
        pass



    if grade_count == 1 or group_count == 1:
        column = 1
        row = 1
        if grade_count == 1:
            legend_list = group_list
        else:
            legend_list = grade_list
        subplot_count = 1
    else:
        column = 2
        row = int(math.ceil(grade_count/2))
        legend_list = group_list
        subplot_count = grade_count

    plt.figure(figsize=(column * 5, row * 4.5))
    plt.subplots_adjust(wspace = 0.5,hspace = 0.3)

    pod = pod_hfmc(hfmc_array)
    sr = sr_hfmc(hfmc_array)
    x = np.arange(0.0001, 1, 0.0001)
    bias_list = [0.2, 0.4, 0.6, 0.8, 1, 1.25, 1.67, 2.5, 5]
    ts_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


    for s in range(subplot_count):
        plt.subplot(column, row, s+1)
        for i in range(len(bias_list)):
            bias = bias_list[i]
            y1 = bias * x
            x2 = x[y1 < 1]
            y2 = y1[y1 < 1]
            if bias < 1:
                plt.plot(x2, y2, '--', color='k', linewidth=0.5)
                plt.text(1.01, bias, "bias=" + str(bias))
            elif bias > 1:
                plt.plot(x2, y2, '--', color='k', linewidth=0.5)
                plt.text(1.0 / bias - 0.05, 1.02, "bias=" + str(bias))
            else:
                plt.plot(x2, y2, '-', color='k', linewidth=0.5)

        for i in range(len(ts_list)):
            ts = ts_list[i]
            hf = 1
            x2 = np.arange(ts, 1, 0.001)
            hit = hf * x2
            hfm = hit / ts
            m = hfm - hf
            y2 = hit / (hit + m)
            plt.plot(x2, y2, "--", color="y", linewidth=0.5)
            error = np.abs(y2 - x2)
            index = np.argmin(error)
            sx = x2[index] + 0.02
            sy = y2[index] - 0.02
            plt.text(sx, sy, "ts=" + str(ts))

        colors = cm.get_cmap('rainbow', 128)
        for i in range(sr.shape[0]):
            color_grade = (i +0.5) /len(legend_list)
            plt.plot(sr[i,s], pod[i,s], 'o', color=colors(color_grade),markersize=12,label = legend_list[i])

        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.xlabel("成功率",fontsize = 14)
        plt.ylabel("命中率",fontsize = 14)


    if len(legend_list) < 10:
        legend_ncol = len(legend_list)
    else:
        legend_ncol = int(math.ceil(len(legend_list)/2))
    plt.legend(loc='upper center', bbox_to_anchor=(0, -0.05,1,1),ncol = legend_ncol,bbox_transform=plt.gcf().transFigure)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
    '''
