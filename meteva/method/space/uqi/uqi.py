import numpy as np
from meteva.method.space.fqi.lib.ampstats import *
#import pyreadr


def uqi(x, xhat, only_nonzero=False):
    out = {}
    tmp = ampstats(x, xhat, only_nonzero=only_nonzero)
    sig12 = np.sqrt(tmp["var_fcst"] * tmp["var_vx"])
    if not np.isnan(tmp["cov"]):
        rho = tmp["cov"] / sig12
    else:
        rho = np.nan
    bb = 2 * (tmp["mean_fcst"] * tmp["mean_vx"]) / (tmp["mean_fcst"] ** 2 + tmp["mean_vx"] ** 2)
    dv = 2 * sig12 / (tmp["var_fcst"] + tmp["var_vx"])
    out["corrcoef_score"] = rho
    out["brightness_score"] = bb
    out["variability_score"] = dv
    if not np.isnan(rho):
        out["uqi"] = rho * bb * dv
    else:
        out["uqi"] = bb * dv
    return out


if __name__ == '__main__':
    #geom000 = pyreadr.read_r('../fuzzy_logic/data/geom000.Rdata')['geom000']
    #geom001 = pyreadr.read_r('../fuzzy_logic/data/geom001.Rdata')['geom001']
    #result = uiqi(geom000, geom001)
    #print("sa")
    pass
