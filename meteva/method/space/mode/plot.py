# -*- coding: utf-8 -*-
"""
Created on Wed Jan  6 16:03:10 2021

"""
import copy
import meteva
import numpy as np
import matplotlib.pyplot as plt
import math
from matplotlib.colors import BoundaryNorm
import os
from .feature_match_analyzer import get_summary


def add_map(ax, add_county_line=False, add_worldmap=True, title=None, sup_fontsize=12):
    if add_worldmap:
        meteva.base.tool.plot_tools.add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk',
                                                           grid0=None)  # "国界"
    meteva.base.tool.plot_tools.add_china_map_2basemap(ax, name="nation", edgecolor='k', lw=0.3,
                                                       encoding='gbk')  # "国界"
    meteva.base.tool.plot_tools.add_china_map_2basemap(ax, edgecolor='k', lw=0.3, encoding='gbk')  # "省界"
    if add_county_line:
        meteva.base.tool.plot_tools.add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2,
                                                           encoding='gbk')  # "省界"
    ax.set_title(title, fontsize=sup_fontsize * 0.9)
    return ax


class mfig:

    def __init__(self,nplot,map_extend,ncol = None,height  = None,width = None,dpi = 300,sup_title = None,sup_fontsize = 12,
              add_county_line = False,add_worldmap = True,title_list = None):

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
        height_hspace = sup_fontsize * 0.04

        width_wspace = height_hspace * 1.5

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
            height_all_plot = height - height_title - height_bottem_xticsk - (
                        nrow - 1) * height_hspace + sup_height_title
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
        elif r < 180:
            inte = 10
        else:
            inte = 20

        vmin = inte * (math.ceil(vmin / inte))
        vmax = inte * ((int)(vmax / inte) + 1)

        xticks = np.arange(vmin, vmax, inte)
        xticks_label = []
        xticks_label_None = []
        for x in range(len(xticks)):
            xticks_label.append(str(round(xticks[x], 6)))
            xticks_label_None.append("")
        if xticks[-1] > 0:
            xticks_label[-1] = "   " + xticks_label[-1] + "°E"
        else:
            xticks_label[-1] = "   " + xticks_label[-1] + "°W"

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
        vmax = inte * ((int)(vmax / inte) + 1)
        yticks = np.arange(vmin, vmax, inte)
        yticks_label = []
        yticks_label_None = []
        for y in range(len(yticks)):
            if yticks[y] >= 0:
                yticks_label.append(str(round(yticks[y], 6)) + "°N")
            else:
                yticks_label.append(str(round(-yticks[y], 6)) + "°S")
            yticks_label_None.append("")

        fig = plt.figure(figsize=(width, height), dpi=dpi)
        y_sup_title = (height_bottem_xticsk - 0.1 + (nrow) * (height_map + height_hspace)) / height
        if sup_title is not None:
            plt.suptitle(sup_title, x=0.6, y=y_sup_title, fontsize=sup_fontsize)
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
            elif r < 180:
                inte = 10
            else:
                inte = 20

            vmin = inte * (math.ceil(vmin / inte))
            vmax = inte * ((int)(vmax / inte) + 1)
            xticks = np.arange(vmin, vmax, inte)
            xticks_label = []
            for x in range(len(xticks)):
                xticks_label.append(str(round(xticks[x], 6)))
            if xticks[-1] > 0:
                xticks_label[-1] = "   " + xticks_label[-1] + "°E"
            else:
                xticks_label[-1] = "   " + xticks_label[-1] + "°W"
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticks_label, fontsize=sup_fontsize * 0.9, family='Times New Roman')

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
            vmax = inte * ((int)(vmax / inte) + 1)
            yticks = np.arange(vmin, vmax, inte)
            yticks_label = []
            for y in range(len(yticks)):

                if yticks[y] >= 0 and y == len(yticks) - 1:
                    yticks_label.append(str(round(yticks[y], 6)) + "°N")
                elif yticks[y] < 0 and y == 0:
                    yticks_label.append(str(round(-yticks[y], 6)) + "°S")
                elif yticks[y] == 0:
                    yticks_label.append("EQ" + "  ")
                else:
                    yticks_label.append(str(round(yticks[y], 6)) + "    ")
            ax.set_yticks(yticks)
            ax.set_yticklabels(yticks_label, fontsize=sup_fontsize * 0.9, family='Times New Roman')
            if title_list is None:
                sub_title = None
            else:
                sub_title = title_list[p]
            add_map(ax, add_county_line=add_county_line, add_worldmap=add_worldmap, sup_fontsize=sup_fontsize,
                    title=sub_title)
            ax_list.append(ax)

        self.ax_list = ax_list
        self.sup_fontsize = sup_fontsize
        self.ncol = ncol


    def add_contourf(self,i,grd,cmap ="rainbow",clevs= None,add_colorbar = True):
        ax = self.ax_list[i]
        x = grd['lon'].values
        y = grd['lat'].values
        vmax = np.max(grd.values)
        vmin = np.min(grd.values)
        cmap1,clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap,clevs=clevs,vmin=vmin,vmax = vmax)
        norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
        im = ax.contourf(x, y, np.squeeze(grd.values), levels=clevs1, cmap=cmap1,norm = norm)

        time_str = meteva.base.tool.time_tools.time_to_str(grd["time"].values[0])
        dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
        title1 = str(grd["member"].values[0]) + " " + dati_str + str(grd["dtime"].values[0]) + "H时效 "
        if "var_name" in grd.attrs.keys():
            title1 = title1 + grd.attrs["var_name"]
        ax.set_title(title1, fontsize=self.sup_fontsize* 0.9, pad=0)

        fig = plt.gcf()
        width = fig.bbox.width/fig.dpi
        height = fig.bbox.height/fig.dpi
        location = [ax.bbox.x1/fig.dpi/width+0.005, ax.bbox.y0 / fig.dpi/height, 0.01, ax.bbox.height/fig.dpi/height]

        if(add_colorbar):
            colorbar_position = fig.add_axes(location)  # 位置[左,下,宽,高]
            cb = plt.colorbar(im,cax= colorbar_position)
            cb.ax.tick_params(labelsize=self.sup_fontsize * 0.8)

    def add_mesh(self,i,grd,cmap = "rainbow",clevs = None,add_colorbar = True,matched = True):
        ax = self.ax_list[i]
        x = grd['lon'].values
        y = grd['lat'].values
        vmax = np.max(grd.values)
        vmin = np.min(grd.values)
        cmap1,clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap,clevs=clevs,vmin=vmin,vmax = vmax)
        norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
        #im = ax.pcolormesh(x, y, np.squeeze(grd.values), levels=clevs1, cmap=cmap1,norm = norm)
        im = ax.pcolormesh(x, y, np.squeeze(grd.values), cmap=cmap1, norm=norm)
        fig = plt.gcf()
        width = fig.bbox.width/fig.dpi
        height = fig.bbox.height/fig.dpi
        location = [ax.bbox.x1/fig.dpi/width+0.005, ax.bbox.y0 / fig.dpi/height, 0.01, ax.bbox.height/fig.dpi/height]

        if(add_colorbar):
            colorbar_position = fig.add_axes(location)  # 位置[左,下,宽,高]
            cb =  plt.colorbar(im,cax= colorbar_position)
            if matched :
                cticks = [-1]
                cticks.extend((np.array(clevs1[2:])+0.5).tolist())
                cticks = np.array(cticks)
                cb.set_ticks(cticks)
                clabels = ["未\n配\n对"]
                for i in range(2,len(clevs1)):
                    clabels.append(str(int(clevs1[i]+0.5)))
                    #clabels.extend((np.array(clevs1[2:])+0.5).tolist())
                cb.set_ticklabels(clabels)
            else:
                cticks=(np.array(clevs1[2:])+0.5).tolist()
                cticks = np.array(cticks)
                cb.set_ticks(cticks)
                clabels = []
                #clabels = ["未\n配\n队"]
                for i in range(2,len(clevs1)):
                    clabels.append(str(int(clevs1[i]+0.5)))
                cb.set_ticklabels(clabels)
            cb.ax.tick_params(labelsize=self.sup_fontsize * 0.8)
        time_str = meteva.base.tool.time_tools.time_to_str(grd["time"].values[0])
        dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
        title1 = str(grd["member"].values[0]) + " " + dati_str + str(grd["dtime"].values[0]) + "H时效 "
        if "var_name" in grd.attrs.keys():
            title1 = title1 + grd.attrs["var_name"]
        ax.set_title(title1, fontsize=self.sup_fontsize* 0.9, pad=0)



