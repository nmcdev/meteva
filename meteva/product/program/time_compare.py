import numpy as np
import matplotlib.pyplot as plt
import datetime
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签\
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import seaborn as sns
import meteva
import matplotlib.patches as patches
import copy
import math
import pandas as pd

def time_list_line_error(sta_ob_and_fos0,s = None,save_dir = None,show = False,title = "不同起报时间预报误差图"):
    pass

def time_list_line(sta_ob_and_fos0,s = None,save_dir = None,show = False,title = "观测和不同起报时间预报对比图"):

    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    ids = list(set(sta_ob_and_fos1.loc[:,"id"]))
    for id in ids:
        sta_ob_and_fos = meteva.base.in_id_list(sta_ob_and_fos1,[id])
        times_fo = sta_ob_and_fos.loc[:, "time"].values
        times_fo = list(set(times_fo))
        times_fo.sort()
        times_fo = np.array(times_fo)
        dhs_fo = (times_fo[1:] - times_fo[0:-1])
        if isinstance(dhs_fo[0], np.timedelta64):
            dhs_fo = dhs_fo / np.timedelta64(1, 'h')
        else:
            dhs_fo = dhs_fo / datetime.timedelta(hours=1)
        dhs_fo_not0 = dhs_fo[dhs_fo != 0]
        dh_y = np.min(dhs_fo_not0)

        dhs = list(set(sta_ob_and_fos.loc[:, "dtime"].values))
        dhs.sort()
        dhs = np.array(dhs)
        # 以观预报时效间隔的最小单位
        ddhs = dhs[1:] - dhs[0:-1]
        dh_x = int(np.min(ddhs))

        width = len(dhs) * 2
        height = len(times_fo) * 1.5
        #print(width)
        if height > 12:
            height = 12
        if width > 18:
            width = 18
        fig = plt.figure(figsize=(width, height))
        grid_plt = plt.GridSpec(len(times_fo), 1, hspace=0)

        time_f0 = times_fo[0]
        data_names = meteva.base.get_stadata_names(sta_ob_and_fos)
        vmax = np.max(sta_ob_and_fos.values[:, 6:])
        vmin = np.min(sta_ob_and_fos.values[:, 6:]) - 0.1
        vmax = (vmax - vmin) * 1.2 + vmin


        dtimes = sta_ob_and_fos["dtime"] * np.timedelta64(1, 'h')
        obtimes = sta_ob_and_fos['time'] + dtimes
        obtimes[-1] = times_fo[0]
        time_all = list(set(obtimes))
        time_all.sort()
        #print(time_all)
        dtime_all = pd.Series(time_all) - times_fo[0]
        x_all = dtime_all/np.timedelta64(1, 'h')
        x_all = x_all.values
        #print(x_all)
        dx_all = x_all[1:] - x_all[:-1]
        dx_all = dx_all[dx_all!=0]
        mindx_all = np.min(dx_all)
        step0 = int(len(x_all) / 30) + 1
        step1 = int(24/(mindx_all*step0))
        if step1 > 0:
            step = int(24/step1/mindx_all)
        else:
            step = step0
        x_plot = x_all[::step]
        time_plot = time_all[::step]
        time_strs = meteva.product.program.get_time_str_list(time_plot, row=2)
        time_strs_null = []
        for i in range(len(time_strs)):
            time_strs_null.append("")

        for i in range(len(times_fo)):
            ax = plt.subplot(grid_plt[i:i + 1, 0])
            time_f1 = times_fo[-i - 1]
            dhour0 = (time_f1 - time_f0) / np.timedelta64(1, 'h')
            sta = meteva.base.in_time_list(sta_ob_and_fos, [time_f1])
            sta = sta.sort_values("dtime")
            x = dhour0 + sta.loc[:, "dtime"].values
            for name in data_names:
                value = sta.loc[:, name].values
                plt.plot(x, value, label=name,marker = ".")
                plt.ylim(vmin, vmax)
                plt.xlim(x_all[0],x_all[-1])
                plt.grid(linestyle='-.')

            time_f1 = meteva.base.tool.time_tools.all_type_time_to_datetime(time_f1)
            time_str = time_f1.strftime('%d{d}%H{h}').format(d='日', h='时')+"        "
            plt.ylabel(time_str, rotation='horizontal')
            if i ==0:
                plt.legend(loc="upper left", ncol=len(data_names),fontsize = 16)
                s1 = s
                if s1 is None:
                    s1 = {}
                    s1["id"] = id
                title1 = meteva.product.program.get_title_from_dict(meteva.product.time_list_line, s1, None, None,
                                                                    None)
                title1 = title1.replace("\n","")
                plt.title(title1)
            if i == len(times_fo) - 1:
                plt.xticks(x_plot, time_strs)
            else:
                plt.xticks(x_plot,time_strs_null)

        if save_dir is None:
            show = True
        else:
            save_path = save_dir + str(id) + ".png"
            meteva.base.tool.path_tools.creat_path(save_path)
            plt.savefig(save_path)
            print("图片已保存至" + save_path)
        if show:
            plt.show()
        plt.close()


