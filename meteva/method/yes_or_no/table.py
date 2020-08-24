import sklearn
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import copy
import numpy as np
import pandas as pd

def contingency_table_yesorno(ob, fo, grade_list=[1e-30],compair = ">=",member_list=None,  save_path=None):
    '''
    contingency_table 预测列联表
    :param ob: 实况数据 任意维numpy数组
    :param fo: 预测数据 任意维numpy数组
    :param grade_list: grade_list: 多个阈值同时检验时的等级参数
    :param save_path: 保存地址，如果保存地址不为空时会将列联表输出到excel，
    其中每一个sheet为一个等级的列联表
    :return: 返回一个列表，列表中的元素为一个阈值条件下，观测-预报列联表
    '''
    if compair not in [">=",">","<","<="]:
        print("compair 参数只能是 >=   >  <  <=  中的一种")
        return
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
    label = []
    if member_list is None:
        if new_Fo_shape[0] == 1:
            label.append('预报')
        else:
            for i in range(new_Fo_shape[0]):
                label.append('预报' + str(i + 1))
    else:
        label.extend(member_list)
    grade_name_list = ['grade=' + str(i) for i in grade_list]
    conf_mx_list = []
    table_data_list = []
    for line in range(new_Fo_shape[0]):

        fo_piece = new_Fo[line, :]

        for grade in grade_list:
            shape = ob.shape
            new_ob = np.zeros(shape)
            new_fo = np.zeros(shape)
            index_list = ["No"]

            if compair == ">=":
                ob_index_list = np.where(ob >= grade)
                fo_index_list = np.where(fo_piece >= grade)
            elif compair == "<=":
                ob_index_list = np.where(ob <= grade)
                fo_index_list = np.where(fo_piece <= grade)
            elif compair == ">":
                ob_index_list = np.where(ob > grade)
                fo_index_list = np.where(fo_piece > grade)
            elif compair == "<":
                ob_index_list = np.where(ob < grade)
                fo_index_list = np.where(fo_piece < grade)

            new_ob[ob_index_list] = 1
            new_fo[fo_index_list] = 1
            index_list.append("Yes")

            new_fo = new_fo.flatten()
            new_ob = new_ob.flatten()
            conf_mx = confusion_matrix(new_fo, new_ob)
            if conf_mx.shape[0] < 2:
                # 说明全都发生或全都不发生
                num = len(new_ob)
                conf_mx = np.zeros((2, 2))
                if new_ob[0] == 0:
                    conf_mx[0, 0] = num
                else:
                    conf_mx[1, 1] = num

            row_sums = conf_mx.sum(axis=1, keepdims=True)
            conf_mx = np.hstack((conf_mx, row_sums))
            line_sums = conf_mx.sum(axis=0, keepdims=True)
            conf_mx = np.vstack((conf_mx, line_sums))
            index_list.append('sum')
            conf_mx_list.append(conf_mx)
            if save_path is not None:
                table_data = pd.DataFrame(conf_mx,
                                          columns=pd.MultiIndex.from_product([['观测'], index_list]),
                                          index=pd.MultiIndex.from_product([['预报'], index_list])
                                          )
                table_data_list.append(table_data)

    if save_path is not None:
        with pd.ExcelWriter(save_path) as writer:
            for i in range(len(table_data_list)):
                a = int(i / len(grade_name_list))
                b = i%len(grade_name_list)

                table_data_list[i].to_excel(writer, sheet_name=label[a]+'_'+grade_name_list[b])
        print("列联表已以excel表格形式保存至" + save_path)
    result = np.array(conf_mx_list)
    if new_Fo_shape[0]>1:
        result = result.reshape(new_Fo_shape[0],len(grade_list),3,3)
    return result

def performance_hfmc(hfmc_array, axis_list_list, suplot_lengend=[1, 0], save_dir=None):
    pass
    '''
    :param ob:
    :param fo:
    :param grade_list:
    :return:

    grade_count = len(grade_list)
    group_count = len(group_list)
    if grade_count == 1:
        #只有一种等级的
        pass
    elif group_list == 1:
        pass
    else:
        pass



    if grade_count == 1 or group_count == 1:
        column = 1
        row = 1
        if grade_count == 1:
            legend_list = group_list
        else:
            legend_list = grade_list
        subplot_count = 1
    else:
        column = 2
        row = int(math.ceil(grade_count/2))
        legend_list = group_list
        subplot_count = grade_count

    plt.figure(figsize=(column * 5, row * 4.5))
    plt.subplots_adjust(wspace = 0.5,hspace = 0.3)

    pod = pod_hfmc(hfmc_array)
    sr = sr_hfmc(hfmc_array)
    x = np.arange(0.0001, 1, 0.0001)
    bias_list = [0.2, 0.4, 0.6, 0.8, 1, 1.25, 1.67, 2.5, 5]
    ts_list = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


    for s in range(subplot_count):
        plt.subplot(column, row, s+1)
        for i in range(len(bias_list)):
            bias = bias_list[i]
            y1 = bias * x
            x2 = x[y1 < 1]
            y2 = y1[y1 < 1]
            if bias < 1:
                plt.plot(x2, y2, '--', color='k', linewidth=0.5)
                plt.text(1.01, bias, "bias=" + str(bias))
            elif bias > 1:
                plt.plot(x2, y2, '--', color='k', linewidth=0.5)
                plt.text(1.0 / bias - 0.05, 1.02, "bias=" + str(bias))
            else:
                plt.plot(x2, y2, '-', color='k', linewidth=0.5)

        for i in range(len(ts_list)):
            ts = ts_list[i]
            hf = 1
            x2 = np.arange(ts, 1, 0.001)
            hit = hf * x2
            hfm = hit / ts
            m = hfm - hf
            y2 = hit / (hit + m)
            plt.plot(x2, y2, "--", color="y", linewidth=0.5)
            error = np.abs(y2 - x2)
            index = np.argmin(error)
            sx = x2[index] + 0.02
            sy = y2[index] - 0.02
            plt.text(sx, sy, "ts=" + str(ts))

        colors = cm.get_cmap('rainbow', 128)
        for i in range(sr.shape[0]):
            color_grade = (i +0.5) /len(legend_list)
            plt.plot(sr[i,s], pod[i,s], 'o', color=colors(color_grade),markersize=12,label = legend_list[i])

        plt.xlim(0, 1)
        plt.ylim(0, 1)
        plt.xlabel("成功率",fontsize = 14)
        plt.ylabel("命中率",fontsize = 14)


    if len(legend_list) < 10:
        legend_ncol = len(legend_list)
    else:
        legend_ncol = int(math.ceil(len(legend_list)/2))
    plt.legend(loc='upper center', bbox_to_anchor=(0, -0.05,1,1),ncol = legend_ncol,bbox_transform=plt.gcf().transFigure)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)
    '''