def plot_value_list(look_list, cmap ="rain_24h",clevs = None,save_path = None,show = False,sup_fontsize=10,dpi = 300,mfg1 = None):

    ncol = len(look_list)
    grid1 = look_list[0]["grid"]
    # grd_ob = look["grd_ob"]
    # grd_fo = look["grd_fo"]
    # grd_ob_smooth = look["grd_ob_smooth"]
    # grd_fo_smooth = look["grd_fo_smooth"]
    # vmax = np.max((np.max(grd_ob), np.max(grd_fo)))
    cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap, clevs=clevs)

    mfg1_show = True
    if mfg1 is None:
        mfg1 = mfig(2*ncol,map_extend=grid1,ncol=ncol,sup_fontsize=sup_fontsize,dpi=dpi)
    else:
        mfg1_show = False

    for i in range(ncol):
        look1 = look_list[i]
        grd = look1["grd"]
        grd_smooth = look1["grd_smooth"]
        mfg1.add_contourf(i,grd,cmap = cmap1,clevs=clevs1,add_colorbar=(i==ncol-1))
        mfg1.add_contourf(ncol + i, grd_smooth, cmap=cmap1, clevs=clevs1,add_colorbar=(i==ncol-1))

    if mfg1_show:
        if save_path is None:
            show = True
        if save_path is not None:
            meteva.base.tool.path_tools.creat_path(save_path)
            file1, extension = os.path.splitext(save_path)
            if(len(extension) ==0):
                print("save_path中没包含后缀，如.png等,未能输出至指定路径")
                return
            extension = extension[1:]
            plt.savefig(save_path,format = extension,bbox_inches='tight')
            print("图片已保存至" + save_path)
        if show:
            plt.show()
        plt.close()




