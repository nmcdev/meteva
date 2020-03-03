import time
import copy
import math
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
import numpy as np
import nmc_verification
import pandas as pd
import datetime
from matplotlib.ticker import MultipleLocator


# 参数数组转换为列表
def para_array_to_list(key_num, para_array):
    key_list = []
    for key in para_array.keys():
        key_list.append(key)
    key_count = len(key_list)

    if (key_num == key_count - 1):
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
        para_list0 = para_array_to_list(key_num + 1, para_array)
        para_list = []
        for para in list1:
            for dict0 in para_list0:
                dict1 = {}
                dict1[key] = para
                for key0 in dict0.keys():
                    dict1[key0] = copy.deepcopy(dict0[key0])
                # print(dict1)
                para_list.append(dict1)
    return para_list


# 自动布局模块
def layout(subplot_num, legend_num, axis_num):
    # 设置一个子图的一些基本参数
    up_low_edge_width = 0.2
    left_right_edge_width = 0.3
    min_width_bar = 1  # bar的最小宽度
    max_width_fig = 5  # 图像的最大宽度
    max_height_fig = 3.5  # 图像的最大高度
    common_legend_height = 1  # 如果子图较多，需要将legend 放在整个fig的顶部共用
    min_subplot_height = 2
    fit_width_bar = 0.15
    fit_suplot_h = 4
    fit_suplot_w = 6
    fit_width_fig = 6

    # 首先找一个最优的宽松布局
    com_legend = False
    row = 0
    while row <= subplot_num:
        row += 1
        row_num = row
        column_num = int(math.ceil(subplot_num / row_num))
        subplot_h = max_height_fig / row_num
        if subplot_h > fit_suplot_h:
            subplot_h = fit_suplot_h

        if subplot_h > 3:
            if subplot_h < 4:
                com_legend = True
            subplot_w = left_right_edge_width * 2 + axis_num * fit_width_bar * (legend_num + 2)
            fig_w = subplot_w * column_num
            if fig_w < fit_width_fig:
                fig_w = fit_width_fig
            if fig_w < max_width_fig:
                fig_h = subplot_h * row_num
                return fig_w, fig_h, row_num, column_num, com_legend

    # 如果宽松布局无法实现，就找一个最优的紧凑布局
    row = 0
    while row <= subplot_num:
        row += 1
        row_num = row
        column_num = int(math.ceil(subplot_num / row_num))
        subplot_h = max_height_fig / row_num
        if subplot_h > fit_suplot_h:
            subplot_h = fit_suplot_h
        com_legend = True
        if subplot_h > 2:
            subplot_w = left_right_edge_width * 2 + axis_num * min_width_bar * (legend_num + 2)
            fig_w = subplot_w * column_num
            if fig_w < max_width_fig:
                fig_h = subplot_h * row_num
                return fig_w, fig_h, row_num, column_num, com_legend

    # 如果紧凑布局还是无法实现，就设置强制布局
    row_num = int(math.ceil(math.sqrt(subplot_num)))
    column_num = int(math.ceil(subplot_num / row_num))
    fig_w = max_width_fig
    fig_h = max_height_fig
    com_legend = True

    return fig_w, fig_h, row_num, column_num, com_legend


