import numpy as np
import matplotlib.pyplot as plt
import datetime
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签\
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import seaborn as sns
import math

import meteva
import pandas as pd


def error_boxplot(sta_ob_and_fos0,s = None, g = None, gll=None,
                  group_name_list=None,threshold = 2,save_dir=None,save_path = None,show = False,dpi = 200,title="误差综合分析图",
                  vmin  = None,vmax = None,spasify_xticks = None,sup_fontsize =10,width = None,height = None):
    '''

    :param sta_ob_and_fos0:
    :param s:
    :param g:
    :param gll:
    :param save_dir:
    :param group_name_list:
    :param threshold:
    :param show:
    :param title:
    :return:
    '''
    if s is not None:
        if g is not None:
            if g == "last_range" or g == "last_step":
                s["drop_last"] = False
            else:
                s["drop_last"] = True



    sta_ob_and_fos = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    if(len(sta_ob_and_fos.index) == 0):
        print("there is no data to verify")
        return
    sta_ob_and_fos_list, gll1 = meteva.base.fun.group(sta_ob_and_fos, g, gll)
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos_list[0])
    if(len(data_names) ==1):
        print("error infomation: only one data column, can't caculate error")
        return

    if isinstance(title, list):
        if len(data_names) -1 != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if len(data_names) -1 != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return

    if group_name_list is None:
        group_name_list = meteva.product.program.get_group_name(gll1)

    for v in range(len(data_names)-1):
        combineData = []
        boxgroup = []
        right_rate = []
        tcount = []
        me_list = []
        mae_list = []
        rmse_list = []
        max_list = []
        min_list = []
        if gll1 is None:
            gll1 = [[0]]
        for i in range(len(gll1)):
            dat = sta_ob_and_fos_list[i].values[:, 7+v] - sta_ob_and_fos_list[i].values[:, 6]
            if vmax is None:
                max_list.append(np.max(dat))
            if vmin is None:
                min_list.append(np.min(dat))
            me_list.append(np.mean(dat))
            mae_list.append(np.mean(np.abs(dat)))
            rmse_list.append(np.sqrt(np.mean(np.power(dat,2))))
            tt = len(dat)
            index = np.where((dat <= threshold) & (dat >= -threshold))
            rcount = len(index[0])
            right_rate.append(rcount / tt)
            tcount.append(tt)
            combineData.append(dat)
            bg = np.ones(tt) * i
            boxgroup.append(bg)
        right_rate = np.array(right_rate)
        tcount = np.array(tcount)


        if vmin is None:
            vmin1 = np.min(np.array(min_list))
        else:
            vmin1 = vmin
        if vmax is None:
            vmax1 = np.max(np.array(max_list))
        else:
            vmax1 = vmax
        dmax = vmax1 - vmin1
        if vmin is None:
            if vmin1 < 0:
                vmin1 = vmin1 - 0.1 * dmax
        if vmax is None:
            vmax1 = vmax1 + 0.2 * dmax



        # 计算最大的横坐标字符串
        #max_str_len = 5
        #for k in range(1, len(group_name_list)):
        #    index = group_name_list[k]
        #    if not type(index) == str:
        #        index = str(index)
        #    indexs = index.split("\n")
        #    for i in range(len(indexs)):
        #        str1 = indexs[i]
        #        if max_str_len < len(str1):
        #            max_str_len = len(str1)

        width_axis_labels = meteva.base.plot_tools.caculate_axis_width(group_name_list, sup_fontsize, 1)
        width_wspace = 2
        width_one_subplot = width_axis_labels + width_wspace
        if width_one_subplot < 2: width_one_subplot = 2
        if width is None:
            width = max(4,min(width_one_subplot,8))

        spasify = 1
        if width_one_subplot > width:
            spasify = int(math.ceil(width_axis_labels / (width - width_wspace)))
        if spasify_xticks is not None:
            xticks_font = sup_fontsize * 0.8 * spasify_xticks * (width - width_wspace) / (width_axis_labels)
            spasify = spasify_xticks
        else:
            xticks_font = sup_fontsize * 0.8

        x = np.arange(1, len(tcount) + 1)
        xticks = x[::spasify]
        xticks_labels = group_name_list[::spasify]

        #if width is None:
        #    width = 0.5 + (1 + max_str_len) * 0.06 * len(group_name_list)
        #    if width < 4:width = 4
        #    if width >8:width = 8

        if height is None:
            height = 4

        fig = plt.figure(figsize=(width, height),dpi = dpi)

        grid_plt = plt.GridSpec(6, 1, hspace=0)

        ax1 = plt.subplot(grid_plt[0:5, 0])
        bplot = ax1.boxplot(combineData, boxgroup, showfliers=True, patch_artist=True, sym='.')
        for i, item in enumerate(bplot["boxes"]):
            item.set_facecolor("lightblue")
        plt.subplots_adjust(left=0.5 / width, right=1 - 0.1 / width)
        plt.ylabel("误差值", fontsize=sup_fontsize *0.9)
        plt.yticks(fontsize = sup_fontsize * 0.8)
        plt.plot(x,me_list,'g',label = '平均误差',zorder = 3)
        plt.plot(x, mae_list, 'b', label='平均绝对误差',zorder = 3)
        plt.plot(x, rmse_list, 'r', label='均方根误差',zorder = 3)
        plt.hlines(0, 1, len(group_name_list), linewidth=1, color="k", linestyles="dashed")
        plt.hlines(threshold, 1, len(group_name_list), linewidth=1, color="k", linestyles="dashed")
        plt.hlines(-threshold, 1, len(group_name_list), linewidth=1, color="k", linestyles="dashed")
        plt.ylim(vmin1,vmax1)
        plt.legend(fontsize =sup_fontsize * 0.8,ncol = 3,loc = "upper center")


        if isinstance(title,list):
            title1 = title[v]
        else:
            title1 = meteva.product.program.get_title_from_dict(title, s, None, None,
                                                                data_names[v + 1])

        plt.title(title1, fontsize=14)

        ax2 = plt.subplot(grid_plt[5, 0])

        plt.bar(x, tcount,width=0.5,label = "样本数")
        plt.legend(fontsize=sup_fontsize * 0.5, loc="upper left")
        xlabel_1 = meteva.product.program.get_x_label(g)

        plt.xlabel(xlabel_1, fontsize=sup_fontsize *0.9)
        plt.xlim(0.5, len(tcount) + 0.5)
        plt.ylim(0, np.max(tcount) * 1.5)


        plt.xticks(xticks, xticks_labels,fontsize = xticks_font)
        plt.yticks(fontsize=sup_fontsize *0.8)
        plt.ylabel("样本数", fontsize=sup_fontsize * 0.9)
        ax2 = ax2.twinx()
        plt.plot(x, right_rate*100, "r", linewidth=2,label = "准确率")
        plt.legend(fontsize=sup_fontsize * 0.5, loc="upper right")
        plt.ylim(0, 100)
        plt.yticks(fontsize=sup_fontsize *0.8)
        plt.ylabel("准确率(%)", fontsize = sup_fontsize * 0.9)

        save_path1 = None
        if save_path is None:
            if save_dir is None:
                show = True
            else:
                save_path1 = save_dir + "/" + data_names[v + 1] + ".png"
        else:
            save_path1 = save_path[v]
        if save_path1 is not None:
            meteva.base.tool.path_tools.creat_path(save_path1)
            plt.savefig(save_path1,bbox_inches='tight')
            print("图片已保存至" + save_path1)
        if show:
            plt.show()
        plt.close()


