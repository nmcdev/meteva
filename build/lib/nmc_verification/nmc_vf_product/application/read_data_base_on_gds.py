import nmc_verification
import os

def find_exist_file(para,filename):
    #首先在本地binaray目录找
    filename = filename.replace("mdfs:///","")
    path = para["local_binary_dir"] +"/"+ filename
    if os.path.exists(path):
        return path
    time_str = nmc_verification.nmc_vf_product.get_dati_str_of_path(path)
    dir,filename1 = os.path.split(filename)
    path = para["local_sta_dir"]+"/" + dir + "/"+time_str+"/"+filename1
    if os.path.exists(path):
        return path
    path = para["local_grid_dir"]+"/" + dir + "/"+time_str+"/"+filename1+".nc"
    if os.path.exists(path):
        return path
    return None

def read_stadata(para, filename,element_id,station = None, level=None,time=None, dtime=None, data_name='data0'):
    path = find_exist_file(para,filename)
    print(path)
    if path is None:
        ip, port = nmc_verification.nmc_vf_base.io.read_gds_ip_port(para["ip_port_file"])
        return nmc_verification.nmc_vf_base.io.read_stadata_from_gds(ip,port,filename,element_id,station,level,time,dtime,data_name)
    else:
        return nmc_verification.nmc_vf_base.io.read_stadata_from_gdsfile(path, element_id, station, level, time,
                                                              dtime, data_name)


def read_stadata_from_griddata(para,filename,station):
    path = find_exist_file(para,filename)
    print(path)
    if path is None:
        ip, port = nmc_verification.nmc_vf_base.io.read_gds_ip_port(para["ip_port_file"])
        return nmc_verification.nmc_vf_base.read_stadata_from_gds_griddata(ip,port,filename,station)
    else:
        file1,ft = os.path.splitext(path)
        if ft == ".nc":
            grd = nmc_verification.nmc_vf_base.read_griddata_from_nc(path)
            sta = nmc_verification.nmc_vf_base.fun.interp_gs_linear(grd,station)
            return sta
        else:
            return nmc_verification.nmc_vf_base.read_stadata_from_gds_griddata_file(path,station)

def read_griddata(para,filename,grid = None):
    path = find_exist_file(para,filename)
    print(path)
    if path is None:
        ip, port = nmc_verification.nmc_vf_base.io.read_gds_ip_port(para["ip_port_file"])
        if filename.find("WIND")>=0:
            return nmc_verification.nmc_vf_base.read_gridwind_from_gds(ip, port, filename, grid)
        else:
            return nmc_verification.nmc_vf_base.read_griddata_from_gds(ip,port,filename,grid)
    else:
        file1,ft = os.path.splitext(path)
        if ft == ".nc":
            return nmc_verification.nmc_vf_base.read_griddata_from_nc(path,grid)
        else:
            if filename.find("WIND") >= 0:
                return nmc_verification.nmc_vf_base.read_gridwind_from_gds_file(path,grid)
            else:
                return nmc_verification.nmc_vf_base.read_griddata_from_gds_file(path,grid)

