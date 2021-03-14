import math


def lengths_psp(x, squared=False):
    lengths2 = (x['x1'] - x['x0']) ** 2 + (x['y1'] - x['y0']) ** 2
    if squared:
        return lengths2
    else:
        return math.sqrt(lengths2)