class veri_plot_set:
    # 初始化设置画图的默认参数
    def __init__(self, subplot=None, legend=None, axis=None, save_dir=""):
        self.subplot = subplot
        self.legend = legend
        self.axis = axis
        self.save_dir = save_dir

    def execute(self, veri_resule, para, dpi, plot_type='plot'):
        plot_type_dict = {
            'bar': self.bar,
            'plot': self.plot
        }
        plot_fun = plot_type_dict[plot_type]
        plot_fun(veri_resule, para, dpi)

    # 柱状图参数设置
    def bar(self, veri_result, para, dpi):
        coords = veri_result.coords

        dims = veri_result.dims
        not_file_dim = [self.subplot, self.legend, self.axis]
        file_pare_dict = {}
        plot_pare_dict = {}
        for dim in dims:
            if not dim in not_file_dim:
                file_pare_dict[dim] = coords[dim].values.tolist()
            else:
                plot_pare_dict[dim] = coords[dim].values.tolist()
        if not file_pare_dict:
            file_pare_dict[self.subplot] = coords[self.subplot].values.tolist()

        file_pare_list = para_array_to_list(0, file_pare_dict)
        colors = ['r', 'b', 'g', 'm', 'c', 'y', 'orange']
        for para_dict in file_pare_list:

            veri_result_plot = veri_result.loc[para_dict]

            subplot_num = 1
            if self.subplot is not None:
                subplot_num = len(plot_pare_dict[self.subplot])
            legend_num = 1
            if self.legend is not None:
                legend_num = len(plot_pare_dict[self.legend])
            axis_num = 1
            if self.axis is not None:
                axis_num = len(plot_pare_dict[self.axis])
            x0 = np.arange(axis_num)
            width_fig, hight_fig, row_num, column_num, com_legend = layout(subplot_num, legend_num, axis_num)

            xticklabel = plot_pare_dict[self.axis]
            interval = 1
            xaxis_index = np.arange(0, len(x0))
            if axis_num > 9 & subplot_num != 1:
                column_num = 1
                row_num = int(subplot_num / column_num)
                # width_fig,hight_fig = hight_fig * (1 + 0.1 * row_num), width_fig * (1 + 0.1 * row_num)+2
                hight_fig = (hight_fig) * (1 + 0.2 * row_num)
                width_fig = hight_fig * 1.6
                hight_fig = hight_fig * 1.8
            if self.is_continuous(self.axis, para):
                if self.axis == 'time':
                    # 判断是否为年还是月
                    xticklabel, xaxis_index, interval = self.set_time_axis(xticklabel, width_fig, dpi)

                    xticklabel = np.array(xticklabel)
                else:
                    xaxis_index = self.set_xaxiS(xticklabel, width_fig, dpi)

            else:
                xticklabel = [str(i) for i in xticklabel]
                max_len = len(max(xticklabel, key=len))
                min_width_fig = axis_num * max_len / 6
                if width_fig / column_num < min_width_fig:
                    width_fig = width_fig * 1.5
                    if width_fig < min_width_fig:
                        column_num = 1
                        width_fig = min_width_fig
                        row_num = subplot_num
                    else:
                        column_num = math.floor(width_fig / min_width_fig)
                        row_num = math.ceil(subplot_num / column_num)
            # plt.figure(figsize=(width_fig*2*column_num,hight_fig*2*row_num))
            # print(width_fig)
            # print(hight_fig)
            fig, axs = plt.subplots(nrows=row_num, ncols=column_num, figsize=(width_fig, hight_fig), dpi=dpi)
            plt.subplots_adjust(wspace=0, hspace=0.45)
            for s in range(subplot_num):
                si = int(s / column_num)
                sj = s % column_num
                if row_num == 1 & column_num == 1:
                    ax = axs
                elif row_num == 1:
                    ax = axs[sj]
                elif column_num == 1:
                    ax = axs[si]
                else:
                    ax = axs[si, sj]

                bar_width = 1 / (legend_num + 2)
                para_dict_subplot = {}

                if self.subplot is not None:
                    para_dict_subplot[self.subplot] = plot_pare_dict[self.subplot][s]
                legends = []
                if self.legend is not None:
                    legends = plot_pare_dict[self.legend]

                values_subplot = veri_result_plot.loc[para_dict_subplot].values
                for c in range(legend_num):
                    x = x0 - 0.5 + (c + 1.5) * bar_width
                    if self.legend is not None:
                        para_dict_subplot[self.legend] = plot_pare_dict[self.legend][c]
                    values = veri_result_plot.loc[para_dict_subplot].values
                    index = values > 100000
                    values[index] = 0

                    ax.scatter(x[index], values[index], marker='x')
                    ax.bar(x, values, bar_width * 0.9)
                    if self.legend is not None:
                        ax.bar(x, values, bar_width * 0.9, color=colors[c], label=legends[c])

                if self.subplot is not None:
                    ax.set_title(para_dict_subplot[self.subplot], fontsize=14)
                xmajorLocator = MultipleLocator(interval)
                ax.xaxis.set_major_locator(xmajorLocator)
                xminorLocator = MultipleLocator(1)
                ax.xaxis.set_minor_locator(xminorLocator)
                ax.set_xticks(x0[xaxis_index])

                ax.set_xticklabels(np.array(xticklabel)[xaxis_index], fontdict={'size': 10})

                y_max = np.max(values_subplot) * 1.5

                ax.set_ylim(0, y_max)

                plt.legend(loc='upper center', bbox_to_anchor=(0, -0.05, 1, 1), ncol=legend_num,
                           bbox_transform=plt.gcf().transFigure)
            save_path = self.save_dir
            for key in para_dict.keys():
                save_path += str(key) + "=" + str(para_dict[key]).replace(':', '') + "_"
            save_path += ".png"
            nmc_verification.nmc_vf_base.tool.path_tools.creat_path(save_path)
            plt.savefig(save_path)

    def set_xaxiS(self, xticklabel, width_fig, dpi):

        xticklabel = [str(i) for i in xticklabel]
        if '\n' in xticklabel[0]:
            max_len = len(xticklabel[0].split('\n')[-1])
        else:
            max_len = len(max(xticklabel, key=len))
        # 求取可以容纳多少个axis
        axis_num = int(math.floor(width_fig * dpi / 10 / max_len))
        if len(xticklabel) > axis_num:
            interval = int(math.ceil(len(xticklabel) / axis_num))
            index = list(range(0, len(xticklabel), interval))
        else:
            index = list(range(0, len(xticklabel), 1))
        return index

    # 需要更改
    def is_continuous(self, axis, para):
        time_coord = ['year', 'month', 'day', 'dtime', 'time']
        all_group = np.array(para['group_set'][self.axis]['group'])
        all_group = all_group.reshape(-1)
        all_group.sort()

        diff = all_group[1:] - all_group[0:-1]

        if axis in time_coord and len(set(diff.flatten())) == 1:
            return True
        else:
            return False

    def set_time_axis(self, xticklabel, width_fig, dpi):

        time0 = datetime.datetime.strptime(xticklabel[0], "%Y-%m-%d %H:%M:%S")

        str_list = [self.get_time_str_one_by_one_n(time0)]
        index_list = []
        for time_name_index in range(len(xticklabel) - 1):
            time1 = datetime.datetime.strptime(xticklabel[time_name_index], "%Y-%m-%d %H:%M:%S")
            time2 = datetime.datetime.strptime(xticklabel[time_name_index + 1], "%Y-%m-%d %H:%M:%S")
            str1 = self.get_time_str_one_by_one_n(time2, time1)

            if '\n' in str1 and len(str1.split('\n')[-1]) >= 6:
                index_list.append(time_name_index + 1)

            str_list.append(str1)

        if len(xticklabel) > 16:
            interval = int(math.ceil(len(xticklabel) / 14))
            index = list(range(0, len(xticklabel), interval))
            for i in index_list:
                if i not in index:
                    str_list[i] = '\n' + str_list[i].split('\n')[-1]
            index = list(set(index + index_list))
            index.sort()

        else:
            index = list(range(0, len(xticklabel)))
            interval = 1

        return str_list, index, interval

    def str_replenish(self, x):
        return x.zfill(2)

    def get_time_str_one_by_one_n(self, time1, time0=None):
        if time0 is None:
            time2 = nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_datetime(time1)
            if time2.hour == 0 and time2.minute == 0:
                # time_str = time2.strftime('%d{d}\n%Y{y}%m{m}').format(y='年', m='月', d='日')
                year = time2.strftime('%y') + '年'
                month = str(int(time2.strftime('%m'))) + '月'
                day = time2.strftime('%d') + '日\n'
                time_str = day + year + month
            elif time2.minute == 0:
                hour = time2.strftime('%H') + '时\n'
                year = time2.strftime('%y') + '年'
                month = str(int(time2.strftime('%m'))) + '月'
                day = str(int(time2.strftime('%d'))) + '日'
                time_str = hour + year + month + day

                # time_str = time2.strftime(str(int('%H')) + '{h}\n%y{y}' + str(int('%m')) + '{m}' + str(int('%d')) + '{d}').format(y='年', m='月',d='日', h='时')
                # time_str = time2.strftime('%H{h}\n%Y{y}%m{m}%d{d}').format(y='年', m='月', d='日', h='时')
            else:
                # time_str = time2.strftime('%M{mi}\n%Y{y}%m{m}%d{d}%H{h}').format(y='年', m='月', d='日', h='时', mi='分')
                hour = str(int(time2.strftime('%H'))) + '时'
                year = time2.strftime('%y') + '年'
                month = str(int(time2.strftime('%m'))) + '月'
                day = str(int(time2.strftime('%d'))) + '日'
                minute = time2.strftime('%M') + '分\n'
                time_str = minute + year + month + day + hour
        else:
            time00 = nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_datetime(time0)
            time2 = nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_datetime(time1)
            if time2.year != time00.year:
                if time2.hour == 0 and time2.minute == 0 and time00.hour == 0 and time00.hour == 0:
                    # time_str = time1.strftime('%d{d}\n%Y{y}%m{m}').format(y='年', m='月', d='日')
                    year = time2.strftime('%y') + '年'
                    month = str(int(time2.strftime('%m'))) + '月'
                    day = time2.strftime('%d') + '日\n'
                    time_str = day + year + month
                elif time1.minute == 0:
                    # time_str = time1.strftime(
                    #     str(int('%H')) + '{h}\n%y{y}' + str(int('%m')) + '{m}' + str(int('%d')) + '{d}').format(y='年',
                    #                                                                             m='月',
                    hour = time2.strftime('%H') + '时\n'
                    year = time2.strftime('%y') + '年'
                    month = str(int(time2.strftime('%m'))) + '月'
                    day = str(int(time2.strftime('%d'))) + '日'
                    time_str = hour + year + month + day
                    # h='时')
                else:
                    hour = str(int(time2.strftime('%H'))) + '时'
                    year = time2.strftime('%y') + '年'
                    month = str(int(time2.strftime('%m'))) + '月'
                    day = str(int(time2.strftime('%d'))) + '日'
                    minute = time2.strftime('%M') + '分\n'
                    time_str = minute + year + month + day + hour
                    # time_str = time1.strftime('%M{mi}\n%Y{y}%m{m}%d{d}%H{h}').format(y='年', m='月', d='日', h='时', mi='分')

            elif time2.month != time00.month:
                if time2.hour == 0 and time2.minute == 0 and time00.hour == 0 and time00.hour == 0:
                    # time_str = time2.strftime('%d{d}\n%m{m}').format(m='月', d='日')
                    month = str(int(time2.strftime('%m'))) + '月'
                    day = time2.strftime('%d') + '日\n'
                    time_str = day + month
                elif time2.minute == 0:
                    # time_str = time2.strftime('%H{h}\n%m{m}%d{d}').format(m='月', d='日', h='时')
                    hour = time2.strftime('%H') + '时\n'

                    month = str(int(time2.strftime('%m'))) + '月'
                    day = str(int(time2.strftime('%d'))) + '日'
                    time_str = hour + month + day
                else:
                    hour = str(int(time2.strftime('%H'))) + '时'
                    month = str(int(time2.strftime('%m'))) + '月'
                    day = str(int(time2.strftime('%d'))) + '日'
                    minute = time2.strftime('%M') + '分\n'
                    time_str = minute + month + day + hour
                    # time_str = time2.strftime('%M{mi}\n%m{m}%d{d}%H{h}').format(m='月', d='日', h='时', mi='分')
            elif time2.day != time00.day:
                if time2.hour == 0 and time2.minute == 0 and time00.hour == 0 and time00.hour == 0:
                    time_str = time2.strftime('%d{d}').format(d='日')
                elif time2.minute == 0:
                    # time_str = time2.strftime('%H{h}\n%d{d}').format(d='日', h='时')
                    hour = time2.strftime('%H') + '时\n'
                    day = str(int(time2.strftime('%d'))) + '日'
                    time_str = hour + day
                else:
                    # time_str = time2.strftime('%M{mi}\n%d{d}%H{h}').format(d='日', h='时', mi='分')
                    hour = str(int(time2.strftime('%H'))) + '时'
                    day = str(int(time2.strftime('%d'))) + '日'
                    minute = time2.strftime('%M') + '分\n'
                    time_str = minute + day + hour
            elif time2.hour != time00.hour:
                if time2.minute == 0:
                    time_str = time2.strftime('%H{h}').format(h='时')
                else:
                    # time_str = time2.strftime('%M{mi}\n%H{h}').format(h='时', mi='分')
                    minute = time2.strftime('%M') + '分\n'
                    hour = str(int(time2.strftime('%H'))) + '时'
                    time_str = minute + hour
            else:
                time_str = time2.strftime("%M分")
        if time_str == '\n20时':
            print('---------------------------')
        return time_str

    def plot(self, veri_result, para, dpi):
        coords = veri_result.coords
        dims = veri_result.dims
        not_file_dim = [self.subplot, self.legend, self.axis]
        file_pare_dict = {}
        plot_pare_dict = {}
        for dim in dims:
            if not dim in not_file_dim:
                file_pare_dict[dim] = coords[dim].values.tolist()
            else:
                plot_pare_dict[dim] = coords[dim].values.tolist()
        if not file_pare_dict:
            file_pare_dict[self.subplot] = coords[self.subplot].values.tolist()
        file_pare_list = para_array_to_list(0, file_pare_dict)
        colors = ['r', 'b', 'g', 'm', 'c', 'y', 'orange']
        for para_dict in file_pare_list:
            veri_result_plot = veri_result.loc[para_dict]
            subplot_num = 1
            if self.subplot is not None:
                subplot_num = len(plot_pare_dict[self.subplot])
            legend_num = 1
            if self.legend is not None:
                legend_num = len(plot_pare_dict[self.legend])
            axis_num = 1
            if self.axis is not None:
                axis_num = len(plot_pare_dict[self.axis])
            x0 = np.arange(axis_num)
            width_fig, hight_fig, row_num, column_num, com_legend = layout(subplot_num, legend_num, axis_num)
            xticklabel = plot_pare_dict[self.axis]
            interval = 1
            xaxis_index = np.arange(0, len(x0))
            if axis_num > 9:
                column_num = 1
                row_num = int(subplot_num / column_num)
                width_fig, hight_fig = hight_fig, width_fig * (1 + 0.1 * row_num)
            if self.is_continuous(self.axis, para):
                if self.axis == 'time':
                    # 判断是否为年还是月
                    xticklabel, xaxis_index, interval = self.set_time_axis(xticklabel, width_fig, dpi)
                    xticklabel = np.array(xticklabel)
                else:
                    xaxis_index = self.set_xaxiS(xticklabel, width_fig, dpi)

            else:
                xticklabel = [str(i) for i in xticklabel]
                max_len = len(max(xticklabel, key=len))
                min_width_fig = axis_num * max_len / 6
                if width_fig / column_num < min_width_fig:
                    width_fig = width_fig * 1.5
                    if width_fig < min_width_fig:
                        column_num = 1
                        width_fig = min_width_fig
                        row_num = subplot_num
                    else:
                        column_num = math.floor(width_fig / min_width_fig)
                        row_num = math.ceil(subplot_num / column_num)
            # plt.figure(figsize=(width_fig*2*column_num,hight_fig*2*row_num))
            fig, axs = plt.subplots(nrows=row_num, ncols=column_num, figsize=(width_fig, hight_fig), dpi=dpi)
            for s in range(subplot_num):
                si = int(s / column_num)
                sj = s % column_num
                if row_num == 1 & column_num == 1:
                    ax = axs
                elif row_num == 1:
                    ax = axs[sj]
                elif column_num == 1:
                    ax = axs[si]
                else:
                    ax = axs[si, sj]

                bar_width = 1 / (legend_num + 2)
                para_dict_subplot = {}

                if self.subplot is not None:
                    para_dict_subplot[self.subplot] = plot_pare_dict[self.subplot][s]
                legends = []
                if self.legend is not None:
                    legends = plot_pare_dict[self.legend]

                values_subplot = veri_result_plot.loc[para_dict_subplot].values
                for c in range(legend_num):
                    x = x0 - 0.5 + (c + 1.5) * bar_width
                    if self.legend is not None:
                        para_dict_subplot[self.legend] = plot_pare_dict[self.legend][c]
                    values = veri_result_plot.loc[para_dict_subplot].values
                    index = values > 100000
                    values[index] = 0

                    ax.scatter(x[index], values[index], marker='x')
                    ax.plot(x, values)
                    if self.legend is not None:
                        ax.plot(x, values, color=colors[c], label=legends[c])

                if self.subplot is not None:
                    ax.set_title(para_dict_subplot[self.subplot])
                xmajorLocator = MultipleLocator(interval)
                ax.xaxis.set_major_locator(xmajorLocator)
                xminorLocator = MultipleLocator(1)
                ax.xaxis.set_minor_locator(xminorLocator)
                ax.set_xticks(x0[xaxis_index])

                ax.set_xticklabels(np.array(xticklabel)[xaxis_index], fontdict={'size': 12})
                y_max = np.max(values_subplot) * 1.5

                ax.set_ylim(0, y_max)

                plt.legend(loc='upper center', bbox_to_anchor=(0, -0.05, 1, 1), ncol=legend_num,
                           bbox_transform=plt.gcf().transFigure)
            save_path = self.save_dir
            for key in para_dict.keys():
                save_path += str(key) + "=" + str(para_dict[key]).replace(':', '') + "_"
            save_path += ".png"
            nmc_verification.nmc_vf_base.tool.path_tools.creat_path(save_path)
            plt.savefig(save_path)

        pass

