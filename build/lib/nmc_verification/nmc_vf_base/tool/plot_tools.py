import os
import numpy as np
import cartopy.crs as ccrs
from nmc_met_graphics.plot.china_map import add_china_map_2cartopy
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import math
from matplotlib.colors import BoundaryNorm

def contourf_2d_grid(grd,title = None,filename = None,clevs= None,cmap = None):
    x = grd['lon'].values
    y = grd['lat'].values
    rlon = x[-1] - x[0]
    rlat = y[-1] - y[0]
    height = 5
    width = height * rlon / rlat + 1
    fig = plt.figure(figsize=(width,height))
    datacrs = ccrs.PlateCarree()
    ax = plt.axes(projection=datacrs)
    if title is not None:
        plt.title(title)
    add_china_map_2cartopy(ax, name='province', edgecolor='k', lw=0.3) #省界
    add_china_map_2cartopy(ax, name='river', edgecolor='blue', lw=0.3) #河流


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
        vmax = inte * ((int)(vmax / inte) + 1)
        clevs = np.arange(vmin,vmax,inte)
    if cmap is None:
        cmap = plt.get_cmap("rainbow")
    im = ax.contourf(x, y, np.squeeze(grd.values),levels = clevs,cmap=cmap, transform=datacrs)
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

    vmin = inte * ((int)(vmin / inte))
    vmax = inte * ((int)(vmax / inte) + 1)
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

    vmin = inte * ((int)(vmin / inte))
    vmax = inte * ((int)(vmax / inte) + 1)
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
    datacrs = ccrs.PlateCarree()
    ax = plt.axes(projection=datacrs)
    map_extent = [x[0],x[-1],y[0],y[-1]]
    ax.set_extent(map_extent)

    if title is not None:
        plt.title(title)
    add_china_map_2cartopy(ax, name='province', edgecolor='k', lw=0.3) #省界
    add_china_map_2cartopy(ax, name='river', edgecolor='blue', lw=0.3) #河流

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
        vmax = inte * ((int)(vmax / inte) + 1)
        clevs = np.arange(vmin,vmax,inte)
    if cmap is None:
        cmap = plt.get_cmap("rainbow")
    norm = BoundaryNorm(clevs, ncolors=cmap.N, clip=True)
    im = ax.pcolormesh(x, y, np.squeeze(grd.values), cmap=cmap,norm=norm,transform=datacrs)
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

    vmin = inte * ((int)(vmin / inte))
    vmax = inte * ((int)(vmax / inte) + 1)
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

    vmin = inte * ((int)(vmin / inte))
    vmax = inte * ((int)(vmax / inte) + 1)
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