import numpy as np
import meteva
import math
import sys
import copy
from . import data_pre
from .feature_props import feature_props
from meteva.method.space.mode.feature_finder import get_disk_kernel,propCounts
from scipy.ndimage import convolve
from scipy.spatial import cKDTree

def rotate_and_pull(pts,angle,gama):
    '''
    根据目标的主轴方向和形态，确定变形后坐标
    :param pts:
    :param angle:
    :param gama:
    :return:
    '''
    x = (math.cos(angle) * pts[:, 0] + math.sin(angle) * pts[:, 1])*gama
    y = -math.sin(angle) * pts[:, 0] + math.cos(angle) * pts[:, 1]
    pts_new = np.array([x,y]).T
    return  pts_new


def caculate_near_rate(pts1,pts2,near_dis,add_min_d = False):
    # pts1_center = np.mean(pts1,axis=0)
    # pts2_center = np.mean(pts2,axis=0)
    # dis_center = (pts1_center[0]-pts2_center[0])**2 + (pts1_center[1]-pts2_center[1])**2
    # if dis_center < near_dis * near_dis:
    #     return 1
    axis_feature1 = meteva.method.mode.caculate_feature_axis(pts1)
    lengths_max = axis_feature1["lengths"]["MajorAxis"]
    lengths_min = axis_feature1["lengths"]["MinorAxis"]
    gama = max(max(lengths_min,near_dis)/max(lengths_max,near_dis),0.5) #计算主轴方向距离压缩比例
    angle= axis_feature1["OrientationAngle"]["MajorAxis"] * math.pi/180
    pts1_rp = rotate_and_pull(pts1,angle,gama)
    pts2_rp = rotate_and_pull(pts2,angle,gama)
    tree = cKDTree(pts1_rp)
    d,_ = tree.query(pts2_rp, k=1)
    if add_min_d:
        min_d = np.min(d)
        rate = len(d[d<near_dis])/len(d) + 0.001/min_d
    else:
        rate = len(d[d < near_dis]) / len(d)
    return rate

def caculate_cover_rate(pts1,pts2,near_dis,ob_rate = 1):

    '''
    计算观测目标和预报目标之间的覆盖度
    :param pts1:
    :param pts2:
    :param near_dis:
    :return:
    '''
    near_rate1 = caculate_near_rate(pts2,pts1,near_dis)
    count1 =near_rate1 * pts1.shape[0]

    near_rate2 = caculate_near_rate(pts1,pts2,near_dis)
    count2 =near_rate2 * pts2.shape[0]

    rate = (count1  + count2* ob_rate) /(pts1.shape[0] +pts2.shape[0]* ob_rate)
    rate -= 0.01 / pts2.shape[0]
    return rate

def combined_near_labels(labelsfeature,near_dis,near_rate):
    labels =[]
    label_count0 = labelsfeature["label_count"]
    labelsfeature_new = copy.deepcopy(labelsfeature)
    if label_count0 ==0:
        return labelsfeature_new
    for i in range(label_count0):
        labelsfeature_new.pop(i+1)

    #print(labelsfeature.keys())
    for i in range(label_count0):
        label_ps1 = np.array([labelsfeature[i+1][1],labelsfeature[i+1][0]]).T
        labels.append(label_ps1)

    max_rate = 1
    while max_rate >= near_rate:
        nlabels = len(labels)
        rate_array = np.zeros((nlabels,nlabels))
        for i in range(0,nlabels):
            rate = 0
            for j in range(nlabels):
                if j==i:continue
                rate = caculate_near_rate(labels[i],labels[j],near_dis,add_min_d=True)
                rate_array[i,j] = rate
                if rate >= 1:
                    break
            if rate >= 1:
                break
        max_rate = np.max(rate_array)
        if max_rate > near_rate:
            index = np.where(rate_array == max_rate)
            i = index[0][0]
            j = index[1][0]
            labels[i] = np.append(labels[i],labels[j],axis=0)
            del labels[j]




    #print(len(labels))
    area_list = []
    for i in range(len(labels)):
        area_list.append(labels[i].shape[0])
    area_array = np.array(area_list)
    #print(area_list)

    sort_index = len(labels)-1 - np.argsort(np.argsort(area_array))

    for i in range(len(labels)):
        j = sort_index[i]
        labelsfeature_new[j+1] = (labels[i][:,1],labels[i][:,0])
    area_array.sort()

    labelsfeature_new["area"] =area_array[::-1]
    labelsfeature_new["label_count"] = len(labels)
    #print(labelsfeature)
    return labelsfeature_new


