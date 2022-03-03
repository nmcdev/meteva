import meteva
import numpy as np
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import math
from matplotlib.colors import BoundaryNorm




def add_map(ax,add_county_line = False,add_worldmap = True,title = None,sup_fontsize = 12):
    if add_worldmap:
        meteva.base.tool.plot_tools.add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"
    meteva.base.tool.plot_tools.add_china_map_2basemap(ax, name="nation", edgecolor='k', lw=0.3,encoding = 'gbk')  #"国界"
    meteva.base.tool.plot_tools.add_china_map_2basemap(ax, edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        meteva.base.tool.plot_tools.add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "省界"
    ax.set_title(title,fontsize = sup_fontsize* 0.9)
    return ax



def creat_axs(nplot,map_extend,ncol = None,height  = None,width = None,dpi = 300,sup_title = None,sup_fontsize = 12,
              add_county_line = False,add_worldmap = True,title_list = None,add_index = None,wspace = None):


    ax_index = []
    if add_index is not None:
        if add_index is True:
            ax_index = ["(a)","(b)","(c)","(d)","(e)","(f)","(g)","(h)","(i)","(j)",
                        "(k)", "(l)", "(m)", "(n)", "(o)", "(p)", "(q)", "(r)", "(s)", "(t)",
                        "(u)", "(v)", "(w)", "(x)", "(y)", "(z)"]
        else:
            ax_index = add_index


    if isinstance(map_extend, list):
        slon = map_extend[0]
        elon = map_extend[1]
        slat = map_extend[2]
        elat = map_extend[3]
        rlon = elon - slon
        rlat = elat - slat
    else:
        slon = map_extend.slon
        slat = map_extend.slat
        elon = map_extend.elon
        elat = map_extend.elat
        rlon = map_extend.elon - map_extend.slon
        rlat = map_extend.elat - map_extend.slat


    if sup_title is None:
        sup_height_title = 0
    else:
        sup_height_title = sup_fontsize * 0.12

    height_title = sup_fontsize * 0.1
    height_bottem_xticsk = sup_fontsize * 0.05
    height_hspace = sup_fontsize * 0.1

    if wspace is None:
        width_wspace = height_hspace*2
    else:
        width_wspace = wspace

    width_colorbar = 0.5
    width_left_yticks = sup_fontsize * 0.2

    if ncol is None:
        match_list = []
        for i in range(nplot, 0, -1):
            ncol = i
            nrow = int(math.ceil(nplot / ncol))
            rate = ncol * rlon / (nrow * rlat)
            if rate < 2 and rate > 9 / 16:
                match_list.append([i, ncol * nrow - nplot])
        if len(match_list) == 0:
            ncol = nplot
        else:
            match_array = np.array(match_list)
            min_index = np.argmin(match_array[:, 1])
            ncol = match_array[min_index, 0]
    nrow = int(math.ceil(nplot / ncol))

    if width is None and height is None:
        width = 8

    if width is None:
        height_all_plot = height - height_title - height_bottem_xticsk - (nrow - 1) * height_hspace + sup_height_title
        height_map = height_all_plot / nrow
        width_map = height_map * rlon / rlat
        width_all_plot = width_map * ncol + (ncol - 1) * width_wspace
        width = width_all_plot + width_colorbar + width_left_yticks
    else:
        width_all_plot = width - width_colorbar - width_left_yticks - (ncol - 1) * width_wspace
        width_map = width_all_plot / ncol
        height_map = width_map * rlat / rlon
        height_all_plot = height_map * nrow + (nrow - 1) * height_hspace
        height = height_all_plot + height_title + height_bottem_xticsk + sup_height_title

    vmax = elon
    vmin = slon
    r = rlon
    if r <= 0.1:
        inte = 0.05
    elif r <= 0.5:
        inte = 0.1
    elif r <= 1:
        inte = 0.2
    elif r <= 5 and r > 1:
        inte = 1
    elif r <= 10 and r > 5:
        inte = 2
    elif r < 20 and r >= 10:
        inte = 4
    elif r <= 30 and r >= 20:
        inte = 5
    elif r < 180:
        inte = 10
    else:
        inte = 20

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte)+0.5)

    xticks = np.arange(vmin, vmax, inte)
    xticks_label = []
    xticks_label_None = []
    for x in range(len(xticks)):
        v1 = xticks[x]
        if abs(v1 - int(v1))<1e-7:
            xticks_label.append(str(int(round(v1, 6))))
        else:
            xticks_label.append(str(round(v1, 6)))
        xticks_label_None.append("")
    if xticks[-1] > 0:
        xticks_label[-1] = "   " + xticks_label[-1] + "°E"
    else:
        xticks_label[-1] = "   " + xticks_label[-1] + "°W"

    vmax = elat
    vmin = slat
    r = rlat
    if r <= 0.05:
        inte = 0.01
    elif r <= 0.3:
        inte = 0.05
    elif r <= 1:
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
    vmax = inte * ((int)(vmax / inte)+0.5)
    yticks = np.arange(vmin, vmax, inte)
    yticks_label = []
    yticks_label_None = []
    for y in range(len(yticks)):
        v1 = yticks[y]
        if abs(v1 - int(v1))<1e-7:
            v1 = int(round(v1, 6))
        else:
            v1 = round(v1, 6)

        if yticks[y] >= 0:
            yticks_label.append(str(v1) + "°N")
        else:
            yticks_label.append(str(v1) + "°S")
        yticks_label_None.append("")

    fig = plt.figure(figsize=(width, height), dpi=dpi)
    y_sup_title = (height_bottem_xticsk -0.1 + (nrow) * (height_map + height_hspace)) / height
    if sup_title is not None:
        plt.suptitle(sup_title, x = 0.6,y = y_sup_title,fontsize=sup_fontsize)
    ax_list = []
    for p in range(nplot):
        pi = p % ncol
        pj = int(p / ncol)

        rect1 = [(width_left_yticks + pi * (width_map + width_wspace)) / width,
                 (height_bottem_xticsk + (nrow - 1 - pj) * (height_map + height_hspace)) / height,
                 width_map / width,
                 height_map / height]
        ax = plt.axes(rect1)
        ax.set_xlim((slon, elon))
        ax.set_ylim((slat, elat))

        # vmax = elon
        # vmin = slon
        # r = max(rlon,rlat)
        # if r <= 0.1:
        #     inte = 0.05
        # elif r <= 0.5:
        #     inte = 0.1
        # elif r <=1:
        #     inte = 0.2
        # elif r <= 5 and r > 1:
        #     inte = 1
        # elif r <= 10 and r > 5:
        #     inte = 2
        # elif r < 20 and r >= 10:
        #     inte = 4
        # elif r <= 30 and r >= 20:
        #     inte = 5
        # elif r < 180:
        #     inte = 10
        # else:
        #     inte = 20
        #
        # vmin = inte * (math.ceil(vmin / inte))
        # vmax = inte * ((int)(vmax / inte) + 0.5)
        # xticks = np.arange(vmin, vmax, inte)
        # xticks_label = []
        # for x in range(len(xticks)):
        #     xticks_label.append(str(round(xticks[x], 6)))
        # if xticks[-1] > 0:
        #     xticks_label[-1] = "   " + xticks_label[-1] + "°E"
        # else:
        #     xticks_label[-1] = "   " + xticks_label[-1] + "°W"
        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks_label, fontsize=sup_fontsize * 0.9, family='Times New Roman')

        # vmax = elat
        # vmin = slat
        # r = rlat
        # if r <= 0.1:
        #     inte = 0.05
        # elif r <= 0.5:
        #     inte = 0.1
        # elif r <=1:
        #     inte = 0.2
        # elif r <= 5 and r > 1:
        #     inte = 1
        # elif r <= 10 and r > 5:
        #     inte = 2
        # elif r < 20 and r >= 10:
        #     inte = 4
        # elif r <= 30 and r >= 20:
        #     inte = 5
        # else:
        #     inte = 10
        #
        # vmin = inte * (math.ceil(vmin / inte))
        # vmax = inte * ((int)(vmax / inte)+0.5)
        # yticks = np.arange(vmin, vmax, inte)
        # yticks_label = []
        # for y in range(len(yticks)):
        #
        #     if yticks[y] >= 0 and y == len(yticks) - 1:
        #         yticks_label.append(str(round(yticks[y], 6)) + "°N")
        #     elif yticks[y] < 0 and y == 0:
        #         yticks_label.append(str(round(-yticks[y], 6)) + "°S")
        #     elif yticks[y] == 0:
        #         yticks_label.append("EQ" + "  ")
        #     else:
        #         yticks_label.append(str(round(yticks[y], 6)) + "    ")
        ax.set_yticks(yticks)
        ax.set_yticklabels(yticks_label, fontsize=sup_fontsize * 0.9, family='Times New Roman')


        if title_list is None:
            sub_title = None
        else:
            sub_title = title_list[p]
        add_map(ax,add_county_line=add_county_line,add_worldmap=add_worldmap,sup_fontsize=sup_fontsize,title=sub_title)

        if len(ax_index)>1:

            ix = slon + 0.008*(elon - slon) * sup_fontsize / width_map
            iy = elat - 0.018*(elat - slat) * sup_fontsize / height_map

            plt.text(ix, iy, ax_index[p], bbox=dict(fc='white', ec='white'),fontsize = sup_fontsize,zorder=100)


        ax_list.append(ax)



    return ax_list


