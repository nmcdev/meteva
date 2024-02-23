import numpy as np


def cbind(x, y):
    return np.column_stack((np.array(x), np.array(y)))
