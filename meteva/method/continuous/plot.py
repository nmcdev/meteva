import matplotlib as mpl
import matplotlib.pyplot as plt
import meteva
import numpy as np
import  math
from sklearn.linear_model import LinearRegression
from  matplotlib import  cm
from matplotlib.ticker import NullFormatter, FixedLocator


def scatter_regress(ob, fo,member_list = None, rtype="linear",vmax = None,vmin = None, ncol = None,save_path=None,show = False,dpi = 300, title="散点回归图",
                    sup_fontsize = 10,width = None,height = None):
    '''
    绘制观测-预报散点图和线性回归曲线
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param save_path:图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    :return:图片，包含散点图和线性回归图,横坐标为观测值，纵坐标为预报值，横坐标很纵轴标取值范围自动设为一致，在图形中间添加了完美预报的参考线。
    '''

    num_max = max(np.max(ob), np.max(fo))
    num_min = min(np.min(ob), np.min(fo))
    dmm = num_max - num_min
    if (num_min < 0):
        num_min -= 0.1 * dmm
    else:
        num_min -= 0.1 * dmm
        if num_min < 0:  # 如果开始全大于，则最低值扩展不超过0
            num_min = 0
    num_max += dmm * 0.1
    if vmax is not None:
        num_max = vmax
    if vmin is not None:
        num_min = vmin
    dmm = num_max - num_min


    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    sub_plot_num = new_Fo_shape[0]

    if ncol is None:
        if sub_plot_num ==1:
            ncols = 1
        elif sub_plot_num %2 == 0:
            ncols = 2
        else:
            ncols = 3
    else:
        ncols = ncol

    nrows = math.ceil(new_Fo_shape[0] / ncols)

    if height is None:
        if nrows==1:
            if ncols <3:
                height_fig = 3.5
            else:
                height_fig = 2.5
        else:
            if ncols > nrows:
                height_fig = 6
            else:
                height_fig = 7
    else:
        height_fig = height

    height_suptitle = 0.4
    height_xticks_title = 0.1
    height_hspace = 0.6
    heidht_axis = (height_fig - height_suptitle - height_xticks_title - height_hspace * (nrows - 1)) / nrows
    width_axis = heidht_axis
    width_yticks = 0.1
    width_wspace = width_yticks * 5
    if width is None:
        width_fig = width_axis * ncols + width_wspace * (ncols - 1) + width_yticks
    else:
        width_fig = width


    fig = plt.figure(figsize=(width_fig,height_fig),dpi = dpi)
    for line in range(new_Fo_shape[0]):
        ob = ob.flatten()
        fo = new_Fo[line,:].flatten()
        markersize = 5 * width_axis * heidht_axis / np.sqrt(ob.size)
        if markersize < 1:
            markersize = 1
        elif markersize > 20:
            markersize = 20

        plt.subplot(nrows, ncols, line + 1)
        plt.plot(fo, ob, '.', color='b', markersize=markersize)
        plt.subplots_adjust(left=0, bottom=0.0, right=1.0, top = 1 - height_suptitle/height_fig,
                            hspace=height_hspace/heidht_axis,wspace=width_wspace/width_axis)
        if rtype == "rate":
            ob_line = np.arange(num_min, num_max, dmm / 30)
            rate = np.mean(ob) / np.mean(fo)
            fo_rg = ob_line * np.mean(ob) / np.mean(fo)
            plt.plot(ob_line, fo_rg, color="k")
            rg_text2 = "Y = " + '%.2f' % rate + "* X"
            plt.text(num_min + 0.05 * dmm, num_min + 0.90 * dmm, rg_text2, fontsize=0.8 * sup_fontsize, color="r")
        elif rtype == "linear":
            X = np.zeros((len(fo), 1))
            X[:, 0] = fo
            clf = LinearRegression().fit(X, ob)
            ob_line = np.arange(num_min, num_max, dmm / 30)
            X = np.zeros((len(ob_line), 1))
            X[:, 0] = ob_line
            fo_rg = clf.predict(X)
            plt.plot(ob_line, fo_rg, color="k")
            rg_text2 = "Y = " + '%.2f' % (clf.coef_[0]) + "* X + " + '%.2f' % (clf.intercept_)
            plt.text(num_min + 0.05 * dmm, num_min + 0.90 * dmm, rg_text2, fontsize=0.8 * sup_fontsize, color="r")

        plt.plot(ob_line, ob_line, '--', color="k",linewidth = 0.5)
        plt.xlim(num_min, num_max)
        plt.ylim(num_min, num_max)
        plt.xticks(fontsize = 0.8 * sup_fontsize)
        plt.yticks(fontsize = 0.8 * sup_fontsize)


        if member_list is None:
            #plt.title('预报'+str(line+1),fontsize = 0.9 * fontsize_sup)
            plt.xlabel('预报'+str(line+1), fontsize=0.9 * sup_fontsize)
        else:
            #plt.title(member_list[line],fontsize = 0.9 * fontsize_sup)
            plt.xlabel(member_list[line], fontsize=0.9 * sup_fontsize)
        #plt.xlabel("预报", fontsize=0.9 * fontsize_sup)

        plt.ylabel("观测", fontsize=0.9 * sup_fontsize)
        plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
        plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内
        #plt.grid(linestyle='--', linewidth=0.5)
    titlelines = title.split("\n")
    fig.suptitle(title, fontsize=sup_fontsize, y=0.99+0.01 * len(titlelines))

    if save_path is None:
        show = True
    else:
        meteva.base.tool.path_tools.creat_path(save_path)
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()
    return None




