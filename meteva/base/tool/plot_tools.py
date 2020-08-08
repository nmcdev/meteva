import os
import numpy as np
import pkg_resources
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import math
from matplotlib.colors import BoundaryNorm
from meteva.base import IV
import meteva
from matplotlib.collections import LineCollection
import matplotlib.patches as patches
import seaborn as sns
import datetime


def readshapefile(shapefile, default_encoding='utf-8'):
    """
    """
    import shapefile as shp
    from shapefile import Reader
    shp.default_encoding = default_encoding
    if not os.path.exists('%s.shp'%shapefile):
        raise IOError('cannot locate %s.shp'%shapefile)
    if not os.path.exists('%s.shx'%shapefile):
        raise IOError('cannot locate %s.shx'%shapefile)
    if not os.path.exists('%s.dbf'%shapefile):
        raise IOError('cannot locate %s.dbf'%shapefile)
    # open shapefile, read vertices for each object, convert
    # to map projection coordinates (only works for 2D shape types).
    try:
        shf = Reader(shapefile, encoding=default_encoding)
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
        if shptype not in [1,3,5,8,13]:
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


def add_china_map_2basemap(ax,name ="province", facecolor='none',
                           edgecolor='c', lw=2, encoding='utf-8', **kwargs):
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
    names = {'world':"worldmap",'nation': "bou1_4p", 'province': "Province",
             'county': "BOUNT_poly", 'river': "hyd1_4p",
             'river_high': "hyd2_4p"}

    names = {'world':"worldmap",'nation': "NationalBorder", 'province': "Province",
             'county': "BOUNT_poly", 'river': "hyd1_4p",
             'river_high': "hyd2_4p"}
        # get shape file and information
    shpfile = pkg_resources.resource_filename(
        'meteva', "resources/maps/" + names[name])
    #print(shpfile)
    shp1 = readshapefile(shpfile, default_encoding=encoding)
    lines = LineCollection(shp1,antialiaseds=(1,))
    lines.set_color(edgecolor)
    lines.set_linewidth(lw)
    lines.set_label('_nolabel_')
    ax.add_collection(lines)


