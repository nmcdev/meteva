from meteva.method.space.fuzzy_logic.lib.vxstats import vxstats


def mincvg2dfun(s_iy, s_ix, subset=None):
    out = vxstats(s_iy, s_ix, which_stats=["pod", "far", "ets"])
    return out
