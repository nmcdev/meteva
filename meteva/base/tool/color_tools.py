import numpy as np
import matplotlib.image as image
from matplotlib import cm
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import matplotlib.colors as colors
import pkg_resources
import math
import os
import colorsys
import meteva

def clev_cmap_temper_2m_k():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_temp_2m.txt")
    cmap,clevs =  get_cmap_and_clevs_from_file(path)
    clevs += 273.15
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs,cmap

def clev_cmap_temper_2m():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_temp_2m.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap

def clev_cmap_rain_1h():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_1h.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap
def clev_cmap_rain_3h():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_3h.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap
def clev_cmap_rain_24h():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_24h.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap
def clev_cmap_rh():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rh.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap
def clev_cmap_vis():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_vis.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap
def clev_cmap_wind_speed():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_wind_speed.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap
def clev_cmap_cloud_total():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_tcdc.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap

def clev_cmap_rain_1h_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_1h_error.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap
def clev_cmap_rain_3h_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_3h_error.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap
def clev_cmap_rh_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rh_error.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap
def clev_cmap_vis_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_vis_error.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap
def clev_cmap_wind_speed_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_wind_speed_error.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap
def clev_cmap_cloud_total_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_tcdc_error.txt")
    cmap, clevs = get_cmap_and_clevs_from_file(path)
    print("不再推荐使用该函数，推荐使用meb.def_cmap_clevs相应功能,请参考color工具中相关说明")
    return clevs, cmap


def cmap_clevs_temper_2m_error():
    clevs1 = [-20,-12,-8,-6,-4,-2,-1]
    nclev = len(clevs1)
    colors0 = cm.get_cmap("winter", nclev)
    colors_list = []
    for i in range(nclev):
        colors_list.append(colors0(i))

    clevs2 = [0,1,2,4,6,8,12,20]
    nclev = len(clevs2)
    colors0 = cm.get_cmap("autumn", nclev)
    for i in range(nclev):
        colors_list.append(colors0(nclev - 1 - i))
    clevs1.extend(clevs2)
    cmap = colors.ListedColormap(colors_list, 'indexed')
    return cmap, clevs1


def cmap_clevs_environment():
    clevs1 =[0,35,75,115,150,250,350]
    nclev = len(clevs1)
    colors_list = np.array([[0,228,0],[255,255,0],[255,126,0],[255,0,0],[153,0,76],[126,0,35]])/256
    cmap = colors.ListedColormap(colors_list, 'indexed')
    return cmap, clevs1

def get_cmap_and_clevs_from_file(path):
    clev_cmap = np.loadtxt(path)
    clevs = clev_cmap[:, 0]
    cmap = clev_cmap[:, 1:] / 255
    cmap = cmap.tolist()
    cmap = colors.ListedColormap(cmap, 'indexed')
    return cmap,clevs

def cmap_clevs_bias_(vmax):
    if vmax is None:
        print("设置bias的cmap时需要指定vmax")
    blue = np.array([0, 0, 255]) / 255
    white = np.array([255, 255, 255]) / 255
    red = np.array([255, 0, 0]) / 255
    black = np.array([0, 0, 0]) / 255
    clev_list = [0]
    cmap_list = [blue]
    for v in range(1,6):
        clev_list.append(v * 0.2)
        cmap_list.append(blue * (1 - v * 0.2) + white * v * 0.2)
    for v in range(1,6):
        clev_list.append(1 + v * 0.2)
        cmap_list.append(white * (1 - v * 0.2) + red * v * 0.2)

    for value in range(2, int(vmax + 1), 1):
        clev_list.append(value)
        cmap_list.append((red * (vmax - value) + black * (value - 2)) / (vmax - 2))
    cmap = colors.ListedColormap(cmap_list, 'indexed')
    return cmap,clev_list


def cmap_clevs_bias(vmax):
    if vmax is None:
        print("设置bias的cmap时需要指定vmax")
    blue = np.array([0, 0, 255]) / 255
    white = np.array([255, 255, 255]) / 255
    yellow = np.array([0.7,0.7,0])
    red = np.array([255, 0, 0]) / 255
    pink = np.array([0.5,0,0.5])
    black = np.array([0, 0, 0]) / 255
    clev_list = [0]
    cmap_list = [blue]
    for v in range(1,6):
        clev_list.append(v * 0.2)
        cmap_list.append(blue * (1 - v * 0.2) + white * v * 0.2)

    for v in range(1,6):
        clev_list.append(1 + v * 0.2)
        cmap_list.append(white * (1 - v * 0.2) + yellow * v * 0.2)

    for v in range(1,6):
        clev_list.append(2 + v * 0.2)
        cmap_list.append(yellow * (1 - v * 0.2) + red * v * 0.2)

    for v in range(1,11):
        clev_list.append(3 + v * 0.5)
        cmap_list.append(red * (1 - v * 0.1) + pink * v * 0.1)

    for value in range(8, int(vmax + 1), 1):
        clev_list.append(value)
        cmap_list.append((pink * (vmax - value) + black * (value - 2)) / (vmax - 2))
    cmap = colors.ListedColormap(cmap_list, 'indexed')
    return cmap,clev_list


