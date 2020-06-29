import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import copy
from  matplotlib import  cm
import meteva
import math



def frequency_histogram(ob, fo,grade_list=None, member_list=None,  vmax = None,save_path=None,show = False,dpi = 300, title="频率统计图"):
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


    legend = ['观测']
    if member_list is None:
        if new_Fo_shape[0] <= 1:
            legend.append('预报')
        else:
            for i in range(new_Fo_shape[0]):
                legend.append('预报' + str(i + 1))
    else:
        legend.extend(member_list)

    result_array = meteva.method.frequency_table(ob, fo, grade_list=grade_list)
    total_count = np.sum(result_array[0,:])
    result_array /= total_count
    if grade_list is not None:
        axis = ["<" + str(grade_list[0])]
        for index in range(len(grade_list) - 1):
            axis.append("[" + str(grade_list[index]) + "," + str(grade_list[index + 1]) + ")")
        axis.append(">=" + str(grade_list[-1]))
    else:
        new_fo = copy.deepcopy(fo).flatten()
        new_ob = copy.deepcopy(ob).flatten()
        fo_list = list(set(new_fo.tolist()))
        fo_list.extend(list(set(new_ob.tolist())))
        axis = list(set(fo_list))

    name_list_dict = {}
    name_list_dict["legend"] = legend
    name_list_dict["类别"] = axis
    meteva.base.plot_tools.bar(result_array,name_list_dict,ylabel= "样本占比",vmin = 0,vmax = vmax,save_path = save_path,show = show,dpi = dpi,title=title)

