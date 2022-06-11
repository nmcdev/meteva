# -*-coding:utf-8-*-
import numpy as np
from .feature_axis import feature_axis


def feature_props(look,label,ob_or_fo = None,which_comps=None, q=None):
    if ob_or_fo =="ob":
        tmp = look['grd_ob_features'][label]
    elif ob_or_fo == "fo":
        tmp = look['grd_fo_features'][label]
    else:
        if label in look["grd_features"].keys():
            tmp = look['grd_features'][label]
        else:
            return None
    grid0 = look["grid"]
    #x = np.zeros((grid0.nlat,grid0.nlon))
    #print("****")
    #print(tmp)
    #x[tmp] = 1
    #x = copy.deepcopy(tmp)
    if which_comps is None:
        which_comps = ["centroid", "area", "axis", "intensity"]
    if q is None:
        q = [0,0.05,0.1,0.25,0.5, 0.75,0.9,0.95,1]
    out = {}

    if "centroid" in which_comps:
        #xd = x.shape
        #dim0 = xd[0]
        #dim1 = xd[1]
        #dim0 = grid0.nlat
        #dim1 = grid0.nlon
        #range0 = np.tile(np.arange(dim0), dim1)
        #range1 = (np.arange(dim1)).repeat(dim0)
        #loc = np.stack((range0, range1), axis=-1)
        #xbool = np.reshape(x, x.size, 'F')
        #xcen = grid0.slon + np.mean(loc[:, 0][xbool == 1]) * grid0.dlon
        #ycen = grid0.slat + np.mean(loc[:, 1][xbool == 1]) * grid0.dlat
        xcen = grid0.slon + np.mean(tmp[1]) * grid0.dlon
        ycen = grid0.slat + np.mean(tmp[0]) * grid0.dlat
        out['centroid'] = {"x": xcen, "y": ycen}
    if "area" in which_comps:
        #out["area"] = np.sum(x) * grid0.dlon*grid0.dlat
        out["area"] = len(tmp[0]) * grid0.dlon * grid0.dlat
    if "axis" in which_comps:
        out["axis"] = feature_axis(look,label,ob_or_fo = ob_or_fo, fac = grid0.dlon*grid0.dlat)
    if "intensity" in which_comps:
       #ivec = {}
       # df = pd.DataFrame(np.array(im[x]), columns=q)
       # for i, val in q:
       #     ivec[val] = df.quantile(val)
        if ob_or_fo == "ob":
            values = look['grd_ob'].values.squeeze()
            labels = look["grd_ob_label"].values.squeeze()
        elif ob_or_fo == "fo":
            values = look['grd_fo'].values.squeeze()
            labels = look["grd_fo_label"].values.squeeze()
        else:
            values = look['grd'].values.squeeze()
            labels = look["grd_label"].values.squeeze()
        valid = values[labels == label]
        ivec = np.quantile(valid,q)
        out["intensity"] = ivec
    return out
