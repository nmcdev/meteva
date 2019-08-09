from sklearn.metrics import confusion_matrix

import pandas as pd
import numpy as np

from sklearn.linear_model import LinearRegression


def multi_category_contingency_table(ob, fo, grade_list=None, save_path='multi_category_contingency_table.xls',
                                     sheet_name='Sheet1'):
    '''
    multi_category_contingency_table 多分类预测列联表
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :param save_path: 保存地址
    :return:
    '''
    if grade_list is not None:
        for index in range(len(grade_list) - 2):
            ob_index_list = np.where((grade_list[index] <= ob) & (ob < grade_list[index + 1]))
            ob[ob_index_list] = grade_list[index]
            fo_index_list = np.where((grade_list[index] <= fo) & (fo < grade_list[index + 1]))
            fo[fo_index_list] = grade_list[index]
        # 此处需修改

    # 通过threshold_list给出的等级划分标准，将ob0，fo0 划分成各个等级

    conf_mx = confusion_matrix(ob, fo)
    row_sums = conf_mx.sum(axis=1, keepdims=True)
    conf_mx = np.hstack((conf_mx, row_sums))
    line_sums = conf_mx.sum(axis=0, keepdims=True)
    conf_mx = np.vstack((conf_mx, line_sums))

    index = list(set(np.hstack((ob, fo))))
    index.append('sum')

    table_data = pd.DataFrame(conf_mx,
                              columns=pd.MultiIndex.from_product([['fo'], index]),
                              index=pd.MultiIndex.from_product([['ob'], index])
                              )
    table_data.to_excel(save_path, sheet_name=sheet_name)
