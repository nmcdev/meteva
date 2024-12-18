import os
import numpy as np
import pkg_resources
import meteva
import matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
from matplotlib.colors import BoundaryNorm
from meteva.base import IV

from matplotlib.collections import LineCollection
import matplotlib.patches as patches
import datetime
import copy

def get_isoline_set(grd):
    values = grd.values
    grid_values = np.squeeze(values)
    vmax = math.ceil(max(grid_values.flatten()))
    vmin = math.ceil(min(grid_values.flatten()))

    dif = (vmax - vmin) / 10.0
    if dif == 0:
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
    return vmin,vmax,inte

def readshapefile(shapefile, default_encoding='utf-8'):
    """
    """
    import shapefile as shp
    from shapefile import Reader

    if not os.path.exists('%s.shp'%shapefile):
        raise IOError('cannot locate %s.shp'%shapefile)
    if not os.path.exists('%s.shx'%shapefile):
        raise IOError('cannot locate %s.shx'%shapefile)
    if not os.path.exists('%s.dbf'%shapefile):
        raise IOError('cannot locate %s.dbf'%shapefile)
    # open shapefile, read vertices for each object, convert
    # to map projection coordinates (only works for 2D shape types).
    try:
        shp.default_encoding = default_encoding
        shf = Reader(shapefile, encoding=default_encoding)
    except:
        try:
            shp.default_encoding = "gbk"
            shf = Reader(shapefile, encoding="gbk")
        except:
            raise IOError('error reading shapefile %s.shp' % shapefile)

    fields = shf.fields
    coords = []; attributes = []

    shptype = shf.shapes()[0].shapeType
    bbox = shf.bbox.tolist()
    info = (shf.numRecords,shptype,bbox[0:2]+[0.,0.],bbox[2:]+[0.,0.])
    npoly = 0
    for shprec in shf.shapeRecords():
        shp = shprec.shape; rec = shprec.record
        npoly = npoly + 1
        #print(shptype)

        if shptype != shp.shapeType:
            #print(shptype)
            #print(shapefile)
            continue
            #raise ValueError('readshapefile can only handle a single shape type per file')
        if shptype not in [1,3,5,8,13,15]:
            raise ValueError('readshapefile can only handle 2D shape types')
        verts = shp.points
        if shptype in [1,8]: # a Point or MultiPoint shape.
            lons, lats = list(zip(*verts))
            if max(lons) > 721. or min(lons) < -721. or max(lats) > 90.01 or min(lats) < -90.01:
                raise ValueError("经纬度范围超出可能值范围")
            # if latitude is slightly greater than 90, truncate to 90
            lats = [max(min(lat, 90.0), -90.0) for lat in lats]
            if len(verts) > 1: # MultiPoint
                x = lons
                y = lats
                coords.append(list(zip(x,y)))
            else: # single Point
                x = lons[0]
                y = lats[0]
                coords.append((x,y))
            attdict={}
            for r,key in zip(rec,fields[1:]):
                attdict[key[0]]=r
            attributes.append(attdict)
        else: # a Polyline or Polygon shape.
            parts = shp.parts.tolist()
            ringnum = 0
            for indx1,indx2 in zip(parts,parts[1:]+[len(verts)]):
                ringnum = ringnum + 1
                lons, lats = list(zip(*verts[indx1:indx2]))
                if max(lons) > 721. or min(lons) < -721. or max(lats) > 90.01 or min(lats) < -90.01:
                    raise ValueError("经纬度范围超出可能值范围")
                # if latitude is slightly greater than 90, truncate to 90
                lats = [max(min(lat, 90.0), -90.0) for lat in lats]
                #x, y = mp.projtran(lons, lats)  #此处引入投影
                x = lons
                y = lats
                coords.append(list(zip(x,y)))
                attdict={}
                for r,key in zip(rec,fields[1:]):
                    attdict[key[0]]=r
                # add information about ring number to dictionary.
                attdict['RINGNUM'] = ringnum
                attdict['SHAPENUM'] = npoly
                attributes.append(attdict)
    # draw shape boundaries for polylines, polygons  using LineCollection.

    return coords


def set_customized_shpfile_list(shpfile_list = None):
    if shpfile_list is None:
        meteva.base.customized_basemap_list = None
    else:
        meteva.base.customized_basemap_list = []
        for shpfile_filename in shpfile_list:
            if shpfile_filename.find("/") <0 and shpfile_filename.find("\\") <0:
                shpfile = pkg_resources.resource_filename(
                    'meteva', "resources/maps/" + shpfile_filename)

                meteva.base.customized_basemap_list.append(shpfile)
            else:
                meteva.base.customized_basemap_list.append(shpfile_filename)
    #print(meteva.base.customized_basemap_list)

def add_china_map_2basemap(ax,name ="province", facecolor='none',
                           edgecolor='c', lw=2, encoding='utf-8',zorder = 20, **kwargs):
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
    if meteva.base.customized_basemap_list is None:
        # names = {'world':"worldmap",'nation': "bou1_4p", 'province': "Province",
        #          'county': "BOUNT_poly", 'river': "hyd1_4p",
        #          'river_high': "hyd2_4p"}
        #
        # names = {'world':"worldmap",'nation': "NationalBorder", 'province': "Province",
        #          'county': "BOUNT_poly", 'river': "hyd1_4p",
        #          'river_high': "hyd2_4p"}
        #     # get shape file and information
        names = {'world':"worldmap",'nation': "NationalBorder", 'province': "Province",
                 'county': "BOUL_X", 'river': "hyd1_4p",
                 'river_high': "hyd2_4p",'world360':"worldmap360"}
        shpfile = pkg_resources.resource_filename(
            'meteva', "resources/maps/" + names[name])
        #print(shpfile)

        shp1 = readshapefile(shpfile, default_encoding=encoding)
        lines = LineCollection(shp1,antialiaseds=(1,),zorder=zorder)
        lines.set_color(edgecolor)
        lines.set_linewidth(lw)
        lines.set_label('_nolabel_')
        ax.add_collection(lines)
    else:
        for shpfile in meteva.base.customized_basemap_list:
            #print(shpfile)

            try:
                shp1 = readshapefile(shpfile, default_encoding=encoding)
                lines = LineCollection(shp1,antialiaseds=(1,),zorder=zorder)
                lines.set_color(edgecolor)
                lines.set_linewidth(lw)
                lines.set_label('_nolabel_')
                ax.add_collection(lines)
            except:
                if encoding =="gbk":
                    encoding ="utf-8"
                elif encoding == "utf-8":
                    encoding = "gbk"

                shp1 = readshapefile(shpfile, default_encoding=encoding)
                lines = LineCollection(shp1, antialiaseds=(1,), zorder=zorder)
                lines.set_color(edgecolor)
                lines.set_linewidth(lw)
                lines.set_label('_nolabel_')
                ax.add_collection(lines)

def contourf_xz(grd,subplot = "member",sup_title = None,title = None,save_path = None,
                            save_dir = None,
                            clevs = None,cmap = "rainbow",show = False,dpi =300,
                      sup_fontsize = 12,width = None,height = None,
                    ncol = None,extend = None,    **kwargs):

    lats = grd["lat"].values
    if lats.size>1:
        print("size of latitude coords in griddata is bigger than one, plot failed,if you want to plot, transform gridata to have one one latitude")
        return

    split = ["member", "time", "dtime"]
    if subplot is not None:
        subplot = [subplot]
        for s in subplot:
            split.remove(s)
    grd_list = meteva.base.split_grd(grd, used_coords=split)

    if not isinstance(save_path,list):
        save_path = [save_path]
    if len(grd_list)>1:
        if len(save_path) != len(grd_list):
            if save_dir is None:
                print("the number of output figures is different from the numbers of save_path")
            else:
                save_path = None

    for i in range(len(grd_list)):
        grd1 = grd_list[i]
        if sup_title is None:
            data_name = grd1["member"].values[0]

            if isinstance(grd1["time"].values[0],np.datetime64):
                time_str = meteva.base.tool.time_tools.all_type_time_to_str(grd1["time"].values[0])
                dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
            else:
                dati_str = ""
            dtime_str = str(int(grd1["dtime"].values[0]))
            if subplot == ["time"]:
                sup_title1 = str(data_name) +  "_" + dtime_str + "H时效"
            elif subplot == ["dtime"]:
                sup_title1 = str(data_name) +  "_" + dati_str
            elif subplot == ["member"]:
                sup_title1 =  dati_str +"_"+ dtime_str + "H时效"
            else:
                sup_title1 = None
        else:
            if isinstance(sup_title, list):
                sup_title1 = sup_title[i]
            else:
                sup_title1 = sup_title

        if subplot is None:
            grd_list1 = [grd1]
        else:
            grd_list1 = meteva.base.split_grd(grd1, used_coords=subplot)

        len1 = len(grd_list1)
        if title is not None:
            if isinstance(title, list):
                title1 = title[i * len1:i * len1 + len1]
            else:
                title1 = title
        else:
            if subplot is not None:
                grd_list1 = meteva.base.split_grd(grd1, used_coords=subplot)
            else:
                grd_list1 = [grd1]
            ng = len(grd_list1)
            title1 = []
            for kk in range(len(grd_list1)):
                grd2 = grd_list1[kk]

                data_name = grd2["member"].values[0]

                if isinstance(grd2["time"].values[0], np.datetime64):
                    time_str = meteva.base.tool.time_tools.all_type_time_to_str(grd2["time"].values[0])
                    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
                else:
                    dati_str = ""
                dtime_str = str(int(grd2["dtime"].values[0]))
                if subplot == ["time"]:
                    title00 = dati_str
                elif subplot == ["dtime"]:
                    title00 = dtime_str + "H时效 "
                elif subplot == ["member"]:
                    title00 = data_name
                else:
                    title00 = str(data_name) + "_" + dati_str + "_" + dtime_str + "H时效"
                title1.append(title00)

        data_array = grd1.values.squeeze()
        name_list_dict = {}
        for coords in ["member","level","time","dtime","lon","lat"]:
            values = grd1[coords].values
            if values.size>1:
                name_list_dict[coords] = values

        if save_path is not None:
            save_path1=save_path[i]
        else:
            if save_dir is not None:
                save_path1 = save_dir +"/"+ sup_title1+".png"
            else:
                save_path1 = None

        mesh_contourf("contourf",data_array,name_list_dict,axis_x="lon",axis_y="level",save_path = save_path1,
                     sup_title = sup_title1,title= title1,
                      clevs = clevs,cmap = cmap,show = show,dpi =dpi,
                    width = width,height = height,sup_fontsize = sup_fontsize,
                    ncol = ncol,extend = extend,**kwargs)


def contourf_yz(grd,subplot = "member",sup_title = None,title = None,save_path = None,
                save_dir = None,
                clevs=None, cmap="rainbow", show=False, dpi=300,
                sup_fontsize=12, width=None, height=None,
                ncol=None, extend=None,
                **kwargs):

    lons = grd["lon"].values
    if lons.size>1:
        print("size of longitude coords in griddata is bigger than one, plot failed,if you want to plot, transform gridata to have one one longitude")
        return

    split = ["member", "time", "dtime"]
    if subplot is not None:
        subplot = [subplot]
        for s in subplot:
            split.remove(s)
    grd_list = meteva.base.split_grd(grd, used_coords=split)

    if not isinstance(save_path,list):
        save_path = [save_path]
    if len(grd_list)>1:
        if len(save_path) != len(grd_list):
            if save_dir is None:
                print("the number of output figures is different from the numbers of save_path")
            else:
                save_path = None

    for i in range(len(grd_list)):
        grd1 = grd_list[i]
        if sup_title is None:
            data_name = grd1["member"].values[0]

            if isinstance(grd1["time"].values[0],np.datetime64):
                time_str = meteva.base.tool.time_tools.all_type_time_to_str(grd1["time"].values[0])
                dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
            else:
                dati_str = ""
            dtime_str = str(int(grd1["dtime"].values[0]))
            if subplot == ["time"]:
                sup_title1 = str(data_name) +  "_" + dtime_str + "H时效"
            elif subplot == ["dtime"]:
                sup_title1 = str(data_name) +  "_" + dati_str
            elif subplot == ["member"]:
                sup_title1 =  dati_str +"_"+ dtime_str + "H时效"
            else:
                sup_title1 = None
        else:
            if isinstance(sup_title, list):
                sup_title1 = sup_title[i]
            else:
                sup_title1 = sup_title

        if subplot is None:
            grd_list1 = [grd1]
        else:
            grd_list1 = meteva.base.split_grd(grd1, used_coords=subplot)

        len1 = len(grd_list1)
        if title is not None:
            if isinstance(title, list):
                title1 = title[i * len1:i * len1 + len1]
            else:
                title1 = title
        else:
            if subplot is not None:
                grd_list1 = meteva.base.split_grd(grd1, used_coords=subplot)
            else:
                grd_list1 = [grd1]
            ng = len(grd_list1)
            title1 = []
            for kk in range(len(grd_list1)):
                grd2 = grd_list1[kk]

                data_name = grd2["member"].values[0]

                if isinstance(grd2["time"].values[0], np.datetime64):
                    time_str = meteva.base.tool.time_tools.all_type_time_to_str(grd2["time"].values[0])
                    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
                else:
                    dati_str = ""
                dtime_str = str(int(grd2["dtime"].values[0]))
                if subplot == ["time"]:
                    title00 = dati_str
                elif subplot == ["dtime"]:
                    title00 = dtime_str + "H时效 "
                elif subplot == ["member"]:
                    title00 = str(data_name)
                else:
                    title00 = str(data_name) + "_" + dati_str + "_" + dtime_str + "H时效"
                title1.append(title00)

        data_array = grd1.values.squeeze()
        name_list_dict = {}
        for coords in ["member","level","time","dtime","lon","lat"]:
            values = grd1[coords].values
            if values.size>1:
                name_list_dict[coords] = values

        if save_path is not None:
            save_path1=save_path[i]
        else:
            if save_dir is not None:
                save_path1 = save_dir+"/" + sup_title1+".png"
            else:
                save_path1 = None
        mesh_contourf("contourf",data_array,name_list_dict,axis_x="lat",axis_y="level",save_path = save_path1,
                     sup_title = sup_title1,  clevs = clevs,cmap = cmap,show = show,dpi =dpi,
                    width = width,height = height,sup_fontsize = sup_fontsize,
                    ncol = ncol,extend = extend,
        title= title1,**kwargs)



def contourf_xy(grd,save_path = None,title = None,clevs= None,cmap ="rainbow",add_county_line = False,add_worldmap =False,show = False,dpi = 300,
                     sup_fontsize = 10,height = None,width = None,subplot = None,ncol = None,sup_title = None,clip= None,add_minmap= None,extend = None,
                save_dir = None):
    contourf_2d_grid(grd,save_path = save_path,title = title,clevs= clevs,cmap =cmap,add_county_line = add_county_line,
                     add_worldmap =add_worldmap,show = show,dpi = dpi,
                     sup_fontsize = sup_fontsize,height = height,width = width,subplot = subplot,ncol = ncol,
                     sup_title = sup_title,clip= clip,add_minmap= add_minmap,extend = extend,save_dir = save_dir)

def contourf_2d_grid(grd,save_path = None,title = None,clevs= None,cmap ="rainbow",add_county_line = False,add_worldmap =False,show = False,dpi = 300,
                     sup_fontsize = 10,height = None,width = None,subplot = None,ncol = None,sup_title = None,clip= None,add_minmap= None,extend = None,
                     save_dir = None):

    vmin = 10e30
    vmax = -10e30
    if isinstance(grd,list):
        grd_list = grd
        for i in range(len(grd_list)):
            vmax1 = np.nanmax(grd_list[i].values)
            vmin1 = np.nanmin(grd_list[i].values)
            if vmax1 > vmax:vmax = vmax1
            if vmin1 > vmin:vmin = vmin1
    else:
        vmin = np.nanmin(grd.values)
        vmax = np.nanmax(grd.values)
        split = ["member","level", "time", "dtime"]
        if subplot is not None:
            subplot = [subplot]
            for s in subplot:
                split.remove(s)
        grd_list = meteva.base.split_grd(grd, used_coords=split)

    if not isinstance(save_path,list):
        save_path = [save_path]
    if len(grd_list)>1:
        if len(save_path) != len(grd_list):
            if save_dir is None:
                print("the number of output figures is different from the numbers of save_path")
            else:
                save_path = None
    for i in range(len(grd_list)):
        grd1 = grd_list[i]
        if sup_title is None:
            level_str = str(int(grd1["level"].values[0]))
            data_name = grd1["member"].values[0]
            time_str = meteva.base.tool.time_tools.all_type_time_to_str(grd1["time"].values[0])
            dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
            dtime_str = str(int(grd1["dtime"].values[0]))
            if subplot == ["level"]:
                sup_title1 = str(data_name) + "_" + dati_str + dtime_str + "H时效"
            elif subplot == ["time"]:
                sup_title1 = str(data_name) + "_Level" + level_str + "_" + dtime_str + "H时效"
            elif subplot == ["dtime"]:
                sup_title1 = str(data_name) + "_Level" + level_str + "_" + dati_str
            elif subplot == ["member"]:
                sup_title1 = " Level" + level_str + "_" + dati_str + dtime_str + "H时效"
            else:
                sup_title1 =None
        else:
            if isinstance(sup_title,list):
                sup_title1 = sup_title[i]
            else:
                sup_title1 = sup_title


        if subplot is None:
            grd_list1 = [grd1]
        else:
            grd_list1 = meteva.base.split_grd(grd1, used_coords=subplot)

        len1 = len(grd_list1)
        if title is not None:
            if isinstance(title,list):
                title1 = title[i * len1:i*len1+len1]
            else:
                title1 = title
        else:
            if subplot is not None:
                grd_list1 = meteva.base.split_grd(grd1, used_coords=subplot)
            else:
                grd_list1 = [grd1]
            ng = len(grd_list1)
            title1 = []
            for kk in range(len(grd_list1)):
                grd2 = grd_list1[kk]
                level_str = str(int(grd2["level"].values[0]))
                data_name = grd2["member"].values[0]
                time_str = meteva.base.tool.time_tools.all_type_time_to_str(grd2["time"].values[0])
                dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
                dtime_str = str(int(grd2["dtime"].values[0]))
                if subplot == ["level"]:
                    title00 =level_str
                elif subplot == ["time"]:
                    title00 = dati_str
                elif subplot == ["dtime"]:
                    title00 = dtime_str +  "H时效 "
                elif subplot == ["member"]:
                    title00 = str(data_name)
                else:
                    title00 =str(data_name) +"_L"+level_str+"_"+ dati_str+"_"+dtime_str+"H时效"
                title1.append(title00)

        if save_path is not None:
            save_path1 = save_path[i]
        else:
            if save_dir is not None:
                save_path1 = save_dir + "/" + sup_title1+".png"
            else:
                save_path1 = None
        plot_2d_grid_list(grd_list1,type = "contour",save_path= save_path1,title= title1,clevs=clevs,cmap=cmap,vmax = vmax,vmin = vmin,add_county_line= add_county_line,
                      add_worldmap = add_worldmap,show=show,dpi = dpi,sup_fontsize = sup_fontsize,height= height,width = width,ncol= ncol,
                      sup_title = sup_title1,clip= clip,add_minmap=add_minmap,extend=extend)



