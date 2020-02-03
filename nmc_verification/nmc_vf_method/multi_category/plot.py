import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import copy

def frequency_histogram(ob, fo,grade_list = None, save_path=None,title = "频率统计图"):
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
    total_num = ob.size

    if grade_list is not None:

        shape = ob.shape
        new_ob = np.zeros(shape)
        new_fo = np.zeros(shape)
        index_list =["<" + str(grade_list[0])]
        ob_index_list = np.where(ob<grade_list[0])
        ob_num_list = [len(ob_index_list[0])]
        fo_index_list = np.where(fo < grade_list[0])
        fo_num_list = [len(fo_index_list[0])]
        for index in range(len(grade_list) - 1):
            ob_index_list = np.where((grade_list[index] <= ob) & (ob < grade_list[index + 1]))
            ob_num_list.append(len(ob_index_list[0]))
            fo_index_list = np.where((grade_list[index] <= fo) & (fo < grade_list[index + 1]))
            fo_num_list.append(len(fo_index_list[0]))
            index_list.append("["+str(grade_list[index]) + "," + str(grade_list[index+1]) + ")")
        ob_index_list = np.where(grade_list[-1] <= ob)
        ob_num_list.append(len(ob_index_list[0]))
        fo_index_list = np.where(grade_list[-1] <= fo)
        fo_num_list.append(len(fo_index_list[0]))
        index_list.append(">=" + str(grade_list[-1]))

    else:
        new_fo = copy.deepcopy(fo).flatten()
        new_ob = copy.deepcopy(ob).flatten()
        index_list = list(set(np.hstack((new_ob, new_fo))))
        ob_num_list = []
        fo_num_list = []
        for i in range(len(index_list)):
            ob_index_list = np.where(ob == index_list[i])
            ob_num_list.append(len(ob_index_list[0]))
            fo_index_list = np.where(fo == index_list[i])
            fo_num_list.append(len(fo_index_list[0]))

    #计算最大的横坐标字符串
    max_str_len = 1
    for index in index_list:
        if max_str_len <len(index):
            max_str_len = len(index)
    #print(max_str_len)
    width = 0.5 + (1+ max_str_len)* 0.1 * len(index_list)
    height = 6
    fig = plt.figure(figsize=(width, height))

    p_ob = np.array(ob_num_list)/total_num
    p_fo = np.array(fo_num_list)/total_num
    x = np.arange(len(index_list))
    plt.bar(x + 0.1, p_ob, width=0.2, facecolor="r", label="观测")
    plt.bar(x - 0.1, p_fo, width=0.2, facecolor="b", label="预报")
    plt.legend()
    plt.xlabel("类别", fontsize=14)



    plt.xticks(x,index_list,fontsize = 12)
    plt.yticks(fontsize = 14)
    plt.ylabel("样本占比", fontsize=14)
    plt.title(title,fontsize = 14)
    ymax = max(np.max(p_ob),np.max(p_fo))* 1.4
    plt.ylim(0.0, ymax)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
        print("检验结果已以图片形式保存至" + save_path)
    plt.close()