def plot_value_and_label_list(look_list,cmap = "rain_24h",clevs = None,save_path = None,sup_fontsize=10,dpi = 300,show = False):
    ncol = len(look_list)
    grid1 = look_list[0]["grid"]
    mfg1 = mfig(3*ncol, map_extend=grid1, ncol=ncol, sup_fontsize=sup_fontsize, dpi=dpi)
    plot_value_list(look_list, cmap, clevs, mfg1=mfg1)
    plot_label_list(look_list, mfg1=mfg1)
    if save_path is None:
        show = True

    if save_path is not None:
        meteva.base.tool.path_tools.creat_path(save_path)
        file1, extension = os.path.splitext(save_path)
        if (len(extension) == 0):
            print("save_path中没包含后缀，如.png等,未能输出至指定路径")
            return
        extension = extension[1:]
        plt.savefig(save_path, format=extension, bbox_inches='tight')
        print("图片已保存至" + save_path)
    if show:
        plt.show()
    plt.close()

def plot_value_and_label(look,cmap = "rain_24h",clevs = None,save_path = None,sup_fontsize=10,dpi = 300,show = False):

    if isinstance(look,list):
        plot_value_and_label_list(look,cmap =cmap,clevs = clevs,save_path = save_path,sup_fontsize=sup_fontsize,dpi = dpi,show = show)
    else:
        grid1 = look["grid"]
        mfg1 = mfig(6,map_extend=grid1,ncol=2,sup_fontsize=sup_fontsize,dpi=dpi)
        plot_value(look,cmap,clevs,mfg1 = mfg1)
        plot_label(look,mfg1 = mfg1)
        if save_path is None:
            show = True

        if save_path is not None:
            meteva.base.tool.path_tools.creat_path(save_path)
            file1, extension = os.path.splitext(save_path)
            if(len(extension) ==0):
                print("save_path中没包含后缀，如.png等,未能输出至指定路径")
                return
            extension = extension[1:]
            plt.savefig(save_path,format = extension,bbox_inches='tight')
            print("图片已保存至" + save_path)
        if show:
            plt.show()
        plt.close()


