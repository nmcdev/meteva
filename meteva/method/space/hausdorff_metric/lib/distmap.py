# -*-coding:utf-8-*-

import math
import numpy as np


# def distmap(a):
#     xcol = a["xcol"]
#     yrow = a["yrow"]
#     m = np.array(a["m"])
#     rlen, clen = m.shape
#     true_list = np.array([])
#     dist = np.zeros((rlen, clen))
#     if sum(sum(m)) == 0:
#         distance = math.sqrt((xcol.max() - xcol.min())**2 + (yrow.max() - yrow.min()) ** 2)
#         dist = np.ones((rlen, clen)) * distance
#     elif sum(sum(m)) != m.size:
#         for i in range(rlen):
#             for j in range(clen):
#                 if m[i, j]:
#                     true_list = np.append(true_list, [xcol[i], yrow[j]])
#         for i in range(rlen):
#             for j in range(clen):
#                 if m[i, j]:
#                     dist[i, j] = 0
#                 else:
#                     point = np.array([xcol[i], yrow[j]])
#                     mat = spatial.distance.cdist(point, true_list, 'cityblock')
#                     dist[i, j] = mat.min()
#     return dist


def rebound(a, window):
    w = a
    x_range = window["x_range"]
    y_range = window["y_range"]
    xcol = newseq(a["xcol"], x_range)
    yrow = newseq(a["yrow"], y_range)
    m = np.zeros((len(xcol), len(yrow)))
    x_min_index = list(xcol).index(min(a['xcol']))
    x_max_index = list(xcol).index(max(a['xcol']))
    y_min_index = list(yrow).index(min(a['yrow']))
    y_max_index = list(yrow).index(max(a['yrow']))
    m[x_min_index:x_max_index+1, y_min_index:y_max_index+1] = a['m']
    m = (m == 1)
    newmask = {"xcol": xcol, "yrow": yrow, "m": m}
    # xx = rasterx(newmask)
    # yy = rastery(newmask)
    # newmask["m"] = inside(xx, yy, w)
    return newmask


## 用于mask
def boundingbox(a, b):
    a_x_min = a["xrange"][0]
    a_x_max = a["xrange"][1]
    a_y_min = a["yrange"][0]
    a_y_max = a["yrange"][1]
    b_x_min = b["xrange"][0]
    b_x_max = b["xrange"][1]
    b_y_min = b["yrange"][0]
    b_y_max = b["yrange"][1]
    x_min = min(a_x_min, b_x_min)
    x_max = max(a_x_max, b_x_max)
    y_min = min(a_y_min, b_y_min)
    y_max = max(a_y_max, b_y_max)
    x_range = [x_min, x_max]
    y_range = [y_min, y_max]
    window = {"x_range": x_range, "y_range": y_range}
    return window


def newseq(oldseq, newrange):
    oldrange = [min(oldseq), max(oldseq)]
    length = len(oldseq)
    dstep = (max(oldseq) - min(oldseq)) / (length - 1)
    nleft = max(0, math.floor((oldrange[0] - newrange[0]) / dstep))
    nright = max(0, math.floor((newrange[1] - oldrange[1]) / dstep))
    newstart = max(oldrange[0] - nleft * dstep, newrange[0])
    newend = min(oldrange[1] + nright * dstep, newrange[1]) + dstep
    return np.arange(newstart, newend, dstep)


# def rasterx(w):
#     len_y = w["yrow"].size
#     return np.tile(np.array(w["xcol"]), (len_y, 1))


# def rastery(w):
#     len_x = w["xcol"].size
#     return np.tile(np.array(w["yrow"]), (len_x, 1)).transpose()


# def inside(x, y, w):
#     x = np.array(x)
#     y = np.array(y)
#     xr = w["xrange"]
#     yr = w["yrange"]
#     frameok = np.array((x >= xr[0]) * (x <= xr[1]) * (y >= yr[0]) * (y <= yr[1]))
#     xf = x.transpose()[frameok.transpose()]
#     yf = y.transpose()[frameok.transpose()]
#     loc = nearest_raster_point(xf, yf, w)
#     okf = np.zeros(loc['col'].size)
#     for i in range(loc['col'].size):
#         okf[i] = w['m'][int(loc['row'][i]) - 1, int(loc['col'][i]) - 1]
#     result = frameok[frameok]
#     for i in range(okf.size):
#         result[i] = okf[i]
#     return okf.reshape(w['m'].shape)


# def nearest_raster_point(x, y, w):
#     x = np.array(x)
#     y = np.array(y)
#     nr = w["dim"][0]
#     nc = w["dim"][1]
#     cc = 1 + np.round((x - w["xcol"][0]) / w["xstep"])
#     rr = 1 + np.round((y - w["ycol"][0]) / w["ystep"])
#     cc = np.maximum(1, np.minimum(cc, nc))
#     rr = np.maximum(1, np.minimum(rr, nr))
#     return {"row": rr, "col": cc}


def rotate(self, angle):
    x = math.cos(angle) * self[:, 0] - math.sin(angle) * self[:, 1]
    y = math.sin(angle) * self[:, 0] + math.cos(angle) * self[:, 1]
    # result = {'xrange': [np.min(x), np.max(x)], 'yrange': [np.min(y), np.max(y)], 'x0': np.min(x), 'x1': np.max(x), 'y0': np.min(y), 'y1': np.max(y)}
    result = {'xrange': [np.min(x), np.max(x)], 'yrange': [np.min(y), np.max(y)],
              'x0': x[0], 'x1': x[1], 'y0': y[0], 'y1': y[1]}
    return result


def getRedDotsCoordinatesFromLeftToRight(np_matrix, red_dor_number=1):
    red_dots = np.where(np_matrix == red_dor_number)
    red_dots = tuple(g[np.argsort(red_dots[-1])] for g in red_dots)
    red_dots = np.stack(red_dots)[::-1].T
    return red_dots
