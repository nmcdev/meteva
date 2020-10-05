import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
from meteva.method.yes_or_no.score import pofd_hfmc, pod_hfmc
from meteva.base.tool.plot_tools import set_plot_IV
from meteva.base import IV
import matplotlib.patches as patches
import meteva
import math


def reliability(Ob, Fo, grade_count=10, member_list=None, vmax = None,log_y = False,save_path=None,show = False,dpi = 300, title="可靠性图",
                sup_fontsize =10,width = None,height = None):
    '''
    :param Ob:
    :param Fo:
    :param save_path:
    :return:
    '''
    hnh_array = meteva.method.hnh(Ob, Fo, grade_count)

    reliability_hnh(hnh_array, member_list=member_list,vmax = vmax,log_y = log_y,dpi = dpi, save_path=save_path,show = show, title=title,
                    width=width, height=height, sup_fontsize=sup_fontsize)


def reliability_hnh(hnh_array,  member_list=None,vmax = None,log_y = False, save_path=None,show = False,dpi = 300, title="可靠性图",
                    sup_fontsize= 10,width = None,height = None):
    '''
    根据中间结果计算
    :param th:
    :param save_path:
    :return:
    '''

    grade_count = hnh_array.shape[-2]
    grade = 1 / grade_count
    if grade_count < 1:
        print('grade_count输入错误，不能小于1')
        return
    grade_list = np.arange(0, 1, grade).tolist()
    grade_list.append(1.1)
    hnh_array = hnh_array.reshape((-1, len(grade_list) - 1, 2))
    new_hnh_array_shape = hnh_array.shape
    label = []
    legend_num = new_hnh_array_shape[0]
    if member_list is None:
        if legend_num== 1:
            label.append('预报')
        else:
            for i in range(legend_num):
                label.append('预报' + str(i + 1))
    else:
        label.extend(member_list)

    color_list = meteva.base.tool.color_tools.get_color_list(legend_num)

    if width is None:
        width = 5.5
    if height is None:
        height = 6.1

    for line in range(new_hnh_array_shape[0]):
        total_grade_num = hnh_array[line, :, 0]
        observed_grade_num = hnh_array[line, :, 1]
        ngrade = len(total_grade_num)
        grade = 1 / ngrade
        total_num = np.sum(total_grade_num)
        under = np.zeros_like(total_grade_num)
        under[:] = total_grade_num[:]
        under[total_grade_num == 0] = 1
        ob_rate = observed_grade_num / under
        ob_rate[total_grade_num == 0] = IV
        ob_rate_noIV = set_plot_IV(ob_rate)
        ob_rate[total_grade_num == 0] = np.nan
        index_iv = np.where(total_grade_num == 0)
        line_x = np.arange(0, 1.00, grade)
        prefect_line_y = np.arange(0, 1.00, grade)
        climate_line_y = np.ones_like(line_x) * np.sum(observed_grade_num) / total_num
        x = np.arange(grade / 2, 1, grade)

        if line == 0:
            fig = plt.figure(figsize=(width,height),dpi = dpi)
            grid_plt = plt.GridSpec(5, 1, hspace=0)
            ax1 = plt.subplot(grid_plt[0:4, 0])
            plt.plot(line_x, prefect_line_y, '--', label="完美", color="k")
            plt.plot(line_x, climate_line_y, ':', label="无技巧", color="k")
        plt.plot(x, ob_rate_noIV, "--", linewidth=0.5, color="k")
        x_iv = x[index_iv[0]]
        ob_rate_noIV_iv = ob_rate_noIV[index_iv[0]]
        plt.plot(x_iv, ob_rate_noIV_iv, "x", color='k')
        plt.plot(x, ob_rate, marker=".", markersize="10", label=label[line], color=color_list[line])

        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.ylim(0.0, 1)
        plt.ylabel("正样本比例",fontsize = sup_fontsize * 0.9)
        plt.legend(loc=2,fontsize = sup_fontsize * 0.9)
        plt.title(title,fontsize = sup_fontsize)
    bar_width = 0.8 / (grade_count * (legend_num+2))
    for line in range(new_hnh_array_shape[0]):
        total_grade_num = hnh_array[line, :, 0]
        observed_grade_num = hnh_array[line, :, 1]
        ngrade = len(total_grade_num)
        grade = 1 / ngrade
        under = np.zeros_like(total_grade_num)
        under[:] = total_grade_num[:]
        under[total_grade_num == 0] = 1
        ob_rate = observed_grade_num / under
        ob_rate[total_grade_num == 0] = IV
        ob_rate[total_grade_num == 0] = np.nan

        x = np.arange(grade / 2, 1, grade)
        if line == 0:
            ax2 = plt.subplot(grid_plt[4, 0], sharex=ax1)
        #x1 = x - 0.01 + (line + 1.5) * 0.01

        x1 = x + (line - legend_num/2 + 0.5) * bar_width
        plt.bar(x1, total_grade_num, width=bar_width*0.8,color=color_list[line])
        plt.ylabel("样本数",fontsize = sup_fontsize * 0.9)
        if log_y: plt.yscale('log')
        plt.xlim(0.0, 1.0)
        plt.xticks(np.arange(0.1, 1.01, 0.1))
        plt.xlabel("预测的概率",fontsize = sup_fontsize * 0.9)
        if vmax is not None:
            plt.ylim(0,vmax)
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()


