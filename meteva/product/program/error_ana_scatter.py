import meteva
import numpy as np
import math


def rmse_scatter(sta_ob_and_fos,s = None,g = None,gll = None,group_name_list= None,save_dir=None,save_path = None,show = False,
                 print_max = 1,threshold = 0,add_county_line = False,map_extend = None,dpi = 300,title="均方根误差站点分布"):
    if len(sta_ob_and_fos.index) == 0:
        print("error infomation: 站点数据内容为空")
        return

    if s is not None:
        if g is not None:
            if g == "last_range" or g == "last_step":
                s["drop_last"] = False
            else:
                s["drop_last"] = True
    if g == "id":
        print("绘制误差平面分布时，g 不能设置为id")
        return
    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos,s = s)
    sta_ob_and_fos_list, gll1 = meteva.base.group(sta_ob_and_fos1, g = g, gll = gll)
    g_num = len(sta_ob_and_fos_list)
    #if(g_num == 1):gll1 = [None]
    if group_name_list is None:
        group_name_list = meteva.product.program.get_group_name(gll1)

    for k in range(g_num):
        sta_ob_and_fos_g1 = sta_ob_and_fos_list[k]
        rmse_sta = meteva.product.score_id(sta_ob_and_fos_g1,meteva.method.rmse)[0]
        #values = rmse_sta.values[:,6:]

        '''
        mean_value = np.mean(values)
        data_names = meteva.base.get_stadata_names(rmse_sta)

        vmax = np.max(values)
        vmin = np.min(values)
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
        '''

        title1 = meteva.product.program.get_title_from_dict(meteva.product.rmse_scatter, s, g, group_name_list[k],"NNN")
        if save_path is None:
            if save_dir is None:
                save_path = None
                show = True
            else:
                fileName = title1.replace("\n", "").replace(":", "")
                save_path = save_dir + "/" + fileName + ".png"
        if save_path is not None: meteva.base.creat_path(save_path)
        meteva.base.tool.plot_tools.scatter_sta(rmse_sta, save_path=save_path, show=show,
                                                fix_size=False, title=title1, print_max=print_max
                                                , add_county_line=add_county_line,
                                                threshold=threshold, map_extend=map_extend, dpi=dpi)

        '''
        for di in range(len(data_names)):
            data_name = data_names[di]
            title1 = meteva.product.program.get_title_from_dict(meteva.product.rmse_scatter, s, g, group_name_list[k],
                                                                data_name)
            if save_path is None:
                if save_dir is None:
                    save_path = None
                    show = True
                else:
                    fileName  = title1.replace("\n","").replace(":","")
                    save_path = save_dir + "/"+fileName+".png"
            if save_path is not None:meteva.base.creat_path(save_path)
            meteva.base.tool.plot_tools.scatter_sta(rmse_sta,value_column = di,save_path= save_path,show = show,
                                                    clevs= clevs1,fix_size=False,title=title1,print_max = print_max
                                                    ,mean_value = mean_value,add_county_line=add_county_line,threshold=threshold,map_extend=map_extend,dpi = dpi)

            if save_path is not None:
                print("图片输出至"+save_path)
                save_path = None
            '''

def mae_scatter(sta_ob_and_fos,s = None,g = None,gll = None,group_name_list= None, save_dir=None,save_path = None,show = False,
                print_max = 1,threshold = 0,add_county_line = False,map_extend= None,dpi = 300,title="绝对误差站点分布图"):

    if len(sta_ob_and_fos.index) == 0:
        print("error infomation: 站点数据内容为空")
        return

    if s is not None:
        if g is not None:
            if g == "last_range" or g == "last_step":
                s["drop_last"] = False
            else:
                s["drop_last"] = True
    if g == "id":
        print("绘制误差平面分布时，g 不能设置为id")
        return

    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos,s = s)
    sta_ob_and_fos_list, gll1 = meteva.base.group(sta_ob_and_fos1, g = g, gll = gll)
    g_num = len(sta_ob_and_fos_list)
    if(g_num == 1):gll1 = [None]
    if group_name_list is None:
        group_name_list = meteva.product.program.get_group_name(gll1)
    for k in range(g_num):
        sta_ob_and_fos_g1 = sta_ob_and_fos_list[k]
        rmse_sta = meteva.product.score_id(sta_ob_and_fos_g1,meteva.method.mae)[0]

        title1 = meteva.product.program.get_title_from_dict(meteva.product.mae_scatter, s, g, group_name_list[k],"NNN")
        if save_path is None:
            if save_dir is None:
                save_path = None
                show = True
            else:
                fileName = title1.replace("\n", "").replace(":", "")
                save_path = save_dir + "/" + fileName + ".png"
        if save_path is not None: meteva.base.creat_path(save_path)
        meteva.base.tool.plot_tools.scatter_sta(rmse_sta, save_path=save_path, show=show,
                                                fix_size=False, title=title1, print_max=print_max
                                                , add_county_line=add_county_line,
                                                threshold=threshold, map_extend=map_extend, dpi=dpi)

        '''
        values = rmse_sta.values[:, 6:]
        mean_value = np.mean(values)
        data_names = meteva.base.get_stadata_names(rmse_sta)
        vmax = np.max(values)
        vmin = np.min(values)
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
        for di in range(len(data_names)):
            data_name = data_names[di]
            title1 = meteva.product.program.get_title_from_dict(meteva.product.mae_scatter, s,  g, group_name_list[k],
                                                                data_name)
            if save_path is None:
                if save_dir is None:
                    save_path = None
                    show = True
                else:
                    fileName  = title1.replace("\n","").replace(":","")
                    save_path = save_dir + "/"+fileName+".png"
            if save_path is not None:meteva.base.creat_path(save_path)
            meteva.base.tool.plot_tools.scatter_sta(rmse_sta,value_column = di,
                                                    save_path= save_path,show= show,fix_size=False,clevs=clevs1,title=title1,print_max = print_max,
                                                    mean_value = mean_value, threshold = threshold,add_county_line = add_county_line,map_extend= map_extend,dpi = dpi)
            if save_path is not None:
                print("图片输出至"+save_path)
                save_path = None
                
        '''

