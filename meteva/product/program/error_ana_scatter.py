import meteva
import numpy as np
import math


def error_scatter(sta_ob_and_fos,method,s = None,g = None,gll = None,group_name_list= None,save_dir=None,save_path = None,show = False,
                 print_max = 0,print_min = 0,threshold = 0,add_county_line = False,map_extend = None,dpi = 300,title=None,
                  sup_fontsize=10,
                  height=None, width=None
                  ):
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
    if(len(sta_ob_and_fos1.index) == 0):
        print("there is no data to verify")
        return
    sta_ob_and_fos_list, gll1 = meteva.base.group(sta_ob_and_fos1, g = g, gll = gll)
    g_num = len(sta_ob_and_fos_list)
    #if(g_num == 1):gll1 = [None]
    if group_name_list is None:
        group_name_list = meteva.product.program.get_group_name(gll1)

    data_names = meteva.base.get_stadata_names(sta_ob_and_fos_list[0])
    fo_num = len(data_names) - 1

    if isinstance(title, list):
        if fo_num * g_num != len(title):
            print("手动设置的title数目和要绘制的图形数目不一致")
            return

    if save_path is not None:
        if isinstance(save_path, str):
            save_path = [save_path]
        if fo_num * g_num != len(save_path):
            print("手动设置的save_path数目和要绘制的图形数目不一致")
            return

    for k in range(g_num):
        sta_ob_and_fos_g1 = sta_ob_and_fos_list[k]
        rmse_sta = meteva.product.score_id(sta_ob_and_fos_g1,method)[0]

        if isinstance(title, list):
            title1 = title[k * fo_num: (k + 1) * fo_num]
        else:
            title1 = []
            for i in range(fo_num):
                title1.append(meteva.product.program.get_title_from_dict(title, s, g, group_name_list[k], data_names[i+1]))

        save_path1 = None
        if save_path is None:
            if save_dir is None:
                show = True
            else:
                save_path1 = []
                for i in range(len(title1)):
                    fileName = title1[i].replace("\n", "").replace(":", "")
                    save_path1.append(save_dir + "/" + fileName + ".png")
        else:
            save_path1 = save_path[k * fo_num: (k + 1) * fo_num]
        meteva.base.tool.plot_tools.scatter_sta(rmse_sta, save_path=save_path1, show=show,
                                                fix_size=False, title=title1, print_max=print_max,print_min = print_min
                                                , add_county_line=add_county_line,
                                                threshold=threshold, map_extend=map_extend, dpi=dpi,sup_fontsize = sup_fontsize,
                                                width = width,height=height)

def rmse_scatter(sta_ob_and_fos,s = None,g = None,gll = None,group_name_list= None,save_dir=None,save_path = None,show = False,
                 print_max = 1,threshold = 0,add_county_line = False,map_extend = None,dpi = 300,title="均方根误差站点分布",
                 sup_fontsize=10,
                 height=None, width=None
                 ):

    error_scatter(sta_ob_and_fos,meteva.method.rmse,s = s,g = g,gll = gll,group_name_list= group_name_list,
                  save_dir= save_dir,save_path = save_path,show = show,print_max =print_max,threshold = threshold,
                  add_county_line= add_county_line,map_extend=map_extend,dpi = dpi,title = title,
                  sup_fontsize=sup_fontsize,
                  height=height, width=width
                  )

def mae_scatter(sta_ob_and_fos,s = None,g = None,gll = None,group_name_list= None, save_dir=None,save_path = None,show = False,
                print_max = 1,threshold = 0,add_county_line = False,map_extend= None,dpi = 300,title="绝对误差站点分布图",
                sup_fontsize=10,
                height=None, width=None
                ):

    error_scatter(sta_ob_and_fos,meteva.method.mae,s = s,g = g,gll = gll,group_name_list= group_name_list,
                  save_dir= save_dir,save_path = save_path,show = show,print_max =print_max,threshold = threshold,
                  add_county_line= add_county_line,map_extend=map_extend,dpi = dpi,title = title,
                  sup_fontsize=sup_fontsize,
                  height=height, width=width
                  )



def me_scatter(sta_ob_and_fos,s= None,g = None,gll = None,group_name_list= None, save_dir=None,save_path = None,show = False,
               print_max = 1,print_min = 1,threshold = 0,add_county_line = False,map_extend= None,dpi = 300,title="误差站点分布图",
               sup_fontsize=10,
               height=None, width=None
               ):

    error_scatter(sta_ob_and_fos,meteva.method.me,s = s,g = g,gll = gll,group_name_list= group_name_list,
                  save_dir= save_dir,save_path = save_path,show = show,print_max =print_max,print_min = print_min,
                  threshold = threshold,add_county_line= add_county_line,map_extend=map_extend,dpi = dpi,title = title,
                  sup_fontsize=sup_fontsize,
                  height=height, width=width
                  )
