import math


def midpoints_psp(axis, squared=False):
    x = (axis['x1'] + axis['x0']) / 2
    y = (axis['y1'] + axis['y0']) / 2
    #y = (axis['y1'] - axis['y0']) ** 2
    return {'x': x, 'y': y, 'window': axis}
