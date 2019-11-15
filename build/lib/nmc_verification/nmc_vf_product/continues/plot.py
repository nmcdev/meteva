import matplotlib.pyplot as plt

import numpy as np

from sklearn.linear_model import LinearRegression

import nmc_verification.nmc_vf_base.function.put_into_sta_data as pisd


def scatter_regress_muti_model(ob, fo_df_list, save_path=None, scattercolor='r', scattersize=5,
                               x_label='bo', y_label='fo', fontsize=10, line_color='r'):
    '''
    scatter_regress_muti_model  多模式下画一张带有回归线的实况和预报数据的散点图
    :param ob:一个实况数据  类型  dataframe
    :param fo_list:多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :param save_path:保存地址
    :param scattercolor:散点颜色
    :param scattersize:散点的大小
    :param x_label: 横坐标的名字
    :param y_label: 纵坐标的名字
    :param fontsize: 横纵坐标的名字字体大小
    :param line_color:回归线的颜色
    '''
    fo_df_list.append(ob)
    meger_df_data = pisd.merge_on_id_and_obTime(fo_df_list)
    ob = meger_df_data.iloc[:, -1].values
    data_len = len(fo_df_list)
    plt.figure(figsize=[6.4 * data_len, 4.8])

    colnums = ['level', 'id', 'time']
    title = ''
    for colnum in colnums:
        the_duplicate_values = meger_df_data[colnum].unique()
        if len(the_duplicate_values) == 1:
            title = title + str(the_duplicate_values[0])
    plt.suptitle(title)
    for index, fo_of_colnum in enumerate(meger_df_data.iloc[:, 7:-1]):
        fo = meger_df_data[fo_of_colnum].values
        plt.subplot(1, data_len, index + 1)
        plt.plot(ob, fo, 'o', markerfacecolor=scattercolor, markersize=scattersize)
        # print(ob)
        # print(fo)
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

        plt.title(fo_of_colnum)

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)


# 需要更改
def box_plot_muti_model(ob, fo_df_list, save_path=None, lables=None):
    '''
    box_plot 画一多模式数据的箱型图
    ---------------
    :param observed:实况数据 df
    :param forecast:预测数据 df列表
    :param save_path: 保存数据的路径
    :param x_lable: 横坐标的标签
    :param y_lable:纵坐标标签
    :param title: 图片名字
    :return:
    '''
    fo_df_list.append(ob)
    meger_df_data = pisd.merge_on_id_and_obTime(fo_df_list)
    title = ''
    colnums = ['level', 'id', 'time']
    for colnum in colnums:
        the_duplicate_values = meger_df_data[colnum].unique()
        if len(the_duplicate_values) == 1:
            title = title + str(the_duplicate_values[0])
    ob = meger_df_data.iloc[:, -1]
    meger_df_data.drop(meger_df_data.columns[-1], axis=1, inplace=True)
    meger_df_data.insert(7, 'ob', ob)
    if lables is None:
        labels = meger_df_data.columns[7:]
    ob_and_fo_data = meger_df_data.iloc[:, 7:]
    ob_and_fo_ndarray_T = ob_and_fo_data.values.T
    ob_and_fo_tuple_T = tuple(ob_and_fo_ndarray_T)
    plt.boxplot(ob_and_fo_tuple_T, labels=labels, whis=(0, 100))
    plt.title(title)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)


# 需要更改
def sorted_ob_fo_muti_model(ob, fo_list, save_path=None, x_label='ob', y_label='fo', fontsize=10, line_color='b'):
    '''
    sorted_ob_fo_muti_model 多模式下先对数据排序，然后在画多个折线图子图
    :param ob:一个实况数据  类型  dataframe
    :param fo_list:多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :param save_path:保存地址
    :param x_label  x轴标签
    :param y_label  y轴标签
    :param fontsize  字体大小
    :param line_color 线的颜色
    :return:
    '''
    fo_list.append(ob)
    meger_df_data = pisd.merge_on_id_and_obTime(fo_list)
    ob = meger_df_data.iloc[:, -1].values

    data_len = len(fo_list)
    plt.figure(figsize=[10 * data_len, 4.8])
    title = ''
    colnums = ['level', 'id', 'time']
    for colnum in colnums:
        the_duplicate_values = meger_df_data[colnum].unique()

        if len(the_duplicate_values) == 1:
            title = title + str(the_duplicate_values[0])
    plt.suptitle(title)
    for index, fo_of_colnum in enumerate(meger_df_data.iloc[:, 7:-1]):
        fo = meger_df_data[fo_of_colnum].values
        plt.subplot(1, data_len, index + 1)
        ob_sorted = np.sort(ob)
        fo_sorted = np.sort(fo)
        plt.plot(fo_sorted, ob_sorted, line_color)
        plt.xlabel(x_label, size=fontsize)

        plt.ylabel(y_label, size=fontsize)

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
