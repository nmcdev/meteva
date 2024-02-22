import numpy as np
from meteva.method.space.fqi.lib.ampstats import *
#import pyreadr


def uiqi(x, xhat, only_nonzero=False):
    out = {'data_name': {'verification': 'x', 'forecast': 'xhat'}}
    tmp = ampstats(x, xhat, only_nonzero=only_nonzero)
    sig12 = np.sqrt(tmp["var_fcst"] * tmp["var_vx"])
    if not np.isnan(tmp["cov"]):
        rho = tmp["cov"] / sig12
    else:
        rho = np.nan
    bb = 2 * (tmp["mean_fcst"] * tmp["mean_vx"]) / (tmp["mean_fcst"] ** 2 + tmp["mean_vx"] ** 2)
    dv = 2 * sig12 / (tmp["var_fcst"] + tmp["var_vx"])
    out["cor"] = rho
    out["brightness_bias"] = bb
    out["distortion_variability"] = dv
    if not np.isnan(rho):
        out["uiqi"] = rho * bb * dv
    else:
        out["uiqi"] = bb * dv
    return out


if __name__ == '__main__':
    #geom000 = pyreadr.read_r('../fuzzy_logic/data/geom000.Rdata')['geom000']
    #geom001 = pyreadr.read_r('../fuzzy_logic/data/geom001.Rdata')['geom001']
    #result = uiqi(geom000, geom001)
    #print("sa")
    pass