def cread_ax(map_extend,height  = None,width = None,dpi = 300,add_county_line = False,title = None,sup_fontsize = 10,add_worldmap = False):
    if isinstance(map_extend,list):
        slon = map_extend[0]
        elon = map_extend[1]
        slat = map_extend[2]
        elat = map_extend[3]

    elif isinstance(map_extend,meteva.base.grid):
        slon = map_extend.slon
        slat = map_extend.slat
        elon = map_extend.elon
        elat = map_extend.elat

    rlon = elon - slon
    rlat = elat - slat

    if height is None:
        height = 4
    title_hight = 0.3
    legend_hight = 0.1
    left_plots_width  = 0.8
    right_plots_width = 0.8
    if width is None:
        width = (height - title_hight - legend_hight) * rlon / rlat + left_plots_width + right_plots_width
    #print(width)
    fig = plt.figure(figsize=(width, height),dpi = dpi)
    rect1 = [left_plots_width / width, legend_hight/height, (width - right_plots_width - left_plots_width) / width, 1-title_hight/height]
    ax = plt.axes(rect1)


    if slon < 70 or elon > 140 or slat < 10 or elat > 60:
        add_worldmap = True
    if add_worldmap:
        meteva.base.tool.plot_tools.add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"

    meteva.base.tool.plot_tools.add_china_map_2basemap(ax, name="nation", edgecolor='k', lw=0.3,encoding = 'gbk')  #"国界"
    meteva.base.tool.plot_tools.add_china_map_2basemap(ax, edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        meteva.base.tool.plot_tools.add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "省界"
    ax.set_xlim((slon, elon))
    ax.set_ylim((slat, elat))
    ax.set_title(title,fontsize = sup_fontsize)


    vmax = elon
    vmin = slon
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
    elif r <180:
        inte = 10
    else:
        inte = 20

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte)+1)
    xticks = np.arange(vmin,vmax,inte)
    xticks_label = []
    for x in range(len(xticks)):
        xticks_label.append(str(round(xticks[x],6)))
    if xticks[-1] >0:
        xticks_label[-1] ="   " +xticks_label[-1] + "°E"
    else:
        xticks_label[-1] ="   " +xticks_label[-1] + "°W"
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks_label,fontsize = sup_fontsize * 0.9)

    vmax = elat
    vmin = slat
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
        if yticks[y] >= 0:
            yticks_label.append(str(round(yticks[y],6))+"°N")
        else:
            yticks_label.append(str(round(-yticks[y], 6)) +"°S")
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks_label,fontsize = sup_fontsize * 0.9)
    return ax

