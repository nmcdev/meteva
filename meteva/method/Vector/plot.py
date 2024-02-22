import matplotlib.pyplot as plt
import os
import math
import numpy as np
import meteva
from matplotlib.colors import BoundaryNorm
import pandas as pd
import datetime


def scatter_uv_error(u_ob,u_fo,v_ob,v_fo,member_list = None,title = "风矢量误差散点分布图"
              , vmax=None, ncol=None, save_path=None, show=False, dpi=300,
               sup_fontsize=10, width=None, height=None,x_label ="U分量",y_label = "v_分量"):


    if vmax is None:
        du = u_fo - u_ob
        dv = v_fo - v_ob
        speed_d= np.sqrt(du * du + dv * dv)
        vmax = np.max(speed_d)
        vmax = math.ceil(vmax)

    Fo_shape = u_fo.shape
    Ob_shape = u_ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_u_Fo = u_fo.reshape(new_Fo_shape)
    new_v_Fo = v_fo.reshape(new_Fo_shape)
    new_Fo_shape = new_u_Fo.shape
    sub_plot_num = new_Fo_shape[0]



    height_title = sup_fontsize * 0.01
    height_bottem_xticsk = sup_fontsize * 0.05
    height_hspace = sup_fontsize * 0.07

    width_wspace = height_hspace

    width_colorbar = 0.5
    width_left_yticks = sup_fontsize * 0.1


    if ncol is None:
        if sub_plot_num ==1:
            ncol = 1
        elif sub_plot_num %2 == 0:
            ncol = 2
        else:
            ncol = 3

    if title is None:
        sup_height_title = 0
    else:
        sup_height_title = sup_fontsize * 0.12
    nrow = math.ceil(new_Fo_shape[0] / ncol)
    if width is None and height is None:
        if sub_plot_num ==1:
            width = 5
        else:
            width = 10


    if width is None:
        height_all_plot = height - height_title - height_bottem_xticsk - (nrow-1) * height_hspace + sup_height_title
        height_axis = height_all_plot / nrow
        width_axis = height_axis
        width_all_plot = width_axis * ncol + (ncol-1) * width_wspace
        width = width_all_plot + width_colorbar + width_left_yticks
    else:
        width_all_plot = width - width_colorbar - width_left_yticks - (ncol - 1) * width_wspace
        width_axis = width_all_plot / ncol
        height_axis = width_axis
        height_all_plot = height_axis * nrow + (nrow-1) * height_hspace
        height = height_all_plot + height_title + height_bottem_xticsk + sup_height_title


    if u_ob.size>10000:
        step = 0.02
    elif u_ob.size < 100:
        step = 0.2
    else:
        step = 2/np.sqrt(u_ob.size)
    step = step * vmax
    grid_count = meteva.base.grid([-vmax,vmax,step],[-vmax,vmax,step])

    fig = plt.figure(figsize=(width, height), dpi=dpi)
    plt.subplots_adjust(hspace = 0.3,wspace = 0.3)
    u1 = u_ob.flatten()
    v1 = v_ob.flatten()

    if member_list is None:
        member_list = []
        for line in range(new_Fo_shape[0]):
            member_list.append("预报" + str(line))

    #为统一色标，需要预先计算出所有误差场的密度场
    sta_count_list = []
    max_count = 0
    nsample = u_ob.size
    for line in range(new_Fo_shape[0]):
        u2 = new_u_Fo[line, :].flatten()
        v2 = new_v_Fo[line, :].flatten()
        markersize = 5 * width_axis * height_axis / np.sqrt(u_ob.size)
        du = u2 - u1
        dv = v2 - v1
        df = pd.DataFrame({"lon": du, "lat": dv})
        sta_xy = meteva.base.sta_data(df)
        sta_xy["time"] = datetime.datetime(2020, 1, 1, 0)
        sta_xy["data0"] = 1
        grd_count = meteva.base.near.add_stavalue_to_nearest_grid(sta_xy, grid=grid_count)
        grd_count.values /=(nsample*step*step) #转换为概率密度
        grd_count = meteva.base.smooth(grd_count,1)
        sta_count = meteva.base.interp_gs_linear(grd_count, sta_xy)
        sta_count_list.append(sta_count)
        count1 = np.max(sta_count["data0"].values)
        if count1 > max_count:
            max_count = count1

    cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap="turbo", clevs=None, vmin=0, vmax=max_count)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N - 1)


    for line in range(new_Fo_shape[0]):
        pi = line % ncol
        pj = int(line / ncol)
        rect1 = [(width_left_yticks + pi * (width_axis + width_wspace))/width,
                 (height_bottem_xticsk + (nrow -1- pj) * (height_axis + height_hspace))/height,
                 width_axis / width,
                 height_axis / height]
        ax = plt.axes(rect1)

        if markersize < 1:
            markersize = 1
        elif markersize > 20:
            markersize = 20
        #plt.subplot(nrows, ncols, line + 1)

        sta_count = sta_count_list[line]
        sta_count = sta_count.sort_values(by=["data0"])
        #print(sta_count)
        colors = sta_count["data0"]
        #sort_index = colors.argsort() #为了将高密度的点画在最上层
        dv_s = sta_count["lat"]
        du_s = sta_count["lon"]
        #colors = colors[sort_index]
        im = plt.scatter(du_s, dv_s, c=colors, s=markersize ,cmap=cmap1, norm=norm)
        #plt.plot(u2-u1,v2-v1,'.',color = colors[line+1], markersize=markersize)
        #plt.plot(u1,v1,'.',color= 'b',  markersize=markersize)
        plt.xlabel(x_label,fontsize = sup_fontsize *0.9)
        plt.ylabel(y_label,fontsize = sup_fontsize *0.9)
        plt.title(member_list[line],fontsize = sup_fontsize)

        #print(maxs)
        plt.xlim(-vmax,vmax)
        plt.ylim(-vmax,vmax)
        #plt.legend()
        angles = np.arange(0,360,45)
        for i in range(len(angles)):
            angle = angles[i] * 3.1415926 /180
            r = np.arange(0,vmax+1,vmax * 0.1)
            x = r * np.sin(angle)
            y = r * np.cos(angle)
            plt.plot(x,y,"--",color = "k",linewidth = 0.5)

        rs = np.arange(0,vmax+1,1)
        for i in range(len(rs)):
            r = rs[i]
            angle = np.arange(0,360) * 3.1415926 /180
            x = r * np.sin(angle)
            y = r * np.cos(angle)
            plt.plot(x,y,"--",color = "k",linewidth = 0.5)

    left_low = (width_left_yticks + ncol * width_axis + (ncol - 1) * width_wspace + 0.1) / width
    # print(left_low)
    colorbar_position_grid = fig.add_axes(
        [left_low, height_bottem_xticsk / height, 0.01, height_all_plot / height])  # 位置[左,下,宽,高]

    # colorbar_position_grid = fig.add_axes([0.92, 0.50, 0.02, 0.32])  # 位置[左,下,宽,高]
    colorbar_ob = plt.colorbar(im, cax=colorbar_position_grid)
    colorbar_ob.ax.tick_params(labelsize=sup_fontsize * 0.5)  # 改变bar标签字体大小

    y_sup_title = (height_bottem_xticsk + (nrow) * (height_axis + height_hspace)) / height
    if title is not None:
        plt.suptitle(title, y = y_sup_title,fontsize=sup_fontsize * 1.2)

    if(save_path is not None):
        file1,extension = os.path.splitext(save_path)
        extension = extension[1:]
        plt.savefig(save_path,format = extension)
    else:
        show = True
    if show:
        plt.show()
    plt.close()


