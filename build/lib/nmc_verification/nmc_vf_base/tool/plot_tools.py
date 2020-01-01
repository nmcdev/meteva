import os
import numpy as np
import pkg_resources
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import math
from matplotlib.colors import BoundaryNorm
from nmc_verification.nmc_vf_base import IV
import nmc_verification
from mpl_toolkits.basemap import Basemap



def add_china_map_2basemap(mp, ax, name='province', facecolor='none',
                           edgecolor='c', lw=2, encoding = 'utf-8',**kwargs):
    """
    Add china province boundary to basemap instance.
    :param mp: basemap instance.
    :param ax: matplotlib axes instance.
    :param name: map name.
    :param facecolor: fill color, default is none.
    :param edgecolor: edge color.
    :param lw: line width.
    :param kwargs: keywords passing to Polygon.
    :return: None.
    """

    # map name
    names = {'nation': "bou1_4p", 'province': "bou2_4p",
             'county': "BOUNT_poly", 'river': "hyd1_4p",
             'river_high': "hyd2_4p"}

    # get shape file and information
    shpfile = pkg_resources.resource_filename(
        'nmc_verification', "resources/maps/" + names[name])
    _ = mp.readshapefile(shpfile, 'states', drawbounds=True,default_encoding=encoding)

    for info, shp in zip(mp.states_info, mp.states):
        poly = Polygon(
            shp, facecolor=facecolor, edgecolor=edgecolor, lw=lw, **kwargs)
        ax.add_patch(poly)


def contourf_2d_grid(grd,title = None,filename = None,clevs= None,cmap = None):
    x = grd['lon'].values
    y = grd['lat'].values
    rlon = x[-1] - x[0]
    rlat = y[-1] - y[0]
    height = 5
    width = height * rlon / rlat + 1
    fig = plt.figure(figsize=(width,height))
    ax = plt.axes()
    grid0 = nmc_verification.nmc_vf_base.get_grid_of_data(grd)
    mp = Basemap(llcrnrlon=grid0.slon, urcrnrlon=grid0.elon, llcrnrlat=grid0.slat, urcrnrlat=grid0.elat)
    add_china_map_2basemap(mp, ax, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    add_china_map_2basemap(mp, ax, name='river', edgecolor='k', lw=0.3, encoding='gbk')  #河流

    if title is not None:
        plt.title(title)
    if clevs is None:
        vmax = np.max(grd.values)
        vmin = np.min(grd.values)
        if vmax - vmin < 1e-10 :
            vmax = vmin + 1.1
        dif=(vmax - vmin) / 10.0
        inte=math.pow(10,math.floor(math.log10(dif)));
        #用基本间隔，将最大最小值除于间隔后小数点部分去除，最后把间隔也整数化
        r=dif/inte
        if  r<3 and r>=1.5:
            inte = inte*2
        elif r<4.5 and r>=3 :
            inte = inte*4
        elif r<5.5 and r>=4.5:
            inte=inte*5
        elif r<7 and r>=5.5:
            inte=inte*6
        elif r>=7 :
            inte=inte*8
        vmin = inte * ((int)(vmin / inte)-1)
        vmax = inte * ((int)(vmax / inte) + 2)
        clevs = np.arange(vmin,vmax,inte)
    if cmap is None:
        cmap = plt.get_cmap("rainbow")
    #im = ax.contourf(x, y, np.squeeze(grd.values),levels = clevs,cmap=cmap, transform=datacrs)
    im = ax.contourf(x, y, np.squeeze(grd.values), levels=clevs, cmap=cmap)
    left_low = (width - 1) / width
    colorbar_position = fig.add_axes([left_low, 0.11, 0.03, 0.77]) # 位置[左,下,宽,高]
    plt.colorbar(im,cax= colorbar_position)

    vmax = x[-1]
    vmin = x[0]
    r = rlon
    if r <= 1:
        inte = 0.1
    elif r <= 5 and r > 1:
        inte = 1
    elif r <= 10 and r > 5:
        inte = 2
    elif r < 20 and r >= 10:
        inte = 4
    elif r <= 30 and r >= 20:
        inte = 5
    else:
        inte = 10

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte)+1)
    xticks = np.arange(vmin,vmax,inte)
    xticks_label = []
    for x in range(len(xticks)):
        xticks_label.append(str(xticks[x]))
    xticks_label[-1] += "°E"
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks_label)

    vmax = y[-1]
    vmin = y[0]
    r = rlat
    if r <= 1:
        inte = 0.1
    elif r <= 5 and r > 1:
        inte = 1
    elif r <= 10 and r > 5:
        inte = 2
    elif r < 20 and r >= 10:
        inte = 4
    elif r <= 30 and r >= 20:
        inte = 5
    else:
        inte = 10

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte)+1)
    yticks = np.arange(vmin,vmax,inte)
    yticks_label = []
    for y in range(len(yticks)):
        yticks_label.append(str(yticks[y]))
    yticks_label[-1] += "°N"
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks_label)

    if(filename is None):
        plt.show()
    else:
        file1,extension = os.path.splitext(filename)
        extension = extension[1:]
        plt.savefig(filename,format = extension)
    plt.close()


