import meteva
import math
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import datetime


def process_compare(ob_list ,fo_list_list ,map_extend = None ,width = 12 ,dpi = 300 ,sup_title = None ,sup_fontsize = 10,
                    add_county_line = False ,add_worldmap = True, xticks_inter = None ,yticks_inter = None ,grid = True,
                    linewidth = [0.3 ,0.3 ,0.2] ,color = ["k" ,"k" ,"k"] ,cmap ="rainbow" ,clevs= None ,save_path = None):
    nrow = len(fo_list_list) + 1
    ncol = len(ob_list)
    for i in range(len(fo_list_list)):
        if ncol < len(fo_list_list[i]):
            ncol = len(fo_list_list[i])

    if map_extend is None:
        map_extend = meteva.base.get_grid_of_data(ob_list[0])


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
    height_hspace = 0
    width_wspace = 0
    width_colorbar = 0.1
    width_left_yticks = sup_fontsize * 0.2

    width_all_plot = width - width_colorbar - width_left_yticks - (ncol - 1) * width_wspace
    width_map = width_all_plot / ncol
    height_map = width_map * rlat / rlon
    height_all_plot = height_map * nrow + (nrow - 1) * height_hspace
    height = height_all_plot + height_title + height_bottem_xticsk + sup_height_title

    vmax = elon
    vmin = slon
    if xticks_inter is None:
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
    else:
        inte = xticks_inter

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte ) +0.5)

    xticks = np.arange(vmin, vmax, inte)
    xticks_label = []
    xticks_label_None = []
    for x in range(len(xticks)):
        v1 = xticks[x]
        if abs(v1 - int(v1) ) <1e-7:
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
    if yticks_inter is None:
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
    else:
        inter = yticks_inter

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte ) +0.5)
    yticks = np.arange(vmin, vmax, inte)
    yticks_label = []
    yticks_label_None = []
    for y in range(len(yticks)):
        v1 = yticks[y]
        if abs(v1 - int(v1) ) <1e-7:
            v1 = int(round(v1, 6))
        else:
            v1 = round(v1, 6)

        if yticks[y] >= 0:
            yticks_label.append(str(v1) + "°N")
        else:
            yticks_label.append(str(v1) + "°S")
        yticks_label_None.append("")
    fig = plt.figure(figsize=(width, height), dpi=dpi)

    y_sup_title = (height_bottem_xticsk  + nrow * height_map +(nrow - 1) * height_hspace) / height
    if sup_title is not None:
        plt.suptitle(sup_title, x=width_left_yticks / width, y=y_sup_title, fontsize=sup_fontsize,
                     horizontalalignment="left",
                     verticalalignment="top")

    valid_time_list = []
    print(len(ob_list))
    for i in range(len(ob_list)):
        print(ob_list[i]["time"].values)
        time1 = meteva.base.all_type_time_to_datetime(ob_list[i]["time"].values[0])
        valid_time_list.append(time1)

    for j in range(len(fo_list_list)):
        fo_list = fo_list_list[j]
        for i in range(len(fo_list)):
            dh = int(fo_list[i]["dtime"].values[0])
            time0 = meteva.base.all_type_time_to_datetime(fo_list[i]["time"].values[0])
            time1 = time0 + datetime.timedelta(hours=dh)
            valid_time_list.append(time1)
    valid_time_list = list(set(valid_time_list))
    valid_time_list.sort()

    col_dict = {}
    for i in range(len(valid_time_list)):
        col_dict[valid_time_list[i]] = i

    #     cmap1,clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap,clevs=clevs,cut_colorbar = False)
    #     norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    #     im = ax.contourf(x, y, np.squeeze(grd1.values), levels=clevs1, cmap=cmap1,norm = norm)

    # 绘制观测
    ax_list_list = []
    ax_list = []
    for i in range(len(ob_list)):
        time1 = meteva.base.all_type_time_to_datetime(ob_list[i]["time"].values[0])
        pi = col_dict[time1]
        pj = 0

        rect1 = [(width_left_yticks + pi * (width_map + width_wspace)) / width,
                 (height_bottem_xticsk + (nrow - 1 - pj) * (height_map + height_hspace)) / height,
                 width_map / width,
                 height_map / height]

        ax = plt.axes(rect1)
        ax.set_xlim((slon, elon))
        ax.set_ylim((slat, elat))

        if i == 0:
            ax.set_yticks(yticks)
            ax.set_yticklabels(yticks_label, fontsize=sup_fontsize * 0.9, family='Times New Roman')
        else:
            ax.set_yticks(yticks)
            ax.set_yticklabels("", fontsize=sup_fontsize * 0.9, family='Times New Roman')

        ax.set_xticks(xticks)
        ax.set_xticklabels("", fontsize=sup_fontsize * 0.9, family='Times New Roman')
        im = meteva.base.add_contourf(ax, ob_list[i], add_colorbar=False, cmap=cmap, cut_colorbar=False)
        if grid: plt.grid(linestyle="--", linewidth=0.5)
        meteva.base.tool.plot_tools_adv.add_map(ax, add_county_line=add_county_line, add_worldmap=add_worldmap,
                                        sup_fontsize=sup_fontsize, title=None,
                                        linewidth=linewidth, color=color)

        tex = meteva.base.get_path(r"DD日HH时", time1)
        ix = slon + 0.02 * (elon - slon) * 5 / width_map
        iy = elat - 0.035 * (elat - slat) * 5 / height_map
        plt.text(ix, iy, tex, bbox=dict(fc='white', ec='white', pad=0), fontsize=sup_fontsize, zorder=100)
        ax_list.append(ax)

        if i == 0:
            location = [(width_left_yticks + ncol * (width_map + width_wspace) + 0.02) / width,
                        height_bottem_xticsk / height,
                        (width_colorbar - 0.02) / width,
                        height_map * nrow / height]

            colorbar_position = fig.add_axes(location)  # 位置[左,下,宽,高]
            plt.colorbar(im, cax=colorbar_position)

    ax_list_list.append(ax_list)

    for j in range(len(fo_list_list)):
        fo_list = fo_list_list[j]
        ax_list = []
        for i in range(len(fo_list)):
            dh = int(fo_list[i]["dtime"].values[0])
            time0 = meteva.base.all_type_time_to_datetime(fo_list[i]["time"].values[0])
            time1 = time0 + datetime.timedelta(hours=dh)
            pi = col_dict[time1]
            pj = j + 1

            rect1 = [(width_left_yticks + pi * (width_map + width_wspace)) / width,
                     (height_bottem_xticsk + (nrow - 1 - pj) * (height_map + height_hspace)) / height,
                     width_map / width,
                     height_map / height]

            ax = plt.axes(rect1)

            ax.set_xlim((slon, elon))
            ax.set_ylim((slat, elat))
            meteva.base.add_contourf(ax, fo_list[i], add_colorbar=False, cmap=cmap)
            if i == 0:
                ylable = meteva.base.get_path("DD\n日\nHH\n时", time0)
                ax.set_ylabel(ylable, fontsize=sup_fontsize * 0.9, rotation="horizontal", verticalalignment="center")
                ax.set_yticks(yticks)
                ax.set_yticklabels(yticks_label, fontsize=sup_fontsize * 0.9, family='Times New Roman')
            else:
                ax.set_yticks(yticks)
                ax.set_yticklabels("", fontsize=sup_fontsize * 0.9, family='Times New Roman')

            if pj == len(fo_list_list) and pi == ncol - 1:
                ax.set_xticks(xticks)
                ax.set_xticklabels(xticks_label, fontsize=sup_fontsize * 0.9, family='Times New Roman')
            elif pj == len(fo_list_list):
                ax.set_xticks(xticks[:-1])
                ax.set_xticklabels(xticks_label[:-1], fontsize=sup_fontsize * 0.9, family='Times New Roman')
            else:
                ax.set_xticks(xticks)
                ax.set_xticklabels("", fontsize=sup_fontsize * 0.9, family='Times New Roman')

            if grid: plt.grid(linestyle="--", linewidth=0.5)
            meteva.base.tool.plot_tools_adv.add_map(ax, add_county_line=add_county_line, add_worldmap=add_worldmap,
                                            sup_fontsize=sup_fontsize, title=None,
                                            linewidth=linewidth, color=color)

            tex = str(dh).zfill(3) + "H"
            ix = slon + 0.02 * (elon - slon) * 5 / width_map
            iy = elat - 0.035 * (elat - slat) * 5 / height_map
            plt.text(ix, iy, tex, bbox=dict(fc='white', ec='white', pad=0), fontsize=sup_fontsize, zorder=100)
            ax_list.append(ax)

    ax_list_list.append(ax_list)