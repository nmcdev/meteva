import matplotlib.colors as colors
import numpy as np
import matplotlib.pyplot as plt
import copy
from matplotlib.colors import BoundaryNorm
import matplotlib.patches as patches




def creat_cmap_from_rgb(rgb_list_list,extend = None):
    if isinstance(rgb_list_list[0],list):
        colors_list = np.array(rgb_list_list)/256
    else:
        colors_list =rgb_list_list
    if extend == 'min':
        cmap = colors.ListedColormap(colors_list[1:])
        cmap.set_under(colors_list[0])
    elif extend == 'max':
        cmap = colors.ListedColormap(colors_list[:-1])
        cmap.set_over(colors_list[-1])
    elif extend == 'both':
        cmap = colors.ListedColormap(colors_list[1:-1])
        cmap.set_under(colors_list[0])
        cmap.set_over(colors_list[-1])
    else:
        cmap = colors.ListedColormap(colors_list)

    return cmap


def score_skill_seaborn(score_array_list,title_list,discription_list,member_list,dtime_list,save_path = None,show = False):

    rgb_list_list = [
        "#00529F", "#0072BB", "#0694CB", "#56B1DA", "#92CCE4", "#C1DCF1", "#DBECF8",
        "#F1F1F1",
        "#FEDECF", "#FFB79B", "#FE8968", "#FF5C3B", "#FF1513", "#DC0002", "#B20000"
    ]
    clevs = [-50, -25, -15, -10, -5, -2, -1, 1, 2, 5, 10, 15, 25, 50]
    cmap = creat_cmap_from_rgb(rgb_list_list)

    xlabels = np.array(dtime_list)/24
    ylabels = member_list[::-1]

    nscore = len(score_array_list)
    skill_list = []
    score_re_list = []  #
    for k in range(nscore):
        score_re = score_array_list[k][::-1 ,:]
        score_re_list.append(score_re)
        skill = 100 * (score_re - score_re[-1, :]) / score_re[-1, :]
        skill_list.append(skill)
    # cmap,clevs = meb.def_cmap_clevs(meb.cmaps.me,clevs=[-50,-25,-15,-10,-5,-2,-1,1,2,5,10,15,25,50])
    fig = plt.figure(figsize=(12.5, 2.5), dpi=600)
    plt.subplots_adjust(wspace=0.05)
    annot_list = [0, 1, 1, 1, 1]
    for k in range(nscore):
        ax_one = plt.subplot(1, nscore, k + 1)
        data_k = copy.deepcopy(skill_list[k])
        nx = data_k.shape[1]
        ny = data_k.shape[0]
        x = np.arange(nx + 1) - 0.5
        y = np.arange(ny + 1) - 0.5
        norm = BoundaryNorm(clevs, ncolors=cmap.N + 1, extend="both")
        im = ax_one.pcolormesh(x, y, data_k, cmap=cmap, norm=norm, linewidths=2, edgecolor="w")
        ax_one.spines['bottom'].set_linewidth(0)
        ax_one.spines['top'].set_linewidth(0)
        ax_one.spines['right'].set_linewidth(0)
        ax_one.spines['left'].set_linewidth(0)
        fmt_tag = "%." + str(annot_list[k]) + "f"
        data = copy.deepcopy(score_re_list[k])

        for j in range(ny):
            for i in range(nx):
                data_ijk = data_k[j, i]
                if not np.isnan(data_ijk):
                    ax_one.text(i, j, fmt_tag % data[j, i], ha="center", va="center", fontsize=10, c="k")
                rect = patches.Rectangle((i - 0.45, j - 0.45), 0.9, 0.9, linewidth=0.1, edgecolor='gray',
                                         facecolor='none')
                ax_one.add_patch(rect)
            rect = patches.Rectangle((-0.45, j - 0.45), 4.9, 0.9, linewidth=0.3, edgecolor='gray', facecolor='none')
            ax_one.add_patch(rect)
        # ax_one.set_xticks(np.arange(nx))
        plt.xticks(np.arange(nx), xlabels, fontsize=11, family='Times New Roman')
        plt.xlabel("Lead time[days]", fontsize=12)
        if k == 0:
            plt.yticks(np.arange(5).tolist(), ylabels, fontsize=12)
        else:
            plt.yticks([])
        plt.title(discription_list[k], fontsize=8)
        plt.text(2, 5.3, title_list[k], fontsize=14, ha="center", va="center")

    location = [0.2, -0.15, 0.6, 0.05]
    colorbar_position = fig.add_axes(location)  # 位置[左,下,宽,高]
    plt.colorbar(im, cax=colorbar_position, orientation="horizontal",
                 ticks=clevs, label="Better <- % difference in RMSE vs ECMWF -> Worse")
    if save_path is None:
        show = True
    else:
        plt.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close()