def scatter_uv(u_ob,u_fo,v_ob,v_fo,member_list = None,title = "风矢量散点分布图"
               , vmax=None, ncol=None, save_path=None, show=False, dpi=300,
               sup_fontsize=10, width=None, height=None,add_randn_to_ob = 0.0,x_label ="U分量",y_label = "v_分量"):


    if vmax is None:
        speed_ob = np.sqrt(u_ob * u_ob + v_ob * v_ob)
        speed_fo = np.sqrt(u_fo * u_fo + v_fo * v_fo)
        vmax = max(np.max(speed_ob), np.max(speed_fo))
        vmax = math.ceil(vmax)

    Fo_shape = u_fo.shape
    Ob_shape = u_ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_u_Fo = u_fo.reshape(new_Fo_shape)
    new_v_Fo = v_fo.reshape(new_Fo_shape)
    new_Fo_shape = new_u_Fo.shape
    sub_plot_num = new_Fo_shape[0] + 1

    height_title = sup_fontsize * 0.01
    height_bottem_xticsk = sup_fontsize * 0.05
    height_hspace = sup_fontsize * 0.07

    width_wspace = height_hspace

    width_colorbar = 0.5
    width_left_yticks = sup_fontsize * 0.1


    if ncol is None:
        if sub_plot_num ==1:
            ncol = 1
        elif sub_plot_num %2 == 0:
            ncol = 2
        else:
            ncol = 3


    if title is None:
        sup_height_title = 0
    else:
        sup_height_title = sup_fontsize * 0.12
    nrow = math.ceil(new_Fo_shape[0] / ncol)
    if width is None and height is None:
        if sub_plot_num ==1:
            width = 5
        else:
            width = 10


    if width is None:
        height_all_plot = height - height_title - height_bottem_xticsk - (nrow-1) * height_hspace + sup_height_title
        height_axis = height_all_plot / nrow
        width_axis = height_axis
        width_all_plot = width_axis * ncol + (ncol-1) * width_wspace
        width = width_all_plot + width_colorbar + width_left_yticks
    else:
        width_all_plot = width - width_colorbar - width_left_yticks - (ncol - 1) * width_wspace
        width_axis = width_all_plot / ncol
        height_axis = width_axis
        height_all_plot = height_axis * nrow + (nrow-1) * height_hspace
        height = height_all_plot + height_title + height_bottem_xticsk + sup_height_title


    u1 = u_ob.flatten() + np.random.randn(len(u_ob))*add_randn_to_ob
    v1 = v_ob.flatten() + np.random.randn(len(v_ob))*add_randn_to_ob

    if member_list is None:
        member_list = ["观测"]
        for line in range(new_Fo_shape[0]):
            member_list.append("预报" + str(line))
    elif len(member_list) == new_Fo_shape[0]:
        member_list.insert(0,"观测")

    if u_ob.size>10000:
        step = 0.02
    elif u_ob.size < 100:
        step = 0.2
    else:
        step = 2/np.sqrt(u_ob.size)
    step = step * vmax
    grid_count = meteva.base.grid([-vmax,vmax,step],[-vmax,vmax,step])
    nsample = u_ob.size
    df = pd.DataFrame({"lon": u1, "lat": v1})
    sta_xy = meteva.base.sta_data(df)
    sta_xy["time"] = datetime.datetime(2020, 1, 1, 0)
    sta_xy["data0"] = 1
    grd_count = meteva.base.near.add_stavalue_to_nearest_grid(sta_xy, grid=grid_count)
    grd_count.values /= (nsample * step * step)  # 转换为概率密度
    grd_count = meteva.base.smooth(grd_count, 1)
    sta_count_ob = meteva.base.interp_gs_linear(grd_count, sta_xy)
    sta_count_ob = sta_count_ob.sort_values(by = ["data0"])
    max_count = sta_count_ob.iloc[-1,-1]

    sta_count_list = [sta_count_ob]
    for line in range(new_Fo_shape[0]):
        u2 = new_u_Fo[line, :].flatten()
        v2 = new_v_Fo[line, :].flatten()
        df = pd.DataFrame({"lon": u2, "lat": v2})
        sta_xy = meteva.base.sta_data(df)
        sta_xy["time"] = datetime.datetime(2020, 1, 1, 0)
        sta_xy["data0"] = 1
        grd_count = meteva.base.near.add_stavalue_to_nearest_grid(sta_xy, grid=grid_count)
        grd_count.values /=(nsample*step*step) #转换为概率密度
        grd_count = meteva.base.smooth(grd_count,1)
        sta_count_fo = meteva.base.interp_gs_linear(grd_count, sta_xy)
        sta_count_fo = sta_count_fo.sort_values(by=["data0"])
        sta_count_list.append(sta_count_fo)
        count1 = sta_count_fo.iloc[-1,-1]
        if count1 > max_count:
            max_count = count1
    markersize = 10 * width_axis * height_axis / np.sqrt(u_ob.size)
    if markersize < 1:
        markersize = 1
    elif markersize > 20:
        markersize = 20

    cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap="turbo", clevs=None, vmin=0, vmax=max_count)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N - 1)


    fig = plt.figure(figsize=(width, height), dpi=dpi)
    colors = meteva.base.color_tools.get_color_list(new_Fo_shape[0]+1)

    for k in range(len(sta_count_list)):
        pi = k % ncol
        pj = int(k / ncol)

        rect1 = [(width_left_yticks + pi * (width_axis + width_wspace))/width,
                 (height_bottem_xticsk + (nrow -1- pj) * (height_axis + height_hspace))/height,
                 width_axis / width,
                 height_axis / height]
        ax = plt.axes(rect1)
        sta_count = sta_count_list[k]

        colors = sta_count["data0"]
        #sort_index = colors.argsort() #为了将高密度的点画在最上层
        dv_s = sta_count["lat"]
        du_s = sta_count["lon"]
        #colors = colors[sort_index]
        im = plt.scatter(du_s, dv_s, c=colors, s=markersize ,cmap=cmap1, norm=norm)
        #plt.subplot(nrow, ncols, line + 1)
        #plt.plot(u1,v1,'.',color= "r", markeredgewidth = 0, markersize=markersize,alpha = 0.5,label = "OBS")
        #plt.plot(u2,v2,'.', markeredgewidth = 0,  markersize=markersize,)

        plt.xlabel(x_label,fontsize = sup_fontsize *0.9)
        plt.ylabel(y_label,fontsize = sup_fontsize *0.9)
        plt.title(member_list[k],fontsize = sup_fontsize)


        plt.xlim(-vmax,vmax)
        plt.ylim(-vmax,vmax)
        #plt.legend(loc = 2,fontsize = sup_fontsize * 0.7)
        angles = np.arange(0,360,45)
        for i in range(len(angles)):
            angle = angles[i] * 3.1415926 /180
            r = np.arange(0,vmax+1,vmax * 0.1)
            x = r * np.sin(angle)
            y = r * np.cos(angle)
            plt.plot(x,y,"--",color = "k",linewidth = 0.5)

        rs = np.arange(0,vmax+1,1)
        for i in range(len(rs)):
            r = rs[i]
            angle = np.arange(0,360) * 3.1415926 /180
            x = r * np.sin(angle)
            y = r * np.cos(angle)
            plt.plot(x,y,"--",color = "k",linewidth = 0.5)
        plt.xticks(fontsize = 0.8 * sup_fontsize)
        plt.yticks(fontsize = 0.8 * sup_fontsize)


    left_low = (width_left_yticks + ncol * width_axis  + (ncol-1)*width_wspace+0.1)/width
    #print(left_low)
    colorbar_position_grid = fig.add_axes([left_low, height_bottem_xticsk / height,0.01, height_all_plot/height])  # 位置[左,下,宽,高]

    #colorbar_position_grid = fig.add_axes([0.92, 0.50, 0.02, 0.32])  # 位置[左,下,宽,高]
    colorbar_ob = plt.colorbar(im, cax=colorbar_position_grid)
    colorbar_ob.ax.tick_params(labelsize=sup_fontsize * 0.5)  # 改变bar标签字体大小


    y_sup_title = (height_bottem_xticsk + (nrow) * (height_axis + height_hspace)) / height
    if title is not None:
        plt.suptitle(title, y = y_sup_title,fontsize=sup_fontsize * 1.2)

    if(save_path is not None):
        file1,extension = os.path.splitext(save_path)
        extension = extension[1:]
        plt.savefig(save_path,format = extension)
    else:
        show = True
    if show:
        plt.show()
    plt.close()

