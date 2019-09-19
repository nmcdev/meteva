import nmc_verification.nmc_vf_base.function.put_into_sta_data as pisd
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LinearRegression


def reliability_diagrams_muti_model(ob, fo_list, grade_list=None, save_path=None, diagona_color='r',
                                    regression_line_color='g',
                                    broken_line_color='b'):
    '''

    :param ob:
    :param fo_list:
    :param grade_list:
    :param save_path:
    :param diagona_color:
    :param regression_line_color:
    :param broken_line_color:
    :return:
    '''
    fo_list.append(ob)

    meger_df_data = pisd.merge_on_id_and_obTime(fo_list)
    ob = meger_df_data.iloc[:, -1].values

    data_len = len(fo_list)
    plt.figure(figsize=[6.4 * data_len, 4.8])

    colnums = ['level', 'id', 'time']
    title = ''
    for colnum in colnums:
        the_duplicate_values = meger_df_data[colnum].unique()
        if len(the_duplicate_values) == 1:
            title = title + str(the_duplicate_values[0])
    plt.suptitle(title)
    for index, fo_of_colnum in enumerate(meger_df_data.iloc[:, 7:-1]):
        fo = meger_df_data[fo_of_colnum].values
        plt.subplot(1, data_len, index + 1)
        if grade_list is None:
            clevs = np.arange(0, 1.0, 10)  # 如果没有给定概率等级，就设置默认等级
        else:
            clevs = grade_list
        orfs = [0]
        for i in range(1, len(clevs)):
            index0 = np.where((fo > clevs[i - 1]) & (fo <= clevs[i]))
            num = np.sum(ob[index0] == 1)
            lenght = len(index0)
            orf = num / lenght
            orfs.append(orf)
        orfs = np.array(orfs)
        X = np.array(clevs)
        X = X.reshape((len(X), -1))
        model = LinearRegression().fit(X, orfs)
        y = model.predict(X)
        plt.plot(X, y, color=regression_line_color)
        plt.plot(clevs, orfs, color=broken_line_color)
        plt.scatter(clevs, orfs, color=broken_line_color)
        plt.plot([0, 1], [0, 1], color=diagona_color)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)