# def layout1(subplot_num, legend_num, axis_num):
#     # 设置一个子图的一些基本参数
#     up_low_edge_width = 0.2
#     left_right_edge_width = 0.3
#     min_width_bar = 0.02  # bar的最小宽度
#     max_width_fig = 12  # 图像的最大宽度
#     max_height_fig = 12  # 图像的最大高度
#     common_legend_height = 1  # 如果子图较多，需要将legend 放在整个fig的顶部共用
#     min_subplot_height = 2
#     fit_width_bar = 0.15
#     fit_suplot_h = 4
#     fit_suplot_w = 6
#     fit_width_fig = 6
#
#     # 首先找一个最优的宽松布局
#     com_legend = False
#     row = 0
#     while row <= subplot_num:
#         row += 1
#         row_num = row
#         column_num = int(math.ceil(subplot_num / row_num))
#         subplot_h = max_height_fig / row_num
#         if subplot_h > fit_suplot_h:
#             subplot_h = fit_suplot_h
#
#         if subplot_h > 3:
#             if subplot_h < 4:
#                 com_legend = True
#             subplot_w = left_right_edge_width * 2 + axis_num * fit_width_bar * (legend_num + 2)
#             fig_w = subplot_w * column_num
#             if fig_w < fit_width_fig:
#                 fig_w = fit_width_fig
#             if fig_w < max_width_fig:
#                 fig_h = subplot_h * row_num
#                 return fig_w, fig_h, row_num, column_num, com_legend
#
#     # 如果宽松布局无法实现，就找一个最优的紧凑布局
#     row = 0
#     while row <= subplot_num:
#         row += 1
#         row_num = row
#         column_num = int(math.ceil(subplot_num / row_num))
#         subplot_h = max_height_fig / row_num
#         if subplot_h > fit_suplot_h:
#             subplot_h = fit_suplot_h
#         com_legend = True
#         if subplot_h > 2:
#             subplot_w = left_right_edge_width * 2 + axis_num * min_width_bar * (legend_num + 2)
#             fig_w = subplot_w * column_num
#             if fig_w < max_width_fig:
#                 fig_h = subplot_h * row_num
#                 return fig_w, fig_h, row_num, column_num, com_legend
#
#     # 如果紧凑布局还是无法实现，就设置强制布局
#     row_num = int(math.ceil(math.sqrt(subplot_num)))
#     column_num = int(math.ceil(subplot_num / row_num))
#     fig_w = max_width_fig
#     fig_h = max_height_fig
#     com_legend = True
#     return fig_w, fig_h, row_num, column_num, com_legend