def roc(Ob, Fo, grade_count=10, member_list=None, save_path=None,show = False,dpi = 300, title="ROC图",
        sup_fontsize =10,width = None,height = None):
    '''

    :param Ob:
    :param Fo:
    :param grade_count:
    :param save_path:
    :return:
    '''
    hnh_array = meteva.method.hnh(Ob, Fo, grade_count)
    roc_hnh(hnh_array,  member_list=member_list, save_path=save_path,show = show,dpi = dpi, title=title,
            width=width, height=height, sup_fontsize=sup_fontsize)


def roc_hfmc(hfmc_array, member_list=None, save_path=None,show = False,dpi = 300, title="ROC图",
            sup_fontsize =10,width = None,height = None):
    '''

    :param hfmc:
    :param save_path:
    :return:
    '''
    if width is None:
        width = 5
    if height is None:
        height = 5
    fig = plt.figure(figsize=(width, height),dpi = dpi)
    grade_count = hfmc_array.shape[-2]
    grade = 1 / grade_count
    if grade_count < 1:
        print('grade_count输入错误，不能小于1')
        return
    grade_list = np.arange(0, 1, grade).tolist()
    grade_list.append(1.1)
    shape = list(hfmc_array.shape)
    new_hfmc_array = hfmc_array.reshape((-1, len(grade_list) - 1, 4))
    new_hfmc_array_shape = new_hfmc_array.shape
    label = []
    if member_list is None:
        if new_hfmc_array_shape[0] == 1:
            label.append('预报')
        else:
            for i in range(new_hfmc_array_shape[0]):
                label.append('预报' + str(i + 1))
    else:
        label.extend(member_list)


    for line in range(new_hfmc_array_shape[0]):
        far = [1]
        far.extend(pofd_hfmc(new_hfmc_array[line, :]).tolist())
        far.append(0)
        pod = [1]
        pod.extend(pod_hfmc(new_hfmc_array[line, :]).tolist())
        pod.append(0)
        far = np.array(far)
        pod = np.array(pod)
        if (far.size < 30):
            plt.plot(far, pod,  linewidth=2, marker=".", label=label[line])
        else:
            plt.plot(far, pod,  linewidth=2, label=label[line])
    plt.plot([0, 1], [0, 1], ":", color="k", linewidth=1, label="无技巧")
    plt.xlabel("空报率", fontsize=sup_fontsize * 0.9)
    plt.ylabel("命中率", fontsize=sup_fontsize * 0.9)
    plt.ylim(0.0, 1.0)
    plt.xlim(0.0, 1.0)
    plt.legend(loc=4, fontsize=sup_fontsize * 0.9)
    plt.title(title, fontsize=sup_fontsize)
    plt.xticks(fontsize=sup_fontsize * 0.8)
    plt.yticks(fontsize=sup_fontsize * 0.8)

    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()

