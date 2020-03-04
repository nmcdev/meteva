import shutil
import datetime
import meteva
import os
from meteva.base.io import DataBlock_pb2
from meteva.base.io.GDS_data_service import GDSDataService
from multiprocessing import Process,cpu_count


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

    dati = meteva.base.time_tools.str_to_time(filename0)
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

def download_one_cup(k,ip,port,local_binary_dir,local_sta_dir,local_grid_dir,file_sta_list,file_grid_list):
    service = GDSDataService(ip, port)
    for filepath in file_sta_list:
        dir,file = os.path.split(filepath)
        save_path = local_binary_dir + "/" + dir + "/" + file
        dati_str = get_dati_str_of_path(save_path)
        try:
            status, response = service.getData(dir, file)
            ByteArrayResult = DataBlock_pb2.ByteArrayResult()
            if status == 200:
                ByteArrayResult.ParseFromString(response)
                if ByteArrayResult is not None:
                    byteArray = ByteArrayResult.byteArray
                    save_path_sta = local_sta_dir + "/" + dir + "/" + dati_str + "/" + file
                    meteva.base.tool.path_tools.creat_path(save_path_sta)
                    br = open(save_path_sta, 'wb')
                    br.write(byteArray)
                    br.close()
                    print(save_path_sta)
                    print(k)
        except Exception as e:
            print(e)

    for filepath in file_grid_list:
        dir,file = os.path.split(filepath)
        save_path = local_binary_dir + "/" + dir + "/" + file
        dati_str = get_dati_str_of_path(save_path)
        try:
            status, response = service.getData(dir, file)
            ByteArrayResult = DataBlock_pb2.ByteArrayResult()
            if status == 200:
                ByteArrayResult.ParseFromString(response)
                if ByteArrayResult is not None:
                    byteArray = ByteArrayResult.byteArray
                    meteva.base.tool.path_tools.creat_path(save_path)
                    br = open(save_path, 'wb')
                    br.write(byteArray)
                    br.close()
                    if dir.upper().find("WIND") >= 0:
                        if (dir.upper().find("GUST")) >= 0:
                            grd = meteva.base.io.byteArray_to_griddata(byteArray)
                        else:
                            grd = meteva.base.io.byteArray_to_gridwind(byteArray)
                    else:
                        grd = meteva.base.io.byteArray_to_griddata(byteArray)
                    save_path_nc = local_grid_dir + "/" + dir + "/" + dati_str + "/" + file + ".nc"
                    meteva.base.write_griddata_to_nc(grd, save_path_nc, creat_dir=True)
                    print(k)
        except Exception as e:
            print(e)


def download_mp(ip,port,local_binary_dir,local_sta_dir,local_grid_dir,download_sta_list,download_grid_list,multi_pro_num):
    max_pro_num = cpu_count() - 2
    if multi_pro_num > max_pro_num:
        multi_pro_num = max_pro_num

    file_sta_dict_list = {}
    file_grid_dict_list = {}
    for i in range(multi_pro_num):
        file_sta_dict_list[i] = []
        file_grid_dict_list[i] = []

    for i in range(len(download_sta_list)):
        k = i % multi_pro_num
        file_sta_dict_list[k].append(download_sta_list[i])
    for i in range(len(download_grid_list)):
        k = i % multi_pro_num
        file_grid_dict_list[k].append(download_grid_list[i])

    PP = []
    for k in range(multi_pro_num):
        tmpp = Process(target=download_one_cup, args=(k,ip,port,local_binary_dir,local_sta_dir,local_grid_dir,file_sta_dict_list[k],file_grid_dict_list[k]))
        PP.append(tmpp)
    print('Waiting for all subprocesses done...')
    for pc in PP:
        pc.start()

    for pp in PP:
        pp.join()
    print('All subprocesses done.')