def probability_density_uv(u_ob,u_fo,v_ob,v_fo,member_list = None,title = "风矢量概率密度分布图"
               , vmax=None, ncol=None, save_path=None, show=False, dpi=300,
               sup_fontsize=10, width=None, height=None,add_randn_to_ob = 0.0,smooth_times = 0,linewidths = 1
                           ,x_label ="U分量",y_label = "v_分量",label_fontsize = 5):


    if vmax is None:
        speed_ob = np.sqrt(u_ob * u_ob + v_ob * v_ob)
        speed_fo = np.sqrt(u_fo * u_fo + v_fo * v_fo)
        vmax = max(np.max(speed_ob), np.max(speed_fo))
        vmax = math.ceil(vmax)

    Fo_shape = u_fo.shape
    Ob_shape = u_ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_u_Fo = u_fo.reshape(new_Fo_shape)
    new_v_Fo = v_fo.reshape(new_Fo_shape)
    new_Fo_shape = new_u_Fo.shape
    sub_plot_num = new_Fo_shape[0]

    height_title = sup_fontsize * 0.01
    height_bottem_xticsk = sup_fontsize * 0.05
    height_hspace = sup_fontsize * 0.07

    width_wspace = height_hspace

    width_colorbar = 0.5
    width_left_yticks = sup_fontsize * 0.1


    if ncol is None:
        if sub_plot_num ==1:
            ncol = 1
        elif sub_plot_num %2 == 0:
            ncol = 2
        else:
            ncol = 3


    if title is None:
        sup_height_title = 0
    else:
        sup_height_title = sup_fontsize * 0.12
    nrow = math.ceil(new_Fo_shape[0] / ncol)
    if width is None and height is None:
        if sub_plot_num ==1:
            width = 5
        else:
            width = 10


    if width is None:
        height_all_plot = height - height_title - height_bottem_xticsk - (nrow-1) * height_hspace + sup_height_title
        height_axis = height_all_plot / nrow
        width_axis = height_axis
        width_all_plot = width_axis * ncol + (ncol-1) * width_wspace
        width = width_all_plot + width_colorbar + width_left_yticks
    else:
        width_all_plot = width - width_colorbar - width_left_yticks - (ncol - 1) * width_wspace
        width_axis = width_all_plot / ncol
        height_axis = width_axis
        height_all_plot = height_axis * nrow + (nrow-1) * height_hspace
        height = height_all_plot + height_title + height_bottem_xticsk + sup_height_title

    step = 0.02 * vmax
    grid_count = meteva.base.grid([-vmax, vmax, step], [-vmax, vmax, step])
    u1 = u_ob.flatten() + np.random.randn(len(u_ob))*add_randn_to_ob
    v1 = v_ob.flatten() + np.random.randn(len(v_ob))*add_randn_to_ob
    df = pd.DataFrame({"lon": u1, "lat": v1})
    sta_xy = meteva.base.sta_data(df)
    sta_xy["time"] = datetime.datetime(2020, 1, 1, 0)
    sta_xy["data0"] = 1
    grd_count = meteva.base.near.add_stavalue_to_nearest_grid(sta_xy, grid=grid_count)
    nsample = u_ob.size
    grd_count.values /=(nsample *step*step)
    grd_count_ob = meteva.base.smooth(grd_count,smooth_times=smooth_times)
    gx = grd_count_ob['lon'].values
    gy = grd_count_ob['lat'].values
    max_count = np.max(grd_count_ob.values)
    grid_count_fo_list = []
    for line in range(new_Fo_shape[0]):

        u2 = new_u_Fo[line, :].flatten()
        v2 = new_v_Fo[line, :].flatten()
        df = pd.DataFrame({"lon": u2, "lat": v2})
        sta_xy = meteva.base.sta_data(df)
        sta_xy["time"] = datetime.datetime(2020, 1, 1, 0)
        sta_xy["data0"] = 1
        grd_count = meteva.base.near.add_stavalue_to_nearest_grid(sta_xy, grid=grid_count)
        grd_count.values /=(nsample*step*step) #转换为概率密度
        grd_count_fo = meteva.base.smooth(grd_count, smooth_times=smooth_times)
        grid_count_fo_list.append(grd_count_fo)
        count1 = np.max(grd_count_fo.values)
        if count1 > max_count:
            max_count = count1
    cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap="turbo", clevs=None, vmin=0, vmax=max_count)
    norm = BoundaryNorm(clevs1, ncolors=cmap1.N - 1)

    mm = clevs1[-1]
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

    if member_list is None:
        member_list = []
        for line in range(new_Fo_shape[0]):
            member_list.append("预报" + str(line))



    fig = plt.figure(figsize=(width, height), dpi=dpi)
    colors = meteva.base.color_tools.get_color_list(new_Fo_shape[0]+1)

    for line in range(new_Fo_shape[0]):
        pi = line % ncol
        pj = int(line / ncol)
        rect1 = [(width_left_yticks + pi * (width_axis + width_wspace))/width,
                 (height_bottem_xticsk + (nrow -1- pj) * (height_axis + height_hspace))/height,
                 width_axis / width,
                 height_axis / height]
        ax = plt.axes(rect1)
        u2 = new_u_Fo[line, :].flatten()
        v2 = new_v_Fo[line, :].flatten()
        df = pd.DataFrame({"lon": u2, "lat": v2})
        sta_xy = meteva.base.sta_data(df)
        sta_xy["time"] = datetime.datetime(2020, 1, 1, 0)
        sta_xy["data0"] = 1
        grd_count = meteva.base.near.add_stavalue_to_nearest_grid(sta_xy, grid=grid_count)
        grd_count.values /= (nsample * step * step)  # 转换为概率密度
        grd_count_fo = meteva.base.smooth(grd_count, smooth_times=smooth_times)

        markersize = 5 * width_axis * height_axis / np.sqrt(u_ob.size)
        if markersize < 1:
            markersize = 1
        elif markersize > 20:
            markersize = 20
        #plt.subplot(nrow, ncols, line + 1)
        #plt.plot(u1,v1,'.',color= "r", markeredgewidth = 0, markersize=markersize,alpha = 0.5,label = "OBS")
        #plt.plot(u2,v2,'.',color= "b", markeredgewidth = 0,  markersize=markersize,alpha = 0.5,label = "FCT")

        im1 = plt.contour(gx, gy, np.squeeze(grd_count_ob.values),linewidths=linewidths,cmap =cmap1,norm = norm)
        ax.clabel(im1, inline=1, fontsize=label_fontsize, fmt=fmt)
        im2 = plt.contour(gx, gy, np.squeeze(grd_count_fo.values),linestyles='--',linewidths=linewidths,cmap =cmap1,norm=norm)
        ax.clabel(im2, inline=1, fontsize=label_fontsize, fmt=fmt)
        plt.xlabel(x_label,fontsize = sup_fontsize *0.9)
        plt.ylabel(y_label,fontsize = sup_fontsize *0.9)
        plt.title(member_list[line],fontsize = sup_fontsize)


        plt.xlim(-vmax,vmax)
        plt.ylim(-vmax,vmax)
        #plt.legend(loc = 2,fontsize = sup_fontsize * 0.7)
        angles = np.arange(0,360,45)
        for i in range(len(angles)):
            angle = angles[i] * 3.1415926 /180
            r = np.arange(0,vmax+1,vmax * 0.1)
            x = r * np.sin(angle)
            y = r * np.cos(angle)
            plt.plot(x,y,"--",color = "k",linewidth = 0.5)

        rs = np.arange(0,vmax+1,1)
        for i in range(len(rs)):
            r = rs[i]
            angle = np.arange(0,360) * 3.1415926 /180
            x = r * np.sin(angle)
            y = r * np.cos(angle)
            plt.plot(x,y,"--",color = "k",linewidth = 0.5)
        plt.xticks(fontsize = 0.8 * sup_fontsize)
        plt.yticks(fontsize = 0.8 * sup_fontsize)

    # left_low = (width_left_yticks + ncol * width_axis + (ncol - 1) * width_wspace + 0.1) / width
    # # print(left_low)
    # colorbar_position_grid = fig.add_axes(
    #     [left_low, height_bottem_xticsk / height, 0.02, height_all_plot / height])  # 位置[左,下,宽,高]
    #
    # colorbar_ob = plt.colorbar(im, cax=colorbar_position_grid)
    # #colorbar_ob = plt.colorbar(ax, cax=colorbar_position_grid)
    # colorbar_ob.ax.tick_params(labelsize=sup_fontsize * 0.5)  # 改变bar标签字体大小
    # colorbar_ob.set_label('风矢量概率密度', fontsize=sup_fontsize * 0.7)


    y_sup_title = (height_bottem_xticsk + (nrow) * (height_axis + height_hspace)) / height
    if title is not None:
        plt.suptitle(title, y = y_sup_title,fontsize=sup_fontsize * 1.2)

    if(save_path is not None):
        file1,extension = os.path.splitext(save_path)
        extension = extension[1:]
        plt.savefig(save_path,format = extension)
    else:
        show = True
    if show:
        plt.show()
    plt.close()


