# -*-coding:utf-8-*-
import math
import numpy as np


def bearing(point1, point2, deg=True, aty="compass"):
    point1 = np.array(point1)
    point2 = np.array(point2)
    if deg:
        point1[:, 1] = point1[:, 1] * math.pi / 180
        point2[:, 1] = point2[:, 1] * math.pi / 180
    dlon = np.array(point1[:, 0] - point2[:, 0])
    if deg:
        dlon = dlon * math.pi / 180

    s = np.multiply(math.cos(point2[:, 1]), math.sin(dlon))
    c_val = np.multiply(math.cos(point1[:, 1]), math.sin(point2[:, 1])) - np.multiply(
        np.multiply(math.sin(point1[:, 1]), math.cos(point2[:, 1])), math.cos(dlon))
    out = np.array(math.atan2(s, c_val))
    if deg:
        out = out * 180 / math.pi
    if aty == "radial":
        out[(out >= 0) & (out <= 45)] = abs(out[(out >= 0) & (out <= 45)] - 45) + 45
        out[out > 45] = 90 - out[out > 45]
        out[out < 0] = out[out < 0] + 360
    return out