def plot_value(look, cmap ="rain_24h",clevs = None,save_path = None,show = False,sup_fontsize=10,dpi = 300,mfg1 = None):
    grid1 = look["grid"]
    grd_ob = look["grd_ob"]
    grd_fo = look["grd_fo"]
    grd_ob_smooth = look["grd_ob_smooth"]
    grd_fo_smooth = look["grd_fo_smooth"]
    vmax = np.max((np.max(grd_ob), np.max(grd_fo)))
    cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap, clevs=clevs, vmin=0, vmax=vmax)

    mfg1_show = True
    if mfg1 is None:
        mfg1 = mfig(4,map_extend=grid1,ncol=2,sup_fontsize=sup_fontsize,dpi=dpi)
    else:
        mfg1_show = False

    mfg1.add_contourf(0,grd_ob,cmap = cmap1,clevs=clevs1,add_colorbar=False)
    mfg1.add_contourf(1, grd_fo, cmap=cmap1, clevs=clevs1)
    mfg1.add_contourf(2, grd_ob_smooth, cmap=cmap1, clevs=clevs1,add_colorbar=False)
    mfg1.add_contourf(3, grd_fo_smooth, cmap=cmap1, clevs=clevs1)

    if mfg1_show:
        if save_path is None:
            show = True
        if save_path is not None:
            meteva.base.tool.path_tools.creat_path(save_path)
            file1, extension = os.path.splitext(save_path)
            if(len(extension) ==0):
                print("save_path中没包含后缀，如.png等,未能输出至指定路径")
                return
            extension = extension[1:]
            plt.savefig(save_path,format = extension,bbox_inches='tight')
            print("图片已保存至" + save_path)
        if show:
            plt.show()
        plt.close()


def add_pts(ax,map_extend,line_dict,nmatched,line_width = None,sup_fontsize=10,dpi = 300):
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
        line_width = map_width *  0.2

    for key in line_dict.keys():
        if key <= nmatched:
            c = "r"
        else:
            c = "k"
        point0 = line_dict[key]
        point = np.zeros([point0.shape[0]+1,point0.shape[1]])
        point[:-1,:] = point0[:,:]
        point[-1,:] = point0[0,:]
        ax.plot(point[:, 0], point[:, 1], "k", linewidth=line_width)
        max_j = np.argmax(point[:,1])
        dlat = 0.1 * rlon / map_width
        lat = point[max_j,1] + dlat * 0.2
        lat1 = point[max_j,1] + dlat * 1.2
        str1 = str(key)
        dlon = 0.1 * len(str1) * rlon / map_width
        if lat1 > elat:
            min_j = np.argmin(point[:,1])
            lon = point[min_j,0]
            lon = min(lon,elon - dlon)
            lon = max(lon,slon + dlon)
            lat = point[min_j,1] - dlat * 0.2
            ax.text(lon,lat,str(key),c = c,horizontalalignment='center',fontweight='bold',
                    verticalalignment = "top")
        else:
            lon = point[max_j,0]
            lon = min(lon,elon - dlon)
            lon = max(lon,slon + dlon)
            ax.text(lon,lat,str(key),c = c,horizontalalignment='center',fontweight='bold')



    ax.set_xlim(slon,elon)
    ax.set_ylim(slat,elat)



