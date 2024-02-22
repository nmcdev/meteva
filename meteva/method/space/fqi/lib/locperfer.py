from .im import im
from .solutionset import solutionset
from .locperf import locperf


def locperfer(x1, x2, thresh, k):
    x1 = im(x1)
    x1["v"] = (x1["v"] >= thresh)
    ix1 = solutionset(x1)
    return locperf(X=x2, Y=ix1, which_stats = "ph", k = k)["ph"]