def contourf_2d_grid(grd,save_path = None,title = None,clevs= None,cmap = None,add_county_line = False,add_worldmap =False,show = False,dpi = 300):

    if save_path is None:
        show = True
    x = grd['lon'].values
    y = grd['lat'].values
    rlon = x[-1] - x[0]
    rlat = y[-1] - y[0]

    height = 5.6
    title_hight = 0.6
    legend_hight = 0.3
    left_plots_width  = 0.8
    right_plots_width = 0.8
    width = (height - title_hight - legend_hight) * rlon / rlat + left_plots_width + right_plots_width
    fig = plt.figure(figsize=(width, height),dpi = dpi)
    rect1 = [left_plots_width / width, legend_hight/height, (width - right_plots_width - left_plots_width) / width, 1-title_hight/height]
    ax = plt.axes(rect1)

    grid0 = meteva.base.get_grid_of_data(grd)


    if grid0.slon < 70 or grid0.elon > 140 or grid0.slat < 10 or grid0.elat > 60:
        add_worldmap = True
    if add_worldmap:
        add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"

    add_china_map_2basemap(ax, name="nation", edgecolor='k', lw=0.3,encoding = 'gbk')  #"国界"
    add_china_map_2basemap(ax, edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "省界"
    ax.set_xlim((grid0.slon, grid0.elon))
    ax.set_ylim((grid0.slat, grid0.elat))

    if title is None:
        time_str = meteva.base.tool.time_tools.time_to_str(grid0.gtime[0])
        dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
        if type(grid0.members[0]) == str:
            model_name = grid0.members[0]
        else:
            model_name = str(grid0.members[0])
        title = model_name + " "+dati_str  + str(grid0.dtimes[0]) + "H时效 " + grd.name
    plt.title(title,fontsize = 14)

    vmax = np.max(grd.values)
    vmin = np.min(grd.values)
    if clevs is not None and cmap is not None:
        clevs1, cmap1 = meteva.base.tool.color_tools.get_part_clev_and_cmap(clevs, cmap, vmax,vmin)
    else:
        if clevs is None:
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
                inte=inte*10
            vmin = inte * ((int)(vmin / inte)-1)
            vmax = inte * ((int)(vmax / inte) + 2)
            clevs1 = np.arange(vmin,vmax,inte)
        else:
            clevs1 = clevs
        if cmap is None:
            cmap1 = plt.get_cmap("rainbow")
        else:
            cmap1 = cmap
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    im = ax.contourf(x, y, np.squeeze(grd.values), levels=clevs1, cmap=cmap1,norm = norm)
    left_low = (width +0.1 - right_plots_width) / width
    colorbar_position = fig.add_axes([left_low, legend_hight / height, 0.02, 1 - title_hight / height])  # 位置[左,下,宽,高]
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
    ax.set_xticklabels(xticks_label,fontsize = 12)

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
    ax.set_yticklabels(yticks_label,fontsize = 12)


    if(save_path is not None):
        file1,extension = os.path.splitext(save_path)
        extension = extension[1:]
        plt.savefig(save_path,format = extension,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()


def pcolormesh_2d_grid(grd,save_path = None,title = None,clevs= None,cmap = None,add_county_line = False,add_worldmap=False,show = False,dpi = 300):

    if save_path is None:
        show = True
    x = grd['lon'].values
    y = grd['lat'].values
    rlon = x[-1] - x[0]
    rlat = y[-1] - y[0]

    grid0 = meteva.base.get_grid_of_data(grd)

    height = 5.6
    title_hight = 0.6
    legend_hight = 0.3
    left_plots_width  = 0.8
    right_plots_width = 0.8
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

    add_china_map_2basemap(ax, name="nation", edgecolor='k', lw=0.3, encoding='gbk')  # "国界"
    add_china_map_2basemap(ax,  edgecolor='k', lw=0.3, encoding='gbk')   # "省界"

    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"

    ax.set_xlim((grid0.slon, grid0.elon))
    ax.set_ylim((grid0.slat, grid0.elat))


    vmax = np.max(grd.values)
    vmin = np.min(grd.values)
    if clevs is not None and cmap is not None:
        clevs1, cmap1 = meteva.base.tool.color_tools.get_part_clev_and_cmap(clevs, cmap, vmax,vmin)
    else:
        if clevs is None:
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
            clevs1 = np.arange(vmin,vmax,inte)
        else:
            clevs1 = clevs

        if cmap is None:
            cmap1 = plt.get_cmap("rainbow")
        else:
            cmap1 = plt.get_cmap(cmap)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    im = ax.pcolormesh(x, y, np.squeeze(grd.values), cmap=cmap1,norm=norm)
    left_low = (width + 0.1 - right_plots_width) / width
    colorbar_position = fig.add_axes([left_low, legend_hight / height, 0.02, 1-title_hight/height])  # 位置[左,下,宽,高]
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
    ax.set_xticklabels(xticks_label,fontsize = 12)



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
    ax.set_yticklabels(yticks_label,fontsize = 12)


    if(save_path is not None):
        file1,extension = os.path.splitext(save_path)
        extension = extension[1:]
        plt.savefig(save_path,format = extension,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()


def scatter_sta(sta0,value_column=None,
                map_extend = None,add_county_line = False,add_worldmap = False,
                clevs=None, cmap=None,
                fix_size = True,threshold = None,mean_value = None,
                print_max = 0,print_min = 0,save_dir = None,
                save_path=None,show = False,dpi = 300,title=None):

    sta = sta0
    if save_path is None:
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



    hight = 5.6
    title_hight = 1.0
    legend_hight = 0.3
    left_plots_width  = 0.8
    right_plots_width = 0.8
    width = (hight - title_hight - legend_hight) * rlon / rlat + left_plots_width + right_plots_width
    map_width = width - left_plots_width - right_plots_width
    map_area = (hight - title_hight - legend_hight) *map_width

    data_names = meteva.base.get_stadata_names(sta)
    #value_column为指定绘制的数据列。 如果不知道绘制某一列就绘制所有列
    if value_column is None:
        plot_data_names = data_names
        value_column = 0
    else:
        plot_data_names = [data_names[value_column]]

    sta_without_iv = meteva.base.sele.not_IV(sta)

    values = sta_without_iv.loc[:, plot_data_names].values
    if mean_value is None:
        mean_value = np.sum(np.abs(values)) / values.size

    #print(mean_value)

    vmax = np.max(sta_without_iv[plot_data_names].values)
    vmin = np.min(sta_without_iv[plot_data_names].values)

    if clevs is not None and cmap is not None:
        clevs1, cmap1 = meteva.base.tool.color_tools.get_part_clev_and_cmap(clevs, cmap, vmax, vmin)
    else:
        if clevs is None:
            if vmax - vmin < 1e-10:
                vmax = vmin + 1.1
            dif = (vmax - vmin) / 10.0
            # print(vmax)
            # print(vmin)
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
            clevs1 = np.arange(vmin, vmax, inte)
        else:
            clevs1 = clevs
        if cmap is None:
            cmap1 = plt.get_cmap("rainbow")
        else:
            cmap1 = plt.get_cmap(cmap)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N, clip=True)
    pointsize = int(100 * map_area / len(sta.index))
    if (pointsize > 30): pointsize = 30
    if (pointsize < 1): pointsize = 1
    pointsize *=3
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
    else:
        inte = 10

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte) + 1)

    xticks = np.arange(vmin, vmax, inte)
    xticks_label = []
    for x in range(len(xticks)):
        xticks_label.append(str(xticks[x]))
    xticks_label[-1] += "°E"


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
        yticks_label.append(str(yticks[y]))
    yticks_label[-1] += "°N"

    nplot = len(plot_data_names)

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
        data_name = data_names[p]
        sta_one_member = meteva.base.sele_by_para(sta,member=[data_name],drop_IV=True)

        x = sta_one_member.loc[:, "lon"].values
        y = sta_one_member.loc[:, "lat"].values
        value = sta_one_member.loc[:, data_name].values

        fig = plt.figure(figsize=(width, hight),dpi = dpi)
        rect1 = [left_plots_width / width, legend_hight / hight, (width - right_plots_width - left_plots_width) / width,
                 1 - title_hight / hight]
        ax = plt.axes(rect1)


        if title is None:
            try:
                time_str = meteva.base.tool.time_tools.time_to_str(sta.iloc[0, 1])
                dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
                title1 = data_name + " " + dati_str + str(sta.iloc[0,2]) + "H时效 "
            except:
                print("time or dtime or level 格式错误，请更改相应数据格式或直接指定title")
                title1= ""
        else:
            #title1 = title.replace("NNN",data_name)
            if isinstance(title,list):
                title1 = title[p]
            else:
                title1 = title +"(" +data_name+")"

        plt.title(title1,fontsize = 14)

        if slon < 70 or elon > 140 or slat < 10 or elat > 60:
            add_worldmap = True
        if add_worldmap:
            add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"


        add_china_map_2basemap(ax, name="province", edgecolor='k', lw=0.3, encoding='gbk',grid0 = None)  # "省界"
        if add_county_line:
            add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk', grid0=None)  # "县界"
        ax.set_xlim((slon, elon))
        ax.set_ylim((slat, elat))
        colors = value
        if fix_size:
            im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=pointsize)
        else:
            area = pointsize * np.abs(value)/mean_value
            if(threshold is not None):
                area[np.abs(value)<threshold] *= 0.1
            im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=area)

        if print_max>0:
            print("取值最大的"+str(print_max)+"个站点：")
            indexs = value.argsort()[-print_max:][::-1]
            for index in indexs:
                print("id:" + str(sta.iloc[index,3]) +"   lon:"+str(sta.iloc[index,4])+"  lat:" + str(sta.iloc[index,5]) +
                      " value:"+str(sta.iloc[index,6+p]))
        if print_min>0:
            print("取值最小的"+str(print_min)+"个站点：")
            indexs = value.argsort()[:print_min]
            for index in indexs:
                print("id:" + str(sta.iloc[index,3]) +"   lon:"+str(sta.iloc[index,4])+"  lat:" + str(sta.iloc[index,5]) +
                      " value:"+str(sta.iloc[index,6+p]))

        colorbar_position = fig.add_axes([left_low, legend_hight / hight, 0.02, 1-title_hight/hight])  # 位置[左,下,宽,高]
        plt.colorbar(im, cax=colorbar_position)

        ax.set_xticks(xticks)
        ax.set_xticklabels(xticks_label,fontsize = 14)

        ax.set_yticks(yticks)
        ax.set_yticklabels(yticks_label,fontsize = 14)


        save_path1 = None
        if save_path is None:
            if save_dir is None:
                show = True
            else:
                save_path1 = save_dir + "/" + data_name + ".png"
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



