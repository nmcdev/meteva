from sklearn.metrics import confusion_matrix
import pandas as pd
import numpy as np
import copy


def contingency_table_multicategory(ob, fo, grade_list=None,member_list=None,  save_path=None):
    '''
    multi_category_contingency_table 多分类预测列联表
    :param ob: 实况数据 任意维numpy数组
    :param fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 如果该参数为None，观测或预报值出现过的值都作为分类标记.
    如果该参数不为None，它必须是一个从小到大排列的实数，以其中列出的数值划分出的多个区间作为分类标签。
    对于预报和观测值不为整数的情况，grade_list 不能设置为None。
    :param save_path: 保存地址
    :return: 内容为混淆矩阵的二维数组，shape为（类别数 + 1）×（类别数 + 1）
    '''
    conf_mx_list = []
    table_data_list = []
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

    if grade_list is not None:
        index_list0 = ["<" + str(grade_list[0])]
        for index in range(len(grade_list) - 1):
            index_list0.append("[" + str(grade_list[index]) + "," + str(grade_list[index + 1]) + ")")
        index_list0.append(">=" + str(grade_list[-1]))
    else:
        new_fo = copy.deepcopy(fo).flatten()
        new_ob = copy.deepcopy(ob).flatten()
        fo_set = list(set(new_fo.tolist()))
        ob_set = list(set(new_ob.tolist()))
        fo_set.extend(ob_set)
        index_list0 = list(set(fo_set))
        index_list0.sort()
        if len(index_list0) > 30:
            print("自动识别的样本类别超过30种，判断样本为连续型变量，grade_list不能缺省")
            return
    for line in range(new_Fo_shape[0]):
        fo_piece = new_Fo[line, :]
        if grade_list is not None:
            ngrade = len(grade_list) + 1
            conf_mx = np.zeros((ngrade, ngrade))
            gle = [-1e300]
            gle.extend(grade_list)
            gle.append(1e300)
            for i in range(len(gle) - 1):
                ob_index_list = np.where((ob >= gle[i]) & (ob < gle[i + 1]))
                fo1 = fo_piece[ob_index_list]
                for j in range(len(gle) - 1):
                    fo_index_list = np.where((fo1 >= gle[j]) & (fo1 < gle[j + 1]))
                    conf_mx[j, i] = len(fo_index_list[0])
        else:
            ngrade = len(index_list0)
            conf_mx = np.zeros((ngrade, ngrade))
            for i in range(ngrade):
                ob_index_list = np.where(ob == index_list0[i])
                if(len(ob_index_list)==0):continue
                fo1 = fo_piece[ob_index_list]
                for j in range(ngrade):
                    fo_index_list = np.where(fo1 == index_list0[j])
                    conf_mx[j, i] = len(fo_index_list[0])
        row_sums = conf_mx.sum(axis=1, keepdims=True)
        conf_mx = np.hstack((conf_mx, row_sums))
        line_sums = conf_mx.sum(axis=0, keepdims=True)
        conf_mx = np.vstack((conf_mx, line_sums))
        index_list = copy.deepcopy(index_list0)
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
                table_data_list[i].to_excel(writer, sheet_name=label[i])
        print("列联表已以excel表格形式保存至" + save_path)
    result = np.array(conf_mx_list)
    result = result.squeeze()
    return result


def frequency_table(ob,fo,grade_list=None, member_list = None,save_path=None):
    '''

    :param ob:
    :param fo:
    :param grade_list:
    :param save_path:
    :param member_list:
    :return:
    '''

    conf_mx_list = []
    table_data_list = []
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
    label = ["观测"]
    if member_list is None:
        if new_Fo_shape[0] <= 1:
            label.append('预报')
        else:
            for i in range(new_Fo_shape[0]):
                label.append('预报' + str(i + 1))
    else:
        label.extend(member_list)

    if grade_list is None:
        new_fo = copy.deepcopy(fo).flatten()
        new_ob = copy.deepcopy(ob).flatten()
        # index_list = list(set(np.hstack((new_ob, new_fo))))
        fo_set = list(set(new_fo.tolist()))
        ob_set = list(set(new_ob.tolist()))
        fo_set.extend(ob_set)
        index_list = list(set(fo_set))
        if len(index_list) > 30:
            print("自动识别的样本类别超过30种，判断样本为连续型变量，grade_list不能缺省")
            return
    else:
        index_list = ["<" + str(grade_list[0])]
        for index in range(len(grade_list) - 1):
            index_list.append("[" + str(grade_list[index]) + "," + str(grade_list[index + 1]) + ")")
        index_list.append(">=" + str(grade_list[-1]))
    conf_mx = np.zeros((len(label), len(index_list)))
    for line in range(new_Fo_shape[0]):
        fo_piece = new_Fo[line, :]
        if grade_list is not None:
            ngrade = len(grade_list) + 1
            gle = [-1e300]
            gle.extend(grade_list)
            gle.append(1e300)
            for i in range(len(gle) - 1):
                if line == 0:
                    ob_index_list = np.where((ob >= gle[i]) & (ob < gle[i + 1]))
                    conf_mx[0, i] = len(ob_index_list[0])
                fo_index_list = np.where((fo_piece >= gle[i]) & (fo_piece < gle[i + 1]))
                conf_mx[line + 1, i] = len(fo_index_list[0])
        else:
            for i in range(len(index_list)):
                if line ==0:
                    ob_index_list = np.where(ob == index_list[i])
                    conf_mx[0, i] = len(ob_index_list[0])
                fo_index_list = np.where(fo_piece == index_list[i])
                conf_mx[1+line, i] = len(fo_index_list[0])
    if save_path is not None:
        table_data = pd.DataFrame(conf_mx,
                                  columns=pd.MultiIndex.from_product([['类别'], index_list]),
                                  index=pd.MultiIndex.from_product([['ob-fo'], label])
                                  )
        table_data.to_excel(save_path, sheet_name='sheet1')
        print("频率表已以excel表格形式保存至" + save_path)
    return conf_mx