def add_contourf(ax,grd,cmap ="rainbow",clevs= None,add_colorbar = True,cut_colorbar = True):
    x = grd['lon'].values
    y = grd['lat'].values
    vmax = np.max(grd.values)
    vmin = np.min(grd.values)

    cmap1,clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap,clevs=clevs,vmin=vmin,vmax = vmax,cut_colorbar = cut_colorbar)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    im = ax.contourf(x, y, np.squeeze(grd.values), levels=clevs1, cmap=cmap1,norm = norm)

    fig = plt.gcf()
    width = fig.bbox.width/fig.dpi
    height = fig.bbox.height/fig.dpi
    location = [ax.bbox.x1/fig.dpi/width+0.005, ax.bbox.y0 / fig.dpi/height, 0.01, ax.bbox.height/fig.dpi/height]

    if(add_colorbar):
        colorbar_position = fig.add_axes(location)  # 位置[左,下,宽,高]
        plt.colorbar(im,cax= colorbar_position)
    return im

def add_contour(ax,grd,color='k',clevs = None,linewidths = 1,label_fontsize = 5):
    x = grd['lon'].values
    y = grd['lat'].values
    vmax = np.max(grd.values)
    vmin = np.min(grd.values)
    if clevs is None:
        dif = (vmax - vmin) / 10.0
        inte = math.pow(10, math.floor(math.log10(dif)));
        #用基本间隔，将最大最小值除于间隔后小数点部分去除，最后把间隔也整数化
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
        vmax = inte * (math.ceil(vmax / inte) + 0.5)
        clevs = np.arange(vmin, vmax, inte)
    mm = max(abs(clevs[0]),abs(clevs[-1]))
    if mm!=0:
        mmi = math.ceil(math.log10(mm))
        if mmi >=2:
            f1 = mmi
            f2 = 0
        elif mmi == 1:
            f1 = 2
            f2 = 1
        else:
            mmi = math.floor(math.log10(mm))
            f1 = 1+abs(mmi)
            f2 = f1
    else:
        f1 = 1
        f2 = 0
    fmt = "%"+str(f1)+"."+str(f2)+"f"
    print(clevs)
    cs = ax.contour(x, y, np.squeeze(grd.values),levels = clevs,colors = color,linewidths = linewidths)
    ax.clabel(cs, inline=1, fontsize=label_fontsize,fmt=fmt)

