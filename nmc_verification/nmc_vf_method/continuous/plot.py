
import matplotlib.pyplot as plt

import numpy as np

from sklearn.linear_model import LinearRegression


def scatter_regress(ob, fo, save_path = None,scattercolor='r', scattersize=5, x_label='fo', y_label='bo', fontsize=10, line_color='r'):

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
    plt.xlabel(x_label, fontszie=fontsize)
    plt.ylabel(y_label)

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)