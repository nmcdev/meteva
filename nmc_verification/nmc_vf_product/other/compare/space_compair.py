import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
import numpy  as np
import cartopy.crs as ccrs

from nmc_met_graphics.plot.china_map import add_china_map_2cartopy
from nmc_verification.nmc_vf_base import function
from sklearn.linear_model import LinearRegression
# import nmc_vf_base as nvb
from nmc_verification.nmc_vf_method import continuous
from nmc_verification.nmc_vf_method import yes_or_no

# 绘制24小时格点站点降水检验图
def draw_veri_rain_24(grid_fo, sta_ob, filename=None):
    fig = plt.figure(figsize=(10, 7))
    # 平面对比图
    rect1 = [0.00, 0.42, 0.7, 0.55]  # 左下宽高
    datacrs = ccrs.PlateCarree()
    ax = plt.axes(rect1, projection=datacrs)
    # 设置地图背景
    map_extent = [grid_fo.slon, grid_fo.elon, grid_fo.slat, grid_fo.elat]
    ax.set_extent(map_extent, crs=datacrs)
    add_china_map_2cartopy(ax, name='province', edgecolor='k', lw=0.3)  # 省界
    add_china_map_2cartopy(ax, name='river', edgecolor='blue', lw=0.3)  # 河流

    # 绘制格点预报场
    x = np.arange(grid_fo.nlon) * grid_fo.dlon + grid_fo.slon
    y = np.arange(grid_fo.nlat) * grid_fo.dlat + grid_fo.slat
    clevs = [0.1, 10, 25, 50, 100, 250, 1000]
    colors_grid = ["#E0EEFA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    plot_grid = ax.contourf(x, y, grid_fo.dat, clevs, colors=colors_grid, transform=datacrs)  # 填色图

    colorbar_position_grid = fig.add_axes([0.035, 0.94, 0.25, 0.015])  # 位置[左,下,宽,高]
    plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='horizontal')
    plt.text(0.035, 0.955, "model accumulated precipition(mm)", fontsize=10)
    # 绘制填色站点值
    sta_ob_in = function.get_from_sta_data.sta_in_grid_xy(sta_ob, grid=grid_fo.grid)
    colors_sta = ['#FFFFFF', '#0055FF', '#00FFB4', '#F4FF00', '#FE1B00', '#910000', '#B800BA']
    dat = sta_ob_in.values[:, 2]
    dat[dat > 1000] = 0
    clevs = [0, 0.1, 10, 25, 50, 100, 250, 1000]
    cleves_name = ["0", "0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"]
    for i in range(len(clevs) - 1):
        index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
        if (len(index0[0]) > 0):
            x = np.squeeze(sta_ob_in.values[index0, 0])
            y = np.squeeze(sta_ob_in.values[index0, 1])
            if (len(index0) == 1):
                x = np.array([x])
                y = np.array([y])
                if (i > 0):
                    ax.scatter(x, y, c=colors_sta[i], transform=ccrs.PlateCarree(), s=3, label=cleves_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i], transform=ccrs.PlateCarree(), s=1, label=cleves_name[i])
    ax.legend(facecolor='whitesmoke', title="observation", loc="lower left", edgecolor='whitesmoke')

    # 散点回归图
    rect2 = [0.07, 0.07, 0.21, 0.30]  # 左下宽高
    ax2 = plt.axes(rect2)
    sta_fo = function.gxy_sxy.interpolation_linear(grid_fo, sta_ob_in)

    ob = sta_ob_in.values[:, 2]
    fo = sta_fo.values[:, 2]
    ax2.plot(ob, fo, '.', color='k')

    # 绘制比例线
    rate = np.sum(fo) / np.sum(ob)
    ob_line = np.arange(0, np.max(ob), np.max(ob) / 30)
    fo_rate = ob_line * rate
    ax2.plot(ob_line[0:20], fo_rate[0:20], 'r')

    # 绘制回归线
    X = np.zeros((len(ob), 1))
    X[:, 0] = ob[:]
    clf = LinearRegression().fit(X, fo)
    X = np.zeros((len(ob_line), 1))
    X[:, 0] = ob_line[:]
    fo_rg = clf.predict(X)
    ax2.plot(ob_line, fo_rg, color='b', linestyle='dashed')
    rg_text1 = "R = " + '%.2f' % (np.corrcoef(ob, fo)[0, 1])
    rg_text2 = "y = " + '%.2f' % (clf.coef_[0]) + "* x + " + '%.2f' % (clf.intercept_)

    maxy = max(np.max(ob), np.max(fo)) + 5
    plt.xlim(0, maxy)
    plt.ylim(0, maxy)
    plt.text(0.05 * maxy, 0.9 * maxy, rg_text1, fontsize=10)
    plt.text(0.05 * maxy, 0.8 * maxy, rg_text2, fontsize=10)
    maxy = max(np.max(ob), np.max(fo))
    ax2.set_xlabel("observation", fontsize=12)
    ax2.set_ylabel("precipitation", fontsize=12)
    ax2.set_title("Obs.vs Pred. Scatter plot", fontsize=12)
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
    ax3.set_xticklabels(["0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"], fontsize=9)
    ax3.set_ylabel("point number", fontsize=10)
    ax3.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(100))

    # 绘制降水站点实况预报统计表
    rect4 = [0.325, 0.255, 0.4, 0.10]  # 左下宽高
    ax4 = plt.axes(rect4)
    ax4.axes.set_axis_off()

    ob_has = ob[ob >= 0.01]
    fo_has = fo[fo >= 0.01]
    text = "制降水站点实况预报 n=" + str(len(ob)) + "\n"
    text += "=======================================================\n"
    text += "                         observation      Predication\n"
    text += "-------------------------------------------------------\n"
    text += "有降水站点数(>=0.01)        " + "%4d" % len(ob_has) + "                %4d" % len(fo_has) + "\n"
    text += "有降水站点数百分比%     " + "%8.2f" % (len(ob_has) / len(ob)) + "%20.2f" % (len(fo_has) / len(fo)) + "\n"
    text += "平均降水量(排除无降水)  " + "%8.2f" % (np.mean(ob_has)) + "%20.2f" % (np.mean(fo_has)) + "\n"
    text += "最大降水量              " + "%8.2f" % (np.max(ob_has)) + "%20.2f" % (np.max(fo_has))
    plt.text(0, 0, text, fontsize=9)

    # 绘制统计检验结果
    rect5 = [0.705, 0.01, 0.28, 0.97]  # 左下宽高
    ax5 = plt.axes(rect5)
    ax5.axes.set_axis_off()

    mae = continuous.score.mae(ob, fo)
    me = continuous.score.me(ob, fo)
    mse = continuous.score.mse(ob, fo)
    rmse = continuous.score.rmse(ob, fo)
    bias_c = continuous.score.bias(ob, fo)
    cor = continuous.score.corr(ob, fo)
    hit, mis, fal, co = yes_or_no.score.hmfn(ob, fo, clevs[1:])
    ts = yes_or_no.score.ts(ob, fo, clevs[1:])
    ets = yes_or_no.score.ets(ob, fo, clevs[1:])
    bias = yes_or_no.score.bias(ob, fo, clevs[1:])
    hit_rate = yes_or_no.score.hit_rate(ob, fo, clevs[1:])
    mis_rate = yes_or_no.score.mis_rate(ob, fo, clevs[1:])
    fal_rate = yes_or_no.score.fal_rate(ob, fo, clevs[1:])
    text = str(len(ob)) + "评分站点预报检验统计量\n"
    text += "Mean absolute error:" + "%6.2f" % mae + "\n"
    text += "Mean error:" + "%6.2f" % me + "\n"
    text += "Mean-squared error:" + "%6.2f" % mse + "\n"
    text += "Root mean-squared error:" + "%6.2f" % rmse + "\n"
    text += "Bias:" + "%6.2f" % bias_c + "\n"
    text += "Correctlation coefficiant:" + "%6.2f" % cor + "\n\n\n"
    leves_name = ["0.1-10-", "10-25--", "25-50--", "50-100-", "100-250", ">=250-"]
    for i in range(len(leves_name)):
        text += ":" + leves_name[i] + "----------------------------\n"
        text += "正确:" + "%-4d" % hit[i] + " 空报:" + "%-4d" % fal[i] + " 漏报:" + "%-4d" % mis[i] + "\n"
        text += "TS:" + "%5.3f" % ts[i] + "                  ETS:" + "%5.3f" % ets[i] + "\n"
        text += "Hit rate:" + "%5.3f" % hit_rate[i] + "     Miss rate: " + "%5.3f" % mis_rate[i] + "\n"
        text += "False alarm ratio:" + "%5.3f" % fal_rate[i] + "  Bias:" + "%5.3f" % bias[i] + "\n\n"
    plt.text(0, 0.00, text, fontsize=11)

    # 图片显示或保存
    if (filename is None):
        plt.show()
    else:
        plt.savefig(filename, dpi=300)
    plt.close()
    return