def plot_2d_grid_list(grd_list,type = "contour",save_path = None,title = None,clevs= None,cmap ="rainbow",add_county_line = False,add_worldmap =False,show = False,dpi = 300,
                     sup_fontsize = 10,height = None,width = None,ncol = None,vmax = None,vmin = None, sup_title = None,clip= None,add_minmap = None,extend = None,grid = False):


    if save_path is None:
        show = True

    x = grd_list[0]['lon'].values
    slon = x[0]
    elon = x[-1]
    y = grd_list[0]['lat'].values
    slat = y[0]
    elat = y[-1]
    rlon = x[-1] - x[0]
    rlat = y[-1] - y[0]



    height_title = sup_fontsize * 0.1
    height_bottem_xticsk = sup_fontsize * 0.05
    height_hspace = sup_fontsize * 0.03

    width_wspace = height_hspace

    width_colorbar = 0.5
    width_left_yticks = sup_fontsize * 0.1

    nplot = len(grd_list)
    if ncol is None:
        match_list = []
        for i in range(nplot,0,-1):
            ncol = i
            nrow = int(math.ceil(len(grd_list) / ncol))
            rate = ncol * rlon/(nrow * rlat)
            if rate <2 and rate > 9/16:
                match_list.append([i,ncol * nrow - nplot])
        if len(match_list)  ==0:
            ncol = nplot
        else:
            match_array = np.array(match_list)
            min_index = np.argmin(match_array[:,1])
            ncol = match_array[min_index,0]
    nrow = int(math.ceil(nplot / ncol))

    if width is None and height is None:
        width = 8

    if width is None:
        height_all_plot = height - height_title - height_bottem_xticsk - (nrow-1) * height_hspace
        height_map = height_all_plot / nrow
        width_map = height_map * rlon / rlat
        width_all_plot = width_map * ncol + (ncol-1) * width_wspace
        width = width_all_plot + width_colorbar + width_left_yticks
    else:
        width_all_plot = width - width_colorbar - width_left_yticks - (ncol - 1) * width_wspace
        width_map = width_all_plot / ncol
        height_map = width_map * rlat / rlon
        height_all_plot = height_map * nrow + (nrow-1) * height_hspace
        height = height_all_plot + height_title + height_bottem_xticsk

    if clevs is None and vmin is None and vmax is None:
        vmax = -1e30
        vmin = 1e30
        for grd in grd_list:
            vmax1 = np.nanmax(grd.values)
            if vmax < vmax1:
                vmax = vmax1
            vmin1 = np.nanmin(grd.values)
            if vmin > vmin1:
                vmin = vmin1
    if extend is None: extend = "neither"
    cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap, clevs=clevs, vmin=vmin, vmax=vmax,extend=extend)
    # norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    # if extend is None:
    #     norm = BoundaryNorm(clevs1, ncolors=cmap1.N - 1)
    # elif extend == "both":
    #     if type=="contour":
    #         norm = BoundaryNorm(clevs1, ncolors=cmap1.N + 1)
    #     else
    #         norm = BoundaryNorm(clevs1, ncolors=cmap1.N + 1,extend=extend)
    # else:
    #     norm = BoundaryNorm(clevs1, ncolors=cmap1.N)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N)
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
        inte = 20
    else:
        inte = 30

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte) + 1)

    xticks = np.arange(vmin, vmax, inte)
    xticks_label = []
    xticks_label_None = []
    for i in range(len(xticks)):
        xticks_label.append(str(round(xticks[i],6)))
        xticks_label_None.append("")
    if xticks[-1] >0:
        xticks_label[-1] ="   " +xticks_label[-1] + "°E"
    else:
        xticks_label[-1] ="   " +xticks_label[-1] + "°W"


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
    elif r < 80:
        inte = 20
    else:
        inte = 30

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte) + 1)
    yticks = np.arange(vmin, vmax, inte)
    yticks_label = []
    yticks_label_None = []
    for j in range(len(yticks)):
        if yticks[j] >= 0:
            yticks_label.append(str(round(yticks[j],6))+"°N")
        else:
            yticks_label.append(str(round(-yticks[j], 6)) +"°S")
        yticks_label_None.append("")


    if isinstance(title, list):
        if nplot != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return


    fig = plt.figure(figsize=(width, height), dpi=dpi)

    for p in range(nplot):
        pi = p % ncol
        pj = int(p / ncol)
        rect1 = [(width_left_yticks + pi * (width_map + width_wspace))/width,
                 (height_bottem_xticsk + (nrow -1- pj) * (height_map + height_hspace))/height,
                 width_map / width,
                 height_map / height]
        ax = plt.axes(rect1)

        if title is None:
            try:

                time_str = meteva.base.tool.time_tools.time_to_str(grd_list[p]["time"].values[0])
                dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
                #print(str(grd_list[p]["dtime"].values[0]))
                title1 = str(grd_list[p]["member"].values[0]) + " " + dati_str + str(grd_list[p]["dtime"].values[0]) + "H时效 "

                if "var_name" in grd_list[p].attrs.keys():
                    title1 = title1 + grd_list[p].attrs["var_name"]
            except:
                print("time or dtime or level 格式错误，请更改相应数据格式或直接指定title")
                title1= ""
        else:
            #title1 = title.replace("NNN",data_name)
            if isinstance(title,list):
                title1 = title[p]
            else:
                title1 = title

        plt.title(title1,fontsize = sup_fontsize,pad = 0)

        if slon < 70 or elon > 140 or slat < 10 or elat > 60:
            add_worldmap = True

        if add_worldmap:
            add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"
            if elon >180:
                add_china_map_2basemap(ax, name= "world360", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"


        add_china_map_2basemap(ax, name="nation", edgecolor='k', lw=0.3, encoding='gbk',grid0 = None)  # "省界"
        add_china_map_2basemap(ax, edgecolor='k', lw=0.3, encoding='gbk')  # "省界"
        if add_county_line:
            add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk', grid0=None)  # "县界"
        ax.set_xlim((slon, elon))
        ax.set_ylim((slat, elat))
        if grid:
            plt.grid()



        knext_row = pi + (pj + 1) * ncol
        if knext_row >= nplot:
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticks_label, fontsize=sup_fontsize * 0.8)#, family='Times New Roman')
        else:
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticks_label_None, fontsize=sup_fontsize * 0.8)#, family='Times New Roman')

        if pi ==0:
            ax.set_yticks(yticks)
            ax.set_yticklabels(yticks_label, fontsize=sup_fontsize * 0.8)#, family='Times New Roman')
        else:
            ax.set_yticks(yticks)
            ax.set_yticklabels(yticks_label_None, fontsize=sup_fontsize * 0.8)#, family='Times New Roman')
        if type == "contour":

            #im = ax.contourf(x, y, np.squeeze(grd_list[p].values), levels=clevs1, cmap=cmap1, norm=norm)
            im = ax.contourf(x, y, np.squeeze(grd_list[p].values), levels=clevs1, cmap=cmap1, norm=norm, extend = extend)
            if clip is not None:
                try:
                    meteva.base.tool.maskout.shp2clip_by_shpfile(im, ax, clip)
                except:
                    if isinstance(clip, str): clip = [clip]
                    if isinstance(clip[0], str):
                        meteva.base.tool.maskout.shp2clip_by_region_name(im, ax, clip)
                    else:
                        meteva.base.tool.maskout.shp2clip_by_lines(im, ax, clip)

        else:
            im = ax.pcolormesh(x, y, np.squeeze(grd_list[p].values), cmap=cmap1, norm=norm)
            #im = ax.pcolormesh(x, y, np.squeeze(grd_list[p].values),  cmap=cmap1, norm=norm, extend=extend)

        if add_minmap is not None:
            minmap_lon_lat = [103, 123, 0, 25]
            minmap_height_rate = 0.27
            height_bigmap = rect1[3]
            height_minmap = height_bigmap * minmap_height_rate
            width_minmap = height_minmap * (minmap_lon_lat[1] - minmap_lon_lat[0]) * height / (
                    minmap_lon_lat[3] - minmap_lon_lat[2]) / width

            width_between_two_map = height_bigmap * 0.01
            sy_minmap = width_between_two_map + rect1[1]
            if add_minmap == "left":
                sx_minmap = rect1[0] + width_between_two_map
            else:
                sx_minmap = rect1[0] + rect1[2] - width_minmap - width_between_two_map
            rect_min = [sx_minmap, sy_minmap, width_minmap, height_minmap]
            ax_min = plt.axes(rect_min)
            plt.xticks([])
            plt.yticks([])
            ax_min.set_xlim((minmap_lon_lat[0], minmap_lon_lat[1]))
            ax_min.set_ylim((minmap_lon_lat[2], minmap_lon_lat[3]))
            ax_min.spines["top"].set_linewidth(0.3)
            ax_min.spines["bottom"].set_linewidth(0.3)
            ax_min.spines["right"].set_linewidth(0.3)
            ax_min.spines["left"].set_linewidth(0.3)
            if elon >180:
                add_china_map_2basemap(ax, name= "world360", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"
            add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"
            add_china_map_2basemap(ax_min, name="nation", edgecolor='k', lw=0.2, encoding='gbk', grid0=None)  # "省界"

            if type == "contour":
                ax_min.contourf(x, y, np.squeeze(grd_list[p].values), levels=clevs1, cmap=cmap1, norm=norm)
            else:
                ax_min.pcolormesh(x, y, np.squeeze(grd_list[p].values), levels=clevs1, cmap=cmap1, norm=norm)

    left_low = (width_left_yticks - 0.2 + ncol * (width_map  + width_wspace))/width

    colorbar_position = fig.add_axes([left_low, height_bottem_xticsk / height,0.02, height_all_plot/height])  # 位置[左,下,宽,高]
    cb = plt.colorbar(im, cax=colorbar_position)
    cb.ax.tick_params(labelsize=sup_fontsize *0.8)  #设置色标刻度字体大小。

    y_sup_title = (height_bottem_xticsk + (nrow) * (height_map + height_hspace)) / height
    if sup_title is not None:
        plt.suptitle(sup_title, y = y_sup_title,fontsize=sup_fontsize * 1.2)

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


def pcolormesh_2d_grid(grd,save_path = None,title = None,clevs= None,cmap = "rainbow",add_county_line = False,add_worldmap=False,show = False,dpi = 300,
                       sup_fontsize = 10,height = None,width = None,extend = None):

    if save_path is None:
        show = True
    x = grd['lon'].values
    y = grd['lat'].values
    rlon = x[-1] - x[0]
    rlat = y[-1] - y[0]

    grid0 = meteva.base.get_grid_of_data(grd)

    if height is None:
        height = 4
    title_hight = 0.6
    legend_hight = 0.3
    left_plots_width  = 0.8
    right_plots_width = 0.8
    if width is None:
        width = (height - title_hight - legend_hight) * rlon / rlat + left_plots_width + right_plots_width



    fig = plt.figure(figsize=(width, height),dpi = dpi)
    rect1 = [left_plots_width / width, legend_hight/height, (width - right_plots_width - left_plots_width) / width, 1-title_hight/height]
    ax = plt.axes(rect1)



    if title is None:
        time_str = meteva.base.tool.time_tools.time_to_str(grid0.gtime[0])
        dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
        if type(grid0.members[0]) == str:
            model_name = grid0.members[0]
        else:
            model_name = str(grid0.members[0])
        title = model_name + " "+dati_str  + str(grid0.dtimes[0]) + "H时效 " + grd.name
    plt.title(title,fontsize = 14)
    grid0 = meteva.base.get_grid_of_data(grd)


    if grid0.slon < 70 or grid0.elon > 140 or grid0.slat < 10 or grid0.elat > 60:
        add_worldmap = True
    if add_worldmap:
        add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"
        if grid0.elon > 180:
            add_china_map_2basemap(ax, name="world360", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"

    add_china_map_2basemap(ax, name="nation", edgecolor='k', lw=0.3, encoding='gbk')  # "国界"
    add_china_map_2basemap(ax,  edgecolor='k', lw=0.3, encoding='gbk')   # "省界"

    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"

    ax.set_xlim((grid0.slon, grid0.elon))
    ax.set_ylim((grid0.slat, grid0.elat))


    vmax = np.nanmax(grd.values)
    vmin = np.nanmin(grd.values)
    if extend is None: extend = "neither"
    cmap1,clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap,clevs=clevs,vmin=vmin,vmax = vmax,extend=extend)

    norm = BoundaryNorm(clevs1, ncolors=cmap1.N)
    im = ax.pcolormesh(x, y, np.squeeze(grd.values), cmap=cmap1,norm=norm)
    #im = ax.contourf(x,y,np.squeeze(grd.values))
    left_low = (width + 0.1 - right_plots_width) / width
    colorbar_position = fig.add_axes([left_low, legend_hight / height, 0.02, 1-title_hight/height])  # 位置[左,下,宽,高]
    plt.colorbar(im,cax= colorbar_position,extend = extend)


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
    ax.set_xticklabels(xticks_label,fontsize = sup_fontsize * 0.9) #, family='Times New Roman')

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
        if yticks[y] >= 0:
            yticks_label.append(str(round(yticks[y],6))+"°N")
        else:
            yticks_label.append(str(round(-yticks[y], 6)) +"°S")
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks_label,fontsize = sup_fontsize * 0.9) #, family='Times New Roman')


    if(save_path is not None):
        file1,extension = os.path.splitext(save_path)
        extension = extension[1:]
        plt.savefig(save_path,format = extension,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()


def mesh_xy(grd,save_path = None,title = None,clevs= None,cmap = "rainbow",add_county_line = False,add_worldmap=False,show = False,dpi = 300,
                       sup_fontsize = 10,height = None,width = None,extend = None):

    pcolormesh_2d_grid(grd,save_path=save_path,title=title,clevs= clevs,cmap=cmap,add_county_line=add_county_line,
                       add_worldmap=add_worldmap,show = show,dpi=dpi,sup_fontsize=sup_fontsize,height=height,width = width,
                       extend=extend)



def scatter_sta(sta0,value_column=None,
                map_extend = None,add_county_line = False,add_worldmap = False,
                clevs=None, cmap="rainbow",
                fix_size = True,threshold = None,mean_value = None,
                print_max = 0,print_min = 0,save_dir = None,
                save_path=None,show = False,dpi = 300,title=None,
                sup_fontsize = 10,
                height = None,width = None,
                min_spot_value = 0,grid = False,subplot = None,ncol = None,point_size = None,sup_title = None,add_minmap = None,
                extend = None,title_in_ax = False):

    sta = sta0
    if save_path is None and save_dir is None:
        show = True
    if isinstance(map_extend,list):
        slon = map_extend[0]
        elon = map_extend[1]
        slat = map_extend[2]
        elat = map_extend[3]
        rlon = elon - slon
        rlat = elat - slat
    elif isinstance(map_extend,meteva.base.grid):
        slon = map_extend.slon
        slat = map_extend.slat
        elon = map_extend.elon
        elat = map_extend.elat
        rlon = map_extend.elon - map_extend.slon
        rlat = map_extend.elat - map_extend.slat
    else:
        slon0 = np.min(sta.loc[:,"lon"].values)
        slat0 = np.min(sta.loc[:,"lat"].values)
        elon0 = np.max(sta.loc[:,"lon"].values)
        elat0 = np.max(sta.loc[:,"lat"].values)
        if elon0>180:
            sta = sta0.copy()
            sta.loc[sta0["lon"] > 180,"lon"] = sta0.loc[sta0["lon"] > 180,"lon"] - 360
            slon0 = np.min(sta.loc[:, "lon"].values)
            elon0 = np.max(sta.loc[:, "lon"].values)

        dlon0 = (elon0 - slon0) * 0.03
        if dlon0 >1:
            dlon0 = 1
        dlat0 = (elon0 - slon0) * 0.03
        if dlat0 >1:
            dlat0 = 1
        slon = slon0 - dlon0
        elon = elon0 + dlon0
        slat = slat0 - dlat0
        elat = elat0 + dlat0
        rlon = elon - slon
        rlat = elat - slat


    if height is None:
        height = 4
    title_hight = 1.0
    legend_hight = 0.3
    left_plots_width  = 0.8
    right_plots_width = 0.8
    if width is None:
        width = (height - title_hight - legend_hight) * rlon / rlat + left_plots_width + right_plots_width
    map_width = width - left_plots_width - right_plots_width
    map_area = (height - title_hight - legend_hight) *map_width

    data_names = meteva.base.get_stadata_names(sta)
    #value_column为指定绘制的数据列。 如果不知道绘制某一列就绘制所有列
    if value_column is None:
        plot_data_names = data_names
        value_column = 0
    else:
        plot_data_names = [data_names[value_column]]
        data_names = plot_data_names
        #print(plot_data_names)

    sta_without_iv = meteva.base.sele.not_IV(sta)
    sta_without_iv = meteva.base.sele.not_nan(sta_without_iv)
    values = sta_without_iv.loc[:, plot_data_names].values
    if mean_value is None:
        mean_value = np.sum(np.abs(values)) / values.size

    vmax_v = np.max(sta_without_iv[plot_data_names].values)
    vmin_v = np.min(sta_without_iv[plot_data_names].values)
    if extend is None: extend = "neither"
    cmap1,clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap,clevs=clevs,vmin=vmin_v,vmax = vmax_v,extend=extend)
    #clevs1, cmap1 = meteva.base.tool.color_tools.def_cmap_clevs(clevs=clevs, cmap=cmap, vmin = None, vmax=None)
    #meteva.base.tool.color_tools.show_cmap_clev(cmap1,clevs1)

    # if extend is None:
    #     norm = BoundaryNorm(clevs1, ncolors=cmap1.N - 1)
    # elif extend == "both":
    #     norm = BoundaryNorm(clevs1, ncolors=cmap1.N + 2, extend=extend)
    # else:
    #     norm = BoundaryNorm(clevs1, ncolors=cmap1.N+1, extend=extend)

    norm = BoundaryNorm(clevs1, ncolors=cmap1.N)

    if point_size is None:

        sta_id1 = sta0.drop_duplicates(['id'])
        sta_dis = meteva.base.sta_dis_ensemble_near_by_sta(sta_id1,nearNum=2)
        dis_values = sta_dis["data1"].values
        dis_values.sort()
        dis1 = dis_values[int(len(dis_values) * 0.02) + 1]
        point_size = (map_width * dis1 / rlon)**2
        if (point_size > 50): point_size = 50
        if (point_size < 0.1): point_size = 0.1
        #point_size *=3
    left_low = (width + 0.1 - right_plots_width) / width


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
    vmax = inte * ((int)(vmax / inte) + 1)

    xticks = np.arange(vmin, vmax, inte)
    xticks_label = []
    for x in range(len(xticks)):
        xticks_label.append(str(round(xticks[x],6)))
    if xticks[-1] >0:
        xticks_label[-1] ="   " +xticks_label[-1] + "°E"
    else:
        xticks_label[-1] ="   " +xticks_label[-1] + "°W"


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
        if yticks[y] >= 0:
            yticks_label.append(str(round(yticks[y],6))+"°N")
        else:
            yticks_label.append(str(round(-yticks[y], 6)) +"°S")


    if subplot is None:

        split = ["level","time","dtime","member"]
        sta_list = meteva.base.split(sta0,used_coords=split)
        nplot = len(sta_list)
        #nplot = len(plot_data_names)
        if isinstance(title, list):
            if nplot != len(title):
                print("手动设置的title数目和要绘制的图形数目不一致")
                return
        if save_path is not None:
            if isinstance(save_path,str):
                save_path = [save_path]
            if nplot != len(save_path):
                print("手动设置的save_path数目和要绘制的图形数目不一致")
                return

        for p in range(nplot):
            #data_name = data_names[p]
            #sta_one_member = meteva.base.sele_by_para(sta,member=[data_name],drop_IV=True)
            sta_one_member = sta_list[p]
            data_name = meteva.base.get_stadata_names(sta_one_member)[0]
            #print(sta_one_member)
            x = sta_one_member.loc[:, "lon"].values
            y = sta_one_member.loc[:, "lat"].values
            value = sta_one_member.loc[:, data_name].values
            fig = plt.figure(figsize=(width, height),dpi = dpi)
            rect1 = [left_plots_width / width, legend_hight / height, (width - right_plots_width - left_plots_width) / width,
                     1 - title_hight / height]
            ax = plt.axes(rect1)


            if title is None:
                try:
                    time_str = meteva.base.tool.time_tools.time_to_str(sta_one_member.iloc[0, 1])
                    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
                    level_str = str(int(sta_one_member.iloc[0, 0]))
                    title1 = str(data_name) + "_L"+level_str+"_" + dati_str + str(sta_one_member.iloc[0,2]) + "H时效"
                except:
                    print("time or dtime or level 格式错误，请更改相应数据格式或直接指定title")
                    title1= ""
            else:
                #title1 = title.replace("NNN",data_name)
                if isinstance(title,list):
                    title1 = title[p]
                else:
                    title1 = title +"(" +str(data_name)+")"

            plt.title(title1,fontsize = sup_fontsize)

            if slon < 70 or elon > 140 or slat < 10 or elat > 60:
                add_worldmap = True
            if add_worldmap:
                add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"
                if elon > 180:
                    add_china_map_2basemap(ax, name="world360", edgecolor='k', lw=0.3, encoding='gbk',
                                           grid0=None)  # "国界"


            add_china_map_2basemap(ax, name="nation", edgecolor='k', lw=0.3, encoding='gbk',grid0 = None)  # "省界"
            add_china_map_2basemap(ax, edgecolor='k', lw=0.3, encoding='gbk')  # "省界"
            if add_county_line:
                add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk', grid0=None)  # "县界"
            ax.set_xlim((slon, elon))
            ax.set_ylim((slat, elat))
            colors = value
            if isinstance(fix_size,bool):
                if fix_size:
                    im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=point_size,edgecolors ="face")
                else:
                    area = point_size * np.abs(value - min_spot_value)/mean_value
                    if(threshold is not None):
                        area[np.abs(value- min_spot_value)<threshold] *= 0.1
                    im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=area)
                    if grid:plt.grid()
            else:
                im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=fix_size)

            if print_max>0:
                print("取值最大的"+str(print_max)+"个站点：")
                indexs = value.argsort()[-print_max:][::-1]
                for index in indexs:
                    print("id:" + str(sta_one_member.iloc[index,3]) +"   lon:"+str(sta_one_member.iloc[index,4])+"  lat:" + str(sta_one_member.iloc[index,5]) +
                          " value:"+str(sta_one_member.iloc[index,6]))
            if print_min>0:
                print("取值最小的"+str(print_min)+"个站点：")
                indexs = value.argsort()[:print_min]
                for index in indexs:
                    print("id:" + str(sta_one_member.iloc[index,3]) +"   lon:"+str(sta_one_member.iloc[index,4])+"  lat:" + str(sta_one_member.iloc[index,5]) +
                          " value:"+str(sta_one_member.iloc[index,6]))

            colorbar_position = fig.add_axes([left_low, legend_hight / height, 0.02, 1-title_hight/height])  # 位置[左,下,宽,高]
            plt.colorbar(im, cax=colorbar_position,extend=extend)


            ax.set_xticks(xticks)
            ax.set_xticklabels(xticks_label,fontsize = sup_fontsize * 0.8) #, family='Times New Roman')

            ax.set_yticks(yticks)
            ax.set_yticklabels(yticks_label,fontsize = sup_fontsize * 0.8 ) #, family='Times New Roman')

            if slon< 75 and elon >130 and elat >50 and slat >3 and slat <25:
                if add_minmap is None:
                    add_minmap = "left"

            if add_minmap is not None:
                if add_minmap != False:
                    minmap_lon_lat = [103, 123, 0, 25]
                    minmap_height_rate = 0.27
                    height_bigmap = rect1[3]
                    height_minmap = height_bigmap * minmap_height_rate
                    width_minmap = height_minmap * (minmap_lon_lat[1] - minmap_lon_lat[0]) * height / (
                            minmap_lon_lat[3] - minmap_lon_lat[2]) / width

                    width_between_two_map = height_bigmap * 0.01
                    sy_minmap = width_between_two_map + rect1[1]
                    if add_minmap == "left":
                        sx_minmap = rect1[0] + width_between_two_map
                    else:
                        sx_minmap = rect1[0] + rect1[2] - width_minmap - width_between_two_map
                    rect_min = [sx_minmap, sy_minmap, width_minmap, height_minmap]
                    ax_min = plt.axes(rect_min)
                    plt.xticks([])
                    plt.yticks([])
                    ax_min.set_xlim((minmap_lon_lat[0], minmap_lon_lat[1]))
                    ax_min.set_ylim((minmap_lon_lat[2], minmap_lon_lat[3]))
                    ax_min.spines["top"].set_linewidth(0.3)
                    ax_min.spines["bottom"].set_linewidth(0.3)
                    ax_min.spines["right"].set_linewidth(0.3)
                    ax_min.spines["left"].set_linewidth(0.3)
                    if elon > 180:
                        add_china_map_2basemap(ax, name="world360", edgecolor='k', lw=0.3, encoding='gbk',
                                               grid0=None)  # "国界"

                    add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk',
                                           grid0=None)  # "国界"
                    add_china_map_2basemap(ax_min, name="nation", edgecolor='k', lw=0.2, encoding='gbk', grid0=None)  # "省界"



            save_path1 = None
            if save_path is None:
                if save_dir is None:
                    show = True
                else:
                    save_path1 = save_dir + "/" + title1 + ".png"
            else:
                save_path1 = save_path[p]
            if save_path1 is not None:
                meteva.base.tool.path_tools.creat_path(save_path1)
                file1, extension = os.path.splitext(save_path1)
                if(len(extension) ==0):
                    print("save_path中没包含后缀，如.png等,未能输出至指定路径")
                    return
                extension = extension[1:]
                plt.savefig(save_path1,format = extension,bbox_inches='tight')
                print("图片已保存至" + save_path1)
            if show:
                plt.show()
            plt.close()


    else:
        split = ["level","time","dtime","member"]
        if not isinstance(subplot,list):
            subplot = [subplot]
        for s in subplot:
            split.remove(s)
        sta_list = meteva.base.split(sta0,used_coords=split)
        ng = len(sta_list)

        if sup_title is None:
            sup_title = []
            for i in range(ng):
                sta0 = sta_list[i]
                if subplot==["level"]:
                    data_names = meteva.base.get_stadata_names(sta0)
                    time_str = meteva.base.tool.time_tools.time_to_str(sta0.iloc[0, 1])
                    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
                    sup_title1 = data_names[0] + "_" + dati_str + str(sta0.iloc[0, 2]) + "H时效"
                elif subplot==["time"]:
                    data_names = meteva.base.get_stadata_names(sta0)
                    level_str = str(int(sta0.iloc[0, 0]))
                    sup_title1 = data_names[0] + "_Level" + level_str + "_"+ str(sta0.iloc[0, 2]) + "H时效"
                elif subplot ==["dtime"]:
                    data_names = meteva.base.get_stadata_names(sta0)
                    time_str = meteva.base.tool.time_tools.time_to_str(sta0.iloc[0, 1])
                    level_str = str(int(sta0.iloc[0, 0]))
                    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
                    sup_title1 = data_names[0] + "_Level"+ level_str + "_" + dati_str
                elif subplot ==["member"]:
                    time_str = meteva.base.tool.time_tools.time_to_str(sta0.iloc[0, 1])
                    level_str = str(int(sta0.iloc[0, 0]))
                    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
                    sup_title1 = "Level" + level_str + "_"+ dati_str+ str(sta0.iloc[0, 2]) + "H时效"
                else:
                    sup_title1 = "none"

                sup_title.append(sup_title1)
        else:
            if not isinstance(sup_title,list):
                sup_title2 = []
                for i in range(ng):
                    sup_title2.append(sup_title)
                sup_title = sup_title2
            if len(sup_title) != ng:
                print("sup_title的数目应该和最终生成的图片数目一致")
                return

        for n in range(ng):
            sta1 = sta_list[n]
            sta_g1  = meteva.base.split(sta1,used_coords = subplot)
            ng1 = len(sta_g1)
            if isinstance(title,list):
                title1 = title[(ng1 * n):(ng1 * (n+1))]
            else:
                title1 = []
                for  kk in range(len(sta_g1)):
                    sta0 = sta_g1[kk]
                    if subplot==["level"]:
                        title00 = str(int(sta0.iloc[0, 0]))
                    elif subplot==["time"]:
                        time_str = meteva.base.tool.time_tools.time_to_str(sta0.iloc[0, 1])
                        title00 = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
                    elif subplot ==["dtime"]:
                        title00 =str(sta0.iloc[0, 2]) + "H时效 "
                    elif subplot ==["member"]:
                        data_names = meteva.base.get_stadata_names(sta0)
                        title00 = data_names[0]
                    else:
                        title00 = "none"
                    title1.append(title00)



            if isinstance(save_path,list):
                save_path1 = save_path[n]
            elif save_path is not None:
                save_path1 = save_path
            elif save_dir is not None:
                save_path1 = save_dir+"/"+sup_title[n]+".png"

            else:
                save_path1 = None



            scatter_sta_list(sta_g1,map_extend = map_extend,add_county_line = add_county_line,
            add_worldmap=add_worldmap,clevs = clevs,cmap = cmap,vmax=vmax_v,vmin = vmin_v,fix_size=fix_size,threshold=threshold,
                             mean_value = mean_value,save_path = save_path1,show = show,dpi = dpi,
                            title = title1,sup_fontsize = sup_fontsize,
                             height=height,width= width,min_spot_value=min_spot_value,grid = grid,ncol = ncol,point_size=point_size,sup_title=sup_title[n],
                             add_minmap = add_minmap,print_max = print_max,print_min = print_min,title_in_ax=title_in_ax,extend=extend)


