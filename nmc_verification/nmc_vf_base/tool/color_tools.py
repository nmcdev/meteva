import numpy as np
import matplotlib.image as image
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import matplotlib.colors as colors


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

def get_color_map_from_picture(path,show = False):
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

    plt.plot(color_type_num_x)
    plt.show()
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