def add_mesh(ax,grd,cmap ="rainbow",clevs= None,add_colorbar = True):
    x = grd['lon'].values
    y = grd['lat'].values
    vmax = np.max(grd.values)
    vmin = np.min(grd.values)
    cmap1,clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap,clevs=clevs,vmin=vmin,vmax = vmax)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    im = ax.pcolormesh(x, y, np.squeeze(grd.values), cmap=cmap1, norm=norm)
    #im = ax.contourf(x, y, np.squeeze(grd.values), levels=clevs1, cmap=cmap1,norm = norm)

    fig = plt.gcf()
    width = fig.bbox.width/fig.dpi
    height = fig.bbox.height/fig.dpi
    left_low = (width +0.1 - 0.8) / width
    if add_colorbar:
        colorbar_position = fig.add_axes([left_low, 0.1 / height, 0.02, 1 - 0.3 / height])  # 位置[左,下,宽,高]
        plt.colorbar(im,cax= colorbar_position)

def add_barbs(ax,wind,color = "k",skip = None):
    x = wind['lon'].values
    y = wind['lat'].values
    X, Y = np.meshgrid(x, y)
    u = np.squeeze(wind.values[0,...])
    v = np.squeeze(wind.values[1,...])

    fig = plt.gcf()
    width = fig.bbox.width/fig.dpi

    if skip is  not None:
        length = math.sqrt((width-1) * skip / x.size) * 10
    else:
        length = ax.bbox.width/fig.dpi
        skip =int((length /10)**2 * x.size / (width - 1))+1

    print(length)
    ax.barbs(X[::skip,::skip],Y[::skip,::skip] , u[::skip,::skip], v[::skip,::skip],
             sizes=dict(emptybarb=0.01, spacing=0.23, height=0.5,width = 0.25),color = color,
             barb_increments=dict(half=2, full=4, flag=20),length = length,linewidth = length * length  * 0.03)
    #ax.barbs(X,Y,u,v,regrid_shape = 20)



