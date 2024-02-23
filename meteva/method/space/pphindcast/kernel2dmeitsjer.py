import math
import numpy as np


def kernel2dmeitsjer(func_type="gauss", **args):
    theta = args
    if 'h' in theta and theta['h'] is not None:
        h = theta['h']
    elif 'nx' in theta and 'ny' in theta and theta['nx'] is not None and theta['ny'] is not None:
        nx = theta['nx']
        ny = theta['ny']
        if 'a' in theta and theta['a'] is not None:
            a = theta['a']
        else:
            a = 1
        xgrid = np.array([val for val in range(1, nx + 1) for i in range(ny)]).reshape(nx, ny)
        ygrid = np.array([val for val in range(1, ny + 1) for i in range(nx)]).reshape(ny, nx).transpose()
        xcen = nx / 2
        ycen = ny / 2
        h = (xgrid - xcen) ** 2 + (ygrid - ycen) ** 2

    if 'sigma' in theta and theta['sigma'] is not None:
        sigma = theta['sigma']
        sigma2 = sigma ** 2
    if func_type == "average":
        out = np.ones([theta['n'], theta['n']]) * (1 / (theta['nx'] * theta['ny']))
    elif func_type == "boxcar":
        out = np.ones([theta['n'], theta['n']]) * (1 / (theta['n'] ** 2))
    elif func_type == "cauchy":
        out = 1 / (1 + h / sigma)
    elif func_type == "disk":
        r = theta['r']
        r2 = r ** 2
        rint = np.ceil(r - 0.5)
        diskg = [n for n in range(-rint, rint + 1)]
        n = len(diskg)
        x = np.array([val for val in diskg for i in range(n)]).reshape(n, n)
        y = np.transpose(x)
        xy_absmax = np.maximum(np.abs(x))
        xy_absmin = np.minimum(np.abs(x))
        tmp1 = tmp2 = hold = np.zeros(n, n)
        val = (xy_absmax + 0.5) ** 2 + (xy_absmin - 0.5) ** 2
        id1 = r2 < val
        id2 = r2 >= val
        tmp1[id1] = (xy_absmin[id1] - 0.5)
        tmp1[id2] = np.sqrt(r ** 2 - (xy_absmax[id2] + 0.5) ** 2)
        val = (xy_absmax - 0.5) ** 2 + (xy_absmin + 0.5) ** 2
        id1 = r2 > val
        id2 = r2 <= val
        tmp2[id1] = xy_absmin[id1] + 0.5
        tmp2[id2] = np.sqrt(r2 - (xy_absmax[id2] - 0.5) ** 2)
        val1 = (xy_absmax + 0.5) ** 2 + (xy_absmin + 0.5) ** 2
        hold_id1 = ((r2 < val1) & (r2 > (xy_absmax - 0.5) ** 2 + (xy_absmin - 0.5) ** 2))
        hold_id2 = ((xy_absmin == 0) & (xy_absmax - 0.5 < r) & (xy_absmax + 0.5 >= r))
        hold_id = hold_id1 | hold_id2
        hold[hold_id] = r2 * (0.5 * (math.asin(tmp2[hold_id] / r) - math.asin(tmp1[hold_id] / r)) + 0.25 * (
                    np.sin(2 * math.asin(tmp2[hold_id] / r)) - np.sin(2 * math.asin(tmp1[hold_id] / r)))) - (
                                    xy_absmax[hold_id] - 0.5) * (tmp2[hold_id] - tmp1[hold_id]) + (
                                    tmp1[hold_id] - xy_absmin[hold_id] + 0.5)
        hold[np.isnan(hold)] = 0
        hold = hold + (val1 < r2)
        hold[rint + 1, rint + 1] = min(np.pi * r2, np.pi / 2)
        rc2 = rint - 0.5
        if rint > 0 and r > rc2 and r2 < rc2 ** 2 + 0.25:
            tmp1 = np.sqrt(r2 - rc2 ** 2)
            tmp1n = tmp1 / r
            hold0 = 2 * (r ** 2 * (0.5 * math.asin(tmp1n) + 0.25 * np.sin(2 * math.asin(tmp1n))) - tmp1 * (rint - 0.5))
            hold[2 * rint + 1, rint + 1] = hold0
            hold[rint + 1, 2 * rint + 1] = hold0
            hold[rint + 1, 1] = hold0
            hold[1, rint + 1] = hold0
            hold[2 * rint, rint + 1] = hold[2 * rint, rint + 1] - hold0
            hold[rint + 1, 2 * rint] = hold[rint + 1, 2 * rint] - hold0
            hold[rint + 1, 2] = hold[rint + 1, 2] - hold0
            hold[2, rint + 1] = hold[2, rint + 1] - hold0

        hold[rint + 1, rint + 1] = min(hold[rint + 1, rint + 1], 1)
        Sn = np.sum(hold)
        out = hold / Sn
    elif func_type == "epanechnikov":
        out = np.zeros(nx, ny)
        out[h <= 1] = 3 / 4 * (1 - h[h <= 1] / sigma2)
    elif func_type == "exponential":
        if theta['a'] is not None:
            a = theta['a']
        else:
            a = 1
        h = np.sqrt(h)
        out = a * math.exp(-h / (2 * sigma2))
    elif func_type == "gauss":
        out = (1 / (2 * np.pi * sigma2)) * math.exp(-h / (2 * sigma2))
    elif func_type == "laplacian" or func_type == "unsharp":
        if theta['a'] is not None:
            a = theta['alpha']
        else:
            a = 0
        a = max(0, min(a, 1))
        o1 = a / (a + 1)
        o2 = (1 - a) / (1 + a)
        out = np.vstack([o1, o2, o1], [o2, -4 / (a + 1), o2], [o1, o2, o1])
        if func_type == "unsharp":
            out = np.vstack([0] * 3, [0, 1, 0], [0] * 3) - out
    elif func_type == "LoG":
        out = (h - 2 * sigma2) * np.exp(-h / (2 * sigma2)) / (sigma2 ** 2)
        out = out - np.mean(out)
    elif func_type == "minvar":
        out = np.zeros(nx, ny)
        out[h <= 1] = 3 / 8 * (3 - 5 * h[h <= 1] / sigma2)
    elif func_type == "multiquad":
        a2 = (theta['a']) ** 2
        if theta['inverse'] is None:
            inverse = False
        else:
            inverse = theta['inverse']
        out = np.sqrt((h + a2))
        if inverse:
            out = 1 / out
    elif func_type == "power":
        p = theta['p']
        h = np.sqrt(h)
        if theta['do.log'] is None:
            do_log = False
        else:
            do_log = theta['do.log']
        if ~do_log:
            out = -h ** p
        else:
            out = -np.log(h ** p + 1)
    elif func_type == "prewitt":
        out = np.vstack([1] * 3, [0] * 3, [-1] * 3)
        if theta['transpose'] is not None:
            if theta['transpose']:
                out = np.transpose(out)
    elif func_type == "radial":
        a = theta['a']
        m = theta['m']
        d = theta['d']
        if d % 2 == 0:
            out = a * h ** (2 * m - d) * np.log(h)
        else:
            out = a * h ** (2 * m - d)
        out[np.isnan(out)] = 0
    elif func_type == "ratquad":
        a = theta['a']
        out = 1 - h / (h + a)
    elif func_type == "sobel":
        out = np.vstack([1, 2, 1], [0] * 3, [-1, -2, -1])
        if theta['transpose'] is not None:
            if theta['transpose']:
                out = np.transpose(out)
    elif func_type == "student":
        p = theta['p']
        h = np.sqrt(h)
        out = 1 / (1 + h ** p)
    elif func_type == "wave":
        phi = theta['phi']
        h = np.sqrt(h)
        out = (phi / h) * np.sin(h / phi)
        out[np.isnan(out)] = 0

    return out
