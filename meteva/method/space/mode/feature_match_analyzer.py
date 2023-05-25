import copy
import numpy as np
from .utils import get_attributes_for_feat, remove_key_from_list
from .feature_props import feature_props
from .feature_comps import feature_comps
from .feature_table import feature_table
from .interester import interester
from .feature_axis import feature_axis
import meteva


def feature_match_analyzer(look_match, which_comps=None, sizefac=1, alpha=0.1, k=1, p=2,
                           c=float("inf"), distfun="distmapfun", y=None, matches=None, object=None):


    x = copy.deepcopy(look_match)
    if which_comps is None:
        which_comps = ["cent.dist", "angle.diff", "area.ratio",
                       "int.area", "bdelta", "haus", "ph", "med", "msd", "fom",
                       "minsep", "bearing"]
    if x['match_type'] == "centmatch" or x['match_type'] == "minboundmatch" or x["match_type"] == "deltamm" or x["match_type"][0] == "MergeForce":
        n = x['matches'].shape[0]
        if n > 0:
            out = []
            a = x
            ## loc 没有值
            if "loc" in a.keys():
                loc = a['loc']
            else:
                loc = None
            #Xfeats = x['Xlabelsfeature']
            #Yfeats = x['Ylabelsfeature']
            Xfeats = x['grd_ob_features']
            Yfeats = x['grd_fo_features']
            #xattribute = get_attributes_for_feat(Xfeats)
            #yattribute = get_attributes_for_feat(Yfeats)
            remove_list = ['Type', 'xrange', 'yrange', 'dim', 'xstep', 'ystep', 'warnings', 'xcol', 'yrow', 'area','label_count']
            #print(Xfeats.keys())
            xkeys = remove_key_from_list(list(Xfeats.keys()), remove_list)
            ykeys = remove_key_from_list(list(Yfeats.keys()), remove_list)
            for i in range(n):
                j = x['matches'][i, 0]-1
                k = x['matches'][i, 1]-1
                ymat = Yfeats[ykeys[j]]
                xmat = Xfeats[xkeys[k]]

                #if xmat.dtype.name is not 'bool':
                #    xmat = (xmat == 1)
                #if ymat.dtype.name is not 'bool':
                #    ymat = (ymat == 1)
                #ymat = {"m": ymat}
                #ymat.update(yattribute)
                #xmat = {"m": xmat}
                #xmat.update(xattribute)
                #out.append(feature_comps(grd_fo=ymat, grd_ob=xmat, which_comps=which_comps,
                #                         sizefac=sizefac, alpha=alpha, k=k, p=p, c=c, distfun=distfun, loc=loc))
                out.append(feature_comps(look_match,label_ob=k+1,label_fo=j+1, which_comps=which_comps,
                                         sizefac=sizefac, alpha=alpha, k=k, p=p, c=c, distfun=distfun, loc=loc))
        else:
            out = "No matches found"
        return out

    elif x['match_type'] == "deltamm":
        if matches is not None:
            obj = matches
        elif y is not None:
            obj = y
        else:
            obj = x
        if "loc" in obj.keys():
            loc = obj['loc']
        else:
            loc = None
        Yfeats = obj['Ylabelsfeature']
        Xfeats = obj['Xlabelsfeature']
        xattribute = get_attributes_for_feat(Xfeats)
        yattribute = get_attributes_for_feat(Yfeats)
        if obj['unmatched']['matches'].shape[0] == 0:
            out = "No matches found"
        else:
            n = obj['unmatched']['matches'].shape[0]
            out = []
            remove_list = ['Type', 'xrange', 'yrange', 'dim', 'xstep', 'ystep', 'warnings', 'xcol', 'yrow', 'area']
            xkeys = remove_key_from_list(list(Xfeats.keys()), remove_list)
            ykeys = remove_key_from_list(list(Yfeats.keys()), remove_list)
            for i in range(n):
                ymat = Yfeats[ykeys[i]]
                xmat = Xfeats[xkeys[i]]
                if xmat.dtype.name is not 'bool':
                    xmat = (xmat == 1)
                if ymat.dtype.name is not 'bool':
                    ymat = (ymat == 1)
                ymat = {"m": ymat}
                ymat.update(yattribute)
                xmat = {"m": xmat}
                xmat.update(xattribute)
                out.append(feature_comps(Y=ymat, X=xmat, which_comps=which_comps, sizefac=sizefac,
                                         alpha=alpha, k=k, p=p, c=c, distfun=distfun, loc=loc))
        return out
    else:
        print("类型错误")
        raise Exception("类型错误")

'''
if __name__ == '__main__':
    data1 = np.load("../../centmatchResult.npy", allow_pickle=True).tolist()
    data2 = np.load("../../deltammResult_PA2.npy", allow_pickle=True).tolist()
    data1['Xlabelsfeature'] = data2['Xlabelsfeature']
    data1['Ylabelsfeature'] = data2['Ylabelsfeature']
    out1 = feature_match_analyzer(data1)
    out2 = feature_match_analyzer(data2)
    print("hello")
'''


