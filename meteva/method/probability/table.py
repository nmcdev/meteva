import numpy as np
import pandas as pd


def hnh(Ob, Fo, grade_count=10,member_list=None,  save_path=None):
    '''
    :param Ob:
    :param Fo:
    :param grade_count:
    :return:
    '''

    grade = 1 / grade_count
    if grade_count < 1:
        print('grade_count输入错误，不能小于1')
        return
    grade_list = np.arange(0, 1, grade).tolist()
    grade_list.append(1.1)
    Ob_shape = Ob.shape
    Fo_shape = Fo.shape
    hnh_array_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    for line in range(new_Fo_shape[0]):
        th_list = []
        for g in range(len(grade_list) - 1):
            index = np.where((new_Fo[line, :] >= grade_list[g]) & (new_Fo[line, :] < grade_list[g + 1]))
            ob1 = Ob[index]
            ob2 = ob1[ob1 > 0]
            th_list.append([ob1.size, ob2.size])
        hnh_array = np.array(th_list)
        hnh_array_list.append(hnh_array)
    hnh_array = np.array(hnh_array_list)
    shape = (new_Fo_shape[0],len(grade_list) - 1,2)
    #shape.append(len(grade_list) - 1)
    #shape.append(2)
    hnh_array = hnh_array.reshape(shape)

    if save_path is not None:

        label = []
        if member_list is None:
            if new_Fo_shape[0] == 1:
                label.append('预报')
            else:
                for i in range(new_Fo_shape[0]):
                    label.append('预报' + str(i + 1))
        else:
            label.extend(member_list)
        grade_list_str = np.arange(1,len(grade_list)).tolist()

        table_data_list = []
        for i in range(new_Fo_shape[0]):
            table_data = pd.DataFrame(hnh_array[i,:],
                                      index=pd.MultiIndex.from_product([['等级'],grade_list_str]),
                                      columns=pd.MultiIndex.from_product([['样本数'], ["正例","负例"]])
                                      )
            table_data_list.append(table_data)
        with pd.ExcelWriter(save_path) as writer:
            for i in range(len(table_data_list)):
                table_data_list[i].to_excel(writer, sheet_name=label[i])
        print("列联表已以excel表格形式保存至" + save_path)

    hnh_array = hnh_array.squeeze()

    return hnh_array