def add_scatter(ax,map_extend,sta0,cmap = "rainbow",clevs = None,point_size = None,fix_size = True,title = None,threshold = 2,min_spot_value = 0,mean_value = 2,
                grid = False,add_colorbar = True,alpha = None):
    sta = sta0
    if isinstance(map_extend, list):
        slon = map_extend[0]
        elon = map_extend[1]
        slat = map_extend[2]
        elat = map_extend[3]
        rlon = elon - slon
        rlat = elat - slat
    else:
        slon = map_extend.slon
        slat = map_extend.slat
        elon = map_extend.elon
        elat = map_extend.elat
        rlon = map_extend.elon - map_extend.slon
        rlat = map_extend.elat - map_extend.slat

    sta_without_iv = meteva.base.sele.not_IV(sta)
    data_names = meteva.base.get_stadata_names(sta_without_iv)
    sta_without_iv = sta_without_iv.sort_values(by=data_names[-1], ascending=True)

    values = sta_without_iv.iloc[:, -1].values

    vmax_v = np.max(sta_without_iv.iloc[:,-1].values)
    vmin_v = np.min(sta_without_iv.iloc[:,-1].values)

    cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap, clevs=clevs, vmin=vmin_v, vmax=vmax_v)

    norm = BoundaryNorm(clevs1, ncolors=cmap1.N - 1)
    fig = plt.gcf()
    map_width = ax.bbox.width/fig.dpi

    if point_size is None:
        sta_id1 = sta0.drop_duplicates(['id'])
        sta_dis = meteva.base.sta_dis_ensemble_near_by_sta(sta_id1, nearNum=2)
        dis_values = sta_dis["data1"].values
        dis_values.sort()
        dis1 = dis_values[int(len(dis_values) * 0.02) + 1]/1.2
        point_size = (map_width * dis1 / rlon) ** 2
        # point_size = 100 * map_area / len(sta.index)
        # print("**************")
        # print(point_size)
        if (point_size > 30): point_size = 30
        if (point_size < 0.5):
            point_size = 0.5
            if alpha is None:
                alpha = 0.5
        # point_size *=3
        #left_low = (width + 0.1 - right_plots_width) / width


    x = sta_without_iv.loc[:, "lon"].values
    y = sta_without_iv.loc[:, "lat"].values
    colors = values
    if isinstance(fix_size, bool):
        if fix_size:
            im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=point_size,edgecolors = "face",alpha = alpha)
        else:
            area = point_size * np.abs(values - min_spot_value) / mean_value
            if (threshold is not None):
                area[np.abs(values - min_spot_value) < threshold] *= 0.1
            im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=area,edgecolors  = 'face',alpha = alpha)
            if grid: plt.grid()
    else:
        im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=fix_size,edgecolors  = 'face',alpha = alpha)
    plt.title(title)

    if add_colorbar:
        width = fig.bbox.width / fig.dpi
        height = fig.bbox.height / fig.dpi
        location = [ax.bbox.x1 / fig.dpi / width + 0.005, ax.bbox.y0 / fig.dpi / height, 0.01,
                    ax.bbox.height / fig.dpi / height]

        if (add_colorbar):
            colorbar_position = fig.add_axes(location)  # 位置[左,下,宽,高]
            plt.colorbar(im, cax=colorbar_position)
    return im


def add_scatter_text(ax,sta0,map_extend = None,color = "k",cmap = None,clevs = None,title = None,tag = 2,
                grid = False,add_colorbar = True,alpha = None,font_size = 10):
    x0 = ax.transLimits._boxin.x0
    x1 = ax.transLimits._boxin.x1
    y0 = ax.transLimits._boxin.y0
    y1 = ax.transLimits._boxin.y1
    sta = meteva.base.sele_by_para(sta0,lon=[x0,x1],lat=[y0,y1])
    sta_without_iv = meteva.base.sele.not_IV(sta)
    data_names = meteva.base.get_stadata_names(sta_without_iv)
    sta_without_iv = sta_without_iv.sort_values(by=data_names[-1], ascending=True)

    vmax_v = np.max(sta_without_iv.iloc[:,-1].values)
    vmin_v = np.min(sta_without_iv.iloc[:,-1].values)
    clevs1 = None
    cmap1 = None
    if cmap is not None:
        cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap, clevs=clevs, vmin=vmin_v, vmax=vmax_v)

    fig = plt.gcf()
    fmt_tag = "%." + str(tag) + "f"

    if cmap1 is None:
        nsta = len(sta_without_iv.index)
        for i in range(nsta):
            x = sta_without_iv.iloc[i,4]
            y = sta_without_iv.iloc[i,5]
            v = sta_without_iv.iloc[i,-1]
            if isinstance(v,str):
                ax.text(x, y, v, ha="center", va="center", fontsize=font_size, color=color)
            else:
                ax.text(x, y, fmt_tag % v, ha="center", va="center",fontsize=font_size,color = color)
    else:
        x = sta_without_iv.iloc[:, 4].values
        y = sta_without_iv.iloc[:, 5].values
        v = sta_without_iv.iloc[:, -1].values
        for k in range(len(clevs1)-1):
            index = np.where((v>clevs1[k])&(v<clevs1[k+1]))
            if len(index[0])>0:
                x1 = x[index]
                y1 = y[index]
                v1 = v[index]
                color = cmap1(k)
                for j in range(x1.size):
                    if isinstance(v1[j],str):
                        ax.text(x1[j], y1[j], v1[j], ha="center", va="center", fontsize=font_size, c=color)
                    else:
                        ax.text(x1[j], y1[j], fmt_tag % v1[j], ha="center", va="center", fontsize=font_size,  c=color)






