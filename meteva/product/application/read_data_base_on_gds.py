import meteva
import os

def find_exist_file(para,filename):
    #首先在本地binaray目录找
    filename = filename.replace("mdfs:///","")
    time_str = meteva.product.get_dati_str_of_path(filename)
    dir,filename1 = os.path.split(filename)
    path = para["local_sta_dir"]+"/" + dir + "/"+time_str+"/"+filename1
    if os.path.exists(path):
        return path
    path = para["local_grid_dir"]+"/" + dir + "/"+time_str+"/"+filename1+".nc"
    if os.path.exists(path):
        return path

    path = para["local_binary_dir"] +"/"+ filename
    if os.path.exists(path):
        return path

    return None

def read_stadata(para, filename,element_id = None,station = None, level=None,time=None, dtime=None, data_name='data0'):
    path = find_exist_file(para,filename)
    print(path)
    if path is None:
        ip, port = meteva.base.io.read_gds_ip_port(para["ip_port_file"])
        return meteva.base.io.read_stadata_from_gds(ip,port,filename,element_id,station,level,time,dtime,data_name)
    else:
        return meteva.base.io.read_stadata_from_gdsfile(path, element_id, station, level, time,
                                                              dtime, data_name)

def read_stadata_from_griddata(para,filename,station):
    path = find_exist_file(para,filename)
    if path is None:
        ip, port = meteva.base.io.read_gds_ip_port(para["ip_port_file"])
        print(filename)
        return meteva.base.read_stadata_from_gds_griddata(ip,port,filename,station)
    else:
        print(path)
        file1,ft = os.path.splitext(path)
        if ft == ".nc":
            grd = meteva.base.read_griddata_from_nc(path)
            sta = meteva.base.fun.interp_gs_linear(grd,station)
            return sta
        else:
            return meteva.base.read_stadata_from_gds_griddata_file(path,station)

def read_griddata(para,filename,grid = None):
    path = find_exist_file(para,filename)
    print(path)
    if path is None:
        ip, port = meteva.base.io.read_gds_ip_port(para["ip_port_file"])
        if filename.find("WIND")>=0:
            return meteva.base.read_gridwind_from_gds(ip, port, filename, grid)
        else:
            return meteva.base.read_griddata_from_gds(ip,port,filename,grid)
    else:
        file1,ft = os.path.splitext(path)
        if ft == ".nc":
            return meteva.base.read_griddata_from_nc(path,grid)
        else:
            if filename.find("WIND") >= 0:
                return meteva.base.read_gridwind_from_gds_file(path,grid)
            else:
                return meteva.base.read_griddata_from_gds_file(path,grid)

def read_stawind(para, filename,station = None, level=None,time=None, dtime=None):
    path = find_exist_file(para,filename)
    print(path)
    if path is None:
        ip, port = meteva.base.io.read_gds_ip_port(para["ip_port_file"])
        return meteva.base.io.read_stawind_from_gds(ip,port,filename,station,level,time,dtime)
    else:
        return meteva.base.io.read_stawind_from_gdsfile(path,  station, level, time,
                                                              dtime)


def read_stawind_from_gridwind(para,filename,station):

    path = find_exist_file(para,filename)
    print(path)
    if path is None:
        ip, port = meteva.base.io.read_gds_ip_port(para["ip_port_file"])
        grd = meteva.base.io.read_gridwind_from_gds(ip,port,filename)
        if grd is not None:
            sta = meteva.base.fun.interp_gs_linear(grd,station)
            return sta
        else:
            return None
    else:
        file1,ft = os.path.splitext(path)
        if ft == ".nc":
            grd = meteva.base.read_griddata_from_nc(path)
            sta = meteva.base.fun.interp_gs_linear(grd,station)
            return sta
        else:
            return meteva.base.read_stawind_from_gds_gridwind_file(path,station)