def scatter_sta_list(sta0_list,map_extend = None,add_county_line = False,add_worldmap = False,
                clevs=None, cmap="rainbow",vmax = None,vmin = None,
                fix_size = True,threshold = None,mean_value = None,
                save_path=None,show = False,dpi = 300,title = None,
                sup_fontsize = 10,
                height = None,width = None,
                min_spot_value = 0,grid = False,ncol = None,point_size = None,sup_title = None,add_minmap = None,print_max = 0,print_min = 0,
                    extend = None, title_in_ax = False):

    sta0 = sta0_list[0]
    if isinstance(map_extend, list):
        slon = map_extend[0]
        elon = map_extend[1]
        slat = map_extend[2]
        elat = map_extend[3]
        rlon = elon - slon
        rlat = elat - slat
    elif isinstance(map_extend, meteva.base.grid):
        slon = map_extend.slon
        slat = map_extend.slat
        elon = map_extend.elon
        elat = map_extend.elat
        rlon = map_extend.elon - map_extend.slon
        rlat = map_extend.elat - map_extend.slat
    else:
        slon0 = np.min(sta0.loc[:, "lon"].values)
        slat0 = np.min(sta0.loc[:, "lat"].values)
        elon0 = np.max(sta0.loc[:, "lon"].values)
        elat0 = np.max(sta0.loc[:, "lat"].values)
        if elon0 > 180:
            sta = sta0.copy()
            sta.loc[sta0["lon"] > 180, "lon"] = sta0.loc[sta0["lon"] > 180, "lon"] - 360
            slon0 = np.min(sta.loc[:, "lon"].values)
            elon0 = np.max(sta.loc[:, "lon"].values)

        dlon0 = (elon0 - slon0) * 0.03
        if dlon0 > 1:
            dlon0 = 1
        dlat0 = (elon0 - slon0) * 0.03
        if dlat0 > 1:
            dlat0 = 1
        slon = slon0 - dlon0
        elon = elon0 + dlon0
        slat = slat0 - dlat0
        elat = elat0 + dlat0
        rlon = elon - slon
        rlat = elat - slat

    if sup_title is None:
        sup_height_title = 0
    else:
        sup_height_title = sup_fontsize * 0.12

    height_title = sup_fontsize * 0.1
    height_bottem_xticsk = sup_fontsize * 0.05
    height_hspace = sup_fontsize * 0.03

    width_wspace = height_hspace

    width_colorbar = 0.5
    width_left_yticks = sup_fontsize * 0.1

    nplot = len(sta0_list)
    if ncol is None:
        match_list = []
        for i in range(nplot,0,-1):
            ncol = i
            nrow = int(math.ceil(len(sta0_list) / ncol))
            rate = ncol * rlon/(nrow * rlat)
            if rate <2 and rate > 9/16:
                match_list.append([i,ncol * nrow - nplot])
        if len(match_list)  ==0:
            ncol = nplot
        else:
            match_array = np.array(match_list)
            min_index = np.argmin(match_array[:,1])
            ncol = match_array[min_index,0]
    nrow = int(math.ceil(nplot / ncol))

    if width is None and height is None:
        width = 8

    if width is None:
        height_all_plot = height - height_title - height_bottem_xticsk - (nrow-1) * height_hspace + sup_height_title
        height_map = height_all_plot / nrow
        width_map = height_map * rlon / rlat
        width_all_plot = width_map * ncol + (ncol-1) * width_wspace
        width = width_all_plot + width_colorbar + width_left_yticks
    else:
        width_all_plot = width - width_colorbar - width_left_yticks - (ncol - 1) * width_wspace
        width_map = width_all_plot / ncol
        height_map = width_map * rlat / rlon
        height_all_plot = height_map * nrow + (nrow-1) * height_hspace
        height = height_all_plot + height_title + height_bottem_xticsk + sup_height_title


    map_area = height_map *width_map
    if extend is None: extend = "neither"
    cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap, clevs=clevs, vmin=vmin, vmax=vmax,extend=extend)
    # if extend is None:
    #     norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    # elif extend == "both":
    #     norm = BoundaryNorm(clevs1, ncolors=cmap1.N + 2, extend=extend)
    # else:
    #     norm = BoundaryNorm(clevs1, ncolors=cmap1.N + 1, extend=extend)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N)
    #print(sta0_list[0])
    if point_size is None:

        sta_id1 = sta0.drop_duplicates(['id'])
        sta_dis = meteva.base.sta_dis_ensemble_near_by_sta(sta_id1,nearNum=2)
        dis_values = sta_dis["data1"].values
        dis_values.sort()
        dis1 = dis_values[int(len(dis_values) * 0.02) + 1]
        point_size = (width_map * dis1 / rlon)**2
        if (point_size > 50): point_size = 50
        if (point_size < 0.1): point_size = 0.1


        #point_size = int(100 * map_area / len(sta0_list[0].index))
        #if (point_size > 50): point_size = 50
        #if (point_size < 1): point_size = 1
        #point_size *=1.5


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
        xticks_label.append(str(round(xticks[x],6)))
        xticks_label_None.append("")
    if xticks[-1] >0:
        xticks_label[-1] ="   " +xticks_label[-1] + "°E"
    else:
        xticks_label[-1] ="   " +xticks_label[-1] + "°W"


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
            yticks_label.append(str(round(yticks[y],6))+"°N")
        else:
            yticks_label.append(str(round(-yticks[y], 6)) +"°S")
        yticks_label_None.append("")


    if isinstance(title, list):
        if nplot != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return


    fig = plt.figure(figsize=(width, height), dpi=dpi)
    title1 = None
    for p in range(nplot):
        sta_one_member = meteva.base.sele_by_para(sta0_list[p],drop_IV=True)
        data_name = meteva.base.get_stadata_names(sta_one_member)

        x = sta_one_member.loc[:, "lon"].values
        y = sta_one_member.loc[:, "lat"].values
        value = sta_one_member.loc[:, data_name].values.squeeze()

        pi = p % ncol
        pj = int(p / ncol)



        rect1 = [(width_left_yticks + pi * (width_map + width_wspace))/width,
                 (height_bottem_xticsk + (nrow -1- pj) * (height_map + height_hspace))/height,
                 width_map / width,
                 height_map / height]
        ax = plt.axes(rect1)

        if title is None:
            try:
                time_str = meteva.base.tool.time_tools.time_to_str(sta_one_member.iloc[0, 1])
                dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
                title1 = data_name[0] + " " + dati_str + str(sta_one_member.iloc[0,2]) + "H时效 "
            except:
                print("time or dtime or level 格式错误，请更改相应数据格式或直接指定title")
                title1= ""
        else:
            #title1 = title.replace("NNN",data_name)
            if isinstance(title,list):
                title1 = title[p]
            else:
                title1 = title

        if title_in_ax:
            ix = slon + 0.02 * (elon - slon) * 5 / width_map
            iy = elat - 0.035 * (elat - slat) * 5 / height_map
            plt.text(ix, iy, title1, bbox=dict(fc='white', ec='white', pad=0), fontsize=sup_fontsize,
                     zorder=100)
        else:
            plt.title(title1, fontsize=sup_fontsize, pad=0)


        if slon < 70 or elon > 140 or slat < 10 or elat > 60:
            add_worldmap = True
        if add_worldmap:
            add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"
            if elon >180:
                add_china_map_2basemap(ax, name= "world360", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"


        add_china_map_2basemap(ax, name="nation", edgecolor='k', lw=0.3, encoding='gbk',grid0 = None)  # "省界"
        add_china_map_2basemap(ax, edgecolor='k', lw=0.3, encoding='gbk')  # "省界"
        if add_county_line:
            add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk', grid0=None)  # "县界"
        ax.set_xlim((slon, elon))
        ax.set_ylim((slat, elat))
        colors = value
        if isinstance(fix_size, bool):
            if fix_size:
                im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=point_size)
            else:

                area = point_size * np.abs(value - min_spot_value)/mean_value
                if(threshold is not None):
                    area[np.abs(value- min_spot_value)<threshold] *= 0.1
                im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=area)
                if grid:plt.grid()
        else:
            im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=fix_size)


        knext_row = pi + (pj + 1) * ncol
        if knext_row >= nplot:
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticks_label, fontsize=sup_fontsize * 0.8) #, family='Times New Roman')
        else:
            ax.set_xticks(xticks)
            ax.set_xticklabels(xticks_label_None, fontsize=sup_fontsize * 0.8) #, family='Times New Roman')

        if pi ==0:
            ax.set_yticks(yticks)
            ax.set_yticklabels(yticks_label, fontsize=sup_fontsize * 0.8 ) #, family='Times New Roman')
        else:
            ax.set_yticks(yticks)
            ax.set_yticklabels(yticks_label_None, fontsize=sup_fontsize * 0.8) #, family='Times New Roman')

        if slon< 75 and elon >130 and elat >50 and slat >3 and slat <25:
            if add_minmap is None:
                add_minmap = "left"
        if add_minmap is not None:
            minmap_lon_lat = [105, 123, 0, 20]
            minmap_height_rate = 0.27
            height_bigmap = rect1[3]
            height_minmap = height_bigmap * minmap_height_rate
            width_minmap = height_minmap * (minmap_lon_lat[1] - minmap_lon_lat[0]) * height / (
                        minmap_lon_lat[3] - minmap_lon_lat[2])/width

            width_between_two_map =  height_bigmap *0.01
            sy_minmap = width_between_two_map + rect1[1]
            if add_minmap =="left":
                sx_minmap = rect1[0] + width_between_two_map
            else:
                sx_minmap = rect1[0] + rect1[2] - width_minmap - width_between_two_map
            rect_min = [sx_minmap,sy_minmap,width_minmap,height_minmap]
            ax_min = plt.axes(rect_min)
            plt.xticks([])
            plt.yticks([])
            ax_min.set_xlim((minmap_lon_lat[0], minmap_lon_lat[1]))
            ax_min.set_ylim((minmap_lon_lat[2], minmap_lon_lat[3]))
            ax_min.spines["top"].set_linewidth(0.3)
            ax_min.spines["bottom"].set_linewidth(0.3)
            ax_min.spines["right"].set_linewidth(0.3)
            ax_min.spines["left"].set_linewidth(0.3)
            if elon >180:
                add_china_map_2basemap(ax, name="world360", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"
            add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"
            add_china_map_2basemap(ax_min, name="nation", edgecolor='k', lw=0.2, encoding='gbk', grid0=None)  # "省界"

        #if print_max >0 or print_min >0:
        #    print(title1)
        if print_max > 0:
            print("取值最大的" + str(print_max) + "个站点：")
            indexs = value.argsort()[-print_max:][::-1]
            for index in indexs:
                print("id:" + str(sta_one_member.iloc[index, 3]) + "   lon:" + str(
                    sta_one_member.iloc[index, 4]) + "  lat:" + str(sta_one_member.iloc[index, 5]) +
                      " value:" + str(sta_one_member.iloc[index, 6]))

        if print_min > 0:
            print("取值最小的" + str(print_min) + "个站点：")
            indexs = value.argsort()[:print_min]
            for index in indexs:
                print("id:" + str(sta_one_member.iloc[index, 3]) + "   lon:" + str(
                    sta_one_member.iloc[index, 4]) + "  lat:" + str(sta_one_member.iloc[index, 5]) +
                      " value:" + str(sta_one_member.iloc[index, 6]))
        if print_max > 0 or print_min > 0:
            print("______________")

    left_low = (width_left_yticks + ncol * (width_map  + width_wspace))/width
    colorbar_position = fig.add_axes([left_low, height_bottem_xticsk / height,0.02, height_all_plot/height])  # 位置[左,下,宽,高]

    cb = plt.colorbar(im, cax=colorbar_position,extend = extend)
    cb.ax.tick_params(labelsize=sup_fontsize *0.8)  #设置色标刻度字体大小。


    title1_list = [""]
    if title1 is not None:
        title1_list = title1.split("\n")


    y_sup_title = (height_bottem_xticsk + (nrow) * (height_map + height_hspace)+(len(title1_list)-1)* sup_fontsize*0.015) / height
    if sup_title is not None:
        plt.suptitle(sup_title, y = y_sup_title,fontsize=sup_fontsize * 1.2)

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




def set_plot_IV(dat0):
    num = len(dat0)
    dat = np.zeros_like(dat0)
    dat[:] = dat0[:]
    if dat[0] == IV:
        dat[0] = 0
        for i in range(1,num):
            if dat0[i] != IV:
                dat[0] = dat0[i]
                break
    if dat[-1] == IV:
        dat[-1] = 0
        for i in range(num-2,-1,-1):
            if dat0[i] != IV:
                dat[-1] = dat0[i]
                break
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


def set_plot_IV_with_out_start_end(dat0):
    num = len(dat0)
    dat = np.zeros_like(dat0)
    dat[:] = dat0[:]

    for i in range(1,num-1):
        if dat[i] == IV:
            i1 = i
            for p in range(1,num):
                i1 = i-p
                if i1<0 or dat[i1] != IV:
                    break
            i2 = i
            for p in range(1,num):
                i2 = i + p
                if i2>= num or dat[i2] != IV:
                    break
            if i1<0 or i2 >=num:continue
            rate = (i- i1) / (i2 - i1)
            dat[i] = dat[i1] * (1-rate) + dat[i2] * rate
    dat[dat == IV] = np.nan
    return dat

def caculate_str_width(str1,fontsize):
    max_lenght = 0
    xtick_1lines = str1.split("\n")
    for xtick1 in xtick_1lines[:2]:
        lenght = 0
        for ch in xtick1:
            if '\u4e00' <= ch <= '\u9fff':
                lenght += 2
            else:
                lenght += 1
        if max_lenght < lenght:
            max_lenght = lenght
    width =  max_lenght  * fontsize / 144
    return width

def caculate_axis_width(xticks,fontsize,legend_num = 1):
    '''
    计算绘图框的宽度
    :param xticks:
    :param fontsize:
    :param legend_num:
    :return:
    '''
    max_lenght = 0

    for i in range(len(xticks)):
        xtick = xticks[i]
        if not type(xtick) == str:
            xtick = str(xtick)
        xtick_1lines = xtick.split("\n")
        for xtick1 in xtick_1lines[:2]:
            lenght = 0
            for ch in xtick1:
                if '\u4e00' <= ch <= '\u9fff':
                    lenght += 2
                else:
                    lenght += 1
            if max_lenght < lenght:
                max_lenght = lenght
    width = 1.1 * max_lenght * len(xticks)  * fontsize/144
    bar_num = len(xticks) * legend_num
    min_bar_widht = 0.1
    total_bar_width = bar_num * min_bar_widht * 1.3
    if total_bar_width >=10:
        total_bar_width = 10
    if width < total_bar_width:
        width = total_bar_width
    return width

def lineh(array,name_list_dict = None,legend = None,axis = None,xlabel = "Value",vmin = None,vmax = None,ncol = None,grid = None,tag = -1,save_path = None,show = False
        ,dpi = 300,bar_width = None,sparsify_yticks = 1,sup_fontsize = 10,title = ""
             ,height = None,width = None,log_y = False,sup_title = None,ylabel = None,legend_col = None,color_list = None,vline = None,marker = None,
             legend_loc =  "upper right",linestyle = None,return_axs = False):
    shape = array.shape
    array = copy.deepcopy(array)

    if len(array[array != meteva.base.IV]) == 0:
        print("所有的值都为缺失值")
        return

    if len(shape) == 1:
        if name_list_dict is None:
            name_list_dict = {}
            name_list_dict["y"] = np.arange(array.size).tolist()
            axis = "y"
        else:
            axis = list(name_list_dict.keys())[0]

        y_one = name_list_dict[axis][0]
        if isinstance(y_one, datetime.datetime):
            yticks_labels = meteva.product.get_time_str_list(name_list_dict[axis], 1)
        else:
            yticks_labels = []
            for local in name_list_dict[axis]:
                if isinstance(local, float):
                    yticks_labels.append(str(round(local, 6)))
                else:
                    yticks_labels.append(str(local))

        if width is None:
            width = 6
        if height is None:
            height = width

        fig = plt.figure(figsize=(width, height), dpi=dpi)
        x = np.arange(array.size)
        y_plot = array[array != meteva.base.IV]
        x_plot = x[array != meteva.base.IV]

        if log_y:
            array[array == 0] = meteva.base.IV
        if vmin is None:
            vmin1 = np.min(array[array != meteva.base.IV])
        else:
            vmin1 = vmin
        if vmax is None:
            vmax1 = np.max(array[array != meteva.base.IV])
        else:
            vmax1 = vmax

        dmax = vmax1 - vmin1
        if log_y and vmin1 <= 0:
            print("取对数坐标时数据的最小值不能<=0")

        if vmin is None:
            if log_y:
                pass
                vmin1 = vmin1 * (vmin1 / vmax1) ** 0.2
            else:
                vmin1 = vmin1 - 0.1 * dmax
        if vmax is None:
            if log_y:
                vmax1 = vmax1 * (vmax1 / vmin1) ** 0.3
            else:
                vmax1 = vmax1 + 0.1 * dmax


        dat0 = array
        index_iv = np.where(dat0 == meteva.base.IV)
        if len(index_iv[0]) == 0:
            if color_list is None:
                plt.plot(dat0,x)
            else:
                plt.plot(dat0,x, color=color_list[0])
        else:
            dat0_all = set_plot_IV_with_out_start_end(dat0)
            plt.plot(dat0_all,x,  "--", linewidth=0.5, color="k")
            x_iv = x[index_iv[0]]
            dat0_iv = dat0_all[index_iv[0]]
            plt.plot(dat0_iv,x_iv,  "x", color='k', markersize=1)
            dat0_notiv = dat0.copy()
            dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
            if color_list is None:
                plt.plot(dat0_notiv,x, marker=marker)
            else:
                plt.plot(dat0_notiv,x, color=color_list[0], marker=marker)
        if tag >= 0:
            for ii in range(len(dat0)):
                a = x[ii]
                b = dat0[ii]
                if np.isnan(b) or b == meteva.base.IV: continue
                ha = "center"
                if ii > 0 and ii < len(dat0) - 1:
                    if b > dat0[ii - 1] and b > dat0[ii + 1]:
                        ha = "left"
                    elif b < dat0[ii - 1] and b < dat0[ii + 1]:
                        ha = "right"
                fmt_tag = "%." + str(tag) + "f"
                plt.text(b,a, fmt_tag % b, ha=ha, va="center",
                         fontsize=sup_fontsize * 0.6)

        yticks = x[sparsify_yticks - 1::sparsify_yticks]
        plt.yticks(yticks, yticks_labels, fontsize=sup_fontsize*0.8)
        plt.yticks(fontsize=sup_fontsize * 0.8)
        if ylabel is None: ylabel = axis
        plt.xlabel(xlabel, fontsize=sup_fontsize * 0.9)
        plt.ylabel(ylabel, fontsize=sup_fontsize * 0.9)

        if isinstance(title, list):
            title = title[0]
        plt.title(title, fontsize=sup_fontsize)
        plt.xlim(vmin1, vmax1)
        plt.ylim(-0.5, array.size - 0.5)
        if vline is not None:
            plt.axvline(vline, ls="--", c="k")
        if log_y:
            ax_one = plt.gca()
            for tick in ax_one.yaxis.get_major_ticks():
                tick.label1.set_fontproperties('stixgeneral')
            plt.yscale('log')
        if grid is not None:
            if grid:
                plt.grid()
            else:
                pass
        else:
            if sparsify_yticks > 2:
                plt.grid()

    elif len(shape) == 2:
        if name_list_dict is None:
            name_list_dict = {}
            list1 = np.arange(shape[0]).tolist()
            list2 = []
            for lv in list1:
                list2.append("x_" + str(lv))
            name_list_dict["x"] = list2
            name_list_dict["y"] = np.arange(shape[1]).tolist()
        keys = list(name_list_dict.keys())
        dat = None
        if legend is None:
            if axis is None:
                legend = keys[0]
                axis = keys[1]
            else:
                if axis != keys[0]:
                    legend = keys[0]
                else:
                    legend = keys[1]
                    dat = array.T
        if legend == keys[1]:
            dat = array.T

        if dat is None:
            dat = array
        if legend not in keys:
            print("legend 参数的取值必须是name_list_dict的key")
        if axis not in keys:
            print("axis 参数的取值必须是name_list_dict的key")

        legend_list = name_list_dict[legend]
        legend_num = len(legend_list)
        if linestyle is None:
            linestyle = []
            for i in range(legend_num):
                linestyle.append("-")
        y_one = name_list_dict[axis][0]

        if isinstance(y_one, datetime.datetime):
            yticks_labels = meteva.product.get_time_str_list(name_list_dict[axis])
        else:
            yticks_labels = []
            for local in name_list_dict[axis]:
                if isinstance(local, float):
                    yticks_labels.append(str(round(local, 6)))
                else:
                    yticks_labels.append(str(local))

        #width_axis = meteva.base.plot_tools.caculate_axis_width(yticks_labels, sup_fontsize, legend_num)
        #width_axis_labels = meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize, 1)


        if width is None:
            width = 8

        if height is None:
            height = width


        fig = plt.figure(figsize=(width, height), dpi=dpi)

        x = np.arange(0, len(name_list_dict[axis]), 1)
        if dat.shape[1] + 1 == len(name_list_dict[axis]):
            x = x - 0.5
            if isinstance(name_list_dict[axis][0], str) and name_list_dict[axis][0].find("<") == 0:
                x[0] += 0.5
            if isinstance(name_list_dict[axis][0], str) and (name_list_dict[axis][-1].find(">") == 0):
                x[-1] -= 0.5
        elif len(x) != len(name_list_dict[axis]):
            print("坐标的size和数据的size不匹配")
            return

        yticks = x[sparsify_yticks - 1::sparsify_yticks]
        yticks_labels = yticks_labels[sparsify_yticks - 1::sparsify_yticks]

        if log_y:
            array[array == 0] = meteva.base.IV
        if vmin is None:
            vmin1 = np.min(array[array != meteva.base.IV])
        else:
            vmin1 = vmin
        if vmax is None:
            vmax1 = np.max(array[array != meteva.base.IV])
        else:
            vmax1 = vmax
        dmax = vmax1 - vmin1

        if log_y and vmin1 <= 0:
            print("取对数坐标时数据的最小值不能<=0")

        if vmin is None:
            if log_y:
                pass
                vmin1 = vmin1 * (vmin1 / vmax1) ** 0.2
            else:
                vmin1_new = vmin1 - 0.1 * dmax
                if vmin1 >= 0 and vmin1_new <= 0:
                    vmin1_new = 0
                vmin1 = vmin1_new

        if vmax is None:
            if log_y:
                vmax1 = vmax1 * (vmax1 / vmin1) ** 0.5
            else:
                vmax1 = vmax1 + 0.1 * dmax

        x = np.arange(dat.shape[1])
        legend0 = str(legend_list[0])
        if legend0.lower().find("ob") < 0 and legend0.find("观测") < 0 and legend0.find(
                "实况") < 0 and legend0.find("零场") < 0:
            # 如果判断第一个legend不是观测想的，则跳过第一个自动颜色
            plt.plot(0, 0)
        for i in range(legend_num):
            dat0 = dat[i, :]
            index_iv = np.where(dat0 == meteva.base.IV)
            if len(index_iv) == 0:
                if color_list is None:
                    if meteva.base.plot_color_dict is not None and legend_list[
                        i] in meteva.base.plot_color_dict.keys():
                        color_set1 = meteva.base.plot_color_dict[legend_list[i]]
                        plt.plot(dat0,x, label=legend_list[i], color=color_set1, linestyle=linestyle[i])
                    else:
                        plt.plot(dat0, x, label=legend_list[i], linestyle=linestyle[i])
                else:
                    plt.plot(dat0,x,  label=legend_list[i], color=color_list[i], linestyle=linestyle[i])
            else:
                dat0_all = set_plot_IV_with_out_start_end(dat0)
                plt.plot(dat0_all,x,  "--", linewidth=0.5, color="k")
                x_iv = x[index_iv[0]]
                dat0_iv = dat0_all[index_iv[0]]
                plt.plot(dat0_iv,x_iv,  "x", color='k', markersize=1)
                dat0_notiv = dat0.copy()
                dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
                if color_list is None:
                    if meteva.base.plot_color_dict is not None and legend_list[
                        i] in meteva.base.plot_color_dict.keys():
                        color_set1 = meteva.base.plot_color_dict[legend_list[i]]
                        plt.plot(dat0_notiv, x, label=name_list_dict[legend][i], color=color_set1, marker=marker,
                                 linestyle=linestyle[i])
                    else:
                        plt.plot(dat0_notiv,x,  label=name_list_dict[legend][i], marker=marker,
                                 linestyle=linestyle[i])
                else:
                    plt.plot(dat0_notiv, x, label=name_list_dict[legend][i], color=color_list[i], marker=marker,
                             linestyle=linestyle[i])
            if tag >= 0:
                for ii in range(len(dat0)):
                    a = x[ii]
                    b = dat0[ii]
                    if np.isnan(b) or b == meteva.base.IV: continue
                    ha = "center"
                    if ii > 0 and ii < len(dat0) - 1:
                        if b > dat0[ii - 1] and b > dat0[ii + 1]:
                            ha = "right"
                        elif b < dat0[ii - 1] and b < dat0[ii + 1]:
                            ha = "left"
                    fmt_tag = "%." + str(tag) + "f"
                    plt.text(b,a, fmt_tag % a, ha=ha, va="center",
                             fontsize=sup_fontsize * 0.6)
        if legend_col is None:legend_col=1
        plt.legend(fontsize=sup_fontsize * 0.8, ncol=legend_col, loc=legend_loc)
        plt.yticks(yticks, yticks_labels, fontsize=sup_fontsize*0.8)

        plt.xlabel(xlabel, fontsize=sup_fontsize * 0.9)
        plt.ylabel(ylabel, fontsize=sup_fontsize * 0.9)
        if isinstance(title, list):
            title = title[0]
        plt.title(title, fontsize=sup_fontsize)
        plt.ylim(-0.5, dat.shape[1] - 0.5)
        plt.xlim(vmin1, vmax1)
        if vline is not None:
            plt.axvline(vline, ls="--", c="k")
        if log_y:
            ax_one = plt.gca()
            for tick in ax_one.yaxis.get_major_ticks():
                tick.label1.set_fontproperties('stixgeneral')
            plt.yscale('log')
        if grid is not None:
            if grid:
                plt.grid()
            else:
                pass
        else:
            if sparsify_yticks > 2:
                plt.grid()

    elif len(shape) == 3:
        if name_list_dict is None:
            name_list_dict = {}
            name_list_dict["z"] = np.arange(shape[0])
            list1 = np.arange(shape[1]).tolist()
            list2 = []
            for lv in list1:
                list2.append("x_" + str(lv))
            name_list_dict["y"] = list2
            name_list_dict["y"] = np.arange(shape[2])
            legend = "x"
            axis = "y"
            subplot = "z"
        keys = list(name_list_dict.keys())
        if legend is None:
            if axis is None:
                legend = keys[1]
                axis = keys[2]
                subplot = keys[0]
            else:
                if axis == keys[2]:
                    legend = keys[1]
                    subplot = keys[0]
                elif axis == keys[1]:
                    legend = keys[2]
                    subplot = keys[0]
                else:
                    legend = keys[2]
                    subplot = keys[1]
        else:
            if axis is None:
                if legend == keys[0]:
                    axis = keys[2]
                    subplot = keys[1]
                elif legend == keys[1]:
                    axis = keys[2]
                    subplot = keys[0]
                else:
                    axis = keys[1]
                    subplot = keys[0]
            else:
                indexlist = [0, 1, 2]
                indexlist.remove(keys.index(legend))
                indexlist.remove(keys.index(axis))
                subplot = keys[indexlist[0]]
        if legend not in keys:
            print("legend 参数的取值必须是name_list_dict的key")
        if axis not in keys:
            print("axis 参数的取值必须是name_list_dict的key")
        newshape = (keys.index(subplot), keys.index(legend), keys.index(axis))
        data = array.transpose(newshape)
        legend_num = len(name_list_dict[legend])
        if linestyle is None:
            linestyle = []
            for i in range(legend_num):
                linestyle.append("-")
        y_one = name_list_dict[axis][0]
        if isinstance(y_one, datetime.datetime):
            yticks_labels = meteva.product.get_time_str_list(name_list_dict[axis], 1)
        elif axis.find("dayofyear") >= 0:
            yticks_labels = meteva.product.get_dayofyear_str_list(name_list_dict[axis])
        else:
            yticks_labels = []
            for local in name_list_dict[axis]:
                if isinstance(local, float):
                    if local == int(local):
                        yticks_labels.append(str(int(local)))
                    else:
                        yticks_labels.append(str(round(local, 6)))
                else:
                    yticks_labels.append(str(local))

        yticks_labels = yticks_labels[sparsify_yticks - 1::sparsify_yticks]

        subplot_num = len(name_list_dict[subplot])

        x = np.arange(len(name_list_dict[axis]))
        if data.shape[2] + 1 == len(name_list_dict[axis]):
            x = x - 0.5
            if isinstance(name_list_dict[axis][0], str) and name_list_dict[axis][0].find("<") == 0:
                x[0] += 0.5
            if isinstance(name_list_dict[axis][0], str) and (name_list_dict[axis][-1].find(">") == 0):
                x[-1] -= 0.5
        elif len(x) != len(name_list_dict[axis]):
            print("坐标的size和数据的size不匹配")
            return

        yticks = x[sparsify_yticks - 1::sparsify_yticks]

        width_one_subplot = 3


        if ncol is None:
            ncol = int(8 / width_one_subplot)
            nrow = int(math.ceil(subplot_num / ncol))
            ncol = int(math.ceil(subplot_num / nrow))
        else:
            nrow = int(math.ceil(len(name_list_dict[subplot]) / ncol))

        if width is None:
            width_fig = 8
        else:
            width_fig = width

        wspace = sup_fontsize * 0.03
        height_hspace = sup_fontsize * 0.03
        height_suplegend = 1
        if height is None:
            height_fig = 6
        else:
            height_fig = height

        fig = plt.figure(figsize=(width_fig, height_fig), dpi=dpi)
        x = np.arange(data.shape[2])

        plt.subplots_adjust(left=0, bottom=0.0, right=1.0, top=1 - height_suplegend / height_fig,
                            hspace=height_hspace, wspace=wspace)

        if bar_width is None:
            width = 0.7 / (legend_num + 2)
        else:
            width = bar_width
        ax_top = None
        for k in range(subplot_num):
            # print(data.shape)
            data_k = data[k, :, :]
            if log_y:
                data_k[data_k == 0] = meteva.base.IV
            if vmin is None:
                dat_k0 = data_k[data_k != meteva.base.IV]
                if dat_k0.size > 0:
                    vmin1 = np.min(dat_k0)
                else:
                    vmin1 = 0
            else:
                if isinstance(vmin, list):
                    if len(vmin) != subplot_num:
                        print("vmin 参数的个数和 子图个数不一致，请重新设置")
                        return
                    else:
                        vmin1 = vmin[k]
                else:
                    vmin1 = vmin

            if vmax is None:
                dat_k0 = data_k[data_k != meteva.base.IV]
                if dat_k0.size > 0:
                    vmax1 = np.max(dat_k0)
                else:
                    vmax1 = vmin1 + 0.1
            else:
                if isinstance(vmax, list):
                    if len(vmax) != subplot_num:
                        print("vmin 参数的个数和 子图个数不一致，请重新设置")
                        return
                    else:
                        vmax1 = vmax[k]
                else:
                    vmax1 = vmax

            dmax = vmax1 - vmin1

            if log_y and vmin1 < 0:
                print("取对数坐标时数据的最小值不能<0")
            if vmin is None:
                if log_y:
                    pass
                    vmin1 = vmin1 * (vmin1 / vmax1) ** 0.2
                else:
                    vmin1_new = vmin1 - 0.2 * dmax
                    if vmin1 >= 0 and vmin1_new <= 0:
                        vmin1_new = 0
                    vmin1 = vmin1_new

            if vmax is None:
                if log_y:
                    vmax1 = vmax1 * (vmax1 / vmin1) ** 0.5
                else:
                    vmax1 = vmax1 + 0.1 * dmax

            ax_one = plt.subplot(nrow, ncol, k + 1)
            if k == 0: ax_top = ax_one
            legend0 = str(name_list_dict[legend][0])
            if legend0.lower().find("ob") < 0 and legend0.find("观测") < 0 and legend0.find(
                    "实况") < 0 and legend0.find("零场") < 0:
                plt.bar(0, 0)
                plt.plot(0, 0)
            for i in range(legend_num):

                dat0 = data[k, i, :]
                index_iv = np.where(dat0 == meteva.base.IV)
                if len(index_iv[0]) == 0:
                    if color_list is None:
                        if meteva.base.plot_color_dict is not None and name_list_dict[legend][
                            i] in meteva.base.plot_color_dict.keys():
                            color_set1 = meteva.base.plot_color_dict[name_list_dict[legend][i]]
                            if k == 0:
                                plt.plot( data[k, i, :], x,label=name_list_dict[legend][i], color=color_set1,
                                         marker=marker, linestyle=linestyle[i])
                            else:
                                plt.plot( data[k, i, :],x, color=color_set1, marker=marker, linestyle=linestyle[i])
                        else:
                            if k == 0:
                                plt.plot(data[k, i, :],x,  label=name_list_dict[legend][i], marker=marker,
                                         linestyle=linestyle[i])
                            else:
                                plt.plot( data[k, i, :], x,marker=marker, linestyle=linestyle[i])
                    else:
                        if k == 0:
                            plt.plot(data[k, i, :],x,  label=name_list_dict[legend][i], color=color_list[i],
                                     marker=marker, linestyle=linestyle[i])
                        else:
                            plt.plot( data[k, i, :],x, color=color_list[i], marker=marker, linestyle=linestyle[i])
                else:
                    dat0_all = set_plot_IV_with_out_start_end(dat0)
                    plt.plot(dat0_all,x,  "--", linewidth=0.5, color="k")
                    x_iv = x[index_iv[0]]
                    dat0_iv = dat0_all[index_iv[0]]
                    plt.plot(dat0_iv,x_iv,  "x", color='k', markersize=1)
                    dat0_notiv = dat0.copy()
                    dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
                    if color_list is None:
                        if meteva.base.plot_color_dict is not None and name_list_dict[legend][
                            i] in meteva.base.plot_color_dict.keys():
                            color_set1 = meteva.base.plot_color_dict[name_list_dict[legend][i]]
                            if k == 0:
                                plt.plot( dat0_notiv,x, label=name_list_dict[legend][i], color=color_set1,
                                         marker=marker, linestyle=linestyle[i])
                            else:
                                plt.plot(dat0_notiv, x, color=color_set1, marker=marker, linestyle=linestyle[i])
                        else:
                            if k == 0:
                                plt.plot( dat0_notiv,x, label=name_list_dict[legend][i], marker=marker,
                                         linestyle=linestyle[i])
                            else:
                                plt.plot( dat0_notiv,x, marker=marker, linestyle=linestyle[i])
                    else:
                        if k == 0:
                            plt.plot( dat0_notiv,x, label=name_list_dict[legend][i], color=color_list[i],
                                     marker=marker, linestyle=linestyle[i])
                        else:
                            plt.plot( dat0_notiv, x,color=color_list[i], marker=marker, linestyle=linestyle[i])

                if tag >= 0:
                    for ii in range(len(dat0)):
                        a = x[ii]
                        b = dat0[ii]
                        if np.isnan(b) or b == meteva.base.IV: continue
                        ha = "center"
                        if ii > 0 and ii < len(dat0) - 1:
                            if b > dat0[ii - 1] and b > dat0[ii + 1]:
                                ha = "right"
                            elif b < dat0[ii - 1] and b < dat0[ii + 1]:
                                ha = "left"
                        fmt_tag = "%." + str(tag) + "f"
                        plt.text(b, a, fmt_tag % b, ha=ha, va="center",
                                 fontsize=sup_fontsize * 0.6)

            ki = k % ncol
            kj = int(k / ncol)

            if ylabel is None: ylabel = axis

            plt.yticks(yticks, yticks_labels, fontsize=sup_fontsize*0.8)
            plt.ylabel(ylabel, fontsize=sup_fontsize * 0.9)

            xminorLocator = mpl.ticker.MultipleLocator(1)  # 将x轴次刻度标签设置xmi
            ax_one.xaxis.set_minor_locator(xminorLocator)

            plt.xticks(fontsize=sup_fontsize * 0.8)
            plt.xlabel(xlabel, fontsize=sup_fontsize * 0.9)

            if vline is not None:
                plt.axvline(vline, ls="--", c="k")
            if isinstance(title, list):
                if (len(title) != subplot_num):
                    print("子图数和设置的子图标题数不一致")
                    return
                title1 = title[k]
            else:
                if subplot_num > 1:
                    title1 = title + str(name_list_dict[subplot][k])
                else:
                    title1 = title
            if subplot_num > 1:
                #y1 = 1 - 0.035 * sup_fontsize / height_fig
                plt.title(title1, fontsize=sup_fontsize, y=0.94,x = 0.01,ha="left",va = "top")
            else:
                plt.title(title1, fontsize=sup_fontsize,x = 0.05,ha="left")

            plt.ylim(-0.5, data.shape[2] - 0.5)

            if log_y:
                for tick in ax_one.yaxis.get_major_ticks():
                    tick.label1.set_fontproperties('stixgeneral')
                plt.yscale('log')

            plt.xlim(vmin1, vmax1)
            if grid is not None:
                if grid:
                    plt.grid()
                else:
                    pass
            else:
                if sparsify_yticks > 2:
                    plt.grid()

        if sup_title is not None:

            if legend_num == 1:
                strss = sup_title.split("\n")
                by = 1 - (height_suplegend - len(strss) * sup_fontsize * 0.01) / height_fig + 0.025
                plt.suptitle(sup_title, y=by, fontsize=sup_fontsize)
            else:
                width_suptitle = caculate_str_width(sup_title, sup_fontsize)
                if legend_col is None:
                    legend_col = int((width_fig - width_suptitle) * 12 / sup_fontsize)
                    if legend_col < 1: legend_col = 1
                    legend_row = int(math.ceil(legend_num / legend_col))
                    legend_col = int(math.ceil(legend_num / legend_row))
                else:
                    legend_row = int(math.ceil(legend_num / legend_col))
                strss = sup_title.split("\n")
                # by = 1 - (height_suplegend - len(strss) * sup_fontsize * 0.01) / height_fig + 0.025

                by = ax_top.bbox.ymax / fig.bbox.ymax + (len(strss) * sup_fontsize * 0.015 + 0.1) / height_fig
                plt.suptitle(sup_title, x=0, y=by, fontsize=sup_fontsize, horizontalalignment='left')

                if matplotlib.__version__ == "3.2.2":
                    by = ax_top.bbox.ymax / fig.bbox.ymax + (legend_row * sup_fontsize * 0.7 * 0.02 + 0.6) / height_fig

                else:
                    by = ax_top.bbox.ymax / fig.bbox.ymax + (legend_row * sup_fontsize * 0.7 * 0.02 + 0.15) / height_fig
                if subplot_num > 1:
                    fig.legend(fontsize=sup_fontsize * 0.7, ncol=legend_col, loc="upper right",
                               bbox_to_anchor=(1, by))
                else:
                    plt.legend(fontsize=sup_fontsize * 0.7, ncol=legend_col, loc="upper right",bbox_to_anchor=(1, by))
        else:
            if legend_num > 1:
                if legend_col is None:
                    legend_col = int(width_fig * 8 / sup_fontsize)
                    if legend_col < 1: legend_col = 1
                    legend_row = int(math.ceil(legend_num / legend_col))
                    legend_col = int(math.ceil(legend_num / legend_row))
                else:
                    legend_row = int(math.ceil(legend_num / legend_col))
                # print(height_fig)
                if matplotlib.__version__ == "3.2.2":
                    by = ax_top.bbox.ymax / fig.bbox.ymax + (legend_row * sup_fontsize * 0.9 * 0.03 + 0.6) / height_fig
                else:
                    by = ax_top.bbox.ymax / fig.bbox.ymax + (legend_row * sup_fontsize * 0.9 * 0.03 + 0.1) / height_fig

                # print(by)

                if subplot_num > 1:
                    fig.legend(fontsize=sup_fontsize * 0.8, ncol=legend_col, loc=legend_loc,
                               bbox_to_anchor=(0.52, by))
                else:
                    plt.legend(fontsize=sup_fontsize * 0.8, ncol=legend_col, loc=legend_loc,bbox_to_anchor=(0.52, by))

    else:
        print("array不能超过3维")
        return
        xticks = []
        for index in index_list:
            if not type(index) == str:
                index = str(index)
            xticks.append(index)

    if return_axs:
        return plt.gca()
    if save_path is None:
        show = True
    else:
        meteva.base.creat_path(save_path)
        plt.savefig(save_path, bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()


def plot_bar(plot_type,array,name_list_dict = None,legend = None,axis = None,ylabel = "Value",vmin = None,vmax = None,ncol = None,grid = None,tag = -1,save_path = None,show = False
        ,dpi = 300,bar_width = None,spasify_xticks = None,sparsify_xticks = None,sup_fontsize = 10,title = ""
             ,height = None,width = None,log_y = False,sup_title = None,xlabel = None,legend_col = None,color_list = None,hline = None,marker = None,
             legend_loc =  "upper center",linestyle = None,return_axs = False,
             lower=None, higher=None
             ):
    shape = array.shape


    if spasify_xticks is not None:
        print("warning: the argument spasify_xticks will be abolished, please use sparsify_xticks instead\n警告：参数spasify_xticks 将被废除，以后请使用参数sparsify_xticks代替")
        sparsify_xticks = spasify_xticks

    array = copy.deepcopy(array)

    if len(array[array!=meteva.base.IV]) ==0:
        print("所有的值都为缺失值")
        return

    if len(shape) ==1:
        if name_list_dict is None:
            name_list_dict = {}
            name_list_dict["x"] = np.arange(array.size).tolist()
            axis = "x"
        else:

            axis = list(name_list_dict.keys())[0]


        #xlabel = list(name_list_dict.keys())[0]
        #xticks = name_list_dict[xlabel]


        x_one = name_list_dict[axis][0]
        if isinstance(x_one,datetime.datetime):
            xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis],3)
        else:
            xticks_labels = []
            for local in name_list_dict[axis]:
                if isinstance(local,float):
                    xticks_labels.append(str(round(local, 6)))
                else:
                    xticks_labels.append(str(local))

        width_axis = meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize,legend_num= 1)

        width_wspace = sup_fontsize * 0.01
        width_one_subplot = width_axis +width_wspace

        spasify = 1
        if width is None:
            width = max(4,min(width_one_subplot,8))

        if width_one_subplot > width:
            spasify = int(math.ceil(width_axis / (width - width_wspace)))


        if sparsify_xticks is not None:
            xticks_font = sup_fontsize * 1.0 * sparsify_xticks * (width - width_wspace) / width_axis
            if xticks_font > sup_fontsize * 0.8:
                xticks_font = sup_fontsize * 0.8
            spasify = sparsify_xticks
        else:
            xticks_font = sup_fontsize * 0.8

        x = np.arange(len(name_list_dict[axis]))
        if array.size + 1 == len(name_list_dict[axis]):
            x = x -0.5
            if isinstance (name_list_dict[axis][0],str) and name_list_dict[axis][0].find("<") ==0:
                x[0] += 0.5
            if isinstance (name_list_dict[axis][0],str) and (name_list_dict[axis][-1].find(">") == 0):
                x[-1] -= 0.5
        elif len(x) != len(name_list_dict[axis]):
            print("坐标的size和数据的size不匹配")
            return

        xticks = x[spasify-1::spasify]
        if isinstance(x_one,datetime.datetime):
            xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis][spasify-1::spasify],3)
        else:
            xticks_labels = xticks_labels[spasify-1::spasify]



        if height is None:
            height = width / 2

        fig = plt.figure(figsize=(width, height), dpi=dpi)
        x = np.arange(array.size)
        y_plot = array[array != meteva.base.IV]
        x_plot = x[array!=meteva.base.IV]

        if log_y:
            array[array == 0] = meteva.base.IV
        if vmin is None:
            vmin1 = np.min(array[array != meteva.base.IV])
        else:
            vmin1 = vmin
        if vmax is None:
            vmax1 = np.max(array[array != meteva.base.IV])
        else:
            vmax1 = vmax

        dmax = vmax1 - vmin1
        if log_y and vmin1 <= 0:
            print("取对数坐标时数据的最小值不能<=0")

        if vmin is None:
            if log_y:
                pass
                vmin1 = vmin1 * (vmin1 / vmax1) ** 0.2
            else:
                if vmin1 < 0 or plot_type == "plot":
                    vmin1 = vmin1 - 0.1 * dmax
        if vmax is None:
            if log_y:
                vmax1 = vmax1 * (vmax1/vmin1)**0.3
            else:
                vmax1 = vmax1 + 0.2 * dmax

        if plot_type == "bar":
            if bar_width is None:
                width = 0.2
            else:
                width = bar_width

            if color_list is None:
                plt.bar(x_plot,y_plot,width= width *0.95)
            else:
                plt.bar(x_plot,y_plot,width= width *0.95,color = color_list[0])

            if lower is not None and higher is not None:
                lower1 = lower[array != meteva.base.IV]
                higher1 = higher[array != meteva.base.IV]
                for cc in range(len(x_plot)):
                    x1 = x_plot[cc]
                    plt.vlines(x1, lower1[cc], higher1[cc], colors='k')

            if len(array[array ==meteva.base.IV])>0:
                x_iv = x[array == meteva.base.IV]
                y_iv = np.zeros(x_iv.size)
                plt.plot(x_iv,y_iv,"^", color='k')
            if tag >= 0:
                # add data tag
                delta = (vmax1 - vmin1) / 20
                for a, b in zip(x_plot, y_plot):
                    fmt_tag = "%." + str(tag) + "f"
                    plt.text(a, b + delta, fmt_tag % b, ha="center", va="bottom", fontsize=sup_fontsize * 0.6)
        else:
            dat0 = array
            index_iv = np.where(dat0 == meteva.base.IV)
            if len(index_iv) == 0:
                if color_list is None:
                    plt.plot(x, dat0)
                else:
                    plt.plot(x, dat0,color = color_list[0])
            else:
                dat0_all = set_plot_IV_with_out_start_end(dat0)
                plt.plot(x, dat0_all, "--", linewidth=0.5, color="k")
                x_iv = x[index_iv[0]]
                dat0_iv = dat0_all[index_iv[0]]
                plt.plot(x_iv, dat0_iv, "x", color='k',markersize = 1)
                dat0_notiv = dat0.copy()
                dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
                if color_list is None:
                    plt.plot(x, dat0_notiv,marker = marker)
                else:
                    plt.plot(x, dat0_notiv,color = color_list[0],marker = marker)
            if tag >= 0:
                for ii in range(len(dat0)):
                    a = x[ii]
                    b = dat0[ii]
                    if np.isnan(b) or b == meteva.base.IV: continue
                    va = "center"
                    if ii > 0 and ii < len(dat0) - 1:
                        if b > dat0[ii - 1] and b > dat0[ii + 1]:
                            va = "bottom"
                        elif b < dat0[ii - 1] and b < dat0[ii + 1]:
                            va = "top"
                    fmt_tag = "%." + str(tag) + "f"
                    plt.text(a, b, fmt_tag % b, ha="center", va=va,
                             fontsize=sup_fontsize * 0.6)

        plt.xticks(xticks,xticks_labels,fontsize = xticks_font)
        plt.yticks(fontsize=sup_fontsize * 0.8)
        if xlabel is None:xlabel = axis
        plt.xlabel(xlabel,fontsize=sup_fontsize * 0.9)
        plt.ylabel(ylabel,fontsize = sup_fontsize * 0.9)

        if isinstance(title,list):
            title = title[0]
        plt.title(title,fontsize = sup_fontsize)
        plt.ylim(vmin1,vmax1)
        plt.xlim(-0.5, array.size - 0.5)
        if hline is not None:
            plt.axhline(hline,ls="--",c="k")
        if log_y:
            ax_one = plt.gca()
            for tick in ax_one.yaxis.get_major_ticks():
                tick.label1.set_fontproperties('stixgeneral')
            plt.yscale('log')
        if grid is not None:
            if grid:
                if plot_type == "bar":
                    plt.grid(axis="y")
                else:
                    plt.grid()
            else:
                pass
        else:
            if spasify > 2:
                if plot_type == "bar":
                    plt.grid(axis="y")
                else:
                    plt.grid()

    elif len(shape)==2:
        if name_list_dict is None:
            name_list_dict = {}
            list1 = np.arange(shape[0]).tolist()
            list2 = []
            for lv in list1:
                list2.append("y_" +str(lv))
            name_list_dict["y"] = list2
            name_list_dict["x"] = np.arange(shape[1]).tolist()
        keys  = list(name_list_dict.keys())
        dat = None
        if legend is None:
            if axis is None:
                legend = keys[0]
                axis = keys[1]
            else:
                if axis != keys[0]:
                    legend = keys[0]
                else:
                    legend = keys[1]
                    dat = array.T
                    #置信区间矩阵跟随转置
                    if lower is not None:
                        lower_ = lower.T
                    if higher is not None:
                        higher_ = higher.T

        if legend == keys[1]:
            dat = array.T
            # 置信区间矩阵跟随转置
            if lower is not None:
                lower_ = lower.T
            if higher is not None:
                higher_ = higher.T

        if dat is None:
            dat = array

            lower_ = lower
            higher_ = lower

        if legend not in keys:
            print("legend 参数的取值必须是name_list_dict的key")
        if axis not in keys:
            print("axis 参数的取值必须是name_list_dict的key")

        legend_list = name_list_dict[legend]
        legend_num = len(legend_list)
        if linestyle is None:
            linestyle = []
            for i in range(legend_num):
                linestyle.append("-")
        x_one = name_list_dict[axis][0]

        if isinstance(x_one,datetime.datetime):
            xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis],3)
        else:
            xticks_labels = []
            for local in name_list_dict[axis]:
                if isinstance(local,float):
                    xticks_labels.append(str(round(local, 6)))
                else:
                    xticks_labels.append(str(local))

        width_axis = meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize,legend_num)
        width_axis_labels = meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize, 1)

        width_wspace =2
        width_one_subplot = width_axis + width_wspace
        if width_one_subplot < 2: width_one_subplot = 2
        if width is None:
            width = max(4,min(width_one_subplot,8))

        spasify = 1
        if width_one_subplot > width:
            spasify = int(math.ceil(width_axis_labels / (width - width_wspace)))
            #width_one_subplot = 10

        if sparsify_xticks is not None:
            xticks_font = sup_fontsize * 1.0 * sparsify_xticks * (width - width_wspace) / width_axis_labels
            if xticks_font > sup_fontsize * 0.8:
                xticks_font = sup_fontsize * 0.8
            spasify = sparsify_xticks
        else:
            xticks_font = sup_fontsize * 0.8



        if height is None:
            height = width / 2

        if legend_col is None:
            legend_col = int(width * 8/ sup_fontsize)
            legend_row = int(math.ceil(legend_num/legend_col))
            legend_col = int(math.ceil(legend_num/legend_row))

        fig = plt.figure(figsize=(width, height), dpi=dpi)

        x = np.arange(0,len(name_list_dict[axis]),1)
        if dat.shape[1] + 1 == len(name_list_dict[axis]):
            x = x -0.5
            if isinstance (name_list_dict[axis][0],str) and name_list_dict[axis][0].find("<") ==0:
                x[0] += 0.5
            if isinstance (name_list_dict[axis][0],str) and (name_list_dict[axis][-1].find(">") == 0):
                x[-1] -= 0.5
        elif len(x) != len(name_list_dict[axis]):
            print("坐标的size和数据的size不匹配")
            return

        xticks = x[spasify-1::spasify]
        if isinstance(x_one,datetime.datetime):
            xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis][spasify-1::spasify],3)
        else:
            xticks_labels = xticks_labels[spasify-1::spasify]

        if log_y:
            array[array == 0] = meteva.base.IV
        if vmin is None:
            vmin1 = np.min(array[array != meteva.base.IV])
        else:
            vmin1 = vmin
        if vmax is None:
            vmax1 = np.max(array[array != meteva.base.IV])
        else:
            vmax1 = vmax
        dmax = vmax1 - vmin1

        if log_y and vmin1 <= 0:
            print("取对数坐标时数据的最小值不能<=0")

        if vmin is None:
            if log_y:
                pass
                vmin1 = vmin1 * (vmin1 / vmax1) ** 0.2
            else:
                vmin1_new = vmin1 - 0.1 * dmax
                if vmin1 >= 0 and vmin1_new <= 0:
                    vmin1_new = 0
                vmin1 = vmin1_new

        if vmax is None:
            if log_y:
                vmax1 = vmax1 * (vmax1/vmin1)**0.5
            else:
                vmax1 = vmax1 + 0.5 * dmax

        x = np.arange(dat.shape[1])
        if plot_type == "bar":
            if bar_width is None:
                bar_width = 0.7 / (legend_num + 2)
            legend0 = str(legend_list[0])
            if legend0.lower().find("ob")<0 and legend0.find("观测")<0 and legend0.find("实况")<0 and legend0.find("零场")<0:
                # 如果判断第一个legend不是观测想的，则跳过第一个自动颜色
                plt.bar(0,0)
            for i in range(legend_num):
                x1 = x + (i - legend_num/2 + 0.5) * bar_width
                dat0 = dat[i,:]
                y_plot = dat0[dat0 != meteva.base.IV]
                x_plot = x1[dat0 != meteva.base.IV]
                if color_list is None:
                    if meteva.base.plot_color_dict is not None and legend_list[i] in meteva.base.plot_color_dict.keys():
                        color_set1 = meteva.base.plot_color_dict[legend_list[i]]
                        bars = plt.bar(x_plot, y_plot, width=bar_width * 0.95, label=legend_list[i],color = color_set1)
                    else:
                        bars = plt.bar(x_plot, y_plot,width=bar_width * 0.95,label = legend_list[i])
                else:
                    bars = plt.bar(x_plot, y_plot, width=bar_width * 0.95, label=legend_list[i],color = color_list[i])


                if lower is not None and higher is not None:
                    lower0= lower_[i,:]
                    lower1 = lower0[dat0 != meteva.base.IV]
                    higher0 = higher_[i, :]
                    higher1 = higher0[dat0 != meteva.base.IV]
                    for cc in range(len(x_plot)):
                        x1 = x_plot[cc]
                        plt.vlines(x1, lower1[cc], higher1[cc], colors='k')

                if len(dat0[dat0 == meteva.base.IV]) > 0:
                    x_iv = x1[dat0 == meteva.base.IV]
                    y_iv = np.zeros(x_iv.size)
                    plt.plot(x_iv, y_iv, "^", color='k')
                if tag >= 0:
                    # add data tag
                    delta = (vmax1 - vmin1) / 20
                    for a, b in zip(x_plot, y_plot):
                        fmt_tag = "%." + str(tag) + "f"
                        plt.text(a, b + delta, fmt_tag % b, ha="center", va="bottom", fontsize=sup_fontsize * 0.6)
        else:
            legend0 = str(legend_list[0])
            if legend0.lower().find("ob")<0 and legend0.find("观测")<0 and legend0.find("实况")<0 and legend0.find("零场")<0:
                # 如果判断第一个legend不是观测想的，则跳过第一个自动颜色
                plt.plot(0,0)
            for i in range(legend_num):
                dat0 = dat[i, :]
                index_iv = np.where(dat0 == meteva.base.IV)
                if len(index_iv) == 0:
                    if color_list is None:
                        if meteva.base.plot_color_dict is not None and legend_list[i] in meteva.base.plot_color_dict.keys():
                            color_set1 = meteva.base.plot_color_dict[legend_list[i]]
                            lines, = plt.plot(x, dat0, label=legend_list[i],color=color_set1,linestyle = linestyle[i])
                        else:
                            lines, = plt.plot(x, dat0, label=legend_list[i],linestyle = linestyle[i])
                    else:
                        lines, = plt.plot(x, dat0, label=legend_list[i],color = color_list[i],linestyle = linestyle[i])
                else:
                    dat0_all = set_plot_IV_with_out_start_end(dat0)
                    plt.plot(x, dat0_all, "--", linewidth=0.5, color="k")
                    x_iv = x[index_iv[0]]
                    dat0_iv = dat0_all[index_iv[0]]
                    plt.plot(x_iv, dat0_iv, "x", color='k',markersize = 1)
                    dat0_notiv = dat0.copy()
                    dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
                    if color_list is None:
                        if meteva.base.plot_color_dict is not None and legend_list[i] in meteva.base.plot_color_dict.keys():
                            color_set1 = meteva.base.plot_color_dict[legend_list[i]]
                            lines, = plt.plot(x, dat0_notiv, label=name_list_dict[legend][i],color = color_set1,marker = marker,linestyle = linestyle[i])
                        else:
                            lines, = plt.plot(x, dat0_notiv, label=name_list_dict[legend][i],marker = marker,linestyle = linestyle[i])
                    else:
                        lines, = plt.plot(x, dat0_notiv, label=name_list_dict[legend][i],color = color_list[i],marker = marker,linestyle = linestyle[i])

                last_bar_color = lines.get_color()
                if lower is not None and higher is not None:
                    lower0= lower_[i,:]
                    higher0 = higher_[i, :]
                    for cc in range(len(x)):
                        if dat0[cc] != meteva.base.IV:
                            x1 = x[cc]
                            plt.vlines(x1, lower0[cc], higher0[cc], colors=last_bar_color,linewidth = 0.5)
                            plt.plot(x1, lower0[cc], marker = ".",markersize=2,linewidth = 0,color=last_bar_color)
                            plt.plot(x1, higher0[cc], marker=".", markersize=2, linewidth=0, color=last_bar_color)

                if tag >= 0:
                    for ii in range(len(dat0)):
                        a = x[ii]
                        b = dat0[ii]
                        if np.isnan(b) or b == meteva.base.IV: continue
                        va = "center"
                        if ii > 0 and ii < len(dat0) - 1:
                            if b > dat0[ii - 1] and b > dat0[ii + 1]:
                                va = "bottom"
                            elif b < dat0[ii - 1] and b < dat0[ii + 1]:
                                va = "top"
                        fmt_tag = "%." + str(tag) + "f"
                        plt.text(a, b, fmt_tag % b, ha="center", va=va,
                                 fontsize=sup_fontsize * 0.6)

        plt.legend(fontsize =sup_fontsize * 0.8,ncol = legend_col,loc =legend_loc)
        plt.xticks(xticks, xticks_labels, fontsize=xticks_font)
        plt.yticks(fontsize=sup_fontsize * 0.8)
        if xlabel is None:xlabel = axis
        plt.xlabel(xlabel, fontsize=sup_fontsize * 0.9)
        plt.ylabel(ylabel, fontsize=sup_fontsize * 0.9)
        if isinstance(title,list):
            title = title[0]
        plt.title(title, fontsize=sup_fontsize)
        plt.xlim(-0.5, dat.shape[1] - 0.5)
        plt.ylim(vmin1,vmax1)
        if hline is not None:
            plt.axhline(hline,ls="--",c="k")
        if log_y:
            ax_one = plt.gca()
            for tick in ax_one.yaxis.get_major_ticks():
                tick.label1.set_fontproperties('stixgeneral')
            plt.yscale('log')
        if grid is not None:
            if grid:
                if plot_type == "bar":
                    plt.grid(axis="y")
                else:
                    plt.grid()
            else:
                pass
        else:
            if spasify > 2:
                if plot_type == "bar":
                    plt.grid(axis="y")
                else:
                    plt.grid()

    elif len(shape)==3:
        if name_list_dict is None:
            name_list_dict = {}
            name_list_dict["z"] = np.arange(shape[0])
            list1 = np.arange(shape[1]).tolist()
            list2 = []
            for lv in list1:
                list2.append("y_" +str(lv))
            name_list_dict["y"] = list2
            name_list_dict["x"] = np.arange(shape[2])
            legend = "y"
            axis = "x"
            subplot = "z"
        keys = list(name_list_dict.keys())
        if legend is None:
            if axis is None:
                legend = keys[1]
                axis = keys[2]
                subplot = keys[0]
            else:
                if axis == keys[2]:
                    legend = keys[1]
                    subplot = keys[0]
                elif axis == keys[1]:
                    legend = keys[2]
                    subplot = keys[0]
                else:
                    legend = keys[2]
                    subplot = keys[1]
        else:
            if axis is None:
                if legend == keys[0]:
                    axis = keys[2]
                    subplot = keys[1]
                elif legend == keys[1]:
                    axis = keys[2]
                    subplot = keys[0]
                else:
                    axis = keys[1]
                    subplot = keys[0]
            else:
                indexlist = [0,1,2]
                indexlist.remove(keys.index(legend))
                indexlist.remove(keys.index(axis))
                subplot = keys[indexlist[0]]
        if legend not in keys:
            print("legend 参数的取值必须是name_list_dict的key")
        if axis not in keys:
            print("axis 参数的取值必须是name_list_dict的key")
        newshape = (keys.index(subplot),keys.index(legend),keys.index(axis))
        data = array.transpose(newshape)
        if lower is not None:
            lower_ = lower.transpose(newshape)
        if higher is not None:
            higher_ = higher.transpose(newshape)

        legend_num = len(name_list_dict[legend])
        if linestyle is None:
            linestyle = []
            for i in range(legend_num):
                linestyle.append("-")
        x_one = name_list_dict[axis][0]
        if isinstance(x_one,datetime.datetime):
            xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis],3)
        elif axis.find("dayofyear")>=0:
            xticks_labels = meteva.product.get_dayofyear_str_list(name_list_dict[axis])
        else:
            xticks_labels = []
            for local in name_list_dict[axis]:
                if isinstance(local,float):
                    xticks_labels.append(str(round(local, 6)))
                else:
                    xticks_labels.append(str(local))

        width_axis = meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize,legend_num)
        width_axis_labels =  meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize,1)

        width_wspace = sup_fontsize * 0.1
        width_one_subplot = width_axis +width_wspace
        if width_one_subplot <2:width_one_subplot = 2
        subplot_num = len(name_list_dict[subplot])
        spasify = 1


        if ncol is not None:
            if width_one_subplot >8/ncol:
                if 8/ncol - width_wspace>0:
                    spasify = int(math.ceil(width_axis_labels/(8/ncol - width_wspace)))
                else:
                    spasify = 10
                width_one_subplot = 8/ncol
        else:
            if width_one_subplot >8:
                spasify = int(math.ceil(width_axis_labels/(8 - width_wspace)))
                width_one_subplot = 8


        if sparsify_xticks is not None:
            xticks_font = sup_fontsize * 1.0 * sparsify_xticks * (width_one_subplot - width_wspace) / width_axis_labels
            if xticks_font > sup_fontsize * 0.8:
                xticks_font = sup_fontsize * 0.8
            spasify = sparsify_xticks
        else:
            xticks_font = sup_fontsize * 0.8

        x = np.arange(len(name_list_dict[axis]))
        if data.shape[2] + 1 == len(name_list_dict[axis]):
            x = x -0.5
            if isinstance (name_list_dict[axis][0],str) and name_list_dict[axis][0].find("<") ==0:
                x[0] += 0.5
            if isinstance (name_list_dict[axis][0],str) and (name_list_dict[axis][-1].find(">") == 0):
                x[-1] -= 0.5
        elif len(x) != len(name_list_dict[axis]):
            print("坐标的size和数据的size不匹配")
            return


        xticks = x[spasify-1::spasify]

        if isinstance(x_one,datetime.datetime):
            xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis][spasify-1::spasify],3)
        elif axis.find("dayofyear")>=0:
            xticks_labels = meteva.product.get_dayofyear_str_list(name_list_dict[axis][spasify-1::spasify])
        else:
            xticks_labels = xticks_labels[spasify-1::spasify]

        xticks_labels_None = []
        for i in range(len(xticks_labels)):
            xticks_labels_None.append("")


        if ncol is None:
            ncol = int(8/width_one_subplot)
            nrow = int(math.ceil(subplot_num/ncol))
            ncol = int(math.ceil(subplot_num/nrow))
        else:
            nrow = int(math.ceil(len(name_list_dict[subplot])/ncol))

        if width is None:
            width_fig = width_one_subplot * ncol
            if width_fig > 8: width_fig = 8
            if width_fig < 4: width_fig = 4
        else:
            width_fig = width

        height_axis = width_axis * 0.5
        height_hspace = sup_fontsize * 0.01
        height_suplegend = 1
        if height is None:
            height_fig = nrow * (height_axis+height_hspace) + height_suplegend
            if height_fig > 6: height_fig = 6
            if height_fig < 3: height_fig = 3
        else:
            height_fig = height



        fig = plt.figure(figsize=(width_fig, height_fig), dpi=dpi)
        x = np.arange(data.shape[2])
        hspace = height_hspace/(width_axis*0.5)
        wspace = width_wspace/width_one_subplot

        plt.subplots_adjust(left=0, bottom=0.0, right=1.0, top = 1 - height_suplegend/height_fig,
                            hspace=0.08,wspace=wspace)

        if bar_width is None:
            width = 0.7 / (legend_num + 2)
        else:
            width = bar_width
        ax_top = None
        for k in range(subplot_num):
            #print(data.shape)
            data_k = data[k,:,:]
            if log_y:
                data_k[data_k == 0] = meteva.base.IV
            if vmin is None:
                dat_k0 = data_k[data_k != meteva.base.IV]
                if dat_k0.size>0:
                    vmin1 = np.min(dat_k0)
                else:
                    vmin1 = 0
            else:
                if isinstance(vmin, list):
                    if len(vmin) != subplot_num:
                        print("vmin 参数的个数和 子图个数不一致，请重新设置")
                        return
                    else:
                        vmin1 = vmin[k]
                else:
                    vmin1 = vmin

            if vmax is None:
                dat_k0 = data_k[data_k != meteva.base.IV]
                if dat_k0.size>0:
                    vmax1 = np.max(dat_k0)
                else:
                    vmax1 = vmin1 + 0.1
            else:
                if isinstance(vmax, list):
                    if len(vmax) != subplot_num:
                        print("vmin 参数的个数和 子图个数不一致，请重新设置")
                        return
                    else:
                        vmax1 = vmax[k]
                else:
                    vmax1 = vmax

            dmax = vmax1- vmin1


            if log_y and vmin1 <0:
                print("取对数坐标时数据的最小值不能<0")
            if vmin is None:
                if log_y:
                    pass
                    vmin1 = vmin1 * (vmin1/vmax1) ** 0.2
                else:
                    vmin1_new  = vmin1 - 0.1 * dmax
                    if vmin1 >=0 and vmin1_new<=0:
                        vmin1_new = 0
                    vmin1 = vmin1_new


            if vmax is None:
                if log_y:
                    vmax1 = vmax1 * (vmax1 / vmin1) ** 0.5
                else:
                    vmax1 = vmax1 + 0.5 * dmax


            ax_one = plt.subplot(nrow, ncol, k + 1)
            if k==0:ax_top = ax_one
            legend0 = str(name_list_dict[legend][0])
            if legend0.lower().find("ob")<0 and legend0.find("观测")<0 and legend0.find("实况")<0 and legend0.find("零场")<0:
                plt.bar(0,0)
                plt.plot(0,0)
            for i in range(legend_num):
                if plot_type == "bar":
                    x1 = x + (i - legend_num / 2 + 0.5) * width
                    dat0 = data[k,i,:]
                    y_plot = dat0[dat0 != meteva.base.IV]
                    x_plot = x1[dat0 != meteva.base.IV]
                    if color_list is None:
                        if meteva.base.plot_color_dict is not None and name_list_dict[legend][i] in meteva.base.plot_color_dict.keys():
                            color_set1 = meteva.base.plot_color_dict[name_list_dict[legend][i]]
                            if k == 0:
                                bars  = plt.bar(x_plot, y_plot, width=width * 0.95, label=name_list_dict[legend][i],color = color_set1)
                            else:
                                bars  = plt.bar(x_plot, y_plot, width=width * 0.95,color = color_set1)
                        else:
                            if k ==0:
                                bars  = plt.bar(x_plot, y_plot, width=width * 0.95, label=name_list_dict[legend][i])
                            else:
                                bars  = plt.bar(x_plot, y_plot, width=width * 0.95)
                    else:
                        if k ==0:
                            bars  = plt.bar(x_plot, y_plot, width=width * 0.95, label=name_list_dict[legend][i],color = color_list[i])
                        else:
                            bars  = plt.bar(x_plot, y_plot, width=width * 0.95,color = color_list[i])

                    if lower is not None and higher is not None:
                        lower0 = lower_[k,i, :]
                        lower1 = lower0[dat0 != meteva.base.IV]
                        higher0 = higher_[k,i, :]
                        higher1 = higher0[dat0 != meteva.base.IV]
                        for cc in range(len(x_plot)):
                            x1 = x_plot[cc]
                            plt.vlines(x1, lower1[cc], higher1[cc], colors='k')


                    if tag >=0:
                        # add data tag
                        delta = (vmax1- vmin1)/20
                        for a,b in zip(x_plot,y_plot):
                            fmt_tag = "%." + str(tag)+"f"
                            plt.text(a,b + delta,fmt_tag % b,ha = "center",va = "bottom",fontsize = sup_fontsize *0.6)

                    if len(dat0[dat0 == meteva.base.IV]) > 0:
                        x_iv = x1[dat0 == meteva.base.IV]
                        y_iv = np.zeros(x_iv.size)
                        plt.plot(x_iv, y_iv, "^", color='k')

                else:
                    dat0 = data[k, i, :]
                    index_iv = np.where(dat0 == meteva.base.IV)
                    if len(index_iv[0]) == 0:
                        if color_list is None:
                            if meteva.base.plot_color_dict is not None and name_list_dict[legend][i] in meteva.base.plot_color_dict.keys():
                                color_set1 = meteva.base.plot_color_dict[name_list_dict[legend][i]]
                                if k == 0:
                                    lines, =plt.plot(x, data[k, i, :], label=name_list_dict[legend][i],color = color_set1,marker = marker,linestyle = linestyle[i])
                                else:
                                    lines, =plt.plot(x, data[k, i, :],color = color_set1,marker = marker,linestyle = linestyle[i])
                            else:
                                if k == 0:
                                    lines, =plt.plot(x, data[k, i, :], label=name_list_dict[legend][i],marker = marker,linestyle = linestyle[i])
                                else:
                                    lines, =plt.plot(x, data[k, i, :],marker = marker,linestyle = linestyle[i])
                        else:
                            if k == 0:
                                lines, =plt.plot(x, data[k, i, :], label=name_list_dict[legend][i],color = color_list[i],marker = marker,linestyle = linestyle[i])
                            else:
                                lines, =plt.plot(x, data[k, i, :],color = color_list[i],marker = marker,linestyle = linestyle[i])
                    else:
                        dat0_all = set_plot_IV_with_out_start_end(dat0)
                        plt.plot(x, dat0_all, "--", linewidth=0.5, color="k")
                        x_iv = x[index_iv[0]]
                        dat0_iv = dat0_all[index_iv[0]]
                        plt.plot(x_iv, dat0_iv, "x", color='k',markersize = 1)
                        dat0_notiv = dat0.copy()
                        dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
                        if color_list is None:
                            if meteva.base.plot_color_dict is not None and name_list_dict[legend][i] in meteva.base.plot_color_dict.keys():
                                color_set1 = meteva.base.plot_color_dict[name_list_dict[legend][i]]
                                if k == 0:
                                    lines, =plt.plot(x, dat0_notiv, label=name_list_dict[legend][i], color=color_set1,marker = marker,linestyle = linestyle[i])
                                else:
                                    lines, =plt.plot(x, dat0_notiv, color=color_set1,marker = marker,linestyle = linestyle[i])
                            else:
                                if k == 0:
                                    lines, =plt.plot(x, dat0_notiv, label=name_list_dict[legend][i],marker = marker,linestyle = linestyle[i])
                                else:
                                    lines, =plt.plot(x, dat0_notiv,marker = marker,linestyle = linestyle[i])
                        else:
                            if k == 0:
                                lines, =plt.plot(x, dat0_notiv, label=name_list_dict[legend][i],color = color_list[i],marker = marker,linestyle = linestyle[i])
                            else:
                                lines, =plt.plot(x, dat0_notiv,color = color_list[i],marker = marker,linestyle = linestyle[i])

                    last_bar_color = lines.get_color()
                    if lower is not None and higher is not None:
                        lower0 = lower_[k,i, :]
                        higher0 = higher_[k,i, :]
                        for cc in range(len(x)):
                            if dat0[cc] != meteva.base.IV:
                                x1 = x[cc]
                                plt.vlines(x1, lower0[cc], higher0[cc], colors=last_bar_color, linewidth=0.5)
                                plt.plot(x1, lower0[cc], marker=".", markersize=2, linewidth=0, color=last_bar_color)
                                plt.plot(x1, higher0[cc], marker=".", markersize=2, linewidth=0, color=last_bar_color)

                    if tag >= 0:
                        for ii in range(len(dat0)):
                            a = x[ii]
                            b = dat0[ii]
                            if np.isnan(b) or b == meteva.base.IV:continue
                            va = "center"
                            if ii>0 and ii < len(dat0) -1:
                                if b > dat0[ii-1] and b > dat0[ii+1]:
                                    va = "bottom"
                                elif b < dat0[ii-1] and b < dat0[ii+1]:
                                    va = "top"
                            fmt_tag = "%." + str(tag) + "f"
                            plt.text(a, b , fmt_tag % b, ha="center", va=va,
                                     fontsize=sup_fontsize * 0.6)


            ki = k % ncol
            kj = int(k / ncol)
            knext_row = ki + (kj+1) * ncol
            #print(knext_row)
            #print(subplot_num)
            if xlabel is None: xlabel = axis
            if knext_row>=subplot_num:
                plt.xticks(xticks, xticks_labels, fontsize=xticks_font)
                plt.xlabel(xlabel, fontsize=sup_fontsize * 0.9)
            else:
                plt.xticks(xticks,xticks_labels_None)
            xminorLocator = mpl.ticker.MultipleLocator(1)  # 将x轴次刻度标签设置xmi
            ax_one.xaxis.set_minor_locator(xminorLocator)
            plt.yticks(fontsize=sup_fontsize * 0.8)
            plt.ylabel(ylabel, fontsize=sup_fontsize * 0.9)
            if hline is not None:
                plt.axhline(hline, ls="--", c="k")
            if isinstance(title, list):
                if(len(title) != subplot_num):
                    print("子图数和设置的子图标题数不一致")
                    return
                title1 = title[k]
            else:
                if subplot_num>1:
                    title1 = title +  str(name_list_dict[subplot][k])
                else:
                    title1 = title
            if subplot_num >1:
                y1 =  1 - 0.035 *  sup_fontsize / (height_fig/nrow)
                plt.title(title1, fontsize=sup_fontsize,y = y1)
            else:
                plt.title(title1, fontsize=sup_fontsize)

            plt.xlim(-0.5, data.shape[2] - 0.5)

            if log_y:
                for tick in ax_one.yaxis.get_major_ticks():
                    tick.label1.set_fontproperties('stixgeneral')
                plt.yscale('log')

            plt.ylim(vmin1,vmax1)
            if grid is not None:
                if grid:
                    if plot_type == "bar":
                        plt.grid(axis = "y")
                    else:
                        plt.grid()
                else:
                    pass
            else:
                if spasify >2:
                    if plot_type == "bar":
                        plt.grid(axis="y")
                    else:
                        plt.grid()

        if sup_title is not None:


            if legend_num ==1:
                strss = sup_title.split("\n")
                by = 1 - (height_suplegend - len(strss) * sup_fontsize * 0.01) / height_fig + 0.025
                plt.suptitle(sup_title, y = by,fontsize=sup_fontsize )
            else:
                width_suptitle = caculate_str_width(sup_title,sup_fontsize)
                if legend_col is None:
                    legend_col = int((width_fig - width_suptitle) *12 / sup_fontsize)
                    if legend_col <1:legend_col = 1
                    legend_row = int(math.ceil(legend_num / legend_col))
                    legend_col = int(math.ceil(legend_num / legend_row))
                else:
                    legend_row = int(math.ceil(legend_num / legend_col))
                strss = sup_title.split("\n")
                #by = 1 - (height_suplegend - len(strss) * sup_fontsize * 0.01) / height_fig + 0.025


                by = ax_top.bbox.ymax / fig.bbox.ymax + (len(strss) * sup_fontsize * 0.015 + 0.1) / height_fig
                plt.suptitle(sup_title, x = 0,y = by, fontsize=sup_fontsize ,horizontalalignment='left')

                if matplotlib.__version__ == "3.2.2":
                    by = ax_top.bbox.ymax / fig.bbox.ymax + (legend_row * sup_fontsize * 0.7 * 0.02 + 0.6) / height_fig

                else:
                    by = ax_top.bbox.ymax / fig.bbox.ymax + (legend_row * sup_fontsize * 0.7 * 0.02 + 0.15) / height_fig
                if subplot_num >1:
                    fig.legend(fontsize = sup_fontsize *0.7,ncol = legend_col,loc = "upper right",
                           bbox_to_anchor=(1,by))
                else:
                    plt.legend(fontsize = sup_fontsize *0.7,ncol = legend_col,loc = "upper right")
        else:
            if legend_num > 1:
                if legend_col is None:
                    legend_col = int(width_fig * 8 / sup_fontsize)
                    if legend_col < 1: legend_col = 1
                    legend_row = int(math.ceil(legend_num / legend_col))
                    legend_col = int(math.ceil(legend_num / legend_row))
                else:
                    legend_row = int(math.ceil(legend_num / legend_col))
                #print(height_fig)
                if matplotlib.__version__ =="3.2.2" :
                    by = ax_top.bbox.ymax/fig.bbox.ymax + (legend_row * sup_fontsize * 0.9 * 0.03 + 0.6) / height_fig
                else:
                    by = ax_top.bbox.ymax / fig.bbox.ymax + (legend_row * sup_fontsize * 0.9 * 0.03 + 0.1) / height_fig

                #print(by)

                if subplot_num > 1:
                    fig.legend(fontsize=sup_fontsize * 0.8, ncol=legend_col, loc=legend_loc,
                               bbox_to_anchor=(0.52, by))
                else:
                    plt.legend(fontsize=sup_fontsize * 0.8, ncol=legend_col, loc=legend_loc)

    else:
        print("array不能超过3维")
        return
        xticks = []
        for index in index_list:
            if not type(index) == str:
                index = str(index)
            xticks.append(index)

    if return_axs:
        return plt.gca()
    if save_path is None:
        show = True
    else:
        meteva.base.creat_path(save_path)
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()



