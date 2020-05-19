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
        if shptype != shp.shapeType:
            print(shapefile)
            raise ValueError('readshapefile can only handle a single shape type per file')
        if shptype not in [1,3,5,8]:
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
    names = {'nation': "bou1_4p", 'province': "bou2_4p",
             'county': "BOUNT_poly", 'river': "hyd1_4p",
             'river_high': "hyd2_4p"}
        # get shape file and information
    shpfile = pkg_resources.resource_filename(
        'meteva', "resources/maps/" + names[name])
    shp1 = readshapefile(shpfile, default_encoding=encoding)
    lines = LineCollection(shp1,antialiaseds=(1,))
    lines.set_color(edgecolor)
    lines.set_linewidth(lw)
    lines.set_label('_nolabel_')
    ax.add_collection(lines)


def contourf_2d_grid(grd,save_path = None,title = None,clevs= None,cmap = None,add_county_line = False,show = False,dpi = 200):

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
    add_china_map_2basemap(ax, grid=grid0, edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
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


def pcolormesh_2d_grid(grd,save_path = None,title = None,clevs= None,cmap = None,add_county_line = False,show = False,dpi = 200):

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

    add_china_map_2basemap(ax, name="province", edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "省界"

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


def scatter_sta(sta,map_extend = None, value_column=0, save_path=None, title=None, clevs=None, cmap=None,
                fix_size = True,add_county_line = False,show = False,print_max = 1,mean_value = None,threshold = None,dpi = 200):

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