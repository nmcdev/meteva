import numpy as np


def get_1sample_data(x0,count):
    x = np.sort(x0)
    index = np.arange(0, count)
    nx = x.size + 0.0

    index_x0 = np.floor(nx * index / count).astype(np.int32)
    index_x1 = index_x0 + 1
    if index_x0[-1] >= nx:
        index_x0[-1] = nx - 1
    if index_x1[-1] >= nx:
        index_x1[-1]  = nx -1

    rate = nx * index / count - index_x0

    value = x[index_x0] * (1-rate) + x[index_x1] * rate

    return value

def get_qqplot_2samples_data(ob,fo,count = 1000):


    x = get_1sample_data(ob,count = count)
    y = get_1sample_data(fo,count = count)

    return x,y
