import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np

from sklearn.linear_model import LinearRegression


def scatter_regress(ob, fo, save_path=None):
    '''
    绘制观测-预报散点图和线性回归曲线
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param save_path:图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    :return:图片，包含散点图和线性回归图,横坐标为观测值，纵坐标为预报值，横坐标很纵轴标取值范围自动设为一致，在图形中间添加了完美预报的参考线。
    '''
    width = 5
    height = 5
    fig = plt.figure(figsize=(width, height))
    markersize = 50 * width * height / ob.size
    if markersize <1:
        markersize = 1
    elif markersize >20:
        markersize = 20
    plt.plot(ob, fo, '.',color= 'b',  markersize=markersize)
    X = np.zeros((len(ob), 1))
    X[:, 0] = ob
    clf = LinearRegression().fit(X, fo)
    num_max = max(np.max(ob),np.max(fo))
    num_min = min(np.min(ob),np.min(fo))
    dmm = num_max - num_min
    if(num_min != 0):
        num_min -= 0.1 * dmm
    num_max += dmm * 0.1
    dmm = num_max - num_min
    ob_line = np.arange(num_min, num_max, dmm / 30)

    X = np.zeros((len(ob_line), 1))
    X[:, 0] = ob_line
    fo_rg = clf.predict(X)
    plt.plot(ob_line, fo_rg,color = "r")
    plt.plot(ob_line, ob_line,'--', color="k")
    plt.xlim(num_min, num_max)
    plt.ylim(num_min, num_max)
    plt.xlabel("观测",fontsize = 14)
    plt.ylabel("预报",fontsize = 14)
    rg_text2 = "y = " + '%.2f' % (clf.coef_[0]) + "* x + " + '%.2f' % (clf.intercept_)
    plt.text(num_min + 0.05 * dmm, num_min + 0.90 * dmm, rg_text2, fontsize=15,color ="r")
    plt.title("散点回归图",fontsize = 14)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)


def pdf_plot(ob, fo, save_path=None):
    '''
    sorted_ob_fo 将传入的两组数据先进行排序
    然后画出折线图
    ----------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param save_path: 图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    :return:图片，包含频率匹配映射关系图,横坐标为观测值，纵坐标为预报值，横坐标很纵轴标取值范围自动设为一致，在图形中间添加了完美预报的参考线。
    '''
    width = 11
    height = 5
    fig = plt.figure(figsize=(width, height))

    num_max = max(np.max(ob), np.max(fo))
    num_min = min(np.min(ob), np.min(fo))
    dmm = num_max - num_min
    if (num_min != 0):
        num_min -= 0.1 * dmm
    num_max += dmm * 0.1
    dmm = num_max - num_min



    ob_sorted = np.sort(ob.flatten())
    fo_sorted = np.sort(fo.flatten())
    ob_sorted_smooth = ob_sorted
    ob_sorted_smooth[1:-1] = 0.5 * ob_sorted[1:-1] + 0.25 * (ob_sorted[0:-2] + ob_sorted[2:])
    fo_sorted_smooth = fo_sorted
    fo_sorted_smooth[1:-1] = 0.5 * fo_sorted[1:-1] + 0.25 * (fo_sorted[0:-2] + fo_sorted[2:])

    plt.subplot(1,2,1)
    y = np.arange(len(ob_sorted_smooth))/(len(ob_sorted_smooth))
    plt.plot(ob_sorted_smooth,y,"r",label = "观测")
    plt.plot(fo_sorted_smooth,y,"b",label = "预报")
    plt.xlabel("变量值",fontsize = 14)
    plt.ylabel("累积概率",fontsize = 14)
    plt.title("概率分布函数对比图",fontsize = 14)
    yticks = np.arange(0,1.01,0.1)
    plt.yticks(yticks)
    plt.legend(loc = "lower right")

    plt.subplot(1, 2, 2)
    ob_line = np.arange(num_min, num_max, dmm / 30)
    plt.plot(ob_line, ob_line, '--', color="k")
    plt.plot(ob_sorted_smooth, fo_sorted_smooth,'r',linewidth = 2)
    plt.xlim(num_min, num_max)
    plt.ylim(num_min, num_max)
    plt.xlabel("观测",fontsize = 14)
    plt.ylabel("预报",fontsize = 14)
    plt.title("频率匹配映射关系图", fontsize=14)



    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)



def box_plot(observed, forecast, save_path=None):
    '''
    box_plot 画一两组数据的箱型图
    ---------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param save_path: 图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    :return:图片，包含箱须图，等级包括,横坐标为"观测"、"预报"，纵坐标为数据值
    '''
    bplot = plt.boxplot((observed, forecast),showfliers =True,patch_artist=True, labels=["观测", "预报"])
    plt.title("频率对比箱须图")
    colors = ["pink", "lightblue"]
    for i, item in enumerate(bplot["boxes"]):
        item.set_facecolor(colors[i])

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
