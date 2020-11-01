import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import copy
from  matplotlib import  cm
import meteva
import math



def frequency_histogram(ob, fo,grade_list=None, member_list=None,  vmax = None,save_path=None,show = False,dpi = 300,plot = "bar", title="频率统计图",
                        sup_fontsize = 10,width = None,height = None,log_y = False):
    '''
    frequency_histogram 对比测试数据和实况数据的发生的频率
    :param ob: 实况数据 任意维numpy数组
    :param fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 如果该参数为None，观测或预报值出现过的值都作为分类标记.
    如果该参数不为None，它必须是一个从小到大排列的实数，以其中列出的数值划分出的多个区间作为分类标签。
    对于预报和观测值不为整数的情况，grade_list 不能设置为None。
    :param save_path: 保存地址
    :return: 无
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


    legend = ['观测']
    if member_list is None:
        if new_Fo_shape[0] <= 1:
            legend.append('预报')
        else:
            for i in range(new_Fo_shape[0]):
                legend.append('预报' + str(i + 1))
    else:
        legend.extend(member_list)



    result_array = meteva.method.frequency_table(ob, fo, grade_list=grade_list)
    total_count = np.sum(result_array[0,:])
    result_array /= total_count
    if grade_list is not None:
        if len(grade_list) >10:
            axis = ["<\n" + str(round(grade_list[0],6))]
            for index in range(len(grade_list)):
                axis.append(str(round(grade_list[index],6)))
            axis.append(">=\n" + str(round(grade_list[-1],6)))
        else:
            axis = ["<" + str(round(grade_list[0],6))]
            for index in range(len(grade_list) - 1):
                axis.append("[" + str(round(grade_list[index],6)) + "," + str(round(grade_list[index + 1],6)) + ")")
            axis.append(">=" + str(round(grade_list[-1],6)))


    else:
        new_fo = copy.deepcopy(fo).flatten()
        new_ob = copy.deepcopy(ob).flatten()
        fo_list = list(set(new_fo.tolist()))
        fo_list.extend(list(set(new_ob.tolist())))
        axis = list(set(fo_list))

    name_list_dict = {}
    name_list_dict["legend"] = legend
    name_list_dict["类别"] = axis
    if log_y:
        vmin = None
    else:
        vmin = 0
    if plot == "bar":
        meteva.base.plot_tools.bar(result_array,name_list_dict,ylabel= "样本占比",vmin = vmin,vmax = vmax,save_path = save_path,show = show,dpi = dpi,title=title,
                                   width = width,height = height,sup_fontsize= sup_fontsize,log_y = log_y)
    else:
        meteva.base.plot_tools.plot(result_array, name_list_dict, ylabel="样本占比", vmin=vmin, vmax=vmax, save_path=save_path,
                                   show=show, dpi=dpi, title=title,
                                    width = width,height = height,sup_fontsize= sup_fontsize,log_y = log_y)


def performance_grade(ob, fo, grade_list=None, member_list=None, x_y="sr_pod", save_path=None, show=False,
                dpi=300, title="综合表现图",
                sup_fontsize=10, width=None, height=None):
    '''
    分级降水的综合评分图
    :param ob:
    :param fo:
    :param grade_list:
    :return:
    '''


    hfmc_array = meteva.method.multi_category.score.hfmc_grade(ob, fo, grade_list)
    pod = meteva.method.yes_or_no.score.pod_hfmc(hfmc_array)
    sr = meteva.method.yes_or_no.score.sr_hfmc(hfmc_array)

    leftw = 0.6
    rightw = 2
    uphight = 1.2
    lowhight = 1.2
    axis_size_x = 3.7
    axis_size_y = 3.5
    if width is None:
        width = axis_size_x + leftw + rightw

    if height is None:
        height = axis_size_y + uphight + lowhight

    fig = plt.figure(figsize=(width, height), dpi=dpi)
    ax1 = fig.add_axes([leftw / width, lowhight / width, axis_size_x / width, axis_size_y / height])

    x = np.arange(0.0001, 1, 0.0001)
    bias_list = [0.2, 0.4, 0.6, 0.8, 1, 1.25, 1.67, 2.5, 5]
    ts_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
    for i in range(len(bias_list)):
        bias = bias_list[i]
        y1 = bias * x
        x2 = x[y1 < 1]
        y2 = y1[y1 < 1]
        if bias < 1:
            # bias <1 的 线
            ax1.plot(x2, y2, '--', color='k', linewidth=0.5)
            ax1.text(1.01, bias, "bias=" + str(bias), fontsize=sup_fontsize * 0.8)
        elif bias > 1:
            # bias》1的线
            ax1.plot(x2, y2, '--', color='k', linewidth=0.5)
            ax1.text(1.0 / bias - 0.05, 1.02, "bias=" + str(bias), fontsize=sup_fontsize * 0.8)
        else:
            # bias ==1 的线
            ax1.plot(x2, y2, '-', color='k', linewidth=0.5)

    for i in range(len(ts_list)):
        ts = ts_list[i]
        hf = 1
        x2 = np.arange(ts, 1, 0.001)
        hit = hf * x2
        hfm = hit / ts
        m = hfm - hf
        y2 = hit / (hit + m)
        # ts 的线
        plt.plot(x2, y2, "--", color="y", linewidth=0.5)
        error = np.abs(y2 - x2)
        index = np.argmin(error)
        sx = x2[index] + 0.02
        sy = y2[index] - 0.02
        ax1.text(sx, sy, "ts=" + str(ts))

    new_sr = sr.reshape((-1, len(grade_list)))
    new_pod = pod.reshape((-1, len(grade_list)))

    new_sr_shape = new_sr.shape
    label = []
    legend_num = new_sr_shape[0]
    if member_list is None:
        if legend_num == 1:
            label.append('预报')
        else:
            for i in range(legend_num):
                label.append('预报' + str(i + 1))
    else:
        label.extend(member_list)

    colors = meteva.base.color_tools.get_color_list(legend_num)

    marker = ['o', 'v', 's', 'p', "P", "*", 'h', "X", "d", "1", "+", "x", ".", "^", "<", ">",
              "2", "3", "4", "8", "H", "D", "|", "_"]

    a_list = []
    grade_num = len(grade_list)
    if legend_num > 1 and grade_num > 1:
        for line in range(legend_num):
            for i in range(len(grade_list)):
                ax1.plot(new_sr[line, i], new_pod[line, i], marker[i], label=i * line, color=colors[line], markersize=6)
                a_list.append(i * line)
        lines, label1 = ax1.get_legend_handles_labels()
        legend2 = ax1.legend(lines[0:len(lines):len(grade_list)], label, loc="upper right",
                             bbox_to_anchor=(1.5, 1), ncol=1, fontsize=sup_fontsize * 0.9)
        legend1 = ax1.legend(lines[:len(grade_list)], ['grade:' + str(i) for i in grade_list], loc="lower right",
                             bbox_to_anchor=(1.5, 0), ncol=1, fontsize=sup_fontsize * 0.9)
        ax1.add_artist(legend1)
        ax1.add_artist(legend2)

    elif legend_num > 1:
        for line in range(legend_num):
            i = 0
            ax1.plot(new_sr[line, i], new_pod[line, i], marker[line], label=i * line, color=colors[line], markersize=6)
            a_list.append(i * line)
        lines, label1 = ax1.get_legend_handles_labels()

        legend2 = ax1.legend(lines[0:len(lines):len(grade_list)], label, loc="upper right",
                             bbox_to_anchor=(1.5, 1), ncol=1, fontsize=sup_fontsize * 0.9)
        ax1.add_artist(legend2)

    elif grade_num > 1:
        colors = meteva.base.color_tools.get_color_list(grade_num)
        for i in range(grade_num):
            line = 0
            ax1.plot(new_sr[line, i], new_pod[line, i], marker[i], label=i * line, color=colors[i], markersize=6)
            a_list.append(i * line)
        lines, label1 = ax1.get_legend_handles_labels()

        legend1 = ax1.legend(lines[:len(grade_list)], ['grade:' + str(i) for i in grade_list], loc="upper right",
                             bbox_to_anchor=(1.5, 1), ncol=1, fontsize=sup_fontsize * 0.9)
        ax1.add_artist(legend1)

    ax1.set_xlim(0, 1)
    ax1.set_ylim(0, 1)
    if x_y == "sr_pod":
        ax1.set_xlabel("成功率", fontsize=sup_fontsize * 0.9)
        ax1.set_ylabel("命中率", fontsize=sup_fontsize * 0.9)
    else:
        ax1.set_xlabel("空报率", fontsize=sup_fontsize * 0.9)
        ax1.set_ylabel("漏报率", fontsize=sup_fontsize * 0.9)
        x = np.arange(0, 1.01, 0.2)
        ax1.set_xticks(x)
        ax1.set_xticklabels(np.round(1 - x, 1))
        y = np.arange(0, 1.01, 0.2)
        ax1.set_yticks(y)
        ax1.set_yticklabels(np.round(1 - y, 1))

    title = title + "\n"
    ax1.set_title(title, fontsize=sup_fontsize)
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path, bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()