def download(para):
    #遍历下载
    now = datetime.datetime.now()
    weekago = now - datetime.timedelta(days=7)
    hm = now.hour * 100 + now.minute
    ip,port = meteva.base.io.read_gds_ip_port(para["ip_port_file"])
    service = GDSDataService(ip, port)
    if (service is None):
        print("service is None")
        return
    download_sta_list = []
    for down_set in para["sta_origin_dirs"]:
        if hm >= down_set[1] and hm <= down_set[2]:
            dir_list = []
            meteva.base.tool.path_tools.get_gds_all_dir(ip,port,down_set[0],dir_list)
            for dir in dir_list:
                file_list = meteva.base.tool.path_tools.get_gds_file_list_in_one_dir(ip,port,dir)
                file_list.sort(reverse = True)
                for file in file_list:
                    dati = get_dati_of_path(file)
                    if dati < weekago:break
                    dati_str = get_dati_str_of_path(file)
                    save_path_sta = para["local_sta_dir"] + "/" + dir + "/" + dati_str + "/" + file
                    if not os.path.exists(save_path_sta):
                        download_sta_list.append(dir + "/" +file)

    download_grid_list = []
    for key in para["grid_origin_dirs"].keys():
        down_set_group  = para["grid_origin_dirs"][key]
        for down_set in down_set_group:
            if hm >= down_set[1] and hm <= down_set[2]:
                dir_list = []
                meteva.base.tool.path_tools.get_gds_all_dir(ip,port,down_set[0],dir_list)
                for dir in dir_list:
                    file_list = meteva.base.tool.path_tools.get_gds_file_list_in_one_dir(ip,port,dir)
                    file_list.sort(reverse=True)
                    for file in file_list:
                        dati = get_dati_of_path(file)
                        if dati < weekago: break
                        save_path = para["local_binary_dir"] + "/" +dir+"/" +file
                        if not os.path.exists(save_path):
                            download_grid_list.append(dir + "/" + file)
                        else:
                            try:
                                dati_str = get_dati_str_of_path(save_path)
                                save_path_nc = para["local_grid_dir"] + "/" + dir + "/" + dati_str + "/" + file+".nc"
                                if not os.path.exists(save_path_nc):
                                    if dir.upper().find("WIND")>=0:
                                        if (dir.upper().find("GUST"))>=0:
                                            grd = meteva.base.read_griddata_from_gds_file(save_path)
                                        else:
                                            grd = meteva.base.read_gridwind_from_gds_file(save_path)
                                    else:
                                        grd = meteva.base.read_griddata_from_gds_file(save_path)
                                    if grd is not None:
                                        meteva.base.write_griddata_to_nc(grd, save_path_nc, creat_dir=True)
                                    else:
                                        print(save_path + "文件格式错误")
                            except Exception as e:
                                print(e)

    download_mp(ip, port, para["local_binary_dir"], para["local_sta_dir"], para["local_grid_dir"], download_sta_list, download_grid_list,
                para["cup_count"])


