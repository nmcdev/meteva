import copy
import math
import matplotlib.pyplot as plt

plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
import numpy as np
import nmc_verification
import pandas as pd
import pathlib


# 参数数组转换为列表
def para_array_to_list(key_num, para_array):
    key_list = []
    for key in para_array.keys():
        key_list.append(key)
    key_count = len(key_list)

    if (key_num == key_count - 1):
        key = key_list[key_num]
        para_list = []
        list1 = para_array[key]
        for para in list1:
            dict1 = {}
            dict1[key] = para
            para_list.append(dict1)
    else:
        key = key_list[key_num]
        list1 = para_array[key]
        para_list0 = para_array_to_list(key_num + 1, para_array)
        para_list = []
        for para in list1:
            for dict0 in para_list0:
                dict1 = {}
                dict1[key] = para
                for key0 in dict0.keys():
                    dict1[key0] = copy.deepcopy(dict0[key0])
                para_list.append(dict1)
    return para_list


class veri_excel_set:
    # 初始化设置写入excel表的默认参数
    def __init__(self, sheet=None, row=None, column=None, save_dir=""):
        self.sheet = sheet

        self.row = row

        self.column = column

        self.save_dir = save_dir

    # excel表参数设置
    def excel(self, veri_result):
        coords = veri_result.coords
        dims = veri_result.dims
        old_not_file_dim = [self.sheet, self.row, self.column]
        not_file_dim = list(filter(None, old_not_file_dim))
        file_pare_dict = {}
        plot_pare_dict = {}
        for dim in dims:
            if not dim in not_file_dim:
                file_pare_dict[dim] = coords[dim].values.tolist()
            else:
                plot_pare_dict[dim] = coords[dim].values.tolist()

        file_pare_list = para_array_to_list(0, file_pare_dict)

        for para_dict in file_pare_list:
            veri_result_plot = veri_result.loc[para_dict]
            subplot_num = 1
            if self.sheet is not None:
                subplot_num = len(plot_pare_dict[self.sheet])
            save_path = self.save_dir
            for key in para_dict.keys():
                save_path += str(key) + "=" + str(para_dict[key]) + "_"
            save_path += ".xlsx"
            pathlib.Path(save_path).touch()
            writer = pd.ExcelWriter(save_path)
            for s in range(subplot_num):
                para_dict_subplot = {}
                sheet_name = 'sheet1'
                if self.sheet is  not None:
                    para_dict_subplot[self.sheet] = plot_pare_dict[self.sheet][s]
                    sheet_name = str(plot_pare_dict[self.sheet][s])
                values_subplot = veri_result_plot.loc[para_dict_subplot]
                dims = values_subplot.dims
                pandas_class = values_subplot.to_pandas()
                if len(dims) > 1:
                    pandas_class.reset_index(dims[0], inplace=True)
                    pandas_class.rename(columns={dims[0]: dims[0] + '\\' + dims[1]}, inplace=True)
                    pandas_class.set_index(dims[0] + '\\' + dims[1], inplace=True)
                pandas_class = pandas_class.round(3)
                pandas_class.to_excel(excel_writer=writer, sheet_name=sheet_name)
            writer.save()
