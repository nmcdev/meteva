import shutil
import datetime
import nmc_verification
import os
from nmc_verification.nmc_vf_base.io import DataBlock_pb2
from nmc_verification.nmc_vf_base.io.GDS_data_service import GDSDataService


def get_dati_of_path(path):
    dir,filename = os.path.split(path)
    filename0 = os.path.splitext(filename)[0]
    a = int(filename0[0:2])
    b = int(filename0[2:4])
    if a ==20:
        if b >12:
            pass
        else:
            filename0 = "20" + filename0
    elif a == 19:
        if b >12:
            pass
        else:
            filename0 = "20" + filename0
    else:
        filename0 = "20" + filename0

    dati = nmc_verification.nmc_vf_base.time_tools.str_to_time(filename0)
    return dati
def get_dati_str_of_path(path):
    dir,filename = os.path.split(path)
    filename0 = os.path.splitext(filename)[0]
    a = int(filename0[0:2])
    b = int(filename0[2:4])
    if a ==20:
        if b >12:
            pass
        else:
            filename0 = "20" + filename0
    elif a == 19:
        if b >12:
            pass
        else:
            filename0 = "20" + filename0
    else:
        filename0 = "20" + filename0
    dati_str = filename0[0:8]

    return dati_str

def download(para):
    #遍历下载
    now = datetime.datetime.now()
    hm = now.hour * 100 + now.minute
    ip,port = nmc_verification.nmc_vf_base.io.read_gds_ip_port(para["ip_port_file"])
    service = GDSDataService(ip, port)
    if (service is None):
        print("service is None")
        return

    for down_set in para["sta_origin_dirs"]:
        if hm >= down_set[1] and hm <= down_set[2]:
            dir_list = []
            nmc_verification.nmc_vf_base.tool.path_tools.get_gds_all_dir(ip,port,down_set[0],dir_list)
            for dir in dir_list:
                file_list = nmc_verification.nmc_vf_base.tool.path_tools.get_gds_file_list_in_one_dir(ip,port,dir)
                for file in file_list:
                    save_path = para["local_binary_dir"] + "/" +dir+"/" +file
                    dati_str = get_dati_str_of_path(save_path)
                    if not os.path.exists(save_path):
                        try:
                            status, response = service.getData(dir, file)
                            ByteArrayResult = DataBlock_pb2.ByteArrayResult()
                            if status == 200:
                                ByteArrayResult.ParseFromString(response)
                                if ByteArrayResult is not None:
                                    byteArray = ByteArrayResult.byteArray
                                    nmc_verification.nmc_vf_base.tool.path_tools.creat_path(save_path)
                                    br = open(save_path, 'wb')
                                    br.write(byteArray)
                                    br.close()
                                    save_path_sta = para["local_sta_dir"] + "/" + dir +"/"+dati_str+ "/" + file
                                    nmc_verification.nmc_vf_base.tool.path_tools.creat_path(save_path_sta)
                                    br = open(save_path_sta, 'wb')
                                    br.write(byteArray)
                                    br.close()
                        except Exception as e:
                            print(e)


                    else:
                        try:
                            save_path_sta = para["local_sta_dir"] + "/" + dir + "/" + dati_str + "/" + file
                            if not os.path.exists(save_path_sta):
                                nmc_verification.nmc_vf_base.tool.path_tools.creat_path(save_path_sta)
                                shutil.copyfile(save_path,save_path_sta)
                        except Exception as e:
                            print(e)

    for key in para["grid_origin_dirs"].keys():
        down_set_group  = para["grid_origin_dirs"][key]
        for down_set in down_set_group:
            if hm >= down_set[1] and hm <= down_set[2]:
                dir_list = []
                nmc_verification.nmc_vf_base.tool.path_tools.get_gds_all_dir(ip,port,down_set[0],dir_list)
                for dir in dir_list:
                    file_list = nmc_verification.nmc_vf_base.tool.path_tools.get_gds_file_list_in_one_dir(ip,port,dir)
                    for file in file_list:
                        save_path = para["local_binary_dir"] + "/" +dir+"/" +file
                        dati_str = get_dati_str_of_path(save_path)
                        if not os.path.exists(save_path):
                            try:
                                status, response = service.getData(dir, file)
                                ByteArrayResult = DataBlock_pb2.ByteArrayResult()
                                if status == 200:
                                    ByteArrayResult.ParseFromString(response)
                                    if ByteArrayResult is not None:
                                        byteArray = ByteArrayResult.byteArray
                                        nmc_verification.nmc_vf_base.tool.path_tools.creat_path(save_path)
                                        br = open(save_path, 'wb')
                                        br.write(byteArray)
                                        br.close()
                                        if dir.upper().find("WIND")>=0:
                                            grd = nmc_verification.nmc_vf_base.io.byteArray_to_gridwind(byteArray)
                                        else:
                                            grd = nmc_verification.nmc_vf_base.io.byteArray_to_griddata(byteArray)
                                        save_path_nc = para["local_grid_dir"] + "/" + dir +"/"+dati_str+ "/" + file+".nc"
                                        nmc_verification.nmc_vf_base.write_griddata_to_nc(grd,save_path_nc,creat_dir=True)
                            except Exception as e:
                                print(e)
                        else:
                            try:
                                save_path_nc = para["local_grid_dir"] + "/" + dir + "/" + dati_str + "/" + file+".nc"
                                if not os.path.exists(save_path_nc):
                                    if dir.upper().find("WIND")>=0:
                                        grd = nmc_verification.nmc_vf_base.read_gridwind_from_gds_file(save_path)
                                    else:
                                        grd = nmc_verification.nmc_vf_base.read_griddata_from_gds_file(save_path)
                                    if grd is not None:
                                        nmc_verification.nmc_vf_base.write_griddata_to_nc(grd, save_path_nc, creat_dir=True)
                                    else:
                                        print(save_path + "文件格式错误")
                            except Exception as e:
                                print(e)

def remove(para):
    dir = para["local_binary_dir"]
    file_list = nmc_verification.nmc_vf_base.tool.path_tools.get_path_list_in_dir(dir)
    now = datetime.datetime.now()
    for file in file_list:
        dati = get_dati_of_path(file)
        dday = (now - dati).total_seconds()/(3600*24)
        if dday > para["max_save_day"]:
            os.remove(file)