def cmap_clevs_temper_error_br(vmax):
    blue = np.array([0, 0, 255]) / 255
    white = np.array([255, 255, 255]) / 255
    red = np.array([255, 0, 0]) / 255
    black = np.array([0, 0, 0]) / 255
    clev_list = []
    cmap_list = []

    vmax = int(math.ceil(vmax))

    if vmax > 5:
        for value in range(-vmax, -5):
            clev_list.append(value)
            cmap_list.append((blue * (value + vmax) + black * (-5 - value)) / (vmax -5))

    for v in range(-5,0):
        clev_list.append(v)
        cmap_list.append((blue * (-v) + white * (5+v))/5)
    for v in range(0,6):
        clev_list.append(v)
        cmap_list.append((white * (5 - v) + red*v)/5)

    if vmax>5:
        for value in range(6, vmax):
            clev_list.append(value)
            cmap_list.append((red * (vmax - value) + black * (value-5)) / (vmax - 5))

    cmap = colors.ListedColormap(cmap_list, 'indexed')
    return cmap,clev_list


def cmap_clevs_me(vmin,vmax):
    max_abs = max(abs(vmax),abs(vmin))
    vmax = max_abs
    vmin = -max_abs
    dif = (vmax - vmin) / 10.0
    inte = math.pow(10, math.floor(math.log10(dif)));
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

    inte = inte/2

    vmin = inte * ((int)(vmin / inte) - 1)

    vmax = inte * ((int)(vmax / inte) + 2)
    clevs1 = np.arange(vmin, -1e-6, inte)
    nclev = len(clevs1)
    colors0 = cm.get_cmap("winter", nclev)
    colors_list = []
    for i in range(nclev):
        colors_list.append(colors0(i))

    clevs2 = np.arange(0, vmax, inte)
    nclev = len(clevs2)
    colors0 = cm.get_cmap("autumn", nclev)
    for i in range(nclev):
        colors_list.append(colors0(nclev -1 - i))
    clevs = np.arange(vmin, vmax, inte)
    cmap = colors.ListedColormap(colors_list, 'indexed')
    return cmap,clevs


def cmap_clevs_me_w0(vmin,vmax):
    max_abs = max(abs(vmax),abs(vmin))
    vmax = max_abs
    vmin = -max_abs
    dif = (vmax - vmin) / 10.0
    inte = math.pow(10, math.floor(math.log10(dif)));
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

    inte = inte/2

    vmin = inte * int(math.floor((vmin / inte)))

    vmax = inte * ((int)(vmax / inte) + 1)

    clevs = np.arange(vmin, vmax, inte)
    num = len(clevs)
    rgb_colors = []
    sp = 3/4
    step = 360*sp / num
    #print(num)
    delta0 = int((num-1)/2)
    left = delta0 % 4
    for i in range(num):
        delta = abs(i-((num-1)/2))
        if i < (num-1)/2:
            h = 0.25 +(1-sp)/2 + delta * step / 360  # 首先均匀的取不同的色相，保持色相维度的差异最大化
            if delta <=(left + 4):
                if delta <=1:delta = 0
                s = 0.75 + 0.25 * delta / (left + 4)  # 通过一个折线波浪 设置不同的饱和度
                l = 0.9 - 0.6 * np.power(delta / (left + 4),1)  # 通过一个折线波浪 设置不同的亮度
            else:
                i1 = i % 4
                s = 0.75 + 0.25 * (i1 / 4)  # 通过一个折线波浪 设置不同的饱和度
                l = 0.3 + 0.6 * np.power((i1 / 4),1)  # 通过一个折线波浪 设置不同的亮度

        else:
            h = 0.25 - (1 - sp) / 2 - delta * step / 360  # 首先均匀的取不同的色相，保持色相维度的差异最大化
            if delta < (left + 4):
                s = 0.75 + 0.25 * delta / (left + 4)  # 通过一个折线波浪 设置不同的饱和度
                l = 0.9 - 0.6 * np.power(delta / (left + 4),1)  # 通过一个折线波浪 设置不同的亮度
            else:
                i1 = 4 - (num-1 - i) % 4
                s = 1 - 0.25 * i1 / 4  # 通过一个折线波浪 设置不同的饱和度
                l = 0.75 - 0.35 * np.power(i1 / 4,1)  # 通过一个折线波浪 设置不同的亮度



        rgb1 = colorsys.hls_to_rgb(h, l, s)
        rgb_colors.append(rgb1)

    clevs = np.arange(vmin, vmax, inte)
    cmap = colors.ListedColormap(rgb_colors, 'indexed')
    return cmap,clevs

