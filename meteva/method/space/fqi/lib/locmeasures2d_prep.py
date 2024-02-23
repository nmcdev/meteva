def locmeasures2d_prep(input_object, k=None, alpha=0.1, bdconst=None, p=2):
    out = input_object
    out["alpha"] = alpha
    if bdconst is None:
        out["bdconst"] = float("inf")
    else:
        out["bdconst"] = bdconst
    out["p"] = p
    out["k"] = k
    return out
