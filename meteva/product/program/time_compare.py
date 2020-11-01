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
import matplotlib as mpl


def time_list_line_error(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,show = False,dpi = 300,title = "多时效预报误差对比图",
                         sup_fontsize = 10,width = None,height = None):
    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    sta_ob_and_fos1 = meteva.base.sele_by_para(sta_ob_and_fos1,drop_IV=True)
    ids = list(set(sta_ob_and_fos1.loc[:,"id"]))
    nids = len(ids)

    if isinstance(title, list):
        if nids != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return
    for n in range(nids):
        id = ids[n]
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

        if width is None:
            width = len(dhs) * 1.2
            if width > 8:width = 8
        if height is None:
            height = len(times_fo) * 1.0
            if height > 5:height = 5

        fig = plt.figure(figsize=(width, height),dpi = dpi)
        grid_plt = plt.GridSpec(len(times_fo), 1, hspace=0)

        time_f0 = times_fo[0]
        data_names = meteva.base.get_stadata_names(sta_ob_and_fos)
        error_array = np.zeros((len(sta_ob_and_fos.index),len(data_names)-1))
        for i in range(len(data_names)-1):
            error_array[:,i] = sta_ob_and_fos.values[:, 7+i] - sta_ob_and_fos.values[:, 6]
        vmax0 = np.max(error_array)
        vmin0 = np.min(error_array) - 0.1
        maxerr = np.maximum(vmax0,-vmin0)
        vmax = maxerr * 1.05
        vmin = -maxerr * 1.05
        #vmax = (vmax - vmin) * 1.2 + vmin
        dif = (vmax - vmin)/2
        inte = math.pow(10, math.floor(math.log10(dif)))
        # 用基本间隔，将最大最小值除于间隔后小数点部分去除，最后把间隔也整数化
        r = dif / inte
        if(r<1.5):
            inte = inte * 0.5
        elif r < 3 and r >= 1.5:
            inte = inte * 1
        elif r < 4.5 and r >= 3:
            inte = inte * 2
        elif r < 5.5 and r >= 4.5:
            inte = inte * 3
        elif r < 7 and r >= 5.5:
            inte = inte * 3
        elif r >= 7:
            inte = inte * 4
        yticks = np.array([-inte,0,inte])

        dtimes = sta_ob_and_fos["dtime"] * np.timedelta64(1, 'h')
        obtimes = sta_ob_and_fos['time'] + dtimes
        obtimes[-1] = times_fo[0]
        time_all = list(set(obtimes))
        time_all.sort()
        #print(time_all)
        dtime_all = pd.Series(time_all) - times_fo[0]
        x_all = dtime_all/np.timedelta64(1, 'h')
        x_all = x_all.values

        x_plot, time_strs = meteva.product.program.get_x_ticks(time_all, width-1)

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
            plt.plot(x,np.zeros(x.size),linewidth = sup_fontsize *0.07)
            for name in data_names[1:]:
                value = sta.loc[:, name].values - sta.iloc[:, 6].values
                plt.plot(x, value, label=name,marker = ".",linewidth = sup_fontsize *0.1,markersize = sup_fontsize *0.3)
                plt.ylim(vmin, vmax)
                plt.yticks(yticks,fontsize = sup_fontsize *0.6)
                plt.xlim(x_all[0],x_all[-1])
                plt.grid(linestyle='-.',linewidth = sup_fontsize *0.07)


            time_f1 = meteva.base.tool.time_tools.all_type_time_to_datetime(time_f1)
            time_str = time_f1.strftime('%d{d}%H{h}').format(d='日', h='时')+"        "
            plt.ylabel(time_str, rotation='horizontal',fontsize = sup_fontsize * 0.75)
            if i ==0:
                plt.legend(loc="upper left", ncol=len(data_names),fontsize = sup_fontsize * 0.9)
                s1 = s
                if s1 is None:
                    s1 = {}
                    s1["id"] = id

                if isinstance(title,list):
                    title1 = title[n]
                else:
                    title1 = meteva.product.program.get_title_from_dict(title, s1, None, None,
                                                                    None)

                    title1 = title1.replace("\n","")
                plt.title(title1,fontsize = sup_fontsize)

            #plt.hlines(0,x_plot[0],x_plot[-1],"k",linewidth = 0.5)
            if i == len(times_fo) - 1:
                plt.xticks(x_plot, time_strs,fontsize =  sup_fontsize * 0.8)
                plt.xlabel("实况时间",fontsize = sup_fontsize * 0.9)
            else:
                plt.xticks(x_plot,time_strs_null)

        rect_ylabel = [0.03, 0.45, 0.0, 0.0]  # 左下宽高
        ax_ylabel = plt.axes(rect_ylabel)
        ax_ylabel.axes.set_axis_off()
        plt.text(0, 0, "起报时间", fontsize=sup_fontsize * 0.9, rotation=90)

        save_path1 = None
        if save_path is None:
            if save_dir is None:
                show = True
            else:
                save_path1 = save_dir+"\\" + str(id) + ".png"
        else:
            save_path1 = save_path[n]

        if save_path1 is not None:
            meteva.base.tool.path_tools.creat_path(save_path1)
            plt.savefig(save_path1,bbox_inches='tight')
            print("图片已保存至" + save_path1)
        if show:
            plt.show()
        plt.close()