def rmse_skill_seaborn(rmse_z ,rmse_t ,rmse_q ,rmse_ws ,rmse_t2m ,member_list,dtime_list,save_path= None,show = False):
    score_array_list = [rmse_z, rmse_t, rmse_t2m, rmse_q, rmse_ws]
    title_list = ["Geopotential" ,"Temperature" ,"Temperature" ,"Humidity" ,"Wind Speed"]
    discription_list = ["500hPa geopotential RMSE[m$^{2}$/s$^{2}$]" ,"850hPa temperature RMSE[K]",
                     "2m temperature RMSE[K]",
                     "700hPa specific humidity RMSE[g/kg]" ,"850hPa wind vector RMSE[m/s]"]
    score_skill_seaborn(score_array_list, title_list, discription_list,member_list,dtime_list, save_path=save_path, show=show)


def seaborn_score_bak(rmse_z ,rmse_t ,rmse_q ,rmse_ws ,rmse_t2m ,g_dict,save_path= None,show = False):

    rmse_z = rmse_z[::-1 ,:]
    rmse_t = rmse_t[::-1 ,:]
    rmse_q = rmse_q[::-1 ,:]
    rmse_ws = rmse_ws[::-1 ,:]
    rmse_t2m = rmse_t2m[::-1 ,:]

    rgb_list_list =[
        "#00529F", "#0072BB",  "#0694CB" ,"#56B1DA" ,"#92CCE4" ,"#C1DCF1" ,"#DBECF8",
        "#F1F1F1",
        "#FEDECF" ,"#FFB79B" ,"#FE8968" ,"#FF5C3B" ,"#FF1513" ,"#DC0002" ,"#B20000"
    ]
    clevs =[-50 ,-25 ,-15 ,-10 ,-5 ,-2 ,-1 ,1 ,2 ,5 ,10 ,15 ,25 ,50]
    cmap = creat_cmap_from_rgb(rgb_list_list)


    xlabels = [1 ,3 ,5 ,7 ,10]
    ylabels = g_dict["member"][::-1]
    titles = ["Geopotential" ,"Temperature" ,"Temperature" ,"Humidity" ,"Wind Speed"]
    titles_little = ["500hPa geopotential RMSE[m$^{2}$/s$^{2}$]" ,"850hPa temperature RMSE[K]",
                     "2m temperature RMSE[K]",
                     "700hPa specific humidity RMSE[g/kg]" ,"850hPa wind vector RMSE[m/s]"]

    skill_z = 100 *(rmse_z - rmse_z[-1 ,:] ) /rmse_z[-1 ,:]
    skill_t = 100 *(rmse_t - rmse_t[-1 ,:] ) /rmse_t[-1 ,:]
    skill_t2m = 100 *(rmse_t2m - rmse_t2m[-1 ,:] ) /rmse_t2m[-1 ,:]
    skill_q = 100 *(rmse_q - rmse_q[-1 ,:] ) /rmse_q[-1 ,:]
    skill_ws = 100 *(rmse_ws - rmse_ws[-1 ,:] ) /rmse_ws[-1 ,:]

    skill_list =[skill_z, skill_t, skill_t2m, skill_q, skill_ws]
    rmse_list = [rmse_z, rmse_t, rmse_t2m, rmse_q, rmse_ws]
    # cmap,clevs = meb.def_cmap_clevs(meb.cmaps.me,clevs=[-50,-25,-15,-10,-5,-2,-1,1,2,5,10,15,25,50])
    fig = plt.figure(figsize=(12.5, 2.5), dpi=600)
    plt.subplots_adjust(wspace=0.05)
    annot_list = [0, 1, 1, 1, 1]
    for k in range(5):
        ax_one = plt.subplot(1, 5, k + 1)
        data_k = copy.deepcopy(skill_list[k])
        nx = data_k.shape[1]
        ny = data_k.shape[0]
        x = np.arange(nx + 1) - 0.5
        y = np.arange(ny + 1) - 0.5
        norm = BoundaryNorm(clevs, ncolors=cmap.N + 1, extend="both")
        im = ax_one.pcolormesh(x, y, data_k, cmap=cmap, norm=norm, linewidths=2, edgecolor="w")
        ax_one.spines['bottom'].set_linewidth(0)
        ax_one.spines['top'].set_linewidth(0)
        ax_one.spines['right'].set_linewidth(0)
        ax_one.spines['left'].set_linewidth(0)
        fmt_tag = "%." + str(annot_list[k]) + "f"
        data = copy.deepcopy(rmse_list[k])

        for j in range(ny):
            for i in range(nx):
                data_ijk = data_k[j, i]
                if not np.isnan(data_ijk):
                    ax_one.text(i, j, fmt_tag % data[j, i], ha="center", va="center", fontsize=10, c="k")
                rect = patches.Rectangle((i - 0.45, j - 0.45), 0.9, 0.9, linewidth=0.1, edgecolor='gray',
                                         facecolor='none')
                ax_one.add_patch(rect)
            rect = patches.Rectangle((-0.45, j - 0.45), 4.9, 0.9, linewidth=0.3, edgecolor='gray', facecolor='none')
            ax_one.add_patch(rect)
        # ax_one.set_xticks(np.arange(nx))
        plt.xticks(np.arange(nx), xlabels, fontsize=11, family='Times New Roman')
        plt.xlabel("Lead time[days]", fontsize=12)
        if k == 0:
            plt.yticks(np.arange(5).tolist(), ylabels, fontsize=12)
        else:
            plt.yticks([])
        plt.title(titles_little[k], fontsize=8)
        plt.text(2, 5.3, titles[k], fontsize=14, ha="center", va="center")

    location = [0.2, -0.15, 0.6, 0.05]
    colorbar_position = fig.add_axes(location)  # 位置[左,下,宽,高]
    plt.colorbar(im, cax=colorbar_position, orientation="horizontal",
                 ticks=clevs, label="Better <- % difference in RMSE vs ECMWF -> Worse")

    if save_path is None:
        show = True
    else:
        plt.savefig(save_path, bbox_inches="tight")
    if show:
        plt.show()
    plt.close()

