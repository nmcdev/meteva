import numpy as np
import math


def zapsmall(x, digits = 7):
    x = np.array(x)
    ina = x is np.nan
    mx = max(abs(x[~ina]))
    round_digis = digits
    if mx > 0:
        round_digis = math.floor(max(0, digits - (np.log10(mx))))
    return np.round(x,  round_digis)
