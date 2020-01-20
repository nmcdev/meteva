import pkg_resources
import os
from nmc_verification.nmc_vf_base.tool.path_tools import creat_path
#dir = pkg_resources.resource_filename('nmc_verification', "resources/stations/grib_api/bin")

def grib_to_nc1(grib_filename,output_dir = None):
    path_cd = grib_filename
    if (os.path.exists(path_cd)):
        # print(path_cd)
        filename, extension = os.path.splitext(path_cd)
        if output_dir is not None:
            output_dir = output_dir.replace("\\", "/")
            output_dir = output_dir + "/"
            creat_path(output_dir)
            dir, filename0 = os.path.split(filename)
            filename = output_dir + filename0
            filename = filename.replace("\\", "/")
        # print(filename)

        #path_out_grib_isobaricInhPa = filename + "_isobaric" + extension
        path_out_nc_isobaricInhPa = filename + ".nc"

        # start = time.time()
        #run_path = "grib_copy.exe -w typeOfLevel=surface,edition=1  " + path_cd + " " + path_out_grib_surface1
        #os.system(run_path)
        #run_path = "grib_copy.exe -w typeOfLevel=surface,edition=2  " + path_cd + " " + path_out_grib_surface2
        #os.system(run_path)
        #run_path = "grib_copy.exe -w typeOfLevel=isobaricInhPa  " + path_cd + " " + path_out_grib_isobaricInhPa
        #os.system(run_path)

        #os.system(r"grib_to_netcdf -o " + path_out_nc1_surface + " " + path_out_grib_surface1)
        #os.system(r"grib_to_netcdf -o " + path_out_nc2_surface + " " + path_out_grib_surface2)
        #os.system(r"grib_to_netcdf -o " + path_out_nc_isobaricInhPa + " " + path_out_grib_isobaricInhPa)
        os.system(r"grib_to_netcdf -o " + path_out_nc_isobaricInhPa+ " " + path_cd)
        # if (os.path.exists(path_cd)): os.remove(path_cd)
        result_list = []
        if (os.path.exists(path_out_nc_isobaricInhPa)): result_list.append(path_out_nc_isobaricInhPa)
        if len(result_list) > 1:
            print("转换生成如下文件：")
            for result in result_list:
                print(result)
            return result_list
        else:
            "未正常生成转换后的nc文件"
            return None

def grib_to_nc(grib_filename,output_dir = None):
    path_cd = grib_filename
    if (os.path.exists(path_cd)):
        #print(path_cd)
        filename,extension = os.path.splitext(path_cd)
        if output_dir is not None:
            output_dir = output_dir.replace("\\","/")
            output_dir = output_dir +"/"
            creat_path(output_dir)
            dir,filename0 = os.path.split(filename)
            filename = output_dir  + filename0
            filename = filename.replace("\\", "/")
        #print(filename)
        path_out_grib_surface1 = filename+"_surface1"+ extension
        path_out_grib_surface2 = filename + "_surface2" + extension
        path_out_grib_isobaricInhPa  = filename + "_isobaric" + extension
        path_out_nc1_surface = filename+"_surface1"+ ".nc"
        path_out_nc2_surface = filename+"_surface2"+ ".nc"
        path_out_nc_isobaricInhPa = filename + "_isobaric" + ".nc"

        # start = time.time()
        run_path = "grib_copy.exe -w typeOfLevel=surface,edition=1  " + path_cd + " " + path_out_grib_surface1
        os.system(run_path)
        run_path = "grib_copy.exe -w typeOfLevel=surface,edition=2  " + path_cd + " " + path_out_grib_surface2
        os.system(run_path)
        run_path = "grib_copy.exe -w typeOfLevel=isobaricInhPa  " + path_cd + " " + path_out_grib_isobaricInhPa
        os.system(run_path)

        os.system(r"grib_to_netcdf -o " + path_out_nc1_surface + " " + path_out_grib_surface1)
        os.system(r"grib_to_netcdf -o " + path_out_nc2_surface + " " + path_out_grib_surface2)
        os.system(r"grib_to_netcdf -o " + path_out_nc_isobaricInhPa + " " + path_out_grib_isobaricInhPa)

        #if (os.path.exists(path_cd)): os.remove(path_cd)
        if (os.path.exists(path_out_grib_isobaricInhPa)): os.remove(path_out_grib_isobaricInhPa)
        if (os.path.exists(path_out_grib_surface1)): os.remove(path_out_grib_surface1)
        if (os.path.exists(path_out_grib_surface2)): os.remove(path_out_grib_surface2)

        result_list = []
        if (os.path.exists(path_out_nc1_surface)): result_list.append(path_out_nc1_surface)
        if (os.path.exists(path_out_nc2_surface)): result_list.append(path_out_nc2_surface)
        if (os.path.exists(path_out_nc_isobaricInhPa)): result_list.append(path_out_nc_isobaricInhPa)
        if len(result_list)>1:
            print("转换生成如下文件：")
            for result in result_list:
                print(result)
            return result_list
        else:
            "未正常生成转换后的nc文件"
            return None


