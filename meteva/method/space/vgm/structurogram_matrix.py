# -*- coding: utf-8 -*-
"""
Created on Fri Jan 22 17:52:38 2021

@author: 1
"""
import numpy as np
import pandas as pd
import meteva
import matplotlib.pyplot as plt
import math


def structurogram_matrix(grd_list, delta = 10, step = 1, q = 1):


    if not isinstance(grd_list,list):
        grd_list = meteva.base.split_grd(grd_list,used_coords=["member"])
    if not isinstance(grd_list,list):
        grd_list = [grd_list]

    names = []
    for grd in grd_list:
        names.append(grd['member'].values[0])

    grid0 = meteva.base.get_grid_of_data(grd_list[0])
    nmin = min(grid0.nlon,grid0.nlat)
    if delta > nmin/2:
        delta = int(nmin/2)

    nv = len(grd_list)



    rx = delta+ delta%step
    delta_y = np.arange(-rx,rx+1,step)
    delta_x = np.arange(-rx,rx+1,step)

    #自定义SI函数
    def SI(ntemp, delta):
        n1 = np.arange(ntemp)
        n2 = n1 + delta
        good = (n2 >= 0) & (n2 < ntemp)
        return np.vstack((n1[good], n2[good])).T

    vg = np.zeros((nv,len(delta_x),len(delta_y)))
    sample =np.zeros((nv,len(delta_x),len(delta_y)))
    dis  =np.zeros((nv,len(delta_x),len(delta_y)))
    for m in range(nv):
        dat = grd_list[m].values.squeeze()
        dat[dat == meteva.base.IV] = np.nan
        for i in range(len(delta_x)):
            for j in range(len(delta_y)):
                MM = SI(ntemp=grid0.nlat, delta=delta_y[j])
                NN = SI(ntemp=grid0.nlon, delta=delta_x[i])

                i0 = MM[:, 0].astype(int)
                j0 = NN[:, 0].astype(int)
                ii, jj = np.meshgrid(i0, j0)
                dat_1 = dat[ii, jj].T
                i1 = MM[:, 1].astype(int)
                j1= NN[:, 1].astype(int)
                ii, jj = np.meshgrid(i1, j1)
                dat_2 = dat[ii, jj].T

                dis[m,i,j] = (delta_y[j]**2 + delta_x[i]**2)**0.5
                index = np.where(np.isnan(dat_1) | np.isnan(dat_1))
                sample[m,i,j]= dat_2.size - len(index[0])
                BigDiff = dat_1 - dat_2
                if q ==1:
                    vg[m,i,j] = np.nanmean(np.abs(BigDiff))
                else:
                    vg[m,i,j] = np.nanmean(BigDiff ** q)


    out = {"dis":dis,"vg":vg,  "sample":sample,"member":names,"delta_x":delta_x.tolist(),"delta_y":delta_y.tolist()}
    return out


def vgm_grd_mesh(grd_list, delta,step = 1, q = 1,
                  dpi = 300,show =False,save_path = None,sup_fontsize  = 10,ncol = 2,width = None,height = None,):

    out = structurogram_matrix(grd_list,delta=delta,step = step,q=q)
    mesh_dict = {"member":out["member"],"东西向平移网格数":out["delta_x"],"南北向平移网格数":out["delta_y"]}
    meteva.base.plot_tools.mesh(out["vg"],mesh_dict,axis_x="东西向平移网格数",axis_y="南北向平移网格数",width=width,
                                height=height,dpi = dpi,show=show,save_path=save_path,sup_fontsize=sup_fontsize,ncol=ncol)
    return out

def out_statistic(out,step):
    '''
    从变率样本矩阵中，统计出每一段距离范围内，平均的变率，以及变率值本身的方差
    :param dv_array:
    :param dmax:
    :param grade_count:
    :return:
    '''

    dmax = np.max(out["dis"][0])
    v_count = out["vg"].shape[0]
    grade_count = int(math.ceil(dmax/step))
    dmax = grade_count * step
    # c：count, m ：mean， v :var
    cmv_array = np.zeros((3, grade_count, v_count))


    for i in range(grade_count):
        index = np.where((out["dis"][0] > i * step) & (out["dis"][0] <= (i + 1) * step))
        for j in range(v_count):
            sample = out["sample"][j][index]
            vg = out["vg"][j][index]
            count = len(sample)
            if count > 0:
                cmv_array[0, i, j] = count
                cmv_array[1, i, j] = np.mean(vg)
                cmv_array[2, i, j] = np.var(vg)

    # 返回dmax，是方便后续程序确切了解组成采用dmax参数值
    return cmv_array, dmax


