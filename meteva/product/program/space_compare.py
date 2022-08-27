import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import numpy  as np
from meteva.base.tool.plot_tools import add_china_map_2basemap
#from sklearn.linear_model import LinearRegression
import meteva
from meteva.base import IV
import math
from matplotlib.colors import BoundaryNorm
from matplotlib.patches import Polygon
import os
import datetime
import scipy.stats as st


def rain_24h_sg(sta_ob,grd_fo,save_path=None,show  = False,dpi = 200,add_county_line = False,sup_fontsize = 10,point_size = None):
    grade_list = [0.1, 10, 25, 50, 100, 250, 1000]
    rain_sg(sta_ob, grd_fo, grade_list, save_path=save_path, show=show, dpi=dpi, add_county_line=add_county_line,sup_fontsize=sup_fontsize,point_size = point_size)


def rain_sg(sta_ob,grd_fo,grade_list,save_path=None,show  = False,dpi = 200,add_county_line = False,x_y = "dtime_member",sup_fontsize = 10,
            height = None,width = None,add_worldmap =False,sup_title = None,point_size = None,ts_grade = None):

    '''
    #绘制24小时降水实况与预报对比图
    :param grd_fo: 输入的网格数据，包含一个平面的网格场
    :param sta_ob:  输入的站点数据，包含一个时刻的站点数据列表
    :param filename: 图片输出路径，缺省时会以调试窗口形式弹出
    :return: 无返回值
    '''
    if len(grade_list)!=7:
        print("grade_list 暂时仅支持长度为7的列表，包含小雨、中雨、大雨、暴雨、大暴雨、特大暴雨以及一个降水上限值")
        return
    grid_fo = meteva.base.get_grid_of_data(grd_fo)

    levels_all = grd_fo["level"].values
    times_all = grd_fo["time"].values
    dtimes_all = grd_fo["dtime"].values
    members_all = grd_fo["member"].values

    clevs = grade_list
    colors_grid = ["#FFFFFF", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#000000"]
    colors_sta = ['#FFFFFF',"#000000","#00FFDD", '#00FF00', '#FFFF00', '#FF9900', '#FE1B00', '#FF0000']

    sta_ob_in = meteva.base.sele_by_para(sta_ob, gxy=grid_fo,value=[0,2000])
    sta_ob_plot = meteva.base.sele_by_para(sta_ob, gxy=grid_fo,value=[grade_list[0],2000])

    dat_ob = sta_ob_plot.values[:, -1]
    #dat_ob[dat_ob > 2000] = 0

    x_ob = sta_ob_plot.loc[:, "lon"].values
    y_ob = sta_ob_plot.loc[:, "lat"].values

    clevs = [0]
    clevs.extend(grade_list)
    clevs_name = ["0"]
    for g0 in range(len(grade_list) - 2):
        if grade_list[g0] == math.floor(grade_list[g0]):
            gs0 = str(int(grade_list[g0]))
        else:
            gs0 = '%.1f' % (grade_list[g0])

        if grade_list[g0 + 1] == math.floor(grade_list[g0 + 1]):
            gs1 = str(int(grade_list[g0 + 1]))
        else:
            gs1 = '%.0f' % (grade_list[g0 + 1])
        clevs_name.append(gs0 + "-" + gs1)
    clevs_name.append(">=" + str(int(grade_list[len(grade_list) - 2])))

    if point_size is None:
        pass

    valid_time = 0
    if "valid_time" in grd_fo.attrs.keys():
        valid_time = grd_fo.attrs["valid_time"]
    if ts_grade is None:ts_grade = grade_list[0]

    if len(levels_all) * len(times_all) * len(dtimes_all) * len(members_all) == 1:

        # 通过经纬度范围设置画幅
        hight = 5.6
        title_hight = 0.3
        legend_hight = 0.6
        left_plots_width = 0
        right_plots_width = 0
        width = (hight - title_hight - legend_hight) * grid_fo.nlon / grid_fo.nlat + left_plots_width + right_plots_width
        map_width = width - left_plots_width - right_plots_width

        fig = plt.figure(figsize=(width, hight),dpi=dpi)
        # 设置画幅的布局方式，
        rect1 = [left_plots_width / width, 0.12, (width - right_plots_width - left_plots_width) / width, 0.84]  # 左下宽高,中央对比图
        ylabelwidth = 0.52 / width
        rect2 = [ylabelwidth, 0.08, left_plots_width / width - ylabelwidth - 0.005, 0.40]  # 左下宽高，散点回归图
        ylabelwidth = 0.65 / width
        rect3 = [ylabelwidth, 0.60, left_plots_width / width - ylabelwidth - 0.005, 0.18]  # 左下宽高，频谱统计柱状图
        rect4 = [0.01, 0.79, left_plots_width / width - 0.045, 0.15]  # 左下宽高，左侧文字
        rect5 = [(width - right_plots_width) / width + 0.005, -0.035, right_plots_width / width - 0.01, 0.90]  # 左下宽高，右侧文字
        width_ob_fo_str = 0.3
        if (map_width < 3.5):
            width_bar = 2.1  # 根据中间地图的宽度，来确定预报colorbar的尺寸
            sta_legend_size = 5  # 根据中间地图的宽度，来确定观测legend的size
        else:
            sta_legend_size = 7
            width_bar = 2.9

        rect6 = [(left_plots_width + 0.5 * map_width - 0.5 * width_bar + 0.5 * width_ob_fo_str) / width, 0.00,
                 width_bar / width, 0.02]  # 预报colorbar
        rect7 = [(left_plots_width + 0.5 * map_width - 0.5 * width_bar - 0.5 * width_ob_fo_str) / width, 0.00,
                 width_ob_fo_str / width, 0.3]  # 观测文字


        ax = plt.axes(rect1)
        # 设置地图背景
        add_china_map_2basemap(ax, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
        if add_county_line:
            add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "省界"
        ax.set_xlim((grid_fo.slon, grid_fo.elon))
        ax.set_ylim((grid_fo.slat, grid_fo.elat))

        # 绘制格点预报场
        x = np.arange(grid_fo.nlon) * grid_fo.dlon + grid_fo.slon
        y = np.arange(grid_fo.nlat) * grid_fo.dlat + grid_fo.slat

        dat = grd_fo.values.squeeze()

        plt.rcParams['xtick.direction'] = 'in'
        plt.rcParams['ytick.direction'] = 'in'
        plot_grid = ax.contourf(x, y, dat, clevs, colors=colors_grid)  # 填色图
        time_str = meteva.base.tool.time_tools.time_to_str(grid_fo.gtime[0])
        dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
        if type(grid_fo.members[0]) == str:
            model_name = grid_fo.members[0]
        else:
            model_name = str(grid_fo.members[0])

        var_name = ""
        if sta_ob.attrs is not None:
            if "var_cn_name" in sta_ob.attrs.keys():
                var_name = sta_ob.attrs["var_cn_name"]
                if var_name=="":
                    var_name = sta_ob.attrs["var_name"]
        title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效"+var_name+"预报和观测"

        if map_width < 3:
            #title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
            ax.set_title(title, fontsize=7)
        elif map_width < 4:
            #title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
            ax.set_title(title, fontsize=10)
        else:
            #title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
            ax.set_title(title, fontsize=11)

        colorbar_position_grid = fig.add_axes(rect6)  # 位置[左,下,宽,高]
        cb = plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='horizontal')
        cb.ax.tick_params(labelsize=8)  # 设置色标刻度字体大小。
        # plt.text(0, 0, "预报(mm)", fontsize=8)

        # 绘制填色站点值
        sta_ob_in = meteva.base.in_grid_xy(sta_ob, grid=grid_fo)

        dat = sta_ob_in.values[:, -1]
        dat[dat > 1000] = 0
        clevs = [0]
        clevs.extend(grade_list)
        clevs_name = ["0"]
        for g0 in range(len(grade_list)-2):
            if grade_list[g0] == math.floor(grade_list[g0]):
                gs0 = str(int(grade_list[g0]))
            else:
                gs0 = '%.1f' % (grade_list[g0])

            if grade_list[g0+1] == math.floor(grade_list[g0+1]):
                gs1 = str(int(grade_list[g0+1]))
            else:
                gs1 = '%.0f' % (grade_list[g0+1])
            clevs_name.append(gs0+"-"+gs1)
        clevs_name.append(">="+ str(int(grade_list[len(grade_list)-2])))

        #cleves_name = ["0", "0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"]
        for i in range(len(clevs) - 1):
            index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
            if (len(index0[0]) > 0):
                x = np.squeeze(sta_ob_in["lon"].values[index0])
                y = np.squeeze(sta_ob_in["lat"].values[index0])
                if (len(index0) == 1):
                    x = np.array([x])
                    y = np.array([y])
                    if (i > 0):
                        ax.scatter(x, y, c=colors_sta[i],  s=3, label=clevs_name[i],
                                   linewidths=0.3, edgecolor='k')
                    else:
                        ax.scatter(x, y, c=colors_sta[i], s=1, label=clevs_name[i],
                                   linewidths=0.1, edgecolor="k")
        ax.legend(facecolor='whitesmoke', loc="lower center", ncol=4, edgecolor='whitesmoke',
                  prop={'size': sta_legend_size},
                  bbox_to_anchor=(0.5 + 0.5 * width_ob_fo_str / map_width, -0.12))
        ax7 = plt.axes(rect7)
        ax7.axes.set_axis_off()
        plt.text(0, 0.00, "观测\n\n预报", fontsize=7)

        # 图片显示或保存
        if(save_path is not None):
            plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
        else:
            show = True
        if show:
            plt.show()
        plt.close()
        return
    else:
        ob_time_list = []
        ob_times = list(set(sta_ob_plot["time"].values))
        ob_times.sort()
        for ii in range(len(ob_times)):
            ob_time_list.append(meteva.base.all_type_time_to_datetime(ob_times[ii]))

        dtimes_valid = []
        fo_time_valid = []
        ob_time_valid = []
        for dtime1 in dtimes_all:
            for time1 in times_all:
                fo_time = meteva.base.all_type_time_to_datetime(time1)
                ob_time1 = fo_time + datetime.timedelta(hours=int(dtime1))
                if ob_time1 in ob_time_list:
                    dtimes_valid.append(dtime1)
                    fo_time_valid.append(fo_time)
                    ob_time_valid.append(ob_time1)
                    break
        if len(set(ob_time_valid))>1 and len(set(fo_time_valid))>1:
            print("参数x_y=dtime_member时，暂时不能支持多个起报时间和多个观测时间对应情况下的检验")

        if x_y == "dtime_member":
            x = grd_fo['lon'].values
            slon = x[0]
            elon = x[-1]
            y = grd_fo['lat'].values
            slat = y[0]
            elat = y[-1]
            rlon = x[-1] - x[0]
            rlat = y[-1] - y[0]

            height_title = sup_fontsize * 0.1
            height_bottem_xticsk = sup_fontsize * 0.05
            height_hspace = sup_fontsize * 0.01

            width_wspace = height_hspace
            width_colorbar = 0.0
            width_left_yticks = sup_fontsize * 0.03
            ncol = len(dtimes_valid)
            nrow = len(members_all)
            nplot = ncol * nrow


            if width is None and height is None:
                width = 8

            if width is None:
                height_all_plot = height - height_title - height_bottem_xticsk - (nrow - 1) * height_hspace
                height_map = height_all_plot / nrow
                width_map = height_map * rlon / rlat
                width_all_plot = width_map * ncol + (ncol - 1) * width_wspace
                width = width_all_plot + width_colorbar + width_left_yticks
            else:
                width_all_plot = width - width_colorbar - width_left_yticks - (ncol - 1) * width_wspace
                width_map = width_all_plot / ncol
                height_map = width_map * rlat / rlon
                height_all_plot = height_map * nrow + (nrow - 1) * height_hspace
                height = height_all_plot + height_title + height_bottem_xticsk



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
            for i in range(len(xticks)):
                xticks_label.append(str(round(xticks[i], 6)))
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
            for j in range(len(yticks)):
                if yticks[j] >= 0:
                    yticks_label.append(str(round(yticks[j], 6)) + "°N")
                else:
                    yticks_label.append(str(round(-yticks[j], 6)) + "°S")
                yticks_label_None.append("")


            fig = plt.figure(figsize=(width, height), dpi=dpi)


            cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=colors_sta, clevs=clevs, vmin=vmin, vmax=vmax)
            norm = BoundaryNorm(clevs, cmap1.N - 1)

            ax_up_right = None
            ylabel_seted = 0
            #print(ncol)
            #print(nrow)
            for pi in range(ncol):
                #print(str(pi) + " ---")
                if len(ob_time_valid) == 1:
                    dtime1 = dtimes_valid[ncol - pi - 1]
                    ob_time = ob_time_valid[0]
                    fo_time1 = None
                    for time1 in fo_time_valid:
                        fo_time = meteva.base.all_type_time_to_datetime(time1)
                        ob_time1 = fo_time + datetime.timedelta(hours=int(dtime1))
                        if ob_time1== ob_time:
                            fo_time1 = time1
                            break
                    if fo_time1 is None: continue
                else:
                    dtime1 = int(dtimes_valid[pi])
                    fo_time1 = fo_time_valid[pi]
                    ob_time1 = fo_time1 + datetime.timedelta(hours = dtime1)
                    sta_ob_plot1 = meteva.base.sele_by_para(sta_ob_plot,time = ob_time1)
                    x_ob = sta_ob_plot1.loc[:, "lon"].values
                    y_ob = sta_ob_plot1.loc[:, "lat"].values
                    dat_ob = sta_ob_plot1.values[:, -1]

                grd1 = meteva.base.in_time_list(grd_fo,[fo_time1])
                grd1 = meteva.base.in_dtime_list(grd1,[dtime1])

                for pj in range(nrow):
                    member1 = members_all[pj]
                    grd2 = meteva.base.in_member_list(grd1,[member1])


                    dat = grd2.values.squeeze()
                    rect1 = [(width_left_yticks + pi * (width_map + width_wspace)) / width,
                             (height_bottem_xticsk + (nrow - 1 - pj) * (height_map + height_hspace)) / height,
                             width_map / width,
                             height_map / height]
                    ax = plt.axes(rect1)

                    if pi ==ncol-1 and pj == 0:
                        ax_up_right = ax

                    if slon < 70 or elon > 140 or slat < 10 or elat > 60:
                        add_worldmap = True
                    if add_worldmap:
                        add_china_map_2basemap(ax, name="world", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "国界"

                    add_china_map_2basemap(ax, name="nation", edgecolor='k', lw=0.3, encoding='gbk', grid0=None)  # "省界"
                    add_china_map_2basemap(ax, edgecolor='k', lw=0.3, encoding='gbk')  # "省界"
                    if add_county_line:
                        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk', grid0=None)  # "县界"
                    ax.set_xlim((slon, elon))
                    ax.set_ylim((slat, elat))
                    if pj ==0:
                        if valid_time == 0:
                            ax.set_title(dtime1)
                        else:
                            dtime_str = str(dtime1 - valid_time) + "-"+ str(dtime1)
                            ax.set_title(dtime_str)

                    knext_row = pi + (pj + 1) * ncol
                    if knext_row >= nplot:
                        ax.set_xticks(xticks)
                        ax.set_xticklabels(xticks_label, fontsize=sup_fontsize * 0.8, family='Times New Roman')
                    else:
                        ax.set_xticks(xticks)
                        ax.set_xticklabels(xticks_label_None, fontsize=sup_fontsize * 0.8, family='Times New Roman')

                    if ylabel_seted == 0:
                        ax.set_yticks(yticks)
                        ax.set_yticklabels(yticks_label, fontsize=sup_fontsize * 0.8, family='Times New Roman')
                        plt.ylabel(member1)
                    else:
                        ax.set_yticks(yticks)
                        ax.set_yticklabels(yticks_label_None, fontsize=sup_fontsize * 0.8, family='Times New Roman')


                    if dat[0,0] == meteva.base.IV:continue
                    im1 = ax.contourf(x, y,dat, clevs, colors=colors_grid)
                    im2 = ax.scatter(x_ob, y_ob, c=dat_ob, cmap=cmap1, norm=norm,s = point_size)
                    grd2_to_sta = meteva.base.interp_gs_nearest(grd2, sta_ob_in)
                    ts = meteva.method.ts(sta_ob_in.values[:, -1], grd2_to_sta.values[:, -1], grade_list=[ts_grade])
                    ts_str = "%.3f" % ts
                    xt = slon + 0.01*(elon - slon)
                    yt = slat + 0.01*(elat - slat)
                    plt.text(xt, yt, ts_str, color = "#FF0000", fontsize=sup_fontsize, zorder=100)


                ylabel_seted = 1

            height_colorbar =0.95 * (ax_up_right.bbox.y1 - ax.bbox.y0) / fig.dpi / height/2


            location = [ax.bbox.x1 / fig.dpi / width + 0.005, ax.bbox.y0 / fig.dpi / height, 0.01,
                        height_colorbar]

            colorbar_position = fig.add_axes(location)  # 位置[左,下,宽,高]
            colorbar_fo = plt.colorbar(im1, cax=colorbar_position)
            colorbar_fo.set_label('预报', fontsize=sup_fontsize * 0.9)

            #cb.ax.tick_params(labelsize=sup_fontsize * 0.8)  # 设置色标刻度字体大小。

            y_sup_title = (height_bottem_xticsk + (nrow) * (height_map + height_hspace)) / height



            location = [ax.bbox.x1 / fig.dpi / width + 0.005, ax_up_right.bbox.y1 / fig.dpi / height - height_colorbar, 0.01,
                       height_colorbar]
            colorbar_position = fig.add_axes(location)  # 位置[左,下,宽,高]
            colorbar_ob = plt.colorbar(im2, cax=colorbar_position)
            colorbar_ob.set_label('观测', fontsize=sup_fontsize * 0.9)

            if sup_title is not None:
                plt.suptitle(sup_title, y=y_sup_title, fontsize=sup_fontsize * 1.2)

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
        else:
            pass




def rain_24h_comprehensive_sg(sta_ob,grd_fo, save_path=None,show = False,dpi = 200,add_county_line = False):
    grade_list = [0.1, 10, 25, 50, 100, 250, 1000]
    rain_comprehensive_sg(sta_ob,grd_fo,grade_list,save_path=save_path,show=show,dpi=dpi,add_county_line=add_county_line)


def rain_comprehensive_sg(sta_ob,grd_fo,grade_list, save_path=None,show = False,dpi = 200,add_county_line = False):
    '''
    #绘制24小时降水实况与预报综合对比检验图，画幅中央为预报实况的对比，左右两侧为各类检验指标
    :param grd_fo: 输入的网格数据，包含一个平面的网格场
    :param sta_ob:  输入的站点数据，包含一个时刻的站点数据列表
    :param filename: 图片输出路径，缺省时会以调试窗口形式弹出
    :return:无返回值
    '''
    if len(grade_list)!=7:
        print("grade_list 暂时仅支持长度为7的列表，包含小雨、中雨、大雨、暴雨、大暴雨、特大暴雨以及一个降水上限值")
        return
    grid_fo = meteva.base.get_grid_of_data(grd_fo)
    #通过经纬度范围设置画幅
    hight = 5.6
    title_hight = 0.3
    legend_hight = 0.6
    left_plots_width  = 3
    right_plots_width = 2.3
    width = (hight - title_hight - legend_hight) * grid_fo.nlon / grid_fo.nlat + left_plots_width + right_plots_width
    map_width = width - left_plots_width - right_plots_width
    map_area = (hight - title_hight - legend_hight) *map_width

    fig = plt.figure(figsize=(width, hight),dpi=dpi)
    # 设置画幅的布局方式，
    rect1 = [left_plots_width/width, 0.12, (width - right_plots_width - left_plots_width)/width, 0.84]  # 左下宽高,中央对比图
    ylabelwidth = 0.52/width
    rect2 = [ylabelwidth, 0.08, left_plots_width / width-ylabelwidth-0.005, 0.40]  # 左下宽高，散点回归图
    ylabelwidth = 0.65 / width
    rect3 = [ylabelwidth, 0.60, left_plots_width / width-ylabelwidth-0.005, 0.18]  # 左下宽高，频谱统计柱状图
    rect4 = [0.01, 0.79, left_plots_width / width-0.045, 0.15]  # 左下宽高，左侧文字
    rect5 = [(width - right_plots_width) / width+0.005, -0.035, right_plots_width/width-0.01, 0.90]  # 左下宽高，右侧文字
    width_ob_fo_str = 0.3
    if(map_width<3.5):
        width_bar = 2.1  #根据中间地图的宽度，来确定预报colorbar的尺寸
        sta_legend_size = 5 #根据中间地图的宽度，来确定观测legend的size
    else:
        sta_legend_size = 7
        width_bar = 2.9

    rect6 = [(left_plots_width + 0.5 * map_width - 0.5*width_bar + 0.5 * width_ob_fo_str)/width, 0.04, width_bar/width, 0.02]  #预报colorbar
    rect7 = [(left_plots_width + 0.5 * map_width - 0.5*width_bar - 0.5 * width_ob_fo_str)/width,0.04,width_ob_fo_str/width,0.3]  #观测文字
    #rect8 = [left_plots_width / width, 0.04, width_ob_fo_str / width, 0.3]  # 预报文字

    ax = plt.axes(rect1)
    # 设置地图背景
    add_china_map_2basemap(ax, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "省界"
    ax.set_xlim((grid_fo.slon, grid_fo.elon))
    ax.set_ylim((grid_fo.slat, grid_fo.elat))

    # 绘制格点预报场
    x = np.arange(grid_fo.nlon) * grid_fo.dlon + grid_fo.slon
    y = np.arange(grid_fo.nlat) * grid_fo.dlat + grid_fo.slat
    clevs =grade_list
    colors_grid = ["#D0DEEA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    dat = grd_fo.values.squeeze()
    #print(x)
    #print(y)
    #print(dat)
    plt.xticks([])
    plt.yticks([])
    plot_grid = ax.contourf(x, y, dat, clevs, colors=colors_grid)  # 填色图
    time_str = meteva.base.tool.time_tools.time_to_str(grid_fo.gtime[0])
    dati_str = time_str[0:4] + "年"+ time_str[4:6] + "月" +time_str[6:8] +"日" + time_str[8:10] + "时"
    if type(grid_fo.members[0]) == str:
        model_name = grid_fo.members[0]
    else:
        model_name = str(grid_fo.members[0])


    var_name = ""
    if sta_ob.attrs is not None:
        if "var_cn_name" in sta_ob.attrs.keys():
            var_name = sta_ob.attrs["var_cn_name"]
            if var_name=="":
                var_name = sta_ob.attrs["var_name"]
    title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效"+var_name+"预报和观测"

    if map_width <3:
        #title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
        ax.set_title(title,fontsize=7)
    elif map_width <4:
        #title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
        ax.set_title(title, fontsize=10)
    else:
        #title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
        ax.set_title(title, fontsize=11)

    colorbar_position_grid = fig.add_axes(rect6)  # 位置[左,下,宽,高]
    cb = plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='horizontal')
    cb.ax.tick_params(labelsize=8)  # 设置色标刻度字体大小。
    #plt.text(0, 0, "预报(mm)", fontsize=8)

    # 绘制填色站点值
    sta_ob_in = meteva.base.in_grid_xy(sta_ob, grid=grid_fo)
    colors_sta = ['#FFFFFF', '#0055FF', '#00FFB4', '#F4FF00', '#FE1B00', '#910000', '#B800BA']
    dat = sta_ob_in.values[:, -1]
    dat[dat > 1000] = 0
    clevs = [0]
    clevs.extend(grade_list)
    #clevs =grade_list
    clevs_name = ["0"]
    for g0 in range(len(grade_list)-2):
        if grade_list[g0] == math.floor(grade_list[g0]):
            gs0 = str(int(grade_list[g0]))
        else:
            gs0 = '%.1f' % (grade_list[g0])

        if grade_list[g0+1] == math.floor(grade_list[g0+1]):
            gs1 = str(int(grade_list[g0+1]))
        else:
            gs1 = '%.0f' % (grade_list[g0+1])
        clevs_name.append(gs0+"-"+gs1)
    clevs_name.append(">="+ str(int(grade_list[len(grade_list)-2])))
    #print(clevs_name)

    pointsize = int(100*map_area / len(dat))
    if(pointsize >30):pointsize = 30
    if(pointsize<1):pointsize = 1

    for i in range(len(clevs) - 1):
        index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
        if (len(index0[0]) > 0):
            x = np.squeeze(sta_ob_in["lon"].values[index0])
            y = np.squeeze(sta_ob_in["lat"].values[index0])
            if (len(index0) == 1):
                x = np.array([x])
                y = np.array([y])
                if (i > 0):
                    ax.scatter(x, y, c=colors_sta[i], s=3*pointsize, label=clevs_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i], s=3*pointsize, label=clevs_name[i],linewidths=0.0,edgecolor = "k")
    ax.legend(facecolor='gainsboro', loc="lower center",ncol=4, edgecolor='whitesmoke',prop={'size':sta_legend_size},
              bbox_to_anchor=(0.5 + 0.5 *width_ob_fo_str/map_width, -0.08))
    ax7 = plt.axes(rect7)
    ax7.axes.set_axis_off()
    plt.text(0, 0.00,"观测\n\n预报", fontsize=7)

    #ax.legend(loc="lower right", ncol=4, facecolor='whitesmoke', title="观测", edgecolor='whitesmoke', fontsize=9,
    #          bbox_to_anchor=(0, -0.32))
    # 散点回归图
    ax2 = plt.axes(rect2)
    sta_fo = meteva.base.interp_gs_nearest(grd_fo, sta_ob_in)
    #print(sta_fo)
    data_name = meteva.base.get_stadata_names(sta_ob_in)
    ob = sta_ob_in[data_name[0]].values
    data_name = meteva.base.get_stadata_names(sta_fo)
    fo = sta_fo[data_name[0]].values
    ob_fo = ob + fo
    index = np.where(~np.isnan(ob_fo))
    ob = ob[index]
    fo = fo[index]
    ax2.plot(fo, ob, '.', color='k')
    maxy = max(np.max(ob), np.max(fo)) + 5

    # 绘制比例线
    rate = np.sum(fo) / (np.sum(ob) + 1e-30)
    ob_line = np.arange(0, (maxy+1), (maxy+1) / 30)
    fo_rate = ob_line * 1
    ax2.plot(ob_line[0:30], fo_rate[0:30], 'b', linestyle='dashed')


    # 绘制回归线
    # X = np.zeros((len(ob), 1))
    # X[:, 0] = ob[:]
    # clf = LinearRegression().fit(X, fo)
    # X = np.zeros((len(ob_line), 1))
    # X[:, 0] = ob_line[:]
    # fo_rg = clf.predict(X)
    # ax2.plot(ob_line, fo_rg, color='r')
    # cor = np.corrcoef(ob,fo)
    # rg_text1 = "R = " + '%.2f' % (cor[0, 1])
    # rg_text2 = "y = " + '%.2f' % (clf.coef_[0]) + "* x + " + '%.2f' % (clf.intercept_)
    # print(rg_text2)
    slope, intercept, r_value, p_value, std_err = st.linregress(fo, ob)
    fo_rg = slope * ob_line + intercept
    ax2.plot(ob_line, fo_rg, color='r')
    rg_text1 = "R = " + '%.2f' % (r_value)
    if intercept >= 0:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X + " + '%.2f' % (intercept)
    else:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X - " + '%.2f' % (-intercept)


    plt.xlim(0, maxy)
    plt.ylim(0, maxy)
    plt.text(0.05 * maxy, 0.9 * maxy, rg_text1, fontsize=10)
    plt.text(0.05 * maxy, 0.8 * maxy, rg_text2, fontsize=10)
    maxy = max(np.max(ob), np.max(fo))
    ax2.set_xlabel("预报", fontsize=9)
    ax2.set_ylabel("观测", fontsize=9)
    ax2.set_title("Obs.vs Pred. Scatter plot", fontsize=12)
    # 设置次刻度间隔

    # 设置次刻度间隔
    if(maxy <5):
        xmi = 0.1
        Xmi = 1
    elif(maxy <50):
        xmi = 1
        if(maxy >25):
            Xmi = 10
        else:
            Xmi = 5
    elif (maxy <100):
        xmi = 2
        if(maxy >50):
            Xmi = 20
        else:
            Xmi = 10
    elif (maxy <250):
        xmi = 5
        if(maxy >100):
            Xmi = 50
        else:
            Xmi = 20
    elif (maxy <1000):
        xmi = 20
        if(maxy >500):
            Xmi = 200
        else:
            Xmi = 100
    else:
        xmi = 50
        Xmi = 250
    xmajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将x主刻度标签设置为次刻度10倍
    ymajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将y主刻度标签设置为次刻度10倍
    ax2.xaxis.set_major_locator(xmajorLocator)
    ax2.yaxis.set_major_locator(ymajorLocator)
    xminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将x轴次刻度标签设置xmi
    yminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将y轴次刻度标签设置ymi
    ax2.xaxis.set_minor_locator(xminorLocator)
    ax2.yaxis.set_minor_locator(yminorLocator)

    # 绘制频率柱状图
    p_ob = np.zeros(len(grade_list)-1)
    p_fo = np.zeros(len(grade_list)-1)
    x = np.arange(len(grade_list)-1) + 1
    for i in range(1, len(clevs) - 1, 1):
        index0 = np.where((ob >= clevs[i]) & (ob < clevs[i + 1]))
        p_ob[i - 1] = len(index0[0])
        index0 = np.where((fo >= clevs[i]) & (fo < clevs[i + 1]))
        p_fo[i - 1] = len(index0[0])

    ax3 = plt.axes(rect3)
    ax3.bar(x - 0.25, p_ob, width=0.2, facecolor="r", label="Obs")
    ax3.bar(x + 0.05, p_fo, width=0.2, facecolor="b", label="Pred")
    ax3.legend(loc="upper right")
    ax3.set_xlabel("precipitation threshold", fontsize=10)
    ax3.set_xticks(x)

    ax3.set_xticklabels(clevs_name[1:], fontsize=9)
    ax3.set_ylabel("point number", fontsize=10)
    ax3.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))

    # 绘制降水站点实况预报统计表

    ax4 = plt.axes(rect4)
    ax4.axes.set_axis_off()

    ob_has = ob[ob >= grade_list[0]]
    fo_has = fo[fo >= grade_list[0]]
    mean_fo = 0
    max_fo = 0
    mean_ob = 0
    max_ob = 0
    if len(fo_has)>1:
        mean_fo = np.mean(fo_has)
        max_fo = np.max(fo_has)
    if len(ob_has)>1:
        mean_ob = np.mean(ob_has)
        max_ob = np.max(ob_has)

    text = "降水站点实况和预报 n=" + str(len(ob)) + "\n"
    text += "=============================================\n"
    text += "                         观测           预报\n"
    text += "---------------------------------------------\n"
    text += "有降水站点数(>="+str(grade_list[0])+")     " + "%4d" % len(ob_has) + "           %4d" % len(fo_has) + "\n"
    text += "有降水站点数百分比%    " + "%6.1f" % (100*len(ob_has) / len(ob)) + "%15.1f" % (100*len(fo_has) / len(fo)) + "\n"
    text += "平均降水量(排除无降水) " + "%6.1f" % (mean_ob) + "%15.1f" % (mean_fo) + "\n"
    text += "最大降水量             " + "%6.1f" % (max_ob) + "%15.1f" % (max_fo)+"\n"
    text += "---------------------------------------------"
    plt.text(0, 0, text, fontsize=9)

    # 绘制统计检验结果

    ax5 = plt.axes(rect5)
    ax5.axes.set_axis_off()

    mae = meteva.method.continuous.score.mae(ob, fo)
    me = meteva.method.continuous.score.me(ob, fo)
    mse = meteva.method.continuous.score.mse(ob, fo)
    rmse = meteva.method.continuous.score.rmse(ob, fo)
    bias_c = meteva.method.continuous.score.bias_m(ob, fo)
    cor = meteva.method.continuous.score.corr(ob, fo)
    pc_sun_rain = meteva.method.pc_of_sun_rain(ob,fo)
    hfmc = meteva.method.yes_or_no.score.hfmc(ob, fo, clevs[1:])
    ts = meteva.method.yes_or_no.score.ts(ob, fo, clevs[1:])
    ets = meteva.method.yes_or_no.score.ets(ob, fo, clevs[1:])
    bias = meteva.method.yes_or_no.score.bias(ob, fo, clevs[1:])
    hit_rate = meteva.method.yes_or_no.score.pod(ob, fo, clevs[1:])
    mis_rate = meteva.method.yes_or_no.score.mr(ob, fo, clevs[1:])
    fal_rate = meteva.method.yes_or_no.score.far(ob, fo, clevs[1:])

    text = str(len(ob)) + "评分站点预报检验统计量\n"
    text += "Mean absolute error:" + "%6.2f" % mae + "\n"
    text += "Mean error:" + "%6.2f" % me + "\n"
    text += "Mean-squared error:" + "%6.2f" % mse + "\n"
    text += "Root mean-squared error:" + "%6.2f" % rmse + "\n"
    text += "Bias:" + "%6.2f" % bias_c + "\n"
    text += "Correlation ceoefficient:" + "%6.2f" % cor + "\n"
    text += "晴雨准确率:" + "%6.2f" % pc_sun_rain + "\n\n"

    clevs_name = ["0"]
    for g0 in range(len(grade_list)-1):
        if grade_list[g0] == math.floor(grade_list[g0]):
            gs0 = str(int(grade_list[g0]))
        else:
            gs0 = '%.1f' % (grade_list[g0])

        clevs_name.append(">="+ gs0)

    leves_name = []
    for name in clevs_name[1:]:
        for nn in range(10-len(name)):
            name = name+"-"
        leves_name.append(name)

    #leves_name = ["0.1-10-", "10-25--", "25-50--", "50-100-", "100-250", ">=250-"]
    for i in range(len(leves_name)):
        text += ":" + leves_name[i] + "------------------------\n"
        text += "正确:" + "%-4d" % hfmc[i,0] + " 空报:" + "%-4d" % hfmc[i,1] + " 漏报:" + "%-4d" % hfmc[i,2] + "\n"
        if ts[i] == IV:
            ts_str = " NULL"
        else:
            ts_str = "%5.3f" % ts[i]
        if ets[i] == IV:
            ets_str = " NULL"
        else:
            ets_str = "%5.3f" % ets[i]
        text += "TS:" + ts_str + "                  ETS:" + ets_str + "\n"
        if hit_rate[i] == IV:
            hit_rate_str = " NULL"
        else:
            hit_rate_str = "%5.3f" % hit_rate[i]
        if mis_rate[i] == IV:
            mis_rate_str = " NULL"
        else:
            mis_rate_str = "%5.3f" % mis_rate[i]
        text += "Hit rate:" + hit_rate_str + "     Miss rate: " + mis_rate_str + "\n"

        if fal_rate[i] == IV:
            fal_rate_str = " NULL"
        else:
            fal_rate_str = "%5.3f" % fal_rate[i]
        if bias[i] == IV:
            bias_str = " NULL"
        else:
            bias_str = "%5.3f" % bias[i]
        text += "False alarm ratio:" + fal_rate_str + "  Bias:" + bias_str + "\n\n"
    plt.text(0, 0.00, text, fontsize=9)

    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()

    return

