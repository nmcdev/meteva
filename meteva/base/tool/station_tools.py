import pkg_resources
import re
import meteva
import pandas as pd

def fuzzyfinder(input_str, collection):
    suggestions = []
    pattern = '.*?'.join(input_str)    # Converts 'djm' to 'd.*?j.*?m'
    regex = re.compile(pattern)         # Compiles a regex.
    for item in collection:
        match = regex.search(item)      # Checks if the current item matches the regex.
        if match:
            suggestions.append((len(match.group()), match.start(), item))
    return [x for _, _, x in sorted(suggestions)]

def muti_strs_finder(input_str, collection):
    strs = input_str.split()
    input_collection = collection
    output_str_list = []
    for i in range(len(strs)):
        output_str_list = fuzzyfinder(strs[i], input_collection)
        if len(output_str_list) ==0:
            if i==0:
                return output_str_list
        else:
            input_collection = output_str_list
    return input_collection

def get_station_id_name_dict(id_name_list_file):
    file1 = None
    try:
        file1 = open(id_name_list_file, encoding="GBK")
        str0 = file1.read()
    except:
        try:
            file1 = open(id_name_list_file,encoding="UTF-8")
            str0 = file1.read()
        except:
            pass
    if file1 is not None:
        file1.close()
        str1 = str0.split("\n")
        station_id_name_dict = {}
        for i in range(len(str1)):
            strs_line = str1[i].split(" ")
            if len(strs_line) ==3:
                values = strs_line[0]
                strs_int = ""
                for i in range(len(values)):
                    strs = values[i]
                    for s in strs:
                        if s.isdigit():
                            strs_int += s
                        else:
                            strs_int += str(ord(s))
                if(len(strs_int) >0):
                    key =  int(strs_int)
                    if not key in station_id_name_dict.keys():
                        value1 = strs_line[1]+"_"+strs_line[2]
                        station_id_name_dict[key] = value1
    else:
        print("warming ：站点名称文件"+id_name_list_file+"读取失败,在后续的产品中不能显示站点中文名称")
        station_id_name_dict = {}
    return station_id_name_dict

station_id_name_dict = get_station_id_name_dict(pkg_resources.resource_filename('meteva', "resources/stations/station_id_pro_county.txt"))
station_name_id_dict = dict(zip(station_id_name_dict.values(),station_id_name_dict.keys()))


def add_station_id_name_dict(id_name_dict):
    for id in id_name_dict.keys():
        name = id_name_dict[id]
        meteva.base.station_id_name_dict[id] = name
        meteva.base.station_name_id_dict[name] = id

def find_station_id_by_city_name(input_strs):
    ele_names = muti_strs_finder(input_strs,station_name_id_dict)
    names_ids = {}
    for names in ele_names:
        names_ids[names] = station_name_id_dict[names]
        #print(names + " : " + str(names_ids[names]))
    return names_ids


def get_station_format_province_set(id_list):
    pro_names = []
    no_province_ids = []
    for id in id_list:
        if id in station_id_name_dict.keys():
            str1 = station_id_name_dict[id]
            str1s = str1.split("_")
            pro_names.append(str1s[0])
        else:
            pro_names.append("未区分")
            no_province_ids.append(id)

    df = pd.DataFrame({
        "id":id_list,
        "province_name":pro_names
    })

    sta = meteva.base.sta_data(df)

    return sta