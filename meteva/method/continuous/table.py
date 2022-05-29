import pandas as pd
import numpy as np
import copy

def accumulation_strenght_table(ob,fo, member_list = None,save_path=None):
    '''

    :param ob:
    :param fo:
    :param grade_list:
    :param save_path:
    :param member_list:
    :return:
    '''

    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])

    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    if member_list is None:
        label = ["观测"]
        if new_Fo_shape[0] <= 1:
            label.append('预报')
        else:
            for i in range(new_Fo_shape[0]):
                label.append('预报' + str(i + 1))
    else:
        label = member_list

    max_ob = np.max(ob)
    max_fo = np.max(fo)
    max_value = max(max_ob,max_fo)+2
    grade_list = np.arange(1,max_value,1).tolist()

    index_list = ["(0," + str(grade_list[0])+")"]
    for index in range(len(grade_list) - 1):
        index_list.append("[" + str(grade_list[index]) + "," + str(grade_list[index + 1]) + ")")
    index_list.append(">=" + str(grade_list[-1]))
    conf_mx = np.zeros((len(label), len(index_list)))

    for line in range(new_Fo_shape[0]):
        fo_piece = new_Fo[line, :]
        if grade_list is not None:
            gle = [-1e300]
            gle.extend(grade_list)
            gle.append(1e300)
            for i in range(len(gle) - 1):
                if line == 0:
                    ob_index_list = np.where((ob >= gle[i]) & (ob < gle[i + 1]))
                    ob_part = ob[ob_index_list]
                    conf_mx[0, i] = np.sum(ob_part)
                fo_index_list = np.where((fo_piece >= gle[i]) & (fo_piece < gle[i + 1]))
                fo_part = fo_piece[fo_index_list]
                conf_mx[line + 1, i] = np.sum(fo_part)

    if save_path is not None:
        table_data = pd.DataFrame(conf_mx.T,
                                  index=pd.MultiIndex.from_product([['类别'], index_list]),
                                  columns=pd.MultiIndex.from_product([['ob-fo'], label])
                                  )
        table_data.to_excel(save_path, sheet_name='sheet1')
        print("累计降水量随强度变化表已以excel表格形式保存至" + save_path)
    return conf_mx


def frequency_strenght_table(ob,fo, member_list = None,save_path=None):
    '''

    :param ob:
    :param fo:
    :param grade_list:
    :param save_path:
    :param member_list:
    :return:
    '''

    Fo_shape = fo.shape
    Ob_shape = ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])

    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    if member_list is None:
        label = ["观测"]
        if new_Fo_shape[0] <= 1:
            label.append('预报')
        else:
            for i in range(new_Fo_shape[0]):
                label.append('预报' + str(i + 1))
    else:
        label = member_list

    max_ob = np.max(ob)
    max_fo = np.max(fo)
    max_value = max(max_ob,max_fo)+2
    grade_list = np.arange(1,max_value,1).tolist()

    index_list = ["(0," + str(grade_list[0])+")"]
    for index in range(len(grade_list) - 1):
        index_list.append("[" + str(grade_list[index]) + "," + str(grade_list[index + 1]) + ")")
    index_list.append(">=" + str(grade_list[-1]))
    conf_mx = np.zeros((len(label), len(index_list)))

    for line in range(new_Fo_shape[0]):
        fo_piece = new_Fo[line, :]
        if grade_list is not None:
            gle = [-1e300]
            gle.extend(grade_list)
            gle.append(1e300)
            for i in range(len(gle) - 1):
                if line == 0:
                    ob_index_list = np.where((ob >= gle[i]) & (ob < gle[i + 1]))
                    ob_part = ob[ob_index_list]
                    conf_mx[0, i] = ob_part.size
                fo_index_list = np.where((fo_piece >= gle[i]) & (fo_piece < gle[i + 1]))
                fo_part = fo_piece[fo_index_list]
                conf_mx[line + 1, i] = fo_part.size

    if save_path is not None:
        table_data = pd.DataFrame(conf_mx.T,
                                  index=pd.MultiIndex.from_product([['类别'], index_list]),
                                  columns=pd.MultiIndex.from_product([['ob-fo'], label])
                                  )
        table_data.to_excel(save_path, sheet_name='sheet1')
        print("降水频次随强度变化表已以excel表格形式保存至" + save_path)
    return conf_mx

