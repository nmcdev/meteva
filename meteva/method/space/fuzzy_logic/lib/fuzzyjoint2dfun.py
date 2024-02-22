import numpy as np
import pandas


def fuzzyjoint2dfun(s_py, s_px, subset=None):
    out = {}
    if type(s_px) == pandas.DataFrame:
        s_px = s_px.fillna(0)
    else:
        s_px = pandas.DataFrame(s_px).fillna(0)
    if type(s_py) == pandas.DataFrame:
        s_py = s_py.fillna(0)
    else:
        s_py = pandas.DataFrame(s_py).fillna(0)

    def vxfun(n11, n01, n10, n00):
        pod = n11 / (n11 + n01)
        far = n10 / (n11 + n10)
        hits_random = (n11 + n01) * (n11 + n10) / (n11 + n01 + n10 + n00)
        ets = (n11 - hits_random) / (n11 + n01 + n10 - hits_random)
        return {'pod': pod, 'far': far, 'ets': ets}

    if subset is None:
        # https://stackoverflow.com/questions/35517220/finding-minima-and-replacing-values-in-pandas-dataframe
        hits = sum(np.sum(np.minimum(s_px, s_py)))  #命中等于x和y中的最小值之和
        miss = sum(np.sum(np.minimum(s_px, 1 - s_py)))  # 漏报等于x 和1-y的最小值 之和
        fa = sum(np.sum(np.minimum(1 - s_px, s_py)))
        cn = sum(np.sum(np.minimum(1 - s_px, 1 - s_py)))
        out["fuzzy"] = vxfun(hits, miss, fa, cn)
        hits = sum(np.sum(s_px * s_py))
        miss = sum(np.sum(s_px * (1 - s_py)))
        fa = sum(np.sum((1 - s_px) * s_py))
        cn = sum(np.sum((1 - s_px) * (1 - s_py)))
        out["joint"] = vxfun(hits, miss, fa, cn)
    else:
        hits = sum(s_px[subset] < s_py[subset])
        miss = sum(s_px[subset] < (1 - s_py[subset]))
        fa = sum((1 - s_px[subset]) < s_py[subset])
        cn = sum((1 - s_px[subset]) < (1 - s_py[subset]))
        out["fuzzy"] = vxfun(hits, miss, fa, cn)
        hits = sum((s_px[subset]) * (s_py[subset]))
        miss = sum((s_px[subset]) * (1 - s_py[subset]))
        fa = sum((1 - s_px[subset]) * s_py[subset])
        cn = sum((1 - s_px[subset]) * (1 - s_py[subset]))
        out["joint"] = vxfun(hits, miss, fa, cn)
    return out
