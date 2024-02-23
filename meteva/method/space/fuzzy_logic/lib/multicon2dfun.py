from meteva.method.space.fuzzy_logic.lib.vxstats import vxstats


def multicon2dfun(s_iy, ix, subset=None):
    out = vxstats(s_iy, ix, which_stats=["pod", "f", "hk"])
    return out
