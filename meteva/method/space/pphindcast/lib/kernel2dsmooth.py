import math
import numpy as np
import pandas as pd
import sys
#sys.path.append(r'F:\Work\MODE\OthersFunctions')
from meteva.method.space.fuzzy_logic.lib.kernel2dmeitsjer import kernel2dmeitsjer
from meteva.method.space.fuzzy_logic.lib.zapsmall import zapsmall


def kernel2dsmooth(x, kernel_type=None, k=None, w=None, x_object=None, xdim=None, nxy=None, setup=False, verbose=False,
                   **args):
    if xdim is None:
        xdim = list(x.shape)
    if nxy is None:
        nxy = np.prod(xdim[1: 2])
    if w is None:
        if kernel_type is not None:
            k = kernel2dmeitsjer(func_type=kernel_type, **args)
        elif k is None:
            print("kernel2dsmooth: must give a value for at least one of kernel.type, K, or W")
            return
        kdim = list(k.shape)
        bigdim = np.subtract(np.sum([xdim, kdim], axis=0), [1, 1])
        if bigdim[0] <= 1024:
            bigdim[0] = 2 ** np.ceil(math.log2(bigdim[0]))
        else:
            bigdim[0] = np.ceil(bigdim[1] / 512) * 512
        if bigdim[1] <= 1024:
            bigdim[1] = 2 ** np.ceil(math.log2(bigdim[1]))
        else:
            bigdim[1] = np.ceil(bigdim[1] / 512) * 512
        kbig = np.zeros((bigdim[0], bigdim[1]))
        kcen = list(map(math.floor, (np.array(kdim) + 1) / 2))
        kbig[0: (kdim[0] - kcen[0] + 1), 0: (kdim[1] - kcen[1] + 1)] = k[kcen[0] - 1: kdim[0], kcen[1] - 1: kdim[1]]
        if kdim[0] > 1:
            kbig[(bigdim[0] - kcen[0] + 1): bigdim[0], 0: (kdim[1] - kcen[1] + 1)] = k[0: (kcen[0] - 1),
                                                                                     kcen[1] - 1: kdim[1]]
        if kdim[1] > 1:
            kbig[0: (kdim[0] - kcen[0] + 1), (bigdim[1] - kcen[1] + 1): bigdim[1]] = k[kcen[0] - 1: kdim[0],
                                                                                     0: (kcen[1] - 1)]
        if kdim[0] > 1 and kdim[1] > 1:
            kbig[(bigdim[0] - kcen[0] + 1): bigdim[0], (bigdim[1] - kcen[1] + 1): bigdim[1]] = k[0: (kcen[0] - 1),
                                                                                               0: (kcen[1] - 1)]
        if verbose:
            print("Finding the FFT of the kernel matrix.\n")
        w = np.fft.fft2(kbig) / np.prod(bigdim)
        if verbose:
            print("FFT of kernel matrix found.\n")
        if setup:
            return w
    else:
        bigdim = w.shape
    out = np.zeros((bigdim[0], bigdim[1]))
    if type(x) == pd.DataFrame:
        x = x.fillna(0)
    out[0: xdim[0], 0: xdim[1]] = x
    # out[pd.DataFrame(out).isna] = 0
    if verbose:
        print("Performing the convolution.\n")
    if x_object is not None:
        out = (np.fft.ifft2(x_object * w)).real[0: xdim[0], 0: xdim[1]]
    else:
        out = ((np.fft.ifft2(np.fft.fft2(out) * w)) * out.size).real[0: xdim[0], 0: xdim[1]]
    if verbose:
        print("The convolution has been carried out.\n")
    return zapsmall(out)