def scatter_sta1(sta0,map_extend = None, value_column=0, save_path=None, title=None, clevs=None, cmap=None,
                fix_size = True,add_county_line = False,show = False,print_max = 1,mean_value = None,threshold = None,dpi = 300):

    if save_path is None:
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
        sta = sta0
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



    hight = 5.6
    title_hight = 1.0
    legend_hight = 0.3
    left_plots_width  = 0.8
    right_plots_width = 0.8
    width = (hight - title_hight - legend_hight) * rlon / rlat + left_plots_width + right_plots_width
    map_width = width - left_plots_width - right_plots_width
    map_area = (hight - title_hight - legend_hight) *map_width

    fig = plt.figure(figsize=(width, hight),dpi = dpi)
    rect1 = [left_plots_width / width, legend_hight / hight, (width - right_plots_width - left_plots_width) / width,
             1 - title_hight / hight]
    ax = plt.axes(rect1)
    data_names = meteva.base.get_stadata_names(sta)
    data_name = data_names[value_column]
    # sta1 = meteva.base.in_member_list(sta,[data_name])

    if title is None:
        try:
            time_str = meteva.base.tool.time_tools.time_to_str(sta.iloc[0, 1])
            dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"

            title = data_name + " " + dati_str + str(sta.iloc[0,2]) + "H时效 "
        except:
            print("time or dtime or level 格式错误，请更改相应数据格式或直接指定title")
            title = ""
    plt.title(title,fontsize = 14)

    if slon<60 or elon > 150 or slat < 0 or elat > 60:
        add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "省界"


    add_china_map_2basemap(ax, name="province", edgecolor='k', lw=0.3, encoding='gbk',grid0 = None)  # "省界"
    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk', grid0=None)  # "省界"
    ax.set_xlim((slon, elon))
    ax.set_ylim((slat, elat))

    vmax = np.max(sta[data_name].values)
    vmin = np.min(sta[data_name].values)

    if clevs is not None and cmap is not None:
        clevs1, cmap1 = meteva.base.tool.color_tools.get_part_clev_and_cmap(clevs, cmap, vmax, vmin)
    else:
        if clevs is None:
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
            vmin = inte * ((int)(vmin / inte) - 1)
            vmax = inte * ((int)(vmax / inte) + 2)
            clevs1 = np.arange(vmin, vmax, inte)
        else:
            clevs1 = clevs
        if cmap is None:
            cmap1 = plt.get_cmap("rainbow")
        else:
            cmap1 = plt.get_cmap(cmap)

    sta1 = sta.loc[:,["lon","lat",data_name]]
    sta1.sort_values(by = [data_name],ascending = False)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N, clip=True)

    x = sta1.loc[:, "lon"].values

    y = sta1.loc[:, "lat"].values
    colors = sta1.loc[:, data_name].values

    pointsize = int(100 * map_area / len(x))
    if (pointsize > 30): pointsize = 30
    if (pointsize < 1): pointsize = 1



    pointsize *=3
    if fix_size:
        im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=pointsize)
    else:
        area = np.abs(sta.loc[:, data_name].values)
        index = np.argmax(area)
        maxvalue = area[index]
        if mean_value is None:
            mean_area = np.sum(area)/area.size
        else:
            mean_area = mean_value
        if(threshold is not None):
            area[area<threshold] = 0.1
        area = pointsize * area/mean_area
        im = ax.scatter(x, y, c=colors, cmap=cmap1, norm=norm, s=area)
        #print(area.argsort()[-3][::-1])
        indexs = area.argsort()[-print_max:][::-1]
        #np.argmax(area)
        if print_max>0:
            print("误差绝对值前"+str(print_max)+"的站点：")
        for index in indexs:
            print("id:" + str(sta.iloc[index,3]) +"   lon:"+str(sta.iloc[index,4])+"  lat:" + str(sta.iloc[index,5]) +" value:"+str(sta.iloc[index,6+value_column]))

    left_low = (width + 0.1 - right_plots_width) / width
    colorbar_position = fig.add_axes([left_low, legend_hight / hight, 0.02, 1-title_hight/hight])  # 位置[左,下,宽,高]
    plt.colorbar(im, cax=colorbar_position)

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
    else:
        inte = 10

    vmin = inte * (math.ceil(vmin / inte))
    vmax = inte * ((int)(vmax / inte) + 1)

    xticks = np.arange(vmin, vmax, inte)
    xticks_label = []
    for x in range(len(xticks)):
        xticks_label.append(str(xticks[x]))

    xticks_label[-1] += "°E"
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticks_label,fontsize = 14)

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
        yticks_label.append(str(yticks[y]))
    yticks_label[-1] += "°N"
    ax.set_yticks(yticks)
    ax.set_yticklabels(yticks_label,fontsize = 14)


    if(save_path is not None):
        file1,extension = os.path.splitext(save_path)
        extension = extension[1:]
        plt.savefig(save_path,format = extension,bbox_inches='tight')
    else:
        show = True
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