def cmap_clevs_me_new(vmin,vmax):
    max_abs = max(abs(vmax),abs(vmin))
    vmax = max_abs
    vmin = -max_abs
    dif = (vmax - vmin) / 10.0
    inte = math.pow(10, math.floor(math.log10(dif)));
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

    inte = inte/2

    vmin = inte * ((int)(vmin / inte) - 1)

    vmax = inte * ((int)(vmax / inte) + 2)
    clevs1 = np.arange(vmin, -1e-6, inte)
    nclev = len(clevs1)
    colors0 = cm.get_cmap("winter", nclev)
    colors_list = []
    for i in range(nclev):
        if i == nclev - 1:
            c1 = np.array(list(colors0(i)))/5 +4/5
            colors_list.append(c1)
        else:
            colors_list.append(colors0(i))

    clevs2 = np.arange(0, vmax, inte)
    nclev = len(clevs2)
    colors0 = cm.get_cmap("autumn", nclev)
    for i in range(nclev):
        if i ==0:
            c1 = np.array(list(colors0(nclev -1 - i)))/5 +4/5
            colors_list.append(c1)
        else:
            colors_list.append(colors0(nclev -1 - i))

    clevs = np.arange(vmin, vmax, inte)
    cmap = colors.ListedColormap(colors_list, 'indexed')
    return cmap,clevs


def cmap_clevs_mae(vmax):

    dif = (vmax) / 10.0
    inte = math.pow(10, math.floor(math.log10(dif)));
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

    inte = inte / 2

    vmin = 0

    vmax = inte * ((int)(vmax / inte) + 1)

    clevs = np.arange(vmin, vmax, inte)
    num = len(clevs)
    rgb_colors = []

    for i in range(num):
        h = 0.8 - i/num
        s = 1
        l = 1 - 0.6 * (i+1)/num
        rgb1 = colorsys.hls_to_rgb(h, l, s)
        rgb_colors.append(rgb1)

    clevs = np.arange(vmin, vmax, inte)
    cmap = colors.ListedColormap(rgb_colors, 'indexed')
    return cmap, clevs


def cmap_clevs_me_bwr(vmin,vmax):

    # max_abs = math.ceil(max(abs(vmax),abs(vmin)))
    # inte = 1
    # vmin = inte * ((int)(vmin / inte))
    #
    max_abs = max(abs(vmax),abs(vmin))
    vmax = max_abs
    vmin = -max_abs
    dif = (vmax - vmin) / 10.0
    inte = math.pow(10, math.floor(math.log10(dif)));
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

    inte = inte/2

    vmin = inte * ((int)(vmin / inte) - 1)
    vmax = inte * ((int)(vmax / inte) + 2)
    max_abs_h = math.ceil(max(abs(vmax),abs(vmin)))/2
    clevs = []
    colors_list = []

    for i in np.arange(vmin,0,inte).tolist():
        clevs.append(i)
        if i <= -max_abs_h:
            rgb = [0,0,(i - vmin)/max_abs_h]
        else:
            rgb = [1+ i/max_abs_h,1+ i/max_abs_h,1]
        #print(rgb)
        if i>=-inte:
            rgb= [1,1,1]
        colors_list.append(rgb)

    for i in np.arange(0,vmax,inte).tolist():
        clevs.append(i)
        if i <= max_abs_h:
            rgb = [1,1- i/max_abs,1- i/max_abs]
        else:
            rgb = [(vmax - i)/max_abs_h,0,0]
        if i < inte:
            rgb = [1,1,1]
        colors_list.append(rgb)
    #print(colors_list)
    cmap = colors.ListedColormap(colors_list, 'indexed')
    return cmap,clevs


def cmap_clevs_mode(vmax):
    '''
    定义mode目标绘制的colorbar
    :param vmax:  最大的目标编号
    :return:
    '''
    if vmax <12:
        cmap1,clevs1 = def_cmap_clevs(cmap="Paired",clevs=np.arange(1,vmax+1))
    elif vmax <20:
        cmap1, clevs1 = def_cmap_clevs(cmap="tab20b", clevs=np.arange(1, vmax+1))
    else:
        cmap1, clevs1 = def_cmap_clevs(cmap="gist_rainbow", clevs=np.arange(1, vmax+1))

    #cmap2 = colors.ListedColormap([[80,80,80],[125,125,125],[255,255,255]], 'indexed')
    #clevs2 = [-2,-1,0]
    cmap2,clevs2 = def_cmap_clevs(cmap = "gray",clevs = [-2,-1,0],vmin =-1,vmax = 0,cut_colorbar=True)
    cmap2,clevs2 = get_part_cmap_and_clevs(cmap2,clevs2,vmin= -0.5,vmax = 0,cut_accurate=True)
    cmap3,clevs3 = merge_cmap_clevs(cmap2,clevs2,cmap1,clevs1)
    clevs3 = (np.array(clevs3) -0.5).tolist()

    #show_cmap_clev(cmap3,clevs3)
    return cmap3,clevs3

