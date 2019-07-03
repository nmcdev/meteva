import os
import nmc_verification
import matplotlib.colors as colors


def copy_m4_to_nc(input_root_dir,output_root_dir,scale_factor = 0.01):
    input_root_dir = input_root_dir.replace("\\","/")
    output_root_dir = output_root_dir.replace("\\","/")
    if input_root_dir[-1] != "/":
        input_root_dir += "/"
    if output_root_dir[-1] != '/':
        output_root_dir += "/"
    (gds_dir,file_model) = os.path.split(input_root_dir)
    save_dir = output_root_dir
    file_list = nmc_verification.nmc_vf_base.tool.path_tools.get_filename_list_in_dir(gds_dir)
    len_input = len(input_root_dir)
    file_num = len(file_list)
    for i in range(file_num):
        file = file_list[i]
        path_input = file.replace("\\","/")
        path_file = path_input[len_input:]
        path_output = output_root_dir + path_file+".nc"
        if not os.path.exists(path_output):
            nmc_verification.nmc_vf_base.tool.path_tools.creat_path(path_output)
            grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_micaps4(path_input)
            if grd is not None:
                nmc_verification.nmc_vf_base.io.write_griddata.write_to_nc(grd,path_output,scale_factor)
            print(100 * i / file_num)
            print(path_output)


idir = r"\\10.20.67.49\u01\data\GRAPES_GFS_MICAPS"
#idir = r"\\10.20.67.49\u01\data\GRAPES_GFS_MICAPS\RAIN24\2018\20181231"
odir = r"G:\grapes_gfs_nc"
copy_m4_to_nc(idir,odir)