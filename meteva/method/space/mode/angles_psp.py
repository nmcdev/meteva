import math


def angles_psp(x, directed=False):
    a = math.atan2(x['y1'] - x['y0'], x['x1'] - x['x0'])
    if ~directed:
        a = a % math.pi
    return a
