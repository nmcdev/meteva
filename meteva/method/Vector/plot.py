import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import math
import numpy as np
import meteva
from matplotlib.colors import BoundaryNorm


def scatter_uv_error(u_ob,u_fo,v_ob,v_fo,member_list = None,title = "风矢量误差散点分布图"
              , vmax=None, ncol=None, save_path=None, show=False, dpi=300,
               sup_fontsize=10, width=None, height=None):


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
        print('实况数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_u_Fo = u_fo.reshape(new_Fo_shape)
    new_v_Fo = v_fo.reshape(new_Fo_shape)
    new_Fo_shape = new_u_Fo.shape
    sub_plot_num = new_Fo_shape[0]

    if ncol is None:
        if sub_plot_num ==1:
            ncols = 1
        elif sub_plot_num %2 == 0:
            ncols = 2
        else:
            ncols = 3
    else:
        ncols = ncol

    nrows = math.ceil(new_Fo_shape[0] / ncols)

    if height is None:
        if nrows==1:
            if ncols <3:
                height_fig = 3.5
            else:
                height_fig = 2.5
        else:
            if ncols > nrows:
                height_fig = 6
            else:
                height_fig = 7
    else:
        height_fig = height

    height_suptitle = 0.1
    height_xticks_title = 0.1
    height_hspace = 0.6
    heidht_axis = (height_fig - height_suptitle - height_xticks_title - height_hspace * (nrows - 1)) / nrows
    width_axis = heidht_axis
    width_yticks = 0.15
    width_wspace = width_yticks * 5
    if width is None:
        width_fig = width_axis * ncols + width_wspace * (ncols - 1) + width_yticks
    else:
        width_fig = width

    fig = plt.figure(figsize=(width_fig,height_fig),dpi = dpi)
    u1 = u_ob.flatten()
    v1 = v_ob.flatten()

    if member_list is None:
        member_list = []
        for line in range(new_Fo_shape[0]):
            member_list.append("预报" + str(line))

    colors = meteva.base.color_tools.get_color_list(new_Fo_shape[0]+1)

    for line in range(new_Fo_shape[0]):
        u2 = new_u_Fo[line, :].flatten()
        v2 = new_v_Fo[line, :].flatten()
        markersize = 5 * width_axis * heidht_axis / np.sqrt(u_ob.size)
        if markersize < 1:
            markersize = 1
        elif markersize > 20:
            markersize = 20
        plt.subplot(nrows, ncols, line + 1)


        plt.plot(u2-u1,v2-v1,'.',color = colors[line+1], markersize=markersize)
        #plt.plot(u1,v1,'.',color= 'b',  markersize=markersize)
        plt.xlabel("U分量",fontsize = sup_fontsize *0.9)
        plt.ylabel("V分量",fontsize = sup_fontsize *0.9)
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

    titlelines = title.split("\n")
    fig.suptitle(title, fontsize=sup_fontsize, y=0.99+0.01 * len(titlelines))
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
               sup_fontsize=10, width=None, height=None,add_randn_to_ob = 0.0):


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
        print('实况数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_u_Fo = u_fo.reshape(new_Fo_shape)
    new_v_Fo = v_fo.reshape(new_Fo_shape)
    new_Fo_shape = new_u_Fo.shape
    sub_plot_num = new_Fo_shape[0]

    if ncol is None:
        if sub_plot_num ==1:
            ncols = 1
        elif sub_plot_num %2 == 0:
            ncols = 2
        else:
            ncols = 3
    else:
        ncols = ncol

    nrows = math.ceil(new_Fo_shape[0] / ncols)

    if height is None:
        if nrows==1:
            if ncols <3:
                height_fig = 3.5
            else:
                height_fig = 2.5
        else:
            if ncols > nrows:
                height_fig = 6
            else:
                height_fig = 7
    else:
        height_fig = height

    height_suptitle = 0.1
    height_xticks_title = 0.1
    height_hspace = 0.6
    heidht_axis = (height_fig - height_suptitle - height_xticks_title - height_hspace * (nrows - 1)) / nrows
    width_axis = heidht_axis
    width_yticks = 0.15
    width_wspace = width_yticks * 5
    if width is None:
        width_fig = width_axis * ncols + width_wspace * (ncols - 1) + width_yticks
    else:
        width_fig = width

    fig = plt.figure(figsize=(width_fig,height_fig),dpi = dpi)
    u1 = u_ob.flatten() + np.random.randn(len(u_ob))*add_randn_to_ob
    v1 = v_ob.flatten() + np.random.randn(len(v_ob))*add_randn_to_ob


    if member_list is None:
        member_list = []
        for line in range(new_Fo_shape[0]):
            member_list.append("预报" + str(line))

    colors = meteva.base.color_tools.get_color_list(new_Fo_shape[0]+1)
    for line in range(new_Fo_shape[0]):
        u2 = new_u_Fo[line, :].flatten()
        v2 = new_v_Fo[line, :].flatten()
        markersize = 15 * width_axis * heidht_axis / np.sqrt(u_ob.size)
        if markersize < 1:
            markersize = 1
        elif markersize > 20:
            markersize = 20
        plt.subplot(nrows, ncols, line + 1)
        plt.plot(u1,v1,'.',color= "r", markeredgewidth = 0, markersize=markersize,alpha = 0.5,label = "ob")
        plt.plot(u2,v2,'.',color= "b", markeredgewidth = 0,  markersize=markersize,alpha = 0.5,label = "fo")

        plt.xlabel("U分量",fontsize = sup_fontsize *0.9)
        plt.ylabel("V分量",fontsize = sup_fontsize *0.9)
        plt.title(member_list[line],fontsize = sup_fontsize)

        #print(maxs)
        plt.xlim(-vmax,vmax)
        plt.ylim(-vmax,vmax)
        plt.legend()
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

    titlelines = title.split("\n")
    fig.suptitle(title, fontsize=sup_fontsize, y=0.99+0.01 * len(titlelines))
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

def statisitic_uv(u_ob,u_fo,v_ob,v_fo,member_list = None,title = "风矢量分布统计图"
               ,vmax=None, ncol=None, save_path=None, show=False, dpi=300,
               sup_fontsize=10, width=None, height=None):


    Fo_shape = u_fo.shape
    Ob_shape = u_ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_u_Fo = u_fo.reshape(new_Fo_shape)
    new_v_Fo = v_fo.reshape(new_Fo_shape)
    new_Fo_shape = new_u_Fo.shape
    sub_plot_num = new_Fo_shape[0]

    if ncol is None:
        if sub_plot_num ==1:
            ncols = 1
        elif sub_plot_num %2 == 0:
            ncols = 2
        else:
            ncols = 3
    else:
        ncols = ncol

    nrows = math.ceil(new_Fo_shape[0] / ncols)

    if height is None:
        if nrows==1:
            if ncols <3:
                height_fig = 3.5
            else:
                height_fig = 2.5
        else:
            if ncols > nrows:
                height_fig = 6
            else:
                height_fig = 7
    else:
        height_fig = height

    height_suptitle = 0.1
    height_xticks_title = 0.1
    height_hspace = 0.6
    heidht_axis = (height_fig - height_suptitle - height_xticks_title - height_hspace * (nrows - 1)) / nrows
    width_axis = heidht_axis
    width_yticks = 0.15
    width_wspace = width_yticks * 5
    if width is None:
        width_fig = width_axis * ncols + width_wspace * (ncols - 1) + width_yticks
    else:
        width_fig = width

    fig = plt.figure(figsize=(width_fig,height_fig),dpi = dpi)
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


    for line in range(new_Fo_shape[0]):
        plt.subplot(nrows, ncols, line + 1)
        ax_ob = plt.scatter(mu1, mv1, c=gray1,s = mf1,cmap = cmap1,norm=norm1)
        ax_fo = plt.scatter(mu2_list[line], mv2_list[line], c=mgray2_list[line],s = mf2_list[line],cmap = cmap2,norm = norm2)

        plt.xlabel("U分量",fontsize = sup_fontsize *0.9)
        plt.ylabel("V分量",fontsize = sup_fontsize *0.9)
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

    colorbar_position_grid = fig.add_axes([0.12, -0.05, 0.35, 0.03])  # 位置[左,下,宽,高]
    colorbar_ob = plt.colorbar(ax_ob, cax=colorbar_position_grid, orientation='horizontal')
    colorbar_ob.set_label('指定角度上观测风速的一致性')
    colorbar_position_grid = fig.add_axes([0.55, -0.05, 0.35, 0.03])  # 位置[左,下,宽,高]
    colorbar_fo = plt.colorbar(ax_fo, cax=colorbar_position_grid, orientation='horizontal')
    colorbar_fo.set_label('指定角度上预报风速的一致性')
    titlelines = title.split("\n")
    fig.suptitle(title, fontsize=sup_fontsize, y=0.99+0.01 * len(titlelines))
    if(save_path is not None):
        file1,extension = os.path.splitext(save_path)
        extension = extension[1:]
        plt.savefig(save_path,format = extension)
    else:
        show = True
    if show:
        plt.show()
    plt.close()


def frequent_distribution_uv():
    pass

def regress_uv():
    pass