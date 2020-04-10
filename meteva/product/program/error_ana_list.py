import numpy as np
import matplotlib.pyplot as plt
import datetime
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签\
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import seaborn as sns

import meteva
import pandas as pd


def error_boxplot(sta_ob_and_fos0,s = None, g = None, gll=None,
                  group_name_list=None,threshold = 2,save_dir=None,show = False,title="误差综合分析图"):
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
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos)
    if(len(data_names) ==1):
        print("error infomation: only one data column, can't caculate error")
        return
    sta_ob_and_fos_list, gll1 = meteva.base.fun.group(sta_ob_and_fos, g, gll)
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
        if gll1 is None:
            gll1 = [[0]]
        for i in range(len(gll1)):
            dat = sta_ob_and_fos_list[i].values[:, 7+v] - sta_ob_and_fos_list[i].values[:, 6]
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

        # 计算最大的横坐标字符串
        max_str_len = 5
        for k in range(1, len(group_name_list)):
            index = group_name_list[k]
            if not type(index) == str:
                index = str(index)
            indexs = index.split("\n")
            for i in range(len(indexs)):
                str1 = indexs[i]
                if max_str_len < len(str1):
                    max_str_len = len(str1)
        width = 0.5 + (1 + max_str_len) * 0.06 * len(group_name_list)
        if width < 6:
            width = 6
        height = 8
        fig = plt.figure(figsize=(width, height))

        grid_plt = plt.GridSpec(6, 1, hspace=0)
        x = np.arange(1, len(tcount) + 1)

        ax1 = plt.subplot(grid_plt[0:5, 0])
        bplot = ax1.boxplot(combineData, boxgroup, showfliers=True, patch_artist=True, sym='.')
        for i, item in enumerate(bplot["boxes"]):
            item.set_facecolor("lightblue")
        plt.subplots_adjust(left=0.5 / width, right=1 - 0.1 / width)
        plt.ylabel("误差值", fontsize=14)
        plt.plot(x,me_list,'g',label = '平均误差',zorder = 3)
        plt.plot(x, mae_list, 'b', label='平均绝对误差',zorder = 3)
        plt.plot(x, rmse_list, 'r', label='均方根误差',zorder = 3)
        plt.hlines(0, 1, len(group_name_list), linewidth=1, color="k", linestyles="dashed")
        plt.hlines(threshold, 1, len(group_name_list), linewidth=1, color="k", linestyles="dashed")
        plt.hlines(-threshold, 1, len(group_name_list), linewidth=1, color="k", linestyles="dashed")
        plt.legend()
        title1 = meteva.product.program.get_title_from_dict(meteva.product.error_boxplot, s, None, None,
                                                            data_names[v + 1])
        #if title is None:
        #    title1 = data_names[v+1]+"误差综合分析图"
        #    title1 = meteva.product.program.get_title_from_dict(meteva.product.error_boxplot,s,None,None,data_names[v+1])
        #    print(title1)
        #else:
        #    if len(data_names) ==1:
        #        title1 = title
        #    else:
        #        title1 = data_names[v+1]+title

        plt.title(title1, fontsize=14)

        ax2 = plt.subplot(grid_plt[5, 0])

        plt.bar(x, tcount)
        xlabel_1 = meteva.product.program.get_x_label(g)
        plt.xlabel(xlabel_1, fontsize=14)
        plt.xlim(0.5, len(tcount) + 0.5)
        plt.ylim(0, np.max(tcount) * 1.5)
        plt.xticks(x, group_name_list)
        plt.ylabel("样本数", fontsize=14)
        ax2 = ax2.twinx()
        plt.plot(x, right_rate*100, "r", linewidth=2)
        plt.ylim(0, 100)
        plt.ylabel("准确率(%)", fontsize=14)


        if save_dir is None:
            show = True
        else:
            save_path = save_dir +"/"+ data_names[v+1]
            plt.savefig(save_path)
            print("检验结果已以图片形式保存至" + save_path)
        if show:
            plt.show()
        plt.close()




def error_boxplot_abs(sta_ob_and_fos0,s = None, g = None, gll=None,
                  group_name_list=None,threshold = 2,save_dir=None,show = False,title="误差综合分析图"):

    if s is not None:
        if g is not None:
            if g == "last_range" or g == "last_step":
                s["drop_last"] = False
            else:
                s["drop_last"] = True

    sta_ob_and_fos = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos)
    if(len(data_names) ==1):
        print("error infomation: only one data column, can't caculate error")
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
        for i in range(len(gll1)):
            dat = sta_ob_and_fos_list[i].values[:, 7+v] - sta_ob_and_fos_list[i].values[:, 6]
            me_list.append(np.mean(dat))
            dat = np.abs(dat)
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

        # 计算最大的横坐标字符串
        max_str_len = 5
        for k in range(1, len(group_name_list)):
            index = group_name_list[k]
            if not type(index) == str:
                index = str(index)
            indexs = index.split("\n")
            for i in range(len(indexs)):
                str1 = indexs[i]
                if max_str_len < len(str1):
                    max_str_len = len(str1)
        width = 0.5 + (1 + max_str_len) * 0.06 * len(group_name_list)
        if width < 6:
            width = 6
        height = 8
        fig = plt.figure(figsize=(width, height))

        fig = plt.figure(figsize=(width, height))
        grid_plt = plt.GridSpec(5, 1, hspace=0)
        x = np.arange(1, len(tcount) + 1)
        ax1 = plt.subplot(grid_plt[0:4, 0])
        bplot = ax1.boxplot(combineData, boxgroup, showfliers=True, patch_artist=True, sym='.')
        for i, item in enumerate(bplot["boxes"]):
            item.set_facecolor("lightblue")
        plt.subplots_adjust(left=0.5 / width, right=1 - 0.1 / width)
        plt.ylabel("误差绝对值", fontsize=16)
        plt.ylim(np.min(me_list) *1.1,maxerror *1.1)
        plt.plot(x,me_list,'g',label = '平均误差',zorder = 3)
        plt.plot(x, mae_list, 'b', label='平均绝对误差',zorder = 3)
        plt.plot(x, rmse_list, 'r', label='均方根误差',zorder = 3)
        plt.legend()

        title1 = meteva.product.program.get_title_from_dict(meteva.product.error_boxplot, s, None, None,
                                                            data_names[v + 1])
        #if title is None:
        #    title1 = data_names[v+1]+"误差综合分析图"
        #else:
        #    if len(data_names) ==1:
        #        title1 = title
        #    else:
        #        title1 = data_names[v+1]+title
        plt.title(title1, fontsize=14)

        plt.hlines(threshold, 1, len(group_name_list), linewidth=1, color="k", linestyles="dashed")
        plt.hlines(0, 1, len(group_name_list), linewidth=1, color="k", linestyles="dashed")
        ax2 = plt.subplot(grid_plt[4, 0])
        plt.bar(x, tcount)
        xlabel_1 = meteva.product.program.get_x_label(g)
        plt.xlabel(xlabel_1, fontsize=14)
        plt.xlim(0.5, len(tcount) + 0.5)
        plt.ylim(0, np.max(tcount) * 1.5)
        plt.xticks(x, group_name_list)
        plt.ylabel("样本数", fontsize=14)
        ax3 = ax2.twinx()
        plt.plot(x, right_rate * 100, "r", linewidth=2)
        plt.ylim(0, 100)
        plt.ylabel("准确率(%)", fontsize=14)

        if save_dir is None:
            show = True
        else:
            save_path = save_dir
            plt.savefig(save_path)
            print("检验结果已以图片形式保存至" + save_path)

        if show:
            plt.show()
        plt.close()

