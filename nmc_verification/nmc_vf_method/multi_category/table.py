from sklearn.metrics import confusion_matrix

import pandas as pd
import numpy as np
import copy
from sklearn.linear_model import LinearRegression


def multi_category_contingency_table(ob, fo, grade_list=None, save_path='mult_category_contingency_table.xls',
                                     is_append_sheet=False, sheet_name='sheet1', excel_writer=None):
    # sheet_name = 'sheet'
    '''
    multi_category_contingency_table 多分类预测列联表
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :param save_path: 保存地址
    :return:
    '''

    if grade_list is not None:
        shape = ob.shape
        new_ob = np.zeros(shape, dtype=np.int64)
        new_fo = np.zeros(shape, dtype=np.int64)
        for index in range(len(grade_list) - 1):
            ob_index_list = np.where((grade_list[index] <= ob) & (ob < grade_list[index + 1]))
            new_ob[ob_index_list] = index
            fo_index_list = np.where((grade_list[index] <= fo) & (fo < grade_list[index + 1]))
            new_fo[fo_index_list] = index

        ob_index_list = np.where(grade_list[-1] <= ob)
        new_ob[ob_index_list] = index + 1
        fo_index_list = np.where(grade_list[-1] <= fo)
        new_fo[fo_index_list] = index + 1
        fo = new_fo
        ob = new_ob
    index = list(set(np.hstack((ob, fo))))

    conf_mx = confusion_matrix(ob, fo)
    row_sums = conf_mx.sum(axis=1, keepdims=True)
    conf_mx = np.hstack((conf_mx, row_sums))
    line_sums = conf_mx.sum(axis=0, keepdims=True)
    conf_mx = np.vstack((conf_mx, line_sums))
    index.append('sum')
    table_data = pd.DataFrame(conf_mx,
                              columns=pd.MultiIndex.from_product([['fo'], index]),
                              index=pd.MultiIndex.from_product([['ob'], index])
                              )
    if not is_append_sheet:
        table_data.to_excel(save_path, sheet_name=sheet_name)
    else:
        print('sheet_name:',sheet_name)
        # print(excel_writer)
        table_data.to_excel(excel_writer=excel_writer, sheet_name=str(sheet_name))
        excel_writer.save()
