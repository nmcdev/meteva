
import  copy
import math
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import numpy as np
import nmc_verification

#参数数组转换为列表
def para_array_to_list(key_num,para_array):
    key_list = []
    for key in para_array.keys():
        key_list.append(key)
    key_count = len(key_list)

    if(key_num ==key_count-1):
        key = key_list[key_num]
        para_list = []
        list1 = para_array[key]
        for para in list1:
            dict1 = {}
            dict1[key] = para
            para_list.append(dict1)
    else:
        key = key_list[key_num]
        list1 = para_array[key]
        para_list0 = para_array_to_list(key_num+1,para_array)
        para_list = []
        for para in list1:
            for dict0 in para_list0:
                dict1 = {}
                dict1[key] = para
                for key0 in dict0.keys():
                    dict1[key0] = copy.deepcopy(dict0[key0])
                #print(dict1)
                para_list.append(dict1)
    return para_list

#自动布局模块
def layout(subplot_num,legend_num,axis_num):
    #设置一个子图的一些基本参数
    up_low_edge_width = 0.2
    left_right_edge_width = 0.3
    min_width_bar = 0.02  #bar的最小宽度
    max_width_fig = 12 # 图像的最大宽度
    max_height_fig = 12 #图像的最大高度
    common_legend_height = 1 # 如果子图较多，需要将legend 放在整个fig的顶部共用
    min_subplot_height = 2
    fit_width_bar = 0.15
    fit_suplot_h = 4
    fit_suplot_w = 6
    fit_width_fig = 6

    #首先找一个最优的宽松布局
    com_legend = False
    row = 0
    while row <= subplot_num:
        row += 1
        row_num = row
        column_num = int(math.ceil(subplot_num / row_num))
        subplot_h = max_height_fig/row_num
        if subplot_h> fit_suplot_h:
            subplot_h = fit_suplot_h

        if subplot_h >3:
            if subplot_h <4:
                com_legend = True
            subplot_w = left_right_edge_width * 2 + axis_num * fit_width_bar * (legend_num + 2)
            fig_w = subplot_w * column_num
            if fig_w <fit_width_fig :fig_w = fit_width_fig
            if fig_w < max_width_fig:
                fig_h = subplot_h * row_num
                return fig_w,fig_h,row_num,column_num,com_legend

    # 如果宽松布局无法实现，就找一个最优的紧凑布局
    row = 0
    while row <= subplot_num:
        row += 1
        row_num = row
        column_num = int(math.ceil(subplot_num / row_num))
        subplot_h = max_height_fig/row_num
        if subplot_h> fit_suplot_h:
            subplot_h = fit_suplot_h
        com_legend = True
        if subplot_h >2:
            subplot_w = left_right_edge_width * 2 + axis_num * min_width_bar * (legend_num + 2)
            fig_w = subplot_w * column_num
            if fig_w < max_width_fig:
                fig_h = subplot_h * row_num
                return fig_w,fig_h,row_num,column_num,com_legend

    #如果紧凑布局还是无法实现，就设置强制布局
    row_num = int(math.ceil(math.sqrt(subplot_num)))
    column_num = int(math.ceil(subplot_num / row_num))
    fig_w = max_width_fig
    fig_h = max_height_fig
    com_legend = True
    return fig_w, fig_h, row_num, column_num, com_legend


#透视表参数设置类
class veri_plot_set:
    #初始化设置画图的默认参数
    def __init__(self,subplot = None,legend = None,axis = None,save_dir = ""):
        self.subplot = subplot
        self.legend = legend
        self.axis = axis
        self.save_dir = save_dir
    
    #柱状图参数设置
    def bar(self,veri_result):
        coords = veri_result.coords
        dims = veri_result.dims
        #print(dims)

        not_file_dim = [self.subplot, self.legend, self.axis]
        file_pare_dict = {}
        plot_pare_dict = {}
        for dim in dims:
            if not dim in not_file_dim:
                file_pare_dict[dim] = coords[dim].values.tolist()
            else:
                plot_pare_dict[dim] = coords[dim].values.tolist()

        file_pare_list = para_array_to_list(0,file_pare_dict)
        print(file_pare_list)
        colors = ['r','b','g','m','c','y','orange']
        for para_dict in file_pare_list:
            #print(para_dict)
            veri_result_plot = veri_result.loc[para_dict]
            #print(veri_result_plot)
            subplot_num = len(plot_pare_dict[self.subplot])
            legend_num = len(plot_pare_dict[self.legend])
            axis_num = len(plot_pare_dict[self.axis])
            width_fig, hight_fig, row_num, column_num,com_legend = layout(subplot_num,legend_num,axis_num)
            print(width_fig)
            print(hight_fig)
            print(row_num)
            print(column_num)
            print(com_legend)
            fig,axs = plt.subplots(nrows=row_num, ncols=column_num, figsize=(width_fig, hight_fig))
            for s in range(subplot_num):
                si = int(s / column_num)
                sj = s % column_num
                if row_num == 1 & column_num ==1:
                    ax = axs
                elif row_num == 1:
                    ax = axs[sj]
                elif column_num == 1:
                    ax = axs[si]
                else:
                    ax = axs[si, sj]

                x0 = np.arange(axis_num)
                bar_width = 1/(legend_num + 2)
                para_dict_subplot = {}
                para_dict_subplot[self.subplot] = plot_pare_dict[self.subplot][s]
                legends = plot_pare_dict[self.legend]
                values_subplot = veri_result_plot.loc[para_dict_subplot].values

                for c in range(legend_num):
                    x = x0 - 0.5 + (c + 1.5) * bar_width
                    para_dict_subplot[self.legend] = plot_pare_dict[self.legend][c]
                    values = veri_result_plot.loc[para_dict_subplot].values
                    ax.bar(x,values,bar_width* 0.8,color =  colors[c], label=legends[c])
                xticklabel = plot_pare_dict[self.axis]

                ax.set_title(para_dict_subplot[self.subplot])
                ax.set_xticks(x0)
                ax.set_xticklabels(xticklabel)
                y_max = np.max(values_subplot) * 1.5
                ax.set_ylim(0,y_max)
                ax.legend()
            save_path = self.save_dir
            for key in para_dict.keys():
                save_path += str(key) + "="+ str(para_dict[key]) + "_"
            save_path += ".png"
            nmc_verification.nmc_vf_base.tool.path_tools.creat_path(save_path)
            plt.savefig(save_path)







