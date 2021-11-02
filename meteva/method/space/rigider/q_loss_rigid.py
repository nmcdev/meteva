import numpy as np


def q_loss_rigid(y1, x0, p1, p0):
    y1 = np.array(y1)
    x0 = np.array(x0)
    dx = y1 - x0
    sdx2 = np.sum(np.power(dx, 2))
    res = sdx2 / dx.size
    return res
