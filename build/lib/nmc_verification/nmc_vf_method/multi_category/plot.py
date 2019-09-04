import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def frequency_histogram(ob, fo, clevs, x_lable='frequency', save_path=None,
                        y_lable='range', left_label='Obs', right_label='Pred',
                        left_color='r', right_color='b', legend_location="upper right", width=0.2):
    '''
    frequency_histogram 对比测试数据和实况数据的发生的频率
    :param ob:一个实况数据  类型  numpy
    :param fo: 预测数据 一维的numpy
    :param clevs: 等级 一个列表
    :param x_lable: 横坐标的名字
    :param save_path: 保存地址
    :param y_lable: 纵坐标的名字
    :param left_label: 左标注名字
    :param right_label: 右标注名字
    :param left_color: 左柱状图的颜色
    :param right_color: 右柱状图颜色
    :param legend_location: 标注所处的地点
    :param width: 宽度
    :return:
    '''
    p_ob = []
    p_fo = []

    xticklabels = []

    for i in range(0, len(clevs) - 1):
        index0 = np.where((ob >= clevs[i]) & (ob < clevs[i + 1]))
        xticklabels.append(str(clevs[i]) + '-' + str(clevs[i + 1]))
        p_ob.append(len(index0[0]) / len(ob))
        index0 = np.where((fo >= clevs[i]) & (fo < clevs[i + 1]))
        p_fo.append(len(index0[0]) / len(fo))
    index0 = np.where(ob >= clevs[-1])
    p_ob.append(len(index0[0]) / len(ob))
    index0 = np.where(fo >= clevs[-1])
    p_fo.append(len(index0[0]) / len(fo))
    xticklabels.append('>=' + str(clevs[-1]))
    x = np.arange(0, len(p_ob))
    ax3 = plt.axes()

    ax3.bar(x + 0.1, p_ob, width=width, facecolor=left_color, label=left_label)
    ax3.bar(x - 0.1, p_fo, width=width, facecolor=right_color, label=right_label)
    ax3.legend(loc=legend_location)
    ax3.set_xlabel(x_lable, fontsize=10)
    ax3.set_xticks(x)
    ax3.set_xticklabels(xticklabels, fontsize=9)
    ax3.set_ylabel(y_lable, fontsize=10)
    ax3.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)



