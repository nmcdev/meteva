import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def frequency_histogram(ob, fo, clevs, x_lable='frequency',
                        y_lable='range', left_label='Obs', right_label='Pred',
                        left_color='r', right_color='b', legend_location="upper right", width=0.2):
    '''
    frequency_histogram 对比测试数据和实况数据的发生的频率
    :param ob:
    :param fo:
    :param clevs:
    :param x_lable:
    :param y_lable:
    :param left_label:
    :param right_label:
    :param left_color:
    :param right_color:
    :param legend_location:
    :param width:
    :return:
    '''
    p_ob = []
    p_fo = []
    x = np.arange(6)
    xticklabels = []
    for i in range(0, len(clevs)-1):
        index0 = np.where((ob >= clevs[i]) & (ob < clevs[i+1]))
        xticklabels.append(str(clevs[i]) + '-' + str(clevs[i+1]))
        p_ob.append(len(index0[0]) / len(ob))
        index0 = np.where((fo >=clevs[i]) & (fo < clevs[i+1]))
        p_fo.append(len(index0[0])/ len(fo))
    index0 = np.where(ob >= clevs[-1])
    p_ob.append(len(index0[0]) / len(ob))
    index0 = np.where(fo >= clevs[-1])
    p_fo.append(len(index0[0]) / len(fo))
    xticklabels.append('>=' + str(clevs[-1]))
    ax3 = plt.axes()
    ax3.bar(x + 0.25, p_ob, width=width, facecolor=left_color, label=left_label)
    ax3.bar(x - 0.05, p_fo, width=width, facecolor=right_color, label=right_label)
    ax3.legend(loc=legend_location)
    ax3.set_xlabel(x_lable, fontsize=10)
    ax3.set_xticks(x)
    ax3.set_xticklabels(xticklabels, fontsize=9)
    ax3.set_ylabel(y_lable, fontsize=10)
    ax3.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))
    plt.show()