if __name__ =="__main__":
    import pandas as pd
    import meteva.method as mem
    import meteva.perspact as mps  # 透视分析模块
    middle_result_path = r"H:\task\other\202308-AImodel\mid\z_tase_cli.h5"
    df_tase_z_cli = pd.read_hdf(middle_result_path)
    rmse_z500, gdict = mps.score_df(df_tase_z_cli, mem.rmse,
                                    s={"time_range": ["2022040108", "2023040108"], "level": 500,
                                       "dtime": [24, 72, 120, 168, 240]},
                                    g=["member", "dtime"],
                                    gll_dict={"member": ["ECMWF", "PANGU", "FENGWU", "FUXI", "Climatology"]})

    middle_result_path = r"H:\task\other\202308-AImodel\mid\t_tase_cli.h5"
    df_tase_t_cli = pd.read_hdf(middle_result_path)
    rmse_t850, gdict = mps.score_df(df_tase_t_cli, mem.rmse,
                                    s={"time_range": ["2022040108", "2023040108"], "level": 850,
                                       "dtime": [24, 72, 120, 168, 240]},
                                    g=["member", "dtime"],
                                    gll_dict={"member": ["ECMWF", "PANGU", "FENGWU", "FUXI", "Climatology"]})

    middle_result_path = r"H:\task\other\202308-AImodel\mid\speed_tase_cli.h5"
    df_tase_speed_cli = pd.read_hdf(middle_result_path)
    rmse_speed850, gdict = mps.score_df(df_tase_speed_cli, mem.rmse,
                                        s={"time_range": ["2022040108", "2023040108"], "level": 850
                                            , "dtime": [24, 72, 120, 168, 240]}, g=["member", "dtime"]
                                        , gll_dict={"member": ["ECMWF", "PANGU", "FENGWU", "FUXI", "Climatology"]})

    middle_result_path = r"H:\task\other\202308-AImodel\mid\q_tase_cli.h5"
    df_tase_q_cli = pd.read_hdf(middle_result_path)
    rmse_q700, gdict = mps.score_df(df_tase_q_cli, mem.rmse, s={"time_range": ["2022040108", "2023040108"], "level": 850
        , "dtime": [24, 72, 120, 168, 240]}, g=["member", "dtime"]
                                    , gll_dict={"member": ["ECMWF", "PANGU", "FENGWU", "FUXI", "Climatology"]})

    middle_result_path = r"H:\task\other\202308-AImodel\mid\t2m_tase_cli.h5"
    df_tase_t2m_cli = pd.read_hdf(middle_result_path)
    rmse_t2m, gdict = mps.score_df(df_tase_t2m_cli, mem.rmse, s={"time_range": ["2022040108", "2023040108"], "level": 2,
                                                                 "dtime": [24, 72, 120, 168, 240]},
                                   g=["member", "dtime"],
                                   gll_dict={"member": ["ECMWF", "PANGU", "FENGWU", "FUXI", "Climatology"]})

    rmse_skill_seaborn(rmse_z500, rmse_t850, rmse_q700, rmse_speed850, rmse_t2m, gdict["member"],gdict["dtime"],
                  save_path=r"H:\task\other\202308-AImodel\png\comprehensive.png")