def rain_24h_comprehensive_chinaland_sg(sta_ob,grd_fo,  save_path=None,show = False,dpi = 200,add_county_line = False,interp = None):
    grade_list = [0.1, 10, 25, 50, 100, 250, 1000]
    rain_comprehensive_chinaland_sg(sta_ob,grd_fo,grade_list,save_path=save_path,show=show,dpi=dpi,add_county_line=add_county_line,interp= interp)


def rain_comprehensive_chinaland_sg(sta_ob,grd_fo,grade_list, save_path=None,show = False,dpi = 200,add_county_line = False,interp = None):
    '''
    #绘制24小时降水实况与预报综合对比检验图，专为为全国区域设置的画面布局，画面更加紧凑
    :param grd_fo: 输入的网格数据，包含一个平面的网格场
    :param sta_ob:  输入的站点数据，包含一个时刻的站点数据列表
    :param filename: 图片输出路径，缺省时会以调试窗口形式弹出
    :return:无返回值
    '''
    if len(grade_list)!=7:
        print("grade_list 暂时仅支持长度为7的列表，包含小雨、中雨、大雨、暴雨、大暴雨、特大暴雨以及一个降水上限值")
        return
    grid_fo = meteva.base.get_grid_of_data(grd_fo)
    fig = plt.figure(figsize=(10, 7),dpi=dpi)
    # 平面对比图
    rect1 = [0.05, 0.43, 0.65, 0.53]  # 左下宽高
    map_area = 70 * 0.41 * 0.55
    ax = plt.axes(rect1)
    # 设置地图背景
    map_extent = [73, 135, 18, 54]
    add_china_map_2basemap(ax, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax.set_xlim((73, 135))
    ax.set_ylim((18, 54))

    # 绘制格点预报场
    x = np.arange(grid_fo.nlon) * grid_fo.dlon + grid_fo.slon
    y = np.arange(grid_fo.nlat) * grid_fo.dlat + grid_fo.slat
    clevs =grade_list
    colors_grid = ["#E0EEFA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    dat = grd_fo.values.squeeze()
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plot_grid = ax.contourf(x, y, dat, clevs, colors=colors_grid)  # 填色图

    colorbar_position_grid = fig.add_axes([0.085, 0.93, 0.25, 0.015])  # 位置[左,下,宽,高]
    plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='horizontal')
    plt.text(0.035, 0.955, "预报(mm)", fontsize=9)
    # 绘制填色站点值
    sta_ob_in = meteva.base.in_grid_xy(sta_ob, grid=grid_fo)
    colors_sta = ['#FFFFFF', '#0055FF', '#00FFB4', '#F4FF00', '#FE1B00', '#910000', '#B800BA']
    dat = sta_ob_in.values[:, -1]
    dat[dat > 1000] = 0
    clevs = [0]
    clevs.extend(grade_list)
    clevs_name = ["0"]
    for g0 in range(len(grade_list)-2):
        if grade_list[g0] == math.floor(grade_list[g0]):
            gs0 = str(int(grade_list[g0]))
        else:
            gs0 = '%.1f' % (grade_list[g0])

        if grade_list[g0+1] == math.floor(grade_list[g0+1]):
            gs1 = str(int(grade_list[g0+1]))
        else:
            gs1 = '%.0f' % (grade_list[g0+1])
        clevs_name.append(gs0+"-"+gs1)
    clevs_name.append(">="+ str(int(grade_list[len(grade_list)-2])))


    #cleves_name = ["0", "0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"]

    pointsize = int(100 * map_area / len(dat))
    if (pointsize > 30): pointsize = 30
    if (pointsize < 1): pointsize = 1

    for i in range(len(clevs) - 1):
        index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
        if (len(index0[0]) > 0):
            x = np.squeeze(sta_ob_in["lon"].values[index0])
            y = np.squeeze(sta_ob_in["lat"].values[index0])
            if (len(index0) == 1):
                x = np.array([x])
                y = np.array([y])
                if (i > 0):
                    ax.scatter(x, y, c=colors_sta[i], s=3*pointsize, label=clevs_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i],  s=pointsize, label=clevs_name[i],
                               linewidths=0.1, edgecolor="k")
    ax.legend(loc="lower left", facecolor='whitesmoke', title="观测",  edgecolor='whitesmoke',fontsize=9)

    #设置图片标题
    time_str = meteva.base.tool.time_tools.time_to_str(grid_fo.gtime[0])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
    if type(grid_fo.members[0]) == str:
        model_name = grid_fo.members[0]
    else:
        model_name = str(grid_fo.members[0])

    var_name = ""
    if sta_ob.attrs is not None:
        if "var_cn_name" in sta_ob.attrs.keys():
            var_name = sta_ob.attrs["var_cn_name"]
            if var_name=="":
                var_name = sta_ob.attrs["var_name"]
    title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效"+var_name+"预报和观测"
    ax.set_title(title)

    # 散点回归图
    rect2 = [0.07, 0.07, 0.21, 0.30]  # 左下宽高
    ax2 = plt.axes(rect2)

    if interp == "linear":
        sta_fo = meteva.base.interp_gs_linear(grd_fo, sta_ob_in)
    else:
        sta_fo = meteva.base.interp_gs_nearest(grd_fo, sta_ob_in)
    # print(sta_fo)
    data_name = meteva.base.get_stadata_names(sta_ob_in)
    ob = sta_ob_in.loc[:,data_name[0]].values
    data_name = meteva.base.get_stadata_names(sta_fo)
    fo = sta_fo.loc[:,data_name[0]].values
    ob_fo = ob + fo
    index = np.where(~np.isnan(ob_fo))
    ob = ob[index]
    fo = fo[index]
    ax2.plot(fo, ob, '.', color='k')
    maxy = max(np.max(ob), np.max(fo)) + 5

    # 绘制比例线
    rate = np.sum(fo) / (np.sum(ob) + 1e-30)
    ob_line = np.arange(0, (maxy + 1), (maxy + 1) / 30)
    fo_rate = ob_line * 1
    ax2.plot(ob_line[0:30], fo_rate[0:30], 'b', linestyle='dashed')

    # 绘制回归线
    # X = np.zeros((len(ob), 1))
    # X[:, 0] = ob[:]
    # clf = LinearRegression().fit(X, fo)
    # X = np.zeros((len(ob_line), 1))
    # X[:, 0] = ob_line[:]
    # fo_rg = clf.predict(X)
    # ax2.plot(ob_line, fo_rg, color='r')
    # cor = np.corrcoef(ob, fo)
    # rg_text1 = "R = " + '%.2f' % (cor[0, 1])
    # rg_text2 = "y = " + '%.2f' % (clf.coef_[0]) + "* x + " + '%.2f' % (clf.intercept_)

    slope, intercept, r_value, p_value, std_err = st.linregress(fo, ob)
    fo_rg = slope * ob_line + intercept
    ax2.plot(ob_line, fo_rg, color='r')
    rg_text1 = "R = " + '%.2f' % (r_value)
    if intercept >= 0:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X + " + '%.2f' % (intercept)
    else:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X - " + '%.2f' % (-intercept)

    plt.xlim(0, maxy)
    plt.ylim(0, maxy)
    plt.text(0.05 * maxy, 0.9 * maxy, rg_text1, fontsize=10)
    plt.text(0.05 * maxy, 0.8 * maxy, rg_text2, fontsize=10)
    maxy = max(np.max(ob), np.max(fo))
    ax2.set_xlabel("预报", fontsize=9)
    ax2.set_ylabel("观测", fontsize=9)
    ax2.set_title("Obs.vs Pred. Scatter plot", fontsize=12)
    # 设置次刻度间隔
    if(maxy <5):
        xmi = 0.1
        Xmi = 1
    elif(maxy <50):
        xmi = 1
        if(maxy >25):
            Xmi = 10
        else:
            Xmi = 5
    elif (maxy <100):
        xmi = 2
        if(maxy >50):
            Xmi = 20
        else:
            Xmi = 10
    elif (maxy <250):
        xmi = 5
        if(maxy >100):
            Xmi = 50
        else:
            Xmi = 20
    elif (maxy <1000):
        xmi = 20
        if(maxy >500):
            Xmi = 200
        else:
            Xmi = 100
    else:
        xmi = 50
        Xmi = 250



    xmajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将x主刻度标签设置为次刻度10倍
    ymajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将y主刻度标签设置为次刻度10倍
    ax2.xaxis.set_major_locator(xmajorLocator)
    ax2.yaxis.set_major_locator(ymajorLocator)
    xminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将x轴次刻度标签设置xmi
    yminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将y轴次刻度标签设置ymi
    ax2.xaxis.set_minor_locator(xminorLocator)
    ax2.yaxis.set_minor_locator(yminorLocator)

    # 绘制频率柱状图
    p_ob = np.zeros(6)
    p_fo = np.zeros(6)
    x = np.arange(6) + 1
    for i in range(1, len(clevs) - 1, 1):
        index0 = np.where((ob >= clevs[i]) & (ob < clevs[i + 1]))
        p_ob[i - 1] = len(index0[0])
        index0 = np.where((fo >= clevs[i]) & (fo < clevs[i + 1]))
        p_fo[i - 1] = len(index0[0])
    rect3 = [0.35, 0.07, 0.325, 0.17]  # 左下宽高
    ax3 = plt.axes(rect3)
    ax3.bar(x - 0.25, p_ob, width=0.2, facecolor="r", label="Obs")
    ax3.bar(x + 0.05, p_fo, width=0.2, facecolor="b", label="Pred")
    ax3.legend(loc="upper right")
    ax3.set_xlabel("precipitation threshold", fontsize=10)
    ax3.set_xticks(x)
    ax3.set_xticklabels(clevs_name[1:], fontsize=9)
    ax3.set_ylabel("point number", fontsize=10)
    ax3.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))

    # 绘制降水站点实况预报统计表
    rect4 = [0.35, 0.235, 0.4, 0.10]  # 左下宽高
    ax4 = plt.axes(rect4)
    ax4.axes.set_axis_off()

    ob_has = ob[ob >= grade_list[0]]
    fo_has = fo[fo >= grade_list[0]]
    mean_fo = 0
    max_fo = 0
    mean_ob = 0
    max_ob = 0
    if len(fo_has)>1:
        mean_fo = np.mean(fo_has)
        max_fo = np.max(fo_has)
    if len(ob_has)>1:
        mean_ob = np.mean(ob_has)
        max_ob = np.max(ob_has)

    text = "降水站点实况和预报 n=" + str(len(ob)) + "\n"
    text += "====================================================\n"
    text += "                              观测           预报  \n"
    text += "----------------------------------------------------\n"
    text += "有降水站点数(>="+str(grade_list[0])+")     " + "%9d" % len(ob_has) + "           %4d" % len(fo_has) + "\n"
    text += "有降水站点数百分比%    " + "%11.1f" % (100*len(ob_has) / len(ob)) + "%15.1f" % (100*len(fo_has) / len(fo)) + "\n"
    text += "平均降水量(排除无降水) " + "%11.1f" % (mean_ob) + "%15.1f" % (mean_fo) + "\n"
    text += "最大降水量             " + "%11.1f" % (max_ob) + "%15.1f" % (max_fo)+"\n"
    text += "----------------------------------------------------"
    plt.text(0, 0, text, fontsize=9)


    # 绘制统计检验结果
    rect5 = [0.71, 0.00, 0.28, 0.85]  # 左下宽高
    ax5 = plt.axes(rect5)
    ax5.axes.set_axis_off()

    mae = meteva.method.continuous.score.mae(ob, fo)
    me = meteva.method.continuous.score.me(ob, fo)
    mse = meteva.method.continuous.score.mse(ob, fo)
    rmse = meteva.method.continuous.score.rmse(ob, fo)
    bias_c = meteva.method.continuous.score.bias_m(ob, fo)
    cor = meteva.method.continuous.score.corr(ob, fo)
    pc_sun_rain = meteva.method.pc_of_sun_rain(ob, fo)
    hfmc = meteva.method.yes_or_no.score.hfmc(ob, fo, clevs[1:])
    ts = meteva.method.yes_or_no.score.ts(ob, fo, clevs[1:])
    ets = meteva.method.yes_or_no.score.ets(ob, fo, clevs[1:])
    bias = meteva.method.yes_or_no.score.bias(ob, fo, clevs[1:])
    hit_rate = meteva.method.yes_or_no.score.pod(ob, fo, clevs[1:])
    mis_rate = meteva.method.yes_or_no.score.mr(ob, fo, clevs[1:])
    fal_rate = meteva.method.yes_or_no.score.far(ob, fo, clevs[1:])
    text = str(len(ob)) + "评分站点预报检验统计量\n\n"
    text += "Mean absolute error:" + "%6.2f" % mae + "\n"
    text += "Mean error:" + "%6.2f" % me + "\n"
    text += "Mean-squared error:" + "%6.2f" % mse + "\n"
    text += "Root mean-squared error:" + "%6.2f" % rmse + "\n"
    text += "Bias:" + "%6.2f" % bias_c + "\n"
    text += "Correlation ceoefficient:" + "%6.2f" % cor + "\n"
    text += "晴雨准确率:" + "%6.2f" % pc_sun_rain + "\n\n"


    #leves_name = ["0.1-10-", "10-25--", "25-50--", "50-100-", "100-250", ">=250-"]

    clevs_name = ["0"]
    for g0 in range(len(grade_list)-1):
        if grade_list[g0] == math.floor(grade_list[g0]):
            gs0 = str(int(grade_list[g0]))
        else:
            gs0 = '%.1f' % (grade_list[g0])

        clevs_name.append(">="+ gs0)
    leves_name = []
    for name in clevs_name[1:]:
        for nn in range(10-len(name)):
            name = name+"-"
        leves_name.append(name)

    for i in range(len(leves_name)):
        text += ":" + leves_name[i] + "------------------------\n"
        text += "正确:" + "%-4d" % hfmc[i, 0] + " 空报:" + "%-4d" % hfmc[i, 1] + " 漏报:" + "%-4d" % hfmc[i, 2] + "\n"
        if ts[i] == IV:
            ts_str = " NULL"
        else:
            ts_str = "%5.3f" % ts[i]
        if ets[i] == IV:
            ets_str = " NULL"
        else:
            ets_str = "%5.3f" % ets[i]
        text += "TS:" + ts_str + "                  ETS:" + ets_str + "\n"
        if hit_rate[i] == IV:
            hit_rate_str = " NULL"
        else:
            hit_rate_str = "%5.3f" % hit_rate[i]
        if mis_rate[i] == IV:
            mis_rate_str = " NULL"
        else:
            mis_rate_str = "%5.3f" % mis_rate[i]
        text += "Hit rate:" + hit_rate_str + "     Miss rate: " + mis_rate_str + "\n"

        if fal_rate[i] == IV:
            fal_rate_str = " NULL"
        else:
            fal_rate_str = "%5.3f" % fal_rate[i]
        if bias[i] == IV:
            bias_str = " NULL"
        else:
            bias_str = "%5.3f" % bias[i]
        text += "False alarm ratio:" + fal_rate_str + "  Bias:" + bias_str + "\n\n"
    plt.text(0, 0.00, text, fontsize=10.3)

    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()
    return

