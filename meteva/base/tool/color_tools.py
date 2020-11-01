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

def get_cmap_and_clevs_from_file(path):
    clev_cmap = np.loadtxt(path)
    clevs = clev_cmap[:, 0]
    cmap = clev_cmap[:, 1:] / 255
    cmap = cmap.tolist()
    cmap = colors.ListedColormap(cmap, 'indexed')
    return cmap,clevs

def cmap_clevs_bias(vmax):
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


def cmap_clevs_error(vmax,vmin):

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

    if show:
        color_bar = im[j_start:j_end,i_start:i_end,:]
        plt.imshow(color_bar)
        plt.xticks([])
        plt.yticks([])
        plt.show()
    cmap = colors.ListedColormap(color_list, 'indexed')
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

def get_part_cmap_and_clevs(cmap_all,clev_all,vmax,vmin):
    if len(clev_all) < 20:
        return cmap_all,clev_all
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
        cmap,clevs = cmap_clevs_error(vmax,vmin)
    elif cmap_name == "ts":
        cmap,clevs= cmap_clevs_ts()
    elif cmap_name == "far":
        cmap,clevs = cmap_clevs_far()
    elif cmap_name == "far":
        cmap,clevs = cmap_clevs_far()
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
    temp_2m_error = "temp_2m_error"
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


def coordinate_cmap_to_clevs(cmap,clevs):
    if hasattr(cmap, "colors"):
        colors0 = np.array(cmap.colors)
        colors_list = []
        ncmap = len(colors0)
        nclev = len(clevs)
        if nclev <2:
            print("clevs' size must bigger than 1")
        for i in range(nclev):
            j = i * (ncmap-1) /(nclev-1)
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



def def_cmap_clevs(cmap = "rainbow",clevs = None,vmin = None,vmax = None):
    #  # 判断是meteva自定义的颜色类型，这从meteva资源文件或函数里生成cmap1 和clevs1
    clevs1 = None
    cmap1 = None

    if isinstance(cmap,str):
        cmap_class = cmaps()
        if hasattr(cmap_class, cmap):
            cmap,clevs1,= get_cmap_and_clevs_by_name(cmap, vmin, vmax)

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
    if vmin is not None and vmax is not None:
        cmap4,clevs4 = get_part_cmap_and_clevs(cmap3, clevs3, vmax, vmin)
    else:
        cmap4,clevs4  = cmap3,clevs3

    return cmap4,clevs4