def bar_line(array,type_list,name_list_dict = None,legend = None,axis = None,vmin_bar = None,vmax_bar = None,
            vmin_line = None,vmax_line = None ,ncol = None,grid = None,tag = -1,save_path = None,show = False
        ,dpi = 300,bar_width = None,spasify_xticks = None,sparsify_xticks = None,sup_fontsize = 10,title = ""
             ,height = None,width = None,log_y_bar = False,log_y_line = False,sup_title = None,
             xlabel = None,ylabel_bar = "Value",ylabel_line = "Value",legend_col = None,color_list = None,hline = None):
    shape = array.shape


    if spasify_xticks is not None:
        print("warning: the argument spasify_xticks will be abolished, please use sparsify_xticks instead\n警告：spasify_xticks 将被废除，以后请使用参数sparsify_xticks代替")
        sparsify_xticks = spasify_xticks

    if len(array[array!=meteva.base.IV]) ==0:
        print("所有的值都为缺失值")
        return

    if len(shape)==2:
        if name_list_dict is None:
            name_list_dict = {}
            list1 = np.arange(shape[0]).tolist()
            list2 = []
            for lv in list1:
                list2.append("y_" +str(lv))
            name_list_dict["y"] = list2
            name_list_dict["x"] = np.arange(shape[1]).tolist()
        keys  = list(name_list_dict.keys())
        dat = None
        if legend is None:
            if axis is None:
                legend = keys[0]
                axis = keys[1]
            else:
                if axis != keys[0]:
                    legend = keys[0]
                else:
                    legend = keys[1]
                    dat = array.T
        if legend == keys[1]:
            dat = array.T

        if dat is None:
            dat = array
        if legend not in keys:
            print("legend 参数的取值必须是name_list_dict的key")
        if axis not in keys:
            print("axis 参数的取值必须是name_list_dict的key")

        legend_list = name_list_dict[legend]
        legend_num = len(legend_list)
        x_one = name_list_dict[axis][0]

        if isinstance(x_one,datetime.datetime):
            xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis],3)
        else:
            xticks_labels = []
            for local in name_list_dict[axis]:
                if isinstance(local,float):
                    xticks_labels.append(str(round(local, 6)))
                else:
                    xticks_labels.append(str(local))

        width_axis = meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize,legend_num)
        width_axis_labels = meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize, 1)

        width_wspace =2
        width_one_subplot = width_axis + width_wspace
        if width_one_subplot < 2: width_one_subplot = 2
        if width is None:
            width = max(4,min(width_one_subplot,8))

        spasify = 1
        if width_one_subplot > width:
            spasify = int(math.ceil(width_axis_labels / (width - width_wspace)))
            #width_one_subplot = 10

        if sparsify_xticks is not None:
            xticks_font = sup_fontsize * 1.0 * sparsify_xticks * (width - width_wspace) / width_axis_labels
            spasify = sparsify_xticks
        else:
            xticks_font = sup_fontsize * 0.8



        if height is None:
            height = width / 2

        if legend_col is None:
            legend_col = int(width * 8/ sup_fontsize)
            legend_row = int(math.ceil(legend_num/legend_col))
            legend_col = int(math.ceil(legend_num/legend_row))

        fig = plt.figure(figsize=(width, height), dpi=dpi)
        ax1 = fig.add_subplot(111)

        x = np.arange(0,len(name_list_dict[axis]),1)
        if dat.shape[1] + 1 == len(name_list_dict[axis]):
            x = x -0.5
            if isinstance (name_list_dict[axis][0],str) and name_list_dict[axis][0].find("<") ==0:
                x[0] += 0.5
            if isinstance (name_list_dict[axis][0],str) and (name_list_dict[axis][-1].find(">") == 0):
                x[-1] -= 0.5
        elif len(x) != len(name_list_dict[axis]):
            print("坐标的size和数据的size不匹配")
            return

        xticks = x[spasify-1::spasify]
        if isinstance(x_one,datetime.datetime):
            xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis][spasify-1::spasify],3)
        else:
            xticks_labels = xticks_labels[spasify-1::spasify]


        dat_bar_list = []
        dat_line_list = []
        for i in range(legend_num):
            if type_list[i] == "bar":
                if log_y_bar:
                    dat[i,dat[i,:]==0] = meteva.base.IV
                dat_bar_list.append(dat[i,:])
            else:
                if log_y_line:
                    dat[i,dat[i,:]==0] = meteva.base.IV
                dat_line_list.append(dat[i,:])

        dat_bar = np.array(dat_bar_list)
        dat_line = np.array(dat_line_list)

        if vmin_bar is None:
            vmin1_bar = np.min(dat_bar[dat_bar != meteva.base.IV])
        else:
            vmin1_bar = vmin_bar
        if vmax_bar is None:
            vmax1_bar = np.max(dat_bar[dat_bar != meteva.base.IV])
        else:
            vmax1_bar = vmax_bar
        dmax_bar = vmax1_bar - vmin1_bar

        if log_y_bar and vmin1_bar <= 0:
            print("取对数坐标时数据的最小值不能<=0")

        if vmin_bar is None:
            if log_y_bar:
                pass
                vmin1_bar = vmin1_bar * (vmin1_bar / vmax1_bar) ** 0.2
            else:
                if vmin1_bar < 0:
                    vmin1_bar = vmin1_bar - 0.1 * dmax_bar

        if vmax_bar is None:
            if log_y_bar:
                vmax1_bar = vmax1_bar * (vmax1_bar/vmin1_bar)**0.5
            else:
                vmax1_bar = vmax1_bar + 0.5 * dmax_bar



        if vmin_line is None:
            vmin1_line = np.min(dat_line[dat_line != meteva.base.IV])
        else:
            vmin1_line = vmin_line
        if vmax_line is None:
            vmax1_line = np.max(dat_line[dat_line != meteva.base.IV])
        else:
            vmax1_line = vmax_line
        dmax_line = vmax1_line - vmin1_line

        if log_y_line and vmin1_line <= 0:
            print("取对数坐标时数据的最小值不能<=0")

        if vmin_line is None:
            if log_y_line:
                pass
                vmin1_line = vmin1_line * (vmin1_line / vmax1_line) ** 0.2
            else:
                vmin1_line = vmin1_line - 0.1 * dmax_line

        if vmax_line is None:
            if log_y_line:
                vmax1_line = vmax1_line * (vmax1_line/vmin1_line)**0.5
            else:
                vmax1_line = vmax1_line + 0.5 * dmax_line

        x = np.arange(dat.shape[1])

        if bar_width is None:
            bar_width = 0.7 / (legend_num + 2)
        legend0 = str(legend_list[0])
        if legend0.lower().find("ob")<0 and legend0.find("观测")<0 and legend0.find("实况")<0 and legend0.find("零场")<0:
            # 如果判断第一个legend不是观测想的，则跳过第一个自动颜色
            plt.bar(0,0)

        for i in range(legend_num):
            if type_list[i] =="bar":
                x1 = x + (i - legend_num/2 + 0.5) * bar_width
                dat0 = dat[i,:]
                y_plot = dat0[dat0 != meteva.base.IV]
                x_plot = x1[dat0 != meteva.base.IV]
                if color_list is None:
                    if meteva.base.plot_color_dict is not None and legend_list[i] in meteva.base.plot_color_dict.keys():
                        color_set1 = meteva.base.plot_color_dict[legend_list[i]]
                        plt.bar(x_plot, y_plot, width=bar_width * 0.95, label=legend_list[i],color = color_set1)
                    else:
                        plt.bar(x_plot, y_plot,width=bar_width * 0.95,label = legend_list[i])
                else:
                    plt.bar(x_plot, y_plot, width=bar_width * 0.95, label=legend_list[i],color = color_list[i])

                if len(dat0[dat0 == meteva.base.IV]) > 0:
                    x_iv = x1[dat0 == meteva.base.IV]
                    y_iv = np.zeros(x_iv.size)
                    plt.plot(x_iv, y_iv, "^", color='k')
                if tag >= 0:
                    # add data tag
                    delta = (vmax1_bar - vmin1_bar) / 20
                    for a, b in zip(x_plot, y_plot):
                        fmt_tag = "%." + str(tag) + "f"
                        plt.text(a, b + delta, fmt_tag % b, ha="center", va="bottom", fontsize=sup_fontsize * 0.6)

        plt.yticks(fontsize=sup_fontsize * 0.8)
        plt.ylabel(ylabel_bar, fontsize=sup_fontsize * 0.9)
        if isinstance(title, list):
            title = title[0]
        plt.ylim(vmin1_bar, vmax1_bar)

        if log_y_bar:
            ax_one = plt.gca()
            for tick in ax_one.yaxis.get_major_ticks():
                tick.label1.set_fontproperties('stixgeneral')
            plt.yscale('log')
        plt.legend(fontsize =sup_fontsize * 0.8,ncol = legend_col,loc = "upper left")

        ax2 = ax1.twinx()

        for i in range(legend_num):
            if type_list[i] != "bar":
                dat0 = dat[i, :]
                index_iv = np.where(dat0 == meteva.base.IV)
                if len(index_iv) == 0:
                    if color_list is None:
                        if meteva.base.plot_color_dict is not None and legend_list[i] in meteva.base.plot_color_dict.keys():
                            color_set1 = meteva.base.plot_color_dict[legend_list[i]]
                            plt.plot(x, dat0, label=legend_list[i],color=color_set1)
                        else:
                            plt.plot(x, dat0, label=legend_list[i])
                    else:
                        plt.plot(x, dat0, label=legend_list[i],color = color_list[i])
                else:
                    dat0_all = set_plot_IV_with_out_start_end(dat0)
                    plt.plot(x, dat0_all, "--", linewidth=0.5, color="k")
                    x_iv = x[index_iv[0]]
                    dat0_iv = dat0_all[index_iv[0]]
                    plt.plot(x_iv, dat0_iv, "x", color='k',markersize = 1)
                    dat0_notiv = dat0.copy()
                    dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
                    if color_list is None:
                        if meteva.base.plot_color_dict is not None and legend_list[i] in meteva.base.plot_color_dict.keys():
                            color_set1 = meteva.base.plot_color_dict[legend_list[i]]
                            plt.plot(x, dat0_notiv, label=name_list_dict[legend][i],color = color_set1)
                        else:
                            plt.plot(x, dat0_notiv, label=name_list_dict[legend][i])
                    else:
                        plt.plot(x, dat0_notiv, label=name_list_dict[legend][i],color = color_list[i])
                if tag >= 0:
                    for ii in range(len(dat0)):
                        a = x[ii]
                        b = dat0[ii]
                        if np.isnan(b) or b == meteva.base.IV: continue
                        va = "center"
                        if ii > 0 and ii < len(dat0) - 1:
                            if b > dat0[ii - 1] and b > dat0[ii + 1]:
                                va = "bottom"
                            elif b < dat0[ii - 1] and b < dat0[ii + 1]:
                                va = "top"
                        fmt_tag = "%." + str(tag) + "f"
                        plt.text(a, b, fmt_tag % b, ha="center", va=va,
                                 fontsize=sup_fontsize * 0.6)

        plt.legend(fontsize =sup_fontsize * 0.8,ncol = legend_col,loc = "upper right")

        plt.xticks(xticks, xticks_labels, fontsize=xticks_font)
        plt.yticks(fontsize=sup_fontsize * 0.8)
        if xlabel is None:xlabel = axis
        plt.xlabel(xlabel, fontsize=sup_fontsize * 0.9)
        plt.ylabel(ylabel_line, fontsize=sup_fontsize * 0.9)
        if isinstance(title,list):
            title = title[0]
        plt.title(title, fontsize=sup_fontsize)
        plt.xlim(-0.5, dat.shape[1] - 0.5)
        plt.ylim(vmin1_line,vmax1_line)
        if hline is not None:
            plt.axhline(hline, ls="--", c="k")
        if log_y_line:
            ax_one = plt.gca()
            for tick in ax_one.yaxis.get_major_ticks():
                tick.label1.set_fontproperties('stixgeneral')
            plt.yscale('log')

        if grid is not None:
            if grid:
                plt.grid(axis="y")

            else:
                pass


    elif len(shape)==3:
        if name_list_dict is None:
            name_list_dict = {}
            name_list_dict["z"] = np.arange(shape[0])
            list1 = np.arange(shape[1]).tolist()
            list2 = []
            for lv in list1:
                list2.append("y_" + str(lv))
            name_list_dict["y"] = list2
            name_list_dict["x"] = np.arange(shape[2])
            legend = "y"
            axis = "x"
            subplot = "z"
        keys = list(name_list_dict.keys())
        if legend is None:
            if axis is None:
                legend = keys[1]
                axis = keys[2]
                subplot = keys[0]
            else:
                if axis == keys[2]:
                    legend = keys[1]
                    subplot = keys[0]
                elif axis == keys[1]:
                    legend = keys[2]
                    subplot = keys[0]
                else:
                    legend = keys[2]
                    subplot = keys[1]
        else:
            if axis is None:
                if legend == keys[0]:
                    axis = keys[2]
                    subplot = keys[1]
                elif legend == keys[1]:
                    axis = keys[2]
                    subplot = keys[0]
                else:
                    axis = keys[1]
                    subplot = keys[0]
            else:
                indexlist = [0, 1, 2]
                indexlist.remove(keys.index(legend))
                indexlist.remove(keys.index(axis))
                subplot = keys[indexlist[0]]
        if legend not in keys:
            print("legend 参数的取值必须是name_list_dict的key")
        if axis not in keys:
            print("axis 参数的取值必须是name_list_dict的key")
        newshape = (keys.index(subplot), keys.index(legend), keys.index(axis))
        data = array.transpose(newshape)
        legend_num = len(name_list_dict[legend])

        x_one = name_list_dict[axis][0]
        if isinstance(x_one, datetime.datetime):
            xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis], 3)
        elif axis.find("dayofyear") >= 0:
            xticks_labels = meteva.product.get_dayofyear_str_list(name_list_dict[axis])
        else:
            xticks_labels = []
            for local in name_list_dict[axis]:
                if isinstance(local, float):
                    xticks_labels.append(str(round(local, 6)))
                else:
                    xticks_labels.append(str(local))

        width_axis = meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize, legend_num)
        width_axis_labels = meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize, 1)

        width_wspace = sup_fontsize * 0.1
        width_one_subplot = width_axis + width_wspace
        if width_one_subplot < 2: width_one_subplot = 2
        subplot_num = len(name_list_dict[subplot])
        spasify = 1

        if ncol is not None:
            if width_one_subplot > 8 / ncol:
                spasify = int(math.ceil(width_axis_labels / (8 / ncol - width_wspace)))
                width_one_subplot = 8 / ncol
        else:
            if width_one_subplot > 8:
                spasify = int(math.ceil(width_axis_labels / (8 - width_wspace)))
                width_one_subplot = 8

        if sparsify_xticks is not None:
            xticks_font = sup_fontsize * 1.0 * sparsify_xticks * (width_one_subplot - width_wspace) / width_axis_labels
            spasify = sparsify_xticks
        else:
            xticks_font = sup_fontsize * 0.8

        x = np.arange(len(name_list_dict[axis]))
        if data.shape[2] + 1 == len(name_list_dict[axis]):
            x = x - 0.5
            if isinstance(name_list_dict[axis][0], str) and name_list_dict[axis][0].find("<") == 0:
                x[0] += 0.5
            if isinstance(name_list_dict[axis][0], str) and (name_list_dict[axis][-1].find(">") == 0):
                x[-1] -= 0.5
        elif len(x) != len(name_list_dict[axis]):
            print("坐标的size和数据的size不匹配")
            return

        xticks = x[spasify-1::spasify]

        if isinstance(x_one, datetime.datetime):
            xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis][spasify-1::spasify], 3)
        elif axis.find("dayofyear") >= 0:
            xticks_labels = meteva.product.get_dayofyear_str_list(name_list_dict[axis][spasify-1::spasify])
        else:
            xticks_labels = xticks_labels[spasify-1::spasify]

        xticks_labels_None = []
        for i in range(len(xticks_labels)):
            xticks_labels_None.append("")

        if ncol is None:
            ncol = int(8 / width_one_subplot)
            nrow = int(math.ceil(subplot_num / ncol))
            ncol = int(math.ceil(subplot_num / nrow))
        else:
            nrow = int(math.ceil(len(name_list_dict[subplot]) / ncol))

        if width is None:
            width_fig = width_one_subplot * ncol
            if width_fig > 8: width_fig = 8
            if width_fig < 4: width_fig = 4
        else:
            width_fig = width

        height_axis = width_axis * 0.5
        height_hspace = sup_fontsize * 0.01
        height_suplegend = 1
        if height is None:
            height_fig = nrow * (height_axis + height_hspace) + height_suplegend
            if height_fig > 6: height_fig = 6
            if height_fig < 3: height_fig = 3
        else:
            height_fig = height

        fig = plt.figure(figsize=(width_fig, height_fig), dpi=dpi)
        x = np.arange(data.shape[2])
        hspace = height_hspace / (width_axis * 0.5)
        wspace = width_wspace / width_one_subplot

        plt.subplots_adjust(left=0, bottom=0.0, right=1.0, top=1 - height_suplegend / height_fig,
                            hspace=0.08, wspace=wspace)

        if bar_width is None:
            width = 0.7 / (legend_num + 2)
        else:
            width = bar_width
        ax_top = None
        for k in range(subplot_num):
            # print(data.shape)
            data_k = data[k, :, :]

            dat_bar_list = []
            dat_line_list = []
            for i in range(legend_num):
                if type_list[i] == "bar":
                    if log_y_bar:
                        data_k[i, data_k[i, :] == 0] = meteva.base.IV
                    dat_bar_list.append(data_k[i, :])
                else:
                    if log_y_line:
                        data_k[i, data_k[i, :] == 0] = meteva.base.IV
                    dat_line_list.append(data_k[i, :])

            dat_bar = np.array(dat_bar_list)
            dat_line = np.array(dat_line_list)

            if vmin_bar is None:
                dat_k0 = dat_bar[dat_bar != meteva.base.IV]
                if dat_k0.size > 0:
                    vmin1_bar = np.min(dat_k0)
                else:
                    vmin1_bar = 0
            else:
                if isinstance(vmin_bar, list):
                    if len(vmin_bar) != subplot_num:
                        print("vmin 参数的个数和 子图个数不一致，请重新设置")
                        return
                    else:
                        vmin1_bar = vmin_bar[k]
                else:
                    vmin1_bar = vmin_bar

            if vmax_bar is None:
                dat_k0 = dat_bar[dat_bar != meteva.base.IV]
                if dat_k0.size > 0:
                    vmax1_bar = np.max(dat_k0)
                else:
                    vmax1_bar = vmin1_bar + 0.1
            else:
                if isinstance(vmax_bar, list):
                    if len(vmax_bar) != subplot_num:
                        print("vmin 参数的个数和 子图个数不一致，请重新设置")
                        return
                    else:
                        vmax1_bar = vmax_bar[k]
                else:
                    vmax1_bar = vmax_bar

            dmax_bar = vmax1_bar - vmin1_bar

            if log_y_bar and vmin1_bar < 0:
                print("取对数坐标时数据的最小值不能<0")
            if vmin_bar is None:
                if log_y_bar:
                    pass
                    vmin1_bar = vmin1_bar * (vmin1_bar / vmax1_bar) ** 0.2
                else:
                    if vmin1_bar < 0:
                        vmin1_bar = vmin1_bar - 0.1 * dmax_bar
            if vmax_bar is None:
                if log_y_bar:
                    vmax1_bar = vmax1_bar * (vmax1_bar / vmin1_bar) ** 0.5
                else:
                    vmax1_bar = vmax1_bar + 0.5 * dmax_bar


            if vmin_line is None:
                dat_k0 = dat_line[dat_line != meteva.base.IV]
                if dat_k0.size > 0:
                    vmin1_line = np.min(dat_k0)
                else:
                    vmin1_line = 0
            else:
                if isinstance(vmin_line, list):
                    if len(vmin_line) != subplot_num:
                        print("vmin 参数的个数和 子图个数不一致，请重新设置")
                        return
                    else:
                        vmin1_line = vmin_line[k]
                else:
                    vmin1_line = vmin_line

            if vmax_line is None:
                dat_k0 = dat_line[dat_line != meteva.base.IV]
                if dat_k0.size > 0:
                    vmax1_line = np.max(dat_k0)
                else:
                    vmax1_line = vmin1_line + 0.1
            else:
                if isinstance(vmax_line, list):
                    if len(vmax_line) != subplot_num:
                        print("vmin 参数的个数和 子图个数不一致，请重新设置")
                        return
                    else:
                        vmax1_line = vmax_line[k]
                else:
                    vmax1_line = vmax_line

            dmax_line = vmax1_line - vmin1_line

            if log_y_line and vmin1_line < 0:
                print("取对数坐标时数据的最小值不能<0")
            if vmin_line is None:
                if log_y_line:
                    pass
                    vmin1_line = vmin1_line * (vmin1_line / vmax1_line) ** 0.2
                else:
                    vmin1_line = vmin1_line - 0.1 * dmax_line
            if vmax_line is None:
                if log_y_line:
                    vmax1_line = vmax1_line * (vmax1_line / vmin1_line) ** 0.5
                else:
                    vmax1_line = vmax1_line + 0.5 * dmax_line


            ax_one = plt.subplot(nrow, ncol, k + 1)
            if k == 0: ax_top = ax_one
            legend0 = str(name_list_dict[legend][0])
            if legend0.lower().find("ob") < 0 and legend0.find("观测") < 0 and legend0.find("实况") < 0 and legend0.find(
                    "零场") < 0:
                plt.bar(0, 0)
                plt.plot(0, 0)
            for i in range(legend_num):
                if type_list[i] == "bar":
                    x1 = x + (i - legend_num / 2 + 0.5) * width
                    dat0 = data[k, i, :]
                    y_plot = dat0[dat0 != meteva.base.IV]
                    x_plot = x1[dat0 != meteva.base.IV]
                    if color_list is None:
                        if meteva.base.plot_color_dict is not None and name_list_dict[legend][
                            i] in meteva.base.plot_color_dict.keys():
                            color_set1 = meteva.base.plot_color_dict[name_list_dict[legend][i]]
                            if k == 0:
                                plt.bar(x_plot, y_plot, width=width * 0.95, label=name_list_dict[legend][i],
                                        color=color_set1)
                            else:
                                plt.bar(x_plot, y_plot, width=width * 0.95, color=color_set1)
                        else:
                            if k == 0:
                                plt.bar(x_plot, y_plot, width=width * 0.95, label=name_list_dict[legend][i])
                            else:
                                plt.bar(x_plot, y_plot, width=width * 0.95)
                    else:
                        if k == 0:
                            plt.bar(x_plot, y_plot, width=width * 0.95, label=name_list_dict[legend][i],
                                    color=color_list[i])
                        else:
                            plt.bar(x_plot, y_plot, width=width * 0.95, color=color_list[i])
                    if tag >= 0:
                        # add data tag
                        delta = (vmax1_bar - vmin1_bar) / 20
                        for a, b in zip(x_plot, y_plot):
                            fmt_tag = "%." + str(tag) + "f"
                            plt.text(a, b + delta, fmt_tag % b, ha="center", va="bottom", fontsize=sup_fontsize * 0.6)

                    if len(dat0[dat0 == meteva.base.IV]) > 0:
                        x_iv = x1[dat0 == meteva.base.IV]
                        y_iv = np.zeros(x_iv.size)
                        plt.plot(x_iv, y_iv, "^", color='k')
            for i in range(legend_num):
                if type_list[i] != "bar":
                    dat0 = data[k, i, :]
                    index_iv = np.where(dat0 == meteva.base.IV)
                    if len(index_iv[0]) == 0:
                        if color_list is None:
                            if meteva.base.plot_color_dict is not None and name_list_dict[legend][i] in meteva.base.plot_color_dict.keys():
                                color_set1 = meteva.base.plot_color_dict[name_list_dict[legend][i]]
                                if k == 0:
                                    plt.plot(x, data[k, i, :], label=name_list_dict[legend][i], color=color_set1)
                                else:
                                    plt.plot(x, data[k, i, :], color=color_set1)
                            else:
                                if k == 0:
                                    plt.plot(x, data[k, i, :], label=name_list_dict[legend][i])
                                else:
                                    plt.plot(x, data[k, i, :])
                        else:
                            if k == 0:
                                plt.plot(x, data[k, i, :], label=name_list_dict[legend][i], color=color_list[i])
                            else:
                                plt.plot(x, data[k, i, :], color=color_list[i])
                    else:
                        dat0_all = set_plot_IV_with_out_start_end(dat0)
                        plt.plot(x, dat0_all, "--", linewidth=0.5, color="k")
                        x_iv = x[index_iv[0]]
                        dat0_iv = dat0_all[index_iv[0]]
                        plt.plot(x_iv, dat0_iv, "x", color='k',markersize = 1)
                        dat0_notiv = dat0.copy()
                        dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
                        if color_list is None:
                            if meteva.base.plot_color_dict is not None and name_list_dict[legend][i] in meteva.base.plot_color_dict.keys():
                                color_set1 = meteva.base.plot_color_dict[name_list_dict[legend][i]]
                                if k == 0:
                                    plt.plot(x, dat0_notiv, label=name_list_dict[legend][i], color=color_set1)
                                else:
                                    plt.plot(x, dat0_notiv, color=color_set1)
                            else:
                                if k == 0:
                                    plt.plot(x, dat0_notiv, label=name_list_dict[legend][i])
                                else:
                                    plt.plot(x, dat0_notiv)
                        else:
                            if k == 0:
                                plt.plot(x, dat0_notiv, label=name_list_dict[legend][i], color=color_list[i])
                            else:
                                plt.plot(x, dat0_notiv, color=color_list[i])

                    if tag >= 0:
                        for ii in range(len(dat0)):
                            a = x[ii]
                            b = dat0[ii]
                            if np.isnan(b) or b == meteva.base.IV: continue
                            va = "center"
                            if ii > 0 and ii < len(dat0) - 1:
                                if b > dat0[ii - 1] and b > dat0[ii + 1]:
                                    va = "bottom"
                                elif b < dat0[ii - 1] and b < dat0[ii + 1]:
                                    va = "top"
                            fmt_tag = "%." + str(tag) + "f"
                            plt.text(a, b, fmt_tag % b, ha="center", va=va,
                                     fontsize=sup_fontsize * 0.6)

            ki = k % ncol
            kj = int(k / ncol)
            knext_row = ki + (kj + 1) * ncol
            # print(knext_row)
            # print(subplot_num)
            if xlabel is None: xlabel = axis
            if knext_row >= subplot_num:
                # plt.xticks(x[::spasify], name_list_dict[axis][::spasify], fontsize=sup_fontsize * 0.8)
                plt.xticks(xticks, xticks_labels, fontsize=xticks_font)
                plt.xlabel(xlabel, fontsize=sup_fontsize * 0.9)
            else:
                plt.xticks(xticks, xticks_labels_None)
            xminorLocator = mpl.ticker.MultipleLocator(1)  # 将x轴次刻度标签设置xmi
            ax_one.xaxis.set_minor_locator(xminorLocator)
            plt.yticks(fontsize=sup_fontsize * 0.8)

            plt.ylabel(ylabel_line, fontsize=sup_fontsize * 0.9)
            if hline is not None:
                plt.axhline(hline, ls="--", c="k")
            if isinstance(title, list):
                if (len(title) != subplot_num):
                    print("子图数和设置的子图标题数不一致")
                    return
                title1 = title[k]
            else:
                if subplot_num > 1:
                    title1 = title + str(name_list_dict[subplot][k])
                else:
                    title1 = title
            if subplot_num > 1:
                y1 = 1 - 0.035 * sup_fontsize / (height_fig / nrow)
                plt.title(title1, fontsize=sup_fontsize, y=y1)
            else:
                plt.title(title1, fontsize=sup_fontsize)

            plt.xlim(-0.5, data.shape[2] - 0.5)


        if sup_title is not None:

            if legend_num == 1:
                strss = sup_title.split("\n")
                by = 1 - (height_suplegend - len(strss) * sup_fontsize * 0.01) / height_fig + 0.025
                plt.suptitle(sup_title, y=by, fontsize=sup_fontsize)
            else:
                width_suptitle = caculate_str_width(sup_title, sup_fontsize)
                if legend_col is None:
                    legend_col = int((width_fig - width_suptitle) * 12 / sup_fontsize)
                    if legend_col < 1: legend_col = 1
                    legend_row = int(math.ceil(legend_num / legend_col))
                    legend_col = int(math.ceil(legend_num / legend_row))
                else:
                    legend_row = int(math.ceil(legend_num / legend_col))
                strss = sup_title.split("\n")
                # by = 1 - (height_suplegend - len(strss) * sup_fontsize * 0.01) / height_fig + 0.025

                by = ax_top.bbox.ymax / fig.bbox.ymax + (len(strss) * sup_fontsize * 0.015 + 0.1) / height_fig
                plt.suptitle(sup_title, x=0, y=by, fontsize=sup_fontsize, horizontalalignment='left')

                # by = 1 - (height_suplegend - legend_row * sup_fontsize * 0.9 * 0.02) / height_fig + 0.05
                if matplotlib.__version__ == "3.2.2":
                    by = ax_top.bbox.ymax / fig.bbox.ymax + (legend_row * sup_fontsize * 0.7 * 0.02 + 0.6) / height_fig
                else:
                    by = ax_top.bbox.ymax / fig.bbox.ymax + (legend_row * sup_fontsize * 0.7 * 0.02 + 0.15) / height_fig
                if subplot_num > 1:
                    fig.legend(fontsize=sup_fontsize * 0.7, ncol=legend_col, loc="upper right",
                               bbox_to_anchor=(1, by))
                else:
                    plt.legend(fontsize=sup_fontsize * 0.7, ncol=legend_col, loc="upper right")
        else:
            if legend_num > 1:
                if legend_col is None:
                    legend_col = int(width_fig * 8 / sup_fontsize)
                    if legend_col < 1: legend_col = 1
                    legend_row = int(math.ceil(legend_num / legend_col))
                    legend_col = int(math.ceil(legend_num / legend_row))
                else:
                    legend_row = int(math.ceil(legend_num / legend_col))
                # print(height_fig)
                if matplotlib.__version__ == "3.2.2":
                    by = ax_top.bbox.ymax / fig.bbox.ymax + (legend_row * sup_fontsize * 1 * 0.03 + 0.6) / height_fig
                else:
                    by = ax_top.bbox.ymax / fig.bbox.ymax + (legend_row * sup_fontsize * 0.9 * 0.03 + 0.1) / height_fig

                # by = 1 - (height_suplegend - legend_row * sup_fontsize * 0.9 * 0.03) / height_fig + 0.025
                # print(by)

                if subplot_num > 1:
                    fig.legend(fontsize=sup_fontsize * 0.8, ncol=legend_col, loc="upper center",
                               bbox_to_anchor=(0.52, by))
                else:
                    plt.legend(fontsize=sup_fontsize * 0.8, ncol=legend_col, loc="upper center")

    else:
        print("array不能超过3维")
        return

    if save_path is None:
        show = True
    else:
        meteva.base.creat_path(save_path)
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()



