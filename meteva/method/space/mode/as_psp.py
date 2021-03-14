import math


def as_psp(x):
    result = {}
    angle = x['angle']
    x1 = (math.cos(angle)) * x['length'] / 2 + x['xmid']
    x0 = x['xmid'] - math.cos(angle) * x['length'] / 2
    y0 = - math.sin(angle) * x['length'] / 2 + x['ymid']
    y1 = x['ymid'] + math.sin(angle) * x['length'] / 2
    result['ends'] = {'x0': x0, 'y0': y0, 'x1': x1, 'y1': y1}
    return result
