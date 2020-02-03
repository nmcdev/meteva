import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
from nmc_verification.nmc_vf_method.yes_or_no.score import pofd_hfmc,pod_hfmc
from nmc_verification.nmc_vf_base.tool.plot_tools import set_plot_IV
from nmc_verification.nmc_vf_base import IV


def hnh(Ob,Fo,grade_count = 10):
    '''

    :param Ob:
    :param Fo:
    :param grade_count:
    :return:
    '''
    grade = 1/grade_count
    grade_list = np.arange(0,1,grade).tolist()
    grade_list.append(1.1)
    th_list = []
    for g in range(len(grade_list)-1):
        index = np.where((Fo>=grade_list[g]) & (Fo < grade_list[g+1]))
        ob1 = Ob[index]
        ob2 = ob1[ob1>0]
        th_list.append([ob1.size,ob2.size])
    hnh_array = np.array(th_list)
    return hnh_array

def reliability(Ob, Fo,grade_count = 10, save_path=None,title = "可靠性图"):
    '''
    :param Ob:
    :param Fo:
    :param save_path:
    :return:
    '''
    hnh_array = hnh(Ob,Fo,grade_count)
    reliability_hnh(hnh_array,save_path,title = title)

def reliability_hnh(hnh_array,save_path = None,title = "可靠性图"):
    '''
    根据中间结果计算
    :param th:
    :param save_path:
    :return:
    '''
    total_grade_num = hnh_array[:,0]
    observed_grade_num = hnh_array[:,1]
    ngrade = len(total_grade_num)
    grade = 1/ngrade
    total_num = np.sum(total_grade_num)
    under = np.zeros_like(total_grade_num)
    under[:] = total_grade_num[:]
    under[total_grade_num == 0] = 1
    ob_rate = observed_grade_num /under
    ob_rate[total_grade_num == 0] = IV
    ob_rate_noIV = set_plot_IV(ob_rate)
    ob_rate[total_grade_num == 0] = np.nan
    index_iv = np.where(total_grade_num == 0)
    line_x = np.arange(0,1.00,grade)
    prefect_line_y = np.arange(0,1.00,grade)
    climate_line_y = np.ones_like(line_x) * np.sum(observed_grade_num)/total_num
    x = np.arange(grade/2,1,grade)
    fig = plt.figure(figsize=(5,5.1))
    grid_plt = plt.GridSpec(5,1,hspace=0)
    ax1 = plt.subplot(grid_plt[0:4,0])
    plt.plot(x,ob_rate_noIV,"--",linewidth = 0.5,color = "k")
    x_iv = x[index_iv[0]]
    ob_rate_noIV_iv = ob_rate_noIV[index_iv[0]]
    plt.plot(x_iv,ob_rate_noIV_iv,"x",color = 'k')
    plt.plot(x,ob_rate,marker = ".",markersize = "10",label = "实际预报",color = "r")
    plt.plot(line_x,prefect_line_y,'--',label = "完美预报",color = "k")
    plt.plot(line_x, climate_line_y, ':', label="无技巧预报",color = "k")
    plt.setp(ax1.get_xticklabels(),visible=False)
    plt.ylim(0.0, 1)
    plt.ylabel("实况的发生比例")
    plt.legend(loc=2)
    plt.title(title)
    ax2 = plt.subplot(grid_plt[4,0], sharex=ax1)
    plt.bar(x, total_grade_num,width=0.03)
    #plt.setp(ax2.get_xticklabels())

    plt.ylabel("样本数")
    plt.xlim(0.0, 1.0)
    plt.xticks(np.arange(0.1,1.01,0.1))
    plt.xlabel("预测的概率")

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        print("检验结果已以图片形式保存至" + save_path)
    plt.close()

def roc(Ob, Fo,grade_count = 10,save_path = None,title = "ROC图"):
    '''

    :param Ob:
    :param Fo:
    :param grade_count:
    :param save_path:
    :return:
    '''
    hnh_array = hnh(Ob,Fo,grade_count)
    roc_hnh(hnh_array,save_path,title)