def add_shear_line(ax,map_extend,graphy):
    if isinstance(map_extend,list):
        slon = map_extend[0]
        elon = map_extend[1]
        slat = map_extend[2]
        elat = map_extend[3]

    elif isinstance(map_extend,meteva.base.grid):
        slon = map_extend.slon
        slat = map_extend.slat
        elon = map_extend.elon
        elat = map_extend.elat

    rlon = elon - slon
    rlat = elat - slat
    fig = plt.gcf()
    map_width = ax.bbox.width / fig.dpi

    line_width = rlon *  0.015/ map_width

    features = graphy["features"]
    for value in features.values():
        line = value["axes"]
        line_type = line["line_type"]
        point = np.array(line["point"])
        dp = np.zeros(point.shape)
        dp[:-1,:] = point[1:,:] - point[:-1,:]
        dp[-1,:] = dp[-2,:]
        length = (dp[:,0]**2 + dp[:,1] **2)**0.5
        dx = -dp[:,1] * line_width/ length
        dy = dp[:,0] * line_width/length


        if line_type =="c":
            ax.plot(point[:,0] - dx ,point[:,1] - dy,"b",linewidth = 1)
            ax.plot(point[:, 0] + dx, point[:, 1] + dy, "b",linewidth =  1)
        else:
            ax.plot(point[:, 0] - dx, point[:, 1] - dy, "r",linewidth =  1)
            ax.plot(point[:, 0] + dx, point[:, 1] + dy, "r",linewidth =  1)
    ax.set_xlim(slon,elon)
    ax.set_ylim(slat,elat)


def add_closed_line(ax,graphy,color = "k",line_width=2,fontsize = 10):
    x0 = ax.transLimits._boxin.x0
    x1 = ax.transLimits._boxin.x1
    y0 = ax.transLimits._boxin.y0
    y1 = ax.transLimits._boxin.y1

    contours =graphy["closed_contours"]
    ncontour = len(contours["cn_label"])


    for n in range(ncontour):
        line_array = contours["cn_xyz"][n][:,0:2]
        ax.plot(line_array[:,0], line_array[:,1], color=color, linewidth=line_width)
        value = contours["cn_label"][n]
        i_s = -1
        line_dict = None
        while i_s < line_array.shape[0]-1:
            i_s += 1
            x = line_array[i_s,0]
            y = line_array[i_s,1]

            if x >=x0 and x<= x1 and y >=y0 and y <= y1:
                if i_s == 0:
                    x_1 = line_array[1,0]
                    y_1 = line_array[1,1]
                    if x_1 == x:
                        rotation = 90
                    else:
                        rotation = math.atan((y_1 - y)/(x_1 - x)) * 180 / math.pi
                    plt.text(x, y, value, ha="center", va="center", fontsize=fontsize, color=color,
                            rotation = rotation,bbox ={"facecolor":"w","pad":0,"linewidth":0})
                    break
                else:
                    if line_dict is None:
                        line_dict = {}
                        line_dict["x"] = []
                        line_dict["y"] = []
                    else:
                        line_dict["x"].append(x)
                        line_dict["y"].append(y)
            else:
                if line_dict is not None:
                    np = len(line_dict["x"])
                    if np >5:
                        np_half = int(np/2)
                        x = line_dict["x"][np_half]
                        y = line_dict["y"][np_half]
                        x_1 =  line_dict["x"][np_half+1]
                        y_1 = line_dict["y"][np_half+1]
                        if x_1 == x:
                            rotation = 90
                        else:
                            rotation = math.atan((y_1 - y) / (x_1 - x)) * 180 / math.pi
                        plt.text(x, y, value, ha="center", va="center", fontsize=fontsize, color=color,
                                 rotation=rotation,bbox ={"facecolor":"w","pad":0,"linewidth":0})
                        line_dict = None


    return