def time_list_line(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,show = False,dpi = 300,title = "预报准确性和稳定性对比图",
                   sup_fontsize = 10,width = None,height = None):
    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    ids = list(set(sta_ob_and_fos1.loc[:,"id"]))
    nids = len(ids)
    if isinstance(title, list):
        if nids != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return

    for n in range(nids):
        id = ids[n]
        #print(id)
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

        if width is None:
            width = len(dhs) * 1.2
            if width > 8:width = 8
            if width < 4:width = 4

        if height is None:
            height = len(times_fo) * 1
            if height > 5:height = 5

        fig = plt.figure(figsize=(width, height),dpi = dpi)
        grid_plt = plt.GridSpec(len(times_fo), 1, hspace=0)

        time_f0 = times_fo[0]
        data_names = meteva.base.get_stadata_names(sta_ob_and_fos)
        values = sta_ob_and_fos.iloc[:, 6:].values.flatten()
        values = values[values != meteva.base.IV]
        vmax = np.max(values)
        vmin = np.min(values) - 0.1
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
        x_plot,time_strs = meteva.product.program.get_x_ticks(time_all,width-1)
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
                plt.plot(x, value, label=name,marker = ".",linewidth = sup_fontsize * 0.1,markersize = sup_fontsize * 0.3)
                plt.ylim(vmin, vmax)
                plt.yticks(fontsize = sup_fontsize * 0.6)
                plt.xlim(x_all[0],x_all[-1])
                plt.grid(linestyle='-.')

            time_f1 = meteva.base.tool.time_tools.all_type_time_to_datetime(time_f1)
            time_str = time_f1.strftime('%d{d}%H{h}').format(d='日', h='时')+"        "
            plt.ylabel(time_str, rotation='horizontal',fontsize = sup_fontsize *0.75)
            if i ==0:
                plt.legend(loc="upper left", ncol=len(data_names),fontsize = sup_fontsize *0.9)
                s1 = s
                if s1 is None:
                    s1 = {}
                s1["id"] = id

                if isinstance(title, list):
                    title1 = title[n]
                else:
                    title1 = meteva.product.program.get_title_from_dict(title, s1, None, None,
                                                                        None)
                    title1 = title1.replace("\n", "")
                plt.title(title1, fontsize=sup_fontsize)
            if i == len(times_fo) - 1:
                #print(x_plot)
                plt.xticks(x_plot, time_strs,fontsize = sup_fontsize * 0.8)
                plt.xlabel("实况时间",fontsize = sup_fontsize * 0.9)
            else:
                plt.xticks(x_plot,time_strs_null)

        rect_ylabel = [0.03, 0.45, 0.0, 0.0]  # 左下宽高
        ax_ylabel = plt.axes(rect_ylabel)
        ax_ylabel.axes.set_axis_off()
        plt.text(0, 0, "起报时间", fontsize=sup_fontsize * 0.9, rotation=90)

        save_path1 = None
        if save_path is None:
            if save_dir is None:
                show = True
            else:
                save_path1 = save_dir+"/" + str(id) + ".png"
        else:
            save_path1 = save_path[n]
        if save_path1 is not None:
            meteva.base.tool.path_tools.creat_path(save_path1)
            plt.savefig(save_path1,bbox_inches='tight')
            print("图片已保存至" + save_path1)
        if show:
            plt.show()
        plt.close()



def time_list_mesh_error(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,
                   max_error = None,cmap_error = None,show = False,xtimetype = "mid",dpi = 300,annot =True,title = "多时效预报误差对比图",
                         sup_fontsize = 10,width = None,height = None):
    '''

    :param sta_ob_and_fos0:
    :param s:
    :param save_dir:
    :param save_path:
    :param clev:
    :param cmap:
    :param plot_error:
    :param cmap_error:
    :param show:
    :param title:
    :return:
    '''

    if max_error is None:
        sta_ob_fos0_noIV = meteva.base.not_IV(sta_ob_and_fos0)
        values = sta_ob_fos0_noIV.values[:,6:].T
        dvalues = values[1:,:] - values[0,:]
        maxd = np.max(np.abs(dvalues))
    else:
        maxd = max_error

    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    sta_ob_and_fos1 = meteva.base.sele_by_para(sta_ob_and_fos1,drop_IV=True)
    if(len(sta_ob_and_fos1.index) == 0):
        print("there is no data to verify")
        return
    ids = list(set(sta_ob_and_fos1.loc[:, "id"]))
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos1)
    times_fo = sta_ob_and_fos1.loc[:, "time"].values
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
    min_dtime = int(np.min(sta_ob_and_fos1["dtime"]))


    ob_time_s = sta_ob_and_fos1["time"] + sta_ob_and_fos1["dtime"] * np.timedelta64(1, 'h')
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

    if width is None:
        width = 8

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
        sta_one_member = meteva.base.in_member_list(sta_ob_and_fos1, [data_names[0],data_name])
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

            if height is None:
                height = width * row / col + 2
            f, ax2 = plt.subplots(figsize=(width, height), nrows=1, edgecolor='black',dpi = dpi)
            plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)


            if cmap_error is None:
                cmap_error ="bwr"
                cmap_part = cmap_error

            sns.heatmap(dat.T, ax=ax2, mask=mask, cmap=cmap_part, vmin=-maxd, vmax=maxd, center=None, robust=False, annot=annot,fmt='.0f'
            , annot_kws = {'size': annot_size})
            ax2.set_xlabel('实况时间',fontsize = sup_fontsize *  0.9)
            ax2.set_ylabel('起报时间',fontsize = sup_fontsize * 0.9)
            ax2.set_xticks(x_plot)
            ax2.set_xticklabels(x_ticks,rotation=360, fontsize=sup_fontsize * 0.8)
            ax2.set_yticks(y_plot)
            ax2.set_yticklabels(y_ticks, rotation=360, fontsize=sup_fontsize * 0.8)

            ax2.grid(linestyle='--', linewidth=0.5)
            ax2.set_ylim(row, 0)
            s1 = s
            if s1 is None:
                s1 = {}
                s1["id"] = id
                s1["member"] =[data_name]
            if isinstance(title,list):
                title1 = title[kk]
            else:
                if id in meteva.base.station_id_name_dict.keys():
                    title1 = title + "(" + data_name + ")" + "{\'id\':" + str(id) +meteva.base.station_id_name_dict[id] +"}"
                else:
                    title1 = title + "(" + data_name + ")" + "{\'id\':" + str(id) +  "}"

            ax2.set_title(title1, loc='left', fontweight='bold', fontsize=sup_fontsize)
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