def roc_hfmc(hfmc,save_path =None,title = "ROC图"):
    '''

    :param hfmc:
    :param save_path:
    :return:
    '''
    fig = plt.figure(figsize=(5.6, 5.6))
    far = [1]
    far.extend(pofd_hfmc(hfmc).tolist())
    far.append(0)
    pod = [1]
    pod.extend(pod_hfmc(hfmc).tolist())
    pod.append(0)
    far = np.array(far)
    pod = np.array(pod)
    if(far.size <30):
        plt.plot(far, pod, color="blue", linewidth=2, marker = ".",label="实际预报")
    else:
        plt.plot(far, pod, color="blue", linewidth=2, label="实际预报")
    plt.plot([0, 1], [0, 1],  ":",color="k",linewidth=1,label = "无技巧预报")
    plt.xlabel("空报率",fontsize = 14)
    plt.ylabel("命中率",fontsize = 14)
    plt.ylim(0.0, 1.0)
    plt.xlim(0.0, 1.0)
    plt.legend(loc=4,fontsize = 14)
    plt.title(title,fontsize = 14)
    plt.xticks(fontsize = 14)
    plt.yticks(fontsize=14)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        print("检验结果已以图片形式保存至" + save_path)
    plt.close()

def roc_hnh(hnh_array,save_path = None,title = "ROC图"):
    '''

    :param th_array:
    :param save_path:
    :return:
    '''
    total_grade_num = hnh_array[:,0]
    observed_grade_num = hnh_array[:,1]
    ngrade = len(total_grade_num)
    hfmc = np.zeros((len(total_grade_num),4))
    total_hap = np.sum(observed_grade_num)
    total_num = np.sum(total_grade_num)
    for i in range(ngrade):
        hfmc[i, 0] = np.sum(observed_grade_num[i:])
        hfmc[i, 1] = np.sum(total_grade_num[i:]) - hfmc[i, 0]
        hfmc[i, 2] = total_hap - hfmc[i, 0]
        hfmc[i, 3]= total_num - (hfmc[i, 0] + hfmc[i, 1]+ hfmc[i, 2])

    roc_hfmc(hfmc, save_path,title)

def discrimination(Ob,Fo,grade_count = 10,save_path=None,title = "区分能力图"):
    '''

    :param Ob:
    :param Fo:
    :param grade_count:
    :param save_path:
    :return:
    '''
    hnh_array = hnh(Ob,Fo,grade_count)
    discrimination_hnh(hnh_array,save_path,title)

def discrimination_hnh(th_array,save_path = None,title = "区分能力图"):
    '''

    :param th_array:
    :param save_path:
    :return:
    '''
    total_grade_num = th_array[:,0]
    observed_grade_num = th_array[:,1]
    total_num = np.sum(total_grade_num)
    observed_grade_rate = observed_grade_num/total_num
    not_observed_grade_num = total_grade_num - observed_grade_num
    not_observed_grade_rate = not_observed_grade_num/total_num
    ngrade = len(total_grade_num)
    grade = 1/ngrade
    x = np.arange(grade / 2, 1, grade)


    width = 8
    height = 6
    fig = plt.figure(figsize=(width, height))
    bar_width = 0.1/len(x)
    plt.bar(x-bar_width,not_observed_grade_rate,width=2*bar_width,edgecolor = 'r',fill = False,label = "未发生")
    plt.bar(x+bar_width,observed_grade_rate,width=2*bar_width,color = 'b',label = "已发生")
    plt.xlabel("预测的概率",fontsize = 14)
    plt.ylabel("占总样本数的比例",fontsize = 14)
    ymax = max(np.max(observed_grade_rate),np.max(not_observed_grade_rate))* 1.4
    plt.ylim(0.0, ymax)
    plt.xlim(0.0, 1.0)
    plt.legend(loc=1)
    plt.yticks(fontsize = 14)
    xtick = np.arange(0,1.001,0.1)
    plt.xticks(xtick,fontsize = 14)
    plt.title(title,fontsize = 14)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        print("检验结果已以图片形式保存至" + save_path)
    plt.close()

