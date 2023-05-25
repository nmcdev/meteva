
import numpy as np
import math
import meteva
import os
import traceback
import warnings
warnings.filterwarnings("ignore")


def write_griddata_to_micaps4(da,save_path = "a.txt",creat_dir = False,effectiveNum = 2,show = False,title = None,inte=None,vmin=None,vmax=None):
    """
    输出micaps4格式文件
    :param da:xarray多维数据信息,需要用 meteva 的格式
    :param save_path:存储路径
    :param creat_dir:存储路径中的文件夹若不存在是否创建
    :param effectiveNum：有效数字，默认 2
    :param show:是否输出存储结果，默认否
    :param title:MICAPS4第四类格式的title，默认根据 save_path 自动生成
    :param inte:MICAPS4第四类格式的等值线间隔，默认根据数值自动生成
    :param vmin:MICAPS4第四类格式的等值线起始值，默认根据数值自动生成
    :param vmax:MICAPS4第四类格式的等值线终止值，默认根据数值自动生成
    :return 最终按照需要保存的路径，将da数据保存为m4格式
    """
    try:
        dir = os.path.split(os.path.abspath(save_path))[0]
        if not os.path.isdir(dir):
            if not creat_dir:
                print("文件夹："+dir+"不存在")
                return False
            else:
                meteva.base.tool.path_tools.creat_path(save_path)

        grid = meteva.base.basicdata.get_grid_of_data(da)
        nlon = grid.nlon
        nlat = grid.nlat
        slon = grid.slon
        slat = grid.slat
        elon = grid.elon
        elat = grid.elat
        dlon = grid.dlon
        dlat = grid.dlat
        level = grid.levels[0]
        stime = grid.stime_str
        year = stime[0:4]
        month = stime[4:6]
        day = stime[6:8]
        hour = stime[8:10]
        hour_range = str(grid.dtimes[0])
        values = da.values
        grid_values = np.squeeze(values)
        
        if(vmax is None):
            vmax = math.ceil(max(grid_values.flatten()))
        if(vmin is None):
            vmin = math.ceil(min(grid_values.flatten()))
        
        if(inte is None):
            dif = (vmax - vmin) / 10.0
            if dif ==0:
                inte = 1
            else:
                inte = math.pow(10, math.floor(math.log10(dif)))
            # 用基本间隔，将最大最小值除于间隔后小数点部分去除，最后把间隔也整数化
            r = dif / inte
            if r < 3 and r >= 1.5:
                inte = inte * 2
            elif r < 4.5 and r >= 3:
                inte = inte * 4
            elif r < 5.5 and r >= 4.5:
                inte = inte * 5
            elif r < 7 and r >= 5.5:
                inte = inte * 6
            elif r >= 7:
                inte = inte * 8
            vmin = inte * ((int)(vmin / inte) - 1)
            vmax = inte * ((int)(vmax / inte) + 1)

        end = len(save_path)
        start = max(0, end - 16)

        if title is None:
            title = ("diamond 4 " + save_path[start:end] + "\n"
                     + year + " " + month + " " + day + " " + hour + " " + hour_range + " " + str(level) + "\n"
                     + "{:.6f}".format(grid.dlon) + " " + "{:.6f}".format(grid.dlat) + " " + "{:.6f}".format(grid.slon) + " " +"{:.6f}".format(grid.elon) + " "
                     + "{:.6f}".format(grid.slat) + " " + "{:.6f}".format(grid.elat) + " " + str(grid.nlon) + " " + str(grid.nlat) + " "
                     + str(inte) + " " + str(vmin) + " " + str(vmax) + " 1 0")
        else:

            title = ("diamond 4 "+ title +"\n"
                     + year + " " + month + " " + day + " " + hour + " " + hour_range + " " + str(level) + "\n"
                     + "{:.6f}".format(grid.dlon) + " " + "{:.6f}".format(grid.dlat) + " " + "{:.6f}".format(grid.slon) + " " + "{:.6f}".format(grid.elon) + " "
                     + "{:.6f}".format(grid.slat) + " " + "{:.6f}".format(grid.elat) + " " + str(grid.nlon) + " " + str(grid.nlat) + " "
                     + str(inte) + " " + str(vmin) + " " + str(vmax) + " 1 0")

        # 二维数组写入micaps文件
        format_str = "%." + str(effectiveNum) + "f "

        np.savetxt(save_path, grid_values, delimiter=' ',
                   fmt=format_str, header=title, comments='',encoding='GBK')
        if show:
            print('成功输出至'+ save_path)
        return True
    except:
        exstr = traceback.format_exc()
        print(exstr)
        return False
    
    
def write_griddata_to_nc(da,save_path = "a.txt",creat_dir = False,effectiveNum = 3,show = False):
    try:
        dir = os.path.split(os.path.abspath(save_path))[0]
        if not os.path.isdir(dir):
            if not creat_dir:
                print("文件夹："+dir+"不存在")
                return False
            else:
                meteva.base.tool.path_tools.creat_path(save_path)
        scale_factor = math.pow(10,-effectiveNum)
        #print(scale_factor)
        encodingdict = {da.name:{
                            'dtype': 'int32',
                            'scale_factor': scale_factor,
                             'zlib': True,
                            '_FillValue':None
                            }
                        }

        da.to_netcdf(save_path,encoding = encodingdict)
        if show:
            print('成功输出至' + save_path)
        return True
    except:
        exstr = traceback.format_exc()
        print(exstr)
        return False
