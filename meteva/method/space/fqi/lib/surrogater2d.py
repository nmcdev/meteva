import numpy as np
from meteva.method.space.fqi.lib.fft2d import fft2d
from meteva.method.space.fqi.lib.aaft2d import aaft2d
from meteva.method.space.fqi.lib.zapsmall import zapsmall
import scipy.stats as ss
from .mae import mae
#import pyreadr


def surrogater2d(im, frac=0.95, n=10, maxiter=100, zero_down=True, verbose=False):
    im = np.array(im)
    xdim = np.shape(im)
    new_dim = xdim + (n, )
    out = np.full(new_dim, np.nan)
    im_vec = im
    tmp = fft2d(im)
    bigdim = tmp["bigdim"]
    sm_n = np.prod(xdim)
    big_n = np.prod(bigdim)
    amps = np.absolute(tmp["fft"])
    for i in range(n):
        sur = aaft2d(im=im, bigdim=bigdim)
        err_min = 0
        past_err = 0
        err = 0
        surmin = np.full(xdim, np.nan)
        if verbose:
            print(
                "\nFound initial surrogate via AAFT method.  Iterating to try to get same power spectrum and distribution as im.\n")
        for k in range(maxiter):
            if verbose:
                print(k)
            temp = fft2d(sur, bigdim=bigdim)
            ampsnew = np.absolute(temp)
            ind = ampsnew == 0
            if np.sum(ind) > 0:
                ampsnew[ind] = 1e-12
            ampsadj = frac * amps + (1 - frac) * ampsnew
            temp = temp * ampsadj / ampsnew
            temp2 = fft2d(temp, bigdim=bigdim, inverse=True) / sm_n
            sur = np.real(temp2)
            if zero_down:
                sur[sur < 0] = 0
                sur = zapsmall(sur)
            if k == 0:
                past_err = np.inf
                err_min = np.inf
            err = mae(amps, ampsnew)
            if err < err_min:
                if verbose:
                    print("\nerr = " + err + " < err_min = " + err_min + "\n")
                surmin = sur
                err_min = err
            if np.isinf(past_err):
                past_err = err
                continue
            elif np.abs((err - past_err) / past_err) * 100 <= 1:
                break
            past_err = err
        if verbose:
            print("\nFinished iterating.  Final Err = " + err + "\n")
        out[:, :, i] = surmin
        if verbose:
            print("\nFound surrogate " + i + "\n")
    return out



if __name__ == '__main__':
    #geom000 = pyreadr.read_r('../data/geom000.Rdata')['geom000']
    #z = surrogater2d(geom000, zero_down = True, n = 10)
    #print("h")
    pass