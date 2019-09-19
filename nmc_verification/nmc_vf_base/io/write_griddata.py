
import numpy as np
import math
import nmc_verification
import os


def write_to_micaps4(da,filename = "a.txt",effectiveNum = 6):
    """
    输出micaps4格式文件
    :param da:xarray多维数据信息
    :param path:存储路径
    :param effectiveNum 有效数字 默认：6
    :return 最终按照需要保存的路径，将da数据保存为m4格式
    """
    grid = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(da)
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

    end = len(filename)
    start = max(0, end - 16)

    title = ("diamond 4 " + filename[start:end] + "\n"
             +year + " "+ month + " " + day+ " " +hour+ " " + hour_range +" " + str(level)+"\n"
            + str(grid.dlon) + " " + str(grid.dlat) + " " + str(grid.slon) + " " + str(grid.elon) + " "
            + str(grid.slat) + " " + str(grid.elat) + " " + str(grid.nlon) + " " + str(grid.nlat) + " "
            + str(inte) + " " + str(vmin) + " " + str(vmax) + " 1 0")


    # 第一行标题
    title0 = 'diamond 4 %s\n' % stime
    # 第二行标题
    title1 = '%s %s %s %s %s 999 %s %s %s %s %s %s %d %d 4 %s %s 2 0.00' \
             % (year, month, day, hour, hour_range,
                dlon, dlat,
                slon, elon, slat,
                elat, nlon, nlat, vmax, vmin)
    #title = title0 + title1
    # 二维数组写入micaps文件
    format_str = "%." + str(effectiveNum) + "f "

    np.savetxt(filename, grid_values, delimiter=' ',
               fmt=format_str, header=title, comments='')
    print('Create [%s] success' % filename)

def write_to_nc(da,filename = "a.txt",scale_factor = 0.01):

    encodingdict = {da.name:{
                        'dtype': 'int32',
                        'scale_factor': scale_factor,
                         'zlib': True,
                        '_FillValue':-9999
                        }
                    }
    da.to_netcdf(filename,encoding = encodingdict)


def write_to_micaps11(wind,filename = "a.txt",effectiveNum = 4):
    dir = os.path.split(os.path.abspath(filename))[0]
    if os.path.isdir(dir):
        grid0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(wind)
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

        end = len(filename)
        start = max(0, end - 16)
        title  = ("diamond 11 " + filename[start:end] + "\n"
                +year + " "+ month + " " + day+ " " +hour +" " + str(level)+"\n"
                + str(grid0.dlon) + " " + str(grid0.dlat) + " " + str(grid0.slon) + " " + str(grid0.elon) + " "
                + str(grid0.slat) + " " + str(grid0.elat) + " " + str(grid0.nlon) + " " + str(grid0.nlat))

        format_str = "%." + str(effectiveNum) + "f "

        np.savetxt(filename, grid_values, delimiter=' ',
                   fmt=format_str, header=title, comments='')
        print('Create [%s] success' % filename)
        return 0
    else:
        return 1