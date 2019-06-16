import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


def frequency_histogram(ob, fo, grade_list = None,save_path = None, x_lable='frequency',
                        y_lable='range', left_label='Obs', right_label='Pred',
                        left_color='r', right_color='b', legend_location="upper right", width=0.2):

    if grade_list is None:
        #ob 和fo 的元素是分类预报的类别，需提取类别集合名称，然后以之为横坐标标注，绘制各类别的频率
        pass
    else:
        #ob 和fo 的元素是连续变量，通过grade_list 将其切割成不同等级，然后不同等级的频率
        pass

    p_ob = np.zeros(6)
    p_fo = np.zeros(6)
    x = np.arange(6)
    xticklabels = []
    for i in range(1, len(grade_list) - 1):
        index0 = np.where((ob > grade_list[i]) & (ob < grade_list[i + 1]))
        xticklabels.append(str(grade_list[i]) + '-' + str(grade_list[i + 1]))
        p_ob[i - 1] = len(index0[0]) / len(ob)
        index0 = np.where((fo > grade_list[i]) & (fo <grade_list[i + 1]))
        p_fo[i - 1] = len(index0[0]) / len(fo)
    xticklabels.append('>=' + str(grade_list[-1]))
    ax3 = plt.axes()
    ax3.bar(x + 0.25, p_ob, width=width, facecolor=left_color, label=left_label)
    ax3.bar(x - 0.05, p_fo, width=width, facecolor=right_color, label=right_label)
    ax3.legend(loc=legend_location)
    ax3.set_xlabel(x_lable, fontsize=10)
    ax3.set_xticks(x)
    ax3.set_xticklabels(xticklabels, fontsize=9)
    ax3.set_ylabel(y_lable, fontsize=10)
    ax3.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))


    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)


