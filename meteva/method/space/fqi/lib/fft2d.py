import numpy as np
import math

import numpy.fft


def fft2d(x, bigdim=None, inverse=False):
    is_null = False
    if bigdim is None:
        is_null = True
    x = np.array(x)
    out = {}
    xdim = x.shape
    if is_null:
        if xdim[0] <= 1024:
            x_index = 2 ** (math.ceil(math.log2(xdim[0])))
        else:
            x_index = math.ceil(xdim[0] / 512) * 512
        if xdim[1] <= 1024:
            y_index = 2 ** math.ceil(math.log2(xdim[1]))
        else:
            y_index = math.ceil(xdim[1] / 512) * 512
        bigdim = (x_index, y_index)
    hold = np.full(bigdim, 0 + 0j)
    hold[0: xdim[0], 0: xdim[1]] = x
    if not inverse:
        hold = numpy.fft.fft2(hold)[0: xdim[0], 0: xdim[1]]
    else:
        hold = hold.size * np.fft.ifft(hold.flatten()).reshape(hold.shape)[0: xdim[0], 0: xdim[1]]
    if is_null:
        out["fft"] = hold
        out["bigdim"] = bigdim
    else:
        out = hold
    return out
