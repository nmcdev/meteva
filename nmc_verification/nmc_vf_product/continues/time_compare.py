import numpy as np
import matplotlib.pyplot as plt
import datetime
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import seaborn as sns
import nmc_verification
import matplotlib.patches as patches
import copy
import math

def ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path = None,max_dh = None,clev = None,cmap = None,plot_error = False,cmap_error= None):
    '''
    :param sta_ob_all: 输入的观测站点数据序列，它为一个pandas数据列表，是包含一个站点的多个时刻的观测
    :param sta_fo_all: 输入的站点预报数据序列，它为一个pandas数据列表，是包含一个站点的多个时刻起报的，多个预报时效的数据
    :param max_dh:   检验图显示的最大预报时效
    :param cmap:    检验图的配色设置
    :param vmax:    检验图显示的最大取值范围，
    :param vmin:   检验图显示的最小值范围，cmap，vmax和vmin 会决定最终colorbar的样式
    :param pic_path:   检验图片输出的路径
    :return:
    '''

    #以最近的预报作为窗口中间的时刻
    times_fo = copy.deepcopy(sta_fo_all["time"].values)
    times_fo.sort()
    time_mid = nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_datetime(times_fo[-1])
    #以观预报数据的间隔的最小单位作为纵坐标的步长
    dhs_fo = (times_fo[1:] - times_fo[0:-1])
    dhs_fo = dhs_fo / np.timedelta64(1, 'h')
    dhs_fo_not0 = dhs_fo[dhs_fo!=0]
    dh_y = np.min(dhs_fo_not0)

    #以数据中最大的预报时效，确定整个窗口的横轴范围宽度
    dhs = copy.deepcopy(sta_fo_all["dtime"].values)
    dhs.sort()
    if max_dh is None:
        max_dh = int(dhs[-1])
    #以观预报时效间隔的最小单位
    ddhs = dhs[1:] - dhs[0:-1]
    ddhs = ddhs[ddhs!=0]
    dh_x = int(np.min(ddhs))

    data_name = nmc_verification.nmc_vf_base.get_undim_data_names(sta_ob_all)[0]
    sta_all = nmc_verification.nmc_vf_base.function.put_into_sta_data.join(sta_ob_all, sta_fo_all)
    col = (int)(2 * max_dh / dh_x + 1)
    hf_col = (int)(max_dh/dh_x)
    row = (int)(max_dh / dh_y)
    dat = np.ones((col, row)) * 9999

    time0 = time_mid - datetime.timedelta(hours=max_dh)
    start_ob_i = 0
    for i in range(col):
        for j in range(row):
            time_fo = time_mid - datetime.timedelta(hours=j * dh_y)
            dh = j * dh_y  + (i - hf_col) * dh_x
            if j==0 and dh == 0:
                start_ob_i = i
            if dh < dh_y and dh >0:
                time_fo = time_fo + datetime.timedelta(hours = dh)
                dh = 0
            sta = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_of_time(sta_all,time_fo)
            sta = sta.loc[sta["dtime"] == dh]
            if (len(sta.index) > 0):
                dat[i, j] = sta[data_name].values[0]
    xticks = []
    x = np.arange(col)
    for i in range(col):
        time_ob = time0 + datetime.timedelta(hours=i * dh_x)
        hour = time_ob.hour
        day = time_ob.day
        if ((i * int(dh_x)) % 12 == 0):
            str1 = str(hour) + "\n" + str(day) + "日"
        else:
            str1 = str(hour)
        xticks.append(str1)
    y = np.arange(row)
    yticks = []
    for j in range(row):
        time_fo = time_mid - datetime.timedelta(hours=j * dh_y)
        hour = time_fo.hour
        day = time_fo.day
        if ((j * int(dh_y)) % 12 == 0):
            str1 = str(day) + "日" + str(hour) + "时"
        else:
            str1 = str(hour) + "时"
        yticks.append(str1)
    mask = np.zeros_like(dat.T)
    mask[dat.T == 9999] = True

    vmin = np.min(dat[dat != 9999])
    vmax = np.max(dat[dat != 9999])

    if plot_error:
        height = 16 * row / col + 3
        f, (ax1, ax2)  = plt.subplots(figsize=(16, height*2),nrows = 2,edgecolor='black')
        plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)

        dvalue = np.zeros_like(dat)
        for i in range(col):
            top_value = 9999
            for j in range(row):
                if dat[i, j] != 9999:
                    top_value = dat[i, j]
                    break
            for j in range(row):
                if dat[i, j] != 9999:
                    dvalue[i, j] = dat[i, j] - top_value

        maxd = np.max(np.abs(dvalue))
        if(maxd >10):
            fmt_str = ".0f"
        else:
            fmt_str = ".1f"
        if cmap_error is None:
            cmap_error = "bwr"
        sns.heatmap(dvalue.T, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd, center=None, robust=False, annot=True,
                    fmt=fmt_str)

        ax1.set_xlabel('实况时间')
        ax1.set_ylabel('起报时间')
        ax1.set_xticks(x+0.5)
        ax1.set_xticklabels(xticks)
        ax1.set_yticklabels(yticks, rotation=360)
        title = data_name + '实况和不同时效预报偏差图'
        ax1.set_title(title, loc='left', fontweight='bold', fontsize='large')
    else:
        height = 16 * row / col + 2
        f, ax2 = plt.subplots(figsize=(16, height), nrows=1, edgecolor='black')
        plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)


    if cmap is None:
        cmap = plt.get_cmap("rainbow")
        cmap_part = cmap
    if clev is not None:
        clev_part,cmap_part = nmc_verification.nmc_vf_base.tool.color_tools.get_part_clev_and_cmap(clev,cmap,vmax,vmin)
        vmax = clev_part[-1]
        vmin = 2 * clev_part[0] - clev_part[1]
    sns.heatmap(dat.T, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax, center=None, robust=False, annot=True,fmt='.0f')
    ax2.set_xlabel('实况时间')
    ax2.set_ylabel('起报时间')
    ax2.set_xticks(x+0.5)
    ax2.set_xticklabels(xticks)
    ax2.set_yticklabels(yticks, rotation=360)
    title = data_name + '实况和不同时效预报对比图'
    ax2.set_title(title, loc='left', fontweight='bold', fontsize='large')

    currentAxis = plt.gca()
    for k in range(row+1):
        x1 = start_ob_i - k * dh_y/dh_x
        y1 = k
        rect = patches.Rectangle((x1, y1), dh_y/dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
        currentAxis.add_patch(rect)

    nmc_verification.nmc_vf_base.tool.path_tools.creat_path(pic_path)
    plt.savefig(pic_path)
    return

def temp_ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path = None,max_dh = None,plot_error = True):
    clev, cmap= nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("temp")
    ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path,max_dh,clev,cmap,plot_error,cmap_error= "bwr")