def time_list_mesh(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,
                   clev = None,cmap = None,plot_error = True,max_error = None,cmap_error= None,
                   show = False,xtimetype = "mid",dpi = 300,annot =True,title = "预报准确性和稳定性对比图",
                   sup_fontsize = 10,width = None,height = None):
    '''

    :param sta_ob_and_fos0:
    :param s:
    :param save_dir:
    :param save_path:
    :param clev:
    :param cmap:
    :param plot_error:
    :param cmap_error:
    :param show:
    :param title:
    :return:
    '''

    if max_error is None:
        sta_ob_fos0_noIV = meteva.base.not_IV(sta_ob_and_fos0)
        values = sta_ob_fos0_noIV.values[:,6:].T
        if(values.size ==0):
            print("无有效的观测数据")
            return
        dvalues = values[1:,:] - values[0,:]
        maxd = np.max(np.abs(dvalues))
    else:
        maxd = max_error

    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    ids = list(set(sta_ob_and_fos1.loc[:,"id"]))
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos1)
    sta_ob_all1 = meteva.base.sele_by_para(sta_ob_and_fos1,member=[data_names[0]])
    sta_fo_all1 = meteva.base.sele_by_para(sta_ob_and_fos1, member=data_names[1:])
    times_fo = sta_fo_all1.loc[:, "time"].values
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
    min_dtime = int(np.min(sta_fo_all1["dtime"]))
    sta_ob_part1 = meteva.base.between_dtime_range(sta_ob_all1,min_dtime,min_dtime+dh_y-0.1)
    sta_ob_part2 = meteva.base.move_fo_time(sta_ob_part1,dh_y)


    ob_time_s = sta_fo_all1["time"] + sta_fo_all1["dtime"] * np.timedelta64(1, 'h')
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

    #t_fo =[]
    #for t in times_fo:
    #    t_fo.append(meteva.base.all_type_time_to_datetime(t))


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
    if width is None:
        width = 8
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
        if plot_error:
            if 2 * nids * nfo != len(title):
                print("手动设置的title数目和要绘制的图形数目不一致")
                return
        else:
            if nids * nfo != len(title):
                print("手动设置的title数目和要绘制的图形数目不一致")
                return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids * nfo != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return
    kk1 = 0
    kk2 = 0
    for d in range(len(data_names)-1):
        data_name = data_names[d+1]
        sta_fo_all2 = meteva.base.in_member_list(sta_fo_all1, data_name)
        meteva.base.set_stadata_names(sta_ob_part2, [data_name])
        sta_one_member = meteva.base.combine_join(sta_ob_part2, sta_fo_all2)
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

            vmin = np.min(dat[dat != meteva.base.IV])
            vmax = np.max(dat[dat != meteva.base.IV])
            #print(vmax)
            if plot_error:
                if height is None:
                    height = (width * row / col + 2) * 2
                f, (ax1, ax2)  = plt.subplots(figsize=(width, height),nrows = 2,edgecolor='black',dpi = dpi)
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90,hspace=0.3)
                dvalue = np.zeros_like(dat)
                for i in range(col):
                    top_value = meteva.base.IV
                    for j in range(row):
                        if dat[i, j] != meteva.base.IV:
                            top_value = dat[i, j]
                            break
                    for j in range(row):
                        if dat[i, j] != meteva.base.IV:
                            dvalue[i, j] = dat[i, j] - top_value

                fmt_str = ".0f"
                if cmap_error is None:
                    cmap_error = "bwr"
                sns.heatmap(dvalue.T, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd, center=None, robust=False, annot=annot,
                            fmt=fmt_str, annot_kws={'size':annot_size})
                #ax1.set_xlabel('实况时间',fontsize = sup_fontsize = 0.9)
                ax1.set_ylabel('起报时间',fontsize = sup_fontsize * 0.9)
                ax1.set_xticks(x_plot)
                ax1.set_xticklabels(x_ticks,rotation=360,fontsize=sup_fontsize * 0.8)
                ax1.set_yticks(y_plot)
                ax1.set_yticklabels(y_ticks, rotation=360, fontsize=sup_fontsize * 0.8)

                if isinstance(title,list):
                    title1 = title[kk2]
                    kk2 +=1
                else:
                    if id in meteva.base.station_id_name_dict.keys():
                        title1 = title+"（误差）"+"("+data_name+")"+ "{\'id\':"+str(id)+meteva.base.station_id_name_dict[id] +"}"
                    else:
                        title1 = title + "（误差）" + "(" + data_name + ")" + "{\'id\':" + str(id) + "}"
                ax1.set_title(title1, loc='left', fontweight='bold', fontsize=sup_fontsize)

                ax1.grid(linestyle='--', linewidth=0.5)

                #plt.tick_params(top='on', right='on', which='both')  # 显示上侧和右侧的刻度
                plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
                plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内

                for k in range(row + 1):
                    jr = row - k - 1
                    time_fo = times_fo[0] + np.timedelta64(1, 'h') * dh_y * jr
                    dhx0 = (time_fo- times_ob[0]) / np.timedelta64(1, 'h') + min_dtime
                    x1 = (dhx0 - dh_y) / dh_x
                    y1 = k
                    rect = patches.Rectangle((x1, y1), dh_y / dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                    ax1.add_patch(rect)
                rect = patches.Rectangle((0, 0), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
                ax1.set_ylim(row, 0)
                ax1.add_patch(rect)

            else:
                if height is None:
                    height = width * row / col + 1.2
                f, ax2 = plt.subplots(figsize=(width, height), nrows=1, edgecolor='black',dpi = dpi)
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)


            if cmap is None:
                cmap = plt.get_cmap("rainbow")
                cmap_part = cmap
            if clev is not None:
                cmap_part ,clev_part= meteva.base.tool.color_tools.get_part_cmap_and_clevs(cmap,clev,vmax,vmin)
                vmax = clev_part[-1]
                vmin = 2 * clev_part[0] - clev_part[1]
            sns.heatmap(dat.T, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax, center=None, robust=False, annot=annot,fmt='.0f'
            , annot_kws = {'size': annot_size})
            ax2.set_xlabel('实况时间',fontsize = sup_fontsize * 0.9)
            ax2.set_ylabel('起报时间',fontsize = sup_fontsize * 0.9)
            ax2.set_xticks(x_plot)
            ax2.set_xticklabels(x_ticks,rotation=360, fontsize=sup_fontsize * 0.8)
            ax2.set_yticks(y_plot)
            ax2.set_yticklabels(y_ticks, rotation=360, fontsize=sup_fontsize * 0.8)
            ax2.grid(linestyle='--', linewidth=0.5)
            ax2.set_ylim(row,0)
            s1 = s
            if s1 is None:
                s1 = {}
                s1["id"] = id
                s1["member"] =[data_name]
            #title1 = meteva.product.program.get_title_from_dict(meteva.product.time_list_mesh, s1, None, None,None)

            #title = data_name + '实况和不同时效预报对比图'
            if isinstance(title,list):
                title1 = title[kk2]
                kk2 +=1
            else:
                if id in meteva.base.station_id_name_dict.keys():
                    title1 = title + "（要素值）" + "(" + data_name + ")" + "{\'id\':" + str(id) +meteva.base.station_id_name_dict[id] +"}"
                else:
                    title1 = title + "（要素值）" + "(" + data_name + ")" + "{\'id\':" + str(id)  + "}"
            ax2.set_title(title1, loc='left', fontweight='bold', fontsize=sup_fontsize)

            for k in range(row):
                jr = row - k - 1
                dhx0 = (times_fo[0] - times_ob[0]) / np.timedelta64(1, 'h') +min_dtime + dh_y * jr
                x1 = (dhx0-dh_y)/dh_x
                y1 = k
                rect = patches.Rectangle((x1, y1), dh_y/dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                ax2.add_patch(rect)
            rect = patches.Rectangle((0,0 ), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
            ax2.add_patch(rect)
            #plt.tick_params(top='on', right='on', which='both')  # 显示上侧和右侧的刻度
            plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
            plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内

            save_path1 = None
            if (save_path is None):
                if save_dir is None:
                    show = True
                else:
                    save_path1 = save_dir + "/" + data_name + "_" + str(id) + ".png"
            else:
                save_path1 = save_path[kk1]
            if save_path1 is not None:
                meteva.base.tool.path_tools.creat_path(save_path1)
                plt.savefig(save_path1, bbox_inches='tight')
                print("图片已保存至" + save_path1)
            if show:
                plt.show()
            plt.close()
            kk1 += 1
    return



def time_list_mesh_temp(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =True,
                        title = "温度预报准确性和稳定性对比图",
                        sup_fontsize = 10,width = None,height = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("temp")
    time_list_mesh(sta_ob_and_fos0,s,save_dir,save_path,clev,cmap,plot_error,cmap_error= "bwr",show = show,dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height)

def time_list_mesh_rain01h(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =True,
                           title = "1小时降水量预报准确性和稳定性对比图",
                           sup_fontsize = 10,width = None,height = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("rain_1h")
    #clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_1h_error")
    time_list_mesh(sta_ob_and_fos0,s,save_dir,save_path,clev,cmap,plot_error,show = show,xtimetype="right",dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height)

def time_list_mesh_rain03h(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =True,
                           title = "3小时降水量预报准确性和稳定性对比图",
                           sup_fontsize = 10,width = None,height = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("rain_3h")
    #clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rain_3h_error")
    time_list_mesh(sta_ob_and_fos0, s, save_dir, save_path, clev, cmap, plot_error, show=show,
                    xtimetype="right",dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height)

def time_list_mesh_rh(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =True,
                      title = "相对湿度预报准确性和稳定性对比图",
                      sup_fontsize = 10,width = None,height = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("rh")
    #clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("rh_error")
    time_list_mesh(sta_ob_and_fos0,s,save_dir,save_path, clev, cmap, plot_error,show = show,dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height)

def time_list_mesh_vis(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =True,
                       title = "能见度预报准确性和稳定性对比图",
                       sup_fontsize = 10,width = None,height = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("vis")
    #clev_error,cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("vis_error")
    time_list_mesh(sta_ob_and_fos0,s,save_dir,save_path,clev,cmap,plot_error,show = show,dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height)


def time_list_mesh_tcdc(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,dpi = 300,annot =True,
                        title = "云量预报准确性和稳定性对比图",
                        sup_fontsize = 10,width = None,height = None):
    cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("tcdc")
    #clev_error, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("tcdc_error")
    time_list_mesh(sta_ob_and_fos0,s,save_dir,save_path,clev,cmap,plot_error = plot_error,show = show,dpi = dpi ,annot = annot,
    title = title,sup_fontsize= sup_fontsize,width=width,height=height)


def time_list_mesh_wind(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,
                        max_error = None,show = False,dpi = 300,title = "风预报准确性和稳定性对比图",
                        sup_fontsize = 10,width = None,height = None):

    if max_error is None:
        sta_ob_fos0_noIV = meteva.base.not_IV(sta_ob_and_fos0)
        values = sta_ob_fos0_noIV.values[:,6:].T
        if(values.size ==0):
            print("无有效的观测数据")
            return
        u = values[0::2,:]
        v = values[1::2,:]
        s2 = u * u +v * v
        speed = np.sqrt(s2.astype(np.float32))
        dvalues = speed[1:, :] - speed[0, :]
        maxd = np.max(np.abs(dvalues))
    else:
        maxd = max_error


    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    ids = list(set(sta_ob_and_fos1.loc[:, "id"]))
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos1)
    ob_names = data_names[0:2]
    fo_names = data_names[2:]
    sta_ob_all1 = meteva.base.sele_by_para(sta_ob_and_fos1,member=ob_names)
    sta_fo_all1 = meteva.base.sele_by_para(sta_ob_and_fos1, member=fo_names)

    times_fo = sta_fo_all1.loc[:, "time"].values
    times_fo = list(set(times_fo))
    if (len(times_fo) == 1):
        print("仅有单个起报时间的预报，程序退出")
        return
    times_fo.sort()
    times_fo = np.array(times_fo)
    # print(times_fo)

    dhs_fo = (times_fo[1:] - times_fo[0:-1])
    if isinstance(dhs_fo[0], np.timedelta64):
        dhs_fo = dhs_fo / np.timedelta64(1, 'h')
    else:
        dhs_fo = dhs_fo / datetime.timedelta(hours=1)
    dhs_fo_not0 = dhs_fo[dhs_fo != 0]
    dh_y = np.min(dhs_fo_not0)
    min_dtime = int(np.min(sta_fo_all1["dtime"]))
    sta_ob_part1 = meteva.base.between_dtime_range(sta_ob_all1, min_dtime, min_dtime + dh_y - 0.1)
    sta_ob_part2 = meteva.base.move_fo_time(sta_ob_part1, dh_y)

    ob_time_s = sta_fo_all1["time"] + sta_fo_all1["dtime"] * np.timedelta64(1, 'h')
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
    # print(dh_x)
    np.sum(dhs_fo_not0)
    row = int(np.sum(dhs_fo_not0) / dh_y) + 1
    col = int(np.sum(dhs_ob_not0) / dh_x) + 1
    # print(row)
    t_ob = []
    for t in times_ob:
        t_ob.append(meteva.base.all_type_time_to_datetime(t))

    # t_fo =[]
    # for t in times_fo:
    #    t_fo.append(meteva.base.all_type_time_to_datetime(t))

    y_plot = np.arange(row) + 0.5
    y_ticks = []
    t_fo0 = meteva.base.all_type_time_to_datetime(times_fo[0])
    step = int(math.ceil(row / 40))

    if step != 1:
        while step * dh_y % 3 != 0:
            step += 1

    y_plot = np.arange(0, row, step) + 0.5
    for j in range(0, row, step):
        jr = row - j - 1
        time_fo = t_fo0 + datetime.timedelta(hours=1) * dh_y * jr
        hour = time_fo.hour
        day = time_fo.day
        # if ((j * int(dh_y)) % 3 == 0):
        str1 = str(day) + "日" + str(hour) + "时"
        # else:
        #    str1 = str(hour) + "时"
        # print(str1)
        y_ticks.append(str1)

    if width is None:
        width = 8
    x_plot, x_ticks = meteva.product.get_x_ticks(times_ob, width - 2)
    x_plot /= dh_x
    x_plot += 0.5
    x = np.arange(col)
    y = np.arange(row)
    nfo = int(len(fo_names)/2)
    nids = len(ids)
    if isinstance(title, list):
        if plot_error:
            if 2 * nids * nfo != len(title):
                print("手动设置的title数目和要绘制的图形数目不一致")
                return
        else:
            if nids * nfo != len(title):
                print("手动设置的title数目和要绘制的图形数目不一致")
                return

    if save_path is not None:
        if isinstance(save_path,str):
            save_path = [save_path]
        if nids * nfo != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return
    kk1 = 0
    kk2 = 0
    lenght = 40 * (width / col)
    for d in range(nfo):
        data_name = fo_names[d*2:d*2+2]
        sta_fo_all2 = meteva.base.in_member_list(sta_fo_all1, data_name)
        meteva.base.set_stadata_names(sta_ob_part2, data_name)
        sta_one_member = meteva.base.combine_join(sta_ob_part2, sta_fo_all2)

        # 以最近的预报作为窗口中间的时刻
        for id in ids:
            sta_one_id = meteva.base.in_id_list(sta_one_member, id)
            #dat = np.ones((col, row)) * meteva.base.IV
            dat_u = np.ones((row,col)) * meteva.base.IV
            dat_v = np.ones(dat_u.shape)* meteva.base.IV
            for j in range(row):
                jr = row - j - 1
                time_fo = times_fo[0] + np.timedelta64(1, 'h') * dh_y * jr
                sta_on_row = meteva.base.in_time_list(sta_one_id, time_fo)
                dhx0 = (time_fo - times_ob[0]) / np.timedelta64(1, 'h')
                dhxs = sta_on_row["dtime"].values + dhx0
                index_i = (dhxs / dh_x).astype(np.int16)

                dat_u[j,index_i] = sta_on_row.values[:, -2]
                dat_v[j,index_i] = sta_on_row.values[:, -1]

            dat_speed = np.sqrt(dat_u * dat_u + dat_v*dat_v)
            dat_speed[dat_u == meteva.base.IV] = meteva.base.IV
            mask = np.zeros_like(dat_speed)
            mask[dat_speed == meteva.base.IV] = True

            if plot_error:
                if height is None:
                    height = (width * row / col + 2) * 2
                f, (ax1, ax2) = plt.subplots(figsize=(width, height), nrows=2, edgecolor='black', dpi=dpi)
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90, hspace=0.3)

                diff_speed = np.zeros_like(dat_speed)
                diff_u = np.zeros_like(dat_u)
                diff_v = np.zeros_like(dat_v)

                # "风速误差"
                for i in range(col):
                    top_value = meteva.base.IV
                    for j in range(row):
                        if dat_speed[j, i] != meteva.base.IV:
                            top_value = dat_speed[j, i]
                            break
                    for j in range(row):
                        if dat_speed[j, i] != meteva.base.IV:
                            diff_speed[j, i] = dat_speed[j, i] - top_value
                # u 分量误差
                for i in range(col):
                    top_value = meteva.base.IV
                    for j in range(row):
                        if dat_u[j, i] != meteva.base.IV:
                            top_value = dat_u[j, i]
                            break
                    for j in range(row):
                        if dat_u[j, i] != meteva.base.IV:
                            diff_u[j, i] = dat_u[j, i] - top_value
                # v 分量误差
                for i in range(col):
                    top_value = meteva.base.IV
                    for j in range(row):
                        if dat_v[j, i] != meteva.base.IV:
                            top_value = dat_v[j, i]
                            break
                    for j in range(row):
                        if dat_v[j, i] != meteva.base.IV:
                            diff_v[j, i] = dat_v[j, i] - top_value


                #clev, cmap_error = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("wind_speed_error")

                sns.heatmap(diff_speed, ax=ax1, mask=mask, cmap="bwr", vmin=-maxd, vmax=maxd)
                # sns.heatmap(dvalue.T, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd, center=None, robust=False, annot=True,
                #            fmt=fmt_str)
                #ax1.set_xlabel('实况时间',fontsize =16 )
                ax1.set_ylabel('起报时间',fontsize =sup_fontsize * 0.9)
                ax1.set_xticks(x_plot)
                ax1.set_xticklabels(x_ticks,fontsize =sup_fontsize * 0.8)
                ax1.set_yticks(y_plot)
                ax1.set_yticklabels(y_ticks, rotation=360,fontsize =sup_fontsize * 0.8)
                #title = "实况(id:" + str(id) + ")和不同时效预报(" + data_name[0][2:] + ")偏差图"
                if isinstance(title,list):
                    title1 = title[kk2]
                    kk2 += 1
                else:
                    title1 = title + "(偏差)" + "(" + data_name[0][2:] + ")" + "{\'id\':" + str(id) + meteva.base.station_id_name_dict[id] + "}"
                ax1.set_title(title1, loc='left', fontweight='bold', fontsize=sup_fontsize)
                ax1.grid(linestyle='--', linewidth=0.5)
                xx, yy = np.meshgrid(x + 0.5, y + 0.5)
                speed_1d = dat_speed.flatten()
                xx_1d = xx.flatten()[speed_1d != meteva.base.IV]
                yy_1d = yy.flatten()[speed_1d != meteva.base.IV]
                u_1d = diff_u.flatten()[speed_1d != meteva.base.IV]
                v_1d = diff_v.flatten()[speed_1d != meteva.base.IV]
                ax1.barbs(xx_1d, yy_1d, u_1d, v_1d, barb_increments={'half': 2, 'full': 4, 'flag': 20},
                          length=lenght)

                plt.rcParams['xtick.direction'] = 'in'  # 将x轴的刻度线方向设置抄向内
                plt.rcParams['ytick.direction'] = 'in'  # 将y轴的刻度方知向设置向内
                for k in range(row + 1):
                    jr = row - k - 1
                    dhx0 = (times_fo[jr] - times_ob[0]) / np.timedelta64(1, 'h') + min_dtime
                    x1 = (dhx0 - dh_y) / dh_x
                    y1 = k
                    rect = patches.Rectangle((x1, y1), dh_y / dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                    ax1.add_patch(rect)
                rect = patches.Rectangle((0, 0), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
                ax1.add_patch(rect)

            else:
                if height is None:
                    height = width * row / col + 1.2
                f, ax2 = plt.subplots(figsize=(width, height), nrows=1, edgecolor='black', dpi=dpi)
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)

            vmin = np.min(dat_speed[dat_speed != meteva.base.IV])
            vmax = np.max(dat_speed[dat_speed != meteva.base.IV])
            cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("wind_speed")
            # print(vmax)
            # print(vmin)
            cmap_part,clev_part  = meteva.base.tool.color_tools.get_part_cmap_and_clevs(cmap,clev, vmax, vmin)
            vmax = clev_part[-1]
            vmin = 2 * clev_part[0] - clev_part[1]

            sns.heatmap(dat_speed, ax=ax2, mask=mask, cmap=cmap_part, vmin=vmin, vmax=vmax)
            ax2.set_xlabel('实况时间',fontsize =sup_fontsize * 0.9)
            ax2.set_ylabel('起报时间',fontsize =sup_fontsize * 0.8)
            ax2.set_xticks(x_plot)
            ax2.set_xticklabels(x_ticks,fontsize =sup_fontsize * 0.8)
            ax2.set_yticks(y_plot)
            ax2.set_yticklabels(y_ticks, rotation=360,fontsize =sup_fontsize * 0.8)
            #title = "实况(" + str(id) + ")和不同时效预报(" + data_name[0][2:] + ")对比图"
            if isinstance(title,list):
                title1 = title[kk2]
                kk2+= 1
            else:
                title1 = title + "(要素值)" + "(" + data_name[0][2:] + ")" + "{\'id\':" + str(id) +meteva.base.station_id_name_dict[id] +"}"
            ax2.set_title(title1, loc='left', fontweight='bold', fontsize=sup_fontsize)
            ax2.grid(linestyle='--', linewidth=0.5)
            xx, yy = np.meshgrid(x + 0.5, y + 0.5)
            speed_1d = dat_speed.flatten()
            xx_1d = xx.flatten()[speed_1d != meteva.base.IV]
            yy_1d = yy.flatten()[speed_1d != meteva.base.IV]
            u_1d = dat_u.flatten()[speed_1d != meteva.base.IV]
            v_1d = dat_v.flatten()[speed_1d != meteva.base.IV]



            ax2.barbs(xx_1d, yy_1d, u_1d, v_1d, barb_increments={'half': 2, 'full': 4, 'flag': 20},
                      length=lenght)

            for k in range(row):
                jr = row - k - 1
                dhx0 = (times_fo[0] - times_ob[0]) / np.timedelta64(1, 'h') +min_dtime + dh_y * jr
                x1 = (dhx0-dh_y)/dh_x
                y1 = k
                rect = patches.Rectangle((x1, y1), dh_y/dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                ax2.add_patch(rect)
            rect = patches.Rectangle((0,0 ), col, row, linewidth=0.8, edgecolor='k', facecolor='none')
            ax2.add_patch(rect)

            save_path1 = None
            if (save_path is None):
                if save_dir is None:
                    show = True
                else:
                    save_path1 = save_dir + "/" + data_name + "_" + str(id) + ".png"
            else:
                save_path1 = save_path[kk1]
            if save_path1 is not None:
                meteva.base.tool.path_tools.creat_path(save_path1)
                plt.savefig(save_path1, bbox_inches='tight')
                print("图片已保存至" + save_path1)
            if show:
                plt.show()
            plt.close()
            kk1 += 1
    return




def time_list_mesh_wind1(sta_ob_and_fos0,s = None,save_dir = None,save_path = None,plot_error = True,show = False,
                         dpi = 200,title = "预报准确性和稳定性对比图",
                         sup_fontsize = 10,width = None,height = None):

    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos0, s)
    data_names = meteva.base.get_stadata_names(sta_ob_and_fos1)
    sta_ob_all0 = meteva.base.sele_by_para(sta_ob_and_fos1,member=data_names[0:2])
    sta_fo_all1 = meteva.base.sele_by_para(sta_ob_and_fos1, member=data_names[2:])


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
            sta_ob_all1["dtime"] = -1
            sta_all = meteva.base.combine_join(sta_ob_all1, sta_fo_all2)
            col = (int)(2 * max_dh / dh_x + 1)
            hf_col = (int)(max_dh/dh_x)
            row = (int)(max_dh / dh_y)
            dat_u = np.ones((row,col)) * meteva.base.IV
            dat_v = np.ones(dat_u.shape)* meteva.base.IV


            time0 = time_mid - datetime.timedelta(hours=max_dh)
            start_ob_i = 0

            for i in range(col):
                for j in range(row):
                    time_fo = time_mid - datetime.timedelta(hours=j * dh_y)
                    dh = j * dh_y  + (i - hf_col) * dh_x
                    if j==0 and dh == 0:
                        start_ob_i = i
                    #if dh < dh_y and dh >0:
                    if dh < 0 and dh >= - dh_y:
                        time_fo = time_fo + datetime.timedelta(hours = dh)
                        dh = -1
                    sta = sta_all.loc[sta_all["time"] == time_fo]
                    sta = sta.loc[sta["dtime"] == dh]
                    if (len(sta.index) > 0):
                        dat_u[j,i] = sta[data_names[0]].values[0]
                        dat_v[j,i] = sta[data_names[1]].values[0]
            dat_speed = np.sqrt(dat_u * dat_u + dat_v*dat_v)
            dat_speed[dat_u == meteva.base.IV] = meteva.base.IV
            xticks = []
            x = np.arange(col)
            for i in range(col):
                time_ob = time0 + datetime.timedelta(hours=i * dh_x)
                hour = time_ob.hour
                day = time_ob.day
                if ((i * int(dh_x)) % 12 == 0):
                    str1 = str(hour) + "\n" + str(day) + "日"
                else:
                    if((i * int(dh_x)) % 6 == 0):
                        str1 = str(hour)
                    else:
                        str1 = ""
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
            mask[dat_speed == meteva.base.IV] = True

            if plot_error:
                height = 16 * row / col + 3
                f, (ax1, ax2)  = plt.subplots(figsize=(16, height*2),nrows = 2,edgecolor='black',dpi = dpi)
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90,hspace=0.3)

                diff_speed = np.zeros_like(dat_speed)
                diff_u = np.zeros_like(dat_u)
                diff_v = np.zeros_like(dat_v)

                #"风速误差"
                for i in range(col):
                    top_value = meteva.base.IV
                    for j in range(row):
                        if dat_speed[j,i] != meteva.base.IV:
                            top_value = dat_speed[j,i]
                            break
                    for j in range(row):
                        if dat_speed[j,i] != meteva.base.IV:
                            diff_speed[j,i] = dat_speed[j,i] - top_value
                #u 分量误差
                for i in range(col):
                    top_value = meteva.base.IV
                    for j in range(row):
                        if dat_u[j,i] != meteva.base.IV:
                            top_value = dat_u[j,i]
                            break
                    for j in range(row):
                        if dat_u[j,i] != meteva.base.IV:
                            diff_u[j,i] = dat_u[j,i] - top_value
                #v 分量误差
                for i in range(col):
                    top_value = meteva.base.IV
                    for j in range(row):
                        if dat_v[j,i] != meteva.base.IV:
                            top_value = dat_v[j,i]
                            break
                    for j in range(row):
                        if dat_v[j,i] != meteva.base.IV:
                            diff_v[j,i] = dat_v[j,i] - top_value

                maxd = np.max(np.abs(diff_speed))
                cmap_error,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("wind_speed_error")

                sns.heatmap(diff_speed, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd)
                #sns.heatmap(dvalue.T, ax=ax1, mask=mask, cmap=cmap_error, vmin=-maxd, vmax=maxd, center=None, robust=False, annot=True,
                #            fmt=fmt_str)
                #ax1.set_xlabel('实况时间')
                ax1.set_ylabel('起报时间')
                ax1.set_xticks(x + 0.5)
                ax1.set_xticklabels(xticks)
                ax1.set_yticklabels(yticks, rotation=360)
                title = "实况(id:"+str(id)+")和不同时效预报("+data_names[0][1:]+")偏差图"
                ax1.set_title(title, loc='left', fontweight='bold', fontsize='large')
                xx, yy = np.meshgrid(x + 0.5, y + 0.5)
                speed_1d = dat_speed.flatten()
                xx_1d = xx.flatten()[speed_1d != meteva.base.IV]
                yy_1d = yy.flatten()[speed_1d != meteva.base.IV]
                u_1d = diff_u.flatten()[speed_1d != meteva.base.IV]
                v_1d = diff_v.flatten()[speed_1d != meteva.base.IV]
                ax1.barbs(xx_1d, yy_1d, u_1d, v_1d, barb_increments={'half': 2, 'full': 4, 'flag': 20})

                for k in range(row + 1):
                    x_1 = start_ob_i - (k+1) * dh_y / dh_x
                    y_1 = k
                    rect = patches.Rectangle((x_1, y_1), dh_y / dh_x, 1, linewidth=2, edgecolor='k', facecolor='none')
                    #currentAxis.add_patch(rect)
                    ax1.add_patch(rect)
            else:
                height = 16 * row / col + 2
                f, ax2 = plt.subplots(figsize=(16, height), nrows=1, edgecolor='black',dpi = dpi)
                plt.subplots_adjust(left=0.1, bottom=0.15, right=0.98, top=0.90)

            vmin = np.min(dat_speed[dat_speed != meteva.base.IV])
            vmax = np.max(dat_speed[dat_speed != meteva.base.IV])
            cmap,clev= meteva.base.tool.color_tools.get_cmap_and_clevs_by_element_name("wind_speed")
            #print(vmax)
            #print(vmin)
            clev_part,cmap_part = meteva.base.tool.color_tools.get_part_cmap_and_clevs(clev,cmap,vmax,vmin)
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
            xx_1d = xx.flatten()[speed_1d !=meteva.base.IV]
            yy_1d = yy.flatten()[speed_1d !=meteva.base.IV]
            u_1d = dat_u.flatten()[speed_1d !=meteva.base.IV]
            v_1d = dat_v.flatten()[speed_1d !=meteva.base.IV]
            ax2.barbs(xx_1d, yy_1d,u_1d,v_1d, barb_increments={'half': 2, 'full': 4, 'flag': 20})

            for k in range(row+1):
                x = start_ob_i - (k+1) * dh_y/dh_x
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
                plt.savefig(save_path,bbox_inches='tight')
                print("图片已保存至" + save_path)
                save_path = None
            if show:
                plt.show()
            plt.close()