def bar(array,name_list_dict = None,legend = None,axis = None,ylabel = "Value",vmin = None,vmax = None,ncol = None,grid = None,tag = -1,save_path = None,show = False
        ,dpi = 300,bar_width = None,title = "",spasify_xticks = None,sparsify_xticks = None,sup_fontsize = 10,width = None,height = None,log_y = False,sup_title = None,xlabel = None,
        legend_col = None,color_list = None,hline = None,marker = None,return_axs=False,
        lower = None,higher = None):

    axs = plot_bar("bar",array = array,name_list_dict=name_list_dict,legend = legend,axis = axis,ylabel = ylabel,vmin= vmin,vmax = vmax,ncol =ncol,grid = grid,tag = tag,
             spasify_xticks = spasify_xticks,sparsify_xticks =sparsify_xticks,save_path = save_path,show = show,
             dpi = dpi,bar_width=bar_width,sup_fontsize= sup_fontsize,title=title,width = width,height = height,log_y = log_y,sup_title= sup_title,xlabel = xlabel,
             legend_col = legend_col,color_list=color_list,hline = hline,marker=marker,return_axs=return_axs,
                   lower=lower, higher=higher
                   )
    return axs


def plot(array,name_list_dict = None,legend = None,axis = None,ylabel = "Value",vmin = None,vmax = None,ncol = None,grid = None,tag = -1,save_path = None,show = False,dpi = 300
         ,title ="",spasify_xticks = None,sparsify_xticks = None,sup_fontsize = 10,width = None,height = None,log_y = False,sup_title = None,xlabel = None,legend_col = None,color_list = None,hline = None,
         marker = None,legend_loc ="upper center",linestyle = None,return_axs = False, lower=None, higher=None):

    axs = plot_bar("line",array,name_list_dict=name_list_dict,legend = legend,axis = axis,ylabel = ylabel,vmin= vmin,vmax = vmax,ncol =ncol,grid = grid,tag=tag ,
             spasify_xticks = spasify_xticks,sparsify_xticks = sparsify_xticks,save_path = save_path,show = show,
             dpi = dpi,sup_fontsize= sup_fontsize,title=title,width = width,height = height,log_y = log_y,sup_title = sup_title,xlabel = xlabel,
             legend_col =legend_col,color_list=color_list,hline = hline,marker = marker,legend_loc =legend_loc,linestyle=linestyle,return_axs = return_axs,
                   lower=lower, higher=higher
                   )
    if return_axs:
        return axs