def cmap_clevs_ts():
    clevs = np.arange(0,1.01,0.1)
    nclev = len(clevs)
    colors0 = cm.get_cmap("jet", nclev)
    colors_list = []
    for i in range(nclev):
        clev = clevs[i]
        cl = []
        cl[0:3] = colors0(i)[0:3]
        cl.append(clev)
        colors_list.append(tuple(cl))
        #print(colors0(i))
    cmap = colors.ListedColormap(colors_list, 'indexed')
    return cmap,clevs

def hour():
    #import matplotlib.colors as colors
    cmap = np.array([[0,0,255],
                     [0,115,255],
                     [16,190,56],
                     [255,255,0],
                     [254,147,5],
                     [255,18,0],
                     [177,0,62],
                     [117,0,121],
                     [0,0,255],])/255
    cmap = cmap.tolist()
    cmap = colors.ListedColormap(cmap, 'indexed')
    clevs = np.arange(0,24,3).tolist()
    return  cmap ,clevs


def cmap_clevs_radar():
    clevs = np.arange(5,75,5).tolist()
    clevs1 = [-5,0]
    clevs1.extend(clevs)
    colors_list = np.array([
        [255, 255, 255],
        [0,0,246],
        [1,160,246],
        [78,242,242],
        [1,255,0],
        [0,200,0],
        [1,144,0],
        [255,255,0],
        [231,192,0],
        [255,144,0],
        [255,0,0],
        [214,0,0],
        [192,0,0],
        [255,0,240],
        [120,0,132],
        [173,144,240]
    ])/256
    cmap = colors.ListedColormap(colors_list, 'indexed')
    return cmap,clevs1

def cmap_clevs_far():
    clevs = np.arange(0,1.01,0.1)
    nclev = len(clevs)
    colors0 = cm.get_cmap("jet", nclev)
    colors_list = []
    for i in range(nclev):
        colors_list.append(colors0(i))
    cmap = colors.ListedColormap(colors_list, 'indexed')
    return cmap,clevs

def cmap_clevs_mr():
    clevs = np.arange(0,1.01,0.1)
    nclev = len(clevs)
    colors0 = cm.get_cmap("jet", nclev)
    colors_list = []
    for i in range(nclev):
        colors_list.append(colors0(i))
    cmap = colors.ListedColormap(colors_list, 'indexed')
    return cmap,clevs


def cmap_clevs_error(vmin,vmax):

    max_abs = max(abs(vmax),abs(vmin))
    vmax = max_abs
    vmin = -max_abs
    dif = (vmax - vmin) / 10.0
    inte = math.pow(10, math.floor(math.log10(dif)));
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
    vmax = inte * ((int)(vmax / inte) + 2)
    clevs = np.arange(vmin, vmax, inte)
    nclev = len(clevs)
    colors0 = cm.get_cmap("bwr", nclev)
    colors_list = []
    for i in range(nclev):
        colors_list.append(colors0(i))
    cmap = colors.ListedColormap(colors_list, 'indexed')
    return cmap,clevs


def get_steps_range(line):
    num = len(line)
    max_nstep = 0

    #首先获得line中各段的起始坐标和长度
    start_list = [0]
    lenght_list = []
    n = 0
    for k in range(1,num):
        n += 1
        if line[k] != line[k-1]:
            lenght_list.append(n)
            start_list.append(k)
            n = 0
    lenght_list.append(n)

    #统计长度序列中保持不变的部分
    start_list_length = [0]
    lenght_list_lenght = []
    n = 0
    for k in range(1,len(lenght_list)):
        n += 1
        if abs(lenght_list[k] - lenght_list[k-1]) > 1:
            lenght_list_lenght.append(n)
            start_list_length.append(k)
            n = 0
    lenght_list_lenght.append(n)

    #计算总共有多少个color等级
    step_num  =  np.max(np.array(lenght_list_lenght))
    #计算等长序列最大个数在lenght_list_lenght对应的起始位置
    k = np.argmax(np.array(lenght_list_lenght))

    # 计算lenght_list_lenght起始坐标在lenght_list中的位置
    j = start_list_length[k]

    # lenght_list中的位置在整个line中的位置
    i_start_list = []
    for i in range(step_num + 1):
        i_start_list.append(start_list[j + i])

    return step_num,i_start_list

