import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import numpy as np
import copy


def box_plot_ensemble(ob, fo,member_list = None, save_path=None,title ="频率对比箱须图"):
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
    if width < 6:
        width = 6
    data = np.zeros((len(ob),en_num+1))
    data[:,0] = ob[:]
    data[:,1:] = fo[:,:]

    fig = plt.figure(figsize=(width,6))
    #plt.boxplot((observed, forecast), labels=["观测","预报" ])

    if member_list is None:
        labels = ["ob\n观测"]
        for i in range(en_num):
            if i == int(en_num/2):
                labels.append(str(i+1)+"\n预报")
            else:
                labels.append(str(i+1))
    else:
        labels = ["观测"]
        labels.extend(member_list)

    bplot = plt.boxplot((data),showfliers =True,patch_artist=True,labels=labels)
    for i, item in enumerate(bplot["boxes"]):
        if i == 0:
            item.set_facecolor("pink")
        else:
            item.set_facecolor("lightblue")
    plt.axvline(0.5,color = "b")
    plt.subplots_adjust(left=0.5/width,right=1-0.1/width)
    plt.title(title,fontsize = 14)

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        print("检验结果已以图片形式保存至" + save_path)
    plt.close()


def rank_histogram(ob,fo,save_path= None,title = "排序柱状图"):
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
    plt.ylabel("比例",fontsize = 14)
    plt.xlabel("观测值在集合序列中的排序号",fontsize = 14)
    plt.title(title,fontsize = 14)
    plt.ylim(0,ymax)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        print("检验结果已以图片形式保存至" + save_path)
    plt.close()


def mse_variance(ob,fo):
    '''
    :param ob:实况数据 一维的numpy
    :param fo:预测数据 二维的numpy数组
    :return:
    '''
    mean_fo = np.mean(fo,axis=0)
    pass