def myheatmap(ax_one,data_0,cmap,clevs,annot=1,fontsize=10):

    data_k = data_0.copy()
    nx = data_k.shape[1]
    ny = data_k.shape[0]
    x = np.arange(nx+1)-0.5
    y = np.arange(ny+1)-0.5

    data_k[data_k==meteva.base.IV] = np.nan
    norm = BoundaryNorm(clevs, ncolors=cmap.N - 1)
    im = ax_one.pcolormesh(x, y, data_k, cmap=cmap, norm=norm)
    im.update_scalarmappable()
    if annot is not None  and annot>=0:
        facecolors = im.get_facecolors()
        facecolors = facecolors.reshape(ny, nx, 4)
        fmt_tag = "%." + str(annot) + "f"
        for i in range(nx):
            for j in range(ny):
                data_ijk = data_k[j, i]
                if not np.isnan(data_ijk):
                    # 获取网格的颜色
                    color = facecolors[j, i, :]
                    # 计算亮度
                    rgb = mpl.colors.colorConverter.to_rgba_array(color)[:, :3]
                    rgb = np.where(rgb <= .03928, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
                    lum = rgb.dot([.2126, .7152, .0722])

                    text_color = ".15" if lum > .408 else "w"
                    ax_one.text(i, j, fmt_tag % data_ijk, ha="center", va="center",
                             fontsize=fontsize, c=text_color)
    fig = plt.gcf()
    fig.colorbar(im, ax=ax_one)

def mesh(array,name_list_dict = None,axis_x = None,axis_y = None,cmap = "rainbow",clevs = None,ncol = None,annot =None,save_path = None,show = False,dpi = 300,
         spasify_xticks = None,sup_fontsize = 10,title ="",sup_title = None,width = None,height = None,rect = None,rect_color = "r"):

    mesh_contourf("mesh",array,name_list_dict=name_list_dict,axis_x=axis_x,axis_y=axis_y,cmap=cmap,clevs=clevs,
                 ncol=ncol,annot=annot,save_path=save_path,show=show,dpi=dpi,spasify_xticks=spasify_xticks,
                 sup_fontsize=sup_fontsize,title=title,sup_title = sup_title,width=width,height=height,rect=rect,rect_color=rect_color)

def contourf(array,name_list_dict = None,axis_x = None,axis_y = None,cmap = "rainbow",clevs = None,ncol = None,annot =None,save_path = None,show = False,dpi = 300,
         spasify_xticks = None,sup_fontsize = 10,title ="",sup_title = None,width = None,height = None,rect = None,rect_color = "r"):

    mesh_contourf("contourf",array,name_list_dict=name_list_dict,axis_x=axis_x,axis_y=axis_y,cmap=cmap,clevs=clevs,
                 ncol=ncol,annot=annot,save_path=save_path,show=show,dpi=dpi,spasify_xticks=spasify_xticks,
                 sup_fontsize=sup_fontsize,title=title,sup_title = sup_title,width=width,height=height,rect=rect,rect_color=rect_color)

def mesh_contourf(type,array,name_list_dict = None,axis_x = None,axis_y = None,cmap = "rainbow",clevs = None,ncol = None,annot =None,save_path = None,show = False,dpi = 300,
         spasify_xticks = None,xticks_inter = None,sup_fontsize = 10,title ="",sup_title =None,width = None,height = None,rect = None,rect_color = "r",extend = None):

    shape = array.shape
    index = np.where(array!=meteva.base.IV)
    if index[0].size == 0:
        print("所有的值都为缺失值")
        return

    if len(shape) == 3 or len(shape) == 2:
        if len(shape) == 2:
            array1 = array[np.newaxis,:]
            if name_list_dict is not None:
                name_list_dict1 = {}
                name_list_dict1["z"] = [0]
                for key in name_list_dict.keys():
                    name_list_dict1[key] = name_list_dict[key]
                name_list_dict = name_list_dict1

        else:
            array1 = array
        shape = array1.shape
        if name_list_dict is None:

            name_list_dict = {}
            name_list_dict["z"] = np.arange(shape[0])
            list1 = np.arange(shape[1]).tolist()
            list2 = []
            for lv in list1:
                list2.append("y_" + str(lv))
            name_list_dict["y"] = list2
            name_list_dict["x"] = np.arange(shape[2])
            legend = "y"
            axis_x = "x"
            subplot = "z"
        keys = list(name_list_dict.keys())
        if axis_y is None:
            if axis_x is None:
                axis_y = keys[1]
                axis_x = keys[2]
                subplot = keys[0]
            else:
                if axis_x == keys[2]:
                    axis_y = keys[1]
                    subplot = keys[0]
                elif axis_x == keys[1]:
                    axis_y = keys[2]
                    subplot = keys[0]
                else:
                    axis_y = keys[2]
                    subplot = keys[1]
        else:
            if axis_x is None:
                if axis_y == keys[0]:
                    axis_x = keys[2]
                    subplot = keys[1]
                elif axis_y == keys[1]:
                    axis_x = keys[2]
                    subplot = keys[0]
                else:
                    axis_x = keys[1]
                    subplot = keys[0]
            else:
                indexlist = [0, 1, 2]
                indexlist.remove(keys.index(axis_y))
                indexlist.remove(keys.index(axis_x))
                subplot = keys[indexlist[0]]
        if axis_y not in keys:
            print("axis_y 参数的取值必须是name_list_dict的key")
        if axis_x not in keys:
            print("axis_x 参数的取值必须是name_list_dict的key")
        newshape = (keys.index(subplot), keys.index(axis_y), keys.index(axis_x))
        #print(array1.shape)
        data = array1.transpose(newshape)
        legend_num = len(name_list_dict[axis_y])

        x_one = name_list_dict[axis_x][0]
        if isinstance(x_one, datetime.datetime):
            xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis_x], 3)
        else:
            xticks_labels = []
            for local in name_list_dict[axis_x]:
                if isinstance(local,float):
                    if int(local) == local:
                        local = int(local)
                xticks_labels.append(str(local))

        width_axis = meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize, legend_num)
        width_axis_labels = meteva.base.plot_tools.caculate_axis_width(xticks_labels, sup_fontsize, 1)

        width_wspace = sup_fontsize * 0.1
        width_one_subplot = width_axis + width_wspace
        if width_one_subplot < 1.5: width_one_subplot = 1.5
        subplot_num = len(name_list_dict[subplot])
        spasify = 1
        if ncol is not None:
            if width_one_subplot > 8/ ncol:
                spasify = int(math.ceil(width_axis_labels / (10 / ncol - width_wspace)))
                width_one_subplot = 8/ ncol
        else:
            if width_one_subplot > 8:
                spasify = int(math.ceil(width_axis_labels / (10 - width_wspace)))
                width_one_subplot = 8

        if axis_x == "lon" or axis_x == "lat":
            vmax = name_list_dict[axis_x][-1]
            vmin = name_list_dict[axis_x][0]
            delta = name_list_dict[axis_x][1] - name_list_dict[axis_x][0]
            rlon = vmax - vmin
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
            vmax = inte * ((int)(vmax / inte) + 0.5)

            xticks = np.arange(vmin, vmax, inte)
            if axis_x == "lon":
                xticks_labels = []

                for x in range(len(xticks)):
                    v1 = xticks[x]
                    if v1 >= 0 and v1 <= 180:
                        if abs(v1 - int(v1)) < 1e-7:
                            xticks_labels.append(str(int(round(v1, 6))) + "°E")
                        else:
                            xticks_labels.append(str(round(v1, 6)) + "°E")
                    else:
                        if v1 < 0:
                            v2 = -v1
                        else:
                            v2 = 360 - v1
                        if abs(v1 - int(v1)) < 1e-7:
                            xticks_labels.append(str(int(round(v2, 6))) + "°W")
                        else:
                            xticks_labels.append(str(round(v2, 6)) + "°W")
            else:

                xticks_labels = []
                for y in range(len(xticks)):
                    v1 = xticks[y]
                    if abs(v1 - int(v1)) < 1e-7:
                        v1 = int(round(v1, 6))
                    else:
                        v1 = round(v1, 6)
                    if xticks[y] >= 0:
                        xticks_labels.append(str(v1) + "°N")
                    else:
                        xticks_labels.append(str(v1) + "°S")
            xticks_font = sup_fontsize * 0.8
            xticks = np.round((xticks-name_list_dict[axis_x][0])/delta,1).astype(np.int32)

        else:
            if spasify_xticks is not None:
                xticks_font = sup_fontsize * 1.0 * spasify_xticks * (width - width_wspace) / width_axis_labels
                spasify = spasify_xticks
            else:
                xticks_font = sup_fontsize * 0.8

            x = np.arange(len(name_list_dict[axis_x]))
            xticks = x[spasify-1::spasify]
            if isinstance(x_one, datetime.datetime):
                xticks_labels = meteva.product.get_time_str_list(name_list_dict[axis_x][spasify-1::spasify], 3)
            else:
                xticks_labels = xticks_labels[spasify-1::spasify]
        #
        # if axis_x =="lon":
        #     xticks_labels[-1] +="°E"
        # if axis_x=="lat":
        #     if int(xticks_labels[-1]) >0:
        #         xticks_labels[-1] += "°N"
        #     else:
        #         xticks_labels_new = []
        #         for xticks1 in xticks_labels:
        #             xticks_labels_new.append(xticks1[1:]) #remove  "-"
        #         xticks_labels_new[-1] += "°S"
        #         xticks_labels = xticks_labels_new


        xticks_labels_None = []
        for i in range(len(xticks_labels)):
            xticks_labels_None.append("")

        y = np.arange(len(name_list_dict[axis_y])+1) -0.5
        yticks = np.arange(len(name_list_dict[axis_y]))
        y_one = name_list_dict[axis_y][0]
        yticks_labels =[]
        if isinstance(y_one, datetime.datetime):
            for time1 in  name_list_dict[axis_y]:
                str1 = "%02d" % time1.day + "日" + "%02d" % time1.hour + "时"
                yticks_labels.append(str1)
        else:
            for local in name_list_dict[axis_y]:
                if isinstance(local, float):
                    if int(local) == local:
                        local = int(local)
                yticks_labels.append(str(local))

        if ncol is None:
            ncol = int(round(8 / width_one_subplot))

            nrow = int(math.ceil(subplot_num / ncol))
            ncol = int(math.ceil(subplot_num / nrow))
        else:
            nrow = int(math.ceil(len(name_list_dict[subplot]) / ncol))
        if width is None:
            width_fig = width_one_subplot * ncol
            if width_fig > 8:width_fig = 8
            if width_fig < 4: width_fig = 4
        else:
            width_fig = width


        height_axis = (width_one_subplot - width_wspace) * data.shape[1] / data.shape[2]
        height_hspace = sup_fontsize * 0.01
        height_suplegend = 0
        if height is None:
            height_fig = nrow * (height_axis + height_hspace) + height_suplegend
            if height_fig > 6:height_fig = 6
            if height_fig < 3: height_fig = 3
        else:
            height_fig = height

        fig = plt.figure(figsize=(width_fig, height_fig), dpi=dpi)
        x = np.arange(data.shape[2]+1) -0.5
        axes_list = []
        hspace = 0.1 * sup_fontsize * nrow/height_fig
        wspace = width_wspace / width_one_subplot

        plt.subplots_adjust(left=0, bottom=0.0, right=1.0, top=1 - height_suplegend / height_fig,
                            hspace=hspace, wspace=wspace)

        vmin =None
        vmax = None
        data = data.astype(np.float32)
        data[data == meteva.base.IV] = np.nan
        if not isinstance(cmap,list):
            data_copy = copy.deepcopy(data)
            data_copy[np.isnan(data_copy)] = meteva.base.IV
            vmin = np.min(data_copy[data_copy != meteva.base.IV])
            vmax = np.max(data_copy[data_copy != meteva.base.IV])
            cmap,clevs = meteva.base.color_tools.def_cmap_clevs(cmap=cmap, clevs=clevs, vmin=vmin, vmax=vmax)

        for k in range(subplot_num):
            data_k = data[k, :, :]
            if isinstance(cmap, list):
                cmap0 = cmap[k]
                if isinstance(clevs,list):
                    clevs0 = clevs[k]
                else:
                    clevs0 = clevs

                data_k_copy = copy.deepcopy(data_k)
                data_k_copy[np.isnan(data_k_copy)] = meteva.base.IV
                vmin = np.min(data_k_copy[data_k_copy != meteva.base.IV])
                vmax = np.max(data_k_copy[data_k_copy != meteva.base.IV])
            else:
                cmap0 = cmap
                clevs0 = clevs
            cmap1,clevs1= meteva.base.color_tools.def_cmap_clevs(cmap = cmap0,clevs=clevs0,vmin=vmin,vmax = vmax)
            ax_one = plt.subplot(nrow, ncol, k + 1)
            if type == "mesh":
                myheatmap(ax_one,data_k,cmap1,clevs1,annot,sup_fontsize)
            else:
                cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap, clevs=clevs, vmin=vmin,
                                                                            vmax=vmax, extend=extend)
                norm = BoundaryNorm(clevs1, ncolors=cmap1.N)
                im = ax_one.contourf(data_k, levels=clevs1, cmap=cmap1, norm=norm,
                                 extend=extend)
                fig.colorbar(im, ax=ax_one)

            ki = k % ncol
            kj = int(k / ncol)
            knext_row = ki + (kj + 1) * ncol


            if axis_x=="lon" or axis_x=="lat":
                #为了让°E显示得更紧凑
                plt.xticks(xticks, xticks_labels, fontsize=xticks_font) #, family='Times New Roman')
            else:
                #为了显示中文字体
                plt.xticks(xticks, xticks_labels, fontsize=xticks_font)
            if knext_row >= subplot_num:
                plt.xlabel(axis_x, fontsize=sup_fontsize * 0.9)

            xminorLocator = mpl.ticker.MultipleLocator(1)  # 将x轴次刻度标签设置xmi
            if axis_y =="lat" or axis_y == "lon":
                # 为了让°E显示得更紧凑
                plt.yticks(yticks,yticks_labels,fontsize=sup_fontsize * 0.8) #,family='Times New Roman')
            else:
                #为了显示中文字体
                plt.yticks(yticks, yticks_labels, fontsize=sup_fontsize * 0.8)
            plt.ylabel(axis_y, fontsize=sup_fontsize * 0.9)
            if rect is not None:
                rect1 = patches.Rectangle((rect[0], rect[1]), rect[2], rect[3], linewidth=2, edgecolor=rect_color, facecolor='none')
                ax_one.add_patch(rect1)
            #plt.ylabel(ylabel, fontsize=sup_fontsize * 0.9)

            if isinstance(title, list):
                if (len(title) != subplot_num):
                    print("子图数和设置的子图标题数不一致")
                    return
                title1 = title[k]
            else:
                if subplot_num > 1:
                    title1 = title  + str(name_list_dict[subplot][k])
                else:
                    title1 = title
            plt.title(title1, fontsize=sup_fontsize)

            #提取第1个绘图框的
            if sup_title is not None:
                if k==0:
                    y = ax_one.bbox.y1 / fig.dpi / height_fig
                    if title1 =="":
                        y_sup_title = y + (sup_fontsize * 0.03) / height_fig
                    else:
                        y_sup_title = y + (sup_fontsize * 0.05) / height_fig
                    plt.suptitle(sup_title, y=y_sup_title, fontsize=sup_fontsize * 1.2)
    else:
        print("array只能绘制2维或3维数据")
        return


    if save_path is None:
        show = True
    else:
        meteva.base.creat_path(save_path)
        plt.savefig(save_path, bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()



def mesh_obtime_time(sta0,save_dir = None,save_path = None,
                   clevs = None,cmap = None,show = False,xtimetype = "mid",dpi = 300,annot =None,
                     sup_fontsize = 10,title = "预报准确性和稳定性对比图",width = None,height = None,multiple = 1):

    sta = sta0.copy()
    sta.iloc[:,6:] *= multiple
    ids = list(set(sta.loc[:, "id"]))
    data_names = meteva.base.get_stadata_names(sta)
    times_fo = sta.loc[:, "time"].values
    times_fo = list(set(times_fo))
    if (len(times_fo) == 1):
        print("仅有单个起报时间的预报，程序退出")
        return
    times_fo.sort()
    times_fo = np.array(times_fo)
    #print(times_fo)

    dhs_fo = (times_fo[1:] - times_fo[0:-1])
    if isinstance(dhs_fo[0], np.timedelta64):
        dhs_fo = dhs_fo / np.timedelta64(1, 'h')
    else:
        dhs_fo = dhs_fo / datetime.timedelta(hours=1)
    dhs_fo_not0 = dhs_fo[dhs_fo != 0]
    dh_y = np.min(dhs_fo_not0)
    min_dtime = int(np.min(sta["dtime"]))


    ob_time_s = sta["time"] + sta["dtime"] * np.timedelta64(1, 'h')
    times_ob = list(set(ob_time_s.values))
    times_ob.sort()
    times_ob = np.array(times_ob)

    dhs_ob = (times_ob[1:] - times_ob[0:-1])
    if isinstance(dhs_ob[0], np.timedelta64):
        dhs_ob = dhs_ob / np.timedelta64(1, 'h')
    else:
        dhs_ob = dhs_ob / datetime.timedelta(hours=1)

    dhs_ob_not0 = dhs_ob[dhs_ob != 0]
    dh_x = meteva.base.tool.math_tools.greatest_common_divisor(dhs_ob_not0)
    #print(dh_x)
    np.sum(dhs_fo_not0)
    row = int(np.sum(dhs_fo_not0)/dh_y)+1
    col = int(np.sum(dhs_ob_not0)/dh_x)+1
    #print(row)
    t_ob = []
    for t in times_ob:
        t_ob.append(meteva.base.all_type_time_to_datetime(t))

    y_ticks = []
    t_fo0= meteva.base.all_type_time_to_datetime(times_fo[0])
    step = int(math.ceil(row / 40))

    if step !=1 :
        while step * dh_y % 3 !=0:
            step +=1

    y_plot = np.arange(0,row,step)+0.5
    for j in range(0,row,step):
        jr = row - j - 1
        time_fo = t_fo0 + datetime.timedelta(hours=1) * dh_y * jr
        hour = time_fo.hour
        day = time_fo.day
        #if ((j * int(dh_y)) % 3 == 0):
        str1 = "%02d"%day + "日" + "%02d"%hour + "时"
        #else:
        #    str1 = str(hour) + "时"
        #print(str1)
        y_ticks.append(str1)

    width0 = col * 0.1 + 2
    height0 = row * 0.1 + 2
    x_plot,x_ticks = meteva.product.get_x_ticks(times_ob,width0-2,row=3)
    #sup_fontsize = 10

    rate = max(width0/8, height0/6)
    if width is None:
        width = width0/rate
    if height is None:
        height = height0/rate

    sup_fontsize = sup_fontsize/rate

    x_plot /= dh_x
    #y_plot, y_ticks = meteva.product.get_y_ticks(times_fo, height)
    if xtimetype == "right":
        x_plot  = x_plot+0.5
    elif xtimetype == "left":
        x_plot = x_plot -0.5
    else:
        x_plot = x_plot


    nids = len(ids)
    nfo = len(data_names)
    if isinstance(title, list):
        if nids * nfo != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids * nfo != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return
    kk = 0
    #print(sta)
    dat = sta[data_names].values
    dat[np.isnan(dat)] = meteva.base.IV
    vmin = np.min(dat[dat != meteva.base.IV])
    vmax = np.max(dat[dat != meteva.base.IV])


    if cmap is None:
        cmap = "bwr"
    cmap_part,clevs_part = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap,clevs=clevs,vmin=vmin,vmax = vmax)

    #if cmap is None:
    #    cmap = "bwr"
    #    cmap_part = cmap
    #if clevs is not None:
    #    clev_part, cmap_part = meteva.base.tool.color_tools.get_part_clev_and_cmap(clevs, cmap, vmax, vmin)
    vmax = clevs_part[-1]
    vmin = 2 * clevs_part[0] - clevs_part[1]

    if annot is None:
        if vmax>1:
            annot = 0
        else:
            annot = 1
    if col >= 120:
        annot = -1
    annot_f = annot
    fmt = "." + str(annot) + "f"
    annot_size = width * 50 / col
    if annot_size > height * 50 / row:
        annot_size = height * 50 / row
    if annot_size > 16:
        annot_size = 16
    annot = annot >= 0

    for d in range(nfo):
        data_name = data_names[d]
        sta_one_member = meteva.base.in_member_list(sta, [data_name])
        #meteva.base.set_stadata_names(sta_ob_part2, [data_name])
        #sta_one_member = meteva.base.combine_join(sta_ob_part2, sta_fo_all2)
        #以最近的预报作为窗口中间的时刻
        for id in ids:
            sta_one_id = meteva.base.in_id_list(sta_one_member,id)
            dat = np.ones((col, row)) * meteva.base.IV

            for j in range(row):
                jr = row - j - 1
                time_fo = times_fo[0] + np.timedelta64(1, 'h') * dh_y * jr
                sta_on_row = meteva.base.in_time_list(sta_one_id,time_fo)
                dhx0 = (time_fo - times_ob[0])/np.timedelta64(1, 'h')
                dhxs = sta_on_row["dtime"].values + dhx0
                index_i = (dhxs/dh_x).astype(np.int16)
                dat[index_i,j] = sta_on_row.values[:,-1]
            mask = np.zeros_like(dat.T)
            mask[dat.T == meteva.base.IV] = True

            f, ax2 = plt.subplots(figsize=(width, height), nrows=1, edgecolor='black',dpi = dpi)
            plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)

            #sns.heatmap(dat.T, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax, center=None, robust=False, annot=annot,fmt=fmt
            #, annot_kws = {'size': annot_size})
            myheatmap(ax2,dat.T,cmap_part,clevs_part,annot_f,annot_size)
            ax2.set_xlabel('实况时间',fontsize = sup_fontsize*0.9)
            ax2.set_ylabel('起报时间',fontsize = sup_fontsize*0.9)
            ax2.set_xticks(x_plot)
            ax2.set_xticklabels(x_ticks,rotation=360, fontsize=sup_fontsize*0.8)
            ax2.set_yticks(y_plot)
            ax2.set_yticklabels(y_ticks, rotation=360,fontsize = sup_fontsize * 0.8)

            ax2.grid(linestyle='--', linewidth=0.5)
            ax2.set_ylim(row-0.5, -0.5)
            ax2.set_title(title[kk], loc='left', fontweight='bold', fontsize= sup_fontsize)
            #rect = patches.Rectangle((0,0 ), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
            #ax2.add_patch(rect)
            #plt.tick_params(top='on', right='on', which='both')  # 显示上侧和右侧的刻度
            plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
            plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内

            save_path1 = None
            if(save_path is None):
                if save_dir is None:
                    show = True
                else:
                    id_str = ""
                    if id != meteva.base.IV:
                        id_str = "_"+str(id)
                    save_path1 = save_dir +"/" +data_name+id_str + ".png"
            else:
                save_path1 = save_path[kk]
            if save_path1 is not None:

                meteva.base.tool.path_tools.creat_path(save_path1)
                plt.savefig(save_path1,bbox_inches='tight')
                print("图片已保存至"+save_path1)
            if show:
                plt.show()
            plt.close()
            kk += 1
    return


