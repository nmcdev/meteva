import numpy as np
import scipy.stats as st
#from .regress2 import regress2



def sma(data):
    x = data['x']
    y = data['y']
    slope =0
    intercept = 0
    try:
        #coeff = regress2(x, y, _method_type_2="reduced major axis")
        slope, intercept, r_value, p_value, std_err = st.linregress(x, y)
    except:
        pass
    while np.isnan(slope):
        maxx = np.max(x) - np.min(x)
        maxy = np.max(y) - np.min(y)
        maxd = max(maxx,maxy)
        x1 = np.random.randn(len(x))* 0.01 * maxd + x
        y1 = np.random.randn(len(y))* 0.01 * maxd + y
        #coeff = regress2(x1, y1, _method_type_2="reduced major axis")
        slope, intercept, r_value, p_value, std_err = st.linregress(x1, y1)


    frome = (min(y + slope * x) - intercept) / (2 * slope)
    to = (max(y + slope * x) - intercept) / (2 * slope)
    l = {}
    l["slope"] = slope
    l["intercept"] = intercept
    #l['coef'] = coeff
    l['from'] = frome
    l['to'] = to
    return l


# def sma_bak(data, log="", method="SMA",
#         type="elevation", alpha=0.05, slope_test=None, elev_test=None,
#         multcomp=False, multcompmethod="default", robust=False, V=np.zeros([2, 2]), n_min=3, quiet=False, *params):
#     x = data['x']
#     y = data['y']
#     coeff = None
#     try:
#         coeff = regress2(x, y, _method_type_2="reduced major axis")
#     except:
#         pass
#     while coeff is None or (np.isnan(coeff["predict"][0])) or coeff['slope']==0:
#         maxx = np.max(x) - np.min(x)
#         maxy = np.max(y) - np.min(y)
#         maxd = max(maxx,maxy)
#         x1 = np.random.randn(len(x))* 0.01 * maxd + x
#         y1 = np.random.randn(len(y))* 0.01 * maxd + y
#         #coeff = regress2(x1, y1, _method_type_2="reduced major axis")
#         coeff = regress2(x1, y1, _method_type_2="major axis")
#         #print(y)
#     #print(coeff)
#     slope = coeff['slope']
#     intercept = coeff['intercept']
#
#     frome = (min(y + slope * x) - intercept) / (2 * slope)
#     to = (max(y + slope * x) - intercept) / (2 * slope)
#     l = {}
#     l['coef'] = coeff
#     l['from'] = frome
#     l['to'] = to
#     return l
