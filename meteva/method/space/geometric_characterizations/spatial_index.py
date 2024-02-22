from meteva.method.space.geometric_characterizations.lib.util import get_attributes
from meteva.method.space.geometric_characterizations.lib.datagrabber_spatialVx import datagrabber_spatialVx
import pandas as pd
from meteva.method.space.geometric_characterizations.aindex import aindex
from meteva.method.space.geometric_characterizations.cindex import cindex
from meteva.method.space.geometric_characterizations.sindex import sindex


def spatial_index(input_object, func_type, thresh=None, dx=1, dy=1, time_point=1, obs=1, model=1):
    attributes = get_attributes(input_object)
    dat = datagrabber_spatialVx(input_object, time_point=time_point - 1, obs=obs - 1, model=model - 1)
    if isinstance(input_object["time"], list):
        attributes["time"] = input_object["time"][time_point]
    else:
        attributes["time"] = input_object["time"]
    if isinstance(input_object["obsname"], list):
        attributes["obs_name"] = input_object["obsname"][obs]
    else:
        attributes["obs_name"] = input_object["obsname"]
    if isinstance(input_object["modelname"], list):
        attributes["model_name"] = input_object["modelname"][model]
    else:
        attributes["model_name"] = input_object["modelname"]
    grd_ob = dat["X"]
    grd_fo = dat["Xhat"]
    if func_type == "a":
        res1 = aindex(grd_ob, thresh=thresh, dx=dx, dy=dy)
        res2 = aindex(grd_fo, thresh=thresh, dx=dx, dy=dy)
    elif func_type == "c":
        res1 = cindex(grd_ob, thresh=thresh)
        res2 = cindex(grd_fo, thresh=thresh)
    elif func_type == "s":
        res1 = sindex(grd_ob, thresh=thresh, loc=attributes["loc"])
        res2 = sindex(grd_fo, thresh=thresh, loc=attributes["loc"])
    else:
        raise Exception("func_type错误")
    res = pd.DataFrame({attributes["obs_name"]: res1, attributes["model_name"]: res2}, index=[0])
    return res
