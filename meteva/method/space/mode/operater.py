from .feature_finder import feature_finder,feature_finder_and_merge
from .centmatch import centmatch
from .merge_force import merge_force
from .consistent import unimerge,unimatch
from .feature_match_analyzer import feature_merged_analyzer
import meteva
import json
import copy
from .plot import plot_value_and_label,plot_feature


def operate(grd_ob, grd_fo, smooth, threshold,minsize,compare = ">=",match_method = centmatch,near_dis =100,
            near_rate =0.3,cover_dis = 100,cover_rate =0.5,summary =True,
            save_dir = None,cmap = "rain_24h",clevs = None,show = False,dpi = 300):
    if match_method.__name__ == unimatch.__name__:
        if not isinstance(smooth,list):
            smooth = [smooth,smooth]
        if not isinstance(threshold,list):
            threshold = [threshold,threshold]
        if not isinstance(minsize,list):
            minsize = [minsize,minsize]
        if not isinstance(near_dis,list):
            near_dis = [near_dis,near_dis]
        if not isinstance(near_rate,list):
            near_rate = [near_rate,near_rate]

        look_ob = feature_finder_and_merge(grd_ob,smooth[0],threshold[0],minsize[0],compare = compare,near_dis=near_dis[0],
                                           near_rate = near_rate[0])
        look_fo = feature_finder_and_merge(grd_fo, smooth[1], threshold[1], minsize[1], compare=compare,
                                           near_dis=near_dis[1],
                                           near_rate=near_rate[1])
        matched_fo = unimatch(look_ob,look_fo,cover_dis,cover_rate)
        look_merge = unimerge(look_ob,matched_fo)
    else:
        look_ff = feature_finder(grd_ob,grd_fo,smooth=smooth,threshold=threshold,minsize=minsize,compare=compare)
        loof_match = match_method(look_ff)
        look_merge = merge_force(loof_match)
    features = feature_merged_analyzer(look_merge,summary=summary)
    time1 = meteva.base.all_type_time_to_datetime(grd_fo["time"].values[0])
    dtime1 = grd_fo["dtime"].values[0]


    if save_dir is not None:
        label_save_path = save_dir + "/label/YYYYMMDDHH.TTT.nc"
        label_save_path = meteva.base.get_path(label_save_path,time1,dtime1)
        meteva.base.creat_path(label_save_path)
        grid1 = meteva.base.get_grid_of_data(grd_fo)
        grid1.members = ["ob",grid1.members[0]]
        labels = meteva.base.grid_data(grid1)
        labels.values[0,...] = look_merge["grd_ob_label"].values[...]
        labels.values[1, ...] = look_merge["grd_fo_label"].values[...]
        meteva.base.write_griddata_to_nc(labels,save_path=label_save_path)
        print("目标编号场已经输出至 "+label_save_path)


        png_save_path = save_dir +"/png/YYYYMMDDHH.TTT.png"
        png_save_path =  meteva.base.get_path(png_save_path,time1,dtime1)
        meteva.base.creat_path(png_save_path)
        plot_value_and_label(look_merge,save_path=png_save_path,show=show,cmap = cmap,clevs = clevs,dpi=dpi)


        json_save_path = save_dir +"/json/YYYYMMDDHH.TTT.txt"
        json_save_path =  meteva.base.get_path(json_save_path,time1,dtime1)
        meteva.base.creat_path(json_save_path)
        nmatch = features["match_count"]
        #json_str = json.dumps(features)
        #print(json_str)

        features_list = copy.deepcopy(features)
        if  features["interester"] is not None:
            features_list["interester"] = features["interester"].tolist()
        label_list_matched = look_merge["label_list_matched"]
        for i in label_list_matched:
            features_list[i]["feature_props"]["ob"]["intensity"] =features[i]["feature_props"]["ob"]["intensity"][4].tolist()
            features_list[i]["feature_props"]["fo"]["intensity"] = features[i]["feature_props"]["fo"]["intensity"][4].tolist()
        for i in label_list_matched:
            q = [0,5,10,25,50, 75, 90, 95, 100]
            for k in range(len(q)):
                features_list[i]["feature_props"]["ob"]["intensity_"+str(q[k])] =features[i]["feature_props"]["ob"]["intensity"][k].tolist()
                features_list[i]["feature_props"]["fo"]["intensity_"+str(q[k])] = features[i]["feature_props"]["fo"]["intensity"][k].tolist()

        miss_labels = look_merge["unmatched"]['ob']
        for i in miss_labels:
            features_list[i]["feature_props"]["ob"]["intensity"] =features[i]["feature_props"]["ob"]["intensity"][4].tolist()

        for i in miss_labels:
            q = [0,5,10,25,50, 75, 90, 95, 100]
            for k in range(len(q)):
                features_list[i]["feature_props"]["ob"]["intensity_"+str(q[k])] =features[i]["feature_props"]["ob"]["intensity"][k].tolist()

        false_alarm_labels = look_merge["unmatched"]['fo']
        for i in false_alarm_labels:
            features_list[i]["feature_props"]["fo"]["intensity"] =features[i]["feature_props"]["fo"]["intensity"][4].tolist()

        for i in false_alarm_labels:
            q = [0,5,10,25,50, 75, 90, 95, 100]
            for k in range(len(q)):
                features_list[i]["feature_props"]["fo"]["intensity_"+str(q[k])] =features[i]["feature_props"]["fo"]["intensity"][k].tolist()

        json_str = json.dumps(features_list)

        br = open(json_save_path, 'w')
        br.write(json_str)
        br.close()
        print("目标属性检验结果已经输出至 "+json_save_path)

        png_save_path = save_dir + "/table/YYYYMMDDHH.TTT.png"
        png_save_path = meteva.base.get_path(png_save_path, time1, dtime1)
        meteva.base.creat_path(png_save_path)
        plot_feature(features, save_path=png_save_path, show=show,dpi=dpi)

    return features


