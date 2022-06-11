import json
import meteva

def load_feature_summary(filename):
    file = open(filename, "r")
    strs = file.read()
    feature = json.loads(strs)
    file.close()
    nmatch = feature["match_count"]
    feature1 = {}
    feature1["match_count"] = feature["match_count"]
    feature1["time"] = feature["time"]
    feature1["dtime"] = feature["dtime"]
    feature1["feature_table"] = feature["feature_table"]
    feature1["interester"] = feature["interester"]

    # for i in range(1,nmatch+1):
    #     feature1[i] = feature[str(i)]
    label_list_matched = feature["label_list_matched"]
    feature1["label_list_matched"] = label_list_matched
    for id in label_list_matched:
        feature1[id] = feature[str(id)]
    return feature1

def load_feature_summary_list(dir):
    file_list = meteva.base.tool.path_tools.get_path_list_in_dir(dir)
    features_list = []
    for file in file_list:
        feature = load_feature_summary(file)
        features_list.append(feature)
    return features_list