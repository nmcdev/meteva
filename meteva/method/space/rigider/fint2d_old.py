import numpy as np
import math
from . import zapsmall
import copy

def fint2d_old(x, ws, s, method=None, derivs=False):
    if method is None:
        method = ["nearest", "linear", "cubic"]
    x = np.array(x)
    ws = np.array(ws)
    dimout = x.shape
    if method == "nearest":
        minx = miny = 1
        maxx = dimout[0]
        maxy = dimout[1]
    elif method == "linear":
        minx = 1
        miny = 1
        maxx = dimout[0] - 1
        maxy = dimout[1] - 1
    elif method == "cubic":
        minx = 2
        miny = 2
        maxx = dimout[0] - 2
        maxy = dimout[1] - 2
    else:
        raise Exception("the input method must be 'nearest', 'linear' or 'cubic'")
    u = ws[:, 0]
    v = ws[:, 1]
    u[u > maxx] = maxx
    u[u < minx] = minx
    v[v > maxy] = maxy
    v[v < miny] = miny
    n = len(u)
    out = np.zeros((dimout[0], dimout[1])) + np.nan
    if derivs:
        out_x = copy.deepcopy(out)
        out_y = copy.deepcopy(out)
        temp_fx = np.array(x[:, 2: dimout[1]] - x[:, 1: (dimout[1] - 1)])
        temp_fxy = np.zeros(temp_fx.size)
        d_fx = cbind(temp_fx, temp_fxy)
        temp_fy = np.array(x[2: dimout[0], :] - x[1: (dimout[0] - 1), :])
        temp_fyy = np.zeros(temp_fy.size)
        d_fy = cbind(temp_fy, temp_fyy.transpose())
    if method == "nearest":
        x = np.floor(u + 0.5)
        x[np.array(x > maxx)] = maxx
        x[np.array(x < minx)] = minx
        y = np.floor(v + 0.5)
        y[np.array(y > maxy)] = maxy
        y[np.array(y < miny)] = miny
        # out[s] = x[cbind(x, y)]
        out[s] = x[cbind(x, y)]
        if derivs:
            out_x[s] = d_fx[cbind(x, y)]
            out_y[s] = d_fy[cbind(x, y)]
            out_x[np.isnan(out_x)] = 0
            out_y[np.isnan(out_y)] = 0
    elif method in ["linear", "cubic"]:
        fu = np.floor(u + 0.5)
        fu[np.array(fu > maxx)] = maxx
        fu[np.array(fu < minx)] = minx
        fv = np.floor(v + 0.5)
        fv[np.array(fv > maxy)] = maxy
        fv[np.array(fv < miny)] = miny
        ufrac = u - fu
        vfrac = v - fv
        fuv = cbind(fu, fv)
        fuv1 = np.array(fuv)
        fuv1[:, 1] = fuv1[:, 1] + 1
        fu1v = np.array(fuv)
        fu1v[:, 0] = fu1v[:, 0] + 1
        fu1v1 = cbind(fu1v[:, 0], fuv1[:, 1])
        if method == "linear":
            fuv = fuv.astype(np.int32)
            fuv1 = fuv1.astype(np.int32)
            out[s] = (1 - ufrac) * (1 - vfrac)
            out[s] = (1 - ufrac) * (1 - vfrac) * x[fuv] + (1 - ufrac) * vfrac * x[fuv1] + ufrac * (1 - vfrac) * x[
                fu1v] + ufrac * vfrac * x[fu1v1]
            if derivs:
                out_x[s] = (1 - ufrac) * (1 - vfrac) * d_fx[fuv] + (1 - ufrac) * vfrac * d_fx[fuv1] + ufrac * (
                        1 - vfrac) * d_fx[fu1v] + ufrac * vfrac * d_fx[fu1v1]
                out_y[s] = (1 - ufrac) * (1 - vfrac) * d_fy[fuv] + (1 - ufrac) * vfrac * d_fy[fuv1] + ufrac * (
                        1 - vfrac) * d_fy[fu1v] + ufrac * vfrac * d_fy[fu1v1]
        elif method == "cubic":
            u_bneg1 = (2 * np.power(ufrac, 2) - np.power(ufrac, 3) - ufrac) / 2
            v_bneg1 = (2 * np.power(vfrac, 2) - np.power(vfrac, 3) - vfrac) / 2
            u_b0 = (3 * np.power(ufrac, 3) - 5 * np.power(ufrac, 2) + 2) / 2
            v_b0 = (3 * np.power(vfrac, 3) - 5 * np.power(vfrac, 2) + 2) / 2
            u_b1 = (4 * np.power(ufrac, 2) - 3 * np.power(ufrac, 3) + ufrac) / 2
            v_b1 = (4 * np.power(vfrac, 2) - 3 * np.power(vfrac, 3) + vfrac) / 2
            u_b2 = ((ufrac - 1) * np.power(ufrac, 2)) / 2
            v_b2 = ((vfrac - 1) * np.power(vfrac, 2)) / 2
            fun1vn1 = fuv - 1
            fun1v = cbind(fun1vn1[:, 0], fuv[:, 1])
            fun1v1 = cbind(fun1v[:, 0], fuv[:, 1] + 1)
            fun1v2 = cbind(fun1v[:, 0], fuv[:, 1] + 2)
            fuvn1 = cbind(fuv[:, 0], fun1vn1[:, 1])
            fuv1 = cbind(fuv[:, 0], fun1v1[:, 1])
            fuv2 = cbind(fuv[:, 0], fun1v2[:, 1])
            fu1vn1 = cbind(fuv[:, 0] + 1, fun1vn1[:, 1])
            fu1v = cbind(fu1vn1[:, 0], fuv[:, 1])
            fu1v1 = cbind(fu1vn1[:, 0], fuv1[:, 1])
            fu1v2 = cbind(fu1vn1[:, 0], fun1v2[:, 1])
            fu2vn1 = cbind(fuv[:, 0] + 2, fun1vn1[:, 1])
            fu2v = cbind(fu2vn1[:, 0], fun1v[:, 1])
            fu2v1 = cbind(fu2vn1[:, 0], fun1v1[:, 1])
            fu2v2 = cbind(fu2vn1[:, 0], fun1v2[:, 1])
            if derivs:
                du_bneg1 = (4 * ufrac - 3 * np.power(ufrac, 2) - 1) / 2
                dv_bneg1 = (4 * vfrac - 3 * np.power(vfrac, 2) - 1) / 2
                du_b0 = (9 * np.power(ufrac, 2) - 10 * ufrac) / 2
                dv_b0 = (9 * np.power(vfrac, 2) - 10 * vfrac) / 2
                du_b1 = (8 * ufrac - 9 * np.power(ufrac, 2) + 1) / 2
                dv_b1 = (8 * vfrac - 9 * np.power(vfrac, 2) + 1) / 2
                du_b2 = (3 * np.power(ufrac, 2) - 2 * ufrac) / 2
                dv_b2 = (3 * np.power(vfrac, 2) - 2 * vfrac) / 2
            temp_out = u_bneg1 * (v_bneg1 * get_by_xy(x,fun1vn1) + v_b0 * get_by_xy(x,fun1v) + v_b1 * get_by_xy(x,fun1v1) + v_b2 * get_by_xy(x, fun1v2)) + u_b0 * (v_bneg1 * get_by_xy(x, fuvn1) + v_b0 * get_by_xy(x, fuv) + v_b1 * get_by_xy(x, fuv1) + v_b2 * get_by_xy(x, fuv2)) + u_b1 * (v_bneg1 * get_by_xy(x, fu1vn1) + v_b0 * get_by_xy(x, fu1v) + v_b1 * get_by_xy(x, fu1v1) + v_b2 * get_by_xy(x, fu1v2)) + u_b2 * (v_bneg1 * get_by_xy(x, fu2vn1) + v_b0 * get_by_xy(x, fu2v) + v_b1 * get_by_xy(x, fu2v1) + v_b2 * get_by_xy(x, fu2v2))
            set_by_xy(out, s, temp_out)
            if derivs:
                temp_out_x = du_bneg1 * (v_bneg1 * get_by_xy(d_fx, fun1vn1) + v_b0 * get_by_xy(d_fx, fun1v) + v_b1 * get_by_xy(d_fx, fun1v1) + v_b2 * get_by_xy(d_fx,
                    fun1v2)) + du_b0 * (v_bneg1 * get_by_xy(d_fx, fuvn1) + v_b0 * get_by_xy(d_fx, fuv) + v_b1 * get_by_xy(d_fx, fuv1) + v_b2 * get_by_xy(d_fx,
                    fuv2)) + du_b1 * (v_bneg1 * get_by_xy(d_fx, fu1vn1) + v_b0 * get_by_xy(d_fx, fu1v) + v_b1 * get_by_xy(d_fx, fu1v1) + v_b2 * get_by_xy(d_fx,
                    fu1v2)) + du_b2 * (v_bneg1 * get_by_xy(d_fx, fu2vn1) + v_b0 * get_by_xy(d_fx, fu2v) + v_b1 * get_by_xy(d_fx, fu2v1) + v_b2 * get_by_xy(d_fx,
                    fu2v2))
                set_by_xy(out_x, s, temp_out_x)
                temp_out_y = dv_bneg1 * (u_bneg1 * get_by_xy(d_fy, fun1vn1) + u_b0 * get_by_xy(d_fy, fuvn1) + u_b1 * get_by_xy(d_fy, fu1vn1) + u_b2 * get_by_xy(d_fy,
                    fu2vn1)) + dv_b0 * (u_bneg1 * get_by_xy(d_fy, fun1v) + u_b0 * get_by_xy(d_fy, fuv) + u_b1 * get_by_xy(d_fy, fu1v) + u_b2 * get_by_xy(d_fy,
                    fu2v)) + dv_b1 * (u_bneg1 * get_by_xy(d_fy, fun1v1) + u_b0 * get_by_xy(d_fy, fuv1) + u_b1 * get_by_xy(d_fy, fu1v1) + u_b2 * get_by_xy(d_fy,
                    fu2v1)) + dv_b2 * (u_bneg1 * get_by_xy(d_fy, fun1v2) + u_b0 * get_by_xy(d_fy, fuv2) + u_b1 * get_by_xy(d_fy, fu1v2) + u_b2 * get_by_xy(d_fy,
                    fu2v2))
                set_by_xy(out_y, s, temp_out_y)
    else:
        raise Exception("method must be one of nearest, linear or cubic")
    out = zapsmall.zapsmall(out)
    if derivs:
        return list(xy=out, dx=out_x, dy=out_y)
    else:
        return out


def cbind(x, y):
    return np.vstack((np.array(x), np.array(y))).transpose()

def get_by_xy(matrix, index):
    row_num = int(index.size / 2)
    result = np.zeros(row_num)
    matrix = np.array(matrix)
    index = np.array(index)
    for i in range(row_num):
        if math.isnan(index[i, 0]):
            x = - 1
        else:
            x = int(index[i, 0]) - 1
        if math.isnan(index[i, 1]):
            y = -1
        else:
            y = int(index[i, 1]) - 1
        result[i] = matrix[x, y]
    return result

def set_by_xy(matrix, index, value):
    row_num = int(index.size / 2)
    for i in range(row_num):
        if math.isnan(index[i, 0]):
            x = - 1
        else:
            x = int(index[i, 0]) - 1
        if math.isnan(index[i, 1]):
            y = -1
        else:
            y = int(index[i, 1]) - 1
        matrix[x, y] = value[i]