def error_boxplot_abs(sta_ob_and_fos0,s = None, g = None, gll=None,
                  group_name_list=None,threshold = 2,save_dir=None,save_path = None,show = False,dpi = 200,title="绝对误差综合分析图",
                    vmin = None, vmax = None, spasify_xticks = None, sup_fontsize = 10, width = None, height = None):

    if s is not None:
        if g is not None:
            if g == "last_range" or g == "last_step":
                s["drop_last"] = False
            else:
                s["drop_last"] = True

    sta_ob_and_fos = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    if(len(sta_ob_and_fos.index) == 0):
        print("there is no data to verify")
        return
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos)
    if(len(data_names) ==1):
        print("error infomation: only one data column, can't caculate error")
        return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if len(data_names) -1 != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return

    if isinstance(title, list):
        if len(data_names) -1 != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return
    sta_ob_and_fos_list, gll1 = meteva.base.fun.group(sta_ob_and_fos, g, gll)
    if group_name_list is None:
        group_name_list = meteva.product.program.get_group_name(gll1)
    if gll1 is None:
        gll1 = [[0]]
    for v in range(len(data_names)-1):
        combineData = []
        boxgroup = []
        right_rate = []
        tcount = []
        maxlist = []

        me_list = []
        mae_list = []
        rmse_list = []
        max_list = []
        for i in range(len(gll1)):
            dat = sta_ob_and_fos_list[i].values[:, 7+v] - sta_ob_and_fos_list[i].values[:, 6]
            me_list.append(np.mean(dat))
            dat = np.abs(dat)
            if vmax is None:
                max_list.append(np.max(dat))
            mae_list.append(np.mean(dat))
            rmse_list.append(np.sqrt(np.mean(dat * dat)))

            maxlist.append(np.max(dat))
            tt = len(dat)
            index = np.where(dat <= threshold)
            rcount = len(index[0])
            right_rate.append(rcount / tt)
            tcount.append(tt)
            combineData.append(dat)
            bg = np.ones(tt) * i
            boxgroup.append(bg)
        right_rate = np.array(right_rate)
        tcount = np.array(tcount)
        maxarray = np.array(maxlist)
        maxerror = np.max(maxarray)


        if vmin is None:
            vmin1 = np.min(np.array(me_list))
        else:
            vmin1 = vmin
        if vmax is None:
            vmax1 = np.max(np.array(max_list))
        else:
            vmax1 = vmax
        dmax = vmax1 - vmin1
        if vmin is None:
            if vmin1 < 0:
                vmin1 = vmin1 - 0.1 * dmax
        if vmax is None:
            vmax1 = vmax1 + 0.2 * dmax

        # 计算最大的横坐标字符串
        width_axis_labels = meteva.base.plot_tools.caculate_axis_width(group_name_list, sup_fontsize, 1)
        width_wspace = 2
        width_one_subplot = width_axis_labels + width_wspace
        if width_one_subplot < 2: width_one_subplot = 2
        if width is None:
            width = max(4,min(width_one_subplot,8))

        spasify = 1
        if width_one_subplot > width:
            spasify = int(math.ceil(width_axis_labels / (width - width_wspace)))
        if spasify_xticks is not None:
            xticks_font = sup_fontsize * 0.8 * spasify_xticks / spasify
            spasify = spasify_xticks
        else:
            xticks_font = sup_fontsize * 0.8


        x = np.arange(1, len(tcount) + 1)
        xticks = x[::spasify]
        xticks_labels = group_name_list[::spasify]
        if height is None:
            height = 4

        fig = plt.figure(figsize=(width, height),dpi = dpi)
        grid_plt = plt.GridSpec(5, 1, hspace=0)
        x = np.arange(1, len(tcount) + 1)
        ax1 = plt.subplot(grid_plt[0:4, 0])
        bplot = ax1.boxplot(combineData, boxgroup, showfliers=True, patch_artist=True, sym='.')
        for i, item in enumerate(bplot["boxes"]):
            item.set_facecolor("lightblue")
        plt.subplots_adjust(left=0.5 / width, right=1 - 0.1 / width)
        plt.ylabel("误差绝对值", fontsize=sup_fontsize *0.9)
        plt.yticks(fontsize=sup_fontsize * 0.8)
        plt.ylim(vmin1,vmax1)
        plt.plot(x,me_list,'g',label = '平均误差',zorder = 3)
        plt.plot(x, mae_list, 'b', label='平均绝对误差',zorder = 3)
        plt.plot(x, rmse_list, 'r', label='均方根误差',zorder = 3)
        plt.legend(fontsize=sup_fontsize * 0.8, ncol=3, loc="upper center")

        if isinstance(title,list):
            title1 = title[v]
        else:
            title1 = meteva.product.program.get_title_from_dict(title, s, None, None,
                                                                data_names[v + 1])


        plt.title(title1, fontsize=sup_fontsize)

        plt.hlines(threshold, 1, len(group_name_list), linewidth=1, color="k", linestyles="dashed")
        plt.hlines(0, 1, len(group_name_list), linewidth=1, color="k", linestyles="dashed")
        ax2 = plt.subplot(grid_plt[4, 0])
        plt.bar(x, tcount,width=0.5,label = "样本数")
        plt.legend(fontsize=sup_fontsize * 0.5, loc="upper left")
        xlabel_1 = meteva.product.program.get_x_label(g)
        plt.xlabel(xlabel_1, fontsize=sup_fontsize *0.9)
        plt.xlim(0.5, len(tcount) + 0.5)
        plt.ylim(0, np.max(tcount) * 1.5)
        plt.xticks(xticks, xticks_labels,fontsize = xticks_font)
        plt.yticks(fontsize=sup_fontsize * 0.8)
        plt.ylabel("样本数", fontsize=sup_fontsize * 0.9)
        ax3 = ax2.twinx()
        plt.plot(x, right_rate*100, "r", linewidth=2,label = "准确率")
        plt.legend(fontsize=sup_fontsize * 0.5, loc="upper right")
        plt.ylim(0, 100)
        plt.yticks(fontsize=sup_fontsize *0.8)
        plt.ylabel("准确率(%)", fontsize=sup_fontsize * 0.9)

        save_path1 = None
        if save_path is None:
            if save_dir is None:
                show = True
            else:
                save_path1 = save_dir + "/" + data_names[v + 1] + ".png"
        else:
            save_path1 = save_path[v]
        if save_path1 is not None:
            meteva.base.tool.path_tools.creat_path(save_path1)
            plt.savefig(save_path1,bbox_inches='tight')
            print("图片已保存至" + save_path1)
        if show:
            plt.show()
        plt.close()