def me_scatter(sta_ob_and_fos,s= None,g = None,gll = None,group_name_list= None, save_dir=None,save_path = None,show = False,
               print_max = 1,print_min = 1,threshold = 0,add_county_line = False,map_extend= None,dpi = 300,title="误差站点分布图"):
    if len(sta_ob_and_fos.index) == 0:
        print("error infomation: 站点数据内容为空")
        return

    if s is not None:
        if g is not None:
            if g == "last_range" or g == "last_step":
                s["drop_last"] = False
            else:
                s["drop_last"] = True
    if g == "id":
        print("绘制误差平面分布时，g 不能设置为id")
        return

    sta_ob_and_fos1 = meteva.base.sele_by_dict(sta_ob_and_fos,s = s)
    sta_ob_and_fos_list, gll1 = meteva.base.group(sta_ob_and_fos1, g = g, gll = gll)

    g_num = len(sta_ob_and_fos_list)
    if(g_num == 1):gll1 = [None]
    if group_name_list is None:
        group_name_list = meteva.product.program.get_group_name(gll1)
    for k in range(g_num):
        sta_ob_and_fos_g1 = sta_ob_and_fos_list[k]
        rmse_sta = meteva.product.score_id(sta_ob_and_fos_g1,meteva.method.me)[0]
        title1 = meteva.product.program.get_title_from_dict(meteva.product.me_scatter, s, g, group_name_list[k],"NNN")
        if save_path is None:
            if save_dir is None:
                save_path = None
                show = True
            else:
                fileName = title1.replace("\n", "").replace(":", "")
                save_path = save_dir + "/" + fileName + ".png"
        if save_path is not None: meteva.base.creat_path(save_path)

        meteva.base.tool.plot_tools.scatter_sta(rmse_sta, save_path=save_path, show=show,
                                                fix_size=False, title=title1, print_max=print_max,print_min=print_min
                                                , add_county_line=add_county_line,
                                                threshold=threshold, map_extend=map_extend, dpi=dpi)

        '''
        values = rmse_sta.values[:, 6:]
        mean_value = np.mean(np.abs(values))
        data_names = meteva.base.get_stadata_names(rmse_sta)
        vmax = np.max(values)
        vmin = np.min(values)
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
        vmaxmax = np.max([-vmin,vmax])
        vmin = -vmaxmax
        vmax = vmaxmax
        clevs1 = np.arange(vmin, vmax, inte)

        for di in range(len(data_names)):
            data_name = data_names[di]
            title1 = meteva.product.program.get_title_from_dict(meteva.product.me_scatter, s,  g, group_name_list[k],
                                                                data_name)
            if save_path is None:
                if save_dir is None:
                    save_path = None
                    show = True
                else:
                    fileName  = title1.replace("\n","").replace(":","")
                    save_path = save_dir + "/"+fileName+".png"

            if save_path is not None:meteva.base.creat_path(save_path)
            meteva.base.tool.plot_tools.scatter_sta(rmse_sta, value_column=di, save_path=save_path,show = show, fix_size=False,
                                                        clevs=clevs1, title=title1,print_max = print_max,print_min=print_min,
                                                    mean_value=mean_value, threshold=threshold,add_county_line = add_county_line,map_extend = map_extend,dpi = dpi)
            if save_path is not None:
                print("图片输出至"+save_path)
                save_path = None
        '''