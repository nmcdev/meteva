# -*-coding:utf-8-*-
import sys
sys.path.append(r'F:\Work\MODE\Submit')
from .distmap import *


def intersect(a, b):
    a_x_min = a["xrange"][0]
    a_x_max = a["xrange"][1]
    a_y_min = a["yrange"][0]
    a_y_max = a["yrange"][1]
    b_x_min = b["xrange"][0]
    b_x_max = b["xrange"][1]
    b_y_min = b["yrange"][0]
    b_y_max = b["yrange"][1]
    x_min = max(a_x_min, b_x_min)
    x_max = min(a_x_max, b_x_max)
    y_min = max(a_y_min, b_y_min)
    y_max = min(a_y_max, b_y_max)
    x_range = [x_min, x_max]
    y_range = [y_min, y_max]
    window = {"x_range": x_range, "y_range": y_range}
    a = rebound(a, window)
    b = rebound(b, window)
    result = a
    am = np.array(a["m"])
    bm = np.array(b["m"])
    rlen, clen = am.shape
    m = am * bm
    result["m"] = m
    return result
