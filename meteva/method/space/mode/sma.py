import numpy as np

from .regress2 import regress2


def sma(data, log="", method="SMA",
        type="elevation", alpha=0.05, slope_test=None, elev_test=None,
        multcomp=False, multcompmethod="default", robust=False, V=np.zeros([2, 2]), n_min=3, quiet=False, *params):
    x = data['x']
    y = data['y']

    coeff = regress2(x, y, _method_type_2="reduced major axis")
    while(np.isnan(coeff["predict"][0])) or coeff['slope']==0:
        maxx = np.max(x) - np.min(x)
        maxy = np.max(y) - np.min(x)
        maxd = max(maxx,maxy)
        x1 = np.random.randn(len(x))* 0.01 * maxd + x
        y1 = np.random.randn(len(y))* 0.01 * maxd + y
        #coeff = regress2(x1, y1, _method_type_2="reduced major axis")
        coeff = regress2(x1, y1, _method_type_2="major axis")
        #print(x)
        #print(y)
    #print(coeff)
    slope = coeff['slope']
    intercept = coeff['intercept']

    frome = (min(y + slope * x) - intercept) / (2 * slope)
    to = (max(y + slope * x) - intercept) / (2 * slope)
    l = {}
    l['coef'] = coeff
    l['from'] = frome
    l['to'] = to
    return l
