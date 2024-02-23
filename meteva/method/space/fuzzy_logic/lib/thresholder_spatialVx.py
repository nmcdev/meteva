from meteva.method.space.fuzzy_logic.lib.datagrabber_spatialVx import datagrabber_spatialVx
from meteva.method.space.fuzzy_logic.lib.thresholder import thresholder


def thresholder_spatialVx(x, func_type=None, th=1, rule=">=", replace_with=0, time_point=1, obs=1,
                          model=1, **args):
    if func_type is None:
        func_type = ["binary", "replace.below"]
    dat = datagrabber_spatialVx(x, time_point=time_point, obs=obs, model=model)
    x_field = dat['X']
    xhat_field = dat['Xhat']
    u = x['thresholds']
    u1 = u[0][th]
    u2 = u[1][th]
    out1 = thresholder(x_field, func_type=func_type, th=u1, rule=rule, replace_with=replace_with)
    out2 = thresholder(xhat_field, func_type=func_type, th=u2, rule=rule, replace_with=replace_with)
    return {'X': out1, 'Xhat': out2}
