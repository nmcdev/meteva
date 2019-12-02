import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_curve

def reliability(Ob, Fo,  save_path=None):
    '''
    :param Ob:
    :param Fo:
    :param save_path:
    :return:
    '''

    grade = np.arange(0,1.11,0.1)
    print(Fo)
    print(Ob)
    observed = Fo[Ob == 1]
    print(observed)
    not_observed = Fo[Ob ==0]
    print(not_observed)
    observed_grade_num =[len(observed[observed<grade[1]])]
    not_observed_grade_num = [len(not_observed[not_observed<grade[1]])]
    total_num = Ob.size
    for i in range(1,len(grade)-2):
        indexs = np.where((observed<grade[i+1]) & (observed >= grade[i]))
        observed_grade_num.append(len(indexs[0]))
        indexs = np.where((not_observed<grade[i+1]) & (not_observed >= grade[i]))
        not_observed_grade_num.append(len(indexs[0]))
    observed_grade_num = np.array(observed_grade_num)
    not_observed_grade_num = np.array(not_observed_grade_num)
    grade_num = observed_grade_num + not_observed_grade_num
    ob_rate = observed_grade_num/(grade_num+ 1e-30)
    line_x = np.arange(0,1.01,0.1)
    prefect_line_y = np.arange(0,1.01,0.1)
    climate_line_y = np.ones_like(line_x) * np.sum(observed_grade_num)/total_num

    x = np.arange(0.05,1,0.1)
    fig = plt.figure(figsize=(5,5))
    grid_plt = plt.GridSpec(5,1,hspace=0)

    ax1 = plt.subplot(grid_plt[0:4,0])
    plt.plot(x,ob_rate,marker = ".",markersize = "10",label = "实际预报",color = "r")
    plt.plot(line_x,prefect_line_y,'--',label = "完美预报",color = "k")
    plt.plot(line_x, climate_line_y, ':', label="无技巧预报",color = "k")
    plt.setp(ax1.get_xticklabels(),visible=False)

    plt.ylim(0.0, 1)
    plt.ylabel("实况的发生比例")

    plt.legend(loc=2)


    ax2 = plt.subplot(grid_plt[4,0], sharex=ax1)
    plt.bar(x, grade_num,width=0.03)
    plt.setp(ax2.get_xticklabels())

    plt.ylabel("样本数")
    plt.xlim(0.0, 1.0)
    plt.xlabel("预测的概率")

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)

def roc(Ob, Fo,save_path = None):
    fig = plt.figure(figsize=(5, 4))
    (fpr_dtree, tpr_dtree, thresholds_dtree) = roc_curve(Ob,Fo, pos_label=1)
    plt.plot(fpr_dtree, tpr_dtree, color="blue", linewidth=2, label="实际预报")
    plt.plot([0, 1], [0, 1],  ":",color="k",linewidth=1,label = "无技巧预报")
    plt.xlabel("空报率")
    plt.ylabel("命中率")
    plt.ylim(0.0, 1.0)
    plt.xlim(0.0, 1.0)
    plt.legend(loc=4)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
    pass

def discrimination(Ob,Fo,save_path=None):
    grade = np.arange(0,1.11,0.1)
    print(Fo)
    print(Ob)
    observed = Fo[Ob == 1]
    print(observed)
    not_observed = Fo[Ob ==0]
    print(not_observed)
    observed_grade_num =[len(observed[observed<grade[1]])]
    not_observed_grade_num = [len(not_observed[not_observed<grade[1]])]
    total_num = Ob.size
    for i in range(1,len(grade)-2):
        indexs = np.where((observed<grade[i+1]) & (observed >= grade[i]))
        observed_grade_num.append(len(indexs[0]))
        indexs = np.where((not_observed<grade[i+1]) & (not_observed >= grade[i]))
        not_observed_grade_num.append(len(indexs[0]))
    observed_grade_num = np.array(observed_grade_num)/total_num
    not_observed_grade_num = np.array(not_observed_grade_num)/total_num
    x = np.arange(0.05,1,0.1)
    plt.bar(x-0.01,not_observed_grade_num,width=0.02,edgecolor = 'r',fill = False,label = "未发生")
    plt.bar(x+0.01,observed_grade_num,width=0.02,color = 'b',label = "已发生")

    plt.xlabel("预测的概率")
    plt.ylabel("占总样本数的比例")
    ymax = max(np.max(observed_grade_num),np.max(not_observed_grade_num))* 1.4
    plt.ylim(0.0, ymax)
    plt.xlim(0.0, 1.0)
    plt.legend(loc=1)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
    pass