def download1(para):
    #遍历下载
    now = datetime.datetime.now()
    hm = now.hour * 100 + now.minute
    ip,port = meteva.base.io.read_gds_ip_port(para["ip_port_file"])
    service = GDSDataService(ip, port)
    if (service is None):
        print("service is None")
        return


    for down_set in para["sta_origin_dirs"]:
        if hm >= down_set[1] and hm <= down_set[2]:
            dir_list = []
            meteva.base.tool.path_tools.get_gds_all_dir(ip,port,down_set[0],dir_list)
            for dir in dir_list:
                file_list = meteva.base.tool.path_tools.get_gds_file_list_in_one_dir(ip,port,dir)
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
                                    meteva.base.tool.path_tools.creat_path(save_path)
                                    br = open(save_path, 'wb')
                                    br.write(byteArray)
                                    br.close()
                                    save_path_sta = para["local_sta_dir"] + "/" + dir +"/"+dati_str+ "/" + file
                                    meteva.base.tool.path_tools.creat_path(save_path_sta)
                                    br = open(save_path_sta, 'wb')
                                    br.write(byteArray)
                                    br.close()
                                    print(para["cup_id"] +" " + save_path_sta)
                        except Exception as e:
                            print(e)
                    else:
                        try:
                            save_path_sta = para["local_sta_dir"] + "/" + dir + "/" + dati_str + "/" + file
                            if not os.path.exists(save_path_sta):
                                meteva.base.tool.path_tools.creat_path(save_path_sta)
                                shutil.copyfile(save_path,save_path_sta)
                        except Exception as e:
                            print(e)

    for key in para["grid_origin_dirs"].keys():
        down_set_group  = para["grid_origin_dirs"][key]
        for down_set in down_set_group:
            if hm >= down_set[1] and hm <= down_set[2]:
                dir_list = []
                meteva.base.tool.path_tools.get_gds_all_dir(ip,port,down_set[0],dir_list)
                for dir in dir_list:
                    file_list = meteva.base.tool.path_tools.get_gds_file_list_in_one_dir(ip,port,dir)
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
                                        meteva.base.tool.path_tools.creat_path(save_path)
                                        br = open(save_path, 'wb')
                                        br.write(byteArray)
                                        br.close()
                                        if dir.upper().find("WIND")>=0:
                                            if(dir.upper().find("GUST"))>=0:
                                                grd = meteva.base.io.byteArray_to_griddata(byteArray)
                                            else:
                                                grd = meteva.base.io.byteArray_to_gridwind(byteArray)
                                        else:
                                            grd = meteva.base.io.byteArray_to_griddata(byteArray)
                                        save_path_nc = para["local_grid_dir"] + "/" + dir +"/"+dati_str+ "/" + file+".nc"
                                        print(para["cup_id"])
                                        meteva.base.write_griddata_to_nc(grd,save_path_nc,creat_dir=True)
                            except Exception as e:
                                print(e)
                        else:
                            try:
                                save_path_nc = para["local_grid_dir"] + "/" + dir + "/" + dati_str + "/" + file+".nc"
                                if not os.path.exists(save_path_nc):
                                    if dir.upper().find("WIND")>=0:
                                        if (dir.upper().find("GUST"))>=0:
                                            grd = meteva.base.read_griddata_from_gds_file(save_path)
                                        else:
                                            grd = meteva.base.read_gridwind_from_gds_file(save_path)
                                    else:
                                        grd = meteva.base.read_griddata_from_gds_file(save_path)
                                    if grd is not None:
                                        meteva.base.write_griddata_to_nc(grd, save_path_nc, creat_dir=True)
                                    else:
                                        print(save_path + "文件格式错误")
                            except Exception as e:
                                print(e)


'''
def download(para):
    multi_pro_num = para["cup_count"]
    para_list = []
    max_pro_num = cpu_count() - 2
    if multi_pro_num>max_pro_num:
        multi_pro_num = max_pro_num

    for i in range(multi_pro_num):
        para_one = {}
        para_one["cup_id"] = i
        para_one["ip_port_file"]= para["ip_port_file"]
        para_one["local_binary_dir"]=para["local_binary_dir"]
        para_one["local_sta_dir"]=para["local_sta_dir"]
        para_one["local_grid_dir"]=para["local_grid_dir"]
        para_one["max_save_day"] = para["max_save_day"]
        para_one["sta_origin_dirs"] =[]
        para_one["grid_origin_dirs"] = {}
        para_list.append(para_one)

    sta_list = para["sta_origin_dirs"]
    for i in range(len(sta_list)):
        para_one = para_list[i % multi_pro_num]
        para_one["sta_origin_dirs"].append(para["sta_origin_dirs"][i])

    fo_key_list = list(para["grid_origin_dirs"].keys())
    for i in range(len(fo_key_list)):
        para_one = para_list[i % multi_pro_num]
        key = fo_key_list[i]
        para_one["grid_origin_dirs"][key] = para["grid_origin_dirs"][key]

    print(para_list)
    PP = []
    for k in range(multi_pro_num):
        run_para = para_list[k]
        tmpp = Process(target=download_one,args=run_para)
        PP.append(tmpp)

    print('Waiting for all subprocesses done...')

    for pc in PP:
        pc.start()

    for pp in PP:
        pp.join()
    print('All subprocesses done.')
'''

def remove(para):
    dir = para["local_binary_dir"]
    file_list = meteva.base.tool.path_tools.get_path_list_in_dir(dir)
    now = datetime.datetime.now()
    for file in file_list:
        dati = get_dati_of_path(file)
        dday = (now - dati).total_seconds()/(3600*24)
        if dday > para["max_save_day"]:
            os.remove(file)