def rain01h_ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path = None,max_dh = None,plot_error = True):
    clev, cmap= nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_1h")
    clev_error, cmap_error = nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_1h_error")
    ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path,max_dh,clev,cmap,plot_error,cmap_error= cmap_error)

def rain03h_ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path = None,max_dh = None,plot_error = True):
    clev, cmap= nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_3h")
    clev_error, cmap_error = nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_3h_error")
    ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path,max_dh,clev,cmap,plot_error,cmap_error= cmap_error)

def rh_ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path = None,max_dh = None,plot_error = True):
    clev, cmap= nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("rh")
    clev_error, cmap_error = nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("rh_error")
    ob_and_multi_time_fo(sta_ob_all, sta_fo_all, pic_path, max_dh, clev, cmap, plot_error, cmap_error=cmap_error)

def vis_ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path = None,max_dh = None,plot_error = True):
    clev, cmap= nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("vis")
    clev_error,cmap_error = nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("vis_error")
    ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path,max_dh,clev,cmap,plot_error,cmap_error= cmap_error)

def tcdc_ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path = None,max_dh = None,plot_error = True):
    clev, cmap= nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("tcdc")
    clev_error, cmap_error = nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name(
        "tcdc_error")
    ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path,max_dh,clev,cmap,plot_error,cmap_error= cmap_error)