def uv_frequent_statistic(u,v,ngrade = 16,half_span = 22.5,rate = 20,smtime = 50):
    '''

    :param u: 输入的u分量列表
    :param v: 输入的v分量列表
    :param ngrade:  统计的时候对360度均匀分布的ngrade个不同角度进行统计
    :param half_span:  统计的角度范围，围绕一个中心角度两侧的扇形角度
    :param rate:  将统计结果加密成连续变化的结果，加密的比例，
    :param smtime:  对一圈统计结果进行平滑的次数
    :return:
    '''
    s1,a1 = meteva.base.tool.math_tools.u_v_to_s_d(u,v)

    step = 360 / ngrade
    ms1 = np.zeros(ngrade)
    ma1 = np.zeros(ngrade)
    mf1 = np.zeros(ngrade)
    mstd1 = np.zeros(ngrade)
    for i in range(ngrade):

        mid_angle = i * step
        d_angle = 180 - np.abs(np.abs(a1 - mid_angle) - 180)
        s2 = s1[d_angle<=half_span]
        if s2.size == 0:
            ms1[i] = 0
            mf1[i] = 0
            ma1[i] = 0
            mstd1[i] = 0.5
        else:
            ms1[i] = np.mean(s2)
            mf1[i] = len(s2)
            ma1[i] = mid_angle
            mstd1[i] = np.std(s2)

    mu1,mv1 = meteva.base.math_tools.s_d_to_u_v(ms1,ma1)

    ngrade2 = ngrade * rate
    x = np.arange(ngrade2)/ rate
    ig = x.astype(dtype='int16')
    dx = x - ig
    ig1 = ig + 1
    ii = ig % ngrade
    ii1 = ig1 % ngrade
    mu2 = mu1[ii] * (1-dx) + mu1[ii1] * dx
    mv2 = mv1[ii] * (1-dx) + mv1[ii1] * dx
    mf2 = mf1[ii] * (1-dx) + mf1[ii1] * dx
    mstd2 = mstd1[ii] * (1-dx) + mstd1[ii1] * dx


    ig = np.arange(ngrade2)
    ig1 = (ig + 1) % ngrade2
    ig_1 = (ig + ngrade2 - 1) % ngrade2
    for k in range(smtime):
        mu2 = (mu2 * 2 + mu2[ig1] + mu2[ig_1])/4
        mv2 = (mv2 * 2 + mv2[ig1] + mv2[ig_1]) / 4
        mf2 = (mf2 * 2 + mf2[ig1] + mf2[ig_1]) / 4
        mstd2 = (mstd2 * 2 + mstd2[ig1] + mstd2[ig_1]) / 4

    mf2 = 10 * (360/half_span) * (mf2/u.size)
    return mu2,mv2,mf2,mstd2



