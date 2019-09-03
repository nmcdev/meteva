import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np

from sklearn.linear_model import LinearRegression


def scatter_regress(ob, fo, save_path=None, scattercolor='r', scattersize=5, x_label='fo', y_label='bo', fontsize=10,
                    line_color='r'):
    # 批量测试降水、温度等要素的绘图结果，获取一组最佳样式
    '''
    scatter_regress 画一张带有回归线的实况和预报数据的散点图，
    :param ob: 实况数据 一维的numpy
    :param fo:预测数据 一维的numpy
    :param save_path: 保存数据的地址
    :param scattercolor:散点颜色
    :param scattersize:散点的大小
    :param x_label: 横坐标的名字
    :param y_label: 纵坐标的名字
    :param fontsize: 横纵坐标的名字字体大小
    :param line_color:回归线的颜色
    :return:
    '''

    plt.plot(ob, fo, 'o', markerfacecolor=scattercolor, markersize=scattersize)

    ob_or_fo = np.hstack((ob, fo))
    num_max = ob_or_fo.max()
    num_min = ob_or_fo.min()
    X = np.zeros((len(ob), 1))
    X[:, 0] = ob
    clf = LinearRegression().fit(X, fo)
    ob_line = np.arange(0, np.max(ob), np.max(ob) / 30)
    X = np.zeros((len(ob_line), 1))
    X[:, 0] = ob_line
    fo_rg = clf.predict(X)
    plt.plot(ob_line, fo_rg, line_color)
    plt.xlim(num_min - num_min / 5, num_max + num_max / 5)
    plt.xlabel(x_label, size=fontsize)

    plt.ylabel(y_label, size=fontsize)

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)


def sorted_ob_fo(ob, fo, save_path=None):
    '''
    sorted_ob_fo 将传入的两组数据先进行排序
    然后画出折线图
    ----------------
    :param ob: 实况数据 一维的numpy
    :param fo:预测数据 一维的numpy
    :param save_path: 保存图片的路径
    :return:
    '''
    ob_sorted = np.sort(ob)
    fo_sorted = np.sort(fo)
    plt.plot(fo_sorted, ob_sorted)

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)


def box_plot(observed, forecast, save_path=None, x_lable='observation', y_lable='forecast', title='box-plot'):
    '''
    box_plot 画一两组数据的箱型图
    ---------------
    :param observed:实况数据 一维的numpy
    :param forecast:预测数据 一维的numpy
    :param save_path: 保存数据的路径
    :param x_lable: 横坐标的标签
    :param y_lable:纵坐标标签
    :param title: 图片名字
    :return:
    '''
    plt.boxplot((observed, forecast), labels=[x_lable, y_lable])
    plt.title(title)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