def plot_label_list(look_list,ncol = None,save_path = None,show = False,sup_fontsize=10,dpi = 300,mfg1 = None):

    nlook = len(look_list)
    grid1 = look_list[0]["grid"]
    start_ax = 2 * nlook
    mfg1_show = True

    if mfg1 is None:
        mfg1 = mfig(nlook,map_extend=grid1,ncol=ncol,sup_fontsize=sup_fontsize,dpi=dpi)
        start_ax = 0
        ncol = mfg1.ncol
    else:
        mfg1_show = False
        ncol = nlook



    vmax = 1
    label_list = []
    for i in range(nlook):
        look =look_list[i]
        nmatch = 1000
        if "match_count" in look.keys():
            nmatch = look["match_count"]
        data_labeled = look['grd_label'].copy()
        data_labeled.values[data_labeled.values>nmatch] = -1
        label_list.append(data_labeled)
        vmax1 = np.max(data_labeled)
        if vmax1 > vmax:
            vmax = vmax1

    cmap2, clevs2 = meteva.base.tool.color_tools.def_cmap_clevs(cmap="mode", clevs=None, vmin=0, vmax=vmax)

    for i in range(nlook):
        look = look_list[i]
        nmatch = 1000
        if "match_count" in look.keys():
            matched = True
            nmatch = look["match_count"]
        else:
            matched = False

        mfg1.add_mesh(start_ax+i,label_list[i],cmap=cmap2,clevs=clevs2,add_colorbar=((i+1)%ncol==0),matched = matched)

        label_count = look["grd_features"]["label_count"]
        pts_dict = {}
        for j in range(label_count):
            feature = meteva.method.feature_axis(look, j + 1, None)
            if feature is not None:
                pts = feature["pts"]
                pts_dict[j+1] =pts
        add_pts(mfg1.ax_list[start_ax + i],look["grid"],pts_dict,nmatch)

    if mfg1_show:
        if save_path is None:
            show = True
        if save_path is not None:
            meteva.base.tool.path_tools.creat_path(save_path)
            file1, extension = os.path.splitext(save_path)
            if(len(extension) ==0):
                print("save_path中没包含后缀，如.png等,未能输出至指定路径")
                return
            extension = extension[1:]
            plt.savefig(save_path,format = extension,bbox_inches='tight')
            print("图片已保存至" + save_path)
        if show:
            plt.show()
        plt.close()

def plot_label(look,save_path = None,show = False,sup_fontsize=10,dpi = 300,mfg1 = None):

    grid1 = look["grid"]
    start_ax = 4
    mfg1_show = True

    if mfg1 is None:
        mfg1 = mfig(2,map_extend=grid1,ncol=2,sup_fontsize=sup_fontsize,dpi=dpi)
        start_ax = 0
    else:
        mfg1_show = False

    nmatch = 1000
    matched = False
    data_Xlabeled = look['grd_ob_label'].copy()
    data_Ylabeled = look['grd_fo_label'].copy()
    if "match_count" in look.keys():
        nmatch = 0
        if len(look["label_list_matched"])>0:
            nmatch = np.max(np.array(look["label_list_matched"]))
        matched = True

        unmatched = look["unmatched"]["ob"]
        for id in unmatched:
            data_Xlabeled.values[data_Xlabeled.values ==id] = -1
        unmatched = look["unmatched"]["fo"]
        for id in unmatched:
            data_Ylabeled.values[data_Ylabeled.values ==id] = -1

    vmax = np.max((np.max(data_Xlabeled), np.max(data_Ylabeled))) + 1
    cmap2, clevs2 = meteva.base.tool.color_tools.def_cmap_clevs(cmap="mode", clevs=None, vmin=0, vmax=vmax)

    mfg1.add_mesh(start_ax,data_Xlabeled,cmap=cmap2,clevs=clevs2,add_colorbar=False,matched = matched)
    mfg1.add_mesh(start_ax+1, data_Ylabeled, cmap=cmap2, clevs=clevs2,add_colorbar=True,matched = matched)

    #ax_list = plot_2d_grid_list([data_Xlabeled, data_Ylabeled],type="mesh",
    #            cmap = "mode", vmax = np.max((np.max(data_Xlabeled), np.max(data_Ylabeled)))+1,ncol=2)
    nob = look["grd_ob_features"]["label_count"]

    pts_dict = {}
    for i in range(nob):
        feature = meteva.method.feature_axis(look, i + 1, "ob")
        pts = feature["pts"]
        pts_dict[i+1] =pts
    add_pts(mfg1.ax_list[start_ax+0],look["grid"],pts_dict,nmatch)

    #nfo = look["grd_fo_features"]["label_count"]
    label_list_fo = look["label_list_fo"]
    pts_dict = {}
    for id in label_list_fo:
        feature = meteva.method.feature_axis(look, id, "fo")
        pts = feature["pts"]
        pts_dict[id] = pts
    add_pts(mfg1.ax_list[start_ax+1],look["grid"],pts_dict,nmatch)
    if mfg1_show:
        if save_path is None:
            show = True
        if save_path is not None:
            meteva.base.tool.path_tools.creat_path(save_path)
            file1, extension = os.path.splitext(save_path)
            if(len(extension) ==0):
                print("save_path中没包含后缀，如.png等,未能输出至指定路径")
                return
            extension = extension[1:]
            plt.savefig(save_path,format = extension,bbox_inches='tight')
            print("图片已保存至" + save_path)
        if show:
            plt.show()
        plt.close()


