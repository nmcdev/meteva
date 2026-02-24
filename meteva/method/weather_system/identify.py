import datetime
import os
import json
import traceback
import numpy as np
import pandas as pd
import meteva
import matplotlib.pyplot as plt
import pkg_resources
import xarray as xr


def set_jar_path(path):
    if os.path.exists(path):
        meteva.base.ws_jar_path = path
        meteva.base.height_oy = os.path.split(path)[0] +"/height_oy.nc"
    else:
        print(path + " not exists")

def java_class_func(jar_path, class_name, func_name, jvm_path=None, *args):
    import jpype
    """
    调用jar包中class下的方法
    :return:
    """
    # jar包路径的配置
    # jarpath = os.path.join(os.path.abspath("."), "D:\\hf-0.1.jar")
    jarpath = os.path.join(os.path.abspath(".."), jar_path)
    # 这里指定了jvm
    if jvm_path:
        jvmpath = jvm_path
    else:
        jvmpath = jpype.getDefaultJVMPath()

    try:
        jpype.startJVM(jvmpath, "-ea", "-Djava.class.path=%s" % jarpath)
    except Exception as e:
        pass

    java_class = jpype.JClass(class_name)
    ru_param = ','.join(list(map(lambda x: json.dumps(x), args)))

    # f1 = open(r"d:/para.txt","w",encoding="utf-8")
    # f1.write(ru_param)
    # f1.close()
    res = str(eval("java_class.%s(%s)" % (func_name, ru_param)))
    #jpype.shutdownJVM()
    return res