def bar(array,name_list_dict = None,legend = None,axis = None,ylabel = "Value",vmin = None,vmax = None,ncol = None,save_path = None,show = False
        ,dpi = 300,bar_width = None,title = ""):
    sup_fontsize = 10
    shape = array.shape

    if len(array[array!=meteva.base.IV]) ==0:
        print("所有的值都为缺失值")
        return

    '''
    if vmin is None:
        vmin1 = np.min(array[array != meteva.base.IV])
    else:
        vmin1 = vmin
    if vmax is None:
        vmax1 = np.max(array[array != meteva.base.IV])
    else:
        vmax1 = vmax

    dmax = vmax1 - vmin1
    if vmin is None:
        if vmin1 < 0:
            vmin1 = vmin1 - 0.1 * dmax
    if vmax is None:
        vmax1 = vmax1 + 0.5 * dmax
    '''

    if len(shape) ==1:
        if name_list_dict is None:
            name_list_dict = {}
            name_list_dict["x"] = np.arange(array.size).tolist()

        xlabel = list(name_list_dict.keys())[0]
        xticks = name_list_dict[xlabel]
        width = meteva.base.plot_tools.caculate_axis_width(xticks, sup_fontsize)
        if width > 10:
            for i in range(len(xticks)):
                if i % 2 == 1:
                    xticks[i] = "|\n" + xticks[i]
            width = 10
        elif width < 5:
            width = 5
        height = width / 2
        fig = plt.figure(figsize=(width, height), dpi=dpi)
        x = np.arange(array.size)
        y_plot = array[array != meteva.base.IV]
        x_plot = x[array!=meteva.base.IV]

        if bar_width is None:
            width = 0.2
        else:
            width = bar_width
        plt.bar(x_plot,y_plot,width= width *0.95)
        if len(array[array ==meteva.base.IV])>0:
            x_iv = x[array == meteva.base.IV]
            y_iv = np.zeros(x_iv.size)
            plt.plot(x_iv,y_iv,"^", color='k')

        plt.xticks(x,xticks,fontsize = sup_fontsize * 0.8)
        plt.yticks(fontsize=sup_fontsize * 0.8)
        plt.xlabel(xlabel,fontsize=sup_fontsize * 0.9)
        plt.ylabel(ylabel,fontsize = sup_fontsize * 0.9)
        if isinstance(title,list):
            title = title[0]
        plt.title(title,fontsize = sup_fontsize)

        if vmin is None:
            vmin1 = np.min(array[array != meteva.base.IV])
        else:
            vmin1 = vmin
        if vmax is None:
            vmax1 = np.max(array[array != meteva.base.IV])
        else:
            vmax1 = vmax

        dmax = vmax1 - vmin1
        if vmin is None:
            if vmin1 < 0:
                vmin1 = vmin1 - 0.1 * dmax
        if vmax is None:
            vmax1 = vmax1 + 0.2 * dmax

        plt.ylim(vmin1,vmax1)

    elif len(shape)==2:
        if name_list_dict is None:
            name_list_dict = {}
            name_list_dict["x"] = np.arange(shape[0]).tolist()
            name_list_dict["y"] = np.arange(shape[1]).tolist()
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
        xticks = name_list_dict[axis]
        width = meteva.base.plot_tools.caculate_axis_width(xticks, sup_fontsize,legend_num)

        if width > 10:
            for i in range(len(xticks)):
                if i % 2 == 1:
                    xticks[i] = "|\n" + str(xticks[i])
            width = 10
        elif width < 5:
            width = 5
        height = width / 2
        legend_col = int(width * 0.8)
        legend_row = int(math.ceil(legend_num/legend_col))
        legend_col = int(math.ceil(legend_num/legend_row))

        fig = plt.figure(figsize=(width, height), dpi=dpi)
        x = np.arange(len(xticks))
        if bar_width is None:
            width = 0.7 / (legend_num + 2)
        else:
            width = bar_width

        for i in range(legend_num):
            x1 = x + (i - legend_num/2 + 0.5) * width
            dat0 = dat[i,:]
            y_plot = dat0[dat0 != meteva.base.IV]
            x_plot = x1[dat0 != meteva.base.IV]
            plt.bar(x_plot, y_plot,width=width * 0.95,label = legend_list[i])
            if len(dat0[dat0 == meteva.base.IV]) > 0:
                x_iv = x1[dat0 == meteva.base.IV]
                y_iv = np.zeros(x_iv.size)
                plt.plot(x_iv, y_iv, "^", color='k')
            #plt.bar(x1, dat[i,:],width=width * 0.95,label = legend_list[i])

        plt.legend(fontsize =sup_fontsize * 0.8,ncol = legend_col,loc = "upper center")
        plt.xticks(x, xticks, fontsize=sup_fontsize * 0.8)
        plt.yticks(fontsize=sup_fontsize * 0.8)
        plt.xlabel(axis, fontsize=sup_fontsize * 0.9)
        plt.ylabel(ylabel, fontsize=sup_fontsize * 0.9)
        if isinstance(title,list):
            title = title[0]
        plt.title(title, fontsize=sup_fontsize)
        plt.xlim(-0.5, len(xticks)-0.5)


        if vmin is None:
            vmin1 = np.min(array[array != meteva.base.IV])
        else:
            vmin1 = vmin
        if vmax is None:
            vmax1 = np.max(array[array != meteva.base.IV])
        else:
            vmax1 = vmax

        dmax = vmax1 - vmin1
        if vmin is None:
            if vmin1 < 0:
                vmin1 = vmin1 - 0.1 * dmax
        if vmax is None:
            vmax1 = vmax1 + 0.5 * dmax

        plt.ylim(vmin1,vmax1)

    elif len(shape)==3:
        if name_list_dict is None:
            name_list_dict["z"] = np.arange(shape[0])
            name_list_dict["y"] = np.arange(shape[1])
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
        legend_num = len(name_list_dict[legend])
        width_axis = meteva.base.plot_tools.caculate_axis_width(name_list_dict[axis], sup_fontsize,legend_num)
        width_wspace = sup_fontsize * 0.1
        width_one_subplot = width_axis +width_wspace
        if width_one_subplot <1.5:width_one_subplot = 1.5
        subplot_num = len(name_list_dict[subplot])
        spasify = 1
        if width_one_subplot >10:
            spasify = int(math.ceil(width_one_subplot/10))
            width_one_subplot = 10
        if ncol is None:
            ncol = int(10/width_one_subplot)
            nrow = int(math.ceil(subplot_num/ncol))
            ncol = int(math.ceil(subplot_num/nrow))
        else:
            nrow = int(math.ceil(len(name_list_dict[subplot])/ncol))
        width_fig = width_one_subplot * ncol
        height_axis = width_axis * 0.5
        height_hspace = sup_fontsize * 0.01
        height_suplegend = 1
        height_fig = nrow * (height_axis+height_hspace) + height_suplegend
        if width_fig>10:width_fig = 10
        if height_fig >7:height_fig = 7
        if width_fig<5: width_fig=5
        if height_fig<3:height_fig=3
        fig = plt.figure(figsize=(width_fig, height_fig), dpi=dpi)
        hspace = height_hspace/(width_axis*0.5)
        wspace = width_wspace/width_one_subplot

        plt.subplots_adjust(left=0, bottom=0.0, right=1.0, top = 1 - height_suplegend/height_fig,
                            hspace=0.08,wspace=wspace)

        if vmin is not None:
            if isinstance(vmin,list):
                if len(vmin) != subplot_num:
                    print("vmin 参数的个数和 子图个数不一致，请重新设置")
                    return
                else:
                    vmin1 = vmin
            else:
                vmin1 = vmin * np.ones(subplot_num)
                vmin1 = vmin1.tolist()

        if vmax is not None:
            if isinstance(vmax,list):
                if len(vmax) != subplot_num:
                    print("vmax 参数的个数和 子图个数不一致，请重新设置")
                    return
                else:
                    vmax1 = vmax
            else:
                vmax1 = vmax * np.ones(subplot_num)

        if bar_width is None:
            width = 0.7 / (legend_num + 2)
        else:
            width = bar_width

        for k in range(subplot_num):
            plt.subplot(nrow, ncol, k + 1)
            x = np.arange(len(name_list_dict[axis]))

            for i in range(legend_num):
                x1 = x + (i - legend_num / 2 + 0.5) * width
                dat0 = data[k,i,:]
                y_plot = dat0[dat0 != meteva.base.IV]
                x_plot = x1[dat0 != meteva.base.IV]
                if k ==0:
                    plt.bar(x_plot, y_plot, width=width * 0.95, label=name_list_dict[legend][i])
                else:
                    plt.bar(x_plot, y_plot, width=width * 0.95)
                if len(dat0[dat0 == meteva.base.IV]) > 0:
                    x_iv = x1[dat0 == meteva.base.IV]
                    y_iv = np.zeros(x_iv.size)
                    plt.plot(x_iv, y_iv, "^", color='k')
                #plt.bar(x1, data[k,i, :], width=width * 0.95, label=name_list_dict[legend][i])
            #plt.legend(fontsize=sup_fontsize * 0.8, ncol=legend_col, loc="upper center")

            ki = k % ncol
            kj = int(k / ncol)
            knext_row = ki + (kj+1) * ncol
            #print(knext_row)
            #print(subplot_num)
            if knext_row>=subplot_num:
                plt.xticks(x[::spasify], name_list_dict[axis][::spasify], fontsize=sup_fontsize * 0.8)
                plt.xlabel(axis, fontsize=sup_fontsize * 0.9)
            else:
                plt.xticks([])
            plt.yticks(fontsize=sup_fontsize * 0.8)

            plt.ylabel(ylabel, fontsize=sup_fontsize * 0.9)

            if isinstance(title, list):
                if(len(title) != subplot_num):
                    print("子图数和设置的子图标题数不一致")
                    return
                title1 = title[k]
            else:
                if subplot_num>1:
                    title1 = title +"("+ subplot +"_"+ str(name_list_dict[subplot][k])+")"
                else:
                    title1 = title
            y1 =  1 - 0.035 *  sup_fontsize / (height_fig/nrow)
            plt.title(title1, fontsize=sup_fontsize,y = y1)
            plt.xlim(-0.5, len(name_list_dict[axis]) - 0.5)

            data_k = data[k,:,:]
            if vmin is None:
                vmin2 = np.min(data_k[data_k != meteva.base.IV])
            else:
                vmin2 = vmin1[k]

            if vmax is None:
                vmax2 = np.max(data_k[data_k != meteva.base.IV])
            else:
                vmax2 = vmax1[k]

            dmax = vmax2- vmin2

            if vmin is None:
                if vmin2 < 0:
                    vmin2 = vmin2 - 0.1 * dmax
            if vmax is None:
                vmax2 = vmax2 + 0.5 * dmax
            plt.ylim(vmin2,vmax2)
        if legend_num>1:
            legend_col = int(width_fig *0.8)
            if legend_col <1:legend_col = 1
            legend_row = int(math.ceil(legend_num / legend_col))
            legend_col = int(math.ceil(legend_num / legend_row))

            by = 0.95 + legend_row * 0.03
            if subplot_num >1:
                fig.legend(fontsize = sup_fontsize *0.9,ncol = legend_col,loc = "upper center",
                       bbox_to_anchor=(0.55,by))
            else:
                plt.legend(fontsize = sup_fontsize *0.9,ncol = legend_col,loc = "upper center")



    else:
        print("array不能超过3维")
        return
        xticks = []
        for index in index_list:
            if not type(index) == str:
                index = str(index)
            xticks.append(index)
    if save_path is None:
        show = True
    else:
        meteva.base.creat_path(save_path)
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()