# dim_names = ["year", "model", "grade", "index"]
# axis_list_list = [[2016, 2017],
#                   ["EC", "NCEP"],
#                   [0.1, 10, 25],
#                   ["ts", "bias"]]
# array = np.zeros((2, 2, 3, 2))
# sla = [3, 2, 0]
# (5, 5)
# sla = [-1, 0, 1]
#
#
# def plot(array, dim_name_list=None, axis_list_list=None, subplot_legend_axis=[0, 1, 2]):
#     pass
#     if dim_name_list is None:
#         ndim = len(array.shape)
#         dim_name_list = []
#         dim_name_list = ["dim1", "dim2"]
#
#     if axis_list_list is None:
#         pass
#
#
# def bar():
#     pass
# time_series = pd.Series(xticklabel)
# time_series = time_series.astype(np.datetime64)
# years = time_series.map(lambda x: x.year).values.astype(np.int16)
# months = time_series.map(lambda x: x.month).values.astype(np.int16)
# days = time_series.map(lambda x: x.day).values.astype(np.int16)
# hours = time_series.map(lambda x: x.hour).values.astype(np.int16)
# months_list = list(map(self.str_replenish, months.astype(np.str).tolist()))
# days_list = list(map(self.str_replenish, days.astype(np.str).tolist()))
# hours_list = list(map(self.str_replenish, hours.astype(np.str).tolist()))
# months_len = len(days_list)

# months_days_list = np.char.add(months_list, days_list)
# enter_list = ['\n'] * months_len
# months_days_list = np.char.add(enter_list, months_days_list)
# months_days_list = np.char.add(months_days_list, hours_list)
# months_days_list = list(months_days_list)
#
# year_index_list = []
# for i in set(years):
#     # 通过列表来实现首个年或者首个月
#     select_year_np = list(time_series.map(lambda x: x.year).values.astype(np.int16) == int(i))
#     year_index = select_year_np.index(True)
#     year_index_list.append(year_index)
#     for j in set(months):
#         select_month_np = list(time_series.map(lambda x: x.month).values.astype(np.int16) == int(i))
#         month_index = select_month_np.index(True)
#         months_index_list.append(month_index)
#     months_days_list[index] = str(i) + str(months_days_list[index])
# index = self.set_xaxiS(months_days_list, width_fig, dpi)
# index = list(set(index + year_index_list))
# index.sort()
# return index, months_days_list