def rain_comprehensive_sl(sta_ob,m14,map_extend,grade_list,save_path=None,show = False,dpi = 200,add_county_line = False,point_size = None,fontsize = None):

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
    sta_ob_in = meteva.base.sele_by_para(sta_ob, lon = [slon,elon],lat = [slat,elat])
    # 通过经纬度范围设置画幅
    hight = 5.6
    title_hight = 0.3
    legend_hight = 0.6
    left_plots_width = 3
    right_plots_width = 2.3
    width = (hight - title_hight - legend_hight) * rlon / rlat + left_plots_width + right_plots_width
    map_width = width - left_plots_width - right_plots_width
    map_area = (hight - title_hight - legend_hight) * map_width

    fig = plt.figure(figsize=(width, hight),dpi=dpi)
    # 设置画幅的布局方式，
    rect1 = [left_plots_width / width, 0.12, (width - right_plots_width - left_plots_width) / width, 0.84]  # 左下宽高,中央对比图
    ylabelwidth = 0.52 / width
    rect2 = [ylabelwidth, 0.08, left_plots_width / width - ylabelwidth - 0.005, 0.40]  # 左下宽高，散点回归图
    ylabelwidth = 0.65 / width
    rect3 = [ylabelwidth, 0.60, left_plots_width / width - ylabelwidth - 0.005, 0.18]  # 左下宽高，频谱统计柱状图
    rect4 = [0.01, 0.79, left_plots_width / width - 0.045, 0.15]  # 左下宽高，左侧文字
    rect5 = [(width - right_plots_width) / width + 0.005, -0.035, right_plots_width / width - 0.01, 0.90]  # 左下宽高，右侧文字
    width_ob_fo_str = 0.3
    if (map_width < 3.5):
        width_bar = 2.1  # 根据中间地图的宽度，来确定预报colorbar的尺寸
        sta_legend_size = 5  # 根据中间地图的宽度，来确定观测legend的size
    else:
        sta_legend_size = 7
        width_bar = 2.9

    rect6 = [(left_plots_width + 0.5 * map_width - 0.5 * width_bar + 0.5 * width_ob_fo_str) / width, 0.04,
             width_bar / width, 0.02]  # 预报colorbar
    rect7 = [(left_plots_width + 0.5 * map_width - 0.5 * width_bar - 0.5 * width_ob_fo_str) / width, 0.04,
             width_ob_fo_str / width, 0.3]  # 观测文字
    # rect8 = [left_plots_width / width, 0.04, width_ob_fo_str / width, 0.3]  # 预报文字

    ax = plt.axes(rect1)
    # 设置地图背景
    add_china_map_2basemap(ax, name='province', edgecolor='k', lw=0.3, encoding='gbk')  # "省界"
    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "省界"
    ax.set_xlim((slon, elon))
    ax.set_ylim((slat, elat))

    # 绘制预报场
    clevs =grade_list
    colors_grid = ["#E0EEFA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    #grade_list = [0,10,25,50,100,250]
    contours = m14["closed_contours"]
    ncontour = len(contours["cn_label"])
    ploys_dict = {}

    for g in range(len(grade_list)):
        grade = grade_list[g]
        ploys_dict[g] = []
        for n in range(ncontour):
            if float(contours["cn_label"][n]) == grade or (int(float(contours["cn_label"][n])) ==0 and g ==0):
                # line = contours["cn_xyz"][n][:,0:2]
                # poly = Polygon(line,facecolor = colors_grid[g],edgecolor="k",linewidth=0.5)
                # poly.set_zorder(0)
                # ax.add_patch(poly)
                # ploys_dict[g].append(line)
                line_array = contours["cn_xyz"][n][:, 0:2]
                poly = Polygon(line_array, facecolor=colors_grid[g], edgecolor="k", linewidth=0.5)
                poly.set_zorder(0)
                ax.add_patch(poly)
                ploys_dict[g].append(line_array)
                value = contours["cn_label"][n]
                i_s = -1
                line_dict = None

                while i_s < line_array.shape[0] - 1:
                    i_s += 1
                    x = line_array[i_s, 0]
                    y = line_array[i_s, 1]
                    if x >= slon and x <= elon and y >= slat and y <= elat:
                        if i_s == 0:
                            x_1 = line_array[1, 0]
                            y_1 = line_array[1, 1]
                            if x_1 == x:
                                rotation = 90
                            else:
                                rotation = math.atan((y_1 - y) / (x_1 - x)) * 180 / math.pi
                            ax.text(x, y, value, ha="center", va="center", fontsize=fontsize, color="k",
                                    rotation=rotation, bbox={"facecolor": "w", "pad": 0, "linewidth": 0})
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
                            npoint = len(line_dict["x"])
                            if npoint > 5:
                                np_half = int(npoint / 2)
                                x = line_dict["x"][np_half]
                                y = line_dict["y"][np_half]
                                x_1 = line_dict["x"][np_half + 1]
                                y_1 = line_dict["y"][np_half + 1]
                                if x_1 == x:
                                    rotation = 90
                                else:
                                    rotation = math.atan((y_1 - y) / (x_1 - x)) * 180 / math.pi
                                ax.text(x, y, value, ha="center", va="center", fontsize=fontsize, color="k",
                                        rotation=rotation, bbox={"facecolor": "w", "pad": 0, "linewidth": 0})
                                line_dict = None


    # 绘制填色站点值

    colors_sta = ['#FFFFFF', '#0055FF', '#00FFB4', '#F4FF00', '#FE1B00', '#910000', '#B800BA']
    dat = sta_ob_in.values[:, -1]
    dat[dat > 1000] = 0
    clevs = [0]
    clevs.extend(grade_list)
    clevs_name = ["0"]
    for g0 in range(len(grade_list)-2):
        if grade_list[g0] == math.floor(grade_list[g0]):
            gs0 = str(int(grade_list[g0]))
        else:
            gs0 = '%.1f' % (grade_list[g0])

        if grade_list[g0+1] == math.floor(grade_list[g0+1]):
            gs1 = str(int(grade_list[g0+1]))
        else:
            gs1 = '%.0f' % (grade_list[g0+1])
        clevs_name.append(gs0+"-"+gs1)
    clevs_name.append(">="+ str(int(grade_list[len(grade_list)-2])))


    #cleves_name = ["0", "0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"]
    if point_size is None:
        pointsize = int(100 * map_area / len(dat))
        if (pointsize > 30): pointsize = 30
        if (pointsize < 1): pointsize = 1
    else:
        pointsize = point_size

    for i in range(len(clevs) - 1):
        index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
        if (len(index0[0]) > 0):
            x = np.squeeze(sta_ob_in["lon"].values[index0])
            y = np.squeeze(sta_ob_in["lat"].values[index0])
            if (len(index0) == 1):
                x = np.array([x])
                y = np.array([y])
                if (i > 0):
                    ax.scatter(x, y, c=colors_sta[i], s=3*pointsize, label=clevs_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i],  s=pointsize, label=clevs_name[i],
                               linewidths=0.1, edgecolor="k")
    ax.legend(loc="lower left", facecolor='whitesmoke', title="观测",  edgecolor='whitesmoke',fontsize=9)

    #设置图片标题
    time_str = meteva.base.tool.time_tools.time_to_str(m14["time"])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"


    var_name = ""
    if sta_ob.attrs is not None:
        if "var_cn_name" in sta_ob.attrs.keys():
            var_name = sta_ob.attrs["var_cn_name"]
            if var_name=="":
                var_name = sta_ob.attrs["var_name"]
    title = " " + dati_str + "起报" + str(m14["dtime"]) + "H时效"+var_name+str(m14["data_name"]) +"预报和观测"
    ax.set_title(title)

    ax7 = plt.axes(rect7)
    ax7.axes.set_axis_off()
    plt.text(0, 0.00, "观测\n\n预报", fontsize=7)

    # ax.legend(loc="lower right", ncol=4, facecolor='whitesmoke', title="观测", edgecolor='whitesmoke', fontsize=9,
    #          bbox_to_anchor=(0, -0.32))
    # 散点回归图
    ax2 = plt.axes(rect2)
    sta_fo = sta_ob_in.copy()  #  meteva.base.interp_gs_nearest(grd_fo, sta_ob_in)

    nsta = len(sta_fo.index)

    grade_list1 = [0]
    grade_list1.extend(grade_list)
    for i in range(nsta):
        point1 = [sta_fo.iloc[i,4],sta_fo.iloc[i,5]]
        gg = 0
        for g in range(len(grade_list)):
            ploys = ploys_dict[g]
            inploy = meteva.base.tool.math_tools.isPoiWithinPoly(point1,ploys)
            if not inploy:
                break
            else:
                gg = g + 1
        sta_fo.iloc[i, -1] = grade_list1[gg]
    # print(sta_fo)
    data_name = meteva.base.get_stadata_names(sta_ob_in)
    ob = sta_ob_in[data_name[0]].values
    data_name = meteva.base.get_stadata_names(sta_fo)
    fo = sta_fo[data_name[0]].values
    ob_fo = ob + fo
    index = np.where(~np.isnan(ob_fo))
    ob = ob[index]
    fo = fo[index]
    ax2.plot(fo, ob, '.', color='k')
    maxy = max(np.max(ob), np.max(fo)) + 5

    # 绘制比例线
    rate = np.sum(fo) / (np.sum(ob) + 1e-30)
    ob_line = np.arange(0, (maxy + 1), (maxy + 1) / 30)
    fo_rate = ob_line * 1
    ax2.plot(ob_line[0:30], fo_rate[0:30], 'b', linestyle='dashed')

    # 绘制回归线
    # X = np.zeros((len(ob), 1))
    # X[:, 0] = ob[:]
    # clf = LinearRegression().fit(X, fo)
    # X = np.zeros((len(ob_line), 1))
    # X[:, 0] = ob_line[:]
    # fo_rg = clf.predict(X)
    # ax2.plot(ob_line, fo_rg, color='r')
    # cor = np.corrcoef(ob, fo)
    # rg_text1 = "R = " + '%.2f' % (cor[0, 1])
    # rg_text2 = "y = " + '%.2f' % (clf.coef_[0]) + "* x + " + '%.2f' % (clf.intercept_)
    slope, intercept, r_value, p_value, std_err = st.linregress(fo, ob)
    fo_rg = slope * ob_line + intercept
    ax2.plot(ob_line, fo_rg, color='r')
    rg_text1 = "R = " + '%.2f' % (r_value)
    if intercept >= 0:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X + " + '%.2f' % (intercept)
    else:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X - " + '%.2f' % (-intercept)

    plt.xlim(0, maxy)
    plt.ylim(0, maxy)
    plt.text(0.05 * maxy, 0.9 * maxy, rg_text1, fontsize=10)
    plt.text(0.05 * maxy, 0.8 * maxy, rg_text2, fontsize=10)
    maxy = max(np.max(ob), np.max(fo))
    ax2.set_xlabel("预报", fontsize=9)
    ax2.set_ylabel("观测", fontsize=9)
    ax2.set_title("Obs.vs Pred. Scatter plot", fontsize=12)
    # 设置次刻度间隔

    # 设置次刻度间隔
    if (maxy < 5):
        xmi = 0.1
        Xmi = 1
    elif (maxy < 50):
        xmi = 1
        if (maxy > 25):
            Xmi = 10
        else:
            Xmi = 5
    elif (maxy < 100):
        xmi = 2
        if (maxy > 50):
            Xmi = 20
        else:
            Xmi = 10
    elif (maxy < 250):
        xmi = 5
        if (maxy > 100):
            Xmi = 50
        else:
            Xmi = 20
    elif (maxy < 1000):
        xmi = 20
        if (maxy > 500):
            Xmi = 200
        else:
            Xmi = 100
    else:
        xmi = 50
        Xmi = 250
    xmajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将x主刻度标签设置为次刻度10倍
    ymajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将y主刻度标签设置为次刻度10倍
    ax2.xaxis.set_major_locator(xmajorLocator)
    ax2.yaxis.set_major_locator(ymajorLocator)
    xminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将x轴次刻度标签设置xmi
    yminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将y轴次刻度标签设置ymi
    ax2.xaxis.set_minor_locator(xminorLocator)
    ax2.yaxis.set_minor_locator(yminorLocator)

    # 绘制频率柱状图
    p_ob = np.zeros(len(grade_list) - 1)
    p_fo = np.zeros(len(grade_list) - 1)
    x = np.arange(len(grade_list) - 1) + 1
    for i in range(1, len(clevs) - 1, 1):
        index0 = np.where((ob >= clevs[i]) & (ob < clevs[i + 1]))
        p_ob[i - 1] = len(index0[0])
        index0 = np.where((fo >= clevs[i]) & (fo < clevs[i + 1]))
        p_fo[i - 1] = len(index0[0])

    ax3 = plt.axes(rect3)
    ax3.bar(x - 0.25, p_ob, width=0.2, facecolor="r", label="Obs")
    ax3.bar(x + 0.05, p_fo, width=0.2, facecolor="b", label="Pred")
    ax3.legend(loc="upper right")
    ax3.set_xlabel("precipitation threshold", fontsize=10)
    ax3.set_xticks(x)

    ax3.set_xticklabels(clevs_name[1:], fontsize=9)
    ax3.set_ylabel("point number", fontsize=10)
    ax3.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))

    # 绘制降水站点实况预报统计表

    ax4 = plt.axes(rect4)
    ax4.axes.set_axis_off()

    ob_has = ob[ob >= grade_list[0]]
    fo_has = fo[fo >= grade_list[0]]
    mean_fo = 0
    max_fo = 0
    mean_ob = 0
    max_ob = 0
    if len(fo_has) > 1:
        mean_fo = np.mean(fo_has)
        max_fo = np.max(fo_has)
    if len(ob_has) > 1:
        mean_ob = np.mean(ob_has)
        max_ob = np.max(ob_has)

    text = "降水站点实况和预报 n=" + str(len(ob)) + "\n"
    text += "=============================================\n"
    text += "                         观测           预报\n"
    text += "---------------------------------------------\n"
    text += "有降水站点数(>=" + str(grade_list[0]) + ")     " + "%4d" % len(ob_has) + "           %4d" % len(fo_has) + "\n"
    text += "有降水站点数百分比%    " + "%6.1f" % (100 * len(ob_has) / len(ob)) + "%15.1f" % (100 * len(fo_has) / len(fo)) + "\n"
    text += "平均降水量(排除无降水) " + "%6.1f" % (mean_ob) + "%15.1f" % (mean_fo) + "\n"
    text += "最大降水量             " + "%6.1f" % (max_ob) + "%15.1f" % (max_fo) + "\n"
    text += "---------------------------------------------"
    plt.text(0, 0, text, fontsize=9)

    # 绘制统计检验结果

    ax5 = plt.axes(rect5)
    ax5.axes.set_axis_off()

    mae = meteva.method.continuous.score.mae(ob, fo)
    me = meteva.method.continuous.score.me(ob, fo)
    mse = meteva.method.continuous.score.mse(ob, fo)
    rmse = meteva.method.continuous.score.rmse(ob, fo)
    bias_c = meteva.method.continuous.score.bias_m(ob, fo)
    cor = meteva.method.continuous.score.corr(ob, fo)
    pc_sun_rain = meteva.method.pc_of_sun_rain(ob, fo)
    hfmc = meteva.method.yes_or_no.score.hfmc(ob, fo, clevs[1:])
    ts = meteva.method.yes_or_no.score.ts(ob, fo, clevs[1:])
    ets = meteva.method.yes_or_no.score.ets(ob, fo, clevs[1:])
    bias = meteva.method.yes_or_no.score.bias(ob, fo, clevs[1:])
    hit_rate = meteva.method.yes_or_no.score.pod(ob, fo, clevs[1:])
    mis_rate = meteva.method.yes_or_no.score.mr(ob, fo, clevs[1:])
    fal_rate = meteva.method.yes_or_no.score.far(ob, fo, clevs[1:])

    text = str(len(ob)) + "评分站点预报检验统计量\n"
    text += "Mean absolute error:" + "%6.2f" % mae + "\n"
    text += "Mean error:" + "%6.2f" % me + "\n"
    text += "Mean-squared error:" + "%6.2f" % mse + "\n"
    text += "Root mean-squared error:" + "%6.2f" % rmse + "\n"
    text += "Bias:" + "%6.2f" % bias_c + "\n"
    text += "Correlation ceoefficient:" + "%6.2f" % cor + "\n"
    text += "晴雨准确率:" + "%6.2f" % pc_sun_rain + "\n\n"

    clevs_name = ["0"]
    for g0 in range(len(grade_list) - 1):
        if grade_list[g0] == math.floor(grade_list[g0]):
            gs0 = str(int(grade_list[g0]))
        else:
            gs0 = '%.1f' % (grade_list[g0])

        clevs_name.append(">=" + gs0)

    leves_name = []
    for name in clevs_name[1:]:
        for nn in range(10 - len(name)):
            name = name + "-"
        leves_name.append(name)

    # leves_name = ["0.1-10-", "10-25--", "25-50--", "50-100-", "100-250", ">=250-"]
    for i in range(len(leves_name)):
        text += ":" + leves_name[i] + "------------------------\n"
        text += "正确:" + "%-4d" % hfmc[i, 0] + " 空报:" + "%-4d" % hfmc[i, 1] + " 漏报:" + "%-4d" % hfmc[i, 2] + "\n"
        if ts[i] == IV:
            ts_str = " NULL"
        else:
            ts_str = "%5.3f" % ts[i]
        if ets[i] == IV:
            ets_str = " NULL"
        else:
            ets_str = "%5.3f" % ets[i]
        text += "TS:" + ts_str + "                  ETS:" + ets_str + "\n"
        if hit_rate[i] == IV:
            hit_rate_str = " NULL"
        else:
            hit_rate_str = "%5.3f" % hit_rate[i]
        if mis_rate[i] == IV:
            mis_rate_str = " NULL"
        else:
            mis_rate_str = "%5.3f" % mis_rate[i]
        text += "Hit rate:" + hit_rate_str + "     Miss rate: " + mis_rate_str + "\n"

        if fal_rate[i] == IV:
            fal_rate_str = " NULL"
        else:
            fal_rate_str = "%5.3f" % fal_rate[i]
        if bias[i] == IV:
            bias_str = " NULL"
        else:
            bias_str = "%5.3f" % bias[i]
        text += "False alarm ratio:" + fal_rate_str + "  Bias:" + bias_str + "\n\n"
    plt.text(0, 0.00, text, fontsize=9)

    # 图片显示或保存
    if (save_path is not None):
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()




