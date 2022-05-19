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
        df_list = []
        for i in range(1,nmatch+1):
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

def features_list_to_df(feature_list):
    df_list = []
    hmfc_list = []
    for features in feature_list:
        hmfc,df = features_tran(features)
        df_list.append(df)
        hmfc_list.append(hmfc)
    #print(df_list)
    df_all = pd.concat(df_list,axis=0)
    df_all = df_all.reset_index(drop=True)
    hmfc_all = pd.concat(hmfc_list,axis=0)
    hmfc_all = hmfc_all.reset_index(drop=True)
    return hmfc_all,df_all