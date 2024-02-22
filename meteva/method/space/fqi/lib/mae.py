import numpy as np


def mae(x1, x2):
    x1 = np.array(x1).flatten()
    x2 = np.array(x2).flatten()
    x = np.array(np.abs(x1 - x2))
    return np.mean(x)
