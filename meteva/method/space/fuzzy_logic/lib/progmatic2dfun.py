import numpy  as np
from meteva.method.space.fuzzy_logic.lib.vxstats import vxstats


def pragmatic2dfun(s_py, ix, m_ix=None, subset=None):
    bs = vxstats(s_py, ix, which_stats="mse", subset=subset)['mse']
    if subset is None:
        if m_ix is None:
            m_ix = np.mean(ix)
        denom = np.sum((m_ix - ix) ** 2) / np.sum(~np.isnan(ix))
    else:
        if m_ix is None:
            m_ix = np.mean(ix[subset])
        denom = np.mean((m_ix - ix[subset]) ** 2)

    bss = 1 - bs / denom
    return {'bs': bs, 'bss': bss}
