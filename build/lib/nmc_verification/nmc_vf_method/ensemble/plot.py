import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import numpy as np
import copy


def box_plot(observed, forecast, save_path=None, x_lable='observation', y_lable='forecast', title='box-plot'):
    '''
    box_plot 画一两组数据的箱型图
    ---------------
    :param observed:实况数据 一维的numpy
    :param forecast:预测数据 二

    、维的numpy
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


def rank_histogram(ob,fo,save_path= None):
    '''
    :param ob:
    :param fo:
    :param save_path:
    :return:
    '''
    en_num = fo.shape[1]
    sample_num = ob.size
    fo1 = copy.deepcopy(fo)
    fo1.sort(axis = 1)
    index = np.where(ob<fo1[:,0])
    rank_num = [len(index[0])]
    for i in range(en_num-1):
        index = np.where((ob>=fo1[:,i]) & (ob < fo1[:,i+1]))
        rank_num.append(len(index[0]))
    index = np.where(ob>=fo1[:,-1])
    rank_num.append(len(index[0]))
    rank_rate = np.array(rank_num)/sample_num
    x = np.arange(0,en_num+1)
    plt.bar(x,rank_rate)
    plt.ylabel("比例")
    plt.xlabel("观测值在集合序列中的排序")
    plt.title("Rank Histogram")
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
    pass


def mse_variance(ob,fo,save_path = None):
    '''
    :param ob:
    :param fo:
    :param save_path:
    :return:
    '''
    mean_fo = np.mean(fo,axis=1)
    mse = np.square(ob- mean_fo)
    var = np.var(fo,axis=1)

    plt.plot(mse,var,'.')
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
    pass

'''
fo = np.random.rand(10000,2)
ob = np.random.rand(10000)

#rank_histogram(ob,fo)
mse_variance(ob,fo)
'''