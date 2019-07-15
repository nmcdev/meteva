
import matplotlib as mpl
import matplotlib.pyplot as plt

def box_plot(observed, forecast, save_path=None, x_lable='observation', y_lable='forecast', title='box-plot'):
    '''
    box_plot 画一两组数据的箱型图
    ---------------
    :param observed:实况数据 一维的numpy
    :param forecast:预测数据 一维的numpy
    :param save_path: 保存数据的路径
    :param x_lable: 横坐标的标签
    :param y_lable:纵坐标标签
    :param title: 图片名字
    :return:
    '''
    plt.boxplot((observed, forecast), labels=[x_lable, y_lable])
    plt.title(title)
    if save_path is None:
        plt.show()
    else:
        plt.savefig(save_path)