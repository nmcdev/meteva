
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

def reliability_diagrams(ob, fo, grade_list = None,save_path = None, diagona_color='r', regression_line_color='g', broken_line_color='b'):
    '''
    reliability_diagrams  可靠性图
    ----------------------------
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :param save_path: 保存地址
    :param diagona_color:理想线颜色
    :param regression_line_color: 回归线颜色
    :param broken_line_color: 折线颜色
    :return:
    '''
    if grade_list is None:
        clevs = np.arange(0,1.0,10) # 如果没有给定概率等级，就设置默认等级
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