def pdf_plot(ob, fo,member_list = None,vmax = None,vmin = None, save_path=None,  show = False,dpi = 300,title="频率匹配检验图",
             sup_fontsize = 10,width = None,height = None,yscale = None):
    '''
    sorted_ob_fo 将传入的两组数据先进行排序
    然后画出折线图
    ----------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param save_path: 图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    :return:图片，包含频率匹配映射关系图,横坐标为观测值，纵坐标为预报值，横坐标很纵轴标取值范围自动设为一致，在图形中间添加了完美预报的参考线。
    '''
    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    if width is None:
        width = 8
    if height is None:
        height = width * 0.45

    fig = plt.figure(figsize=(width, height),dpi = dpi)
    num_max = max(np.max(ob), np.max(fo))
    num_min = min(np.min(ob), np.min(fo))
    dmm = num_max - num_min
    if (num_min != 0):
        num_min -= 0.1 * dmm
    num_max += dmm * 0.1
    if vmax is not None:
        num_max = vmax
    if vmin is not None:
        num_min = vmin
    dmm = num_max - num_min
    ob= ob.flatten()

    ob_sorted = np.sort(ob.flatten())

    ob_sorted_smooth = ob_sorted
    ob_sorted_smooth[1:-1] = 0.5 * ob_sorted[1:-1] + 0.25 * (ob_sorted[0:-2] + ob_sorted[2:])
    ax = plt.subplot(1, 2, 1)
    y = np.arange(len(ob_sorted_smooth)) / (len(ob_sorted_smooth))
    plt.plot(ob_sorted_smooth, y, label="观测")

    dss = ob_sorted_smooth - ob_sorted_smooth[0]
    fnq =[(dss != 0).argmax()]

    for line in range(new_Fo_shape[0]):
        if member_list is None:
            if new_Fo_shape[0] == 1:
                label = '预报'
            else:
                label = '预报' + str(line + 1)
        else:
            label = member_list[line]
        fo_sorted = np.sort(new_Fo[line, :].flatten())
        fo_sorted_smooth = fo_sorted
        fo_sorted_smooth[1:-1] = 0.5 * fo_sorted[1:-1] + 0.25 * (fo_sorted[0:-2] + fo_sorted[2:])
        plt.plot(fo_sorted_smooth, y, label=label)
        plt.xlabel("变量值", fontsize=0.9 * sup_fontsize)
        #plt.xlim(num_min, num_max)

        plt.ylabel("累积概率", fontsize=0.9 * sup_fontsize)
        plt.title("概率分布函数对比图", fontsize=0.9 * sup_fontsize)
        yticks = np.arange(0, 1.01, 0.1)
        plt.yticks(yticks, fontsize=0.8 * sup_fontsize)
        plt.xticks(fontsize=0.8 * sup_fontsize)
        plt.legend(loc="lower right")
        if yscale =="log":
            ax.set_yscale('log')
            major_locator = [0.00001,0.0001,0.001,0.01,0.1,0.5]
            ax.yaxis.set_minor_formatter(NullFormatter())
            ax.yaxis.set_major_locator(FixedLocator(major_locator))
            ax.set_yticklabels(major_locator)
        elif yscale == "logit":
            major_locator=[0.1,0.5,0.9,0.99,0.999,0.9999,0.99999]
            ax.set_yscale('logit')
            ax.yaxis.set_minor_formatter(NullFormatter())
            ax.yaxis.set_major_locator(FixedLocator(major_locator))
            ax.set_yticklabels(major_locator)
            dss = fo_sorted_smooth - fo_sorted_smooth[0]
            fnq.append((dss!=0).argmax())

        else:
            plt.ylim(0, 1)

    if yscale == "logit":
        minfnq = min(fnq)/ob_sorted_smooth.size
        plt.ylim(minfnq,1)


        #plt.yscale('logit')


    plt.subplot(1, 2, 2)
    ob_line = np.arange(num_min, num_max, dmm / 30)
    plt.plot(ob_line, ob_line, '--')
    for line in range(new_Fo_shape[0]):
        if member_list is None:
            if new_Fo_shape[0] == 1:
                label = '预报'
            else:
                label = '预报' + str(line + 1)
        else:
            label = member_list[line]
        fo_sorted = np.sort(new_Fo[line, :].flatten())
        fo_sorted_smooth = fo_sorted
        fo_sorted_smooth[1:-1] = 0.5 * fo_sorted[1:-1] + 0.25 * (fo_sorted[0:-2] + fo_sorted[2:])
        plt.plot(fo_sorted_smooth, ob_sorted_smooth, linewidth=2, label=label)
        plt.xlim(num_min, num_max)
        plt.ylim(num_min, num_max)
        plt.xlabel("预报", fontsize=0.9 * sup_fontsize)
        plt.ylabel("观测", fontsize=0.9 * sup_fontsize)
        plt.title("频率匹配映射关系图", fontsize=0.9 * sup_fontsize)
        plt.legend(loc="lower right", fontsize=0.9 * sup_fontsize)
        plt.yticks(fontsize=0.8 * sup_fontsize)
        plt.xticks(fontsize=0.8 * sup_fontsize)
    if title is not None:
        plt.suptitle(title + "\n", y=1.00, fontsize=sup_fontsize)

    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()