def comprehensive_probability(Ob,Fo,grade_count = 10,save_path = None,title = "概率预报综合检验图"):
    '''
    :param Ob:
    :param Fo:
    :param save_path:
    :return:
    '''
    hnh_array= hnh(Ob,Fo,grade_count)
    comprehensive_hnh(hnh_array,save_path,title)

def comprehensive_hnh(th_array,save_path = None,title = "概率预报综合检验图"):
    '''

    :param th_array:
    :param save_path:
    :return:
    '''
    total_grade_num = th_array[:, 0]
    observed_grade_num = th_array[:, 1]
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
    fig = plt.figure(figsize=(10, 7))
    title_lines = len(title.split("\n"))
    plt.suptitle(title,y = 0.90 + 0.03 * title_lines)
    plt.subplots_adjust(wspace=0.2, hspace=1)
    grid_plt = plt.GridSpec(6, 2)
    ax1 = plt.subplot(grid_plt[0:4, 0])
    plt.plot(x, ob_rate_noIV, "--", linewidth=0.5, color="k")
    x_iv = x[index_iv[0]]
    ob_rate_noIV_iv = ob_rate_noIV[index_iv[0]]
    plt.plot(x_iv, ob_rate_noIV_iv, "x", color='k')
    plt.plot(x, ob_rate, marker=".", markersize="10", label="实际预报", color="r")
    plt.plot(line_x, prefect_line_y, '--', label="完美预报", color="k")
    plt.plot(line_x, climate_line_y, ':', label="无技巧预报", color="k")
    plt.xlim(0.0, 1.0)
    plt.ylim(0.0, 1)
    plt.xlabel("预测的概率")
    plt.ylabel("实况的发生比例")
    plt.legend(loc=2)

    ax2 = plt.subplot(grid_plt[4:, 0])
    plt.bar(x, total_grade_num, width=0.03)
    #plt.setp(ax2.get_xticklabels())
    plt.xlim(0.0, 1.0)
    plt.ylabel("样本数")
    plt.xlabel("预测的概率")


    total_hap = np.sum(observed_grade_num)
    hfmc = np.zeros((len(total_grade_num), 4))
    for i in range(ngrade):
        hfmc[i, 0] = np.sum(observed_grade_num[i:])
        hfmc[i, 1] = np.sum(total_grade_num[i:]) - hfmc[i, 0]
        hfmc[i, 2] = total_hap - hfmc[i, 0]
        hfmc[i, 3]= total_num - (hfmc[i, 0] + hfmc[i, 1]+ hfmc[i, 2])

    far = [1]
    far.extend(pofd_hfmc(hfmc).tolist())
    far.append(0)
    pod = [1]
    pod.extend(pod_hfmc(hfmc).tolist())
    pod.append(0)
    far = np.array(far)
    pod = np.array(pod)

    ax3 = plt.subplot(grid_plt[0:4, 1])
    plt.plot(far, pod, color="blue", linewidth=2, label="实际预报")
    plt.plot([0, 1], [0, 1], ":", color="k", linewidth=1, label="无技巧预报")
    plt.xlabel("空报率")
    plt.ylabel("命中率")
    plt.ylim(0.0, 1.0)
    plt.xlim(0.0, 1.0)
    plt.legend(loc=4)

    ax4 = plt.subplot(grid_plt[4:, 1])
    plt.bar(x - 0.01, not_observed_grade_num/total_num, width=0.02, edgecolor='r', fill=False, label="未发生")
    plt.bar(x + 0.01, observed_grade_num/total_num, width=0.02, color='b', label="已发生")

    plt.xlabel("预测的概率")
    plt.ylabel("占总样本数的比例")
    ymax = max(np.max(observed_grade_num/total_num), np.max(not_observed_grade_num/total_num)) * 1.5
    plt.ylim(0.0, ymax)
    plt.xlim(0.0, 1.0)

    plt.legend(loc="upper right", ncol=2)

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        print("检验结果已以图片形式保存至" + save_path)
    plt.close()