def get_cmap_from_picture(path,show = False):

    #im的第一维是y方向，第二维是x方向，第三维是rgb
    im = image.imread(path)
    #首先沿着x方向寻找
    rgb_to_1d = np.zeros((im.shape[0],im.shape[1]))
    rgb_to_1d = im[:,:,0] * 256* 256 + im[:,:,1] * 256 + im[:,:,2]


    color_type_num_y = np.zeros(im.shape[0])
    for y in range(im.shape[0]):
        line = rgb_to_1d[y,:] #line 是一条沿着x方向的线
        rgb_list = line.tolist()
        color_set  = set(rgb_list)
        color_type_num_y[y] = len(color_set)

    color_type_num_x = np.zeros(im.shape[1])
    for x in range(im.shape[1]):
        line = rgb_to_1d[:,x] #line_x 是一条沿着y方向的线
        rgb_list = line.tolist()
        color_set  = set(rgb_list)
        color_type_num_x[x] = len(color_set)


    max_color_type_y = np.max(color_type_num_y)
    max_color_type_x = np.max(color_type_num_x)
    max_color_type = max(max_color_type_x,max_color_type_y)


    max_step_num = 0
    i_start = 0
    i_end = 0
    j_start  = 0
    j_end = 0
    color_list = []

    ij_list = np.where(color_type_num_x == max_color_type)[0]
    if(len(ij_list) > 0):
        k_list_list = []
        k_list = [0]
        for k in range(1,len(ij_list)):
            if ij_list[k] - ij_list[k-1] == 1:
                k_list.append(k)
            else:
                k_list_list.append(k_list)
                k_list = [k]
        k_list_list.append(k_list)

        for k in range(len(k_list_list)):
            k_list =k_list_list[k]
            mid = int((ij_list[0] + ij_list[-1])/2)
            line = rgb_to_1d[:,mid]
            step_num,start_list = get_steps_range(line)
            if step_num > max_step_num:
                max_step_num = step_num
                i_start = ij_list[0]
                i_end = ij_list[-1]
                j_start = start_list[0]
                j_end = start_list[-1]
                color_list = []
                for i in range(step_num):
                    start = start_list[-i-2]
                    color_list.append(im[start,mid,:])


    #
    ij_list = np.where(color_type_num_y == max_color_type)[0]
    if len(ij_list) >0:
        k_list_list = []
        k_list = [0]
        for k in range(1,len(ij_list)):
            if ij_list[k] - ij_list[k-1] == 1:
                k_list.append(k)
            else:
                k_list_list.append(k_list)
                k_list = [k]
        k_list_list.append(k_list)

        for k in range(len(k_list_list)):
            k_list =k_list_list[k]
            mid = int((ij_list[0] + ij_list[-1])/2)
            line = rgb_to_1d[mid,:]
            step_num,start_list = get_steps_range(line)
            if step_num > max_step_num:
                max_step_num = step_num
                j_start = ij_list[0]
                j_end = ij_list[-1]
                i_start = start_list[0]
                i_end = start_list[-1]
                color_list = []
                for i in range(step_num):
                    start = start_list[i]
                    color_list.append(im[mid,start,:])

    cmap = colors.ListedColormap(color_list, 'indexed')

    if show:
        show_cmap_clev(cmap)

    return cmap


def get_cmap_and_clevs_by_element_name(element_name):
    path = None
    if element_name == "temp":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_temp_2m.txt")
    elif element_name == "rain_1h":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_1h.txt")
    elif element_name == "rain_1h_error":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_1h_error.txt")
    elif element_name == "rain_3h":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_3h.txt")
    elif element_name == "rain_3h_error":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_3h_error.txt")
    elif element_name == "rh":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rh.txt")
    elif element_name == "rh_error":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rh_error.txt")
    elif element_name == "vis":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_vis.txt")
    elif element_name == "vis_error":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_vis_error.txt")
    elif element_name == "wind_speed":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_wind_speed.txt")
    elif element_name == "wind_speed_error":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_wind_speed_error.txt")
    elif element_name == "tcdc":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_tcdc.txt")
    elif element_name == "tcdc_error":
        path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_tcdc_error.txt")
    cmap,clevs = get_cmap_and_clevs_from_file(path)
    return cmap,clevs

def get_part_cmap_and_clevs(cmap_all,clev_all,vmax,vmin,cut_accurate = False):


    if cut_accurate:
        start_i = 0
        for i in range(len(clev_all) - 1):
            if vmin < clev_all[i + 1]:
                start_i = i
                break
        end_i = 0
        for i in range(len(clev_all) - 1):
            if vmax > clev_all[i]:
                end_i = i+2

    else:
        if len(clev_all) < 20:
            return cmap_all, clev_all
        start_i = 0
        for i in range(len(clev_all)-1):
            if vmin<clev_all[i+1]:
                start_i = i
                break
        end_i = 0
        for i in range(len(clev_all)-1):
            if vmax > clev_all[i]:
                end_i = i+2
        if end_i - start_i<=15:
            end_i = start_i+15


    clevs_part = clev_all[start_i:end_i]
    if hasattr(cmap_all,"colors"):
        cmap_colors = cmap_all.colors
        cmap_colors_part = cmap_colors[start_i:end_i]
        cmap_part = colors.ListedColormap(cmap_colors_part, 'indexed')
    else:
        cmap_part = cmap_all
    return cmap_part,clevs_part

