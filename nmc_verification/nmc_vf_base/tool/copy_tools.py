import os
import nmc_verification
import matplotlib.colors as colors
import time


def copy_m4_to_nc(input_root_dir,output_root_dir,scale_factor = 0.01,recover= False,grid = None):
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
    start = time.time()
    copyed_num = 0
    for i in range(file_num):
        file = file_list[i]
        path_input = file.replace("\\","/")
        path_file = path_input[len_input:]
        path_output = output_root_dir + path_file+".nc"
        if not os.path.exists(path_output) or recover:
            nmc_verification.nmc_vf_base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_micaps4(path_input)
            else:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_micaps4(path_input,grid=grid)
            if grd is not None:
                nmc_verification.nmc_vf_base.io.write_griddata.write_to_nc(grd,path_output,scale_factor)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)


def copy_gds_to_nc(input_root_dir,output_root_dir,scale_factor = 0.01,recover= False,grid = None):
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
    start = time.time()
    copyed_num = 0
    for i in range(file_num):
        file = file_list[i]
        path_input = file.replace("\\","/")
        path_file = path_input[len_input:]
        path_output = output_root_dir + path_file+".nc"
        if not os.path.exists(path_output) or recover:
            nmc_verification.nmc_vf_base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_gds_file(path_input)
            else:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_gds_file(path_input,grid=grid)
            if grd is not None:
                nmc_verification.nmc_vf_base.io.write_griddata.write_to_nc(grd,path_output,scale_factor)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)


def copy_gds_to_m4(input_root_dir,output_root_dir,scale_factor = 0.01,recover= False,grid = None):
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
    start = time.time()
    copyed_num = 0
    for i in range(file_num):
        file = file_list[i]
        path_input = file.replace("\\","/")
        path_file = path_input[len_input:]
        path_output = output_root_dir + path_file
        if not os.path.exists(path_output) or recover:
            nmc_verification.nmc_vf_base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_gds_file(path_input)
            else:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_from_gds_file(path_input,grid=grid)
            if grd is not None:
                nmc_verification.nmc_vf_base.io.write_griddata.write_to_micaps4(grd,path_output,effectiveNum=2)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)



def copy_wind_gds_to_nc(input_root_dir,output_root_dir,scale_factor = 0.01,recover= False,grid = None):
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
    start = time.time()
    copyed_num = 0
    for i in range(file_num):
        file = file_list[i]
        path_input = file.replace("\\","/")
        path_file = path_input[len_input:]
        path_output = output_root_dir + path_file+".nc"
        if not os.path.exists(path_output) or recover:
            nmc_verification.nmc_vf_base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_wind_from_gds_file(path_input)
            else:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_wind_from_gds_file(path_input,grid=grid)
            if grd is not None:
                nmc_verification.nmc_vf_base.io.write_griddata.write_to_nc(grd,path_output,scale_factor)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)



def copy_wind_gds_to_m11(input_root_dir,output_root_dir,scale_factor = 0.01,recover= False,grid = None):
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
    start = time.time()
    copyed_num = 0
    for i in range(file_num):
        file = file_list[i]
        path_input = file.replace("\\","/")
        path_file = path_input[len_input:]
        path_output = output_root_dir + path_file
        if not os.path.exists(path_output) or recover:
            nmc_verification.nmc_vf_base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_wind_from_gds_file(path_input)
            else:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_wind_from_gds_file(path_input,grid=grid)
            if grd is not None:
                nmc_verification.nmc_vf_base.io.write_griddata.write_to_micaps11(grd,path_output)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)



def copy_wind_m2_to_m11(input_root_dir,output_root_dir,scale_factor = 0.01,recover= False,grid = None):
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
    start = time.time()
    copyed_num = 0
    for i in range(file_num):
        file = file_list[i]
        path_input = file.replace("\\","/")
        path_file = path_input[len_input:]
        path_output = output_root_dir + path_file
        if not os.path.exists(path_output) or recover:
            nmc_verification.nmc_vf_base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_wind_from_micaps2(path_input)
            else:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_wind_from_micaps2(path_input,grid=grid)
            if grd is not None:
                nmc_verification.nmc_vf_base.io.write_griddata.write_to_micaps11(grd,path_output)
                end = time.time()
                copyed_num +=1

                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)



def copy_wind_m11_to_nc(input_root_dir,output_root_dir,scale_factor = 0.01,recover= False,grid = None):
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
    start = time.time()
    copyed_num = 0
    for i in range(file_num):
        file = file_list[i]
        path_input = file.replace("\\","/")
        path_file = path_input[len_input:]
        path_output = output_root_dir + path_file+".nc"
        if not os.path.exists(path_output) or recover:
            nmc_verification.nmc_vf_base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_wind_from_micap11(path_input)
            else:
                grd = nmc_verification.nmc_vf_base.io.read_griddata.read_wind_from_micap11(path_input,grid=grid)
            if grd is not None:
                nmc_verification.nmc_vf_base.io.write_griddata.write_to_nc(grd,path_output,scale_factor)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60))
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)