# 绘制24小时降水实况与预报对比图
def show_obfo_rain_24(grid_fo, sta_ob, filename=None):
    fig = plt.figure(figsize=(6, 3.6))
    # 平面对比图
    rect1 = [0.01, 0.01, 0.98, 0.98]  # 左下宽高
    datacrs = ccrs.PlateCarree()
    ax = plt.axes(rect1, projection=datacrs)
    # 设置地图背景
    map_extent = [grid_fo.slon, grid_fo.elon, grid_fo.slat, grid_fo.elat]
    ax.set_extent(map_extent, crs=datacrs)
    add_china_map_2cartopy(ax, name='province', edgecolor='k', lw=0.3)  # 省界
    add_china_map_2cartopy(ax, name='river', edgecolor='blue', lw=0.3)  # 河流

    # 绘制格点预报场
    x = np.arange(grid_fo.nlon) * grid_fo.dlon + grid_fo.slon
    y = np.arange(grid_fo.nlat) * grid_fo.dlat + grid_fo.slat
    clevs = [0.1, 10, 25, 50, 100, 250, 1000]
    colors_grid = ["#E0EEFA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    plot_grid = ax.contourf(x, y, grid_fo.dat, clevs, colors=colors_grid, transform=datacrs)  # 填色图

    colorbar_position_grid = fig.add_axes([0.035, 0.94, 0.25, 0.015])  # 位置[左,下,宽,高]
    plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='horizontal')
    plt.text(0.035, 0.955, "model accumulated precipition(mm)", fontsize=10)
    # 绘制填色站点值
    sta_ob_in = function.get_from_sta_data.sta_in_grid_xy(sta_ob, grid=grid_fo.grid)
    colors_sta = ['#FFFFFF', '#0055FF', '#00FFB4', '#F4FF00', '#FE1B00', '#910000', '#B800BA']
    dat = sta_ob_in.values[:, 2]
    dat[dat > 1000] = 0
    clevs = [0, 0.1, 10, 25, 50, 100, 250, 1000]
    cleves_name = ["0", "0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"]
    for i in range(len(clevs) - 1):
        index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
        if (len(index0[0]) > 0):
            x = np.squeeze(sta_ob_in.values[index0, 0])
            y = np.squeeze(sta_ob_in.values[index0, 1])
            if (len(index0) == 1):
                x = np.array([x])
                y = np.array([y])
                if (i > 0):
                    ax.scatter(x, y, c=colors_sta[i], transform=ccrs.PlateCarree(), s=3, label=cleves_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i], transform=ccrs.PlateCarree(), s=1, label=cleves_name[i])
    ax.legend(facecolor='whitesmoke', title="observation", loc="lower left", edgecolor='whitesmoke')

    # 图片显示或保存
    if (filename is None):
        plt.show()
    else:
        plt.savefig(filename, dpi=300)
    plt.close()
    return