def unimatch_pro(look_ob,look_fo,cover_dis,cover_rate):
    out = copy.deepcopy(look_fo)

    grid0= look_ob["grid"]
    near_dis = cover_dis/111/grid0.dlon

    ob_id_list = look_ob["id_list"]
    fo_id_list = look_fo["id_list"]
    label_count_ob = len(ob_id_list)
    label_count_fo = len(fo_id_list)

    if label_count_ob >0 and label_count_fo >0:
        labels_ob = []
        for i in range(label_count_ob):
            id1 = ob_id_list[i]
            label_ps1 = np.array([look_ob["grd_features"][id1][1],look_ob["grd_features"][id1][0]]).T
            labels_ob.append(label_ps1)

        labels_fo = []

        for i in range(label_count_fo):
            id1 = fo_id_list[i]
            label_ps2 = np.array([look_fo["grd_features"][id1][1],look_fo["grd_features"][id1][0]]).T
            labels_fo.append(label_ps2)

        max_rate = 1
        combined_fo_dict = {}
        used_ob = np.ones(label_count_ob)
        used_fo = np.ones(label_count_fo)
        while max_rate >= cover_rate:
            max_rate = 0
            max_i = -1
            max_j_list = None
            max_pts_fo = None
            for i in range(label_count_ob):
                if used_ob[i] ==0:continue
                rate_1row = np.zeros(label_count_fo)
                for j in range(label_count_fo):
                    if used_fo[j] ==0:continue
                    rate_1row[j] = caculate_cover_rate(labels_ob[i],labels_fo[j],near_dis)
                index = np.argsort(-rate_1row)
                pts_fo = labels_fo[index[0]]
                for j in range(0,label_count_fo):
                    if rate_1row[index[j]] > 0:
                        if j > 0:
                            pts_fo =  np.append(pts_fo,labels_fo[index[j]],axis=0)
                            rate_c = caculate_cover_rate(labels_ob[i],pts_fo,near_dis)
                            if rate_c > max_rate:
                                max_rate = rate_c
                                max_i = i
                                max_j_list = index[0:j+1]
                                max_pts_fo = pts_fo
                        else:
                            rate_c = rate_1row[index[j]]
                            if rate_c> max_rate:
                                max_rate = rate_c
                                max_i = i
                                max_j_list = [index[0]]
                                max_pts_fo = pts_fo

                    else:
                        break
                    if max_rate>=1:
                        break
                if max_rate>=1:
                    break

            if max_rate > cover_rate:
                id1 = ob_id_list[max_i]
                combined_fo_dict[id1] = (max_pts_fo[:,1],max_pts_fo[:,0])
                used_fo[max_j_list] = 0
                used_ob[max_i] =0


        id_list = list(combined_fo_dict.keys())
        nmatch =0
        if len(id_list)>0:
            nmatch = max(combined_fo_dict.keys())
        #print(combined_fo_dict)

        #kk = np.max(np.array(ob_id_list))
        if "max_label" in look_ob.keys():
            kk = look_ob["max_label"]
        else:
            kk = np.max(np.array(ob_id_list))
        for k in range(len(labels_fo)):
            if used_fo[k] > 0:
                kk += 1
                combined_fo_dict[kk] = (labels_fo[k][:, 1], labels_fo[k][:, 0])
                id_list.append(kk)

        grd_fo_labeled = look_fo["grd"].copy()
        grd_fo_labeled.attrs["var_name"] = "目标编号"
        label_value = np.zeros((grid0.nlat, grid0.nlon))
        for key in combined_fo_dict.keys():
            label = combined_fo_dict[key]
            label_value[label] = key
        grd_fo_labeled.values[:] = label_value[:]
        combined_fo_dict["label_count"] = len(id_list)
        for key in look_fo["grd_features"].keys():
            if key not in combined_fo_dict.keys():
                if isinstance(key,str):
                    combined_fo_dict[key] = copy.deepcopy(look_fo["grd_features"][key])
        out["grd_features"]= combined_fo_dict
        out["grd_label"]= grd_fo_labeled
        out["match_count"] = nmatch
        out["max_label"] = kk
        out["id_list"] =id_list
    out["match_type"] = "unimatch"



    return out



