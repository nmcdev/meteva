import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import numpy as np
import copy
import meteva


def box_plot_ensemble(ob, fo,member_list = None, vmax = None,vmin = None,save_path=None,show = False,dpi = 300,title ="频率对比箱须图",
                      sup_fontsize = 10,width = None,height = None):
    '''
    box_plot 画一两组数据的箱型图
    ---------------
    :param ob:实况数据 一维的numpy
    :param fo:预测数据 二维的numpy数组
    :param save_path 不为None时输出到图片中
    :return: 无
    '''
    en_num = fo.shape[0]
    if width is None:
        width = en_num * 0.22 + 0.3
        if width < 4:
            width = 4
        if width >8:
            width = 8
    if height is None:
        height = 0.6 * width
    data = np.zeros((len(ob),en_num+1))
    data[:,0] = ob[:]
    data[:,1:] = fo[:,:].T

    fig = plt.figure(figsize=(width,height),dpi = dpi)
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

    bplot = plt.boxplot((data),showfliers =True,patch_artist=True,labels=labels,sym = '.')
    for i, item in enumerate(bplot["boxes"]):
        if i == 0:
            item.set_facecolor("pink")
        else:
            item.set_facecolor("lightblue")
    plt.axvline(0.5,color = "b")
    plt.subplots_adjust(left=0.5/width,right=1-0.1/width)
    plt.xticks(fontsize = 0.9 * sup_fontsize)
    plt.yticks(fontsize = 0.8 * sup_fontsize)
    plt.title(title,fontsize = sup_fontsize)
    plt.ylabel("value")
    if vmin is not None or vmax is not None:
        if vmin is not None:
            if vmax is None:
                vmax = np.max(data)
                dmax = vmax - vmin
                plt.ylim(vmin,vmax+ dmax * 0.05)
            else:
                plt.ylim(vmin, vmax)
        else:
            vmin = np.min(data)
            dmax = vmax - vmin
            plt.ylim(vmin- dmax * 0.05,vmax)

    if save_path is None:
        show = True
    else:
        meteva.base.creat_path(save_path)
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()


def rank_histogram(ob,fo,vmax = None,save_path= None,show = False,dpi = 300,title = "排序柱状图",
                   sup_fontsize=10, width=None, height=None):
    '''
    :param ob:一维numpy数组
    :param fo: 二维numpy数组
    :param save_path:
    :return:
    '''
    en_num = fo.shape[0]
    sample_num = ob.size
    fo1 = copy.deepcopy(fo)
    fo1.sort(axis = 0)
    index = np.where(ob<fo1[0,:])

    en_num = fo.shape[0]
    if width is None:
        width = en_num * 0.22 + 0.3
        if width < 6:
            width = 6
        if width >10:
            width = 10
    if height is None:
        height = width * 0.4

    fig = plt.figure(figsize=(width,height),dpi = dpi)

    rank_num = [len(index[0])]
    for i in range(en_num-1):
        index = np.where((ob>=fo1[i,:]) & (ob < fo1[i+1,:]))
        rank_num.append(len(index[0]))
    index = np.where(ob>=fo1[-1,:])

    rank_num.append(len(index[0]))
    rank_rate = np.array(rank_num)/sample_num
    x = np.arange(0,en_num+1)

    plt.xticks(x,fontsize = 0.8 * sup_fontsize)
    plt.bar(x,rank_rate)
    plt.ylabel("比例",fontsize = 0.9 * sup_fontsize)
    plt.xlabel("观测值在集合序列中的排序号",fontsize = 0.9 * sup_fontsize)
    plt.title(title,fontsize = sup_fontsize)
    if vmax is None:
        ymax = np.max(rank_rate) * 1.5
    else:
        ymax = vmax
    plt.ylim(0,ymax)
    plt.xlim(-0.5,en_num+0.5)
    if save_path is None:
        show = True
    else:
        meteva.base.creat_path(save_path)
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()


def mse_variance(ob,fo):
    '''
    :param ob:实况数据 一维的numpy
    :param fo:预测数据 二维的numpy数组
    :return:
    '''
    mean_fo = np.mean(fo,axis=0)
    pass



