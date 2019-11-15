import nmc_verification.nmc_vf_base.function.put_into_sta_data as pisd
import nmc_verification
from sklearn.metrics import confusion_matrix
import nmc_verification.nmc_vf_method.multi_category.table as table
import string
import pandas as pd
import numpy as np
import pathlib


def multi_mode_and_multi_classification_predictive_contingency_table(ob, fo_list, grade_list=None, save_path=None):
    '''

    :param ob:一个实况数据  类型  dataframe
    :param fo_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :param grade_list:等级  列表list
    :param save_path: 保存地址
    :return:
    '''
    fo_list.append(ob)
    meger_df_data = pisd.merge_on_id_and_obTime(fo_list)
    ob_data = meger_df_data.iloc[:, -1]
    ob_data = ob_data.values
    colnums = ['level', 'id', 'time']
    title = ''
    for colnum in colnums:
        the_duplicate_values = meger_df_data[colnum].unique()
        if len(the_duplicate_values) == 1:
            title = title + str(the_duplicate_values[0])
    if ':' in title:
        title = title[:-13]
        title = title.translate(str.maketrans(':', ':', string.punctuation))
    if save_path is None:
        save_path = title + '.xlsx'
    else:
        save_path = save_path + '/' + title + '.xlsx'

    pathlib.Path(save_path).touch()
    writer = pd.ExcelWriter(save_path)
    for fo_of_colnum in meger_df_data.iloc[:, 7:-1]:
        fo_of_data = meger_df_data[fo_of_colnum].values
        table.multi_category_contingency_table(ob_data, fo_of_data, grade_list=grade_list, is_append_sheet=True,
                                               excel_writer=writer, sheet_name=fo_of_colnum, )
        # multi_category_contingency_table(ob_data, fo_of_data, writer, fo_of_colnum, grade_list=grade_list)
    writer.close()