def roc_hnh(hnh_array,  member_list=None, save_path=None,show  =False, dpi = 300, title="ROC图",
            sup_fontsize =10,width = None,height = None):
    '''

    :param th_array:
    :param save_path:
    :return:
    '''
    hfmc_list = []
    grade_count = hnh_array.shape[-2]
    grade = 1 / grade_count
    if grade_count < 1:
        print('grade_count输入错误，不能小于1')
        return
    grade_list = np.arange(0, 1, grade).tolist()
    grade_list.append(1.1)
    shape = list(hnh_array.shape)
    hnh_array = hnh_array.reshape((-1, len(grade_list) - 1, 2))
    new_hnh_array_shape = hnh_array.shape
    for line in range(new_hnh_array_shape[0]):
        total_grade_num = hnh_array[line, :, 0]
        observed_grade_num = hnh_array[line, :, 1]
        ngrade = len(total_grade_num)
        hfmc = np.zeros((len(total_grade_num), 4))
        total_hap = np.sum(observed_grade_num)
        total_num = np.sum(total_grade_num)
        for i in range(ngrade):
            hfmc[i, 0] = np.sum(observed_grade_num[i:])
            hfmc[i, 1] = np.sum(total_grade_num[i:]) - hfmc[i, 0]
            hfmc[i, 2] = total_hap - hfmc[i, 0]
            hfmc[i, 3] = total_num - (hfmc[i, 0] + hfmc[i, 1] + hfmc[i, 2])
        hfmc_list.append(hfmc)
    hfmc_array = np.array(hfmc_list)
    shape = shape[:-2]
    shape.append(len(grade_list) - 1)
    shape.append(4)
    hfmc_array.reshape(shape)
    roc_hfmc(hfmc_array,  member_list=member_list,dpi=dpi,show=show, save_path=save_path, title=title,sup_fontsize=sup_fontsize,width= width,height= height)


def discrimination(Ob, Fo, grade_count=10,member_list=None,  vmax = None,log_y  = False, save_path=None,show = False,dpi = 300, title="区分能力图",
                    sup_fontsize =10,width = None,height = None):
    '''

    :param Ob:
    :param Fo:
    :param grade_count:
    :param save_path:
    :return:
    '''
    hnh_array = meteva.method.hnh(Ob, Fo, grade_count)
    discrimination_hnh(hnh_array, member_list = member_list,vmax = vmax,log_y = log_y, save_path=save_path,show = show,dpi = dpi, title=title,
                       width=width, height=height, sup_fontsize=sup_fontsize)


def discrimination_hnh(hnh_array,  member_list=None, vmax = None,log_y = False,save_path=None,show = False,dpi = 300, title="区分能力图",
                        sup_fontsize =10,width = None,height = None):
    '''

    :param th_array:
    :param save_path:
    :return:
    '''

    grade_count = hnh_array.shape[-2]
    grade = 1 / grade_count
    if grade_count < 1:
        print('grade_count输入错误，不能小于1')
        return
    grade_list = (np.arange(0, 1+0.5* grade, grade) *100).astype(np.int16)/100
    new_th_array = hnh_array.reshape((-1, len(grade_list) - 1, 2))
    new_th_array_shape = new_th_array.shape

    if width is None:
        width = meteva.base.plot_tools.caculate_axis_width(grade_list,sup_fontsize,new_th_array_shape[0])
        if width > 10:
            width = 10
        if width<5:
            width =5
    if height is None:
        height = width *0.5
    label = []
    legend_num = new_th_array_shape[0]
    if member_list is None:
        if legend_num == 1:
            label.append('预报')
        else:
            for i in range(legend_num):
                label.append('预报' + str(i + 1))
    else:
        label.extend(member_list)

    fig = plt.figure(figsize=(width, height),dpi = dpi)
    ymax = 0
    color_list = meteva.base.tool.color_tools.get_color_list(legend_num)
    legend_col = int(width * 0.7)
    legend_row = int(math.ceil(legend_num / legend_col))
    legend_col = int(math.ceil(legend_num / legend_row))

    axes = plt.subplot(1, 1, 1)
    grade = 1 / grade_count
    x = np.arange(grade / 2, 1, grade)
    bar_width = 1 / (grade_count * (legend_num+3))

    mark_line_x = []
    mark_line_y = []
    for line in range(new_th_array_shape[0]):
        total_grade_num = new_th_array[line, :, 0]
        observed_grade_num = new_th_array[line, :, 1]
        total_num = np.sum(total_grade_num)
        observed_grade_rate = observed_grade_num / total_num
        not_observed_grade_num = total_grade_num - observed_grade_num
        not_observed_grade_rate = not_observed_grade_num / total_num

        x1 = x + (line - legend_num/2 + 0.5) * bar_width
        mark_line_x.append(x1)
        mark_line_y.append((not_observed_grade_rate + observed_grade_rate)* x)

        axes.bar(x1, observed_grade_rate, width=bar_width*0.8,fc = color_list[line])
        axes.bar(x1, not_observed_grade_rate + observed_grade_rate, width=bar_width*0.8, fill=False,ec = color_list[line])

        ymax = max(np.max(not_observed_grade_rate + observed_grade_rate), ymax)
    mark_line_x = np.array(mark_line_x)
    mark_line_y = np.array(mark_line_y)
    mark_line_x = mark_line_x.T.flatten()
    mark_line_y = mark_line_y.T.flatten()
    axes.plot(mark_line_x, mark_line_y, '.', color='k')
    lines = axes.get_children()
    plt.xlabel("预测的概率", fontsize=sup_fontsize * 0.9)
    plt.ylabel("占总样本数的比例", fontsize=sup_fontsize * 0.9)
    if log_y: plt.yscale("log")

    if vmax is None:
        if log_y:
            vmax = ymax * 10
        else:
            vmax = ymax * 1.5


    plt.ylim(0.0, vmax)
    plt.xlim(0.0, 1)
    nlabel = len(label)
    legend1 = plt.legend([lines[0], lines[grade_count],lines[grade_count * nlabel * 2 ]], ['观测正例', '观测负例',"合理比例"],
                         loc='upper center', bbox_to_anchor=(0.5, 1), ncol=3,fontsize = sup_fontsize * 0.9)
    axes.add_artist(legend1)
    if legend_num > 1:
        legend2 = plt.legend(lines[0:grade_count * nlabel * 2:grade_count * 2], label, loc='upper center',
                             bbox_to_anchor=(0.5, 1 - 0.3/height), ncol = legend_col)

        axes.add_artist(legend2)

    plt.yticks(fontsize = sup_fontsize * 0.8)
    xtick = np.arange(0, 1.001, 0.1)
    plt.xticks(xtick, fontsize=sup_fontsize * 0.8)
    plt.title(title, fontsize=sup_fontsize)
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()


