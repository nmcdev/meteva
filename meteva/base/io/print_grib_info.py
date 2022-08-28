import xarray as xr
import os
from multiprocessing import Process
import sys
import copy


class Logger(object):
    def __init__(self, filename='default.log', stream=sys.stdout):
        self.terminal = stream
        self.log = open(filename, 'w')

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        pass



def open_dataset(filename,filter_by_keys={}):
    sys.stdout = Logger('grib_read_out.txt', sys.stdout)
    sys.stderr = Logger('grib_read_err.txt', sys.stderr)
    backend_kwargs = {"filter_by_keys":filter_by_keys, "indexpath": ""}
    ds1 = xr.open_dataset(filename, engine="cfgrib", backend_kwargs=backend_kwargs)
    print(ds1)
    ds1.close()




def pro(filename,filter_by_keys):
    tmpp = Process(target=open_dataset, kwargs={"filename":filename,"filter_by_keys":filter_by_keys})
    tmpp.start()
    tmpp.join()

def print_grib_file_info(filename,filter_by_keys = {},info = None,print_info = True):
    pro(filename,filter_by_keys)
    if info is None:
        info = []

    has_error=False
    if os.path.exists("grib_read_err.txt"):
        grib_read_err = open("grib_read_err.txt", "r")
        err_infos = grib_read_err.read()
        strs = err_infos.split("\n")
        if len(strs)>1:
            has_error=True
    if os.path.exists("grib_read_out.txt"):
        grib_read_out = open("grib_read_out.txt", "r")
        out_infos = grib_read_out.read()

        if len(out_infos)>0:
            print("*************************************************************************")
            print("使用参数 filter_by_keys = "+str(filter_by_keys)+"查看到的数据内容为：")
            print(out_infos)

        if "typeOfLevel" not in filter_by_keys:
            valid_levelType = ["isobaricInhPa", "surface", "meanSea", "heightAboveGround", "heightAboveGroundLayer",
                               "cloudBase", "cloudTop", "pressureFromGroundLayer"]
            out_info = out_infos.split("\n")
            if len(out_info)>2:
                i_c = 0
                i_d = 0
                for i  in range(len(out_info)):
                    if out_info[i].strip() == "Coordinates:":
                        i_c = i
                    if out_info[i].strip() == "Data variables:":
                        i_d = i

                index1 = out_infos.find("Data variables:")
                index2 = out_infos.find("Attributes:")
                variables = out_infos[index1:index2]

                had_valid = False
                for i in range(i_c+1,i_d):
                    str1 = out_info[i].replace("*","")
                    str_list = str1.split()
                    str2 = str_list[0].strip()
                    #if str2 in valid_levelType:
                    if variables.find(str2)>=0 and str2 in valid_levelType:
                        had_valid = True
                        print("*************************************************************************")
                        print("请在读取该grib文件时添加参数 \nfilter_by_keys= {'typeOfLevel':'"+str2+"'}")

                if not had_valid:
                    print("请根据以上数据内容信息，确认所需读取的物理量对应的levelType")
        if not has_error:
            return

    if has_error:
        grib_read_err = open("grib_read_err.txt", "r")
        err_infos = grib_read_err.read()
        if err_infos.find("filter_by_keys")>=0:
            strs = err_infos.split("\n")
            for str1 in strs:
                if str1.find("filter_by_keys=") >= 0:
                    filter_by_keys1 = {}
                    str1s = str1.split("=")
                    str1s = str1s[1].replace("{","").replace("}","").replace("'","").replace(" ","").split(",")
                    for str2 in str1s:
                        key,value = str2.split(":")
                        filter_by_keys1[key] = value
                        info.append(filter_by_keys1)
                        try:
                            print_grib_file_info(filename,filter_by_keys=filter_by_keys1,info = info,print_info = False)
                        except:
                            pass
        elif err_infos.find("skipping variable: paramId=") >= 0:
            strs = err_infos.split("\n")
            for str1 in strs:
                if str1.find("skipping variable: paramId=") >= 0:
                    filter_by_keys1 = copy.deepcopy(filter_by_keys)
                    str1s = str1.split()
                    str1s_kv = str1s[2].split("==")
                    filter_by_keys1[str1s_kv[0]] = int(str1s_kv[1])
                    #str1s_kv = str1s[3].split("=")
                    #filter_by_keys1[str1s_kv[0]] = str1s_kv[1]
                    info.append(filter_by_keys1)
                    try:
                        print_grib_file_info(filename, filter_by_keys=filter_by_keys1, info=info, print_info=False)
                    except:
                        pass

    if print_info:
        info_short = []
        print("在读取数据时需添加如下参数当中的一个")
        for info1 in info:
            if "shortName" in info1.keys():
                info_short.append(info1)
            else:
                print("filter_by_keys = "+str(info1))
        for info1 in info_short:
            shortName = info1["shortName"]
            del info1["shortName"]
            print("若需查看变量"+shortName+"请添加参数:")
            print("filter_by_keys = "+str(info1))
    else:
        return info

if __name__=="__main__":

    #path = r"\\10.28.16.239\ensemble_datasets\ReanalysisData\CRA\2014\20140101\CRA40LAND_SURFACE_2014010112_GLB_0P25_HOUR_V1_0_0.grib"
    #print_grib_file_info(path)


    #print_grib_file_info(r"H:\test_data\input\meb\era5-levels-members.grib")
    print_grib_file_info(r"D:\book\test_data\charpter5\test.grib")
