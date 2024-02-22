import numbers


def datagrabber_spatialVx(x, time_point=1, obs=1, model=1):
    if not isinstance(time_point, numbers.Number):
        raise Exception("datagrabber: invalid time.point argument.")
    if not isinstance(obs, numbers.Number):
        raise Exception("datagrabber: invalid obs argument.  Must be numeric.")
    if not isinstance(obs, numbers.Number):
        raise Exception("datagrabber: invalid model argument.  Must be numeric.")
    xdim = x["xdim"]
    nobs = x["nobs"]
    nf = x["nforecast"]
    vx = x['X']
    if nobs > 1:
        vx = vx[obs]
    fcst = x['Xhat']
    if nf > 1:
        fcst = fcst[model]
    if len(xdim) == 3:
        vx = vx[:, :, time_point]
        fcst = fcst[:, :, time_point]
    out = {"X": vx, "Xhat": fcst}
    return out