def comprehensive_probability(Ob, Fo, grade_count=10, member_list=None,vmax = None,log_y = False,save_path=None,dpi = 300,show = False, title="概率预报综合检验图",
                                sup_fontsize =10,width = None,height = None):
    '''
    :param Ob:
    :param Fo:
    :param save_path:
    :return:
    '''
    hnh_array = meteva.method.hnh(Ob, Fo, grade_count)
    comprehensive_hnh(hnh_array,member_list = member_list,vmax = vmax,log_y = log_y,save_path=save_path,show = show, dpi = dpi,title=title,
                      width=width, height=height, sup_fontsize=sup_fontsize)


def comprehensive_hnh(hnh_array,  member_list=None,vmax = None,log_y = False, save_path=None,show = False,dpi = 300, title="概率预报综合检验图",
                      sup_fontsize =10,width = None,height = None):
    '''

    :param th_array:
    :param save_path:
    :return:
    '''
    if width is None:
        width  = 8
    if height is None:
        height = 5.6
    fig = plt.figure(figsize=(width,height),dpi = dpi)
    grade_count = hnh_array.shape[-2]
    grade = 1 / grade_count
    if grade_count < 1:
        print('grade_count输入错误，不能小于1')
        return
    grade_list = np.arange(0, 1, grade).tolist()
    grade_list.append(1.1)
    shape = list(hnh_array.shape)
    new_th_array = hnh_array.reshape((-1, len(grade_list) - 1, 2))
    new_th_array_shape = new_th_array.shape
    label = []
    legend_num = new_th_array_shape[0]
    if member_list is None:
        if legend_num == 1:
            label.append('预报')
        else:
            for i in range(legend_num):
                label.append('预报' + str(i + 1))
    else:
        label.extend(member_list)
    color_list = meteva.base.tool.color_tools.get_color_list(legend_num)
    bar_width = 1.0 / (grade_count * (legend_num + 3))
    ymax = -9999
    mark_line_x = []
    mark_line_y = []
    for line in range(legend_num):
        total_grade_num = new_th_array[line, :, 0]
        observed_grade_num = new_th_array[line, :, 1]
        total_num = np.sum(total_grade_num)

        under = np.zeros_like(total_grade_num)
        under[:] = total_grade_num[:]
        under[total_grade_num == 0] = 1
        ob_rate = observed_grade_num / under
        ob_rate[total_grade_num == 0] = IV
        ob_rate_noIV = set_plot_IV(ob_rate)
        ob_rate[total_grade_num == 0] = np.nan
        index_iv = np.where(total_grade_num == 0)

        not_observed_grade_num = total_grade_num - observed_grade_num

        ngrade = len(total_grade_num)
        grade = 1 / ngrade
        x = np.arange(grade / 2, 1, grade)

        line_x = np.arange(0, 1.01, 0.1)
        prefect_line_y = np.arange(0, 1.01, 0.1)
        climate_line_y = np.ones_like(line_x) * np.sum(observed_grade_num) / total_num

        grid_plt = plt.GridSpec(6, 2)
        if line == 0:
            plt.suptitle(title,fontsize= sup_fontsize,y=0.95)
            plt.subplots_adjust(wspace=0.2, hspace=1)
            ax3 = plt.subplot(grid_plt[0:4, 1])
            ax4 = plt.subplot(grid_plt[4:, :])
            ax1 = plt.subplot(grid_plt[0:4, 0])
        ax1.plot(x, ob_rate_noIV, "--", linewidth=0.5, color="k")
        x_iv = x[index_iv[0]]
        ob_rate_noIV_iv = ob_rate_noIV[index_iv[0]]

        ax1.plot(x_iv, ob_rate_noIV_iv, "x", color='k',label = None)
        if line == 0:
            ax1.plot(line_x, prefect_line_y, '--', label="完美", color="k")
            ax1.plot(line_x, climate_line_y, ':', label="无技巧", color="k")
        ax1.plot(x, ob_rate, marker=".", markersize="10", color=color_list[line],label = None)

        x1 = x + (line -legend_num / 2 + 0.5) * bar_width
        total_hap = np.sum(observed_grade_num)
        hfmc = np.zeros((len(total_grade_num), 4))
        for i in range(ngrade):
            hfmc[i, 0] = np.sum(observed_grade_num[i:])
            hfmc[i, 1] = np.sum(total_grade_num[i:]) - hfmc[i, 0]
            hfmc[i, 2] = total_hap - hfmc[i, 0]
            hfmc[i, 3] = total_num - (hfmc[i, 0] + hfmc[i, 1] + hfmc[i, 2])

        far = [1]
        far.extend(pofd_hfmc(hfmc).tolist())
        far.append(0)
        pod = [1]
        pod.extend(pod_hfmc(hfmc).tolist())
        pod.append(0)
        far = np.array(far)
        pod = np.array(pod)

        if line == 0:
            ax3.plot([0, 1], [0, 1], ":", color="k", linewidth=1, label="无技巧")
        ax3.plot(far, pod, color=color_list[line], linewidth=2, label=label[line])
        #ax4.bar(x1, observed_grade_num, width=bar_width*0.8, color=color_list[line],label = label[line])
        ax4.bar(x1, (not_observed_grade_num+ observed_grade_num), width=bar_width*0.8,edgecolor=color_list[line],label =label[line])

        ax4.set_xlabel("预测的概率",fontsize= sup_fontsize *0.9)
        ax4.set_ylabel("样本数",fontsize= sup_fontsize *0.9)
        ymax = max(np.max(observed_grade_num+not_observed_grade_num), ymax)
        mark_line_x.append(x1)
        mark_line_y.append((not_observed_grade_num+ observed_grade_num)* x)

    ax1.set_xlim(0.0, 1)
    ax1.set_ylim(0.0, 1)
    ax1.set_xlabel("预测的概率",fontsize= sup_fontsize *0.9)
    ax1.set_ylabel("实况的发生比例",fontsize= sup_fontsize *0.9)
    ax1.legend(loc=2,fontsize= sup_fontsize *0.9)
    ax3.set_xlabel("空报率",fontsize= sup_fontsize *0.9)
    ax3.set_ylabel("命中率",fontsize= sup_fontsize *0.9)
    ax3.set_ylim(0.0, 1.0)
    ax3.set_xlim(0.0, 1.0)
    ax3.legend(loc=4,fontsize= sup_fontsize *0.9)
    ax4.set_xlim(0.0, 1)
    ax4.set(title='\n')
    ax4.set_xticks(np.arange(0,1.01,1/grade_count))
    #ax4.legend(loc="upper right", ncol=2)

    #mark_line_x = np.array(mark_line_x)
    #mark_line_y = np.array(mark_line_y)
    #mark_line_x = mark_line_x.T.flatten()
    #mark_line_y = mark_line_y.T.flatten()
    #ax4.plot(mark_line_x, mark_line_y, '.', color='k',markersize = bar_width * 300)
    #lines = ax4.get_children()
    #ax4.legend([lines[0], lines[grade_count],lines[grade_count * legend_num * 2 ]], ['观测正例', '观测负例',"合理比例"],
    #                     loc='upper center', bbox_to_anchor=(0.5, 1.0), ncol=3, prop={'size': 6},fontsize= sup_fontsize *0.9)

    if log_y: ax4.set_yscale('log')
    if vmax is None:
        ax4.set_ylim(0.0, ymax * 1.5)
    else:
        ax4.set_ylim(0.0, vmax)
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()
