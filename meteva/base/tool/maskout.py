# -*- coding: utf-8 -*-
########################################################################################################################
# ### This module enables you to maskout the unneccessary data outside the
#                     interest region on a matplotlib-plotted output instance
# ################### in an effecient way,You can use this script for free   ###########################################
# ######################################################################################################################
# ####USAGE:INPUT include 'originfig':the matplotlib instance##
#                         'ax': the Axes instance
#                         'shapefile': the shape file used for generating a basemap A
#                         'region':the name of a region of on the basemap A,outside the region the data is to be maskout
#           OUTPUT    is  'clip' :the the masked-out or clipped matplotlib instance.
import shapefile
from matplotlib.path import Path
from matplotlib.patches import PathPatch
import pkg_resources
import numpy as np

def getPathFromShp(shpfile, region):
    try:
        sf = shapefile.Reader(shpfile)
        vertices = []  # 这块是已经修改的地方
        codes = []  # 这块是已经修改的地方

        for shape_rec in sf.shapeRecords():
            # if shape_rec.record[3] == region:  # 这里需要找到和region匹配的唯一标识符，record[]中必有一项是对应的。
            if region == [100000] or shape_rec.record[4] in region:  # 这块是已经修改的地方
                pts = shape_rec.shape.points
                prt = list(shape_rec.shape.parts) + [len(pts)]
                for i in range(len(prt) - 1):
                    for j in range(prt[i], prt[i + 1]):
                        vertices.append((pts[j][0], pts[j][1]))
                    codes += [Path.MOVETO]
                    codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                    codes += [Path.CLOSEPOLY]
                path = Path(vertices, codes)
        return path
    except Exception as err:
        print(err)
        return None


def shp2clip(originfig, ax, shpfile, region):
    sf = shapefile.Reader(shpfile)
    vertices = []  # 这块是已经修改的地方
    codes = []  # 这块是已经修改的地方
    region_lower = []
    if isinstance(region,list):
        for strs  in region:
            region_lower.append(strs.lower())
    else:
        region_lower.append(region.lower())
    for shape_rec in sf.shapeRecords():
        # if shape_rec.record[3] == region:  # 这里需要找到和region匹配的唯一标识符，record[]中必有一项是对应的。

        #if(len(shape_rec.record) ==1):continue
        if shape_rec.record[3].lower() in region_lower:  # 这块是已经修改的地方
            pts = shape_rec.shape.points
            prt = list(shape_rec.shape.parts) + [len(pts)]
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i + 1]):
                    vertices.append((pts[j][0], pts[j][1]))
                codes += [Path.MOVETO]
                codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                codes += [Path.CLOSEPOLY]
            path = Path(vertices, codes)
            # extents = path.get_extents()
            patch = PathPatch(path, transform=ax.transData, facecolor='none', edgecolor='black')
    for contour in originfig.collections:
        contour.set_clip_path(patch)
    return path, patch



def shp2clip_pro_id(originfig, ax, shpfile, num_list):
    sf = shapefile.Reader(shpfile)
    vertices = []  # 这块是已经修改的地方
    codes = []  # 这块是已经修改的地方

    shape_recs = sf.shapeRecords()

    for i in range(len(shape_recs)):
        # if shape_rec.record[3] == region:  # 这里需要找到和region匹配的唯一标识符，record[]中必有一项是对应的。

        #if(len(shape_rec.record) ==1):continue

        if i in num_list:  # 这块是已经修改的地方
            shape_rec = shape_recs[i]
            pts = shape_rec.shape.points
            prt = list(shape_rec.shape.parts) + [len(pts)]
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i + 1]):
                    vertices.append((pts[j][0], pts[j][1]))
                codes += [Path.MOVETO]
                codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                codes += [Path.CLOSEPOLY]
            path = Path(vertices, codes)
            # extents = path.get_extents()
            patch = PathPatch(path, transform=ax.transData, facecolor='none', edgecolor='black')
    for contour in originfig.collections:
        contour.set_clip_path(patch)
    return path, patch




