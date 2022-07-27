# -*-coding:utf-8-*-

from .feature_props import feature_props
from . import bearing as bear
from .locperf import *
from .deltametric import *
from .intersect import *
from .utils import get_attributes_for_feat,remove_key_from_list



def feature_comps(look,label_ob,label_fo, which_comps=None,  alpha=0.1, k=1,
                  p=2, c=float('inf'), distfun='distmapfun',
                  deg=True, aty='compass'):

    XtmpAttributes = get_attributes_for_feat(look['grd_ob_features'])
    remove_list = ['Type', 'xrange', 'yrange', 'dim', 'xstep', 'ystep', 'warnings', 'xcol', 'yrow']  # 需要移除的属性列表
    xkeys = remove_key_from_list(list(look['grd_ob_features'].keys()), remove_list)
    X = {"m": look['grd_ob_features'][label_ob]}
    X.update(XtmpAttributes)

    YtmpAttributes = get_attributes_for_feat(look['grd_fo_features'])
    ykeys = remove_key_from_list(list(look['grd_fo_features'].keys()), remove_list)
    Y = {"m": look['grd_fo_features'][label_fo]}
    Y.update(YtmpAttributes)
    grid0 = look["grid"]

    out = {}
    if which_comps is None:
        which_comps = ["cent_dist", "angle_diff", "area_ratio", "int_area", "bdelta", "haus", "ph", "med", "msd", "fom",
                       "minsep", "bearing"]
    id1 = []
    for i, val in enumerate(["cent_dist", "angle_diff", "area_ratio", "int_area", "bearing"]):
        id1.append(val in which_comps)
    if any(id1):
        list1 = []
        if "cent_dist" in which_comps or "bearing" in which_comps:
            list1.append("centroid")
        if "area_ratio" in which_comps or "int_area" in which_comps:
            list1.append("area")
        if "angle_diff" in which_comps:
            list1.append("axis")
    id2 = []
    for i, val in enumerate(["ph", "med", "msd", "fom", "minsep"]):
        id2.append(val in which_comps)
    list2 = []
    # 需要考虑id2为矩阵的情况
    if any(id2):
        list2 = np.array(["ph", "med", "msd", "fom", "minsep"])[id2]
    if any(id1):
        x_single_props = feature_props(look,label_ob,"ob", list1)
        y_single_props = feature_props(look,label_fo,"fo", list1)
        out = {}
        if "cent_dist" in which_comps:
            x_cent_x = x_single_props["centroid"]["x"]
            x_cent_y = x_single_props["centroid"]["y"]
            y_cent_x = y_single_props["centroid"]["x"]
            y_cent_y = y_single_props["centroid"]["y"]
            out['cent_dist'] = math.sqrt((y_cent_x - x_cent_x)**2 + (y_cent_y - x_cent_y)**2)
        if "angle_diff" in which_comps:
            phiX = x_single_props['axis']['OrientationAngle']['MajorAxis'] * math.pi/180
            phiY = y_single_props['axis']['OrientationAngle']['MajorAxis'] * math.pi/180
            out['angle_diff'] = abs(math.atan2(math.sin(phiX - phiY), math.cos(phiX - phiY)) * 180/math.pi)
        if "area_ratio"in which_comps or "int_area" in which_comps:
            Xa = x_single_props['area']
            Ya = y_single_props['area']
        if "area_ratio" in which_comps:
            out['area_ratio'] = min(Xa, Ya)/max(Xa, Ya)
        if "int_area" in which_comps:
            denom = (Xa + Ya)/2
            XY = intersect(X, Y)
            XYa = np.sum(XY["m"]) * (grid0.dlon*grid0.dlat)
            #XYa = (fp.feature_props(XY, None, "area", sizefac**2, None, loc))["area"]
            out['int_area'] = XYa/denom

        if "bearing" in which_comps:
            out['bearing'] = bear.bearing(np.vstack((np.array(y_single_props['centroid']['x']), np.array(y_single_props['centroid']['y']))).transpose(),
                                          np.vstack((np.array(x_single_props['centroid']['x']), np.array(x_single_props['centroid']['y']))).transpose(), deg, aty)
        if "bdelta" in which_comps:
            out['bdelta'] = deltametric(X, Y, p, c)
        if "haus" in which_comps:
            out['haus'] = deltametric(X, Y, float('inf'), float('inf'))
        if any(id2):
            out.update(locperf(X, Y, list2, alpha, k))
        return out
'''
if __name__ == '__main__':
    grd_ob = grd_ob_feature
    grd_fo = grd_fo_feature
    
'''
