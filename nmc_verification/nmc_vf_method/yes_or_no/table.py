import sklearn
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import copy
import numpy as np
import pandas as pd


def contingency_table(ob, fo, grade=None, save_path='contingency_table.xls', sheet_name='sheet1',
                      is_append_sheet=False, excel_write=None):
    '''
    contingency_table 二分类预测列联表
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :param save_path: 保存地址
    :return:
    '''

    # 需要更改
    if grade is not None:
        shape = ob.shape
        new_ob = np.zeros(shape, dtype=np.int64)
        new_fo = np.zeros(shape, dtype=np.int64)

        ob_index_list = np.where(grade <= ob)
        new_ob[ob_index_list] = 0
        fo_index_list = np.where(grade <= fo)
        new_fo[fo_index_list] = 0
        ob_index_list = np.where(grade > ob)
        new_ob[ob_index_list] = 1
        fo_index_list = np.where(grade > fo)
        new_fo[fo_index_list] = 1
        ob = new_ob
        fo = new_fo
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
    if is_append_sheet:
        table_data.to_excel(excel_writer=excel_write, sheet_name=sheet_name)
        excel_write.save()
    else:
        table_data.to_excel(save_path, sheet_name=sheet_name)
# contingency_table1

# def contingency_table(ob, fo,threshold_list = None,save_path = None, figsize=(9, 4), x_label=None, y_label=None, title='contingency table', fontsize=20,

#                   fontproperties='KaiTi', col_labels=['yes', 'no', 'Total'], row_labels=['yes', 'no', 'Total']):
# '''
# contingency_table 用来画一张二分类预测列联表
# -------------------------------------
# :param ob: 实况数据
# :param fo: 预测数据
# :param threshold_list: 阈值列表
# :param save_path: 保存路径
# :param figsize:
# :param x_label: x方向标签
# :param y_label: y方向标签
# :param title: 标题
# :param fontsize: 字体大小
# :param fontproperties: 字体
# :param col_labels: 列标签
# :param row_labels: 行标签
# :return:
# '''
# # 扩展一下该函数的功能
# # 当threshold_list 为None时，ob和fo里的取值默认是只为0或1的，否则根据threshold_list 里的阈值判断ob和fo里的元素是0或1，进一步绘图
# #threshold_list 有多个取值时，每个表的title 需要显示等级的内容
#
# if threshold_list is None:
#     cm = confusion_matrix(ob, fo)
#     tn, fp, fn, tp = cm.ravel()
#     fig = plt.figure(figsize=figsize)
#     ax = fig.add_subplot(111, frameon=True, xticks=[], yticks=[])
#     table_vals = [[tn, fn, tn + fn], [fp, tp, fp + tp], [tn + fp, fn + tp, tn + fp + fn + tp]]
#
#     # 表格左上角需标明行和列哪个是预报，哪个是实况
#     my_table = plt.table(cellText=table_vals,
#                          rowLabels=row_labels, colLabels=col_labels,
#                          loc='center')
#
#
#     my_table.set_fontsize(10)
#     my_table.scale(0.7, 3.5)
#     plt.text(0.05, 0.5, y_label, fontsize=fontsize, rotation=90)
#     plt.text(0.5, 0.9, x_label, fontsize=fontsize)
#     plt.title(title, fontproperties=fontproperties, fontsize=25)
#     #plt.show()
# else:
#     tn = len(threshold_list)
#     # threshold_list 有1各阈值时，表titile不变
#
#     # threshold_list 有多个取值时，每个表的title 需要显示等级的内容
#
#     for i in range(len(threshold_list)):
#         ob1 = copy.deepcopy(ob)
#         fo1 = copy.deepcopy(fo)
#         ob1[ob1>=threshold_list[i]] = 1
#         ob1[ob1< threshold_list[i]] =0
#         fo1[fo1>=threshold_list[i]] = 1
#         fo1[fo1< threshold_list[i]] =0
#
#         #绘制表格
#
# if save_path is None:
#     plt.show()
# else:
#     plt.savefig(save_path)
#
# #print("success")
