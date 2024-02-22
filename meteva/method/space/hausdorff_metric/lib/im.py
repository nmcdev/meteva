import numpy as np
import pandas as pd

from meteva.method.space.hausdorff_metric.lib.as_unitname import as_unitname


def im(mat, xcol=None, yrow=None, xrange=None, yrange=None, unitname=None):
    typ = type(mat)
    if typ == "double":
        typ = "real"
    miss_xcol = xcol is None
    miss_yrow = yrow is None
    xcol = range(0, mat.shape[0])
    yrow = range(0, mat.shape[1])
    if mat.shape is not None:
        nr = mat.shape[1]
        nc = mat.shape[0]
        if np.isnan(nc):
            nc = 1
            nr = len(mat)
            if miss_xcol:
                xcol = range(0, nc)
        if len(xcol) != nc:
            raise Exception("Length of xcol does not match ncol(mat)")
        if len(yrow) != nr:
            raise Exception("Length of yrow does not match nrow(mat)")
    else:
        if miss_xcol or miss_yrow:
            raise Exception("mat is not a matrix and I can\'t guess its dimensions")
        if len(mat) != len(xcol) * len(yrow):
            return
        nc = len(xcol)
        nr = len(yrow)

    # lev = None
    # if 'categories' in mat:
    #     lev = mat.categories
    # if mat.dtype == 'category':
    #     typ = "category"
    # elif lev is not None:
    #     typ = "category"
    #     mat = pd.Categorical(mat, categories=lev)
    if type(mat) != pd.DataFrame:
        mat.reshape(nr, nc)
    if (miss_xcol or len(xcol) <= 1) and xrange is not None:
        xstep = np.diff(xrange) / nc
        xcol = np.linspace(start=xrange[0] + xstep / 2, stop=xrange[1] - xstep / 2, num=nc)
    elif len(xcol) > 1:
        xcol = np.linspace(start=min(xcol), stop=max(xcol), num=len(xcol))
        xstep = np.diff(xcol)[0]
        xrange = np.array([min(xcol), max(xcol)]) + np.array([-1, 1]) * xstep / 2
    else:
        raise Exception("Cannot determine pixel width")
    if (miss_yrow or len(yrow) <= 1) and yrange is not None:
        ystep = np.diff(yrange) / nr
        yrow = np.linspace(start=yrange[1] + ystep / 2, stop=yrange[2] - ystep / 2, num=nr)
    elif len(yrow) > 1:
        yrow = np.linspace(start=min(yrow), stop=max(yrow), num=len(yrow))
        ystep = np.diff(yrow)[0]
        yrange = np.array([min(yrow), max(yrow)]) + np.array([-1, 1]) * ystep / 2
    else:
        raise Exception("Cannot determine pixel height")
    unitname = as_unitname(unitname)
    out = {'v': mat, 'dim': [nr, nc], 'xrange': xrange, 'yrange': yrange,
           'xstep': xstep, 'ystep': ystep, 'xcol': xcol, 'yrow': yrow, 'type': typ, 'units': unitname}
    return out
