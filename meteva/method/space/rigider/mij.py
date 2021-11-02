import numpy as np


def mij(x, s=None, i=0, j=0):
    x = np.array(x)
    if s is None:
        xdim = x.shape
        range0 = np.tile(np.arange(xdim[0]), xdim[1])
        range1 = (np.arange(xdim[1])).repeat(xdim[0])
        s = np.stack((range0, range1), axis=-1)
    s[:, 0] = np.power(s[:, 0], i)
    s[:, 1] = np.power(s[:, 1], j)
    s = np.prod(s, axis=1)
    result = np.sum(s * np.reshape(x, -1, 'F'))
    return result
