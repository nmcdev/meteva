
import matplotlib as mpl
import matplotlib.pyplot as plt

import numpy as np

from sklearn.linear_model import LinearRegression


def scatter_regress(ob, fo, save_path = None,scattercolor='r', scattersize=5, x_label='fo', y_label='bo', fontsize=10, line_color='r'):

    #批量测试降水、温度等要素的绘图结果，获取一组最佳样式

    plt.plot(ob, fo, 'o', markerfacecolor=scattercolor, markersize=scattersize)
    plt.legend(numpoints=3, loc='right')
    if ob.max() > fo.max():
        num_max = ob.max()
    else:
        num_max = fo.max()
    if ob.min() > fo.min():
        num_min = fo.min()
    else:
        num_min = ob.min()
    X = np.zeros((len(ob), 1))
    X[:, 0] = ob
    clf = LinearRegression().fit(X, fo)
    ob_line = np.arange(0, np.max(ob), np.max(ob) / 30)
    X = np.zeros((len(ob_line), 1))
    X[:, 0] = ob_line
    fo_rg = clf.predict(X)
    plt.plot(ob_line, fo_rg, line_color)
    plt.xlim(num_min - num_min / 5, num_max + num_max / 5)
    plt.xlabel(x_label, fontsize=fontsize)
    #plt.xlabel(x_label, fontszie=fontsize)
    plt.ylabel(y_label)

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)

def sorted_ob_fo(ob,fo,save_path = None):
    ob_sorted = np.sort(ob)
    fo_sorted = np.sort(fo)
    plt.plot(fo_sorted,ob_sorted)

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)

def box_plot(observed, forecast, save_path=None, x_lable='observation', y_lable='forecast', title='box-plot'):
    plt.boxplot((observed, forecast), labels=[x_lable, y_lable])
    plt.title(title)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)