def mesh_obtime_dtime(sta0,save_dir = None,save_path = None,
                   clevs = None,cmap = None,show = False,xtimetype = "mid",dpi = 300,annot =None,title = "预报准确性和稳定性对比图",
                      sup_fontsize = 10,width = None,height = None,multiple = 1):

    sta = sta0.copy()
    sta.iloc[:,6:] *= multiple
    ids = list(set(sta.loc[:, "id"]))
    data_names = meteva.base.get_stadata_names(sta)

    dhs_fo = sta.loc[:, "dtime"].values
    dhs_fo = list(set(dhs_fo))
    dhs_fo.sort()

    ob_time_s = sta["time"] + sta["dtime"] * np.timedelta64(1, 'h')
    times_ob = list(set(ob_time_s.values))
    times_ob.sort()
    times_ob = np.array(times_ob)

    dhs_ob = (times_ob[1:] - times_ob[0:-1])
    if isinstance(dhs_ob[0], np.timedelta64):
        dhs_ob = dhs_ob / np.timedelta64(1, 'h')
    else:
        dhs_ob = dhs_ob / datetime.timedelta(hours=1)


    dhs_ob_not0 = dhs_ob[dhs_ob != 0]

    dh_x = meteva.base.tool.math_tools.greatest_common_divisor(dhs_ob_not0)
    #print(dh_x)
    row = len(dhs_fo)
    col = int(np.sum(dhs_ob_not0)/dh_x)+1
    #print(row)
    t_ob = []
    for t in times_ob:
        t_ob.append(meteva.base.all_type_time_to_datetime(t))
    y_ticks = dhs_fo

    width0 = col * 0.1 + 2
    height0 = row * 0.1 + 2

    #sup_fontsize = 10

    rate = max(width0 / 8, height0 / 6)
    if width is None:
        width = width0/rate
    if height is None:
        height = height0/rate

    sup_fontsize = sup_fontsize / rate
    x_plot, x_ticks = meteva.product.get_x_ticks(times_ob, width - 2,row=3)

    x_plot /= dh_x
    #y_plot, y_ticks = meteva.product.get_y_ticks(times_fo, height)
    if xtimetype == "right":
        x_plot  = x_plot+0.5
    elif xtimetype == "left":
        x_plot = x_plot -0.5
    else:
        x_plot = x_plot



    nids = len(ids)
    nfo = len(data_names)
    if isinstance(title, list):
        if nids * nfo != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids * nfo != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return
    kk = 0

    dat = sta[data_names].values
    dat[np.isnan(dat)] = meteva.base.IV
    vmin = np.min(dat[dat != meteva.base.IV])
    vmax = np.max(dat[dat != meteva.base.IV])
    if cmap is None:
        cmap = "bwr"
    cmap_part,clevs_part = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap,clevs=clevs,vmin=vmin,vmax = vmax)

    #if cmap is None:
    #    cmap = "bwr"
    #    cmap_part = cmap
    #if clevs is not None:
    #    clev_part, cmap_part = meteva.base.tool.color_tools.get_part_clev_and_cmap(clevs, cmap, vmax, vmin)
    vmax = clevs_part[-1]
    vmin = 2 * clevs_part[0] - clevs_part[1]

    if annot is None:
        if vmax>1:
            annot = 0
        else:
            annot = 1
    if col >= 120:
        annot = -1
    fmt = "." + str(annot) + "f"
    annot_f = annot
    annot_size = width * 50 / col
    if annot_size > height * 50 / row:
        annot_size = height * 50 / row
    if annot_size > 16:
        annot_size = 16
    annot = annot >= 0

    #print(times_ob[0])
    for d in range(nfo):
        data_name = data_names[d]
        sta_one_member = meteva.base.in_member_list(sta, [data_name])
        #meteva.base.set_stadata_names(sta_ob_part2, [data_name])
        #sta_one_member = meteva.base.combine_join(sta_ob_part2, sta_fo_all2)
        #以最近的预报作为窗口中间的时刻
        for id in ids:
            sta_one_id = meteva.base.in_id_list(sta_one_member,id)
            dat = np.ones((col, row)) * meteva.base.IV
            for j in range(row):
                sta_on_row = meteva.base.in_dtime_list(sta_one_id,dhs_fo[j])
                #print(sta_on_row)
                dhxs = (sta_on_row["time"].values - times_ob[0])/np.timedelta64(1, 'h') + dhs_fo[j]
                index_i = (dhxs/dh_x).astype(np.int16)
                dat[index_i,j] = sta_on_row.values[:,-1]
            mask = np.zeros_like(dat.T)
            mask[dat.T == meteva.base.IV] = True

            f, ax2 = plt.subplots(figsize=(width, height), nrows=1, edgecolor='black',dpi = dpi)
            plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)

            #sns.heatmap(dat.T, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax, center=None, robust=False, annot=annot,fmt=fmt
            #, annot_kws = {'size': annot_size})

            myheatmap(ax2,dat.T,cmap_part,clevs_part,annot_f,annot_size)
            ax2.set_xlabel('实况时间',fontsize = sup_fontsize*0.9)
            ax2.set_ylabel('预报时效',fontsize = sup_fontsize*0.9)
            ax2.set_xticks(x_plot)
            ax2.set_xticklabels(x_ticks,rotation=360, fontsize=sup_fontsize * 0.8)
            ax2.set_yticks(np.arange(len(y_ticks)))
            ax2.set_yticklabels(y_ticks, rotation=360, fontsize=sup_fontsize * 0.8)

            ax2.grid(linestyle='--', linewidth=0.5)
            ax2.set_ylim(row-0.5, -0.5)
            ax2.set_title(title[kk], loc='left', fontweight='bold', fontsize=sup_fontsize)
            #rect = patches.Rectangle((0,0 ), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
            #ax2.add_patch(rect)
            #plt.tick_params(top='on', right='on', which='both')  # 显示上侧和右侧的刻度
            plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
            plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内

            save_path1 = None
            if(save_path is None):
                if save_dir is None:
                    show = True
                else:
                    id_str = ""
                    if id != meteva.base.IV:
                        id_str = "_"+str(id)
                    save_path1 = save_dir +"/" +data_name+id_str + ".png"
            else:
                save_path1 = save_path[kk]
            if save_path1 is not None:

                meteva.base.tool.path_tools.creat_path(save_path1)
                plt.savefig(save_path1,bbox_inches='tight')
                print("图片已保存至"+save_path1)
            if show:
                plt.show()
            plt.close()
            kk += 1
    return