def comprehensive(Ob,Fo,save_path = None):
    '''
    :param Ob:
    :param Fo:
    :param save_path:
    :return:
    '''
    grade = np.arange(0,1.11,0.1)
    observed = Fo[Ob == 1]
    not_observed = Fo[Ob ==0]
    observed_grade_num =[len(observed[observed<grade[1]])]
    not_observed_grade_num = [len(not_observed[not_observed<grade[1]])]
    total_num = Ob.size
    for i in range(1,len(grade)-2):
        indexs = np.where((observed<grade[i+1]) & (observed >= grade[i]))
        observed_grade_num.append(len(indexs[0]))
        indexs = np.where((not_observed<grade[i+1]) & (not_observed >= grade[i]))
        not_observed_grade_num.append(len(indexs[0]))
    observed_grade_num = np.array(observed_grade_num)
    not_observed_grade_num = np.array(not_observed_grade_num)
    grade_num = observed_grade_num + not_observed_grade_num
    ob_rate = observed_grade_num/(grade_num+ 1e-30)
    line_x = np.arange(0,1.01,0.1)
    prefect_line_y = np.arange(0,1.01,0.1)
    climate_line_y = np.ones_like(line_x) * np.sum(observed_grade_num)/total_num

    x = np.arange(0.05,1,0.1)
    fig = plt.figure(figsize=(10,6))
    plt.subplots_adjust(wspace=0.2, hspace=1)
    grid_plt = plt.GridSpec(5,2)
    ax1 = plt.subplot(grid_plt[0:4,0])
    plt.plot(x,ob_rate,marker = ".",markersize = "10",label = "实际预报",color = "r")
    plt.plot(line_x,prefect_line_y,'--',label = "完美预报",color = "k")
    plt.plot(line_x, climate_line_y, ':', label="无技巧预报",color = "k")
    plt.xlim(0.0, 1.0)
    plt.ylim(0.0, 1)
    plt.xlabel("预测的概率")
    plt.ylabel("实况的发生比例")
    plt.legend(loc=2)

    ax2 = plt.subplot(grid_plt[4,0])
    plt.bar(x, grade_num,width=0.03)
    plt.setp(ax2.get_xticklabels())
    plt.xlim(0.0, 1.0)
    plt.ylabel("样本数")
    plt.xlabel("预测的概率")

    (fpr_dtree, tpr_dtree, thresholds_dtree) = roc_curve(Ob, Fo, pos_label=1)
    ax3 = plt.subplot(grid_plt[0:4,1])
    plt.plot(fpr_dtree, tpr_dtree, color="blue", linewidth=2, label="实际预报")
    plt.plot([0, 1], [0, 1], ":", color="k", linewidth=1, label="无技巧预报")
    plt.xlabel("空报率")
    plt.ylabel("命中率")
    plt.ylim(0.0, 1.0)
    plt.xlim(0.0, 1.0)
    plt.legend(loc=4)

    ax4 = plt.subplot(grid_plt[4, 1])
    plt.bar(x-0.01,not_observed_grade_num,width=0.02,edgecolor = 'r',fill = False,label = "未发生")
    plt.bar(x+0.01,observed_grade_num,width=0.02,color = 'b',label = "已发生")

    plt.xlabel("预测的概率")
    plt.ylabel("占总样本数的比例")
    ymax = max(np.max(observed_grade_num),np.max(not_observed_grade_num))* 2
    plt.ylim(0.0, ymax)
    plt.xlim(0.0, 1.0)
    plt.legend(loc=9,ncol=2)

    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
    pass