def plot_dv_statistic(cmv_array,dmax,member_list = None,width = None,height = None,xlabel = "距离（网格数）",ylabel = "变化幅度",
                      dpi = 300,show =False,save_path = None,sup_fontsize = 12):
    '''
    绘制变率统计结果
    :param cmv_array:
    :param dmax:
    :param member_list:
    :param width:
    :param height:
    :param xlabel:
    :param ylabel:
    :param dpi:
    :param show:
    :param save_path:
    :param sup_fontsize:
    :return:
    '''
    if height is None:
        height = 3

    grade_count = cmv_array.shape[-2]
    grade = dmax / grade_count

    grade_list = (grade * (np.arange(grade_count)+1)).astype(np.int16)
    grade_list_mid = (grade * (np.arange(grade_count)+0.5)).astype(np.int16)
    if width is None:
        width = meteva.base.tool.plot_tools.caculate_axis_width(grade_list,sup_fontsize*1.5,legend_num=1)
    fig = plt.figure(figsize=(width, height),dpi = dpi)

    v_count = cmv_array.shape[-1]
    label = []
    if member_list is None:

        label = ["观测"]
        for i in range(1,v_count):
            label.append('预报' + str(i))
    else:
        label.extend(member_list)

    color_list =meteva.base.color_tools.get_color_list(v_count)

    grid_plt = plt.GridSpec(5, 1, hspace=0)
    ax1 = plt.subplot(grid_plt[0:4, 0])
    plt.yticks(fontsize = sup_fontsize * 0.8)
    plt.ylabel(ylabel,fontsize = sup_fontsize * 0.9)
    max_list =[]
    for v in range(v_count):
        plt.plot(grade_list_mid,cmv_array[1,:,v],c = color_list[v],label= label[v])
        var = np.sqrt(cmv_array[2,:,v])
        plt.plot(grade_list_mid,cmv_array[1,:,v] - var,"--",c = color_list[v],linewidth =0.5)
        max_list.append(np.max(cmv_array[1,:,v] + var))
        plt.plot(grade_list_mid,cmv_array[1,:,v] + var,"--",c = color_list[v],linewidth =0.5)


    plt.xlim(0,grade_list[-1])
    maxv = np.max(np.array(max_list))
    plt.ylim(0,maxv*1.2)
    plt.legend(loc =2,ncol = 4,fontsize = sup_fontsize * 0.8)
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax2 = plt.subplot(grid_plt[4, 0], sharex=ax1)
    plt.yticks(fontsize=sup_fontsize * 0.8)
    plt.ylabel("样本数",fontsize = sup_fontsize * 0.9)
    plt.xlim(0,grade_list[-1])
    plt.xlabel(xlabel,fontsize = sup_fontsize * 0.9)
    plt.bar(grade_list_mid, cmv_array[0,:,0], width=grade * 0.5,color = "grey")
    #plt.xlabel(xlabel=grade_list)

    plt.xticks(grade_list,fontsize = sup_fontsize * 0.8)
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path,bbox_inches='tight')
        print("检验结果已以图片形式保存至" + save_path)
    if show is True:
        plt.show()
    plt.close()


def vgm_grd(grd_list, delta,step = 1, q = 1,
                  dpi = 300,show =False,save_path = None,sup_fontsize  = 10,width = None,height = None):

    out = structurogram_matrix(grd_list,delta=delta,step=step,q=q)

    cmv_array,dmax = out_statistic(out,step=step)

    plot_dv_statistic(cmv_array,dmax,member_list=out["member"]
                      ,width=width,height = height,dpi = dpi,show=show,save_path =save_path,sup_fontsize=sup_fontsize)
    return cmv_array




    
if __name__ == "__main__":
    #dat = pd.read_csv("F:\\Work\\MODE\\tra_test\\FeatureFinder\\pert000.csv")

    filename_ob = r'H:\test_data\input\mem\mode\ob\rain03\20070111.000.nc'
    grd = meteva.base.read_griddata_from_nc(filename_ob)
    dat = grd.values.squeeze()
    look_SGM = vgm_grd_mesh(grd)    #读入的是dataframe数据，有行列名称
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    