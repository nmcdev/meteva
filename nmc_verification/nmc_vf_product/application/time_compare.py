import nmc_verification
import datetime
import time
import os
import pandas as pd

def read_stadata_from_gds_file_or_service(binary_root,ip,port,filename,station,gds_filename_list = None):
    filename1 = binary_root + "/" + filename
    if os.path.exists(filename1):
        #print("从本地读取数据")
        sta = nmc_verification.nmc_vf_base.read_stadata_from_gds_griddata_file(filename1,station)
        return sta
    else:
        #print("从gds读取数据")
        dir, filename2 = os.path.split(filename)
        if gds_filename_list is None:
            gds_filename_list = nmc_verification.nmc_vf_base.path_tools.get_gds_file_list_in_one_dir(ip, port, dir)
        if filename2 in gds_filename_list:
            sta = nmc_verification.nmc_vf_base.read_stadata_from_gds_griddata(ip, port, dir + "/" + filename2, station)
            return sta
        else:
            #print(filename + "文件不存在")
            return None


def gds_ob_multi_time_fo(para):
    now = datetime.datetime.now()
    now = datetime.datetime(now.year, now.month, now.day, now.hour, 0)
    for file in para["ip_port_file"]:
        if os.path.exists(file):
            ip, port = nmc_verification.nmc_vf_base.read_gds_ip_port(file)
            break
    df = pd.DataFrame({"id": para["station_id_list"],
                       "lon":para["station_lon_list"],
                       "lat":para["station_lat_list"]})
    station = nmc_verification.nmc_vf_base.sta_data(df)
    station["data0"] = 1e10
    #print(station)
    id_list = para["station_id_list"]
    fo_time_list = []
    for i in range(para["max_dh"] + 12):
        time0 = now - datetime.timedelta(hours=i)
        if time0.hour in para["update_hours"]:
            fo_time_list.append(time0)
    #time0 = now - datetime.timedelta(hours =24)
    #path = nmc_verification.nmc_vf_base.get_path(para["ob_dir"], time0)
    #nmc_verification.nmc_vf_base.print_gds_file_values_names(ip, port, path)

    if para["value_type"] == "风":
        dir_u, file_u = os.path.split(para["fo_grd_dir_u"])
        file_list_u = nmc_verification.nmc_vf_base.path_tools.get_gds_file_list_in_one_dir(ip, port, dir_u)
        dir_v, file_v = os.path.split(para["fo_grd_dir_v"])
        file_list_v = nmc_verification.nmc_vf_base.path_tools.get_gds_file_list_in_one_dir(ip, port, dir_v)

        # 读取预报数据
        sta_fo_all = None
        ob_time_list = []
        print("开始加载预报数据")
        begin = time.time()
        for i in range(len(fo_time_list)):
            time0 = fo_time_list[i]
            for dh in range(para["max_dh"]):
                filename = nmc_verification.nmc_vf_base.get_path(file_u, time0, dh)
                if not filename in file_list_u: continue
                sta_u = nmc_verification.nmc_vf_base.read_stadata_from_gds_griddata(ip, port, dir_u + "/" + filename, station)
                if (sta_u is None): continue
                nmc_verification.nmc_vf_base.set_stadata_coords(sta_u, time=time0, dtime=dh)
                filename = nmc_verification.nmc_vf_base.get_path(file_v, time0, dh)
                if not filename in file_list_v: continue
                sta_v = nmc_verification.nmc_vf_base.read_stadata_from_gds_griddata(ip, port, dir_v + "/" + filename, station)
                if sta_v is None: continue
                nmc_verification.nmc_vf_base.set_stadata_coords(sta_v, time=time0, dtime=dh)
                sta_uv = nmc_verification.nmc_vf_base.combine_on_all_coords(sta_u, sta_v)
                nmc_verification.nmc_vf_base.set_stadata_names(sta_uv, data_name_list=["u" + para["title"], "v" + para["title"]])
                sta_fo_all = nmc_verification.nmc_vf_base.combine_join(sta_fo_all, sta_uv)
                ob_time = time0 + datetime.timedelta(hours=dh)
                ob_time_list.append(ob_time)
                #print(filename)
            if(i>1):
                time_end  = time.time()
                time_left = int((time_end - begin) * (len(fo_time_list) - i - 1) / (i+1 )) + 1
                print("载入预报场还需" + str(time_left) + "秒")

        ob_time_list = set(ob_time_list)
        ob_time_list1 = []
        for ob_time in ob_time_list:
            if ob_time <= now:
                ob_time_list1.append(ob_time)
        ob_time_list1.sort()
        print("开始加载观测数据")
        begin = time.time()
        sta_ob_s_all = None
        sta_ob_d_all = None
        for i in range(len(ob_time_list1)):
            time0 = ob_time_list1[i]
            path = nmc_verification.nmc_vf_base.get_path(para["ob_dir"], time0)
            element_id = nmc_verification.nmc_vf_base.gds_element_id_dict[para["ob_s_name"]]
            sta_s = nmc_verification.nmc_vf_base.read_stadata_from_gds(ip, port, filename=path, element_id=element_id,station=station)
            if sta_s is None: continue
            sta_ob_s_all = nmc_verification.nmc_vf_base.combine_join(sta_ob_s_all, sta_s)
            element_id = nmc_verification.nmc_vf_base.gds_element_id_dict[para["ob_d_name"]]
            sta_d = nmc_verification.nmc_vf_base.read_stadata_from_gds(ip, port, filename=path, element_id=element_id,station=station)
            if sta_d is None: continue
            sta_ob_d_all = nmc_verification.nmc_vf_base.combine_join(sta_ob_s_all, sta_d)
            if i >1:
                time_end = time.time()
                time_left = int((time_end - begin) * (len(ob_time_list1) - i - 1) / (i + 1)) + 1
                print("载入观测数据还需" + str(time_left) + "秒")

        sta_ob_s_all = nmc_verification.nmc_vf_base.between_value_range(sta_ob_s_all, -1e10, 1e9)
        sta_ob_d_all = nmc_verification.nmc_vf_base.between_value_range(sta_ob_d_all, -1e10, 1e9)
        sta_ob_all = nmc_verification.nmc_vf_base.diag.speed_angle_to_wind(sta_ob_s_all, sta_ob_d_all)

        for id in id_list:
            output_path = para["output_dir"]
            if (output_path is not None):
                output_path = nmc_verification.nmc_vf_base.get_path(output_path, now)
                output_path = output_path + "/" + str(id) + ".png"
            sta_ob = nmc_verification.nmc_vf_base.in_id_list(sta_ob_all, [id])
            sta_fo = nmc_verification.nmc_vf_base.in_id_list(sta_fo_all, [id])
            nmc_verification.nmc_vf_product.wind_ob_and_multi_time_fo(sta_ob, sta_fo, pic_path=output_path, max_dh=para["max_dh"],
                                                     plot_error=True)
    else:
        dir, file = os.path.split(para["fo_grd_dir"])
        file_list = nmc_verification.nmc_vf_base.path_tools.get_gds_file_list_in_one_dir(ip, port, dir)
        # 读取预报数据
        print("开始加载预报数据")
        begin = time.time()
        sta_fo_all = None
        ob_time_list = []
        for i in range(len(fo_time_list)):
            time0 = fo_time_list[i]
            for dh in range(para["max_dh"]):
                filename = nmc_verification.nmc_vf_base.get_path(file, time0, dh)
                sta_u = read_stadata_from_gds_file_or_service(para["local_root"],ip,port,dir + "/" + filename, station,file_list)
                #if not filename in file_list: continue
                #sta_u = nmc_verification.nmc_vf_base.read_stadata_from_gds_griddata(ip, port, dir + "/" + filename, station)
                if (sta_u is None): continue
                ob_time = time0 + datetime.timedelta(hours=dh)
                ob_time_list.append(ob_time)
                nmc_verification.nmc_vf_base.set_stadata_coords(sta_u, time=time0, dtime=dh)
                nmc_verification.nmc_vf_base.set_stadata_names(sta_u, data_name_list=[para["title"]])
                sta_fo_all = nmc_verification.nmc_vf_base.combine_join(sta_fo_all, sta_u)
            time_end  = time.time()
            time_left = int((time_end - begin) * (len(fo_time_list) - i - 1) / (i+1 )) + 1
            print("载入预报场还需" + str(time_left) + "秒")

        ob_time_list = set(ob_time_list)
        ob_time_list1 = []
        for ob_time in ob_time_list:
            if ob_time <= now:
                ob_time_list1.append(ob_time)
        ob_time_list1.sort()
        print("开始加载观测数据")
        begin = time.time()
        sta_ob_all = None
        for i in range(len(ob_time_list1)):
            time0 = ob_time_list1[i]
            path = nmc_verification.nmc_vf_base.get_path(para["ob_dir"], time0)
            sta_s = nmc_verification.nmc_vf_base.read_stadata_from_gds(ip, port, filename=path,
                                              element_id=nmc_verification.nmc_vf_base.gds_element_id_dict[para["ob_name"]],
                                                                       station= station)
            if sta_s is None: continue
            sta_ob_all = nmc_verification.nmc_vf_base.combine_join(sta_ob_all, sta_s)
            if i > 1:
                time_end = time.time()
                time_left = int((time_end - begin) * (len(ob_time_list1) - i - 1) / (i + 1)) + 1
                print("载入观测数据还需" + str(time_left) + "秒")

        sta_ob_all = nmc_verification.nmc_vf_base.between_value_range(sta_ob_all,-1e10,1e9)

        for id in id_list:
            output_path = para["output_dir"]
            if (output_path is not None):
                output_path = nmc_verification.nmc_vf_base.get_path(output_path, now)
                output_path = output_path + "/" + str(id) + ".png"
            sta_ob = nmc_verification.nmc_vf_base.in_id_list(sta_ob_all, [id])
            sta_fo = nmc_verification.nmc_vf_base.in_id_list(sta_fo_all, [id])
            if para["value_type"] == "温度":
                nmc_verification.nmc_vf_product.temp_ob_and_multi_time_fo(sta_ob, sta_fo, pic_path=output_path, max_dh=para["max_dh"],
                                                         plot_error=True)
            elif para["value_type"] == "降水1h":
                pass
            elif para["value_type"] == "能见度":
                nmc_verification.nmc_vf_product.vis_ob_and_multi_time_fo(sta_ob, sta_fo, pic_path=output_path, max_dh=para["max_dh"],
                                                         plot_error=True)
            elif para["value_type"] == "相对湿度":
                nmc_verification.nmc_vf_product.rh_ob_and_multi_time_fo(sta_ob, sta_fo, pic_path=output_path,
                                                                     max_dh=para["max_dh"],
                                                                     plot_error=True)