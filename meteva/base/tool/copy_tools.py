import os
import meteva
import matplotlib.colors as colors
import time
from meteva.base.io.GDS_data_service import GDSDataService
from meteva.base.io import DataBlock_pb2
from multiprocessing import freeze_support,Process,cpu_count




def copy_data_one_cup(input_path,output_path,read_method,write_method,read_args,write_args):

    dat = read_method(filename = input_path,**read_args)
    meteva.base.creat_path(output_path)
    write_method(dat,save_path = output_path,**write_args)



def copy_data(input_root_dir,output_root_dir,read_method,write_method,read_args ={},write_args ={}, recover = False,tran_extension = None,process_count = 1):
    #获取所以的输入文件
    input_root_dir = input_root_dir.replace("\\", "/")
    output_root_dir = output_root_dir.replace("\\", "/")
    if input_root_dir[-1] != "/":
        input_root_dir += "/"
    if output_root_dir[-1] != '/':
        output_root_dir += "/"
    file_list = meteva.base.tool.path_tools.get_path_list_in_dir(input_root_dir)
    len_input = len(input_root_dir)
    input_path_list = []
    output_path_list = []
    for file in file_list:
        filename_part = file[len_input:]
        output_path = output_root_dir + filename_part
        if tran_extension is not None:
            if tran_extension[0] == "+":
                output_path += tran_extension[1:]
            elif tran_extension[0] == "-":
                str_len = len(tran_extension) - 1
                if output_path[-str_len:] == tran_extension[1:]:
                    output_path = output_path[:-str_len]
            else:
                "print the chang_file_type args must start with + or -"
        if recover or not os.path.exists(output_path):
            input_path_list.append(file)
            output_path_list.append(output_path)
    meteva.base.tool.multi_run(process_count = process_count,method=copy_data_one_cup,
                               Input_path = input_path_list,Output_path = output_path_list,
                               read_method = read_method,write_method = write_method,
                               read_args  = read_args,write_args = write_args)



def copy_m4_to_nc(input_root_dir,output_root_dir,effectiveNum = 3,recover= False,grid = None):
    input_root_dir = input_root_dir.replace("\\","/")
    output_root_dir = output_root_dir.replace("\\","/")
    if input_root_dir[-1] != "/":
        input_root_dir += "/"
    if output_root_dir[-1] != '/':
        output_root_dir += "/"
    (gds_dir,file_model) = os.path.split(input_root_dir)
    save_dir = output_root_dir
    file_list = meteva.base.tool.path_tools.get_path_list_in_dir(gds_dir)
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
            meteva.base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = meteva.base.io.read_griddata_from_micaps4(path_input)
            else:
                grd = meteva.base.io.read_griddata_from_micaps4(path_input,grid=grid)
            if grd is not None:
                meteva.base.io.write_griddata_to_nc(grd,path_output,effectiveNum)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                #print(path_output)



def copy_gds_to_nc(input_root_dir,output_root_dir,effectiveNum = 3,recover= False,grid = None):
    input_root_dir = input_root_dir.replace("\\","/")
    output_root_dir = output_root_dir.replace("\\","/")
    if input_root_dir[-1] != "/":
        input_root_dir += "/"
    if output_root_dir[-1] != '/':
        output_root_dir += "/"
    (gds_dir,file_model) = os.path.split(input_root_dir)
    save_dir = output_root_dir
    file_list = meteva.base.tool.path_tools.get_path_list_in_dir(gds_dir)
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
            meteva.base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = meteva.base.io.read_griddata_from_gds_file(path_input)
            else:
                grd = meteva.base.io.read_griddata_from_gds_file(path_input,grid=grid)
            if grd is not None:
                meteva.base.io.write_griddata_to_nc(grd,path_output,effectiveNum)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)


def copy_gds_to_m4(input_root_dir,output_root_dir,effectiveNum = 3,recover= False,grid = None):
    input_root_dir = input_root_dir.replace("\\","/")
    output_root_dir = output_root_dir.replace("\\","/")
    if input_root_dir[-1] != "/":
        input_root_dir += "/"
    if output_root_dir[-1] != '/':
        output_root_dir += "/"
    (gds_dir,file_model) = os.path.split(input_root_dir)
    save_dir = output_root_dir
    file_list = meteva.base.tool.path_tools.get_path_list_in_dir(gds_dir)
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
            meteva.base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = meteva.base.io.read_griddata_from_gds_file(path_input)
            else:
                grd = meteva.base.io.read_griddata_from_gds_file(path_input,grid=grid)
            if grd is not None:
                meteva.base.io.write_griddata_to_micaps4(grd,path_output,effectiveNum = effectiveNum)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)



