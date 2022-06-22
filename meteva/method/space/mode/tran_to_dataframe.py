import pandas as pd
import meteva

def features_tran(features):
    try:
        time1 = meteva.base.all_type_time_to_time64(features["time"])
        tabel = features["feature_table"]["contingency_table_yesorno"]
        hmfc = pd.DataFrame({
            "level":[0],"time":[time1],"dtime":[features["dtime"]],"id":[meteva.base.IV],
            "lon":[meteva.base.IV],"lat":[meteva.base.IV],
            "Hits":[tabel["Hits"]],"Misses":[tabel["Misses"]],
            "False alarms":[tabel["False alarms"]],"Correct negatives":[tabel["Correct negatives"]]
        })
        nmatch = features["match_count"]
        label_list_matched = features["label_list_matched"]
        df_list = []
        for i in label_list_matched:
            fi = features[i]
            dict1 = {
                "level": [0], "time": [time1], "dtime": [features["dtime"]], "id": [i],
                "lon":[fi["feature_props"]["ob"]["centroid"]["x"]],"lat":[fi["feature_props"]["ob"]["centroid"]["y"]],
                "ob_lenghts_MajorAxis":[fi["feature_axis"]["ob"]["lengths"]["MajorAxis"]],
                "ob_lenghts_MinorAxis": [fi["feature_axis"]["ob"]["lengths"]["MinorAxis"]],
                "ob_window_x0":[fi["feature_axis"]["ob"]["window"]["x0"]],
                "ob_window_y0": [fi["feature_axis"]["ob"]["window"]["y0"]],
                "ob_window_x1": [fi["feature_axis"]["ob"]["window"]["x1"]],
                "ob_window_y1": [fi["feature_axis"]["ob"]["window"]["y1"]],
                "ob_centroid_x": [fi["feature_props"]["ob"]["centroid"]["x"]],
                "ob_centroid_y": [fi["feature_props"]["ob"]["centroid"]["y"]],
                "ob_area": [fi["feature_props"]["ob"]["area"]],
                "ob_intensity": [fi["feature_props"]["ob"]["intensity"]],


                "fo_lenghts_MajorAxis": [fi["feature_axis"]["fo"]["lengths"]["MajorAxis"]],
                "fo_lenghts_MinorAxis": [fi["feature_axis"]["fo"]["lengths"]["MinorAxis"]],
                "fo_window_x0": [fi["feature_axis"]["fo"]["window"]["x0"]],
                "fo_window_y0": [fi["feature_axis"]["fo"]["window"]["y0"]],
                "fo_window_x1": [fi["feature_axis"]["fo"]["window"]["x1"]],
                "fo_window_y1": [fi["feature_axis"]["fo"]["window"]["y1"]],
                "fo_centroid_x": [fi["feature_props"]["fo"]["centroid"]["x"]],
                "fo_centroid_y": [fi["feature_props"]["fo"]["centroid"]["y"]],
                "fo_area": [fi["feature_props"]["fo"]["area"]],
                "fo_intensity": [fi["feature_props"]["fo"]["intensity"]]
            }

            if "intensity_50" in fi["feature_props"]["ob"].keys():
                q = [0,5,10,25,50, 75, 90, 95, 100]
                for k in range(len(q)):
                    dict1["ob_intensity_" + str(q[k])] = [fi["feature_props"]["ob"]["intensity_" + str(q[k])]]
                    dict1["fo_intensity_" + str(q[k])] = [fi["feature_props"]["fo"]["intensity_" + str(q[k])]]

            keys = ["cent_dist", "angle_diff", "area_ratio", "int_area", "bearing",
                    "bdelta", "haus", "medMiss", "medFalseAlarm", "msdMiss", "msdFalseAlarm", "ph", "fom", "minsep"]
            for key in keys:
                dict1[key] = fi["feature_comps"][key]
            df = pd.DataFrame(dict1)
            df_list.append(df)
        if len(df_list)>0:
            df = pd.concat(df_list,axis=0)
        else:
            df = None
        return  hmfc,df
    except:
        print("将以下检验概要信息转换成DataFrame失败")
        print(features)