def write_cmap_and_clevs(cmap,clevs,path):
    num = len(clevs)
    clev_cmap = np.zeros((num,4))
    clev_cmap[:,0] = clevs[:]
    cmap_data = np.array(cmap.colors)
    max_data = np.max(cmap_data)
    if max_data <=1:
        clev_cmap[:,1:] = cmap_data * 255
    else:
        clev_cmap[:, 1:] = cmap_data
    np.savetxt(path,clev_cmap,fmt = "%f")

def get_denser_cmap(cmap,multi_num):
    if hasattr(cmap,"colors"):
        colors0 = np.array(cmap.colors)
        colors_list = []
        num = len(colors0) - 1
        for i in range(num):
            for j in range(multi_num):
                color1 = (colors0[i,:]*(multi_num-j) + colors0[i+1,:] * j)/multi_num
                colors_list.append(color1.tolist())
        colors_list.append(colors0[-1])
        cmap_denser = colors.ListedColormap(colors_list, 'indexed')
        return cmap_denser
    else:
        return cmap

def show_cmap_clev(cmap,clev = None):
    """
    Show color map.
    :param cmap: color map instance.
    :return: None
    """
    n_colors = len(cmap.colors)
    width = 8
    heigh = 2
    n_h = int(heigh * n_colors/width)
    im = np.outer(np.ones(n_h), np.arange(n_colors))


    fig, ax = plt.subplots(1, figsize=(width, heigh),
                           subplot_kw=dict(xticks=[], yticks=[]))
    if clev is not None:
        max_tick = 10
        step = int(math.ceil(n_colors/max_tick))
        x = np.arange(0,n_colors,step).astype(np.int32)
        #print(x)
        ax.set_xticks(x)
        labels = []
        for i in range(x.size):
            labels.append(round(clev[x[i]],6))
        ax.set_xticklabels(labels)
    ax.imshow(im, cmap=cmap)


def get_color_list(legend_num):
    colors_list = []
    if legend_num<=10:
        colors = cm.get_cmap("tab10")
        for i in range(legend_num):
            colors_list.append(colors(i))
    elif legend_num <=20:
        colors = cm.get_cmap("tab20")
        for i in range(legend_num):
            colors_list.append(colors(i))
    else:
        colors = cm.get_cmap('gist_rainbow', 128)
        for i in range(legend_num):
            color_grade = i / legend_num
            colors_list.append(colors(color_grade))
    return colors_list


def get_cmap_and_clevs_by_name(cmap_name,vmin,vmax):
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_"+cmap_name+".txt")
    if os.path.exists(path):
        cmap,clevs = get_cmap_and_clevs_from_file(path)
    elif cmap_name == "bias":
        cmap,clevs = cmap_clevs_bias(vmax)
    elif cmap_name == "error":
        cmap,clevs = cmap_clevs_error(vmin,vmax)
    elif cmap_name == "me":
        cmap,clevs = cmap_clevs_me(vmin,vmax)
    elif cmap_name == "me_bwr":
        cmap,clevs = cmap_clevs_me_bwr(vmin,vmax)
    elif cmap_name == "me_w0":
        cmap,clevs = cmap_clevs_me_w0(vmin,vmax)
    elif cmap_name == "ts":
        cmap,clevs= cmap_clevs_ts()
    elif cmap_name == "far":
        cmap,clevs = cmap_clevs_far()
    elif cmap_name == "far":
        cmap,clevs = cmap_clevs_far()
    elif cmap_name == "mode":
        cmap, clevs = cmap_clevs_mode(vmax)
    elif cmap_name == "temper_2m_error":
        cmap, clevs = cmap_clevs_temper_2m_error()
    elif cmap_name == "temper_error_br":
        cmap, clevs = cmap_clevs_temper_error_br(vmax)
    elif cmap_name =="environment":
        cmap,clevs = cmap_clevs_environment()
    elif cmap_name =="radar":
        cmap,clevs = cmap_clevs_radar()
    elif cmap_name =="mae":
        cmap, clevs = cmap_clevs_mae(vmax)
    elif cmap_name =="hour":
        cmap,clevs = hour()
    else:
        print("该配色方案名称不识别")
        return None,None
    return cmap,clevs


class cmaps:
    rain_1h = "rain_1h"
    rain_1h_error = "rain_1h_error"
    rain_3h = "rain_3h"
    rain_3h_error = "rain_3h_error"
    rain_24h = "rain_24h"
    rain_24h_error = "rain_24h_error"
    temp_2m = "temp_2m"
    temper_2m_error = "temper_2m_error"
    rh = "rh"
    rh_error = "rh_error"
    vis = "vis"
    vis_error = "vis_error"
    wind_speed = "wind_speed"
    wind_speed_error = "wind_speed_error"
    tcdc = "tcdc"
    tcdc_error  = "tcdc_error"
    bias = "bias"
    error = "error"
    ts = "ts"
    far = "far"
    mr = "mr"
    mode = "mode"
    me = "me"
    temper_error_br ="temper_error_br"
    environment = "environment"
    radar = "radar"
    me_bwr = "me_bwr"
    me_w0 = "me_w0"
    mae = "mae"
    hour = "hour"


