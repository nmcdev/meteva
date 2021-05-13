import copy
import os
import numpy as np
import traceback
import pandas as pd
import datetime
import meteva
import json
import gzip

def write_stadata_to_micaps3(sta0,save_path = "a.txt",creat_dir = False, type = -1,effectiveNum = 4,show = False,title = None):
    """
    生成micaps3格式的文件
    :param sta0:站点数据信息
    :param save_path 需要保存的文件路径和名称
    :param type 类型：默认：1
    :param effectiveNum 有效数字 默认为：4
    :return:保存为micaps3格式的文件
    """
    try:
        sta = copy.deepcopy(sta0)
        dir = os.path.split(os.path.abspath(save_path))[0]
        if not os.path.isdir(dir):
            if not creat_dir:
                print("文件夹：" + dir + "不存在")
                return False
            else:
                meteva.base.tool.path_tools.creat_path(save_path)

        br = open(save_path,'w')
        end = len(save_path)
        start = max(0, end-16)
        nsta =len(sta.index)
        time = sta['time'].iloc[0]
        if isinstance(time,np.datetime64) or isinstance(time,datetime.datetime):
            time_str = meteva.base.tool.time_tools.time_to_str(time)
            time_str = time_str[0:4] + " " +time_str[4:6] + " " + time_str[6:8] + " " + time_str[8:10] + " "
        else:
            time_str = "2099 01 01 0 "

        if np.isnan(sta['level'].iloc[0]):
            level = 0
        else:
            level = int(sta['level'].iloc[0])
        if type<0 or level == np.NaN or level ==pd.NaT:
            level = int(type)

        if title is None:
            str1=("diamond 3 " + save_path[start:end] + "\n"+ time_str + str(level) +" 0 0 0 0\n1 " + str(nsta) + "\n")
        else:
            str1 = ("diamond 3 " + title + "\n" + time_str + str(level) + " 0 0 0 0\n1 " + str(
                nsta) + "\n")
        br.write(str1)
        br.close()
        data_names = meteva.base.basicdata.get_stadata_names(sta)
        if "alt" not in data_names:
            data_name = meteva.base.basicdata.get_stadata_names(sta)[0]
            df = copy.deepcopy(sta[['id','lon','lat',data_name]])
            df['alt'] = 0
            df = df.reindex(columns=['id', 'lon', 'lat', 'alt', data_name])
        else:
            colums = ['id','lon','lat','alt']
            for name in data_names:
                if name != "alt":
                    colums.append(name)
                    break
            df = sta.loc[:,colums]
            if len(colums) == 4:
                df["data0"] = 0
        effectiveNum_str = "%." + '%d'% effectiveNum + "f"
        df.to_csv(save_path,mode='a',header=None,sep = "\t",float_format=effectiveNum_str,index = None)
        if show:
            print('成功输出至' + save_path)
        return True
    except:
        exstr = traceback.format_exc()
        print(exstr)
        return False

def tran_stadata_to_gds_flow(sta):
    discriminator = b"mdfs"
    data_type =3
    data_type_byte = np.ndarray.tobytes(np.array([data_type]).astype(np.int16))

    description =""
    if "description" in sta.attrs.keys():
        description =  description + sta.attrs["description"]
    description = description.encode(encoding='utf-8')
    if len(description) < 100:
        description = description + np.ndarray.tobytes(np.zeros(100 - len(description)).astype(np.int8))


    level = np.ndarray.tobytes(np.array([sta.iloc[0,0]]).astype(np.float32))

    levelDescription = ""
    if "levelDescription" in sta.attrs.keys():
        levelDescription = sta.attrs["levelDescription"]
    levelDescription = levelDescription.encode(encoding='utf-8')
    if len(levelDescription) < 50:
        levelDescription = levelDescription + np.ndarray.tobytes(np.zeros(50 - len(levelDescription)).astype(np.int8))

    time0 = meteva.base.all_type_time_to_datetime(sta["time"].values[0])
    y = time0.year
    m = time0.month
    d = time0.day
    h = time0.hour
    min = time0.minute
    se = time0.second

    y_m_d_h_M_s_timezone = np.ndarray.tobytes(np.array([y,m,d,h,min,se,8]).astype(np.int32))
    blank = np.ndarray.tobytes(np.zeros(100).astype(np.int8))

    nsta = len(sta.index)
    station_number = np.ndarray.tobytes(np.array([nsta]).astype(np.int32))
    data_names = meteva.base.get_stadata_names(sta)
    nele = len(data_names)
    value_bytes = np.ndarray.tobytes(np.array([nele]).astype(np.int16))

    for j in range(nele):
        value_bytes += np.ndarray.tobytes(np.array([601,5]).astype(np.int16))

    for i in range(nsta):
        value_bytes += np.ndarray.tobytes(np.array([sta.iloc[i,3],sta.iloc[i,4],sta.iloc[i,5]]).astype(np.float32))
        value_bytes += np.ndarray.tobytes(np.array(nele).astype(np.int16))
        for j in range(nele):
            value_bytes += np.ndarray.tobytes(np.array([601]).astype(np.int16))
            value_bytes += np.ndarray.tobytes(np.array([sta.iloc[i,6+j]]).astype(np.float32))


    bytes1 = discriminator+data_type_byte+description+level+levelDescription+y_m_d_h_M_s_timezone
    bytes2 = blank+station_number+value_bytes
    bytes = bytes1+bytes2

    return bytes

