import copy


def hoods2dSetUpLists(input_object, which_methods, mat):
    out = {}
    if "mincvr" in which_methods:
        out['mincvr'] = {}
        out['mincvr']['pod'] = copy.copy(mat)
        out['mincvr']['far'] = copy.copy(mat)
        out['mincvr']['ets'] = copy.copy(mat)

    if "multi_event" in which_methods:
        out['multi_event'] = {}
        out['multi_event']['pod'] = copy.copy(mat)
        out['multi_event']['f'] = copy.copy(mat)
        out['multi_event']['hk'] = copy.copy(mat)

    if "fuzzy" in which_methods:
        out['fuzzy'] = {}
        out['fuzzy']['pod'] = copy.copy(mat)
        out['fuzzy']['far'] = copy.copy(mat)
        out['fuzzy']['ets'] = copy.copy(mat)

    if "joint" in which_methods:
        out['joint'] = {}
        out['joint']['pod'] = copy.copy(mat)
        out['joint']['far'] = copy.copy(mat)
        out['joint']['ets'] = copy.copy(mat)

    if "fss" in which_methods:
        out['fss'] = {}
        out['fss']['values'] = copy.copy(mat)
        out['fss']['fss_random'] = out['fss']['fss_uniform'] = 0

    if "pragmatic" in which_methods:
        out['pragmatic'] = {}
        out['pragmatic']['bs'] = copy.copy(mat)
        out['pragmatic']['bss'] = copy.copy(mat)

    return out
