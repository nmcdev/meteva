import numpy as np


def ampstats(x, xhat, only_nonzero=False):
    x = np.array(x)
    xhat = np.array(xhat)
    if only_nonzero:
        idy = (xhat != 0)
        idx = (x != 0)
    else:
        idy = np.full(xhat.shape, True)
        idx = np.full(x.shape, True)
    m1 = np.nanmean(xhat[idy])
    v1 = np.nanvar(xhat[idy])
    m2 = np.nanmean(x[idx])
    v2 = np.nanvar(x[idx])
    if not only_nonzero:
        ind = (~np.isnan(xhat)) & (~np.isnan(x))
        v12 = np.cov(xhat[ind].flatten(), x[ind].flatten())
        v12 = v12[0][1]
    else:
        v12 = np.nan
    return {"mean_fcst": m1, "mean_vx": m2, "var_fcst": v1, "var_vx": v2, "cov": v12}