def get_summary(feature):
    out = copy.deepcopy(feature)
    #print(out.keys())
    if "is_summary" not in out.keys():
        out["is_summary"] = True
        if out["interester"] is not None:
            nmatch = out["match_count"]
            interest = out["interester"]
            index = np.arange(nmatch)
            dat = interest["total_interest"][index, index]
            out["interester"] = dat

        label_list_matched = out["label_list_matched"]
        for i in label_list_matched:
            del out[i]["feature_axis"]["ob"]["point"]
            del out[i]["feature_axis"]["ob"]["MajorAxis"]
            del out[i]["feature_axis"]["ob"]["MinorAxis"]
            del out[i]["feature_axis"]["ob"]["aspect_ratio"]
            del out[i]["feature_axis"]["ob"]["OrientationAngle"]["MinorAxis"]
            del out[i]["feature_axis"]["ob"]["pts"]
            del out[i]["feature_axis"]["ob"]["MidPoint"]
            del out[i]["feature_axis"]["ob"]["sma_fit"]
            del out[i]["feature_axis"]["ob"]["phi"]

            del out[i]["feature_axis"]["fo"]["point"]
            del out[i]["feature_axis"]["fo"]["MajorAxis"]
            del out[i]["feature_axis"]["fo"]["MinorAxis"]
            del out[i]["feature_axis"]["fo"]["aspect_ratio"]
            del out[i]["feature_axis"]["fo"]["OrientationAngle"]["MinorAxis"]
            del out[i]["feature_axis"]["fo"]["pts"]
            del out[i]["feature_axis"]["fo"]["MidPoint"]
            del out[i]["feature_axis"]["fo"]["sma_fit"]
            del out[i]["feature_axis"]["fo"]["phi"]

            del out[i]["feature_props"]["ob"]["axis"]
            del out[i]["feature_props"]["fo"]["axis"]

        miss_labels = out["unmatched"]['ob']

        for i in miss_labels:
            del out[i]["feature_axis"]["ob"]["point"]
            del out[i]["feature_axis"]["ob"]["MajorAxis"]
            del out[i]["feature_axis"]["ob"]["MinorAxis"]
            del out[i]["feature_axis"]["ob"]["aspect_ratio"]
            del out[i]["feature_axis"]["ob"]["OrientationAngle"]["MinorAxis"]
            del out[i]["feature_axis"]["ob"]["pts"]
            del out[i]["feature_axis"]["ob"]["MidPoint"]
            del out[i]["feature_axis"]["ob"]["sma_fit"]
            del out[i]["feature_axis"]["ob"]["phi"]
            del out[i]["feature_props"]["ob"]["axis"]


        false_alarm_labels = out["unmatched"]["fo"]
        for i in false_alarm_labels:
            del out[i]["feature_axis"]["fo"]["point"]
            del out[i]["feature_axis"]["fo"]["MajorAxis"]
            del out[i]["feature_axis"]["fo"]["MinorAxis"]
            del out[i]["feature_axis"]["fo"]["aspect_ratio"]
            del out[i]["feature_axis"]["fo"]["OrientationAngle"]["MinorAxis"]
            del out[i]["feature_axis"]["fo"]["pts"]
            del out[i]["feature_axis"]["fo"]["MidPoint"]
            del out[i]["feature_axis"]["fo"]["sma_fit"]
            del out[i]["feature_axis"]["fo"]["phi"]
            del out[i]["feature_props"]["fo"]["axis"]

    return out

def feature_merged_analyzer(look_merge,summary =True):
    nmatch = look_merge["match_count"]
    out = {}
    out["time"] = meteva.base.all_type_time_to_str(look_merge["grd_fo"]["time"].values[0])
    out["dtime"] = int(look_merge["grd_fo"]["dtime"].values[0])
    out["member"] = look_merge["grd_fo"]["member"].values[0]
    out["match_count"] = nmatch
    f_table = feature_table(look_merge)
    out["feature_table"] = f_table
    interest = interester(look_merge)
    out["interester"] = interest

    label_list_matched = look_merge["label_list_matched"]
    out["label_list_matched"] = label_list_matched
    out["unmatched"] = look_merge["unmatched"]

    for i in label_list_matched:
        f_axis_ob = feature_axis(look_merge, i, "ob")
        f_axis_fo = feature_axis(look_merge, i, "fo")
        f_props_ob = feature_props(look_merge, i, "ob")
        f_props_fo = feature_props(look_merge, i, "fo")
        f_comps = feature_comps(look_merge, i, i)
        out1 = {}
        #print(f_axis_ob.keys())

        out1["feature_axis"] = {"ob":f_axis_ob,"fo":f_axis_fo}
        out1["feature_props"]= {"ob":f_props_ob,"fo":f_props_fo}
        out1["feature_comps"] = f_comps

        out[i] = out1

    miss_labels = look_merge["unmatched"]['ob']
    for i in miss_labels:
        f_axis_ob = feature_axis(look_merge, i, "ob")
        f_props_ob = feature_props(look_merge, i, "ob")
        out1 = {}
        out1["feature_axis"] = {"ob":f_axis_ob}
        out1["feature_props"]= {"ob":f_props_ob}
        out[i] = out1


    false_alarm_labels = look_merge["unmatched"]["fo"]
    for i in false_alarm_labels:
        f_axis_fo = feature_axis(look_merge, i, "fo")
        f_props_fo = feature_props(look_merge, i, "fo")
        if i in out.keys():
            out1 = out[i]
            out1["feature_axis"]["fo"]= f_axis_fo
            out1["feature_props"]["fo"]= f_props_fo
        else:
            out1 = {}
            out1["feature_axis"] = {"fo": f_axis_fo}
            out1["feature_props"] = {"fo": f_props_fo}

        out[i] = out1

    if summary:
        out = get_summary(out)

    return out