def pcolormesh_2d_grid(grd,title = None,filename = None,clevs= None,cmap = None):
    x = grd['lon'].values
    y = grd['lat'].values
    rlon = x[-1] - x[0]
    rlat = y[-1] - y[0]
    height = 5
    width = height * rlon / rlat + 1
    fig = plt.figure(figsize=(width,height))

    ax = plt.axes()

    if title is not None:
        plt.title(title)
    grid0 = nmc_verification.nmc_vf_base.get_grid_of_data(grd)
    mp = Basemap(llcrnrlon=grid0.slon, urcrnrlon=grid0.elon, llcrnrlat=grid0.slat, urcrnrlat=grid0.elat)
    add_china_map_2basemap(mp, ax, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    add_china_map_2basemap(mp, ax, name='river', edgecolor='k', lw=0.3, encoding='gbk')  #河流

    if clevs is None:
        vmax = np.max(grd.values)
        vmin = np.min(grd.values)
        if vmax - vmin < 1e-10 :
            vmax = vmin + 1.1
        dif=(vmax - vmin) / 10.0
        inte=math.pow(10,math.floor(math.log10(dif)));
        #用基本间隔，将最大最小值除于间隔后小数点部分去除，最后把间隔也整数化
        r=dif/inte
        if  r<3 and r>=1.5:
            inte = inte*2
        elif r<4.5 and r>=3 :
            inte = inte*4
        elif r<5.5 and r>=4.5:
            inte=inte*5
        elif r<7 and r>=5.5:
            inte=inte*6
        elif r>=7 :
            inte=inte*8
        vmin = inte * ((int)(vmin / inte))
        vmax = inte * ((int)(vmax / inte) + 2)
        clevs = np.arange(vmin,vmax,inte)
    if cmap is None:
        cmap = plt.get_cmap("rainbow")
    norm = BoundaryNorm(clevs, ncolors=cmap.N, clip=True)
    im = ax.pcolormesh(x, y, np.squeeze(grd.values), cmap=cmap,norm=norm)
    left_low = (width - 1) / width
    colorbar_position = fig.add_axes([left_low, 0.11, 0.03, 0.77]) # 位置[左,下,宽,高]
    plt.colorbar(im,cax= colorbar_position)

    vmax = x[-1]
    vmin = x[0]
    r = rlon
    if r <= 1:
        inte = 0.1
    elif r <= 5 and r > 1:
        inte = 1
    elif r <= 10 and r > 5:
        inte = 2
    elif r < 20 and r >= 10:
        inte = 4
    elif r <= 30 and r >= 20:
        inte = 5
    else:
        inte = 10

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte)+1)
    xticks = np.arange(vmin,vmax,inte)
    xticks_label = []
    for x in range(len(xticks)):
        xticks_label.append(str(xticks[x]))
    xticks_label[-1] += "°E"
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks_label)



    vmax = y[-1]
    vmin = y[0]
    r = rlat
    if r <= 1:
        inte = 0.1
    elif r <= 5 and r > 1:
        inte = 1
    elif r <= 10 and r > 5:
        inte = 2
    elif r < 20 and r >= 10:
        inte = 4
    elif r <= 30 and r >= 20:
        inte = 5
    else:
        inte = 10

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte)+1)
    yticks = np.arange(vmin,vmax,inte)
    yticks_label = []
    for y in range(len(yticks)):
        yticks_label.append(str(yticks[y]))
    yticks_label[-1] += "°N"
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks_label)

    if(filename is None):
        plt.show()
    else:
        file1,extension = os.path.splitext(filename)
        extension = extension[1:]
        plt.savefig(filename,format = extension)
    plt.close()


def set_plot_IV(dat0):
    num = len(dat0)
    dat = np.zeros_like(dat0)
    dat[:] = dat0[:]
    if dat[0] == IV:
        dat[0] = 0
        for i in range(1,num):
            if dat0[i] != IV:
                dat[0] = dat0[i]
    if dat[-1] == IV:
        dat[-1] = 0
        for i in range(num-2,-1,-1):
            if dat0[i] != IV:
                dat[-1] = dat0[i]

    for i in range(1,num-1):
        if dat[i] == IV:
            i1 = 0
            for p in range(num):
                if dat[i - p] != IV:
                    i1 = i - p
                    break
            i2 = num - 1
            for p in range(num):
                if dat[i + p] != IV:
                    i2 = i + p
                    break
            rate = (i- i1) / (i2 - i1)
            dat[i] = dat[i1] * (1-rate) + dat[i2] * rate
    return dat