def rain_comprehensive_chinaland_sl(sta_ob,m14,grade_list, save_path=None,show = False,dpi = 200,add_county_line = False,point_size = None,fontsize = None):
    '''
    #绘制24小时降水实况与预报综合对比检验图，专为为全国区域设置的画面布局，画面更加紧凑
    :param grd_fo: 输入的网格数据，包含一个平面的网格场
    :param sta_ob:  输入的站点数据，包含一个时刻的站点数据列表
    :param filename: 图片输出路径，缺省时会以调试窗口形式弹出
    :return:无返回值
    '''
    if len(grade_list)!=7:
        print("grade_list 暂时仅支持长度为7的列表，包含小雨、中雨、大雨、暴雨、大暴雨、特大暴雨以及一个降水上限值")
        return

    fig = plt.figure(figsize=(10, 7),dpi=dpi)
    # 平面对比图
    rect1 = [0.05, 0.43, 0.65, 0.53]  # 左下宽高
    grid_fo = meteva.base.grid([73,135,0.05],[18,54,0.05])

    map_area = 70 * 0.41 * 0.55
    ax = plt.axes(rect1)
    # 设置地图背景
    map_extent = [73, 135, 18, 54]
    add_china_map_2basemap(ax, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax.set_xlim((73, 135))
    ax.set_ylim((18, 54))

    # 绘制预报场
    clevs =grade_list
    colors_grid = ["#E0EEFA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'

    #grade_list = [0,10,25,50,100,250]
    contours = m14["closed_contours"]
    ncontour = len(contours["cn_label"])
    ploys_dict = {}


    for g in range(len(grade_list)):
        grade = grade_list[g]
        ploys_dict[g] = []
        for n in range(ncontour):
            if float(contours["cn_label"][n]) == grade or (int(float(contours["cn_label"][n])) ==0 and g ==0):
                line_array = contours["cn_xyz"][n][:,0:2]
                poly = Polygon(line_array,facecolor = colors_grid[g],edgecolor="k",linewidth=0.5)
                poly.set_zorder(0)
                ax.add_patch(poly)
                ploys_dict[g].append(line_array)
                value = contours["cn_label"][n]
                i_s = -1
                line_dict = None

                while i_s < line_array.shape[0] - 1:
                    i_s += 1
                    x = line_array[i_s, 0]
                    y = line_array[i_s, 1]
                    if x >= grid_fo.slon and x <= grid_fo.elon and y >= grid_fo.slat and y <= grid_fo.elat:
                        if i_s == 0:
                            x_1 = line_array[1, 0]
                            y_1 = line_array[1, 1]
                            if x_1 == x:
                                rotation = 90
                            else:
                                rotation = math.atan((y_1 - y) / (x_1 - x)) * 180 / math.pi
                            ax.text(x, y, value, ha="center", va="center", fontsize=fontsize, color="k",
                                    rotation=rotation, bbox={"facecolor": "w", "pad": 0, "linewidth": 0})
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
                            npoint = len(line_dict["x"])
                            if npoint > 5:
                                np_half = int(npoint / 2)
                                x = line_dict["x"][np_half]
                                y = line_dict["y"][np_half]
                                x_1 = line_dict["x"][np_half + 1]
                                y_1 = line_dict["y"][np_half + 1]
                                if x_1 == x:
                                    rotation = 90
                                else:
                                    rotation = math.atan((y_1 - y) / (x_1 - x)) * 180 / math.pi
                                ax.text(x, y, value, ha="center", va="center", fontsize=fontsize, color="k",
                                        rotation=rotation, bbox={"facecolor": "w", "pad": 0, "linewidth": 0})
                                line_dict = None




    #colorbar_position_grid = fig.add_axes([0.085, 0.93, 0.25, 0.015])  # 位置[左,下,宽,高]
    #plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='horizontal')
    #plt.text(0.035, 0.955, "预报(mm)", fontsize=9)
    # 绘制填色站点值
    sta_ob_in = meteva.base.in_grid_xy(sta_ob, grid=grid_fo)
    colors_sta = ['#FFFFFF', '#0055FF', '#00FFB4', '#F4FF00', '#FE1B00', '#910000', '#B800BA']
    dat = sta_ob_in.values[:, -1]
    dat[dat > 1000] = 0
    clevs = [0]
    clevs.extend(grade_list)
    clevs_name = ["0"]
    for g0 in range(len(grade_list)-2):
        if grade_list[g0] == math.floor(grade_list[g0]):
            gs0 = str(int(grade_list[g0]))
        else:
            gs0 = '%.1f' % (grade_list[g0])

        if grade_list[g0+1] == math.floor(grade_list[g0+1]):
            gs1 = str(int(grade_list[g0+1]))
        else:
            gs1 = '%.0f' % (grade_list[g0+1])
        clevs_name.append(gs0+"-"+gs1)
    clevs_name.append(">="+ str(int(grade_list[len(grade_list)-2])))


    #cleves_name = ["0", "0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"]
    if point_size is None:
        pointsize = int(100 * map_area / len(dat))
        if (pointsize > 30): pointsize = 30
        if (pointsize < 1): pointsize = 1
    else:
        pointsize = point_size

    for i in range(len(clevs) - 1):
        index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
        if (len(index0[0]) > 0):
            x = np.squeeze(sta_ob_in["lon"].values[index0])
            y = np.squeeze(sta_ob_in["lat"].values[index0])
            if (len(index0) == 1):
                x = np.array([x])
                y = np.array([y])
                if (i > 0):
                    ax.scatter(x, y, c=colors_sta[i], s=3*pointsize, label=clevs_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i],  s=pointsize, label=clevs_name[i],
                               linewidths=0.1, edgecolor="k",)
    ax.legend(loc="lower left", facecolor='whitesmoke', title="观测",  edgecolor='whitesmoke',fontsize=9)

    #设置图片标题
    time_str = meteva.base.tool.time_tools.time_to_str(m14["time"])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"


    var_name = ""
    if sta_ob.attrs is not None:
        if "var_cn_name" in sta_ob.attrs.keys():
            var_name = sta_ob.attrs["var_cn_name"]
            if var_name=="":
                var_name = sta_ob.attrs["var_name"]
    title = " " + dati_str + "起报" + str(m14["dtime"]) + "H时效"+var_name+str(m14["data_name"]) +"预报和观测"
    ax.set_title(title)

    # 散点回归图
    rect2 = [0.07, 0.07, 0.21, 0.30]  # 左下宽高
    ax2 = plt.axes(rect2)
    sta_fo = sta_ob_in.copy()  #  meteva.base.interp_gs_nearest(grd_fo, sta_ob_in)

    nsta = len(sta_fo.index)

    grade_list1 = [0]
    grade_list1.extend(grade_list)
    for i in range(nsta):
        point1 = [sta_fo.iloc[i,4],sta_fo.iloc[i,5]]
        gg = 0
        for g in range(len(grade_list)):
            ploys = ploys_dict[g]
            inploy = meteva.base.tool.math_tools.isPoiWithinPoly(point1,ploys)
            if not inploy:
                break
            else:
                gg = g + 1
        sta_fo.iloc[i, -1] = grade_list1[gg]


    # print(sta_fo)
    data_name = meteva.base.get_stadata_names(sta_ob_in)
    ob = sta_ob_in.loc[:,data_name[0]].values
    data_name = meteva.base.get_stadata_names(sta_fo)
    fo = sta_fo.loc[:,data_name[0]].values
    ob_fo = ob + fo
    index = np.where(~np.isnan(ob_fo))
    ob = ob[index]
    fo = fo[index]
    ax2.plot(fo, ob, '.', color='k')
    maxy = max(np.max(ob), np.max(fo)) + 5

    # 绘制比例线
    rate = np.sum(fo) / (np.sum(ob) + 1e-30)
    ob_line = np.arange(0, (maxy + 1), (maxy + 1) / 30)
    fo_rate = ob_line * 1
    ax2.plot(ob_line[0:30], fo_rate[0:30], 'b', linestyle='dashed')

    # 绘制回归线
    # X = np.zeros((len(ob), 1))
    # X[:, 0] = ob[:]
    # clf = LinearRegression().fit(X, fo)
    # X = np.zeros((len(ob_line), 1))
    # X[:, 0] = ob_line[:]
    # fo_rg = clf.predict(X)
    # ax2.plot(ob_line, fo_rg, color='r')
    # cor = np.corrcoef(ob, fo)
    # rg_text1 = "R = " + '%.2f' % (cor[0, 1])
    # rg_text2 = "y = " + '%.2f' % (clf.coef_[0]) + "* x + " + '%.2f' % (clf.intercept_)
    slope, intercept, r_value, p_value, std_err = st.linregress(fo, ob)
    fo_rg = slope * ob_line + intercept
    ax2.plot(ob_line, fo_rg, color='r')
    rg_text1 = "R = " + '%.2f' % (r_value)
    if intercept >= 0:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X + " + '%.2f' % (intercept)
    else:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X - " + '%.2f' % (-intercept)

    plt.xlim(0, maxy)
    plt.ylim(0, maxy)
    plt.text(0.05 * maxy, 0.9 * maxy, rg_text1, fontsize=10)
    plt.text(0.05 * maxy, 0.8 * maxy, rg_text2, fontsize=10)
    maxy = max(np.max(ob), np.max(fo))
    ax2.set_xlabel("预报", fontsize=9)
    ax2.set_ylabel("观测", fontsize=9)
    ax2.set_title("Obs.vs Pred. Scatter plot", fontsize=12)
    # 设置次刻度间隔
    if(maxy <5):
        xmi = 0.1
        Xmi = 1
    elif(maxy <50):
        xmi = 1
        if(maxy >25):
            Xmi = 10
        else:
            Xmi = 5
    elif (maxy <100):
        xmi = 2
        if(maxy >50):
            Xmi = 20
        else:
            Xmi = 10
    elif (maxy <250):
        xmi = 5
        if(maxy >100):
            Xmi = 50
        else:
            Xmi = 20
    elif (maxy <1000):
        xmi = 20
        if(maxy >500):
            Xmi = 200
        else:
            Xmi = 100
    else:
        xmi = 50
        Xmi = 250

    xmajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将x主刻度标签设置为次刻度10倍
    ymajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将y主刻度标签设置为次刻度10倍
    ax2.xaxis.set_major_locator(xmajorLocator)
    ax2.yaxis.set_major_locator(ymajorLocator)
    xminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将x轴次刻度标签设置xmi
    yminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将y轴次刻度标签设置ymi
    ax2.xaxis.set_minor_locator(xminorLocator)
    ax2.yaxis.set_minor_locator(yminorLocator)

    # 绘制频率柱状图
    p_ob = np.zeros(6)
    p_fo = np.zeros(6)
    x = np.arange(6) + 1
    for i in range(1, len(clevs) - 1, 1):
        index0 = np.where((ob >= clevs[i]) & (ob < clevs[i + 1]))
        p_ob[i - 1] = len(index0[0])
        index0 = np.where((fo >= clevs[i]) & (fo < clevs[i + 1]))
        p_fo[i - 1] = len(index0[0])
    rect3 = [0.35, 0.07, 0.325, 0.17]  # 左下宽高
    ax3 = plt.axes(rect3)
    ax3.bar(x - 0.25, p_ob, width=0.2, facecolor="r", label="Obs")
    ax3.bar(x + 0.05, p_fo, width=0.2, facecolor="b", label="Pred")
    ax3.legend(loc="upper right")
    ax3.set_xlabel("precipitation threshold", fontsize=10)
    ax3.set_xticks(x)
    ax3.set_xticklabels(clevs_name[1:], fontsize=9)
    ax3.set_ylabel("point number", fontsize=10)
    ax3.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))

    # 绘制降水站点实况预报统计表
    rect4 = [0.35, 0.235, 0.4, 0.10]  # 左下宽高
    ax4 = plt.axes(rect4)
    ax4.axes.set_axis_off()

    ob_has = ob[ob >= 0.01]
    fo_has = fo[fo >= 0.01]
    mean_fo = 0
    max_fo = 0
    mean_ob = 0
    max_ob = 0
    if len(fo_has)>1:
        mean_fo = np.mean(fo_has)
        max_fo = np.max(fo_has)
    if len(ob_has)>1:
        mean_ob = np.mean(ob_has)
        max_ob = np.max(ob_has)

    text = "降水站点实况和预报 n=" + str(len(ob)) + "\n"
    text += "====================================================\n"
    text += "                              观测           预报  \n"
    text += "----------------------------------------------------\n"
    text += "有降水站点数(>=0.01)     " + "%9d" % len(ob_has) + "           %4d" % len(fo_has) + "\n"
    text += "有降水站点数百分比%    " + "%11.1f" % (100*len(ob_has) / len(ob)) + "%15.1f" % (100*len(fo_has) / len(fo)) + "\n"
    text += "平均降水量(排除无降水) " + "%11.1f" % (mean_ob) + "%15.1f" % (mean_fo) + "\n"
    text += "最大降水量             " + "%11.1f" % (max_ob) + "%15.1f" % (max_fo)+"\n"
    text += "----------------------------------------------------"
    plt.text(0, 0, text, fontsize=9)


    # 绘制统计检验结果
    rect5 = [0.705, 0.08, 0.28, 0.85]  # 左下宽高
    ax5 = plt.axes(rect5)
    ax5.axes.set_axis_off()

    mae = meteva.method.continuous.score.mae(ob, fo)
    me = meteva.method.continuous.score.me(ob, fo)
    mse = meteva.method.continuous.score.mse(ob, fo)
    rmse = meteva.method.continuous.score.rmse(ob, fo)
    bias_c = meteva.method.continuous.score.bias_m(ob, fo)
    cor = meteva.method.continuous.score.corr(ob, fo)
    pc_sun_rain = meteva.method.pc_of_sun_rain(ob, fo)
    hfmc = meteva.method.yes_or_no.score.hfmc(ob, fo, clevs[1:])
    ts = meteva.method.yes_or_no.score.ts(ob, fo, clevs[1:])
    ets = meteva.method.yes_or_no.score.ets(ob, fo, clevs[1:])
    bias = meteva.method.yes_or_no.score.bias(ob, fo, clevs[1:])
    hit_rate = meteva.method.yes_or_no.score.pod(ob, fo, clevs[1:])
    mis_rate = meteva.method.yes_or_no.score.mr(ob, fo, clevs[1:])
    fal_rate = meteva.method.yes_or_no.score.far(ob, fo, clevs[1:])
    text = str(len(ob)) + "评分站点预报检验统计量\n"
    text += "Mean absolute error:" + "%6.2f" % mae + "\n"
    text += "Mean error:" + "%6.2f" % me + "\n"
    text += "Mean-squared error:" + "%6.2f" % mse + "\n"
    text += "Root mean-squared error:" + "%6.2f" % rmse + "\n"
    text += "Bias:" + "%6.2f" % bias_c + "\n"
    text += "Correlation ceoefficient:" + "%6.2f" % cor + "\n"
    text += "晴雨准确率:" + "%6.2f" % pc_sun_rain + "\n\n"


    #leves_name = ["0.1-10-", "10-25--", "25-50--", "50-100-", "100-250", ">=250-"]

    clevs_name = ["0"]
    for g0 in range(len(grade_list)-1):
        if grade_list[g0] == math.floor(grade_list[g0]):
            gs0 = str(int(grade_list[g0]))
        else:
            gs0 = '%.1f' % (grade_list[g0])

        clevs_name.append(">="+ gs0)
    leves_name = []
    for name in clevs_name[1:]:
        for nn in range(10-len(name)):
            name = name+"-"
        leves_name.append(name)

    for i in range(len(leves_name)):
        text += ":" + leves_name[i] + "------------------------\n"
        text += "正确:" + "%-4d" % hfmc[i, 0] + " 空报:" + "%-4d" % hfmc[i, 1] + " 漏报:" + "%-4d" % hfmc[i, 2] + "\n"
        if ts[i] == IV:
            ts_str = " NULL"
        else:
            ts_str = "%5.3f" % ts[i]
        if ets[i] == IV:
            ets_str = " NULL"
        else:
            ets_str = "%5.3f" % ets[i]
        text += "TS:" + ts_str + "                  ETS:" + ets_str + "\n"
        if hit_rate[i] == IV:
            hit_rate_str = " NULL"
        else:
            hit_rate_str = "%5.3f" % hit_rate[i]
        if mis_rate[i] == IV:
            mis_rate_str = " NULL"
        else:
            mis_rate_str = "%5.3f" % mis_rate[i]
        text += "Hit rate:" + hit_rate_str + "     Miss rate: " + mis_rate_str + "\n"

        if fal_rate[i] == IV:
            fal_rate_str = " NULL"
        else:
            fal_rate_str = "%5.3f" % fal_rate[i]
        if bias[i] == IV:
            bias_str = " NULL"
        else:
            bias_str = "%5.3f" % bias[i]
        text += "False alarm ratio:" + fal_rate_str + "  Bias:" + bias_str + "\n\n"
    plt.text(0, 0.00, text, fontsize=10)

    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()
    return