def plot(array,name_list_dict = None,legend = None,axis = None,ylabel = "Value",vmin = None,vmax = None,ncol = None,save_path = None,show = False,dpi = 300,title =""):
    if len(array[array!=meteva.base.IV]) ==0:
        print("所有的值都为缺失值")
        return
    if vmin is None:
        vmin1 = np.min(array[array != meteva.base.IV])
    else:
        vmin1 = vmin
    if vmax is None:
        vmax1 = np.max(array[array != meteva.base.IV])
    else:
        vmax1 = vmax

    dmax = vmax1 - vmin1
    if vmin is None:
        if vmin1 < 0:
            vmin1 = vmin1 - 0.1 * dmax
    if vmax is None:
        vmax1 = vmax1 + 0.5 * dmax

    sup_fontsize = 10
    shape = array.shape
    if len(shape) ==1:
        if name_list_dict is None:
            name_list_dict = {}
            name_list_dict["x"] = np.arange(array.size).tolist()

        xlabel = list(name_list_dict.keys())[0]
        xticks = name_list_dict[xlabel]
        width = meteva.base.plot_tools.caculate_axis_width(xticks, sup_fontsize)
        if width > 10:
            for i in range(len(xticks)):
                if i % 2 == 1:
                    xticks[i] = "|\n" + xticks[i]
            width = 10
        elif width < 5:
            width = 5
        height = width / 2
        fig = plt.figure(figsize=(width, height), dpi=dpi)
        x = np.arange(array.size)

        dat0 = array
        index_iv = np.where(dat0 == meteva.base.IV)
        if len(index_iv) == 0:
            plt.plot(x, dat0)
        else:
            dat0_all = set_plot_IV(dat0)
            plt.plot(x, dat0_all, "--", linewidth=0.5, color="k")
            x_iv = x[index_iv[0]]
            dat0_iv = dat0_all[index_iv[0]]
            plt.plot(x_iv, dat0_iv, "x", color='k')
            dat0_notiv = dat0.copy()
            dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
            plt.plot(x, dat0_notiv)

        plt.xticks(x,xticks,fontsize = sup_fontsize * 0.8)
        plt.yticks(fontsize=sup_fontsize * 0.8)
        plt.xlabel(xlabel,fontsize=sup_fontsize * 0.9)
        plt.ylabel(ylabel,fontsize = sup_fontsize * 0.9)
        if isinstance(title,list):
            title = title[0]
        plt.title(title,fontsize = sup_fontsize)

        if vmin is None:
            vmin1 = np.min(array[array != meteva.base.IV])
        else:
            vmin1 = vmin
        if vmax is None:
            vmax1 = np.max(array[array != meteva.base.IV])
        else:
            vmax1 = vmax

        dmax = vmax1 - vmin1
        if vmin is None:
            if vmin1 < 0:
                vmin1 = vmin1 - 0.1 * dmax
        if vmax is None:
            vmax1 = vmax1 + 0.2 * dmax
        plt.ylim(vmin1,vmax1)

    elif len(shape)==2:
        if name_list_dict is None:
            name_list_dict = {}
            name_list_dict["x"] = np.arange(shape[0]).tolist()
            name_list_dict["y"] = np.arange(shape[1]).tolist()
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
        if dat is None:
            dat = array
        if legend not in keys:
            print("legend 参数的取值必须是name_list_dict的key")
        if axis not in keys:
            print("axis 参数的取值必须是name_list_dict的key")
        legend_list = name_list_dict[legend]
        legend_num = len(legend_list)
        xticks = name_list_dict[axis]
        width = meteva.base.plot_tools.caculate_axis_width(xticks, sup_fontsize,legend_num)

        if width > 10:
            for i in range(len(xticks)):
                if i % 2 == 1:
                    xticks[i] = "|\n" + str(xticks[i])
            width = 10
        elif width < 5:
            width = 5
        height = width / 2
        legend_col = int(width * 0.8)
        legend_row = int(math.ceil(legend_num/legend_col))
        legend_col = int(math.ceil(legend_num/legend_row))

        fig = plt.figure(figsize=(width, height), dpi=dpi)
        x = np.arange(len(xticks))
        width = 0.8 / (legend_num+2)

        for i in range(legend_num):
            #x1 = x + (i - legend_num/2 + 0.5) * width
            #plt.plot(x, dat[i,:],label = legend_list[i])

            dat0 = dat[i, :]
            index_iv = np.where(dat0 == meteva.base.IV)
            if len(index_iv) == 0:
                plt.plot(x, dat0,label = legend_list[i])
            else:
                dat0_all = set_plot_IV(dat0)
                plt.plot(x, dat0_all, "--", linewidth=0.5, color="k")
                x_iv = x[index_iv[0]]
                dat0_iv = dat0_all[index_iv[0]]
                plt.plot(x_iv, dat0_iv, "x", color='k')
                dat0_notiv = dat0.copy()
                dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
                plt.plot(x, dat0_notiv, label=name_list_dict[legend][i])


        plt.legend(fontsize =sup_fontsize * 0.8,ncol = legend_col,loc = "upper center")
        plt.xticks(x, xticks, fontsize=sup_fontsize * 0.8)
        plt.yticks(fontsize=sup_fontsize * 0.8)
        plt.xlabel(axis, fontsize=sup_fontsize * 0.9)
        plt.ylabel(ylabel, fontsize=sup_fontsize * 0.9)
        if isinstance(title,list):
            title = title[0]
        plt.title(title, fontsize=sup_fontsize)
        plt.xlim(-0.5, len(xticks)-0.5)


        if vmin is None:
            vmin1 = np.min(array[array != meteva.base.IV])
        else:
            vmin1 = vmin
        if vmax is None:
            vmax1 = np.max(array[array != meteva.base.IV])
        else:
            vmax1 = vmax

        dmax = vmax1 - vmin1
        if vmin is None:
            if vmin1 < 0:
                vmin1 = vmin1 - 0.1 * dmax
        if vmax is None:
            vmax1 = vmax1 + 0.5 * dmax

        plt.ylim(vmin1,vmax1)


    elif len(shape)==3:

        if name_list_dict is None:
            name_list_dict["z"] = np.arange(shape[0])
            name_list_dict["y"] = np.arange(shape[1])
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
        legend_num = len(name_list_dict[legend])
        width_axis = meteva.base.plot_tools.caculate_axis_width(name_list_dict[axis], sup_fontsize,legend_num)

        width_wspace = sup_fontsize * 0.1
        width_one_subplot = width_axis +width_wspace
        subplot_num = len(name_list_dict[subplot])
        spasify = 1
        if width_one_subplot >10:
            spasify = int(math.ceil(width_one_subplot/10))
            width_one_subplot = 10
        if ncol is None:
            ncol = int(10/width_one_subplot)
            nrow = int(math.ceil(subplot_num/ncol))
            ncol = int(math.ceil(subplot_num/nrow))
        else:
            nrow = int(math.ceil(len(name_list_dict[subplot])/ncol))
        width_fig = width_one_subplot * ncol
        height_axis = width_axis * 0.5
        height_hspace = sup_fontsize * 0.1
        height_suplegend = 1
        height_fig = nrow * (height_axis+height_hspace) + height_suplegend
        if width_fig>10:
            width_fig = 10
        if height_fig >7:height_fig = 7
        if width_fig<5: width_fig=5
        if height_fig<3:height_fig=3
        fig = plt.figure(figsize=(width_fig, height_fig), dpi=dpi)
        #plt.subplots_adjust(left=0, bottom=0.0, right=1.0, top = 1 - height_suplegend/height_fig,
        #                    hspace=height_hspace/(width_axis*0.5),wspace=width_wspace/width_axis)
        wspace = width_wspace/width_one_subplot
        plt.subplots_adjust(left=0, bottom=0.0, right=1.0, top = 1 - height_suplegend/height_fig,
                            hspace=0.08,wspace=wspace)
        if vmin is not None:
            if isinstance(vmin,list):
                if len(vmin) != subplot_num:
                    print("vmin 参数的个数和 子图个数不一致，请重新设置")
                    return
                else:
                    vmin1 = vmin
            else:
                vmin1 = vmin * np.ones(subplot_num)
                vmin1 = vmin1.tolist()

        if vmax is not None:
            if isinstance(vmax,list):
                if len(vmax) != subplot_num:
                    print("vmax 参数的个数和 子图个数不一致，请重新设置")
                    return
                else:
                    vmax1 = vmax
            else:
                vmax1 = vmax * np.ones(subplot_num)

        for k in range(subplot_num):
            plt.subplot(nrow, ncol, k + 1)
            x = np.arange(len(name_list_dict[axis]))
            width = 0.8 / (legend_num + 2)
            for i in range(legend_num):
                dat0 = data[k, i, :]
                index_iv = np.where(dat0 == meteva.base.IV)
                if len(index_iv) ==0:
                    if k == 0:
                        plt.plot(x, data[k, i, :], label=name_list_dict[legend][i])
                    else:
                        plt.plot(x, data[k, i, :])
                else:
                    dat0_all = set_plot_IV(dat0)
                    plt.plot(x, dat0_all, "--", linewidth=0.5, color="k")
                    x_iv = x[index_iv[0]]
                    dat0_iv = dat0_all[index_iv[0]]
                    plt.plot(x_iv, dat0_iv, "x", color='k')
                    dat0_notiv = dat0.copy()
                    dat0_notiv[dat0_notiv == meteva.base.IV] = np.nan
                    if k==0:
                        plt.plot(x,dat0_notiv,label=name_list_dict[legend][i])
                    else:
                        plt.plot(x, dat0_notiv)

            #plt.legend(fontsize=sup_fontsize * 0.8, ncol=legend_col, loc="upper center")
            ki = k % ncol
            kj = int(k / ncol)
            knext_row = ki + (kj+1) * ncol
            if knext_row>=subplot_num:
                plt.xticks(x[::spasify], name_list_dict[axis][::spasify], fontsize=sup_fontsize * 0.8)
                plt.xlabel(axis, fontsize=sup_fontsize * 0.9)
            else:
                plt.xticks([])

            #plt.xticks(x[::spasify], name_list_dict[axis][::spasify], fontsize=sup_fontsize * 0.8)
            plt.yticks(fontsize=sup_fontsize * 0.8)
            #plt.xlabel(axis, fontsize=sup_fontsize * 0.9)
            plt.ylabel(ylabel, fontsize=sup_fontsize * 0.9)

            if isinstance(title, list):
                if(len(title) != subplot_num):
                    print("子图数和设置的子图标题数不一致")
                    return
                title1 = title[k]
            else:
                if subplot_num>1:
                    title1 = title +"("+ subplot +"_"+ str(name_list_dict[subplot][k])+")"
                else:
                    title1 = title

            y1 =  1 - 0.035 *  sup_fontsize / (height_fig/nrow)
            plt.title(title1, fontsize=sup_fontsize,y = y1)

            #plt.title(title1, fontsize=sup_fontsize)

            plt.xlim(-0.5, len(name_list_dict[axis]) - 0.5)

            data_k = data[k, :, :]
            if vmin is None:
                vmin2 = np.min(data_k[data_k != meteva.base.IV])
            else:
                vmin2 = vmin1[k]

            if vmax is None:
                vmax2 = np.max(data_k[data_k != meteva.base.IV])
            else:
                vmax2 = vmax1[k]

            dmax = vmax2 - vmin2

            if vmin is None:
                if vmin2 < 0:
                    vmin2 = vmin2 - 0.1 * dmax
            if vmax is None:
                vmax2 = vmax2 + 0.5 * dmax
            plt.ylim(vmin2, vmax2)
        if legend_num > 1:
            legend_col = int(width_fig * 0.8)
            if legend_col < 1: legend_col = 1
            legend_row = int(math.ceil(legend_num / legend_col))
            legend_col = int(math.ceil(legend_num / legend_row))

            by = 0.95 + legend_row * 0.03
            if subplot_num > 1:
                fig.legend(fontsize=sup_fontsize * 0.9, ncol=legend_col, loc="upper center",
                           bbox_to_anchor=(0.55, by))
            else:
                plt.legend(fontsize=sup_fontsize * 0.9, ncol=legend_col, loc="upper center")

            '''
            plt.ylim(vmin1, vmax1)
            if len(name_list_dict[axis]) > 30:
                plt.grid()
            if legend_num>1:
                width_axis = width_fig/ncol
                legend_col = int(width_axis *0.8)
                legend_row = int(math.ceil(legend_num / legend_col))
                legend_col = int(math.ceil(legend_num / legend_row))
                plt.legend(fontsize = sup_fontsize *0.9,ncol = legend_col,loc = "upper center")
            '''
    else:
        print("array不能超过3维")
        return
        xticks = []
        for index in index_list:
            if not type(index) == str:
                index = str(index)
            xticks.append(index)
    if save_path is None:
        show = True
    else:
        meteva.base.creat_path(save_path)
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show:
        plt.show()
    plt.close()

