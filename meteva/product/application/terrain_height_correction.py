import meteva


def terrain_height_correction(sta_all,start = 1):
    delta = meteva.base.read_stadata_from_micaps3(meteva.base.terrain_height_correction_data)
    ids = list(set(sta_all["id"].values.tolist()))
    delta = meteva.base.in_id_list(delta,ids)
    #print(delta)
    delta["level"] = meteva.base.IV
    delta["time"] = meteva.base.IV
    delta["dtime"] = meteva.base.IV
    datanames = meteva.base.get_stadata_names(sta_all)
    sta_all_delta = meteva.base.combine_expand_IV(sta_all,delta)
    for i in range(start,len(datanames)):
        name = datanames[i]
        sta_all_delta[name] += sta_all_delta.iloc[:,-1]
    datanames = meteva.base.get_stadata_names(sta_all_delta)
    sta_all_corrected = sta_all_delta.drop(columns = [datanames[-1]])
    return sta_all_corrected