def time_list_mesh(sta_ob_all0,sta_fo_all0,s = None,save_dir = None,
                   clev = None,cmap = None,plot_error = True,cmap_error= None,show = False,title = "预报准确性和稳定性对比图"):
    '''
    :param sta_ob_all: 输入的观测站点数据序列，它为一个pandas数据列表，是包含一个站点的多个时刻的观测
    :param sta_fo_all: 输入的站点预报数据序列，它为一个pandas数据列表，是包含一个站点的多个时刻起报的，多个预报时效的数据
    :param max_dh:   检验图显示的最大预报时效
    :param cmap:    检验图的配色设置
    :param vmax:    检验图显示的最大取值范围，
    :param vmin:   检验图显示的最小值范围，cmap，vmax和vmin 会决定最终colorbar的样式
    :param save_path:   检验图片输出的路径
    :return:
    '''

    sta_fo_all1 = meteva.base.sele_by_dict(sta_fo_all0, s)
    ids_fos = list(set(sta_fo_all1.loc[:,"id"]))
    ids_obs = list(set(sta_ob_all0.loc[:,"id"]))
    for id in ids_obs:
        if id not in ids_fos:continue
        sta_ob_all2 = meteva.base.in_id_list(sta_ob_all0,[id])
        data_names = meteva.base.get_stadata_names(sta_fo_all1)
        sta_fo_all1_1 = meteva.base.in_id_list(sta_fo_all1,[id])
        for data_name in data_names:
            #以最近的预报作为窗口中间的时刻
            sta_fo_all2 = meteva.base.in_member_list(sta_fo_all1_1,[data_name])
            times_fo = sta_fo_all2.loc[:,"time"].values
            times_fo = list(set(times_fo))
            if(len(times_fo)==1):
                print("仅有单个起报时间的预报，程序退出")
                return
            times_fo.sort()
            times_fo = np.array(times_fo)
            time_mid = meteva.base.tool.time_tools.all_type_time_to_datetime(times_fo[-1])
            #以观预报数据的间隔的最小单位作为纵坐标的步长
            dhs_fo = (times_fo[1:] - times_fo[0:-1])
            if isinstance(dhs_fo[0],np.timedelta64):
                dhs_fo = dhs_fo / np.timedelta64(1, 'h')
            else:
                dhs_fo = dhs_fo / datetime.timedelta(hours=1)
            dhs_fo_not0 = dhs_fo[dhs_fo!=0]

            dh_y = np.min(dhs_fo_not0)

            #以数据中最大的预报时效，确定整个窗口的横轴范围宽度
            dhs = copy.deepcopy(sta_fo_all2["dtime"].values)
            dhs.sort()
            max_dh = int(dhs[-1])
            #以观预报时效间隔的最小单位
            ddhs = dhs[1:] - dhs[0:-1]

            ddhs = ddhs[ddhs!=0]
            dh_x = int(np.min(ddhs))

            data_name = meteva.base.get_undim_data_names(sta_fo_all2)[0]
            sta_ob_all3 = copy.deepcopy(sta_ob_all2)
            meteva.base.set_stadata_names(sta_ob_all3,[data_name])
            sta_all = meteva.base.combine_join(sta_ob_all3, sta_fo_all2)
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
                    sta = sta_all.loc[sta_all["time"] == time_fo]
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
                mind = np.min(dvalue)
                fmt_str = ".0f"
                #if(maxd >10 or mind):
                #    fmt_str = ".0f"
                #else:
                #    fmt_str = ".1f"
                if cmap_error is None:
                    cmap_error = "bwr"
                sns.heatmap(dvalue.T, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd, center=None, robust=False, annot=True,
                            fmt=fmt_str)

                ax1.set_xlabel('实况时间')
                ax1.set_ylabel('起报时间')
                ax1.set_xticks(x+0.5)
                ax1.set_xticklabels(xticks)
                ax1.set_yticklabels(yticks, rotation=360)
                title = '不同时效预报误差和稳定性对比（误差）'+"("+data_name+")"+ "{\'id\':"+str(id)+"}"
                ax1.set_title(title, loc='left', fontweight='bold', fontsize='large')
                for k in range(row + 1):
                    x1 = start_ob_i - k * dh_y / dh_x
                    y1 = k
                    rect = patches.Rectangle((x1, y1), dh_y / dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                    ax1.add_patch(rect)
            else:
                height = 16 * row / col + 2
                f, ax2 = plt.subplots(figsize=(16, height), nrows=1, edgecolor='black')
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)


            if cmap is None:
                cmap = plt.get_cmap("rainbow")
                cmap_part = cmap
            if clev is not None:
                clev_part,cmap_part = meteva.base.tool.color_tools.get_part_clev_and_cmap(clev,cmap,vmax,vmin)
                vmax = clev_part[-1]
                vmin = 2 * clev_part[0] - clev_part[1]
            sns.heatmap(dat.T, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax, center=None, robust=False, annot=True,fmt='.0f')
            ax2.set_xlabel('实况时间')
            ax2.set_ylabel('起报时间')
            ax2.set_xticks(x+0.5)
            ax2.set_xticklabels(xticks)
            ax2.set_yticklabels(yticks, rotation=360)
            s1 = s
            if s1 is None:
                s1 = {}
                s1["id"] = id
                s1["member"] =[data_name]
            #title1 = meteva.product.program.get_title_from_dict(meteva.product.time_list_mesh, s1, None, None,None)

            #title = data_name + '实况和不同时效预报对比图'
            title1 = '不同时效预报误差和稳定性对比（要素值）' + "(" + data_name + ")" + "{\'id\':" + str(id) + "}"
            ax2.set_title(title1, loc='left', fontweight='bold', fontsize='large')


            for k in range(row+1):
                x1 = start_ob_i - k * dh_y/dh_x
                y1 = k
                rect = patches.Rectangle((x1, y1), dh_y/dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                ax2.add_patch(rect)

            if save_dir is None:
                show = True
            else:
                save_path = save_dir +"/" +data_name+"_"+str(id) + ".png"
                meteva.base.tool.path_tools.creat_path(save_path)
                plt.savefig(save_path)
                print("图片已保存至"+save_path)
            if show:
                plt.show()
            plt.close()
    return

def time_list_mesh_temp(sta_ob_all,sta_fo_all,s = None,save_dir = None,plot_error = True,show = False):
    clev, cmap= meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("temp")
    time_list_mesh(sta_ob_all,sta_fo_all,s,save_dir,clev,cmap,plot_error,cmap_error= "bwr",show = show)

def time_list_mesh_rain01h(sta_ob_all,sta_fo_all,s = None,save_dir = None,plot_error = True,show = False):
    clev, cmap= meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_1h")
    clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_1h_error")
    time_list_mesh(sta_ob_all,sta_fo_all,s,save_dir,clev,cmap,plot_error,cmap_error= cmap_error,show = show)

def time_list_mesh_rain03h(sta_ob_all,sta_fo_all,s = None,save_dir = None,plot_error = True,show = False):
    clev, cmap= meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_3h")
    clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_3h_error")
    time_list_mesh(sta_ob_all,sta_fo_all,s,save_dir,clev,cmap,plot_error,cmap_error= cmap_error,show = show)

def time_list_mesh_rh(sta_ob_all,sta_fo_all,s = None,save_dir = None,plot_error = True,show = False):
    clev, cmap= meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rh")
    clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rh_error")
    time_list_mesh(sta_ob_all, sta_fo_all,s,save_dir, clev, cmap, plot_error, cmap_error=cmap_error,show = show)

def time_list_mesh_vis(sta_ob_all,sta_fo_all,s = None,save_dir = None,plot_error = True,show = False):
    clev, cmap= meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("vis")
    clev_error,cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("vis_error")
    time_list_mesh(sta_ob_all,sta_fo_all,s,save_dir,clev,cmap,plot_error,cmap_error= cmap_error)

def time_list_mesh_tcdc(sta_ob_all,sta_fo_all,s = None,save_dir = None,plot_error = True,show = False):
    clev, cmap= meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("tcdc")
    clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name(
        "tcdc_error")
    time_list_mesh(sta_ob_all,sta_fo_all,s,save_dir,clev,cmap,plot_error,cmap_error= cmap_error,show = show)

def time_list_mesh_wind(sta_ob_all0,sta_fo_all0,s = None,save_dir = None,plot_error = True,show = False,save_path = None,title = "预报准确性和稳定性对比图"):


    sta_fo_all1 = meteva.base.sele_by_dict(sta_fo_all0, s)
    ids_fos = list(set(sta_fo_all1.loc[:,"id"]))
    ids_obs = list(set(sta_ob_all0.loc[:,"id"]))
    for id in ids_obs:
        if id not in ids_fos:continue
        sta_ob_all2 = meteva.base.in_id_list(sta_ob_all0,[id])
        sta_fo_all1_1 = meteva.base.in_id_list(sta_fo_all1,[id])
        data_names = meteva.base.get_stadata_names(sta_fo_all1_1)
        num = int(len(data_names)/2)
        for n in range(num):
            members = [data_names[n*2],data_names[n*2+1]]
            sta_fo_all2 = meteva.base.in_member_list(sta_fo_all1_1,member_list=members)
            #以最近的预报作为窗口中间的时刻
            times_fo = copy.deepcopy(sta_fo_all2["time"].values)
            times_fo = list(set(times_fo))
            #print(times_fo)
            if(len(times_fo)==1):
                print("仅有单个起报时间的预报，程序退出")
                return
            times_fo.sort()
            times_fo = np.array(times_fo)
            time_mid = meteva.base.tool.time_tools.all_type_time_to_datetime(times_fo[-1])
            #以观预报数据的间隔的最小单位作为纵坐标的步长
            dhs_fo = (times_fo[1:] - times_fo[0:-1])
            if isinstance(dhs_fo[0],np.timedelta64):
                dhs_fo = dhs_fo / np.timedelta64(1, 'h')
            else:
                dhs_fo = dhs_fo / datetime.timedelta(hours=1)
            dhs_fo_not0 = dhs_fo[dhs_fo!=0]
            dh_y = np.min(dhs_fo_not0)

            #以数据中最大的预报时效，确定整个窗口的横轴范围宽度
            dhs = copy.deepcopy(sta_fo_all2["dtime"].values)
            dhs.sort()
            max_dh = int(dhs[-1])
            #以观预报时效间隔的最小单位
            ddhs = dhs[1:] - dhs[0:-1]
            ddhs = ddhs[ddhs!=0]
            dh_x = int(np.min(ddhs))


            data_names = meteva.base.get_stadata_names(sta_fo_all2)
            #print(data_names)
            sta_ob_all1 = copy.deepcopy(sta_ob_all2)
            #print(sta_ob_all1)
            meteva.base.set_stadata_names(sta_ob_all1,data_names)
            sta_all = meteva.base.combine_join(sta_ob_all1, sta_fo_all2)
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
                clev, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("wind_speed_error")

                sns.heatmap(diff_speed, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd)
                #sns.heatmap(dvalue.T, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd, center=None, robust=False, annot=True,
                #            fmt=fmt_str)
                ax1.set_xlabel('实况时间')
                ax1.set_ylabel('起报时间')
                ax1.set_xticks(x + 0.5)
                ax1.set_xticklabels(xticks)
                ax1.set_yticklabels(yticks, rotation=360)
                title = "实况(id:"+str(id)+")和不同时效预报("+data_names[0][1:]+")偏差图"
                ax1.set_title(title, loc='left', fontweight='bold', fontsize='large')
                xx, yy = np.meshgrid(x + 0.5, y + 0.5)
                speed_1d = dat_speed.flatten()
                xx_1d = xx.flatten()[speed_1d != 9999]
                yy_1d = yy.flatten()[speed_1d != 9999]
                u_1d = diff_u.flatten()[speed_1d != 9999]
                v_1d = diff_v.flatten()[speed_1d != 9999]
                ax1.barbs(xx_1d, yy_1d, u_1d, v_1d, barb_increments={'half': 2, 'full': 4, 'flag': 20})

                for k in range(row + 1):
                    x_1 = start_ob_i - k * dh_y / dh_x
                    y_1 = k
                    rect = patches.Rectangle((x_1, y_1), dh_y / dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                    #currentAxis.add_patch(rect)
                    ax1.add_patch(rect)


            else:
                height = 16 * row / col + 2
                f, ax2 = plt.subplots(figsize=(16, height), nrows=1, edgecolor='black')
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)

            vmin = np.min(dat_speed[dat_speed != 9999])
            vmax = np.max(dat_speed[dat_speed != 9999])
            clev, cmap = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("wind_speed")
            #print(vmax)
            #print(vmin)
            clev_part,cmap_part = meteva.base.tool.color_tools.get_part_clev_and_cmap(clev,cmap,vmax,vmin)
            vmax = clev_part[-1]
            vmin = 2 * clev_part[0] - clev_part[1]

            sns.heatmap(dat_speed, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax)
            ax2.set_xlabel('实况时间')
            ax2.set_ylabel('起报时间')
            ax2.set_xticks(x+0.5)
            ax2.set_xticklabels(xticks)
            ax2.set_yticklabels(yticks, rotation=360)
            title =  "实况("+str(id)+")和不同时效预报("+data_names[0][1:]+")对比图"
            ax2.set_title(title, loc='left', fontweight='bold', fontsize='large')
            xx,yy = np.meshgrid(x+0.5,y+0.5)
            speed_1d = dat_speed.flatten()
            xx_1d = xx.flatten()[speed_1d !=9999]
            yy_1d = yy.flatten()[speed_1d !=9999]
            u_1d = dat_u.flatten()[speed_1d !=9999]
            v_1d = dat_v.flatten()[speed_1d !=9999]
            ax2.barbs(xx_1d, yy_1d,u_1d,v_1d, barb_increments={'half': 2, 'full': 4, 'flag': 20})

            for k in range(row+1):
                x = start_ob_i - k * dh_y/dh_x
                y = k
                rect = patches.Rectangle((x, y), dh_y/dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                ax2.add_patch(rect)

            if save_path is None:
                if save_dir is None:
                    show = True
                else:

                    save_path = save_dir +"/" +members[0]+"_"+str(id) + ".png"
                    meteva.base.tool.path_tools.creat_path(save_path)
                    plt.savefig(save_path)
                    print("图片已保存至"+save_path)
            else:
                meteva.base.tool.path_tools.creat_path(save_path)
                plt.savefig(save_path)
                print("图片已保存至" + save_path)
            if show:
                plt.show()
            plt.close()