def plot_interest(interest,save_path = None,show = False):
    shape = list(interest["interest"].shape)
    shape[2] = shape[2]+1
    dat = np.zeros(shape)
    dat[:,:,:-1] = interest["interest"][:,:,:]
    dat[:,:,-1] = interest["total_interest"][:,:]
    p_list = copy.deepcopy(interest["properties"])
    p_list.append("total interest")
    name_list_dict = {
        "fo_label_id": interest["label_list_fo"],
        "ob_label_id": interest["label_list_ob"],
        "properties":p_list
    }
    meteva.base.tool.plot_tools.mesh(dat, name_list_dict=name_list_dict, annot=2, axis_x="ob_label_id",
                             axis_y="fo_label_id",save_path = save_path,show = show,ncol = 2)

def plot_feature(feature,save_path = None,show = False,dpi = 100):

    feature = get_summary(feature)
    sup_fontsize = 10
    row = 43
    col1 = 10
    label_list_matched = feature["label_list_matched"]
    nmatch = len(label_list_matched)
    col2 = 6 + nmatch
    col = max(col1,col2)

    width = col * sup_fontsize * 0.08
    height = row * sup_fontsize * 0.02
    fig = plt.figure(figsize=(width,height),dpi =dpi)
    axis = plt.axes([0,0,1,1])

    axis.axes.set_axis_off()
    axis.set_xlim(0,col)
    axis.set_ylim(0,row)
    plt.hlines(0.05, 0, col, "k", linewidth=0.5)
    for i in range(1,14):
        plt.hlines(i,2,col,"k",linewidth = 0.5,linestyles="--")
    plt.hlines(14,0,col,"k",linewidth = 0.5)

    for i in range(14,22):
        plt.hlines(i,2  + 2*(i%2),col,"k",linewidth = 0.5,linestyles="--")
    plt.hlines(22,0,col,"k",linewidth = 0.5)

    for i in range(22,36):
        plt.hlines(i,2  + 2*(i%2),col,"k",linewidth = 0.5,linestyles="--")
    plt.hlines(36,0,col,"k",linewidth = 0.5)
    plt.hlines(37,0,col,"k",linewidth = 0.5)
    plt.hlines(38,0,col,"k",linewidth = 1,linestyles="-")
    plt.hlines(39,0,col,"k",linewidth = 0.5,linestyles="--")
    plt.hlines(40,2,col,"k",linewidth = 0.5,linestyles="-")
    plt.hlines(41, 2, col, "k", linewidth=0.5, linestyles="--")
    plt.hlines(42,0,col,"k",linewidth = 1,linestyles="-")
    row1 = row-1+0.2
    plt.text(0,row1,"起报时间:"+feature["time"],fontsize=sup_fontsize)
    plt.text(3,row1,"预报时效:"+str(feature["dtime"]),fontsize=sup_fontsize)
    plt.text(6,row1,"成功匹配目标数:"+str(nmatch),fontsize=sup_fontsize)
    plt.text(0,row1-1,"整场目标预报评价",fontsize=sup_fontsize)
    plt.text(0,row1-1,"整场目标预报评价",fontsize=sup_fontsize)

    keys = ["Hits","Misses","False alarms","Correct negatives"]
    values = feature["feature_table"]["contingency_table_yesorno"]

    for i in range(len(keys)):
        plt.text(i*2+2,row1-1,keys[i],fontsize=sup_fontsize)
        plt.text(i*2+2,row1-2, int(values[keys[i]]), fontsize=sup_fontsize)


    keys = ["ets","pod","pofd","far","hss"]
    values = feature["feature_table"]["score"]
    for i in range(len(keys)):
        plt.text(i*2,row1-3,keys[i],fontsize=sup_fontsize)
        plt.text(i*2, row1-4, "{:.3f}".format(values[keys[i]]), fontsize=sup_fontsize)


    plt.text(0, row1-5, "逐个目标属性检验", fontsize=sup_fontsize)

    for i in range(nmatch):
        id = label_list_matched[i]
        plt.text(6+i, row1-5, "目标"+str(id), fontsize=sup_fontsize)

    plt.text(0, row1-6, "目标整体相似度", fontsize=sup_fontsize)
    for i in range(nmatch):
        plt.text(6+i, row1-6, "{:.3f}".format(feature["interester"][i]), fontsize=sup_fontsize)

    plt.text(0, row1-7, "目标轴属性", fontsize=sup_fontsize)

    names = ["主轴长度","次轴长度","主轴倾角","矩形窗_x0","矩形窗_y0","矩形窗_x1","矩形窗_y1","质心_x","质心_y","面积","中位数强度"]
    for i in range(len(names)):
        plt.text(2, row1-(7+i*2), names[i], fontsize=sup_fontsize)
        plt.text(4, row1-(7+i*2), "观测", fontsize=sup_fontsize)
        plt.text(4, row1-(8+i*2), "预报", fontsize=sup_fontsize)


    for i in range(nmatch):
        keys1 = ["ob","fo"]
        for j in range(2):
            id = label_list_matched[i]
            values = feature[id]["feature_axis"][keys1[j]]

            plt.text(6+i, row1-(7+j), "{:.3f}".format(values["lengths"]["MajorAxis"]), fontsize=sup_fontsize)
            plt.text(6+i, row1-(9+j), "{:.3f}".format(values["lengths"]["MinorAxis"]), fontsize=sup_fontsize)
            plt.text(6+i, row1-(11+j), "{:.3f}".format(values["OrientationAngle"]["MajorAxis"]), fontsize=sup_fontsize)
            plt.text(6+i, row1-(13+j), "{:.3f}".format(values["window"]["x0"]), fontsize=sup_fontsize)
            plt.text(6+i, row1-(15+j), "{:.3f}".format(values["window"]["y0"]), fontsize=sup_fontsize)
            plt.text(6+i, row1-(17+j), "{:.3f}".format(values["window"]["x1"]), fontsize=sup_fontsize)
            plt.text(6+i, row1-(19+j), "{:.3f}".format(values["window"]["y1"]), fontsize=sup_fontsize)

            values = feature[id]["feature_props"][keys1[j]]
            plt.text(6+i, row1-(21+j), "{:.3f}".format(values["centroid"]["x"]), fontsize=sup_fontsize)
            plt.text(6+i, row1-(23+j), "{:.3f}".format(values["centroid"]["y"]), fontsize=sup_fontsize)
            plt.text(6+i, row1-(25+j), "{:.3f}".format(values["area"]), fontsize=sup_fontsize)
            plt.text(6+i, row1-(27+j), "{:.3f}".format(values["intensity"][4]), fontsize=sup_fontsize)



    names = ["质心距离","角度差","面积比","重叠面积比例","bearing方位角","bdelta距离","haus距离","medMiss","medFalseAlarm","msdMiss",
             "msdFalseAlarm","ph距离","fom","minsep最近距离"]
    keys = ["cent_dist","angle_diff","area_ratio","int_area","bearing",
            "bdelta","haus","medMiss","medFalseAlarm","msdMiss","msdFalseAlarm","ph","fom","minsep"]

    for i in range(len(names)):
        plt.text(2, row1 - (29+i), names[i], fontsize=sup_fontsize)

        for j in range(nmatch):
            id = label_list_matched[j]
            plt.text(6+j,row1-(29+i), "{:.3f}".format(feature[id]["feature_comps"][keys[i]]), fontsize=sup_fontsize)

    plt.text(0, row1-21, "目标面属性", fontsize=sup_fontsize)
    plt.text(0, row1-29, "目标属性对比", fontsize=sup_fontsize)
    if save_path is None:
        show = True

    if save_path is not None:
        meteva.base.tool.path_tools.creat_path(save_path)
        file1, extension = os.path.splitext(save_path)
        if (len(extension) == 0):
            print("save_path中没包含后缀，如.png等,未能输出至指定路径")
            return
        extension = extension[1:]
        plt.savefig(save_path, format=extension, bbox_inches='tight')
        print("图片已保存至" + save_path)
    if show:
        plt.show()
    plt.close()