def add_trough_axes(ax,map_extend,graphy,line_width = None):
    if isinstance(map_extend,list):
        slon = map_extend[0]
        elon = map_extend[1]
        slat = map_extend[2]
        elat = map_extend[3]

    elif isinstance(map_extend,meteva.base.grid):
        slon = map_extend.slon
        slat = map_extend.slat
        elon = map_extend.elon
        elat = map_extend.elat

    rlon = elon - slon
    rlat = elat - slat
    fig = plt.gcf()
    map_width = ax.bbox.width / fig.dpi

    if line_width is None:
        line_width = rlon *  0.015/ map_width

    features = graphy["features"]
    for value in features.values():
        line = value["axes"]
        point = np.array(line["point"])
        ax.plot(point[:, 0], point[:, 1], "r", linewidth=line_width)

    ax.set_xlim(slon,elon)
    ax.set_ylim(slat,elat)

def add_jet_axes(ax,map_extend,graphy):
    if isinstance(map_extend,list):
        slon = map_extend[0]
        elon = map_extend[1]
        slat = map_extend[2]
        elat = map_extend[3]

    elif isinstance(map_extend,meteva.base.grid):
        slon = map_extend.slon
        slat = map_extend.slat
        elon = map_extend.elon
        elat = map_extend.elat

    rlon = elon - slon
    rlat = elat - slat
    fig = plt.gcf()
    map_width = ax.bbox.width / fig.dpi

    line_width = rlon *  0.015/ map_width

    features = graphy["features"]
    for value in features.values():
        line = value["axes"]
        point = np.array(line["point"])
        npoint = len(line["point"])

        ns = npoint -1
        dx = 0
        dy = 0
        while ns >0:
            ns -= 1
            dx = point[npoint-1,0] - point[ns,0]
            dy = point[npoint-1,1] - point[ns,1]
            dis = (dx**2 + dy**2)**0.5
            if dis > 0.3:
                break

        ax.arrow(point[ns,0],point[ns,1],dx*0.01,dy*0.01,head_width=0.3,head_length = 0.3,fc = "yellow",ec = "yellow")
        ax.plot(point[:ns, 0], point[:ns, 1], "yellow", linewidth=2)

    ax.set_xlim(slon,elon)
    ax.set_ylim(slat,elat)


def add_cyclone_trace(ax,sta_cyclone_trace,size = 0.2):

    np = len(sta_cyclone_trace.index)
    for i in range(np - 1):
        lon = [sta_cyclone_trace.iloc[i,4],sta_cyclone_trace.iloc[i+1,4]]
        lat = [sta_cyclone_trace.iloc[i,5],sta_cyclone_trace.iloc[i+1,5]]
        speed = sta_cyclone_trace.iloc[i+1,-1]


        if speed > 10.8 and speed <17.2:
            color = "yellow"
        elif speed >=17.2 and speed <24.5:
            color = "b"
        elif speed >= 24.5 and speed < 32.7:
            color = "g"
        elif speed >= 32.7 and speed < 41.5:
            color = "orange"
        elif speed >=41.5 and speed < 51:
            color = "m"
        else:
            color = "r"
        ax.plot(lon, lat, c = color, linewidth=1, zorder=29)
        time_ob = sta_cyclone_trace.iloc[i,1]

        if (time_ob.hour - 2) %12 ==0:
            r_o = size
            lon_list = []
            lat_list = []
            for a in range(0,360,5):
                if a> 70 and a<135:
                    lon1 = lon[0] + r_o *2.5 * math.cos(70 * math.pi/180)
                    lat1 = lat[0] + r_o *2.5 * math.sin(70 * math.pi/180)
                elif a >250 and a < 315:
                    lon1 = lon[0] + r_o * 2.5 * math.cos(250 * math.pi / 180)
                    lat1 = lat[0] + r_o * 2.5 * math.sin(250 * math.pi / 180)
                else:
                    theta = math.pi * a / 180
                    lon1 = lon[0] + r_o * math.cos(theta)
                    lat1 = lat[0] + r_o * math.sin(theta)
                lon_list.append(lon1)
                lat_list.append(lat1)
            plt.fill(lon_list,lat_list,c = color,zorder = 30)
            r_o = size * 0.3
            lon_list = []
            lat_list = []
            for a in range(0,360,5):
                theta = math.pi * a / 180
                lon1 = lon[0] + r_o * math.cos(theta)
                lat1 = lat[0] + r_o * math.sin(theta)
                lon_list.append(lon1)
                lat_list.append(lat1)
            plt.fill(lon_list,lat_list,c = "white",zorder = 30)