def coordinate_cmap_to_clevs(cmap,clevs):
    if hasattr(cmap, "colors"):
        colors0 = np.array(cmap.colors)
        colors_list = []
        ncmap = len(colors0)
        nclev = len(clevs)
        if nclev <2:
            print("clevs' size must bigger than 1")
        for i in range(nclev):
            if nclev>1:
                j = i * (ncmap-1) /(nclev-1)
            else:
                j = 0
            j0 = int(j)
            j1 = min(j0 + 1,ncmap-1)
            dj = j - j0
            color1 = (colors0[j0, :] * (1 - dj) + colors0[j1, :] * dj)
            colors_list.append(color1.tolist())
        cmap_co = colors.ListedColormap(colors_list, 'indexed')
        return cmap_co,clevs
    else:
        print("cmap is not colormap")
        return



def def_cmap_clevs(cmap = "rainbow",clevs = None,vmin = None,vmax = None,cut_colorbar = True):
    #  # 判断是meteva自定义的颜色类型，这从meteva资源文件或函数里生成cmap1 和clevs1
    clevs1 = None
    cmap1 = None

    if isinstance(cmap,str):
        cmap_class = cmaps()
        if hasattr(cmap_class, cmap):
            if vmin is None:
                vmin = np.min(np.array(clevs))
            if vmax is None:
                vmax = np.max(np.array(clevs))
            if vmax is not None and vmin == vmax:vmin = vmax - 1
            cmap,clevs1= get_cmap_and_clevs_by_name(cmap, vmin, vmax)
    if isinstance(cmap,list):
        if isinstance(cmap[0],list):
            cmap_list = cmap
        else:
            cmap_list = []
            for c1 in cmap:
                r1 = int(c1[1:3].upper(), 16)/256
                g1 = int(c1[3:5].upper(), 16)/256
                b1 = int(c1[5:7].upper(), 16)/256
                cmap_list.append([r1,g1,b1])
        cmap = colors.ListedColormap(cmap_list, 'indexed')


    #设置clevs2
    if clevs is None:
        if clevs1 is None:
            # 如果cmap字符不是meteva内集成的，则判断它是matplotlib集成的，则进一步根据最大最小值生成cmap，clevs
            if vmin is None or vmax is None:
                print("clev and vmin/vmax cann't be None at the same time while cmap is matplotlib strType cmap")
                return
            if vmax - vmin < 1e-10:
                vmax = vmin + 1.1
            dif = (vmax - vmin) / 10.0
            inte = math.pow(10, math.floor(math.log10(dif)));
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


            vmin = inte * (math.floor(vmin / inte))
            vmax = inte * (math.ceil(vmax / inte)+0.5)
            clevs2 = np.arange(vmin, vmax, inte)
        else:
            clevs2 = clevs1
    else:
        clevs2 = clevs

    # 设置cmap2
    if cmap1 is None:
        if isinstance(cmap,str):
            nclev = len(clevs2)
            colors0 = cm.get_cmap(cmap, nclev)
            colors_list = []
            for i in range(nclev):
                colors_list.append(colors0(i))
            cmap2 = colors.ListedColormap(colors_list, 'indexed')
        else:
            cmap2 = cmap
    else:
        cmap2 = cmap1


    #将cmap2 和clev2 协调
    cmap3,clevs3 = coordinate_cmap_to_clevs(cmap2,clevs2)

    # 从cmap3 和cmap3中提取部分colorbar

    if vmin is not None and vmax is not None and cut_colorbar:
        cmap4,clevs4 = get_part_cmap_and_clevs(cmap3, clevs3, vmax, vmin)
    else:
        cmap4,clevs4  = cmap3,clevs3

    return cmap4,clevs4


def merge_cmap_clevs(cmap0,clevs0,cmap1,clevs2):
    '''
    合并两个colorbar
    :param cmap0:
    :param clevs0:
    :param cmap1:
    :param clevs2:
    :return:
    '''
    colors0 = np.array(cmap0.colors).tolist()
    colors1 = np.array(cmap1.colors).tolist()
    colors0.extend(colors1)
    cmap_m = colors.ListedColormap(colors0, 'indexed')
    clevs0.extend(clevs2)
    return cmap_m,clevs0


def cart2sph(x, y, z):
    XsqPlusYsq = x ** 2 + y ** 2
    r = math.sqrt(XsqPlusYsq + z ** 2)  # r
    lat = math.atan2(z, math.sqrt(XsqPlusYsq))  # theta
    lon = math.atan2(y, x)  # phi
    return r, lat, lon


