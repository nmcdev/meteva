import sklearn
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import copy
import numpy as np
import pandas as pd

def contingency_table(ob, fo, grade_list=[1e-30], save_path=None):
    '''
    contingency_table 预测列联表
    :param ob: 实况数据 任意维numpy数组
    :param fo: 预测数据 任意维numpy数组
    :param grade_list: grade_list: 多个阈值同时检验时的等级参数
    :param save_path: 保存地址，如果保存地址不为空时会将列联表输出到excel，
    其中每一个sheet为一个等级的列联表
    :return: 返回一个列表，列表中的元素为一个阈值条件下，观测-预报列联表
    '''
    conf_mx_list = []
    table_data_list = []
    for grade in grade_list:
        shape = ob.shape
        new_ob = np.zeros(shape)
        new_fo = np.zeros(shape)
        index_list =["未发生"]
        ob_index_list = np.where(ob >= grade)
        new_ob[ob_index_list] = 1
        fo_index_list = np.where(fo >= grade)
        new_fo[fo_index_list] = 1
        index_list.append("发生")

        new_fo = new_fo.flatten()
        new_ob = new_ob.flatten()
        conf_mx = confusion_matrix(new_fo, new_ob)
        if conf_mx.shape[0] < 2:
            #说明全都发生或全都不发生
            num = len(new_ob)
            conf_mx = np.zeros((2, 2))
            if new_ob[0] == 0:
                conf_mx[0,0] = num
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
                                      columns=pd.MultiIndex.from_product([['ob'], index_list]),
                                      index=pd.MultiIndex.from_product([['fo'], index_list])
                                      )
            table_data_list.append(table_data)
    if save_path is not None:
        with pd.ExcelWriter(save_path) as writer:
            for i in range(len(table_data_list)):
                table_data_list[i].to_excel(writer, sheet_name='grade_'+str(grade_list[i]))

    return conf_mx_list

