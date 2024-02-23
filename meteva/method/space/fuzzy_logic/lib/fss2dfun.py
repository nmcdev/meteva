import numpy as np


def fss2dfun(s_py, s_px, subset=None, verbose=False):
    id1 = ~np.isnan(s_py)
    id2 = ~np.isnan(s_px)
    if verbose:
        print("Finding the numbers of non-missing values for each field.\n")
    if subset is None:
        n1 = np.sum(id1)
        n2 = np.sum(id2)
        nxy = np.sum(id1 & id2)
        if verbose:
            print(nxy, " total number of non-missing points.\n")
        num = np.sum(((s_py - s_px) ** 2)) / nxy
        if verbose:
            print("MSE = ", num, "\n")
        denom = np.sum([[y ** 2 for y in x] for x in s_py]) / n1 + np.sum([[y ** 2 for y in x] for x in s_px]) / n2
    else:
        num = np.mean((s_py[subset] - s_px[subset]) ** 2)
        denom = np.mean((s_py[subset]) ** 2 + (s_px[subset]) ** 2)

    if verbose:
        print("Reference MSE = ", denom, "\n")
    return 1 - num / denom