def features_tran_miss(features):
    # try:
        time1 = meteva.base.all_type_time_to_time64(features["time"])
        miss_labels = features["unmatched"]['ob']
        df_list = []
        for i in miss_labels:
            fi = features[i]
            dict1 = {
                "level": [0], "time": [time1], "dtime": [features["dtime"]], "id": [i],
                "lon":[fi["feature_props"]["ob"]["centroid"]["x"]],"lat":[fi["feature_props"]["ob"]["centroid"]["y"]],
                "ob_lenghts_MajorAxis":[fi["feature_axis"]["ob"]["lengths"]["MajorAxis"]],
                "ob_lenghts_MinorAxis": [fi["feature_axis"]["ob"]["lengths"]["MinorAxis"]],
                "ob_window_x0":[fi["feature_axis"]["ob"]["window"]["x0"]],
                "ob_window_y0": [fi["feature_axis"]["ob"]["window"]["y0"]],
                "ob_window_x1": [fi["feature_axis"]["ob"]["window"]["x1"]],
                "ob_window_y1": [fi["feature_axis"]["ob"]["window"]["y1"]],
                "ob_centroid_x": [fi["feature_props"]["ob"]["centroid"]["x"]],
                "ob_centroid_y": [fi["feature_props"]["ob"]["centroid"]["y"]],
                "ob_area": [fi["feature_props"]["ob"]["area"]],
                "ob_intensity": [fi["feature_props"]["ob"]["intensity"]],
            }
            if "intensity_50" in fi["feature_props"]["ob"].keys():
                q = [0,5,10,25,50, 75, 90, 95, 100]
                for k in range(len(q)):
                    dict1["ob_intensity_" + str(q[k])] = [fi["feature_props"]["ob"]["intensity_" + str(q[k])]]
            df = pd.DataFrame(dict1)
            df_list.append(df)
        if len(df_list)>0:
            df = pd.concat(df_list,axis=0)
        else:
            df = None
        return  df
    # except:
    #     print("将以下检验概要信息转换成DataFrame失败")
    #     print(features)



def features_tran_false_alarm(features):
    try:
        time1 = meteva.base.all_type_time_to_time64(features["time"])
        false_alarm_labels = features["unmatched"]['fo']
        df_list = []
        for i in false_alarm_labels:
            fi = features[i]
            dict1 = {
                "level": [0], "time": [time1], "dtime": [features["dtime"]], "id": [i],
                "lon":[fi["feature_props"]["fo"]["centroid"]["x"]],"lat":[fi["feature_props"]["fo"]["centroid"]["y"]],
                "fo_lenghts_MajorAxis": [fi["feature_axis"]["fo"]["lengths"]["MajorAxis"]],
                "fo_lenghts_MinorAxis": [fi["feature_axis"]["fo"]["lengths"]["MinorAxis"]],
                "fo_window_x0": [fi["feature_axis"]["fo"]["window"]["x0"]],
                "fo_window_y0": [fi["feature_axis"]["fo"]["window"]["y0"]],
                "fo_window_x1": [fi["feature_axis"]["fo"]["window"]["x1"]],
                "fo_window_y1": [fi["feature_axis"]["fo"]["window"]["y1"]],
                "fo_centroid_x": [fi["feature_props"]["fo"]["centroid"]["x"]],
                "fo_centroid_y": [fi["feature_props"]["fo"]["centroid"]["y"]],
                "fo_area": [fi["feature_props"]["fo"]["area"]],
                "fo_intensity": [fi["feature_props"]["fo"]["intensity"]]
            }
            if "intensity_50" in fi["feature_props"]["fo"].keys():
                q = [0,5,10,25,50, 75, 90, 95, 100]
                for k in range(len(q)):
                    dict1["fo_intensity_" + str(q[k])] = [fi["feature_props"]["fo"]["intensity_" + str(q[k])]]
            df = pd.DataFrame(dict1)
            df_list.append(df)
        if len(df_list)>0:
            df = pd.concat(df_list,axis=0)
        else:
            df = None
        return  df
    except:
        print("将以下检验概要信息转换成DataFrame失败")
        print(features)


def features_list_to_df(feature_list):
    hit_list = []
    hmfc_list = []
    for i in range(len(feature_list)):
        features = feature_list[i]
        hmfc,hit = features_tran(features)
        hit_list.append(hit)
        hmfc_list.append(hmfc)
    #print(df_list)
    df_hit = pd.concat(hit_list,axis=0)
    df_hit = df_hit.reset_index(drop=True)
    hmfc_all = pd.concat(hmfc_list,axis=0)
    hmfc_all = hmfc_all.reset_index(drop=True)
    return hmfc_all,df_hit



def features_list_to_df_c(feature_list):
    hit_list = []
    hmfc_list = []
    mis_list = []
    fal_list = []
    for i in range(len(feature_list)):
        features = feature_list[i]
        hmfc,hit = features_tran(features)
        mis = features_tran_miss(features)
        fal = features_tran_false_alarm(features)
        hit_list.append(hit)
        hmfc_list.append(hmfc)
        mis_list.append(mis)
        fal_list.append(fal)

    hmfc_all = pd.concat(hmfc_list,axis=0)
    hmfc_all = hmfc_all.reset_index(drop=True)
    df_hit = pd.concat(hit_list,axis=0)
    df_hit = df_hit.reset_index(drop=True)
    df_mis = pd.concat(mis_list,axis=0)
    df_mis = df_mis.reset_index(drop=True)
    df_fal = pd.concat(fal_list,axis=0)
    df_fal = df_fal.reset_index(drop=True)

    return hmfc_all,df_hit,df_fal,df_mis