def shp2clip_by_lines(originfig, ax, line_list):
    vertices = []  # 这块是已经修改的地方
    codes = []  # 这块是已经修改的地方
    for i in range(len(line_list)):
        # if shape_rec.record[3] == region:  # 这里需要找到和region匹配的唯一标识符，record[]中必有一项是对应的。

        #if(len(shape_rec.record) ==1):continue
        pts = line_list[i]
        for j in range(len(pts)):
            vertices.append((pts[j][0], pts[j][1]))
        vertices.append((pts[0][0], pts[0][1]))
        codes += [Path.MOVETO]
        codes += [Path.LINETO] * (len(pts)-1)
        codes += [Path.CLOSEPOLY]
    path = Path(vertices, codes)
        # extents = path.get_extents()
    patch = PathPatch(path, transform=ax.transData, facecolor='none', edgecolor='black')
    for contour in originfig.collections:
        contour.set_clip_path(patch)
    return path, patch


def shp2clip_by_region_name(originfig, ax, region_name_list):
    province = pkg_resources.resource_filename('meteva', "resources/maps/Province")

    province_ch_name = ["北京","天津","河北","山西","内蒙古",
                        "辽宁","吉林","黑龙江","上海","江苏",
                        "浙江","安徽","福建","江西", "山东",
                        "河南","湖北","湖南","广东","广西",
                        "海南","重庆","四川","贵州","云南",
                        "西藏","陕西","甘肃","青海","宁夏",
                        "新疆","台湾","香港","澳门"]

    province_name =["beijing","tianjin","hebei","shanxi","neimenggu",
                    "liaoning", "jilin", "heilongjiang", "shanghai", "jiangsu",
                    "zhejiang", "anhui", "fujian", "jiangxi", "shandong",
                    "henan", "hubei", "hunan", "guangdong", "guangxi",
                    "hainan", "chongqing", "sichuan", "guizhou", "yunnan",
                    "xizang", "shaanxi", "gansu", "qinghai", "ningxia",
                    "xinjiang", "taiwan", "xianggang", "aomen"]


    region_id_list = []
    #print(region_name_list)
    for region_name in region_name_list:
        if region_name.lower()=="china" or region_name=="中国":
            region_id_list.extend(np.arange(34).tolist())
        else:
            for i in range(len(province_name)):
                if region_name.find(province_ch_name[i])>=0:
                    region_id_list.append(i)
                if region_name.lower().find(province_name[i])>=0:
                    region_id_list.append(i)

    #print(region_id_list)
    region_id_list = list(set(region_id_list))
    shp2clip_pro_id(originfig, ax, province, region_id_list)


def shp2clip_by_shpfile(originfig, ax, shpfile):
    sf = shapefile.Reader(shpfile)
    vertices = []  # 这块是已经修改的地方
    codes = []  # 这块是已经修改的地方
    shape_recs = sf.shapeRecords()
    for i in range(len(shape_recs)):
        # if shape_rec.record[3] == region:  # 这里需要找到和region匹配的唯一标识符，record[]中必有一项是对应的。

        # if(len(shape_rec.record) ==1):continue
            shape_rec = shape_recs[i]
            pts = shape_rec.shape.points
            prt = list(shape_rec.shape.parts) + [len(pts)]
            for i in range(len(prt) - 1):
                for j in range(prt[i], prt[i + 1]):
                    vertices.append((pts[j][0], pts[j][1]))
                codes += [Path.MOVETO]
                codes += [Path.LINETO] * (prt[i + 1] - prt[i] - 2)
                codes += [Path.CLOSEPOLY]
            path = Path(vertices, codes)
            # extents = path.get_extents()
            patch = PathPatch(path, transform=ax.transData, facecolor='none', edgecolor='black')
    for contour in originfig.collections:
        contour.set_clip_path(patch)
    return path, patch

