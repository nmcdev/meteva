
import numpy as np
import math
import meteva
import os
import traceback
import zlib
import warnings
warnings.filterwarnings("ignore")

def write_griddata_to_micaps4(da,save_path = "a.txt",creat_dir = False,effectiveNum = 6,show = False,title = None):
    """
    输出micaps4格式文件
    :param da:xarray多维数据信息
    :param path:存储路径
    :param effectiveNum 有效数字 默认：6
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
        vmax = math.ceil(max(grid_values.flatten()))
        vmin = math.ceil(min(grid_values.flatten()))

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
                     + "{:.6f}".format(grid.dlon) + " " + "{:.6f}".format(grid.dlat) + " " + str(grid.slon) + " " + str(grid.elon) + " "
                     + str(grid.slat) + " " + str(grid.elat) + " " + str(grid.nlon) + " " + str(grid.nlat) + " "
                     + str(inte) + " " + str(vmin) + " " + str(vmax) + " 1 0")
        else:

            title = ("diamond 4 "+ title +"\n"
            + year + " " + month + " " + day + " " + hour + " " + hour_range + " " + str(level) + "\n"
            + "{:.6f}".format(grid.dlon) + " " + "{:.6f}".format(grid.dlat) + " " + str(grid.slon) + " " + str(grid.elon) + " "
            + str(grid.slat) + " " + str(grid.elat) + " " + str(grid.nlon) + " " + str(grid.nlat) + " "
            + str(inte) + " " + str(vmin) + " " + str(vmax) + " 1 0")

        # 二维数组写入micaps文件
        format_str = "%." + str(effectiveNum) + "f "

        np.savetxt(save_path, grid_values, delimiter=' ',
                   fmt=format_str, header=title, comments='')
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

