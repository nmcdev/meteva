

import sklearn

from sklearn.metrics import confusion_matrix

import matplotlib as mpl

import matplotlib.pyplot as plt

import numpy as np

from sklearn.linear_model import LinearRegression


def multi_category_contingency_table(ob0, fo0,grade_list = None,save_path = None, figsize=(20, 10), x_label=None, y_label=None,

                                     title='multi category contingency table', text_fontsize=20, title_fontsize=25,

                                     fontproperties='KaiTi', col_labels=None, row_labels=None):
    '''
    multi_category_contingency_table 多分类预测列联表
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :param save_path: 保存地址
    :param figsize:
    :param x_label: x轴标签
    :param y_label: y轴标签
    :param title: 标题
    :param text_fontsize:
    :param title_fontsize: 标题文字大小
    :param fontproperties: 字体
    :param col_labels: 行标签
    :param row_labels: 列标签
    :return:
    '''
    if grade_list is None:
        ob = ob0
        fo = fo0
    else:
        ob = None #
        fo = None # 通过threshold_list给出的等级划分标准，将ob0，fo0 划分成各个等级

    conf_mx = confusion_matrix(ob, fo)
    row_sums = conf_mx.sum(axis=1, keepdims=True)
    conf_mx = np.hstack((conf_mx, row_sums))
    line_sums = conf_mx.sum(axis=0, keepdims=True)
    conf_mx = np.vstack((conf_mx, line_sums))
    labels = []
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, frameon=True, xticks=[], yticks=[])
    if (col_labels == None) or (row_labels == None):
        for i in range(0, len(conf_mx[0, :])):
            labels.append(str(i))
        labels[-1] = 'Total'
    if col_labels == None:
        col_labels = labels
    if row_labels == None:
        row_labels = labels
    lengh = len(row_labels)
    my_table = plt.table(cellText=conf_mx,
                         rowLabels=row_labels, colLabels=col_labels,
                         loc='center')
    my_table.set_fontsize(10)
    my_table.scale(figsize[1] / (lengh), figsize[0] / (lengh))
    plt.text(0.5, 0.9, x_label, fontsize=text_fontsize)
    plt.text(0.5, 0.9, y_label, fontsize=text_fontsize)
    plt.title(title, fontproperties=fontproperties, fontsize=title_fontsize)

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)