def temper_gg(grd_ob,grd_fo,save_path = None,show = False,dpi = 200,add_county_line = False,ob_name = "实况",fo_name = "预报",grd_ob_name = None,grd_fo_name = None):


    ob_min = np.min(grd_ob.values)
    fo_min = np.min(grd_fo.values)
    ob_max = np.max(grd_ob.values)
    fo_max = np.max(grd_fo.values)

    ob_fo_max = max(ob_max,fo_max)
    ob_fo_min = min(ob_min,fo_min)

    if ob_fo_max > 120:
        cmap_temp,clevs_temp = meteva.base.tool.color_tools.clev_cmap_temper_2m_k()
    else:
        cmap_temp,clevs_temp = meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("temp")

    cmap,clevs = meteva.base.tool.color_tools.get_part_cmap_and_clevs(cmap_temp,clevs_temp,ob_fo_max,ob_fo_min)

    width = 9  #整个画面的宽度
    width_colorbar = 0.6
    height_title = 0.3
    height_veri_plot = 0.5
    #meteva.base.reset(grd_fo)
    grid0 = meteva.base.get_grid_of_data(grd_fo)
    rlat = grid0.elat - grid0.slat
    rlon = grid0.elon - grid0.slon

    if grd_ob_name is not None:
        print("warming: 参数 grd_ob_name将废弃，请用参数ob_name替代")
        ob_name = grd_ob_name
    if grd_fo_name is not None:
        print("warming: 参数 grd_fo_name将废弃， 请用参数fo_name替代")
        fo_name = grd_fo_name

    if(rlon <= rlat * 0.5):
        #采用3*1布局
        width_map = (width - 2 * width_colorbar) / 3
        height_map = (rlat/ rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [width_colorbar/width, height_veri_plot/ height, width_map/width , height_map/height]  # 实况
        rect2 = [(1 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width ,  height_map/height] # 预报
        rect3 = [(2 * width_map +width_colorbar+0.05)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.015,height_map/height]
        error_colorbar_box = [(3 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.015,height_map/height]

    else:
        #采用1*2 + 1 布局
        width_map = (width - 2 * width_colorbar) / 1.5
        height_map = (rlat/ rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [(width_colorbar -0.03)/width, (height_veri_plot + 0.5 * height_map) / height, 0.5 * width_map/width , 0.5* height_map/height]  # 实况
        rect2 = [(width_colorbar -0.03)/width, height_veri_plot / height, 0.5 * width_map/width , 0.5* height_map/height] # 预报
        rect3 = [(0.5 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.01,height_map/height]
        error_colorbar_box = [(1.5 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.01,height_map/height]

    rect4 = [0.05, 0.06, 0.26, height_veri_plot / height-0.1]  # 散点回归图，左下宽高
    rect5 = [0.38, 0.06, 0.28, height_veri_plot / height-0.1]  # 频率柱状图， 左下宽高
    rect6 = [0.67, 0.01, 0.3, height_veri_plot / height-0.03]  # 左下宽高
    rect_title = [ width_colorbar/width,(height_veri_plot+ height_map)/height,1-2*width_colorbar/width, 0.001]

    fig = plt.figure(figsize=(width, height),dpi=dpi)
    # 平面对比图1




    # 设置地图背景
    ax1 = plt.axes(rect1)
    add_china_map_2basemap(ax1, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax1, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax1.set_xlim((grid0.slon, grid0.elon))
    ax1.set_ylim((grid0.slat, grid0.elat))



    # 绘制格点预报场
    x = np.arange(grid0.nlon) * grid0.dlon + grid0.slon
    y = np.arange(grid0.nlat) * grid0.dlat + grid0.slat
    #clevs = [-10,0,15,20,22,24,26,28,30,32,34,35]
    #colors_grid = ["#00AAAA","#009500","#808000", "#BFBF00","#FFFF00","#FFD400","#FFAA00","#FF7F00","#FF0000","#FF002A","#FF0055","#FF0055"]
    error = grd_fo.values.squeeze() - grd_ob.values.squeeze()
    plt.xticks([])
    plt.yticks([])
    plot_grid = ax1.contourf(x, y, grd_ob.values.squeeze(), levels=clevs, cmap=cmap)  # 填色图
    ax1.set_title(ob_name,fontsize=18,loc="left",y = 0.0)
    colorbar_position_grid = fig.add_axes(ob_fo_colorbar_box)  # 位置[左,下,宽,高]
    plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='vertical')
    #plt.title("温度(℃)", fontsize=8,verticalalignment='bottom')

    ax2 = plt.axes(rect2)
    add_china_map_2basemap(ax2, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax2, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax2.set_xlim((grid0.slon, grid0.elon))
    ax2.set_ylim((grid0.slat, grid0.elat))
    plt.xticks([])
    plt.yticks([])
    ax2.contourf(x, y, grd_fo.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    ax2.set_title(fo_name, fontsize=18, loc="left",y = 0.0)

    #clevs1 = [-5,-4,-3,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,3,4,5]

    ax3 = plt.axes(rect3)
    add_china_map_2basemap(ax3, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax3, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax3.set_xlim((grid0.slon, grid0.elon))
    ax3.set_ylim((grid0.slat, grid0.elat))
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    #plot_grid1 = ax3.contourf(x, y,error , clevs1,cmap = "bwr")  # 填色图
    cmap1, clevs1 = meteva.base.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temper_2m_error)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    plot_grid1 = ax3.contourf(x, y, error,    levels = clevs1, cmap = cmap1, norm = norm)  # 填色图
    colorbar_position_grid1 = fig.add_axes(error_colorbar_box)  # 位置[左,下,宽,高]
    title_error = fo_name + ' - ' + ob_name
    ax3.set_title(title_error,fontsize=18, loc="left",y = 0.0)
    plt.colorbar(plot_grid1, cax=colorbar_position_grid1, orientation='vertical')
    plt.title("误差(℃)", fontsize=8, verticalalignment='bottom')

    time_str = meteva.base.tool.time_tools.time_to_str(grid0.gtime[0])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
    if type(grid0.members[0]) == str:
        model_name = grid0.members[0]
    else:
        model_name = str(grid0.members[0])

    title = model_name + " " + dati_str + "起报" + str(grid0.dtimes[0]) + "H时效预报和实况对比及误差"
    ax_title = plt.axes(rect_title)
    ax_title.axes.set_axis_off()
    ax_title.set_title(title)


    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()

def temper_comprehensive_gg(grd_ob,grd_fo,save_path = None,show = False,dpi = 200,add_county_line = False,ob_name = "实况",fo_name = "预报",grd_ob_name = None,grd_fo_name = None):

    ob_min = np.min(grd_ob.values)
    fo_min = np.min(grd_fo.values)
    ob_max = np.max(grd_ob.values)
    fo_max = np.max(grd_fo.values)

    ob_fo_max = max(ob_max,fo_max)
    ob_fo_min = min(ob_min,fo_min)
    #clevs_temp, cmap_temp = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("temp")

    if ob_fo_max > 120:
        cmap_temp,clevs_temp= meteva.base.tool.color_tools.clev_cmap_temper_2m_k()
    else:
        cmap_temp,clevs_temp = meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("temp")

    cmap, clevs = meteva.base.tool.color_tools.get_part_cmap_and_clevs(cmap_temp,clevs_temp,ob_fo_max,ob_fo_min)

    width = 9  #整个画面的宽度
    width_colorbar = 0.6
    height_title = 0.3
    height_veri_plot = 3

    #meteva.base.reset(grd_fo)
    grid0 = meteva.base.get_grid_of_data(grd_fo)
    rlat = grid0.elat - grid0.slat
    rlon = grid0.elon - grid0.slon
    if(rlon <= rlat * 0.5):
        #采用3*1布局
        width_map = (width - 2 * width_colorbar) / 3
        height_map = (rlat/ rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [width_colorbar/width, height_veri_plot/ height, width_map/width , height_map/height]  # 实况
        rect2 = [(1 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width ,  height_map/height] # 预报
        rect3 = [(2 * width_map +width_colorbar+0.05)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.015,height_map/height]
        error_colorbar_box = [(3 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.015,height_map/height]

    else:
        #采用1*2 + 1 布局
        width_map = (width - 2 * width_colorbar) / 1.5
        height_map = (rlat/ rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [(width_colorbar -0.03)/width, (height_veri_plot + 0.5 * height_map) / height, 0.5 * width_map/width , 0.5* height_map/height]  # 实况
        rect2 = [(width_colorbar -0.03)/width, height_veri_plot / height, 0.5 * width_map/width , 0.5* height_map/height] # 预报
        rect3 = [(0.5 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.01,height_map/height]
        error_colorbar_box = [(1.5 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.01,height_map/height]

    rect4 = [0.05, 0.06, 0.26, height_veri_plot / height-0.1]  # 散点回归图，左下宽高
    rect5 = [0.38, 0.06, 0.28, height_veri_plot / height-0.1]  # 频率柱状图， 左下宽高
    rect6 = [0.67, 0.01, 0.3, height_veri_plot / height-0.03]  # 左下宽高
    rect_title = [ width_colorbar/width,(height_veri_plot+ height_map)/height,1-2*width_colorbar/width, 0.001]

    fig = plt.figure(figsize=(width, height),dpi=dpi)
    # 平面对比图1


    if grd_ob_name is not None:
        print("warming: 参数 grd_ob_name将废弃，请用参数ob_name替代")
        ob_name = grd_ob_name
    if grd_fo_name is not None:
        print("warming: 参数 grd_fo_name将废弃， 请用参数fo_name替代")
        fo_name = grd_fo_name

    # 设置地图背景

    ax1 = plt.axes(rect1)
    add_china_map_2basemap(ax1, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax1, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax1.set_xlim((grid0.slon, grid0.elon))
    ax1.set_ylim((grid0.slat, grid0.elat))


    # 绘制格点预报场
    x = np.arange(grid0.nlon) * grid0.dlon + grid0.slon
    y = np.arange(grid0.nlat) * grid0.dlat + grid0.slat
    #clevs = [-10,0,15,20,22,24,26,28,30,32,34,35]
    #colors_grid = ["#00AAAA","#009500","#808000", "#BFBF00","#FFFF00","#FFD400","#FFAA00","#FF7F00","#FF0000","#FF002A","#FF0055","#FF0055"]
    plt.xticks([])
    plt.yticks([])
    plot_grid = ax1.contourf(x, y, grd_ob.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    ax1.set_title(ob_name,fontsize=18,loc="left",y = 0.0)
    colorbar_position_grid = fig.add_axes(ob_fo_colorbar_box)  # 位置[左,下,宽,高]
    plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='vertical')
    plt.title("温度(℃)", fontsize=8,verticalalignment='bottom')

    ax2 = plt.axes(rect2)
    plt.xticks([])
    plt.yticks([])
    add_china_map_2basemap(ax2, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax2, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax2.set_xlim((grid0.slon, grid0.elon))
    ax2.set_ylim((grid0.slat, grid0.elat))
    ax2.contourf(x, y, grd_fo.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    ax2.set_title(fo_name, fontsize=18, loc="left",y = 0.0)

    clevs1 = [-5,-4,-3,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,3,4,5]
    error = grd_fo.values.squeeze() - grd_ob.values.squeeze()

    ax3 = plt.axes(rect3)
    add_china_map_2basemap(ax3, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax3, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax3.set_xlim((grid0.slon, grid0.elon))
    ax3.set_ylim((grid0.slat, grid0.elat))

    #plot_grid1 = ax3.contourf(x, y,error , clevs1,cmap = "bwr")  # 填色图
    #cmap1,clevs1 = meteva.base.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temper_error_br,vmax= np.max(np.abs(error)))
    cmap1, clevs1 = meteva.base.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temper_2m_error)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    plot_grid1 = ax3.contourf(x, y, error,    levels = clevs1, cmap = cmap1, norm = norm)  # 填色图
    colorbar_position_grid1 = fig.add_axes(error_colorbar_box)  # 位置[左,下,宽,高]
    title_error = fo_name + ' - ' + ob_name
    ax3.set_title(title_error,fontsize=18, loc="left",y = 0.0,color = "k")
    plt.colorbar(plot_grid1, cax=colorbar_position_grid1, orientation='vertical')
    plt.title("误差(℃)", fontsize=8, verticalalignment='bottom')

    time_str = meteva.base.tool.time_tools.time_to_str(grid0.gtime[0])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
    if type(grid0.members[0]) == str:
        model_name = grid0.members[0]
    else:
        model_name = str(grid0.members[0])

    title = model_name + " " + dati_str + "起报" + str(grid0.dtimes[0]) + "H时效预报和实况对比及误差"
    ax_title = plt.axes(rect_title)
    ax_title.axes.set_axis_off()
    ax_title.set_title(title)

    # 散点回归图
    ax2 = plt.axes(rect4)
    # 保证这两个值的正确性
    ob = grd_ob.values.flatten()
    fo = grd_fo.values.flatten()
    #X = np.zeros((len(fo), 1))
    #X[:, 0] = fo
    #clf = LinearRegression().fit(X, ob)
    num_max = max(np.max(ob), np.max(fo))
    num_min = min(np.min(ob), np.min(fo))
    dmm = num_max - num_min
    if (num_min != 0):
        num_min -= 0.1 * dmm
    num_max += dmm * 0.1
    dmm = num_max - num_min
    ob_line = np.arange(num_min, num_max, dmm / 30)

    #X = np.zeros((len(ob_line), 1))
    #X[:, 0] = ob_line
    #fo_rg = clf.predict(X)

    slope, intercept, r_value, p_value, std_err = st.linregress(fo, ob)
    fo_rg = slope * ob_line + intercept
    ax2.plot(ob_line, fo_rg, color='r')
    rg_text1 = "R = " + '%.2f' % (r_value)
    if intercept >= 0:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X + " + '%.2f' % (intercept)
    else:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X - " + '%.2f' % (-intercept)

    ax2.plot(fo, ob, '.', color='b',markersize=1)
    ax2.plot(ob_line, fo_rg, color="r")
    ax2.plot(ob_line, ob_line, '--', color="k")
    ax2.set_xlim(num_min, num_max)
    ax2.set_ylim(num_min, num_max)
    ax2.set_xlabel(fo_name,fontsize=10)
    ax2.set_ylabel(ob_name,fontsize=10)
    #rg_text2 = "Y = " + '%.2f' % (clf.coef_[0]) + "* X + " + '%.2f' % (clf.intercept_)
    ax2.text(num_min + 0.05 * dmm, num_min + 0.90 * dmm, rg_text2, fontsize=15, color="r")

    # 设置次刻度间隔
    xmi = 1
    if (np.max(ob) > 100): xmi = 2
    ymi = 1
    if (np.max(fo) > 100): ymi = 2
    xmajorLocator = mpl.ticker.MultipleLocator(10 * xmi)  # 将x主刻度标签设置为次刻度10倍
    ymajorLocator = mpl.ticker.MultipleLocator(10 * ymi)  # 将y主刻度标签设置为次刻度10倍
    ax2.xaxis.set_major_locator(xmajorLocator)
    ax2.yaxis.set_major_locator(ymajorLocator)
    xminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将x轴次刻度标签设置xmi
    yminorLocator = mpl.ticker.MultipleLocator(ymi)  # 将y轴次刻度标签设置ymi
    ax2.xaxis.set_minor_locator(xminorLocator)
    ax2.yaxis.set_minor_locator(yminorLocator)

    #折线图
    # 绘制频率柱状图
    p_ob = np.zeros(len(clevs)-1)
    p_fo = np.zeros(len(clevs)-1)
    x = clevs[0:-1]
    for i in range(len(clevs) - 1):
        index0 = np.where((ob >= clevs[i]) & (ob < clevs[i + 1]))
        p_ob[i] = len(index0[0])
        index0 = np.where((fo >= clevs[i]) & (fo < clevs[i + 1]))
        p_fo[i] = len(index0[0])

    ax5 = plt.axes(rect5)
    # ax5.plot(p_ob, color='r',label="Obs")
    # ax5.plot(p_fo, color='b',label="Pred")
    ax5.bar(x + 0.5, p_ob, width=0.4,color='r', label=ob_name)
    ax5.bar(x + 1.1, p_fo, width=0.4,color="b", label=fo_name)
    ax5.legend(loc="upper right")
    ax5.set_xlabel("等级", fontsize=10)
    ax5.set_ylabel("站点数", fontsize=10)
    #ax5.set_title("频率统计图", fontsize=10)
    ax5.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1000))
    maxy = max(np.max(p_fo),np.max(p_ob)) * 1.4
    ax5.set_ylim(0,maxy)

    #检验效果图
    # 绘制降水站点实况预报统计表
    ax6 = plt.axes(rect6)
    ax6.axes.set_axis_off()
    ob_mean = np.mean(grd_ob.values)
    fo_mean = np.mean(grd_fo.values)


    maee = meteva.method.continuous.score.mae(ob, fo)
    mee = meteva.method.continuous.score.me(ob, fo)
    msee = meteva.method.continuous.score.mse(ob, fo)
    rmsee = meteva.method.continuous.score.rmse(ob, fo)
    bias_ce = meteva.method.continuous.score.bias_m(ob, fo)
    cor = meteva.method.continuous.score.corr(ob,fo)


    text = "格点检验统计量 n=" + str(len(ob)) + "\n"
    text += "==============================================\n"
    text += "                     实况               预报   \n"
    text += "----------------------------------------------\n"
    text += "平均温度         " + "%8.2f" % (ob_mean) + "%20.2f" % (fo_mean) + "\n\n"
    text += "温度范围    " + "%8.2f" % (ob_min)+ "~%6.2f" % (ob_max) +"%12.2f" % (fo_min)+ "~%6.2f" % (fo_max) + "\n\n"
    text += "==============================================\n\n"
    text += "Mean absolute error:" + "%6.2f" % maee + "\n\n"
    text += "Mean error:" + "%6.2f" % mee + "\n\n"
    text += "Mean-squared error:" + "%6.2f" % msee + "\n\n"
    text += "Root mean-squared error:" + "%6.2f" % rmsee + "\n\n"
    text += "Bias:" + "%6.2f" % bias_ce + "\n\n"
    text += "Correlation ceoefficient:" + "%6.2f" % cor + "\n"
    plt.text(0, 0, text, fontsize=9)

    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()

def temper_comprehensive_sg(sta_ob,grd_fo,save_path = None,show = False,dpi = 200,add_county_line = False,ob_name = "观测",fo_name = "预报"):

    #meteva.base.reset(grd_fo)
    grid0 = meteva.base.get_grid_of_data(grd_fo)
    rlat = grid0.elat - grid0.slat
    rlon = grid0.elon - grid0.slon
    sta_ob1 = meteva.base.sele_by_para(sta_ob,grid=grid0)
    sta_fo1 = meteva.base.interp_gs_linear(grd_fo,sta_ob1)

    ob_min = np.min(sta_ob1.iloc[:,-1].values)
    fo_min = np.min(grd_fo.values)
    ob_max = np.max(sta_ob1.iloc[:,-1].values)
    fo_max = np.max(grd_fo.values)

    ob_fo_max = max(ob_max,fo_max)
    ob_fo_min = min(ob_min,fo_min)
    #clevs_temp, cmap_temp = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("temp")

    if ob_fo_max > 120:
        cmap_temp,clevs_temp= meteva.base.tool.color_tools.clev_cmap_temper_2m_k()
    else:
        cmap_temp,clevs_temp = meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("temp")

    cmap, clevs = meteva.base.tool.color_tools.get_part_cmap_and_clevs(cmap_temp,clevs_temp,ob_fo_max,ob_fo_min)

    width = 9  #整个画面的宽度
    width_colorbar = 0.6
    height_title = 0.3
    height_veri_plot = 3

    if(rlon <= rlat * 0.5):
        #采用3*1布局
        width_map = (width - 2 * width_colorbar) / 3
        height_map = (rlat/ rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [width_colorbar/width, height_veri_plot/ height, width_map/width , height_map/height]  # 实况
        rect2 = [(1 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width ,  height_map/height] # 预报
        rect3 = [(2 * width_map +width_colorbar+0.05)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.015,height_map/height]
        error_colorbar_box = [(3 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.015,height_map/height]

    else:
        #采用1*2 + 1 布局
        width_map = (width - 2 * width_colorbar) / 1.5
        height_map = (rlat/ rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [(width_colorbar -0.03)/width, (height_veri_plot + 0.5 * height_map) / height, 0.5 * width_map/width , 0.5* height_map/height]  # 实况
        rect2 = [(width_colorbar -0.03)/width, height_veri_plot / height, 0.5 * width_map/width , 0.5* height_map/height] # 预报
        rect3 = [(0.5 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.01,height_map/height]
        error_colorbar_box = [(1.5 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.01,height_map/height]

    rect4 = [0.05, 0.06, 0.26, height_veri_plot / height-0.1]  # 散点回归图，左下宽高
    rect5 = [0.38, 0.06, 0.28, height_veri_plot / height-0.1]  # 频率柱状图， 左下宽高
    rect6 = [0.67, 0.01, 0.3, height_veri_plot / height-0.03]  # 左下宽高
    rect_title = [ width_colorbar/width,(height_veri_plot+ height_map)/height,1-2*width_colorbar/width, 0.001]

    fig = plt.figure(figsize=(width, height),dpi=dpi)
    # 平面对比图1



    # 设置地图背景
    ax1 = plt.axes(rect1)
    add_china_map_2basemap(ax1, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax1, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax1.set_xlim((grid0.slon, grid0.elon))
    ax1.set_ylim((grid0.slat, grid0.elat))



    #clevs = [-10,0,15,20,22,24,26,28,30,32,34,35]
    #colors_grid = ["#00AAAA","#009500","#808000", "#BFBF00","#FFFF00","#FFD400","#FFAA00","#FF7F00","#FF0000","#FF002A","#FF0055","#FF0055"]
    plt.xticks([])
    plt.yticks([])

    #plot_ob = ax1.contourf(x, y, grd_ob.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    plot_ob = meteva.base.plot_tools.add_scatter(ax1,grid0,sta_ob1,cmap=meteva.base.cmaps.temp_2m,alpha=1)

    ax1.set_title(ob_name,fontsize=18,loc="left",y = 0.0)
    colorbar_position_grid = fig.add_axes(ob_fo_colorbar_box)  # 位置[左,下,宽,高]
    plt.colorbar(plot_ob, cax=colorbar_position_grid, orientation='vertical')
    plt.title("温度(℃)", fontsize=8,verticalalignment='bottom')

    ax2 = plt.axes(rect2)
    plt.xticks([])
    plt.yticks([])
    add_china_map_2basemap(ax2, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax2, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax2.set_xlim((grid0.slon, grid0.elon))
    ax2.set_ylim((grid0.slat, grid0.elat))
    # 绘制格点预报场
    x = np.arange(grid0.nlon) * grid0.dlon + grid0.slon
    y = np.arange(grid0.nlat) * grid0.dlat + grid0.slat
    ax2.contourf(x, y, grd_fo.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    ax2.set_title(fo_name, fontsize=18, loc="left",y = 0.0)


    error_sta = meteva.base.minus_on_id(sta_fo1,sta_ob1)
    #error_grd = meteva.base.interp_sg_idw_delta(error_sta,grid0,halfR=300)

    ax3 = plt.axes(rect3)
    add_china_map_2basemap(ax3, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax3, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax3.set_xlim((grid0.slon, grid0.elon))
    ax3.set_ylim((grid0.slat, grid0.elat))

    #plot_grid1 = ax3.contourf(x, y,error , clevs1,cmap = "bwr")  # 填色图
    #cmap1,clevs1 = meteva.base.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temper_error_br,vmax= np.max(np.abs(error)))
    #cmap1, clevs1 = meteva.base.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temper_2m_error)
    #norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    #plot_grid1 = ax3.contourf(x, y, error,    levels = clevs1, cmap = cmap1, norm = norm)  # 填色图
    plot_error = meteva.base.plot_tools.add_scatter(ax3,grid0,error_sta,cmap=meteva.base.cmaps.temper_2m_error,alpha=1)
    colorbar_position_grid1 = fig.add_axes(error_colorbar_box)  # 位置[左,下,宽,高]
    title_error = fo_name + ' - ' + ob_name
    ax3.set_title(title_error,fontsize=18, loc="left",y = 0.0,color = "k")
    plt.colorbar(plot_error, cax=colorbar_position_grid1, orientation='vertical')
    plt.title("误差(℃)", fontsize=8, verticalalignment='bottom')

    time_str = meteva.base.tool.time_tools.time_to_str(grid0.gtime[0])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
    if type(grid0.members[0]) == str:
        model_name = grid0.members[0]
    else:
        model_name = str(grid0.members[0])

    title = model_name + " " + dati_str + "起报" + str(grid0.dtimes[0]) + "H时效预报和实况对比及误差"
    ax_title = plt.axes(rect_title)
    ax_title.axes.set_axis_off()
    ax_title.set_title(title)

    # 散点回归图
    ax2 = plt.axes(rect4)
    # 保证这两个值的正确性
    ob = sta_ob1.iloc[:,-1].values
    fo = sta_fo1.iloc[:,-1].values
    # X = np.zeros((len(fo), 1))
    # X[:, 0] = fo
    # clf = LinearRegression().fit(X, ob)
    num_max = max(np.max(ob), np.max(fo))
    num_min = min(np.min(ob), np.min(fo))
    dmm = num_max - num_min
    if (num_min != 0):
        num_min -= 0.1 * dmm
    num_max += dmm * 0.1
    dmm = num_max - num_min
    ob_line = np.arange(num_min, num_max, dmm / 30)
    # X = np.zeros((len(ob_line), 1))
    # X[:, 0] = ob_line
    # fo_rg = clf.predict(X)

    slope, intercept, r_value, p_value, std_err = st.linregress(fo, ob)
    fo_rg = slope * ob_line + intercept
    ax2.plot(ob_line, fo_rg, color='r')
    rg_text1 = "R = " + '%.2f' % (r_value)
    if intercept >= 0:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X + " + '%.2f' % (intercept)
    else:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X - " + '%.2f' % (-intercept)

    ax2.plot(fo, ob, '.', color='b',markersize=1)
    ax2.plot(ob_line, fo_rg, color="r")
    ax2.plot(ob_line, ob_line, '--', color="k")
    ax2.set_xlim(num_min, num_max)
    ax2.set_ylim(num_min, num_max)
    ax2.set_xlabel(fo_name,fontsize=10)
    ax2.set_ylabel(ob_name,fontsize=10)
    #rg_text2 = "Y = " + '%.2f' % (clf.coef_[0]) + "* X + " + '%.2f' % (clf.intercept_)
    ax2.text(num_min + 0.05 * dmm, num_min + 0.90 * dmm, rg_text2, fontsize=15, color="r")

    # 设置次刻度间隔
    xmi = 1
    if (np.max(ob) > 100): xmi = 2
    ymi = 1
    if (np.max(fo) > 100): ymi = 2
    xmajorLocator = mpl.ticker.MultipleLocator(10 * xmi)  # 将x主刻度标签设置为次刻度10倍
    ymajorLocator = mpl.ticker.MultipleLocator(10 * ymi)  # 将y主刻度标签设置为次刻度10倍
    ax2.xaxis.set_major_locator(xmajorLocator)
    ax2.yaxis.set_major_locator(ymajorLocator)
    xminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将x轴次刻度标签设置xmi
    yminorLocator = mpl.ticker.MultipleLocator(ymi)  # 将y轴次刻度标签设置ymi
    ax2.xaxis.set_minor_locator(xminorLocator)
    ax2.yaxis.set_minor_locator(yminorLocator)

    #折线图
    # 绘制频率柱状图
    p_ob = np.zeros(len(clevs)-1)
    p_fo = np.zeros(len(clevs)-1)
    x = clevs[0:-1]
    for i in range(len(clevs) - 1):
        index0 = np.where((ob >= clevs[i]) & (ob < clevs[i + 1]))
        p_ob[i] = len(index0[0])
        index0 = np.where((fo >= clevs[i]) & (fo < clevs[i + 1]))
        p_fo[i] = len(index0[0])

    ax5 = plt.axes(rect5)
    # ax5.plot(p_ob, color='r',label="Obs")
    # ax5.plot(p_fo, color='b',label="Pred")
    ax5.bar(x + 0.5, p_ob, width=0.4,color='r', label=ob_name)
    ax5.bar(x + 1.1, p_fo, width=0.4,color="b", label=fo_name)
    ax5.legend(loc="upper right")
    ax5.set_xlabel("等级", fontsize=10)
    ax5.set_ylabel("站点数", fontsize=10)
    #ax5.set_title("频率统计图", fontsize=10)
    ax5.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1000))
    maxy = max(np.max(p_fo),np.max(p_ob)) * 1.4
    ax5.set_ylim(0,maxy)

    #检验效果图
    # 绘制降水站点实况预报统计表
    ax6 = plt.axes(rect6)
    ax6.axes.set_axis_off()
    ob_mean = np.mean(ob)
    fo_mean = np.mean(fo)


    maee = meteva.method.continuous.score.mae(ob, fo)
    mee = meteva.method.continuous.score.me(ob, fo)
    msee = meteva.method.continuous.score.mse(ob, fo)
    rmsee = meteva.method.continuous.score.rmse(ob, fo)
    bias_ce = meteva.method.continuous.score.bias_m(ob, fo)
    cor = meteva.method.continuous.score.corr(ob,fo)


    text = "格点检验统计量 n=" + str(len(ob)) + "\n"
    text += "==============================================\n"
    text += "                     实况               预报   \n"
    text += "----------------------------------------------\n"
    text += "平均温度         " + "%8.2f" % (ob_mean) + "%20.2f" % (fo_mean) + "\n\n"
    text += "温度范围    " + "%8.2f" % (ob_min)+ "~%6.2f" % (ob_max) +"%12.2f" % (fo_min)+ "~%6.2f" % (fo_max) + "\n\n"
    text += "==============================================\n\n"
    text += "Mean absolute error:" + "%6.2f" % maee + "\n\n"
    text += "Mean error:" + "%6.2f" % mee + "\n\n"
    text += "Mean-squared error:" + "%6.2f" % msee + "\n\n"
    text += "Root mean-squared error:" + "%6.2f" % rmsee + "\n\n"
    text += "Bias:" + "%6.2f" % bias_ce + "\n\n"
    text += "Correlation ceoefficient:" + "%6.2f" % cor + "\n"
    plt.text(0, 0, text, fontsize=9)

    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()



def temper_sg(sta_ob,grd_fo,save_path = None,show = False,dpi = 200,add_county_line = False,ob_name = "观测",fo_name = "预报"):

    #meteva.base.reset(grd_fo)
    grid0 = meteva.base.get_grid_of_data(grd_fo)
    rlat = grid0.elat - grid0.slat
    rlon = grid0.elon - grid0.slon
    sta_ob1 = meteva.base.sele_by_para(sta_ob,grid=grid0)
    sta_fo1 = meteva.base.interp_gs_linear(grd_fo,sta_ob1)

    ob_min = np.min(sta_ob1.iloc[:,-1].values)
    fo_min = np.min(grd_fo.values)
    ob_max = np.max(sta_ob1.iloc[:,-1].values)
    fo_max = np.max(grd_fo.values)

    ob_fo_max = max(ob_max,fo_max)
    ob_fo_min = min(ob_min,fo_min)
    #clevs_temp, cmap_temp = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("temp")

    if ob_fo_max > 120:
        cmap_temp,clevs_temp= meteva.base.tool.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temp_2m)
    else:
        cmap_temp, clevs_temp = meteva.base.tool.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temp_2m)

    #print(clevs_temp)

    cmap, clevs = meteva.base.tool.color_tools.get_part_cmap_and_clevs(cmap_temp,clevs_temp,ob_fo_max,ob_fo_min)

    width = 9  #整个画面的宽度
    width_colorbar = 0.6
    height_title = 0.3
    height_veri_plot = 3

    if(rlon <= rlat * 0.5):
        #采用3*1布局
        width_map = (width - 2 * width_colorbar) / 3
        height_map = (rlat/ rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [width_colorbar/width, height_veri_plot/ height, width_map/width , height_map/height]  # 实况
        rect2 = [(1 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width ,  height_map/height] # 预报
        rect3 = [(2 * width_map +width_colorbar+0.05)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.015,height_map/height]
        error_colorbar_box = [(3 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.015,height_map/height]

    else:
        #采用1*2 + 1 布局
        width_map = (width - 2 * width_colorbar) / 1.5
        height_map = (rlat/ rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [(width_colorbar -0.03)/width, (height_veri_plot + 0.5 * height_map) / height, 0.5 * width_map/width , 0.5* height_map/height]  # 实况
        rect2 = [(width_colorbar -0.03)/width, height_veri_plot / height, 0.5 * width_map/width , 0.5* height_map/height] # 预报
        rect3 = [(0.5 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.01,height_map/height]
        error_colorbar_box = [(1.5 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.01,height_map/height]

    rect4 = [0.05, 0.06, 0.26, height_veri_plot / height-0.1]  # 散点回归图，左下宽高
    rect5 = [0.38, 0.06, 0.28, height_veri_plot / height-0.1]  # 频率柱状图， 左下宽高
    rect6 = [0.67, 0.01, 0.3, height_veri_plot / height-0.03]  # 左下宽高
    rect_title = [ width_colorbar/width,(height_veri_plot+ height_map)/height,1-2*width_colorbar/width, 0.001]

    fig = plt.figure(figsize=(width, height),dpi=dpi)
    # 平面对比图1



    # 设置地图背景
    ax1 = plt.axes(rect1)
    add_china_map_2basemap(ax1, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax1, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax1.set_xlim((grid0.slon, grid0.elon))
    ax1.set_ylim((grid0.slat, grid0.elat))



    #clevs = [-10,0,15,20,22,24,26,28,30,32,34,35]
    #colors_grid = ["#00AAAA","#009500","#808000", "#BFBF00","#FFFF00","#FFD400","#FFAA00","#FF7F00","#FF0000","#FF002A","#FF0055","#FF0055"]
    plt.xticks([])
    plt.yticks([])

    #plot_ob = ax1.contourf(x, y, grd_ob.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    plot_ob = meteva.base.plot_tools.add_scatter(ax1,grid0,sta_ob1,cmap=meteva.base.cmaps.temp_2m,alpha=1)

    ax1.set_title(ob_name,fontsize=18,loc="left",y = 0.0)
    colorbar_position_grid = fig.add_axes(ob_fo_colorbar_box)  # 位置[左,下,宽,高]
    plt.colorbar(plot_ob, cax=colorbar_position_grid, orientation='vertical')
    plt.title("温度(℃)", fontsize=8,verticalalignment='bottom')

    ax2 = plt.axes(rect2)
    plt.xticks([])
    plt.yticks([])
    add_china_map_2basemap(ax2, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax2, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax2.set_xlim((grid0.slon, grid0.elon))
    ax2.set_ylim((grid0.slat, grid0.elat))
    # 绘制格点预报场
    x = np.arange(grid0.nlon) * grid0.dlon + grid0.slon
    y = np.arange(grid0.nlat) * grid0.dlat + grid0.slat
    ax2.contourf(x, y, grd_fo.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    ax2.set_title(fo_name, fontsize=18, loc="left",y = 0.0)


    error_sta = meteva.base.minus_on_id(sta_fo1,sta_ob1)
    #error_grd = meteva.base.interp_sg_idw_delta(error_sta,grid0,halfR=300)

    ax3 = plt.axes(rect3)
    add_china_map_2basemap(ax3, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax3, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax3.set_xlim((grid0.slon, grid0.elon))
    ax3.set_ylim((grid0.slat, grid0.elat))

    #plot_grid1 = ax3.contourf(x, y,error , clevs1,cmap = "bwr")  # 填色图
    #cmap1,clevs1 = meteva.base.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temper_error_br,vmax= np.max(np.abs(error)))
    #cmap1, clevs1 = meteva.base.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temper_2m_error)
    #norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    #plot_grid1 = ax3.contourf(x, y, error,    levels = clevs1, cmap = cmap1, norm = norm)  # 填色图
    plot_error = meteva.base.plot_tools.add_scatter(ax3,grid0,error_sta,cmap=meteva.base.cmaps.temper_2m_error,alpha=1)
    colorbar_position_grid1 = fig.add_axes(error_colorbar_box)  # 位置[左,下,宽,高]
    title_error = fo_name + ' - ' + ob_name
    ax3.set_title(title_error,fontsize=18, loc="left",y = 0.0,color = "k")
    plt.colorbar(plot_error, cax=colorbar_position_grid1, orientation='vertical')
    plt.title("误差(℃)", fontsize=8, verticalalignment='bottom')

    time_str = meteva.base.tool.time_tools.time_to_str(grid0.gtime[0])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
    if type(grid0.members[0]) == str:
        model_name = grid0.members[0]
    else:
        model_name = str(grid0.members[0])

    title = model_name + " " + dati_str + "起报" + str(grid0.dtimes[0]) + "H时效预报和实况对比及误差"
    ax_title = plt.axes(rect_title)
    ax_title.axes.set_axis_off()
    ax_title.set_title(title)


    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()


def temper_comprehensive_ss(sta_ob,sta_fo,map_extend = None,save_path = None,show = False,dpi = 200,add_county_line = False,ob_name = "观测",fo_name = "预报"):

    sta0 = meteva.base.combine_on_id(sta_ob, sta_fo)
    grid0 = None
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
        grid0 = map_extend
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
        map_extend = [slon,elon,slat,elat]


    sta_ob1 = meteva.base.put_stadata_on_station(sta_ob,sta0)
    sta_fo1 = meteva.base.put_stadata_on_station(sta_fo,sta0)

    ob_min = np.min(sta_ob1.iloc[:,-1].values)
    fo_min = np.min(sta_fo1.iloc[:,-1].values)
    ob_max = np.max(sta_ob1.iloc[:,-1].values)
    fo_max = np.max(sta_fo1.iloc[:,-1].values)

    ob_fo_max = max(ob_max,fo_max)
    ob_fo_min = min(ob_min,fo_min)
    #clevs_temp, cmap_temp = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("temp")

    if ob_fo_max > 120:
        cmap_temp,clevs_temp= meteva.base.tool.color_tools.clev_cmap_temper_2m_k()
    else:
        cmap_temp,clevs_temp = meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("temp")

    cmap, clevs = meteva.base.tool.color_tools.get_part_cmap_and_clevs(cmap_temp,clevs_temp,ob_fo_max,ob_fo_min)

    width = 9  #整个画面的宽度
    width_colorbar = 0.6
    height_title = 0.3
    height_veri_plot = 3

    if(rlon <= rlat * 0.5):
        #采用3*1布局
        width_map = (width - 2 * width_colorbar) / 3
        height_map = (rlat/ rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [width_colorbar/width, height_veri_plot/ height, width_map/width , height_map/height]  # 实况
        rect2 = [(1 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width ,  height_map/height] # 预报
        rect3 = [(2 * width_map +width_colorbar+0.05)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.015,height_map/height]
        error_colorbar_box = [(3 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.015,height_map/height]

    else:
        #采用1*2 + 1 布局
        width_map = (width - 2 * width_colorbar) / 1.5
        height_map = (rlat / rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [(width_colorbar -0.03)/width, (height_veri_plot + 0.5 * height_map) / height, 0.5 * width_map/width , 0.5* height_map/height]  # 实况
        rect2 = [(width_colorbar -0.03)/width, height_veri_plot / height, 0.5 * width_map/width , 0.5* height_map/height] # 预报
        rect3 = [(0.5 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.01,height_map/height]
        error_colorbar_box = [(1.5 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.01,height_map/height]

    rect4 = [0.05, 0.06, 0.26, height_veri_plot / height-0.1]  # 散点回归图，左下宽高
    rect5 = [0.38, 0.06, 0.28, height_veri_plot / height-0.1]  # 频率柱状图， 左下宽高
    rect6 = [0.67, 0.01, 0.3, height_veri_plot / height-0.03]  # 左下宽高
    rect_title = [ width_colorbar/width,(height_veri_plot+ height_map)/height,1-2*width_colorbar/width, 0.001]

    fig = plt.figure(figsize=(width, height),dpi=dpi)
    # 平面对比图1

    # 设置地图背景
    ax1 = plt.axes(rect1)
    add_china_map_2basemap(ax1, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax1, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax1.set_xlim((slon, elon))
    ax1.set_ylim((slat, elat))



    #clevs = [-10,0,15,20,22,24,26,28,30,32,34,35]
    #colors_grid = ["#00AAAA","#009500","#808000", "#BFBF00","#FFFF00","#FFD400","#FFAA00","#FF7F00","#FF0000","#FF002A","#FF0055","#FF0055"]
    plt.xticks([])
    plt.yticks([])

    #plot_ob = ax1.contourf(x, y, grd_ob.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    plot_ob = meteva.base.plot_tools.add_scatter(ax1,map_extend,sta_ob1,cmap=meteva.base.cmaps.temp_2m,alpha=1)

    ax1.set_title(ob_name,fontsize=18,loc="left",y = 0.0)
    colorbar_position_grid = fig.add_axes(ob_fo_colorbar_box)  # 位置[左,下,宽,高]
    plt.colorbar(plot_ob, cax=colorbar_position_grid, orientation='vertical')
    plt.title("温度(℃)", fontsize=8,verticalalignment='bottom')

    ax2 = plt.axes(rect2)
    plt.xticks([])
    plt.yticks([])
    add_china_map_2basemap(ax2, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax2, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    #ax2.set_xlim((grid0.slon, grid0.elon))
    #ax2.set_ylim((grid0.slat, grid0.elat))
    # 绘制格点预报场
    #x = np.arange(grid0.nlon) * grid0.dlon + grid0.slon
    #y = np.arange(grid0.nlat) * grid0.dlat + grid0.slat
    #ax2.contourf(x, y, grd_fo.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    plot_fo = meteva.base.plot_tools.add_scatter(ax2, map_extend, sta_fo1, cmap=meteva.base.cmaps.temp_2m,alpha=1)
    ax2.set_title(fo_name, fontsize=18, loc="left",y = 0.0)


    error_sta = meteva.base.minus_on_id(sta_fo1,sta_ob1)
    #error_grd = meteva.base.interp_sg_idw_delta(error_sta,grid0,halfR=300)

    ax3 = plt.axes(rect3)
    add_china_map_2basemap(ax3, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax3, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax1.set_xlim((slon, elon))
    ax1.set_ylim((slat, elat))

    #plot_grid1 = ax3.contourf(x, y,error , clevs1,cmap = "bwr")  # 填色图
    #cmap1,clevs1 = meteva.base.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temper_error_br,vmax= np.max(np.abs(error)))
    #cmap1, clevs1 = meteva.base.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temper_2m_error)
    #norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    #plot_grid1 = ax3.contourf(x, y, error,    levels = clevs1, cmap = cmap1, norm = norm)  # 填色图
    plot_error = meteva.base.plot_tools.add_scatter(ax3,map_extend,error_sta,cmap=meteva.base.cmaps.temper_2m_error,alpha=1)
    colorbar_position_grid1 = fig.add_axes(error_colorbar_box)  # 位置[左,下,宽,高]
    title_error = fo_name + ' - ' + ob_name
    ax3.set_title(title_error,fontsize=18, loc="left",y = 0.0,color = "k")
    plt.colorbar(plot_error, cax=colorbar_position_grid1, orientation='vertical')
    plt.title("误差(℃)", fontsize=8, verticalalignment='bottom')

    time_str = meteva.base.tool.time_tools.time_to_str(sta_fo["time"].values[0])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
    model_name = meteva.base.get_stadata_names(sta_fo)[0]
    title = model_name + " " + dati_str + "起报" + str(sta_fo["dtime"].values[0]) + "H时效预报和实况对比及误差"
    ax_title = plt.axes(rect_title)
    ax_title.axes.set_axis_off()
    ax_title.set_title(title)

    # 散点回归图
    ax2 = plt.axes(rect4)
    # 保证这两个值的正确性
    ob = sta_ob1.iloc[:,-1].values
    fo = sta_fo1.iloc[:,-1].values
    # X = np.zeros((len(fo), 1))
    # X[:, 0] = fo
    # clf = LinearRegression().fit(X, ob)
    num_max = max(np.max(ob), np.max(fo))
    num_min = min(np.min(ob), np.min(fo))
    dmm = num_max - num_min
    if (num_min != 0):
        num_min -= 0.1 * dmm
    num_max += dmm * 0.1
    dmm = num_max - num_min
    ob_line = np.arange(num_min, num_max, dmm / 30)
    # X = np.zeros((len(ob_line), 1))
    # X[:, 0] = ob_line
    # fo_rg = clf.predict(X)

    slope, intercept, r_value, p_value, std_err = st.linregress(fo, ob)
    fo_rg = slope * ob_line + intercept
    ax2.plot(ob_line, fo_rg, color='r')
    rg_text1 = "R = " + '%.2f' % (r_value)
    if intercept >= 0:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X + " + '%.2f' % (intercept)
    else:
        rg_text2 = "Y = " + '%.2f' % (slope) + "* X - " + '%.2f' % (-intercept)

    ax2.plot(fo, ob, '.', color='b',markersize=1)
    ax2.plot(ob_line, fo_rg, color="r")
    ax2.plot(ob_line, ob_line, '--', color="k")
    ax2.set_xlim(num_min, num_max)
    ax2.set_ylim(num_min, num_max)
    ax2.set_xlabel(fo_name,fontsize=10)
    ax2.set_ylabel(ob_name,fontsize=10)
    #rg_text2 = "Y = " + '%.2f' % (clf.coef_[0]) + "* X + " + '%.2f' % (clf.intercept_)
    ax2.text(num_min + 0.05 * dmm, num_min + 0.90 * dmm, rg_text2, fontsize=15, color="r")

    # 设置次刻度间隔
    xmi = 1
    if (np.max(ob) > 100): xmi = 2
    ymi = 1
    if (np.max(fo) > 100): ymi = 2
    xmajorLocator = mpl.ticker.MultipleLocator(10 * xmi)  # 将x主刻度标签设置为次刻度10倍
    ymajorLocator = mpl.ticker.MultipleLocator(10 * ymi)  # 将y主刻度标签设置为次刻度10倍
    ax2.xaxis.set_major_locator(xmajorLocator)
    ax2.yaxis.set_major_locator(ymajorLocator)
    xminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将x轴次刻度标签设置xmi
    yminorLocator = mpl.ticker.MultipleLocator(ymi)  # 将y轴次刻度标签设置ymi
    ax2.xaxis.set_minor_locator(xminorLocator)
    ax2.yaxis.set_minor_locator(yminorLocator)

    #折线图
    # 绘制频率柱状图
    p_ob = np.zeros(len(clevs)-1)
    p_fo = np.zeros(len(clevs)-1)
    x = clevs[0:-1]
    for i in range(len(clevs) - 1):
        index0 = np.where((ob >= clevs[i]) & (ob < clevs[i + 1]))
        p_ob[i] = len(index0[0])
        index0 = np.where((fo >= clevs[i]) & (fo < clevs[i + 1]))
        p_fo[i] = len(index0[0])

    ax5 = plt.axes(rect5)
    # ax5.plot(p_ob, color='r',label="Obs")
    # ax5.plot(p_fo, color='b',label="Pred")
    ax5.bar(x + 0.5, p_ob, width=0.4,color='r', label=ob_name)
    ax5.bar(x + 1.1, p_fo, width=0.4,color="b", label=fo_name)
    ax5.legend(loc="upper right")
    ax5.set_xlabel("等级", fontsize=10)
    ax5.set_ylabel("站点数", fontsize=10)
    #ax5.set_title("频率统计图", fontsize=10)
    ax5.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1000))
    maxy = max(np.max(p_fo),np.max(p_ob)) * 1.4
    ax5.set_ylim(0,maxy)

    #检验效果图
    # 绘制降水站点实况预报统计表
    ax6 = plt.axes(rect6)
    ax6.axes.set_axis_off()
    ob_mean = np.mean(ob)
    fo_mean = np.mean(fo)


    maee = meteva.method.continuous.score.mae(ob, fo)
    mee = meteva.method.continuous.score.me(ob, fo)
    msee = meteva.method.continuous.score.mse(ob, fo)
    rmsee = meteva.method.continuous.score.rmse(ob, fo)
    bias_ce = meteva.method.continuous.score.bias_m(ob, fo)
    cor = meteva.method.continuous.score.corr(ob,fo)


    text = "格点检验统计量 n=" + str(len(ob)) + "\n"
    text += "==============================================\n"
    text += "                     实况               预报   \n"
    text += "----------------------------------------------\n"
    text += "平均温度         " + "%8.2f" % (ob_mean) + "%20.2f" % (fo_mean) + "\n\n"
    text += "温度范围    " + "%8.2f" % (ob_min)+ "~%6.2f" % (ob_max) +"%12.2f" % (fo_min)+ "~%6.2f" % (fo_max) + "\n\n"
    text += "==============================================\n\n"
    text += "Mean absolute error:" + "%6.2f" % maee + "\n\n"
    text += "Mean error:" + "%6.2f" % mee + "\n\n"
    text += "Mean-squared error:" + "%6.2f" % msee + "\n\n"
    text += "Root mean-squared error:" + "%6.2f" % rmsee + "\n\n"
    text += "Bias:" + "%6.2f" % bias_ce + "\n\n"
    text += "Correlation ceoefficient:" + "%6.2f" % cor + "\n"
    plt.text(0, 0, text, fontsize=9)

    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()

def temper_ss(sta_ob, sta_fo, map_extend=None, save_path=None, show=False, dpi=200,
                            add_county_line=False, ob_name="观测", fo_name="预报"):

    sta0 = meteva.base.combine_on_id(sta_ob, sta_fo)
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
        grid0 = map_extend
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
        map_extend = [slon, elon, slat, elat]

    sta_ob1 = meteva.base.put_stadata_on_station(sta_ob, sta0)
    sta_fo1 = meteva.base.put_stadata_on_station(sta_fo, sta0)

    ob_min = np.min(sta_ob1.iloc[:, -1].values)
    fo_min = np.min(sta_fo1.iloc[:, -1].values)
    ob_max = np.max(sta_ob1.iloc[:, -1].values)
    fo_max = np.max(sta_fo1.iloc[:, -1].values)

    ob_fo_max = max(ob_max, fo_max)
    ob_fo_min = min(ob_min, fo_min)
    # clevs_temp, cmap_temp = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("temp")

    if ob_fo_max > 120:
        cmap_temp, clevs_temp = meteva.base.tool.color_tools.clev_cmap_temper_2m_k()
    else:
        cmap_temp, clevs_temp = meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("temp")

    cmap, clevs = meteva.base.tool.color_tools.get_part_cmap_and_clevs(cmap_temp, clevs_temp, ob_fo_max, ob_fo_min)

    width = 9  # 整个画面的宽度
    width_colorbar = 0.6
    height_title = 0.3
    height_veri_plot = 3

    if (rlon <= rlat * 0.5):
        # 采用3*1布局
        width_map = (width - 2 * width_colorbar) / 3
        height_map = (rlat / rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [width_colorbar / width, height_veri_plot / height, width_map / width, height_map / height]  # 实况
        rect2 = [(1 * width_map + width_colorbar) / width, height_veri_plot / height, width_map / width,
                 height_map / height]  # 预报
        rect3 = [(2 * width_map + width_colorbar + 0.05) / width, height_veri_plot / height, width_map / width,
                 height_map / height]  # 误差
        ob_fo_colorbar_box = [0.02, height_veri_plot / height, 0.015, height_map / height]
        error_colorbar_box = [(3 * width_map + width_colorbar + 0.05) / width, height_veri_plot / height, 0.015,
                              height_map / height]

    else:
        # 采用1*2 + 1 布局
        width_map = (width - 2 * width_colorbar) / 1.5
        height_map = (rlat / rlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [(width_colorbar - 0.03) / width, (height_veri_plot + 0.5 * height_map) / height,
                 0.5 * width_map / width, 0.5 * height_map / height]  # 实况
        rect2 = [(width_colorbar - 0.03) / width, height_veri_plot / height, 0.5 * width_map / width,
                 0.5 * height_map / height]  # 预报
        rect3 = [(0.5 * width_map + width_colorbar) / width, height_veri_plot / height, width_map / width,
                 height_map / height]  # 误差
        ob_fo_colorbar_box = [0.02, height_veri_plot / height, 0.01, height_map / height]
        error_colorbar_box = [(1.5 * width_map + width_colorbar + 0.05) / width, height_veri_plot / height, 0.01,
                              height_map / height]

    rect4 = [0.05, 0.06, 0.26, height_veri_plot / height - 0.1]  # 散点回归图，左下宽高
    rect5 = [0.38, 0.06, 0.28, height_veri_plot / height - 0.1]  # 频率柱状图， 左下宽高
    rect6 = [0.67, 0.01, 0.3, height_veri_plot / height - 0.03]  # 左下宽高
    rect_title = [width_colorbar / width, (height_veri_plot + height_map) / height, 1 - 2 * width_colorbar / width,
                  0.001]

    fig = plt.figure(figsize=(width, height),dpi=dpi)
    # 平面对比图1

    # 设置地图背景
    ax1 = plt.axes(rect1)
    add_china_map_2basemap(ax1, name='province', edgecolor='k', lw=0.3, encoding='gbk')  # "省界"
    if add_county_line:
        add_china_map_2basemap(ax1, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax1.set_xlim((slon, elon))
    ax1.set_ylim((slat, elat))

    # clevs = [-10,0,15,20,22,24,26,28,30,32,34,35]
    # colors_grid = ["#00AAAA","#009500","#808000", "#BFBF00","#FFFF00","#FFD400","#FFAA00","#FF7F00","#FF0000","#FF002A","#FF0055","#FF0055"]
    plt.xticks([])
    plt.yticks([])

    # plot_ob = ax1.contourf(x, y, grd_ob.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    plot_ob = meteva.base.plot_tools.add_scatter(ax1, map_extend, sta_ob1, cmap=meteva.base.cmaps.temp_2m, alpha=1)

    ax1.set_title(ob_name, fontsize=18, loc="left", y=0.0)
    colorbar_position_grid = fig.add_axes(ob_fo_colorbar_box)  # 位置[左,下,宽,高]
    plt.colorbar(plot_ob, cax=colorbar_position_grid, orientation='vertical')
    plt.title("温度(℃)", fontsize=8, verticalalignment='bottom')

    ax2 = plt.axes(rect2)
    plt.xticks([])
    plt.yticks([])
    add_china_map_2basemap(ax2, name='province', edgecolor='k', lw=0.3, encoding='gbk')  # "省界"
    if add_county_line:
        add_china_map_2basemap(ax2, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    # ax2.set_xlim((grid0.slon, grid0.elon))
    # ax2.set_ylim((grid0.slat, grid0.elat))
    # 绘制格点预报场
    # x = np.arange(grid0.nlon) * grid0.dlon + grid0.slon
    # y = np.arange(grid0.nlat) * grid0.dlat + grid0.slat
    # ax2.contourf(x, y, grd_fo.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    plot_fo = meteva.base.plot_tools.add_scatter(ax2, map_extend, sta_fo1, cmap=meteva.base.cmaps.temp_2m, alpha=1)
    ax2.set_title(fo_name, fontsize=18, loc="left", y=0.0)

    error_sta = meteva.base.minus_on_id(sta_fo1, sta_ob1)
    # error_grd = meteva.base.interp_sg_idw_delta(error_sta,grid0,halfR=300)

    ax3 = plt.axes(rect3)
    add_china_map_2basemap(ax3, name='province', edgecolor='k', lw=0.3, encoding='gbk')  # "省界"
    if add_county_line:
        add_china_map_2basemap(ax3, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax1.set_xlim((slon, elon))
    ax1.set_ylim((slat, elat))

    # plot_grid1 = ax3.contourf(x, y,error , clevs1,cmap = "bwr")  # 填色图
    # cmap1,clevs1 = meteva.base.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temper_error_br,vmax= np.max(np.abs(error)))
    # cmap1, clevs1 = meteva.base.color_tools.def_cmap_clevs(cmap=meteva.base.cmaps.temper_2m_error)
    # norm = BoundaryNorm(clevs1, ncolors=cmap1.N-1)
    # plot_grid1 = ax3.contourf(x, y, error,    levels = clevs1, cmap = cmap1, norm = norm)  # 填色图
    plot_error = meteva.base.plot_tools.add_scatter(ax3, map_extend, error_sta,
                                                    cmap=meteva.base.cmaps.temper_2m_error, alpha=1)
    colorbar_position_grid1 = fig.add_axes(error_colorbar_box)  # 位置[左,下,宽,高]
    title_error = fo_name + ' - ' + ob_name
    ax3.set_title(title_error, fontsize=18, loc="left", y=0.0, color="k")
    plt.colorbar(plot_error, cax=colorbar_position_grid1, orientation='vertical')
    plt.title("误差(℃)", fontsize=8, verticalalignment='bottom')

    time_str = meteva.base.tool.time_tools.time_to_str(sta_fo["time"].values[0])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
    model_name = meteva.base.get_stadata_names(sta_fo)[0]
    title = model_name + " " + dati_str + "起报" + str(sta_fo["dtime"].values[0]) + "H时效预报和实况对比及误差"
    ax_title = plt.axes(rect_title)
    ax_title.axes.set_axis_off()
    ax_title.set_title(title)


    # 图片显示或保存
    if (save_path is not None):
        plt.savefig(save_path, dpi=dpi, bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()