def copy_wind_gds_to_nc(input_root_dir,output_root_dir,effectiveNum = 3,recover= False,grid = None):
    input_root_dir = input_root_dir.replace("\\","/")
    output_root_dir = output_root_dir.replace("\\","/")
    if input_root_dir[-1] != "/":
        input_root_dir += "/"
    if output_root_dir[-1] != '/':
        output_root_dir += "/"
    (gds_dir,file_model) = os.path.split(input_root_dir)
    save_dir = output_root_dir
    file_list = meteva.base.tool.path_tools.get_path_list_in_dir(gds_dir)
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
            meteva.base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = meteva.base.io.read_gridwind_from_gds_file(path_input)
            else:
                grd = meteva.base.io.read_gridwind_from_gds_file(path_input,grid=grid)
            if grd is not None:
                meteva.base.io.write_griddata_to_nc(grd,path_output,effectiveNum)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)



def copy_wind_gds_to_m11(input_root_dir,output_root_dir,effectiveNum = 3,recover= False,grid = None):
    input_root_dir = input_root_dir.replace("\\","/")
    output_root_dir = output_root_dir.replace("\\","/")
    if input_root_dir[-1] != "/":
        input_root_dir += "/"
    if output_root_dir[-1] != '/':
        output_root_dir += "/"
    (gds_dir,file_model) = os.path.split(input_root_dir)
    save_dir = output_root_dir
    file_list = meteva.base.tool.path_tools.get_path_list_in_dir(gds_dir)
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
            meteva.base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = meteva.base.io.read_griddata_wind_from_gds_file(path_input)
            else:
                grd = meteva.base.io.read_gridwind_from_gds_file(path_input,grid=grid)
            if grd is not None:
                meteva.base.io.write_griddata_to_micaps11(grd,path_output,effectiveNum)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)



def copy_wind_m2_to_m11(input_root_dir,output_root_dir,effectiveNum = 3,recover= False,grid = None):
    input_root_dir = input_root_dir.replace("\\","/")
    output_root_dir = output_root_dir.replace("\\","/")
    if input_root_dir[-1] != "/":
        input_root_dir += "/"
    if output_root_dir[-1] != '/':
        output_root_dir += "/"
    (gds_dir,file_model) = os.path.split(input_root_dir)
    save_dir = output_root_dir
    file_list = meteva.base.tool.path_tools.get_path_list_in_dir(gds_dir)
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
            meteva.base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = meteva.base.io.read_griddata_wind_from_micaps2(path_input)
            else:
                grd = meteva.base.io.read_griddata_wind_from_micaps2(path_input,grid=grid)
            if grd is not None:
                meteva.base.io.write_griddata_to_micaps11(grd,path_output,effectiveNum)
                end = time.time()
                copyed_num +=1

                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60)) + 1
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)



def copy_wind_m11_to_nc(input_root_dir,output_root_dir,effectiveNum = 3,recover= False,grid = None):
    input_root_dir = input_root_dir.replace("\\","/")
    output_root_dir = output_root_dir.replace("\\","/")
    if input_root_dir[-1] != "/":
        input_root_dir += "/"
    if output_root_dir[-1] != '/':
        output_root_dir += "/"
    (gds_dir,file_model) = os.path.split(input_root_dir)
    save_dir = output_root_dir
    file_list = meteva.base.tool.path_tools.get_path_list_in_dir(gds_dir)
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
            meteva.base.tool.path_tools.creat_path(path_output)
            if grid is None:
                grd = meteva.base.io.read_griddata_wind_from_micap11(path_input)
            else:
                grd = meteva.base.io.read_gridwind_from_micap11(path_input,grid=grid)
            if grd is not None:
                meteva.base.io.write_griddata_to_nc(grd,path_output,effectiveNum)
                end = time.time()
                copyed_num +=1
                left_minutes = int((end - start) * ( file_num - i -1) / (copyed_num * 60))
                print("剩余" + str(left_minutes) + "分钟")
                print(path_output)


def download_gds_files_to_local(ip, port, gds_dir, local_dir,recover= False):
    print(gds_dir)
    filelist = meteva.base.tool.path_tools.get_gds_file_list_in_one_dir(ip, port, gds_dir)
    for file in filelist:
        save_path = local_dir +  "/" + file
        if not os.path.exists(save_path) or recover:
            service = GDSDataService(ip, port)
            if service is not None:
                status, response = service.getData(gds_dir, file)
                if status == 200:
                    ByteArrayResult = DataBlock_pb2.ByteArrayResult()
                    ByteArrayResult.ParseFromString(response)
                    meteva.base.tool.path_tools.creat_path(save_path)
                    br = open(save_path, 'wb')
                    br.write(ByteArrayResult.byteArray)
                    br.close()