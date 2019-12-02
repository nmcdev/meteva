import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import numpy as np
import copy


def box_plot(ob, fo, save_path=None):
    '''
    box_plot 画一两组数据的箱型图
    ---------------
    :param ob:实况数据 一维的numpy
    :param fo:预测数据 二维的numpy数组
    :param save_path 不为None时输出到图片中
    :return: 无
    '''
    en_num = fo.shape[1]
    width = en_num * 0.22 + 0.3
    data = np.zeros((len(ob),en_num+1))
    data[:,0] = ob[:]
    data[:,1:] = fo[:,:]

    fig = plt.figure(figsize=(width,4))
    #plt.boxplot((observed, forecast), labels=["观测","预报" ])
    labels = ["观测"]
    for i in range(en_num):
        if i == int(en_num/2):
            labels.append(str(i)+"\n预报")
        else:
            labels.append(str(i))
    plt.boxplot((data),labels=labels)
    plt.axvline(0.5,color = "b")
    plt.subplots_adjust(left=0.5/width,right=1-0.1/width)


    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)


def rank_histogram(ob,fo,save_path= None):
    '''
    :param ob:一维numpy数组
    :param fo: 二维numpy数组
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
    ymax = np.max(rank_rate) * 1.5
    plt.bar(x,rank_rate)
    plt.ylabel("比例")
    plt.xlabel("观测值在集合序列中的排序")
    plt.title("Rank Histogram")
    plt.ylim(0,ymax)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
    pass



fo = np.random.rand(100,50)
ob = np.random.rand(100)


pass
#mse_variance(ob,fo)
