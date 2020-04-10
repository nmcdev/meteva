import numpy as np
import matplotlib.image as image
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import matplotlib.colors as colors
import pkg_resources
import math



def clev_cmap_temper_2m():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_temp_2m.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_rain_1h():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_1h.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_rain_3h():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_3h.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_rain_24h():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_24h.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_rh():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rh.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_vis():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_vis.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_wind_speed():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_wind_speed.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_cloud_total():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_tcdc.txt")
    return get_clev_and_cmap_from_file(path)

def clev_cmap_rain_1h_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_1h_error.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_rain_3h_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rain_3h_error.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_rh_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_rh_error.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_vis_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_vis_error.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_wind_speed_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_wind_speed_error.txt")
    return get_clev_and_cmap_from_file(path)
def clev_cmap_cloud_total_error():
    path = pkg_resources.resource_filename('meteva', "resources/colormaps/color_tcdc_error.txt")
    return get_clev_and_cmap_from_file(path)

def get_clev_and_cmap_from_file(path):
    clev_cmap = np.loadtxt(path)
    clev = clev_cmap[:, 0]
    cmap = clev_cmap[:, 1:] / 255
    cmap = cmap.tolist()
    cmap = colors.ListedColormap(cmap, 'indexed')
    return clev,cmap

def clev_cmap_bias_1(vmax):
    blue = np.array([0, 0, 255]) / 255
    white = np.array([255, 255, 255]) / 255
    red = np.array([255, 0, 0]) / 255
    black = np.array([0, 0, 0]) / 255
    clev_list = [0]
    cmap_list = [blue]
    for v in range(5):
        clev_list.append(v * 0.2)
        cmap_list.append(blue * (1 - v * 0.2) + white * v * 0.2)
    for v in range(5):
        clev_list.append(1 + v * 0.2)
        cmap_list.append(white * (1 - v * 0.2) + red * v * 0.2)

    for value in range(2, vmax + 1, 1):
        clev_list.append(value)
        cmap_list.append((red * (vmax - value) + black * (value - 2)) / (vmax - 2))
    cmap = colors.ListedColormap(cmap_list, 'indexed')
    return clev_list,cmap

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

def get_clev_and_cmap_by_element_name(element_name):
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
    clev,cmap = get_clev_and_cmap_from_file(path)
    return clev,cmap

def get_part_clev_and_cmap(clev_all,cmap_all,vmax,vmin):
    start_i = 0
    for i in range(len(clev_all)-1):
        if vmin<clev_all[i+1]:
            start_i = i
            break
    end_i = 0
    for i in range(len(clev_all)-1):
        if vmax > clev_all[i]:
            end_i = i+2
    #print(start_i)
    #print(end_i)
    if end_i - start_i<=3:
        end_i = start_i+3

    clev_part = clev_all[start_i:end_i]
    if hasattr(cmap_all,"colors"):
        cmap_colors = cmap_all.colors
        cmap_colors_part = cmap_colors[start_i:end_i]
        cmap_part = colors.ListedColormap(cmap_colors_part, 'indexed')
    else:
        cmap_part = cmap_all
    return clev_part,cmap_part

def write_clev_and_cmap(clev,cmap,path):
    num = len(clev)
    clev_cmap = np.zeros((num,4))
    clev_cmap[:,0] = clev[:]
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
    heigh = 1
    n_h = int(heigh * n_colors/width)
    im = np.outer(np.ones(n_h), np.arange(n_colors))


    fig, ax = plt.subplots(1, figsize=(width, heigh),
                           subplot_kw=dict(xticks=[], yticks=[]))
    if clev is not None:
        max_tick = 10
        step = int(math.ceil(n_colors/max_tick))
        x = np.arange(0,n_colors,step).astype(np.int32)
        print(x)
        ax.set_xticks(x)
        labels = []
        for i in range(x.size):
            labels.append(clev[x[i]])
        ax.set_xticklabels(labels)
    ax.imshow(im, cmap=cmap)

