import numpy as np
import scipy.stats as ss
import math
from .fft2d import fft2d
from .cbind import cbind
import numpy.fft
#import pyreadr


def aaft2d(im, bigdim=None):
    im = np.array(im)
    xdim = im.shape
    im_vec = im.flatten()
    n = im_vec.size
    im2 = np.random.normal(size=xdim)
    im2_vec = im2.flatten()
    out = np.full(xdim, np.nan)
    rk1 = ss.rankdata(im_vec) - 1
    s_im2_vec = np.sort(im2_vec)
    rk1 = np.floor(rk1).astype(int)
    z = s_im2_vec[rk1]
    if bigdim is None:
        if xdim[0] <= 1024:
            x_index = 2 ** math.ceil(math.log2(xdim[0]))
        else:
            x_index = math.ceil(xdim[0] / 512) * 512
        if xdim[1] <= 1024:
            y_index = 2 ** math.ceil(math.log2(xdim[1]))
        else:
            y_index = math.ceil(xdim[1] / 512) * 512
        bigdim = (x_index, y_index)
    big_0_mat = np.full(bigdim, 0 + 0j)
    big_n = np.prod(bigdim)
    x = np.full(bigdim, 0.0)
    x[0: xdim[0], 0: xdim[1]] = np.array(z).reshape(xdim)
    zfft = fft2d(x, bigdim=bigdim)
    nr1 = math.ceil(xdim[0] / 2) - 1
    nr2 = (xdim[0] - 1)
    nc2 = math.ceil(xdim[1] / 2) - 1
    pi = 2 * math.pi * np.random.normal(size=(nr1, 1))
    pj = 2 * math.pi * np.random.normal(size=(1, nc2))
    pij = 2 * math.pi * np.random.normal(size=(nr2, nc2))
    if xdim[1] % 2 == 0:
        qij = 2 * math.pi * np.random.normal(size=(nr1, 1))
        if xdim[0] % 2 == 0:
            qij = np.concatenate((qij, np.zeros(1), -np.flipud(qij)))
        else:
            qij = np.concatenate((qij, -np.flipud(qij)))
        qij_shape = (nr2, qij.size / nr2)
        qij = qij.reshape(qij_shape)
        phij = cbind(cbind(pij, qij), -np.fliplr(np.flipud(pij)))
    else:
        phij = cbind(pij, -np.fliplr(np.flipud(pij)))
    if xdim[0] % 2 == 0:
        phi = np.concatenate((np.zeros(1), pi.flatten(), np.zeros(1), -np.flipud(pi).flatten()))
    else:
        phi = np.concatenate((np.zeros(1), pi.flatten(), -np.flipud(pi).flatten()))
    if xdim[1] % 2 == 0:
        phj = np.concatenate((np.zeros(1), pj.flatten(), np.zeros(1), -np.fliplr(pj).flatten()))
    else:
        phj = np.concatenate((np.zeros(1), pj.flatten(), -np.fliplr(pj).flatten()))
    ph = np.full(xdim, 0.0)
    ph[1: xdim[0], 1: xdim[1]] = phij
    ph[0, :] = phj
    ph[:, 0] = phi
    k = big_0_mat
    k[0: xdim[0], 0: xdim[1]] = zfft[0: xdim[0], 0: xdim[1]] * np.exp((0 + 1j) * ph)
    j = np.array(np.real(np.fft.ifft(k.flatten()) * k.size / n).reshape(k.shape)[0: xdim[0], 0: xdim[1]])
    rk2 = ss.rankdata(j.flatten()) - 1
    j = np.sort(im_vec)
    rk2 = np.floor(rk2).astype(int)
    j = np.array(j[rk2])
    out = j.reshape(xdim)
    return out


if __name__ == '__main__':
    # geom000 = pyreadr.read_r('../data/geom000.Rdata')['geom000']
    # z = aaft2d(geom000)
    # print("h")
    pass
