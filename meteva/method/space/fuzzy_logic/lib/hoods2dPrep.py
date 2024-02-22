
def hoods2dPrep(input_object, pe=None, levels=None, max_n=None, smooth_fun="hoods2dsmooth", smooth_params=None):
    out = input_object
    data = input_object['data']
    xdim = [0] * len(data)
    for i in range(0, len(data) - 1, 1):
        xdim[i] = data[i].shape[0]
    if levels is None:
        if max_n is None:
            max_n = 2 * max(xdim) - 1
        else:
            if max_n % 2 == 0:
                max_n = max_n - 1
            if max_n > 2 * max(xdim) - 1:
                print("fss2d: max_n must be less than 2N-1, where N is " + str(max(xdim)))
                return
        if max_n < 1:
            print("fss2d: max_n must be a positive integer.")
            return
        levels = range(1, max_n, 2)

    out["levels"] = levels
    out["max_n"] = max_n
    out["smooth_fun"] = smooth_fun
    out["smooth_params"] = smooth_params
    if pe is None:
        pe = [1 / item ** 2 for item in levels]
    if len(pe) == 1:
        pe = [pe] * len(levels)
    out["pe"] = pe
    return out
