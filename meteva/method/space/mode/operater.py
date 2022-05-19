from .feature_finder import feature_finder
from .centmatch import centmatch
from .merge_force import merge_force
from .feature_match_analyzer import feature_merged_analyzer
import meteva
import json
import copy
from .plot import plot_value_and_label,plot_feature


def operate(grd_ob, grd_fo, smooth, threshold,minsize,compare = ">=",match_method = centmatch,summary =True,
            save_dir = None,cmap = "rain_24h",clevs = None,show = False):
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
        plot_value_and_label(look_merge,save_path=png_save_path,show=show,cmap = cmap,clevs = clevs)


        json_save_path = save_dir +"/json/YYYYMMDDHH.TTT.txt"
        json_save_path =  meteva.base.get_path(json_save_path,time1,dtime1)
        meteva.base.creat_path(json_save_path)
        nmatch = features["match_count"]
        #json_str = json.dumps(features)
        #print(json_str)
        features_list = copy.deepcopy(features)
        if  features["interester"] is not None:
            features_list["interester"] = features["interester"].tolist()
        for i in range(1,nmatch+1):
            features_list[i]["feature_props"]["ob"]["intensity"] =features[i]["feature_props"]["ob"]["intensity"][0].tolist()
            features_list[i]["feature_props"]["fo"]["intensity"] = features[i]["feature_props"]["fo"]["intensity"][0].tolist()
        for i in range(1,nmatch+1):
            q = [0,5,10,25,50, 75, 90, 95, 100]
            for k in range(len(q)):
                features_list[i]["feature_props"]["ob"]["intensity_"+str(q[k])] =features[i]["feature_props"]["ob"]["intensity"][k].tolist()
                features_list[i]["feature_props"]["fo"]["intensity_"+str(q[k])] = features[i]["feature_props"]["fo"]["intensity"][k].tolist()

        json_str = json.dumps(features_list)
        br = open(json_save_path, 'w')
        br.write(json_str)
        br.close()
        print("目标属性检验结果已经输出至 "+json_save_path)

        png_save_path = save_dir + "/table/YYYYMMDDHH.TTT.png"
        png_save_path = meteva.base.get_path(png_save_path, time1, dtime1)
        meteva.base.creat_path(png_save_path)
        plot_feature(features, save_path=png_save_path, show=show)

    return features