def wind_ob_and_multi_time_fo(sta_ob_all,sta_fo_all,pic_path = None,max_dh = None,plot_error = True):


    #以最近的预报作为窗口中间的时刻
    times_fo = copy.deepcopy(sta_fo_all["time"].values)
    times_fo.sort()
    time_mid = nmc_verification.nmc_vf_base.tool.time_tools.all_type_time_to_datetime(times_fo[-1])
    #以观预报数据的间隔的最小单位作为纵坐标的步长
    dhs_fo = (times_fo[1:] - times_fo[0:-1])
    dhs_fo = dhs_fo / np.timedelta64(1, 'h')
    dhs_fo_not0 = dhs_fo[dhs_fo!=0]
    dh_y = np.min(dhs_fo_not0)

    #以数据中最大的预报时效，确定整个窗口的横轴范围宽度
    dhs = copy.deepcopy(sta_fo_all["dtime"].values)
    dhs.sort()
    if max_dh is None:
        max_dh = int(dhs[-1])
    #以观预报时效间隔的最小单位
    ddhs = dhs[1:] - dhs[0:-1]
    ddhs = ddhs[ddhs!=0]
    dh_x = int(np.min(ddhs))


    data_names = nmc_verification.nmc_vf_base.get_undim_data_names(sta_ob_all)
    title = data_names[0][1:]
    sta_all = nmc_verification.nmc_vf_base.function.put_into_sta_data.join(sta_ob_all, sta_fo_all)
    col = (int)(2 * max_dh / dh_x + 1)
    hf_col = (int)(max_dh/dh_x)
    row = (int)(max_dh / dh_y)
    dat_u = np.ones((row,col)) * 9999
    dat_v = np.ones(dat_u.shape)* 9999
    dat_speed = np.ones(dat_u.shape)*9999

    time0 = time_mid - datetime.timedelta(hours=max_dh)
    start_ob_i = 0

    for i in range(col):
        for j in range(row):
            time_fo = time_mid - datetime.timedelta(hours=j * dh_y)
            dh = j * dh_y  + (i - hf_col) * dh_x
            if j==0 and dh == 0:
                start_ob_i = i
            if dh < dh_y and dh >0:
                time_fo = time_fo + datetime.timedelta(hours = dh)
                dh = 0
            sta = sta_all.loc[sta_all["time"] == time_fo]
            sta = sta.loc[sta["dtime"] == dh]
            if (len(sta.index) > 0):
                dat_u[j,i] = sta[data_names[0]].values[0]
                dat_v[j,i] = sta[data_names[1]].values[0]
                dat_speed[j,i] = math.sqrt(dat_u[j,i] **2 + dat_v[j,i] **2)
    xticks = []
    x = np.arange(col)
    for i in range(col):
        time_ob = time0 + datetime.timedelta(hours=i * dh_x)
        hour = time_ob.hour
        day = time_ob.day
        if ((i * int(dh_x)) % 12 == 0):
            str1 = str(hour) + "\n" + str(day) + "日"
        else:
            str1 = str(hour)
        xticks.append(str1)
    y = np.arange(row)
    yticks = []
    for j in range(row):
        time_fo = time_mid - datetime.timedelta(hours=j * dh_y)
        hour = time_fo.hour
        day = time_fo.day
        if ((j * int(dh_y)) % 12 == 0):
            str1 = str(day) + "日" + str(hour) + "时"
        else:
            str1 = str(hour) + "时"
        yticks.append(str1)
    mask = np.zeros_like(dat_speed)
    mask[dat_speed == 9999] = True

    if plot_error:
        height = 16 * row / col + 3
        f, (ax1, ax2)  = plt.subplots(figsize=(16, height*2),nrows = 2,edgecolor='black')
        plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)

        diff_speed = np.zeros_like(dat_speed)
        diff_u = np.zeros_like(dat_u)
        diff_v = np.zeros_like(dat_v)

        #"风速误差"
        for i in range(col):
            top_value = 9999
            for j in range(row):
                if dat_speed[j,i] != 9999:
                    top_value = dat_speed[j,i]
                    break
            for j in range(row):
                if dat_speed[j,i] != 9999:
                    diff_speed[j,i] = dat_speed[j,i] - top_value
        #u 分量误差
        for i in range(col):
            top_value = 9999
            for j in range(row):
                if dat_u[j,i] != 9999:
                    top_value = dat_u[j,i]
                    break
            for j in range(row):
                if dat_u[j,i] != 9999:
                    diff_u[j,i] = dat_u[j,i] - top_value
        #v 分量误差
        for i in range(col):
            top_value = 9999
            for j in range(row):
                if dat_v[j,i] != 9999:
                    top_value = dat_v[j,i]
                    break
            for j in range(row):
                if dat_v[j,i] != 9999:
                    diff_v[j,i] = dat_v[j,i] - top_value

        maxd = np.max(np.abs(diff_speed))
        clev, cmap_error = nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("wind_speed_error")

        sns.heatmap(dat_speed, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd)
        #sns.heatmap(dvalue.T, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd, center=None, robust=False, annot=True,
        #            fmt=fmt_str)
        ax1.set_xlabel('实况时间')
        ax1.set_ylabel('起报时间')
        ax1.set_xticks(x + 0.5)
        ax1.set_xticklabels(xticks)
        ax1.set_yticklabels(yticks, rotation=360)
        title = title + '实况和不同时效预报偏差图'
        ax1.set_title(title, loc='left', fontweight='bold', fontsize='large')
        xx, yy = np.meshgrid(x + 0.5, y + 0.5)
        speed_1d = dat_speed.flatten()
        xx_1d = xx.flatten()[speed_1d != 9999]
        yy_1d = yy.flatten()[speed_1d != 9999]
        u_1d = diff_u.flatten()[speed_1d != 9999]
        v_1d = diff_v.flatten()[speed_1d != 9999]
        ax1.barbs(xx_1d, yy_1d, u_1d, v_1d, barb_increments={'half': 2, 'full': 4, 'flag': 20})

        currentAxis = plt.gca()
        for k in range(row + 1):
            x_1 = start_ob_i - k * dh_y / dh_x
            y_1 = k
            rect = patches.Rectangle((x_1, y_1), dh_y / dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
            currentAxis.add_patch(rect)


    else:
        height = 16 * row / col + 2
        f, ax2 = plt.subplots(figsize=(16, height), nrows=1, edgecolor='black')
        plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)

    vmin = np.min(dat_speed[dat_speed != 9999])
    vmax = np.max(dat_speed[dat_speed != 9999])
    clev, cmap = nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("wind_speed")
    clev_part,cmap_part = nmc_verification.nmc_vf_base.tool.color_tools.get_part_clev_and_cmap(clev,cmap,vmax,vmin)
    vmax = clev_part[-1]
    vmin = 2 * clev_part[0] - clev_part[1]

    sns.heatmap(dat_speed, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax)
    ax2.set_xlabel('实况时间')
    ax2.set_ylabel('起报时间')
    ax2.set_xticks(x+0.5)
    ax2.set_xticklabels(xticks)
    ax2.set_yticklabels(yticks, rotation=360)
    title = title + '实况和不同时效预报对比图'
    ax2.set_title(title, loc='left', fontweight='bold', fontsize='large')
    xx,yy = np.meshgrid(x+0.5,y+0.5)
    speed_1d = dat_speed.flatten()
    xx_1d = xx.flatten()[speed_1d !=9999]
    yy_1d = yy.flatten()[speed_1d !=9999]
    u_1d = dat_u.flatten()[speed_1d !=9999]
    v_1d = dat_v.flatten()[speed_1d !=9999]
    ax2.barbs(xx_1d, yy_1d,u_1d,v_1d, barb_increments={'half': 2, 'full': 4, 'flag': 20})

    currentAxis = plt.gca()
    for k in range(row+1):
        x = start_ob_i - k * dh_y/dh_x
        y = k
        rect = patches.Rectangle((x, y), dh_y/dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
        currentAxis.add_patch(rect)

    nmc_verification.nmc_vf_base.tool.path_tools.creat_path(pic_path)
    plt.savefig(pic_path)
    return

