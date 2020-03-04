import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np

from sklearn.linear_model import LinearRegression


def scatter_regress(ob, fo,rtype = "linear",save_path=None,title = "散点回归图"):
    '''
    绘制观测-预报散点图和线性回归曲线
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param save_path:图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    :return:图片，包含散点图和线性回归图,横坐标为观测值，纵坐标为预报值，横坐标很纵轴标取值范围自动设为一致，在图形中间添加了完美预报的参考线。
    '''
    width = 6
    height = 6
    fig = plt.figure(figsize=(width, height))
    markersize = 5 * width * height / np.sqrt(ob.size)
    if markersize <1:
        markersize = 1
    elif markersize >20:
        markersize = 20
    plt.plot(fo,ob, '.',color= 'b',  markersize=markersize)
    if rtype == "rate":
        num_max = max(np.max(ob),np.max(fo))
        num_min = min(np.min(ob),np.min(fo))
        dmm = num_max - num_min
        if(num_min < 0):
            num_min -= 0.1 * dmm
        else:
            num_min -= 0.1 * dmm
            if num_min<0:  #如果开始全大于，则最低值扩展不超过0
                num_min = 0
        num_max += dmm * 0.1
        dmm = num_max - num_min
        ob_line = np.arange(num_min, num_max, dmm / 30)
        rate = np.mean(ob)/np.mean(fo)
        fo_rg = ob_line * np.mean(ob)/np.mean(fo)
        plt.plot(ob_line, fo_rg,color = "r")
        plt.plot(ob_line, ob_line,'--', color="k")
        plt.xlim(num_min, num_max)
        plt.ylim(num_min, num_max)
        plt.xlabel("预报",fontsize = 14)
        plt.ylabel("观测",fontsize = 14)
        rg_text2 = "Y = " + '%.2f' % rate + "* X"
        plt.text(num_min + 0.05 * dmm, num_min + 0.90 * dmm, rg_text2, fontsize=15,color ="r")
    elif rtype== "linear":
        X = np.zeros((len(fo), 1))
        X[:, 0] = fo
        clf = LinearRegression().fit(X, ob)
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
        plt.xlabel("预报",fontsize = 14)
        plt.ylabel("观测",fontsize = 14)
        rg_text2 = "Y = " + '%.2f' % (clf.coef_[0]) + "* X + " + '%.2f' % (clf.intercept_)
        plt.text(num_min + 0.05 * dmm, num_min + 0.90 * dmm, rg_text2, fontsize=15,color ="r")
    plt.title(title,fontsize = 14)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        print("检验结果已以图片形式保存至" + save_path)
    plt.close()


def pdf_plot(ob, fo, save_path=None,title = "频率匹配检验"):
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
    plt.title("概率分布函数对比图",fontsize = 12)
    yticks = np.arange(0,1.01,0.1)
    plt.yticks(yticks)
    plt.legend(loc = "lower right")

    plt.subplot(1, 2, 2)
    ob_line = np.arange(num_min, num_max, dmm / 30)
    plt.plot(ob_line, ob_line, '--', color="k")
    plt.plot(fo_sorted_smooth, ob_sorted_smooth,'r',linewidth = 2)
    plt.xlim(num_min, num_max)
    plt.ylim(num_min, num_max)
    plt.xlabel("预报",fontsize = 14)
    plt.ylabel("观测",fontsize = 14)
    plt.title("频率匹配映射关系图", fontsize=12)
    if title is not None:
        plt.suptitle(title+"\n",y = 1.00,fontsize = 14)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        print("检验结果已以图片形式保存至" + save_path)
    plt.close()


def box_plot_continue(ob, fo, save_path=None,title = "频率对比箱须图"):
    '''
    box_plot 画一两组数据的箱型图
    ---------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param save_path: 图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    :return:图片，包含箱须图，等级包括,横坐标为"观测"、"预报"，纵坐标为数据值
    '''
    width = 6
    height = 6
    fig = plt.figure(figsize=(width, height))
    bplot = plt.boxplot((ob, fo),showfliers =True,patch_artist=True, labels=["观测", "预报"])
    plt.title(title)
    colors = ["pink", "lightblue"]
    for i, item in enumerate(bplot["boxes"]):
        item.set_facecolor(colors[i])

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        print("检验结果已以图片形式保存至" + save_path)
    plt.close()