def box_plot_continue(ob, fo,  member_list=None,vmax = None,vmin = None, save_path=None, show = False,dpi = 300,title="频率对比箱须图",
                      sup_fontsize = 10,width = None,height = None,):
    '''
    box_plot 画一两组数据的箱型图
    ---------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param save_path: 图片保存路径，缺省时不输出图片，而是以默认绘图窗口形式展示
    :return:图片，包含箱须图，等级包括,横坐标为"观测"、"预报"，纵坐标为数据值
    '''
    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])

    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    list_fo = list(new_Fo)

    xticks = ['观测']
    if member_list is None:
        if new_Fo_shape[0] == 1:
            xticks.append('预报')
        else:
            for i in range(new_Fo_shape[0]):
                xticks.append('预报' + str(i + 1))
    else:
        xticks.extend(member_list)

    #print(width)
    new_list_fo = []
    for fo_piece in list_fo:
        new_list_fo.append(fo_piece.flatten())
    ob = ob.flatten()
    new_list_fo.append(ob)
    tuple_of_ob = tuple(new_list_fo)

    if width is None:
        width = meteva.base.plot_tools.caculate_axis_width(xticks, sup_fontsize) +0.5
        if width >10:
            for i in range(len(xticks)):
                if i % 2 ==1:
                    xticks[i] ="|\n" + xticks[i]
            width = 10
        elif width < 5:
            width = 5

    if height is None:
        height = width/2

    fig = plt.figure(figsize=(width, height), dpi=dpi)

    markersize = 5 * width * height / np.sqrt(ob.size)
    if markersize < 1:
        markersize = 1
    elif markersize > 20:
        markersize = 20
    colors_list= []
    colors = cm.get_cmap('rainbow', 128)
    for i in range(len(xticks)):
        color_grade = i / len(xticks)

        colors_list.append(colors(color_grade))

    bplot = plt.boxplot(tuple_of_ob, showfliers=True, patch_artist=True, labels=xticks)

    plt.xticks(fontsize = 0.9 * sup_fontsize)
    plt.yticks(fontsize = 0.9 * sup_fontsize)

    plt.title(title,fontsize = sup_fontsize)
    for i, item in enumerate(bplot["boxes"]):
        item.set_facecolor(colors_list[i])
    #plt.title(title, fontsize=sup_fontsize)

    if vmin is not None or vmax is not None:
        if vmin is not None:
            if vmax is None:
                vmax = max(np.max(ob), np.max(fo))
                dmax = vmax - vmin
                plt.ylim(vmin,vmax+ dmax * 0.05)
            else:
                plt.ylim(vmin, vmax)
        else:
            vmin =  min(np.min(ob), np.min(fo))
            dmax = vmax - vmin
            plt.ylim(vmin- dmax * 0.05,vmax)


    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()