def mesh_time_dtime(sta0,save_dir = None,save_path = None,
                   clevs = None,cmap = None,show = False,xtimetype = "mid",dpi = 300,annot =None,sup_fontsize = 10,title = "预报准确性对比图",
                    width = None,height = None,add_min_xticks = False,multiple = 1):

    sta = sta0.copy()
    sta.iloc[:,6:] *= multiple
    ids = list(set(sta.loc[:, "id"]))
    data_names = meteva.base.get_stadata_names(sta)
    times_fo = sta.loc[:, "time"].values
    times_fo = list(set(times_fo))
    if (len(times_fo) == 1):
        print("仅有单个起报时间的预报，程序退出")
        return
    times_fo.sort()
    times_fo = np.array(times_fo)


    dhs_fo = sta.loc[:, "dtime"].values
    dhs_fo = list(set(dhs_fo))
    dhs_fo.sort(reverse = True)
    #print(times_fo)
    dhs_x = (times_fo[1:] - times_fo[0:-1])
    if isinstance(dhs_x[0], np.timedelta64):
        dhs_x = dhs_x / np.timedelta64(1, 'h')
    else:
        dhs_x = dhs_x / datetime.timedelta(hours=1)
    dhs_x_not0 = dhs_x[dhs_x != 0]


    dh_x = meteva.base.tool.math_tools.greatest_common_divisor(dhs_x_not0)

    #print(dh_x)
    row = len(dhs_fo)
    col = int(np.sum(dhs_x_not0)/dh_x)+1
    #print(row)
    t_ob = []
    for t in times_fo:
        t_ob.append(meteva.base.all_type_time_to_datetime(t))



    width0 = col * 0.15 + 2
    height0 = row * 0.15 + 2

    #sup_fontsize = 10

    rate = max(width0 / 8, height0 / 6)
    if width is None:
        width = width0/rate
    if height is None:
        height = height0/rate


    x_plot, x_ticks = meteva.product.get_x_ticks(times_fo, width - 2,row = 3)
    y_plot, y_ticks = meteva.product.get_y_ticks(dhs_fo, height,sup_fontsize * 0.8)

    #sup_fontsize = sup_fontsize / (width0/width)

    rate2 = sup_fontsize * len(x_ticks) * 0.05 / width
    if rate2 > 1:
        sup_fontsize = sup_fontsize/rate2

    x_plot /= dh_x
    #y_plot, y_ticks = meteva.product.get_y_ticks(times_fo, height)
    if xtimetype == "right":
        x_plot  = x_plot+0.5
    elif xtimetype == "left":
        x_plot = x_plot -0.5
    else:
        x_plot = x_plot


    nids = len(ids)
    nfo = len(data_names)
    if isinstance(title, list):
        if nids * nfo != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids * nfo != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return
    kk = 0

    dat = sta[data_names].values
    dat[np.isnan(dat)] = meteva.base.IV

    vmin = np.min(dat[dat != meteva.base.IV])
    vmax = np.max(dat[dat != meteva.base.IV])
    if cmap is None:
        cmap = "bwr"


    cmap_part,clevs_part = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap,clevs=clevs,vmin=vmin,vmax = vmax)
    vmax = clevs_part[-1]
    vmin = 2 * clevs_part[0] - clevs_part[1]


    if annot is None:
        if vmax>1:
            annot = 0
        else:
            annot = 1
    if col >= 120:
        annot = -1

    annot_f = annot
    fmt = "." + str(annot) + "f"

    annot_size = width * 50 / col

    if annot_size > height * 50 / row:
        annot_size = height * 50 / row
    if annot_size > 16:
        annot_size = 16
    annot = annot >= 0


    #print(times_ob[0])
    for d in range(nfo):
        data_name = data_names[d]
        sta_one_member = meteva.base.in_member_list(sta, [data_name])
        #meteva.base.set_stadata_names(sta_ob_part2, [data_name])
        #sta_one_member = meteva.base.combine_join(sta_ob_part2, sta_fo_all2)
        #以最近的预报作为窗口中间的时刻
        for id in ids:
            sta_one_id = meteva.base.in_id_list(sta_one_member,id)
            dat = np.ones((col, row)) * meteva.base.IV
            for j in range(row):
                sta_on_row = meteva.base.in_dtime_list(sta_one_id,dhs_fo[j])
                #print(sta_on_row)
                dhxs = (sta_on_row["time"].values - times_fo[0])/np.timedelta64(1, 'h')
                index_i = (dhxs/dh_x).astype(np.int16)
                dat[index_i,j] = sta_on_row.values[:,-1]
            mask = np.zeros_like(dat.T)
            mask[dat.T == meteva.base.IV] = True


            #height = width * row / col + 2
            #print(width)
            #print(height)
            f, ax2 = plt.subplots(figsize=(width, height), nrows=1, edgecolor='black',dpi = dpi)
            plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)
            #norm = BoundaryNorm(clevs_part, ncolors=cmap_part.N - 1)

#            sns.heatmap(dat.T, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax, center=None, robust=False, annot=annot,fmt=fmt
#           , annot_kws = {'size': annot_size})
            myheatmap(ax2,dat.T,cmap_part,clevs_part,annot_f,annot_size)

            ax2.set_xlabel('起报时间',fontsize = sup_fontsize * 0.9)
            ax2.set_ylabel('预报时效',fontsize = sup_fontsize * 0.9)
            ax2.set_xticks(x_plot)
            ax2.set_xticklabels(x_ticks,rotation=360, fontsize=sup_fontsize * 0.8)
            if add_min_xticks:ax2.set_xticks(np.arange(max(x_plot)+1))

            ax2.set_yticks(y_plot)
            ax2.set_yticklabels(y_ticks, rotation=360, fontsize=sup_fontsize * 0.8)

            ax2.grid(linestyle='--', linewidth=min(0.5,2*width/col))
            ax2.set_ylim(row-0.5, -0.5)
            ax2.set_title(title[kk], loc='left', fontweight='bold', fontsize=sup_fontsize)
            #rect = patches.Rectangle((-0.5,-0.5), col, row+, linewidth=0.8, edgecolor='k', facecolor='none')
            #ax2.add_patch(rect)
            #plt.tick_params(top='on', right='on', which='both')  # 显示上侧和右侧的刻度
            plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
            plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内

            save_path1 = None
            if(save_path is None):
                if save_dir is None:
                    show = True
                else:
                    id_str = ""
                    if id != meteva.base.IV:
                        id_str = "_"+str(id)
                    save_path1 = save_dir +"/" +data_name+id_str + ".png"
            else:
                save_path1 = save_path[kk]
            if save_path1 is not None:

                meteva.base.tool.path_tools.creat_path(save_path1)
                plt.savefig(save_path1,bbox_inches='tight')
                print("图片已保存至"+save_path1)
            if show:
                plt.show()
            plt.close()
            kk += 1
    return


def barbs_grid_wind(grid_wind,width = None,height = None,sup_fontsize = 12,dpi = 300,skip = None,save_path = None,show = False):
    grid1 = meteva.base.get_grid_of_data(grid_wind)
    axs = meteva.base.creat_axs(1, map_extend=grid1, add_minmap=False, ncol=2, width=width,height=height,sup_fontsize=sup_fontsize,dpi=dpi)
    meteva.base.add_barbs(axs[0], grid_wind,skip=skip)

    if save_path is None:
        show = True
    else:
        meteva.base.creat_path(save_path)
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()


def add_scatter(ax,map_extend,sta0,cmap = None,clevs = None,point_size = None,fix_size = True,title = None,threshold = 2,min_spot_value = 0,mean_value = 2,
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

    ax.set_xlim((slon, elon))
    ax.set_ylim((slat, elat))

    sta_without_iv = meteva.base.sele.not_IV(sta)

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


    if add_colorbar:
        width = fig.bbox.width / fig.dpi
        height = fig.bbox.height / fig.dpi
        location = [ax.bbox.x1 / fig.dpi / width + 0.005, ax.bbox.y0 / fig.dpi / height, 0.01,
                    ax.bbox.height / fig.dpi / height]

        if (add_colorbar):
            colorbar_position = fig.add_axes(location)  # 位置[左,下,宽,高]
            plt.colorbar(im, cax=colorbar_position)
    return im



