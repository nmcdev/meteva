import numpy as np


def rigid_transform(theta, p0, n, cen):
    theta = np.array(theta)
    p0 = np.array(p0)
    cen = np.array(cen)
    if n is None:
        n = p0.shape[0]
    p0cen = p0 - cen
    r = theta[2]
    p0cen = np.hstack((np.cos(r) * p0cen[:, 0] - np.sin(r) * p0cen[:, 1], np.sin(r) * p0cen[:, 0] + np.cos(r) * p0cen[:, 1]))
    res = p0cen.reshape((n, 2), order="F") + np.tile(np.array(theta[0:2]), n).reshape(n, 2, order='C') + cen
    return res