def taylor_diagram(ob, fo,member_list=None, save_path=None,show = False,dpi = 300, title="",
                sup_fontsize =10,width = None,height = None):
    '''

    :param ob:
    :param fo:
    :param grade_list:
    :return:
    '''

    leftw = 0.3
    rightw = 1.5
    uphight = 1.2
    lowhight = 1.2
    axis_size_x = 3
    axis_size_y = 3
    if width is None:
        width = axis_size_x + leftw + rightw

    if height is None:
        height = axis_size_y + uphight + lowhight

    stds = meteva.method.ob_fo_std(ob,fo)
    corrs = meteva.method.corr(ob,fo)
    corrs1 = [1]
    if isinstance(corrs,float):
        corrs1.append(corrs)
    else:
        for i in range(len(corrs)):
            corrs1.append(corrs[i])


    fig = plt.figure(figsize=(width, height),dpi=dpi)
    ax1 = fig.add_axes([leftw / width, lowhight / width, axis_size_x / width, axis_size_y / height])


    max_stds = max(stds)

    dif = (max_stds) / 10.0
    if dif == 0:
        inte = 1
    else:
        inte = math.pow(10, math.floor(math.log10(dif)))
    # 用基本间隔，将最大最小值除于间隔后小数点部分去除，最后把间隔也整数化
    r = dif / inte
    if r < 3 and r >= 1.5:
        inte = inte * 2
    elif r < 4.5 and r >= 3:
        inte = inte * 4
    elif r < 5.5 and r >= 4.5:
        inte = inte * 5
    elif r < 7 and r >= 5.5:
        inte = inte * 6
    elif r >= 7:
        inte = inte * 8
    vmax = inte * ((int)(max_stds / inte) + 1)



    std_list = np.arange(inte,vmax+inte/2,inte)
    corr_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9,0.98]


    #画观测弧线
    # 画弧线
    angle = np.arange(0,math.pi/2,math.pi/1000)
    std = stds[0]
    x2 = np.cos(angle) * std
    y2 = np.sin(angle) * std
    plt.plot(x2, y2,color = "steelblue",linewidth = 1)
    for i in range(len(std_list)):
        std = std_list[i]
        x2 = np.cos(angle) * std
        y2 = np.sin(angle) * std
        if i <len(std_list)-1:
            plt.plot(x2, y2, ":", color="k", linewidth=0.5)
        else:
            plt.plot(x2, y2,color = "k",linewidth = 0.5)



    #画围绕观测的弧线
    angle = np.arange(0,math.pi,math.pi/1000)
    for i in range(len(std_list)):
        std = std_list[i]
        x2 = np.cos(angle) * std + stds[0]
        y2 = np.sin(angle) * std
        dis = np.sqrt(x2 * x2 + y2 * y2)
        x2 = x2[dis < vmax]
        y2 = y2[dis < vmax]

        plt.plot(x2, y2, ":", color="g", linewidth=0.5)

    #相关系数射线
    r0 = np.arange(0,vmax,inte/100)
    for i in range(len(corr_list)):
        corr = corr_list[i]
        angle = np.arccos(corr)
        x1 = r0 * np.cos(angle)
        y1 = r0 * np.sin(angle)
        ax1.plot(x1, y1, '-.', color='b', linewidth=0.4)
        rt = vmax* 1.01
        xt = rt * np.cos(angle)
        yt = rt * np.sin(angle)
        ax1.text(xt, yt, str(corr),fontsize = sup_fontsize * 0.8)


    angle = 60 * math.pi/180
    rt = vmax * 1.01
    xt = rt * np.cos(angle)
    yt = rt * np.sin(angle)

    ax1.text(xt, yt,"相关系数" , fontsize=sup_fontsize * 0.8,rotation=-30,)

    ax1.set_xticks(std_list)
    ax1.set_yticks(std_list)
    ax1.set_xlim(0,vmax)
    ax1.set_ylim(0, vmax)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    ax1.set_xlabel("标准差")
    ax1.set_ylabel("标准差")



    # 画预报观测点
    labels = ["观测"]
    labels.extend(member_list)
    for i in range(len(stds)):
        corr = corrs1[i]
        angle = np.arccos(corr)
        xp = stds[i] * np.cos(angle)
        yp = stds[i] * np.sin(angle)
        ax1.plot(xp, yp,"o", label=labels[i], markersize=6)
    lines, label1 = ax1.get_legend_handles_labels()

    if len(stds)> 7:
        legend2 = ax1.legend(lines, label1, loc="upper right",
                         bbox_to_anchor=(1.4, 1.05), ncol=1, fontsize=sup_fontsize * 0.9)
    elif len(stds)>5:
        legend2 = ax1.legend(lines, label1, loc="upper right",
                         bbox_to_anchor=(1.2, 1.05), ncol=1, fontsize=sup_fontsize * 0.9)
    else:
        legend2 = ax1.legend(lines, label1, loc="upper right",
                         bbox_to_anchor=(1.1, 1.05), ncol=1, fontsize=sup_fontsize * 0.9)
    ax1.add_artist(legend2)


    title = title + "\n"
    ax1.set_title(title,fontsize = sup_fontsize)
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()