def statistic_uv(u_ob,u_fo,v_ob,v_fo,member_list = None,title = "风矢量分布统计图"
               ,vmax=None, ncol=None, save_path=None, show=False, dpi=300,
               sup_fontsize=10, width=None, height=None,x_label ="U分量",y_label = "v_分量"):


    Fo_shape = u_fo.shape
    Ob_shape = u_ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_u_Fo = u_fo.reshape(new_Fo_shape)
    new_v_Fo = v_fo.reshape(new_Fo_shape)
    new_Fo_shape = new_u_Fo.shape
    sub_plot_num = new_Fo_shape[0]


    height_title = sup_fontsize * 0.01
    height_bottem_xticsk = sup_fontsize * 0.05
    height_hspace = sup_fontsize * 0.07

    width_wspace = height_hspace

    width_colorbar = 1
    width_left_yticks = sup_fontsize * 0.1


    if ncol is None:
        if sub_plot_num ==1:
            ncol = 1
        elif sub_plot_num %2 == 0:
            ncol = 2
        else:
            ncol = 3

    if title is None:
        sup_height_title = 0
    else:
        sup_height_title = sup_fontsize * 0.12
    nrow = math.ceil(new_Fo_shape[0] / ncol)
    if width is None and height is None:
        if sub_plot_num ==1:
            width = 5
        else:
            width = 10


    if width is None:
        height_all_plot = height - height_title - height_bottem_xticsk - (nrow-1) * height_hspace + sup_height_title
        height_axis = height_all_plot / nrow
        width_axis = height_axis
        width_all_plot = width_axis * ncol + (ncol-1) * width_wspace
        width = width_all_plot + width_colorbar + width_left_yticks
    else:
        width_all_plot = width - width_colorbar - width_left_yticks - (ncol - 1) * width_wspace
        width_axis = width_all_plot / ncol
        height_axis = width_axis
        height_all_plot = height_axis * nrow + (nrow-1) * height_hspace
        height = height_all_plot + height_title + height_bottem_xticsk + sup_height_title


    fig = plt.figure(figsize=(width, height), dpi=dpi)
    #plt.subplots_adjust(hspace = 0.3,wspace = 0.30)
    u1 = u_ob.flatten()
    v1 = v_ob.flatten()


    mu1,mv1,mf1,mstd1 = uv_frequent_statistic(u1,v1)
    ms1,ma1 = meteva.base.math_tools.u_v_to_s_d(mu1,mv1)

    gray1 = ms1/(ms1+mstd1)
    cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap="autumn", vmin=0.5, vmax=1)
    norm1= BoundaryNorm(clevs1, ncolors=cmap1.N-1)

    cmap2, clevs2= meteva.base.tool.color_tools.def_cmap_clevs(cmap="winter",  vmin=0.5, vmax=1)
    norm2= BoundaryNorm(clevs2, ncolors=cmap1.N-1)

    if member_list is None:
        member_list = []
        for line in range(new_Fo_shape[0]):
            member_list.append("预报" + str(line))

    ms_list = [ms1]
    mu2_list = []
    mv2_list = []
    mf2_list = []
    mgray2_list = []
    for line in range(new_Fo_shape[0]):
        u2 = new_u_Fo[line, :].flatten()
        v2 = new_v_Fo[line, :].flatten()
        mu2, mv2, mf2, mstd2 = uv_frequent_statistic(u2, v2)
        ms2, ma2 = meteva.base.math_tools.u_v_to_s_d(mu2, mv2)
        ms_list.append(ms2)
        mu2_list.append(mu2)
        mv2_list.append(mv2)
        mf2_list.append(mf2)
        gray2 = ms2 / (ms2 + mstd2)
        mgray2_list.append(gray2)

    if vmax is None:
        vmax = np.max(np.array(ms_list)) * 1.2

    ax_ob = None
    ax_fo = None
    for line in range(new_Fo_shape[0]):
        #print(member_list[line])
        pi = line % ncol
        pj = int(line / ncol)
        rect1 = [(width_left_yticks + pi * (width_axis + width_wspace))/width,
                 (height_bottem_xticsk + (nrow -1- pj) * (height_axis + height_hspace))/height,
                 width_axis / width,
                 height_axis / height]
        ax = plt.axes(rect1)

        ax_ob = plt.scatter(mu1, mv1, c=gray1,s = mf1,cmap = cmap1,norm=norm1)
        ax_fo = plt.scatter(mu2_list[line], mv2_list[line], c=mgray2_list[line],s = mf2_list[line],cmap = cmap2,norm = norm2)

        plt.xlabel(x_label,fontsize = sup_fontsize *0.9)
        plt.ylabel(y_label,fontsize = sup_fontsize *0.9)
        plt.title(member_list[line],fontsize = sup_fontsize)

        #print(maxs)
        plt.xlim(-vmax,vmax)
        plt.ylim(-vmax,vmax)
        #plt.legend()
        angles = np.arange(0,360,45)
        for i in range(len(angles)):
            angle = angles[i] * 3.1415926 /180
            r = np.arange(0,vmax+1,vmax * 0.1)
            x = r * np.sin(angle)
            y = r * np.cos(angle)
            plt.plot(x,y,"--",color = "k",linewidth = 0.5)

        rs = np.arange(0,vmax+1,1)
        for i in range(len(rs)):
            r = rs[i]
            angle = np.arange(0,360) * 3.1415926 /180
            x = r * np.sin(angle)
            y = r * np.cos(angle)
            plt.plot(x,y,"--",color = "k",linewidth = 0.5)


    left_low = (width_left_yticks + ncol * width_axis  + (ncol-1)*width_wspace+0.1)/width
    #print(left_low)
    colorbar_position_grid = fig.add_axes([left_low, height_bottem_xticsk / height,0.02, 0.455*height_all_plot/height])  # 位置[左,下,宽,高]

    #colorbar_position_grid = fig.add_axes([0.92, 0.50, 0.02, 0.32])  # 位置[左,下,宽,高]
    colorbar_ob = plt.colorbar(ax_ob, cax=colorbar_position_grid)
    colorbar_ob.ax.tick_params(labelsize=sup_fontsize * 0.5)  # 改变bar标签字体大小

    colorbar_ob.set_label('观测风速的一致性',fontsize = sup_fontsize * 0.7)
    #colorbar_position_grid = fig.add_axes([0.92, 0.15, 0.02, 0.32])  # 位置[左,下,宽,高]
    colorbar_position_grid = fig.add_axes([left_low, (height_bottem_xticsk+0.545 * height_all_plot) / height,
                                           0.02, 0.455*height_all_plot/height])  # 位置[左,下,宽,高]


    colorbar_fo = plt.colorbar(ax_fo, cax=colorbar_position_grid)
    colorbar_fo.ax.tick_params(labelsize=sup_fontsize * 0.5)  # 改变bar标签字体大小
    colorbar_fo.set_label('预报风速的一致性',fontsize = sup_fontsize * 0.7)
    y_sup_title = (height_bottem_xticsk + (nrow) * (height_axis + height_hspace)) / height
    if title is not None:
        plt.suptitle(title, y = y_sup_title,fontsize=sup_fontsize * 1.2)
    if(save_path is not None):
        file1,extension = os.path.splitext(save_path)
        extension = extension[1:]
        plt.savefig(save_path,format = extension)
    else:
        show = True
    if show:
        plt.show()
    plt.close()

def statisitic_uv(u_ob,u_fo,v_ob,v_fo,member_list = None,title = "风矢量分布统计图"
               ,vmax=None, ncol=None, save_path=None, show=False, dpi=300,
               sup_fontsize=10, width=None, height=None):

   statistic_uv(u_ob,u_fo,v_ob,v_fo,member_list=member_list,title=title,vmax=vmax,ncol=ncol,
                save_path=save_path,show=show,dpi=dpi,sup_fontsize=sup_fontsize,width=width,height = height)

def frequent_distribution_uv():
    pass

def regress_uv():
    pass