def write_griddata_to_micaps11(wind,save_path = "a.txt",creat_dir = False,effectiveNum = 3,show = False,title = None):
    try:
        dir = os.path.split(os.path.abspath(save_path))[0]
        if not os.path.isdir(dir):
            if not creat_dir:
                print("文件夹："+dir+"不存在")
                return False
            else:
                meteva.base.tool.path_tools.creat_path(save_path)
        grid0 = meteva.base.basicdata.get_grid_of_data(wind)
        nlon = grid0.nlon
        nlat = grid0.nlat
        slon = grid0.slon
        slat = grid0.slat
        elon = grid0.elon
        elat = grid0.elat
        dlon = grid0.dlon
        dlat = grid0.dlat
        level = grid0.levels[0]
        stime = grid0.stime_str
        year = stime[0:4]
        month = stime[4:6]
        day = stime[6:8]
        hour = stime[8:10]
        values = wind.values
        grid_values = np.squeeze(values).reshape(2*nlat,nlon)

        end = len(save_path)
        start = max(0, end - 16)

        if title is None:
            title = ("diamond 11 " + save_path[start:end] + "\n"
                     + year + " " + month + " " + day + " " + hour + " " + str(level) + "\n"
                     + str(grid0.dlon) + " " + str(grid0.dlat) + " " + str(grid0.slon) + " " + str(grid0.elon) + " "
                     + str(grid0.slat) + " " + str(grid0.elat) + " " + str(grid0.nlon) + " " + str(grid0.nlat))
        else:

            title  = ("diamond 11 " + title+ "\n"
                    +year + " "+ month + " " + day+ " " +hour +" " + str(level)+"\n"
                    + str(grid0.dlon) + " " + str(grid0.dlat) + " " + str(grid0.slon) + " " + str(grid0.elon) + " "
                    + str(grid0.slat) + " " + str(grid0.elat) + " " + str(grid0.nlon) + " " + str(grid0.nlat))

        format_str = "%." + str(effectiveNum) + "f "

        np.savetxt(save_path, grid_values, delimiter=' ',
                   fmt=format_str, header=title, comments='')
        if show:
            print('成功输出至' + save_path)
        return True
    except:
        exstr = traceback.format_exc()
        print(exstr)
        return False

def tran_griddata_to_gds_flow(da):
    grid0 = meteva.base.get_grid_of_data(da)
    discriminator = b"mdfs"
    if len(grid0.members)==1:
        data_type = 4
    elif len(grid0.members)==2:
        data_type =11
    else:
        print("仅支持micap4类和micaps11类数据输出成GDS格式")
    data_type_byte = np.ndarray.tobytes(np.array([data_type]).astype(np.int16))
    mName = grid0.members[0]
    mName = mName.encode(encoding='utf-8')
    if len(mName)<20:
        mName = mName + np.ndarray.tobytes(np.zeros(20-len(mName)).astype(np.int8))

    eleName = b""
    if "eleName" in da.attrs.keys():
        eleName = da.attrs["eleName"]
    if len(eleName) < 50:
        eleName = eleName + np.ndarray.tobytes(np.zeros(50 - len(eleName)).astype(np.int8))

    description =b""
    if "description" in da.attrs.keys():
        description = da.attrs["description"]
    if len(description) < 30:
        description = description + np.ndarray.tobytes(np.zeros(30 - len(description)).astype(np.int8))


    level = np.ndarray.tobytes(np.array(grid0.levels[0]).astype(np.float32))
    y_m_d_h_timezone_peroid = np.ndarray.tobytes(np.array([2021,1,1,8,8,0]).astype(np.int32))
    slon_elon_dlon = np.ndarray.tobytes(np.array([grid0.slon,grid0.elon,grid0.dlon]).astype(np.float32))
    nlon = np.ndarray.tobytes(np.array([grid0.nlon]).astype(np.int32))
    slat_elat_dlat = np.ndarray.tobytes(np.array([grid0.slat, grid0.elat, grid0.dlat]).astype(np.float32))
    nlat  =  np.ndarray.tobytes(np.array([grid0.nlat]).astype(np.int32))
    vmin,vmax,inte = meteva.base.tool.plot_tools.get_isoline_set(da)
    sValue_eValue_dValue = np.ndarray.tobytes(np.array([vmin,vmax,inte]).astype(np.float32))
    blank = np.ndarray.tobytes(np.zeros(100).astype(np.int8))
    value_bytes = np.ndarray.tobytes(da.values.astype(np.float32))
    bytes1 = discriminator+data_type_byte+mName+eleName+description+level+y_m_d_h_timezone_peroid
    bytes2 = slon_elon_dlon+nlon+slat_elat_dlat+nlat+sValue_eValue_dValue+blank+value_bytes
    bytes = bytes1+bytes2

    return bytes

def write_griddata_to_gds_file(da,save_path = "a.txt",creat_dir = False,show = False):
    try:
        dir = os.path.split(os.path.abspath(save_path))[0]
        if not os.path.isdir(dir):
            if not creat_dir:
                print("文件夹："+dir+"不存在")
                return False
            else:
                meteva.base.tool.path_tools.creat_path(save_path)

        bytes = tran_griddata_to_gds_flow(da)
        br = open(save_path, 'wb')
        br.write(bytes)
        br.close()
        if show:
            print('成功输出至' + save_path)
        return True
    except:
        exstr = traceback.format_exc()
        print(exstr)
        return False

if __name__ == "__main__":
    grd = meteva.base.read_griddata_from_micaps4(r"H:\test_data\input\meb\m4.txt")
    write_griddata_to_gds_file(grd,save_path=r"H:\test_data\output\meb\gds_test.000")
