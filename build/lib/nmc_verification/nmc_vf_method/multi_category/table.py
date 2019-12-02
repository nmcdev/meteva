from sklearn.metrics import confusion_matrix

import pandas as pd
import numpy as np
import copy
from sklearn.linear_model import LinearRegression



def contingency_table(ob, fo, grade_list=None, save_path=None):
    '''
    multi_category_contingency_table 多分类预测列联表
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :param save_path: 保存地址
    :return:
    '''

    if grade_list is not None:
        ngrade = len(grade_list) + 1
        conf_mx = np.zeros((ngrade, ngrade))
        gle = [-1e300]
        gle.extend(grade_list)
        gle.append(1e300)
        for i in range(len(gle) - 1):
            ob_index_list = np.where((ob >= gle[i]) & (ob < gle[i+ 1 ]))
            fo1 = fo[ob_index_list]
            for j in range(len(gle)- 1 ):
                fo_index_list = np.where((fo1 >= gle[j]) & (fo1< gle[j+ 1]))
                conf_mx[i,j ] = len(fo_index_list[0])

        index_list = ["<" + str(grade_list[0])]
        for index in range(len(grade_list) - 1):
            index_list.append("[" + str(grade_list[index]) + "," + str(grade_list[index + 1]) + ")")
        index_list.append(">=" + str(grade_list[-1]))
    else:
        new_fo = copy.deepcopy(fo).flatten()
        new_ob = copy.deepcopy(ob).flatten()
        index_list = list(set(np.hstack((new_ob, new_fo))))
        conf_mx = confusion_matrix(new_fo, new_ob)
    row_sums = conf_mx.sum(axis=1, keepdims=True)
    conf_mx = np.hstack((conf_mx, row_sums))
    line_sums = conf_mx.sum(axis=0, keepdims=True)
    conf_mx = np.vstack((conf_mx, line_sums))
    index_list.append('sum')
    if save_path is not None:
        table_data = pd.DataFrame(conf_mx,
                                  columns=pd.MultiIndex.from_product([['观测'], index_list]),
                                  index=pd.MultiIndex.from_product([['预报'], index_list])
                                  )
        print(save_path)
        table_data.to_excel(save_path, sheet_name='sheet1')
    return conf_mx


def hap_num_table(ob,fo, grade_list=None, save_path=None):
    '''
    contingency_table 多分类各等级发生样本数
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :param save_path: 保存地址
    :return:
    '''
    '''
    multi_category_contingency_table 多分类预测列联表
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :param save_path: 保存地址
    :return:
    '''

    if grade_list is not None:
        ngrade = len(grade_list) + 1
        conf_mx = np.zeros((2, ngrade))
        gle = [-1e300]
        gle.extend(grade_list)
        gle.append(1e300)
        for i in range(len(gle) - 1):
            ob_index_list = np.where((ob >= gle[i]) & (ob < gle[i+ 1 ]))
            conf_mx[0,i] = len(ob_index_list[0])
            fo_index_list = np.where((fo >= gle[i]) & (fo < gle[i + 1]))
            conf_mx[1, i] = len(fo_index_list[0])
        index_list = ["<" + str(grade_list[0])]
        for index in range(len(grade_list) - 1):
            index_list.append("[" + str(grade_list[index]) + "," + str(grade_list[index + 1]) + ")")
        index_list.append(">=" + str(grade_list[-1]))
    else:
        new_fo = copy.deepcopy(fo).flatten()
        new_ob = copy.deepcopy(ob).flatten()
        index_list = list(set(np.hstack((new_ob, new_fo))))
        conf_mx = np.zeros((2, len(index_list)))
        for i in range(len(index_list)):
            ob_index_list = np.where(ob == index_list[i])
            conf_mx[0,i] = len(ob_index_list[0])
            fo_index_list = np.where(fo == index_list[i])
            conf_mx[1, i] = len(fo_index_list[0])

    if save_path is not None:
        table_data = pd.DataFrame(conf_mx,
                                  columns=pd.MultiIndex.from_product([['类别'], index_list]),
                                  index=pd.MultiIndex.from_product([['ob-fo'], ["观测","预报"]])
                                  )
        print(save_path)
        table_data.to_excel(save_path, sheet_name='sheet1')
    return conf_mx