def get_seprated_rgb_method1(num):
    '''
    通过再hsl球体空间种，寻找距离最远的num个点来，获得对比度最大的num个颜色
    :param num:  需要返回的颜色数目
    :return:  rgb列表
    '''
    loc0 = np.zeros((3, num + 1))
    loc0[:, 0] = [0, 0, 1]  # 固定第一个点是白色
    loc0[:, 1] = [0, 1, 0]  # 固定第二个点是红色
    loc0[0, 2:] = np.arange(1, num) / num  #初始化其他点的位置

    # 将每个颜色看作hsl空间种的一个同号带电粒子，根据每个受力调整其位置，逐步迭代方法，使它们距离更远。
    for i in range(20000):
        # 计算受力
        force = np.zeros((3, num))
        for j in range(1, num):
            other = np.zeros((3, num))
            other[:, 0:j + 1] = loc0[:, 0:j + 1]
            other[:, j + 1:] = loc0[:, j + 2:]
            this = loc0[:, j + 1]
            dxyz = this.T - other.T

            dis2 = np.sum(np.power(dxyz, 2), axis=1)
            force_j_m = dxyz.T / dis2.T
            force_j = np.sum(force_j_m, axis=1)
            force[:, j] = force_j[:]
        # 根据受力方向调整每个
        force_s = np.sqrt(np.sum(np.power(force, 2), axis=0))
        mean_f = np.mean(force_s)
        for j in range(1, num):
            if force_s[j] > mean_f:
                move = 0.009 * force[:, j] / force_s[j]
                loc_new = loc0[:, j + 1] + move
                dis0 = np.sqrt(np.sum(np.power(loc_new, 2)))
                if dis0 > 1:
                    loc_new /= dis0
                loc0[:, j + 1] = loc_new
    # 直角坐标转换成球坐标，再转换成hsl色彩模式
    loc0 = loc0.T.tolist()
    loc0.pop(0)
    loc1 = []
    for j in range(num):
        r, lat, lon = cart2sph(loc0[j][0], loc0[j][1], loc0[j][2])
        s = r
        h = lon / (2 * math.pi)
        l = 0.5 + lat / math.pi
        loc1.append([h, l, s])
    loc1 = np.array(loc1)
    loc1[:, 0] -= loc1[0, 0]
    loc2 = loc1[loc1[:, 0].argsort(), :]  # 按照色相排序
    loc3 = np.zeros(loc2.shape)
    index = np.where(loc2[:, 0] < 0)
    nm = len(index[0])
    loc3[num - nm:, :] = loc2[0:nm, :]
    loc3[:num - nm, :] = loc2[nm:, :]  # 将红色调整到第一个

    # 转换成rgb
    rgb_colors = []
    for j in range(num):
        rgb1 = colorsys.hls_to_rgb(loc3[j, 0], loc3[j, 1], loc3[j, 2])
        rgb_colors.append(rgb1)
    return rgb_colors


def get_seprated_rgb_method2(num):
    '''
    设置较大区分度的一组颜色
    :param num:  需要返回的颜色数目
    :return:  rgb列表
    '''
    rgb_colors = []
    step = 360.0 / num
    for i in range(num):
        h = i * step / 360  # 首先均匀的取不同的色相，保持色相维度的差异最大化
        i1 = i % 6
        if i1 <= 2:
            di = 0.5 - i1
        else:
            di = 0.5 + i1 - 4
        s = 0.75 + 0.25 * di / 1.5  # 通过一个折线波浪 设置不同的饱和度
        l = 0.5 + 0.25 * di / 1.5    # 通过一个折线波浪 设置不同的亮度
        rgb1 = colorsys.hls_to_rgb(h, l, s)
        rgb_colors.append(rgb1)

    return rgb_colors


def set_plot_color_dict_method0(member_list):
    if len(member_list) >20:
        print("tab20颜色方案只能支持member_list长度小于等于20的情况")
        return

    cm0 = cm.get_cmap("tab20")
    color_list0 = []
    for i in range(20):
        color_list0.append(cm0(i))
    plot_color_dict = {}
    for i in range(len(member_list)):
        plot_color_dict[member_list[i]] = color_list0[i]
    meteva.base.plot_color_dict = plot_color_dict
    return

def set_plot_color_dict_method1(member_list):
    color_list0 = get_seprated_rgb_method1(len(member_list))
    plot_color_dict = {}
    for i in range(len(member_list)):
        plot_color_dict[member_list[i]] = color_list0[i]
    meteva.base.plot_color_dict = plot_color_dict
    return

def set_plot_color_dict_method2(member_list):
    color_list0 = get_seprated_rgb_method2(len(member_list))
    plot_color_dict = {}
    for i in range(len(member_list)):
        plot_color_dict[member_list[i]] = color_list0[i]
    meteva.base.plot_color_dict = plot_color_dict
    return