def write_stadata_to_gds_file(da,save_path = "a.txt",creat_dir = False,show = False):
    try:
        dir = os.path.split(os.path.abspath(save_path))[0]
        if not os.path.isdir(dir):
            if not creat_dir:
                print("文件夹："+dir+"不存在")
                return False
            else:
                meteva.base.tool.path_tools.creat_path(save_path)

        bytes = tran_stadata_to_gds_flow(da)
        br = open(save_path, 'wb')
        br.write(bytes)
        br.close()
        if show:
            print('成功输出至' + save_path)
        return True
    except:
        exstr = traceback.format_exc()
        print(exstr)
        return False

def pretty_floats(obj,effective_num):
    if isinstance(obj, float):
        return round(obj, effective_num)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v,effective_num)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return map(pretty_floats, obj)
    return obj

def stadata_to_json(sta,effective_num):
    data_names = meteva.base.get_stadata_names(sta)
    sta1 = sta.round(effective_num)
    #print(effective_num)
    #print(sta1)
    meteva.base.set_stadata_names(sta1,["data0"])
    dict_attrs = copy.deepcopy(sta.attrs)
    dict_attrs["time"] = meteva.base.all_type_time_to_str(sta1['time'].values[0])
    dict_attrs["dtime"] = str(sta1['dtime'].values[0])
    dict_attrs["level"] = str(sta1['level'].values[0])
    dict_attrs["model"] = data_names[0]
    sta1 = sta1.drop(["level","time","dtime"],axis = 1)
    if  "data_start_columns" not in dict_attrs.keys():
        dict_attrs["data_start_columns"] = 6
    dict1 = {}
    dict1["attrs"] =dict_attrs
    #print(dict_attrs)
    dict1["data"] = sta1.to_dict(orient='index')
    json_str = json.dumps(pretty_floats(dict1,effective_num))
    return json_str


def stadata_to_json_bytes(sta,effective_num):
    json_str = stadata_to_json(sta,effective_num)
    json_bytes = gzip.compress(json_str.encode("GBK"))
    return json_bytes

def write_stadata_to_json_file(sta,filename,effective_num = 3):
    br = open(filename, 'w')
    json_str = stadata_to_json(sta,effective_num)
    br.write(json_str)
    br.close()

def write_stadata_to_json_byte_file(sta,filename,effective_num = 3):
    br = open(filename, 'wb')
    json_bytes = stadata_to_json_bytes(sta,effective_num)
    br.write(json_bytes)
    br.close()

def put_stadata_to_micaps(sta,effective_num = 3,layer_description = None):

    import MPython
    pyclient = MPython.MICAPSPython()
    if (pyclient.GetConnectStatus()):
        print("MICAPS4客户端已连接")
    else:
        pyclient.ReConnect()

    data_names = meteva.base.get_stadata_names(sta)
    nrow = len(data_names)

    if nrow ==1:
        if layer_description is not None:
            if isinstance(layer_description,list):
                sta.attrs["data_source"] = layer_description[0]
                #sta.attrs["layer_description"] = layer_description[0]
            else:
                #sta.attrs["layer_description"] = layer_description
                sta.attrs["data_source"] = layer_description
        else:
            #sta.attrs["layer_description"] = ""
            pass
        if "model" not in sta.attrs.keys():
            sta.attrs["model"] = data_names[0]
        json_bytes = stadata_to_json_bytes(sta, effective_num)
        pyclient.CreateDiscreteLayer(json_bytes)
    else:
        for i in range(nrow):
            sta1 = meteva.base.in_member_list(sta,[data_names[i]])
            if layer_description is not None:
                sta1.attrs["data_source"] = layer_description[i]
                #sta1.attrs["layer_description"] = layer_description[i]
            else:
                #sta1.attrs["layer_description"] = ""
                pass
            if "model" not in sta1.attrs.keys():
                sta1.attrs["model"] = data_names[i]

            json_bytes = stadata_to_json_bytes(sta1,effective_num)
            pyclient.CreateDiscreteLayer(json_bytes)

'''def sta_to_json(sta,effective_num):
    sta1 = sta.round(effective_num)
    sta1.attrs = copy.deepcopy(sta.attrs)
    sta1["time"]=sta1['time'].apply(lambda x: x.strftime('%Y%m%d%H%M'))
    dict1 = {}
    dict1["attrs"] = sta1.attrs
    dict1["data"] = sta1.to_dict(orient='index')
    str_data = json.dumps(dict1)
    return str_data'''



if __name__ == "__main__":
    meteva.base.print_gds_file_values_names(r"H:\test_data\20210220160000.000")
    sta = meteva.base.read_stadata_from_gdsfile(r"H:\test_data\20210220160000.000",element_id=603)
    sta.attrs["description"] = "Temp"
    print(sta)
    write_stadata_to_gds_file(sta,save_path=r"H:\test_data\output\meb\m3_gds_test.000")