def high_low_center(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100,grade_interval = 5):
    grid0 = meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()
    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()

    para = {"type":"high_low_center",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,"grade_interval":grade_interval,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    file1 = open(r"H:\task\develop\java\sysIdentify\para_json.txt","w")
    file1.write(para_json)
    file1.close()

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None

def vortex(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100):
    grid0 = meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()
    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()
    para = {"type":"vortex",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)


    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None


def anti_vortex(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 500):
    grid0 = meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()
    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()
    para = {"type":"anti_vortex",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    # file1 = open(r"H:\task\develop\java\sysIdentify\para_json.txt","w")
    # file1.write(para_json)
    # file1.close()


    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None

def trough(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100):
    grid0 = meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()

    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()

    para = {"type":"trough",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon":grid_h.slon,"h_slat":grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data":h_data}
    para_json = json.dumps(para)

    file1 = open(r"H:\task\develop\java\sysIdentify\para_json.txt","w")
    file1.write(para_json)
    file1.close()

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None


def reverse_trough(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100):
    grid0 = meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()
    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()
    para = {"type":"reverse_trough",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)
    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None

def convergence_line(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()
    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()
    para = {"type":"convergence_line",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None


def shear(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()
    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()
    para = {"type":"shear",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    file1 = open(r"H:\task\develop\java\sysIdentify\para_json.txt","w")
    file1.write(para_json)
    file1.close()

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None

def jet(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 100,jet_min_speed = 12,only_south_jet =False):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()
    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()
    para = {"type":"jet",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":resolution,"jet_min_speed":jet_min_speed,"only_south_jet":str(only_south_jet),
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)



    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None


def subtropical_high(grd,output_dir_root,smooth_times = 0,min_size = 500,necessary_height = 5840,sufficient_height = 5880):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()
    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()
    para = {"type":"subtropical_high",
            "smooth_times":smooth_times,"min_size":min_size,"necessary_height":necessary_height,"sufficient_height":sufficient_height,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    # file1 = open(r"H:\task\develop\java\sysIdentify\para_json.txt","w")
    # file1.write(para_json)
    # file1.close()

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None


def south_asia_high(grd,output_dir_root,smooth_times = 0,min_size = 800,sn_height = 16680):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()
    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()
    para = {"type":"south_asia_high",
            "smooth_times":smooth_times,"min_size":min_size,"sn_height":sn_height,
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None

def tran_graphy_to_df(graphy):
    '''

    :param graphy:
    :return:
    '''
    if graphy is None: return None,None

    dtime = int(graphy["dtime"])

    time  = meteva.base.all_type_time_to_time64(graphy["time"])

    level = graphy["level"]

    ids = graphy["features"].keys()

    list1 = []
    center = None
    for id in ids:
        feature = graphy["features"][id]
        lon = feature["center"]["lon"]
        lat = feature["center"]["lat"]
        center_value = round(feature["center"]["value"],2)
        if len(feature["region"].keys())>0:
            area = round(feature["region"]["area"],2)
            strength = round(feature["region"]["strength"])
            dict1 = {"level":level,"time":time,"dtime":dtime,"id" :int(id),"lon":lon,"lat":lat,"value":center_value,"area":area,"strength":strength}
            list1.append(dict1)
    if len(list1)>0:
        center = pd.DataFrame(list1)

    list1 = []
    for id in ids:
        points = graphy["features"][id]["axes"]["point"]
        if len(points)>0:
            array = np.array(points)
            lon = array[:,0]
            lat = array[:,1]
            df = pd.DataFrame({"lon":lon,"lat":lat})
            df["id"] = int(id)
            list1.append(df)
    if len(list1)>0:
        df = pd.concat(list1,axis = 0)
        df["level"] = level
        df["time"] = time
        df["dtime"] = dtime
        df["data0"] = 0
        axes = meteva.base.sta_data(df)
        return center,axes
    else:
        return center,None

def cold_front(grd,output_dir_root,smooth_times = 0,min_size = 500):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()
    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()
    para = {"type":"cold_front",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":"low",
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    # file1 = open(r"H:\task\develop\java\sysIdentify\para_json.txt","w")
    # file1.write(para_json)
    # file1.close()

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None


def warm_front(grd,output_dir_root,smooth_times = 10,min_size = 300):
    grid0 =  meteva.base.get_grid_of_data(grd)
    data = grd.values.flatten().tolist()
    height_oy = meteva.base.read_griddata_from_nc(meteva.base.height_oy)
    grid_h = meteva.base.get_grid_of_data(height_oy)
    h_data = height_oy.values.flatten().tolist()
    para = {"type":"warm_front",
            "smooth_times":smooth_times,"min_size":min_size,"resolution":"low",
            "level" : int(grid0.levels[0]),"time" : grid0.stime_str[0:10],"dtime" : int(grid0.dtimes[0]),
            "nlon":grid0.nlon,"nlat":grid0.nlat,"startlon":float(grid0.slon),"startlat":float(grid0.slat),"dlon":float(grid0.dlon),"dlat":float(grid0.dlat),
            "data":data,"output_dir_root":output_dir_root,
            "h_nlon": grid_h.nlon, "h_nlat": grid_h.nlat,
            "h_slon": grid_h.slon, "h_slat": grid_h.slat,
            "h_dlon": grid_h.dlon, "h_dlat": grid_h.dlat,
            "h_data": h_data
            }
    para_json = json.dumps(para)

    file1 = open(r"H:\task\develop\java\sysIdentify\para_json.txt","w")
    file1.write(para_json)
    file1.close()

    str_json = java_class_func(meteva.base.ws_jar_path,"Jpype","ws",None,para_json)
    if str_json !="null" and len(str_json)>0:
        graphy = json.loads(str_json)
        return graphy
    else:
        return None


if __name__=="__main__":
    jar_path = r"H:\task\develop\java\sysIdentify\out\artifacts\sysIdentify_jar\sysIdentify.jar"
    set_jar_path(jar_path)
    # grid6 = meteva.base.grid([0, 359.75, 0.25], [-89.75, 89.75, 0.25])
    # #grid6 = meteva.base.grid([150, 230, 0.5], [15, 65, 0.5])
    # t850 = meteva.base.read_griddata_from_micaps4(r"H:\test_data\input\mem\ws\ECMWF\T\850\18010820.000", grid=grid6)
    # t850.values -= meteva.base.K
    # output_dir_root = r"H:\test_data\output\method\ws"
    # graphy_wf = warm_front(t850, output_dir_root, smooth_times=30, min_size=500)

    # axs = meb.creat_axs(1, map_extend=grid6, ncol=1, add_minmap=False, wspace=1)
    # t850_smooth = meb.smooth(t850, 5)
    # meb.add_contourf(axs[0], t850_smooth, cmap=meb.cmaps.temp_2m)
    # meb.add_warm_fronts(axs[0], graphy_wf, linewidth=1)  # 绘制暖锋


    output_dir_root = r"H:\test_data\output\method\ws"
    #
    #path = r"H:\task\link\fengyun\20221230.nc"
    grid6 = meteva.base.grid([0, 359.5, 0.5], [-89.5, 89.5, 0.5])
    #h = meteva.base.read_griddata_from_nc(path,grid = grid6,level=500,dtime = 0)
    #trough(h,output_dir_root,smooth_times=30,min_size=500)
    path = r"H:\task\link\fengyun\ECMWF_D1D_FOR_GLB_U_20250307000000_12_100_50000.MIC"
    wind = meteva.base.read_gridwind_from_micaps11(path,grid = grid6,level=0,dtime=0)
    shear(wind,output_dir_root,min_size= 500)
    print()
    #path = r"\task\link\fengyun\1747909521636.m4.MIC"
    #grd = meteva.base.read_griddata_from_micaps4(path)
    # print(grd)
    #
    # #meteva.base.write_griddata_to_nc(grd,r"H:\task\develop\java\OAL\test_data\hgt\500\2024022420.000.nc")
    #
    #high_low_center(grd,output_dir_root,resolution = "low",smooth_times = 0,min_size = 1,grade_interval = 40)


    # path = r"O:\data\grid\ECMWF_HR\WIND\850\20220326\22032608.000.nc"
    # #
    # # import xarray
    # # wind = xarray.open_dataset(path)
    # # print(wind)
    # wind = meteva.base.read_griddata_from_nc(path)
    # print(wind)


    #save_path = r"H:\test_data\input\mem\ws\ECMWF\WIND\850\22032608.000"
    #wind = meteva.base.read_gridwind_from_micaps11(save_path,level=0,time = datetime.datetime(2022,3,26,8),dtime = 0)

    #meteva.base.write_griddata_to_micaps11(wind,save_path=r"H:\test_data\input\mem\ws\ECMWF\WIND\850\22032608.000",creat_dir=True)

    #graphy_anti_vortex =anti_vortex(wind,output_dir_root,smooth_times = 5)

    # grid6 = meteva.base.grid([150, 230, 0.5], [0, 80, 0.5])
    # t850 = meteva.base.read_griddata_from_micaps4(r"H:\test_data\input\mem\ws\ECMWF\T\850\18010820.000",grid = grid6)
    # graphy_cf = warm_front(t850, output_dir_root, smooth_times=30)

    # # 读取1000hPa位势高度场
    # h1000 = meteva.base.read_griddata_from_micaps4(r"H:\test_data\input\mem\ws\ECMWF\H\1000\22062600.012",
    #                                        level=1000, time="2022062600", dtime=12)
    # # 调用高低压识别算法
    # graphy_hl = meteva.method.weather_system.high_low_center(h1000, output_dir_root, smooth_times=10)
    # print(graphy_hl.keys())  # 返回结果的字典中包含了 type, level,time,dtime 和 features等关键词
    # save_path = r"H:\test_data\input\mem\ws\ECMWF\T\850\a.txt"
    # grd = meteva.base.read_griddata_from_gds_file(save_path)
    # save_path = r"H:\test_data\input\mem\ws\ECMWF\T\850\19071208.000"
    # meteva.base.write_griddata_to_micaps4(grd,save_path)

    #path = r"\\10.28.16.234\data2\AI\ECMWF\tigge\t850_201801.grib"
    # import xarray as xr
    # grd = xr.open_dataset(path)
    # print(grd)
    #grd = meteva.base.read_griddata_from_grib(path, value_name="t", dtime_dim="step", level_type="isobaricInhPa")
    #print(grd)

    # time1 = datetime.datetime(2018,1,1,8)
    # while time1 < datetime.datetime(2018,2,1,8):
    #     time_ut = time1 - datetime.timedelta(hours=8)
    #     #grd1 = meteva.base.sele_by_para(grd,time=[time_ut],dtime = 0)
    #     path = meteva.base.get_path(r"\\10.28.16.234\data2\AI\CRA40\2018\T\850\YYYYMMDDHH.nc",time_ut)
    #     grd1 = meteva.base.read_griddata_from_nc(path)
    #     save_path = meteva.base.get_path(r"H:\test_data\input\mem\ws\ECMWF\T\850\YYMMDDHH.000",time1)
    #
    #     meteva.base.write_griddata_to_micaps4(grd1,save_path=save_path)
    #     time1 += datetime.timedelta(hours=12)
    #


    # time1 = datetime.datetime(2018,1,1,8)
    # while time1 < datetime.datetime(2018,2,1,8):
    #     time_ut = time1 - datetime.timedelta(hours=8)
    #     #grd1 = meteva.base.sele_by_para(grd,time=[time_ut],dtime = 0)
    #     path = meteva.base.get_path(r"\\10.28.16.234\data2\AI\CRA40\2018\MSL\YYYYMMDDHH.nc",time_ut)
    #     grd1 = meteva.base.read_griddata_from_nc(path)
    #     grd1.values /=100
    #     save_path = meteva.base.get_path(r"H:\test_data\input\mem\ws\ECMWF\MSL\YYMMDDHH.000",time1)
    #
    #     meteva.base.write_griddata_to_micaps4(grd1,save_path=save_path,creat_dir=True)
    #     time1 += datetime.timedelta(hours=12)