def mesh_tdt(sta,x = "time",save_dir = None,save_path = None,
                   clev = None,cmap = None,show = False,xtimetype = "mid",dpi = 300,annot =True,title = "预报准确性和稳定性对比图"):


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
    dh_x = np.min(dhs_ob_not0)
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
        str1 = str(day) + "日" + str(hour) + "时"
        #else:
        #    str1 = str(hour) + "时"
        #print(str1)
        y_ticks.append(str1)

    width = 14
    x_plot,x_ticks = meteva.product.get_x_ticks(times_ob,width-2)
    x_plot /= dh_x
    #y_plot, y_ticks = meteva.product.get_y_ticks(times_fo, height)
    if xtimetype == "right":
        x_plot  = x_plot+1
    elif xtimetype == "left":
        x_plot = x_plot +0
    else:
        x_plot = x_plot +0.5
    if annot:
        annot = col <120
    annot_size = width * 50 / col
    if annot_size >16:
        annot_size= 16

    nids = len(ids)
    nfo = len(data_names) - 1
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
    for d in range(nfo):
        data_name = data_names[d+1]
        sta_one_member = meteva.base.in_member_list(sta, [data_names[0],data_name])
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
                dat[index_i,j] = sta_on_row.values[:,-1] - sta_on_row.values[:,-2]
            mask = np.zeros_like(dat.T)
            mask[dat.T == meteva.base.IV] = True

            vmin = np.min(dat[dat != meteva.base.IV])
            vmax = np.max(dat[dat != meteva.base.IV])

            height = width * row / col + 2
            f, ax2 = plt.subplots(figsize=(width, height), nrows=1, edgecolor='black',dpi = dpi)
            plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)


            if cmap_error is None:
                cmap_error ="bwr"
                cmap_part = cmap_error

            sns.heatmap(dat.T, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax, center=None, robust=False, annot=annot,fmt='.0f'
            , annot_kws = {'size': annot_size})
            ax2.set_xlabel('实况时间',fontsize = 16)
            ax2.set_ylabel('起报时间',fontsize = 16)
            ax2.set_xticks(x_plot)
            ax2.set_xticklabels(x_ticks,rotation=360, fontsize=14)
            ax2.set_yticks(y_plot)
            ax2.set_yticklabels(y_ticks, rotation=360, fontsize=14)

            ax2.grid(linestyle='--', linewidth=0.5)
            ax2.set_ylim(row, 0)
            ax2.set_title(title, loc='left', fontweight='bold', fontsize=18)
            rect = patches.Rectangle((0,0 ), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
            ax2.add_patch(rect)
            #plt.tick_params(top='on', right='on', which='both')  # 显示上侧和右侧的刻度
            plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
            plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内

            save_path1 = None
            if(save_path is None):
                if save_dir is None:
                    show = True
                else:
                    save_path1 = save_dir +"/" +data_name+"_"+str(id) + ".png"
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