def unimatch(look_ob,look_fo,cover_dis,cover_rate):
    out = copy.deepcopy(look_fo)

    grid0= look_ob["grid"]
    near_dis = cover_dis/111/grid0.dlon
    label_count_ob = look_ob["grd_features"]["label_count"]
    label_count_fo = look_fo["grd_features"]["label_count"]
    if label_count_ob >0 and label_count_fo >0:
        labels_ob = []
        for i in range(label_count_ob):
            label_ps1 = np.array([look_ob["grd_features"][i+1][1],look_ob["grd_features"][i+1][0]]).T
            labels_ob.append(label_ps1)

        labels_fo = []

        for i in range(label_count_fo):
            label_ps2 = np.array([look_fo["grd_features"][i+1][1],look_fo["grd_features"][i+1][0]]).T
            labels_fo.append(label_ps2)

        max_rate = 1

        combined_fo_dict = {}
        used_ob = np.ones(label_count_ob)
        used_fo = np.ones(label_count_fo)
        while max_rate >= cover_rate:
            max_rate = 0
            max_i = -1
            max_j_list = None
            max_pts_fo = None
            for i in range(label_count_ob):
                if used_ob[i] ==0:continue
                rate_1row = np.zeros(label_count_fo)
                for j in range(label_count_fo):
                    if used_fo[j] ==0:continue
                    rate_1row[j] = caculate_cover_rate(labels_ob[i],labels_fo[j],near_dis)
                index = np.argsort(-rate_1row)
                pts_fo = labels_fo[index[0]]
                for j in range(0,label_count_fo):
                    if rate_1row[index[j]] > 0:
                        if j > 0:
                            pts_fo =  np.append(pts_fo,labels_fo[index[j]],axis=0)
                            rate_c = caculate_cover_rate(labels_ob[i],pts_fo,near_dis)
                            if rate_c > max_rate:
                                max_rate = rate_c
                                max_i = i
                                max_j_list = index[0:j+1]
                                max_pts_fo = pts_fo
                        else:
                            rate_c = rate_1row[index[j]]
                            if rate_c> max_rate:
                                max_rate = rate_c
                                max_i = i
                                max_j_list = [index[0]]
                                max_pts_fo = pts_fo

                    else:
                        break


            if max_rate > cover_rate:
                combined_fo_dict[max_i+1] = (max_pts_fo[:,1],max_pts_fo[:,0])
                used_fo[max_j_list] = 0
                used_ob[max_i] =0


        id_list = list(combined_fo_dict.keys())
        nmatch =0
        if len(id_list)>0:
            nmatch = max(combined_fo_dict.keys())
        #print(combined_fo_dict)

        kk = label_count_ob
        for k in range(len(labels_fo)):
            if used_fo[k] > 0:
                kk += 1
                combined_fo_dict[kk] = (labels_fo[k][:, 1], labels_fo[k][:, 0])
                id_list.append(kk)

        grd_fo_labeled = look_fo["grd"].copy()
        grd_fo_labeled.attrs["var_name"] = "目标编号"
        label_value = np.zeros((grid0.nlat, grid0.nlon))
        for key in combined_fo_dict.keys():
            label = combined_fo_dict[key]
            label_value[label] = key
        grd_fo_labeled.values[:] = label_value[:]
        combined_fo_dict["label_count"] = kk
        for key in look_fo["grd_features"].keys():
            if key not in combined_fo_dict.keys():
                if isinstance(key,str):
                    combined_fo_dict[key] = copy.deepcopy(look_fo["grd_features"][key])
        out["grd_features"]= combined_fo_dict
        out["grd_label"]= grd_fo_labeled
        out["match_count"] = nmatch
        out["max_label"] = kk
        out["id_list"] =id_list
    out["match_type"] = "unimatch"


    return out


def unimerge(look_ob,look_fo):

    label_list_ob = look_ob["id_list"]
    label_list_fo = look_fo["id_list"]
    label_list_matched = list(set(label_list_ob) & set(label_list_fo))
    label_list_all = list(set(label_list_ob) | set(label_list_fo))
    vxunmatched = copy.deepcopy(label_list_ob)
    fcunmatched = copy.deepcopy(label_list_fo)
    for id in label_list_matched:
        vxunmatched.remove(id)
        fcunmatched.remove(id)

    if len(label_list_all)>0:
        max_label = np.max(np.array(label_list_all))
    else:
        max_label = 0

    out = {'grd_ob': look_ob["grd"],
           "grd_ob_smooth": look_ob["grd_smooth"],
           "grd_ob_features": look_ob["grd_features"],
           "grd_ob_label": look_ob["grd_label"],
           'grd_fo': look_fo["grd"],
           "grd_fo_smooth": look_fo["grd_smooth"],
           "grd_fo_features": look_fo["grd_features"],
           "grd_fo_label": look_fo["grd_label"],
           "grid":look_ob["grid"],
           "match_count":len(label_list_matched),
           "max_label" : max_label,
           "label_list_ob":label_list_ob,
           "label_list_fo":label_list_fo,
           "label_list_matched":label_list_matched,
           "label_list_all":label_list_all,
           "unmatched":{'ob': vxunmatched, 'fo': fcunmatched},
           "matches":np.array([label_list_matched,label_list_matched]).T,
           "match_type":look_fo["match_type"]}

    return out