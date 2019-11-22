import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import numpy  as np
import cartopy.crs as ccrs
from nmc_met_graphics.plot.china_map import add_china_map_2cartopy
#import nmc_met_class.basicdatatrans as bt
from sklearn.linear_model import LinearRegression
import nmc_verification

def rain_24h_sg(sta_ob,grd_fo,  filename=None):
    '''
    #绘制24小时降水实况与预报对比图
    :param grd_fo: 输入的网格数据，包含一个平面的网格场
    :param sta_ob:  输入的站点数据，包含一个时刻的站点数据列表
    :param filename: 图片输出路径，缺省时会以调试窗口形式弹出
    :return: 无返回值
    '''
    grid_fo = nmc_verification.nmc_vf_base.get_grid_of_data(grd_fo)
    # 通过经纬度范围设置画幅
    hight = 5.6
    title_hight = 0.3
    legend_hight = 0.6
    left_plots_width = 0
    right_plots_width = 0
    width = (hight - title_hight - legend_hight) * grid_fo.nlon / grid_fo.nlat + left_plots_width + right_plots_width
    map_width = width - left_plots_width - right_plots_width

    fig = plt.figure(figsize=(width, hight))
    # 设置画幅的布局方式，
    rect1 = [left_plots_width / width, 0.12, (width - right_plots_width - left_plots_width) / width, 0.84]  # 左下宽高,中央对比图
    ylabelwidth = 0.52 / width
    rect2 = [ylabelwidth, 0.08, left_plots_width / width - ylabelwidth - 0.005, 0.40]  # 左下宽高，散点回归图
    ylabelwidth = 0.65 / width
    rect3 = [ylabelwidth, 0.60, left_plots_width / width - ylabelwidth - 0.005, 0.18]  # 左下宽高，频谱统计柱状图
    rect4 = [0.01, 0.79, left_plots_width / width - 0.045, 0.15]  # 左下宽高，左侧文字
    rect5 = [(width - right_plots_width) / width + 0.005, -0.035, right_plots_width / width - 0.01, 0.90]  # 左下宽高，右侧文字
    width_ob_fo_str = 0.3
    if (map_width < 3.5):
        width_bar = 2.1  # 根据中间地图的宽度，来确定预报colorbar的尺寸
        sta_legend_size = 5  # 根据中间地图的宽度，来确定观测legend的size
    else:
        sta_legend_size = 7
        width_bar = 2.9

    rect6 = [(left_plots_width + 0.5 * map_width - 0.5 * width_bar + 0.5 * width_ob_fo_str) / width, 0.04,
             width_bar / width, 0.02]  # 预报colorbar
    rect7 = [(left_plots_width + 0.5 * map_width - 0.5 * width_bar - 0.5 * width_ob_fo_str) / width, 0.04,
             width_ob_fo_str / width, 0.3]  # 观测文字


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
    colors_grid = ["#D0DEEA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    dat = grd_fo.values.squeeze()
    # print(x)
    # print(y)
    # print(dat)
    plot_grid = ax.contourf(x, y, dat, clevs, colors=colors_grid, transform=datacrs)  # 填色图
    time_str = nmc_verification.nmc_vf_base.tool.time_tools.time_to_str(grid_fo.gtime[0])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
    if type(grid_fo.members[0]) == str:
        model_name = grid_fo.members[0]
    else:
        model_name = str(grid_fo.members[0])

    if map_width < 3:
        title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
        ax.set_title(title, fontsize=7)
    elif map_width < 4:
        title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
        ax.set_title(title, fontsize=10)
    else:
        title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
        ax.set_title(title, fontsize=11)

    colorbar_position_grid = fig.add_axes(rect6)  # 位置[左,下,宽,高]
    cb = plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='horizontal')
    cb.ax.tick_params(labelsize=8)  # 设置色标刻度字体大小。
    # plt.text(0, 0, "预报(mm)", fontsize=8)

    # 绘制填色站点值
    sta_ob_in = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_grid_xy(sta_ob, grid=grid_fo)
    colors_sta = ['#FFFFFF', '#0055FF', '#00FFB4', '#F4FF00', '#FE1B00', '#910000', '#B800BA']
    dat = sta_ob_in.values[:, -1]
    dat[dat > 1000] = 0
    clevs = [0, 0.1, 10, 25, 50, 100, 250, 1000]
    cleves_name = ["0", "0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"]
    for i in range(len(clevs) - 1):
        index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
        if (len(index0[0]) > 0):
            x = np.squeeze(sta_ob_in["lon"].values[index0])
            y = np.squeeze(sta_ob_in["lat"].values[index0])
            if (len(index0) == 1):
                x = np.array([x])
                y = np.array([y])
                if (i > 0):
                    ax.scatter(x, y, c=colors_sta[i], transform=ccrs.PlateCarree(), s=3, label=cleves_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i], transform=ccrs.PlateCarree(), s=1, label=cleves_name[i],
                               linewidths=0.1, edgecolor="k")
    ax.legend(facecolor='whitesmoke', loc="lower center", ncol=4, edgecolor='whitesmoke',
              prop={'size': sta_legend_size},
              bbox_to_anchor=(0.5 + 0.5 * width_ob_fo_str / map_width, -0.08))
    ax7 = plt.axes(rect7)
    ax7.axes.set_axis_off()
    plt.text(0, 0.00, "观测\n\n预报", fontsize=7)

    # 图片显示或保存
    if (filename is None):
        plt.show()
        print()
    else:
        plt.savefig(filename, dpi=300)
    plt.close()
    return

def rain_24h_comprehensive_sg(sta_ob,grd_fo, filename=None):
    '''
    #绘制24小时降水实况与预报综合对比检验图，画幅中央为预报实况的对比，左右两侧为各类检验指标
    :param grd_fo: 输入的网格数据，包含一个平面的网格场
    :param sta_ob:  输入的站点数据，包含一个时刻的站点数据列表
    :param filename: 图片输出路径，缺省时会以调试窗口形式弹出
    :return:无返回值
    '''

    grid_fo = nmc_verification.nmc_vf_base.get_grid_of_data(grd_fo)
    #通过经纬度范围设置画幅
    hight = 5.6
    title_hight = 0.3
    legend_hight = 0.6
    left_plots_width  = 3
    right_plots_width = 2.3
    width = (hight - title_hight - legend_hight) * grid_fo.nlon / grid_fo.nlat + left_plots_width + right_plots_width
    map_width = width - left_plots_width - right_plots_width

    fig = plt.figure(figsize=(width, hight))
    # 设置画幅的布局方式，
    rect1 = [left_plots_width/width, 0.12, (width - right_plots_width - left_plots_width)/width, 0.84]  # 左下宽高,中央对比图
    ylabelwidth = 0.52/width
    rect2 = [ylabelwidth, 0.08, left_plots_width / width-ylabelwidth-0.005, 0.40]  # 左下宽高，散点回归图
    ylabelwidth = 0.65 / width
    rect3 = [ylabelwidth, 0.60, left_plots_width / width-ylabelwidth-0.005, 0.18]  # 左下宽高，频谱统计柱状图
    rect4 = [0.01, 0.79, left_plots_width / width-0.045, 0.15]  # 左下宽高，左侧文字
    rect5 = [(width - right_plots_width) / width+0.005, -0.035, right_plots_width/width-0.01, 0.90]  # 左下宽高，右侧文字
    width_ob_fo_str = 0.3
    if(map_width<3.5):
        width_bar = 2.1  #根据中间地图的宽度，来确定预报colorbar的尺寸
        sta_legend_size = 5 #根据中间地图的宽度，来确定观测legend的size
    else:
        sta_legend_size = 7
        width_bar = 2.9

    rect6 = [(left_plots_width + 0.5 * map_width - 0.5*width_bar + 0.5 * width_ob_fo_str)/width, 0.04, width_bar/width, 0.02]  #预报colorbar
    rect7 = [(left_plots_width + 0.5 * map_width - 0.5*width_bar - 0.5 * width_ob_fo_str)/width,0.04,width_ob_fo_str/width,0.3]  #观测文字
    #rect8 = [left_plots_width / width, 0.04, width_ob_fo_str / width, 0.3]  # 预报文字

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
    colors_grid = ["#D0DEEA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    dat = grd_fo.values.squeeze()
    #print(x)
    #print(y)
    #print(dat)
    plot_grid = ax.contourf(x, y, dat, clevs, colors=colors_grid, transform=datacrs)  # 填色图
    time_str = nmc_verification.nmc_vf_base.tool.time_tools.time_to_str(grid_fo.gtime[0])
    dati_str = time_str[0:4] + "年"+ time_str[4:6] + "月" +time_str[6:8] +"日" + time_str[8:10] + "时"
    if type(grid_fo.members[0]) == str:
        model_name = grid_fo.members[0]
    else:
        model_name = str(grid_fo.members[0])

    if map_width <3:
        title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
        ax.set_title(title,fontsize=7)
    elif map_width <4:
        title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
        ax.set_title(title, fontsize=10)
    else:
        title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
        ax.set_title(title, fontsize=11)

    colorbar_position_grid = fig.add_axes(rect6)  # 位置[左,下,宽,高]
    cb = plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='horizontal')
    cb.ax.tick_params(labelsize=8)  # 设置色标刻度字体大小。
    #plt.text(0, 0, "预报(mm)", fontsize=8)

    # 绘制填色站点值
    sta_ob_in = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_grid_xy(sta_ob, grid=grid_fo)
    colors_sta = ['#FFFFFF', '#0055FF', '#00FFB4', '#F4FF00', '#FE1B00', '#910000', '#B800BA']
    dat = sta_ob_in.values[:, -1]
    dat[dat > 1000] = 0
    clevs = [0, 0.1, 10, 25, 50, 100, 250, 1000]
    cleves_name = ["0", "0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"]
    for i in range(len(clevs) - 1):
        index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
        if (len(index0[0]) > 0):
            x = np.squeeze(sta_ob_in["lon"].values[index0])
            y = np.squeeze(sta_ob_in["lat"].values[index0])
            if (len(index0) == 1):
                x = np.array([x])
                y = np.array([y])
                if (i > 0):
                    ax.scatter(x, y, c=colors_sta[i], transform=ccrs.PlateCarree(), s=3, label=cleves_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i], transform=ccrs.PlateCarree(), s=1, label=cleves_name[i],linewidths=0.1,edgecolor = "k")
    ax.legend(facecolor='whitesmoke', loc="lower center",ncol=4, edgecolor='whitesmoke',prop={'size':sta_legend_size},
              bbox_to_anchor=(0.5 + 0.5 *width_ob_fo_str/map_width, -0.08))
    ax7 = plt.axes(rect7)
    ax7.axes.set_axis_off()
    plt.text(0, 0.00,"观测\n\n预报", fontsize=7)

    #ax.legend(loc="lower right", ncol=4, facecolor='whitesmoke', title="观测", edgecolor='whitesmoke', fontsize=9,
    #          bbox_to_anchor=(0, -0.32))
    # 散点回归图
    ax2 = plt.axes(rect2)
    sta_fo = nmc_verification.nmc_vf_base.function.gxy_sxy.interpolation_linear(grd_fo, sta_ob_in)
    #print(sta_fo)
    data_name = nmc_verification.nmc_vf_base.get_data_names(sta_ob_in)
    ob = sta_ob_in[data_name[0]].values
    data_name = nmc_verification.nmc_vf_base.get_data_names(sta_fo)
    fo = sta_fo[data_name[0]].values
    ax2.plot(ob, fo, '.', color='k')

    # 绘制比例线
    rate = np.sum(fo) / (np.sum(ob) + 1e-30)
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
    cor = np.corrcoef(ob,fo)
    rg_text1 = "R = " + '%.2f' % (cor[0, 1])
    rg_text2 = "y = " + '%.2f' % (clf.coef_[0]) + "* x + " + '%.2f' % (clf.intercept_)

    maxy = max(np.max(ob), np.max(fo)) + 5
    plt.xlim(0, maxy)
    plt.ylim(0, maxy)
    plt.text(0.05 * maxy, 0.9 * maxy, rg_text1, fontsize=10)
    plt.text(0.05 * maxy, 0.8 * maxy, rg_text2, fontsize=10)
    maxy = max(np.max(ob), np.max(fo))
    ax2.set_xlabel("观测", fontsize=9)
    ax2.set_ylabel("预报", fontsize=9)
    ax2.set_title("Obs.vs Pred. Scatter plot", fontsize=12)
    # 设置次刻度间隔
    xmi = 2
    if (np.max(ob) > 100): xmi = 5
    ymi = 2
    if (np.max(fo) > 100): ymi = 5
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

    ax4 = plt.axes(rect4)
    ax4.axes.set_axis_off()

    ob_has = ob[ob >= 0.01]
    fo_has = fo[fo >= 0.01]
    text = "降水站点实况和预报 n=" + str(len(ob)) + "\n"
    text += "=============================================\n"
    text += "                         观测           预报\n"
    text += "---------------------------------------------\n"
    text += "有降水站点数(>=0.01)     " + "%4d" % len(ob_has) + "           %4d" % len(fo_has) + "\n"
    text += "有降水站点数百分比%    " + "%6.1f" % (len(ob_has) / len(ob)) + "%15.1f" % (len(fo_has) / len(fo)) + "\n"
    text += "平均降水量(排除无降水) " + "%6.1f" % (np.mean(ob_has)) + "%15.1f" % (np.mean(fo_has)) + "\n"
    text += "最大降水量             " + "%6.1f" % (np.max(ob_has)) + "%15.1f" % (np.max(fo_has))+"\n"
    text += "---------------------------------------------"
    plt.text(0, 0, text, fontsize=9)

    # 绘制统计检验结果

    ax5 = plt.axes(rect5)
    ax5.axes.set_axis_off()

    mae = nmc_verification.nmc_vf_method.continuous.score.mae(ob, fo)
    me = nmc_verification.nmc_vf_method.continuous.score.me(ob, fo)
    mse = nmc_verification.nmc_vf_method.continuous.score.mse(ob, fo)
    rmse = nmc_verification.nmc_vf_method.continuous.score.rmse(ob, fo)
    bias_c = nmc_verification.nmc_vf_method.continuous.score.bias(ob, fo)
    cor = nmc_verification.nmc_vf_method.continuous.score.corr(ob, fo)
    hit, mis, fal, co = nmc_verification.nmc_vf_method.yes_or_no.score.hmfn(ob, fo, clevs[1:])
    ts = nmc_verification.nmc_vf_method.yes_or_no.score.ts(ob, fo, clevs[1:])
    ets = nmc_verification.nmc_vf_method.yes_or_no.score.ets(ob, fo, clevs[1:])
    bias = nmc_verification.nmc_vf_method.yes_or_no.score.bias(ob, fo, clevs[1:])
    hit_rate = nmc_verification.nmc_vf_method.yes_or_no.score.hit_rate(ob, fo, clevs[1:])
    mis_rate = nmc_verification.nmc_vf_method.yes_or_no.score.mis_rate(ob, fo, clevs[1:])
    fal_rate = nmc_verification.nmc_vf_method.yes_or_no.score.fal_rate(ob, fo, clevs[1:])
    text = str(len(ob)) + "评分站点预报检验统计量\n"
    text += "Mean absolute error:" + "%6.2f" % mae + "\n"
    text += "Mean error:" + "%6.2f" % me + "\n"
    text += "Mean-squared error:" + "%6.2f" % mse + "\n"
    text += "Root mean-squared error:" + "%6.2f" % rmse + "\n"
    text += "Bias:" + "%6.2f" % bias_c + "\n"
    text += "Correctlation coefficiant:" + "%6.2f" % cor + "\n\n\n"
    leves_name = ["0.1-10-", "10-25--", "25-50--", "50-100-", "100-250", ">=250-"]
    for i in range(len(leves_name)):
        text += ":" + leves_name[i] + "---------------------------\n"
        text += "正确:" + "%-4d" % hit[i] + " 空报:" + "%-4d" % fal[i] + " 漏报:" + "%-4d" % mis[i] + "\n"
        text += "TS:" + "%5.3f" % ts[i] + "                  ETS:" + "%5.3f" % ets[i] + "\n"
        text += "Hit rate:" + "%5.3f" % hit_rate[i] + "     Miss rate: " + "%5.3f" % mis_rate[i] + "\n"
        text += "False alarm ratio:" + "%5.3f" % fal_rate[i] + "  Bias:" + "%5.3f" % bias[i] + "\n\n"
    plt.text(0, 0.00, text, fontsize=9)

    # 图片显示或保存
    if (filename is None):
        plt.show()
        print()
    else:
        plt.savefig(filename, dpi=300)
    plt.close()
    return

def rain_24h_comprehensive_chinaland_sg(sta_ob,grd_fo,  filename=None):
    '''
    #绘制24小时降水实况与预报综合对比检验图，专为为全国区域设置的画面布局，画面更加紧凑
    :param grd_fo: 输入的网格数据，包含一个平面的网格场
    :param sta_ob:  输入的站点数据，包含一个时刻的站点数据列表
    :param filename: 图片输出路径，缺省时会以调试窗口形式弹出
    :return:无返回值
    '''

    grid_fo = nmc_verification.nmc_vf_base.get_grid_of_data(grd_fo)
    fig = plt.figure(figsize=(10, 7))
    # 平面对比图
    rect1 = [0.00, 0.41, 0.7, 0.55]  # 左下宽高
    datacrs = ccrs.PlateCarree()
    ax = plt.axes(rect1, projection=datacrs)
    # 设置地图背景
    map_extent = [73, 135, 18, 54]
    ax.set_extent(map_extent, crs=datacrs)
    add_china_map_2cartopy(ax, name='province', edgecolor='k', lw=0.3)  # 省界
    add_china_map_2cartopy(ax, name='river', edgecolor='blue', lw=0.3)  # 河流

    # 绘制格点预报场
    x = np.arange(grid_fo.nlon) * grid_fo.dlon + grid_fo.slon
    y = np.arange(grid_fo.nlat) * grid_fo.dlat + grid_fo.slat
    clevs = [0.1, 10, 25, 50, 100, 250, 1000]
    colors_grid = ["#E0EEFA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    dat = grd_fo.values.squeeze()
    plot_grid = ax.contourf(x, y, dat, clevs, colors=colors_grid, transform=datacrs)  # 填色图

    colorbar_position_grid = fig.add_axes([0.035, 0.93, 0.25, 0.015])  # 位置[左,下,宽,高]
    plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='horizontal')
    plt.text(0.035, 0.955, "预报(mm)", fontsize=9)
    # 绘制填色站点值
    sta_ob_in = nmc_verification.nmc_vf_base.function.get_from_sta_data.sta_in_grid_xy(sta_ob, grid=grid_fo)
    colors_sta = ['#FFFFFF', '#0055FF', '#00FFB4', '#F4FF00', '#FE1B00', '#910000', '#B800BA']
    dat = sta_ob_in.values[:, -1]
    dat[dat > 1000] = 0
    clevs = [0, 0.1, 10, 25, 50, 100, 250, 1000]
    cleves_name = ["0", "0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"]
    for i in range(len(clevs) - 1):
        index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
        if (len(index0[0]) > 0):
            x = np.squeeze(sta_ob_in["lon"].values[index0])
            y = np.squeeze(sta_ob_in["lat"].values[index0])
            if (len(index0) == 1):
                x = np.array([x])
                y = np.array([y])
                if (i > 0):
                    ax.scatter(x, y, c=colors_sta[i], transform=ccrs.PlateCarree(), s=3, label=cleves_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i], transform=ccrs.PlateCarree(), s=1, label=cleves_name[i],
                               linewidths=0.1, edgecolor="k")
    ax.legend(loc="lower left", facecolor='whitesmoke', title="观测",  edgecolor='whitesmoke',fontsize=9)

    #设置图片标题
    time_str = nmc_verification.nmc_vf_base.tool.time_tools.time_to_str(grid_fo.gtime[0])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
    if type(grid_fo.members[0]) == str:
        model_name = grid_fo.members[0]
    else:
        model_name = str(grid_fo.members[0])
    title = model_name + " " + dati_str + "起报" + str(grid_fo.dtimes[0]) + "H时效预报和观测"
    ax.set_title(title)



    # 散点回归图
    rect2 = [0.07, 0.07, 0.21, 0.30]  # 左下宽高
    ax2 = plt.axes(rect2)
    sta_fo = nmc_verification.nmc_vf_base.function.gxy_sxy.interpolation_linear(grd_fo, sta_ob_in)
    #print(sta_fo)
    data_name = nmc_verification.nmc_vf_base.get_data_names(sta_ob_in)
    ob = sta_ob_in[data_name[0]].values
    data_name = nmc_verification.nmc_vf_base.get_data_names(sta_fo)
    fo = sta_fo[data_name[0]].values
    ax2.plot(ob, fo, '.', color='k')

    # 绘制比例线
    rate = np.sum(fo) / (np.sum(ob) + 1e-30)
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
    cor = np.corrcoef(ob,fo)
    rg_text1 = "R = " + '%.2f' % (cor[0, 1])
    rg_text2 = "y = " + '%.2f' % (clf.coef_[0]) + "* x + " + '%.2f' % (clf.intercept_)

    maxy = max(np.max(ob), np.max(fo)) + 5
    plt.xlim(0, maxy)
    plt.ylim(0, maxy)
    plt.text(0.05 * maxy, 0.9 * maxy, rg_text1, fontsize=10)
    plt.text(0.05 * maxy, 0.8 * maxy, rg_text2, fontsize=10)
    maxy = max(np.max(ob), np.max(fo))
    ax2.set_xlabel("观测", fontsize=12)
    ax2.set_ylabel("预报", fontsize=12)
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
    text = "降水站点实况和预报 n=" + str(len(ob)) + "\n"
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

    mae = nmc_verification.nmc_vf_method.continuous.score.mae(ob, fo)
    me = nmc_verification.nmc_vf_method.continuous.score.me(ob, fo)
    mse = nmc_verification.nmc_vf_method.continuous.score.mse(ob, fo)
    rmse = nmc_verification.nmc_vf_method.continuous.score.rmse(ob, fo)
    bias_c = nmc_verification.nmc_vf_method.continuous.score.bias(ob, fo)
    cor = nmc_verification.nmc_vf_method.continuous.score.corr(ob, fo)
    hit, mis, fal, co = nmc_verification.nmc_vf_method.yes_or_no.score.hmfn(ob, fo, clevs[1:])
    ts = nmc_verification.nmc_vf_method.yes_or_no.score.ts(ob, fo, clevs[1:])
    ets = nmc_verification.nmc_vf_method.yes_or_no.score.ets(ob, fo, clevs[1:])
    bias = nmc_verification.nmc_vf_method.yes_or_no.score.bias(ob, fo, clevs[1:])
    hit_rate = nmc_verification.nmc_vf_method.yes_or_no.score.hit_rate(ob, fo, clevs[1:])
    mis_rate = nmc_verification.nmc_vf_method.yes_or_no.score.mis_rate(ob, fo, clevs[1:])
    fal_rate = nmc_verification.nmc_vf_method.yes_or_no.score.fal_rate(ob, fo, clevs[1:])
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
        print()
    else:
        plt.savefig(filename, dpi=300)
    plt.close()
    return

def temper(sta_ob,grd_fo,filename = None):
    pass

def temper_comprehensive_gg(grd_ob,grd_fo,filename = None):

    ob_min = np.min(grd_ob.values)
    fo_min = np.min(grd_fo.values)
    ob_max = np.max(grd_ob.values)
    fo_max = np.max(grd_fo.values)

    ob_fo_max = max(ob_max,fo_max)
    ob_fo_min = min(ob_min,fo_min)
    clevs_temp, cmap_temp = nmc_verification.nmc_vf_base.tool.color_tools.get_clev_and_cmap_by_element_name("temp")
    clevs,cmap = nmc_verification.nmc_vf_base.tool.color_tools.get_part_clev_and_cmap(clevs_temp,cmap_temp,ob_fo_max,ob_fo_min)

    width = 9  #整个画面的宽度
    width_colorbar = 0.6
    height_title = 0.3
    height_veri_plot = 3

    grid0 = nmc_verification.nmc_vf_base.get_grid_of_data(grd_fo)
    if(grid0.nlon <= grid0.nlat * 0.5):
        #采用3*1布局
        width_map = (width - 2 * width_colorbar) / 3
        height_map = (grid0.nlat/ grid0.nlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [width_colorbar/width, height_veri_plot/ height, width_map/width , height_map/height]  # 实况
        rect2 = [(1 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width ,  height_map/height] # 预报
        rect3 = [(2 * width_map +width_colorbar+0.05)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.015,height_map/height]
        error_colorbar_box = [(3 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.015,height_map/height]

    else:
        #采用1*2 + 1 布局
        width_map = (width - 2 * width_colorbar) / 1.5
        height_map = (grid0.nlat / grid0.nlon) * width_map
        height = height_map + height_title + height_veri_plot
        rect1 = [(width_colorbar -0.03)/width, (height_veri_plot + 0.5 * height_map) / height, 0.5 * width_map/width , 0.5* height_map/height]  # 实况
        rect2 = [(width_colorbar -0.03)/width, height_veri_plot / height, 0.5 * width_map/width , 0.5* height_map/height] # 预报
        rect3 = [(0.5 * width_map +width_colorbar)/width, height_veri_plot / height, width_map/width , height_map/height]  # 误差
        ob_fo_colorbar_box = [0.02,height_veri_plot / height,0.01,height_map/height]
        error_colorbar_box = [(1.5 * width_map +width_colorbar+0.05)/width,height_veri_plot / height,0.01,height_map/height]

    rect4 = [0.05, 0.06, 0.26, height_veri_plot / height-0.1]  # 散点回归图，左下宽高
    rect5 = [0.38, 0.06, 0.28, height_veri_plot / height-0.1]  # 频率柱状图， 左下宽高
    rect6 = [0.67, 0.01, 0.3, height_veri_plot / height-0.03]  # 左下宽高
    rect_title = [ width_colorbar/width,(height_veri_plot+ height_map)/height,1-2*width_colorbar/width, 0.001]

    fig = plt.figure(figsize=(width, height))
    # 平面对比图1
    datacrs = ccrs.PlateCarree()
    ax1 = plt.axes(rect1, projection=datacrs)
    ax2 = plt.axes(rect2, projection=datacrs)
    ax3 = plt.axes(rect3, projection=datacrs)
    # 设置地图背景

    map_extent = [grid0.slon, grid0.elon, grid0.slat, grid0.elat]
    ax1.set_extent(map_extent, crs=datacrs)
    ax2.set_extent(map_extent, crs=datacrs)
    ax3.set_extent(map_extent, crs=datacrs)
    add_china_map_2cartopy(ax1, name='province', edgecolor='k', lw=0.3)  # 省界
    add_china_map_2cartopy(ax1, name='river', edgecolor='blue', lw=0.3)  # 河流
    add_china_map_2cartopy(ax2, name='province', edgecolor='k', lw=0.3)  # 省界
    add_china_map_2cartopy(ax2, name='river', edgecolor='blue', lw=0.3)  # 河流
    add_china_map_2cartopy(ax3, name='province', edgecolor='k', lw=0.3)  # 省界
    add_china_map_2cartopy(ax3, name='river', edgecolor='blue', lw=0.3)  # 河流

    # 绘制格点预报场
    x = np.arange(grid0.nlon) * grid0.dlon + grid0.slon
    y = np.arange(grid0.nlat) * grid0.dlat + grid0.slat
    #clevs = [-10,0,15,20,22,24,26,28,30,32,34,35]
    #colors_grid = ["#00AAAA","#009500","#808000", "#BFBF00","#FFFF00","#FFD400","#FFAA00","#FF7F00","#FF0000","#FF002A","#FF0055","#FF0055"]

    plot_grid = ax1.contourf(x, y, grd_ob.values.squeeze(), levels = clevs,cmap=cmap, transform=datacrs)  # 填色图
    ax1.set_title("实况",fontsize=12,loc="left",y = 0.0)
    colorbar_position_grid = fig.add_axes(ob_fo_colorbar_box)  # 位置[左,下,宽,高]
    plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='vertical')
    plt.title("温度(℃)", fontsize=8,verticalalignment='bottom')

    ax2.contourf(x, y, grd_fo.values.squeeze(), levels = clevs,cmap=cmap, transform=datacrs)  # 填色图
    ax2.set_title("预报", fontsize=12, loc="left",y = 0.0)

    clevs1 = [-5,-4,-3,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,3,4,5]
    error = grd_fo.values.squeeze() - grd_ob.values.squeeze()

    plot_grid1 = ax3.contourf(x, y,error , clevs1,cmap = "bwr", transform=datacrs)  # 填色图
    colorbar_position_grid1 = fig.add_axes(error_colorbar_box)  # 位置[左,下,宽,高]
    ax3.set_title("预报 - 实况",fontsize=12, loc="left",y = 0.0)
    plt.colorbar(plot_grid1, cax=colorbar_position_grid1, orientation='vertical')
    plt.title("误差(℃)", fontsize=8, verticalalignment='bottom')

    time_str = nmc_verification.nmc_vf_base.tool.time_tools.time_to_str(grid0.gtime[0])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
    if type(grid0.members[0]) == str:
        model_name = grid0.members[0]
    else:
        model_name = str(grid0.members[0])

    title = model_name + " " + dati_str + "起报" + str(grid0.dtimes[0]) + "H时效预报和实况对比及误差"
    ax_title = plt.axes(rect_title)
    ax_title.axes.set_axis_off()
    ax_title.set_title(title)

    # 散点回归图
    ax2 = plt.axes(rect4)
    # 保证这两个值的正确性

    ob = grd_ob.values.flatten()
    fo = grd_fo.values.flatten()
    print(len(ob), len(fo))
    ax2.plot(ob, fo, '.', color='k')
    print(np.sum(fo), np.sum(ob))
    # 绘制比例线
    rate = np.sum(fo) / np.sum(ob)
    ob_line = np.arange(0, np.max(ob), np.max(ob) / 30)
    fo_rate = ob_line * rate
    ax2.plot(ob_line[0:20], fo_rate[0:20], 'r')

    # 绘制回归线
    X = np.zeros((len(ob), 1))
    X[:, 0] = ob[:]
    #绘制回归线
    clf = LinearRegression().fit(X, fo)
    X = np.zeros((len(ob_line), 1))
    X[:, 0] = ob_line[:]
    fo_rg = clf.predict(X)
    ax2.plot(ob_line, fo_rg, color='b', linestyle='dashed')
    rg_text1 = "R = " + '%.2f' % (np.corrcoef(ob,fo)[0,1])
    rg_text2 = "y = " + '%.2f' %(clf.coef_[0]) + "* x + " + '%.2f' %(clf.intercept_)
    maxy = max(np.max(ob), np.max(fo)) + 5
    plt.xlim(0, maxy)
    plt.ylim(0, maxy)
    plt.text(0.05*maxy, 0.9*maxy, rg_text1, fontsize=10)
    plt.text(0.05*maxy, 0.8*maxy, rg_text2, fontsize=10)
    # maxy = max(np.max(ob),np.max(fo))
    ax2.set_xlabel("实况", fontsize=10)
    ax2.set_ylabel("预报", fontsize=10)
    ax2.set_title("散点回归图", fontsize=10)
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

    #折线图
    # 绘制频率柱状图
    p_ob = np.zeros(len(clevs)-1)
    p_fo = np.zeros(len(clevs)-1)
    x = clevs[0:-1]
    for i in range(len(clevs) - 1):
        index0 = np.where((ob >= clevs[i]) & (ob < clevs[i + 1]))
        p_ob[i] = len(index0[0])
        index0 = np.where((fo >= clevs[i]) & (fo < clevs[i + 1]))
        p_fo[i] = len(index0[0])

    ax5 = plt.axes(rect5)
    # ax5.plot(p_ob, color='r',label="Obs")
    # ax5.plot(p_fo, color='b',label="Pred")
    ax5.bar(x + 0.5, p_ob, width=0.4,color='r', label="实况")
    ax5.bar(x + 1.1, p_fo, width=0.4,color="b", label="预报")
    ax5.legend(loc="upper right")
    ax5.set_xlabel("等级", fontsize=10)
    ax5.set_ylabel("站点数", fontsize=10)
    ax5.set_title("频率统计图", fontsize=10)
    ax5.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1000))
    maxy = max(np.max(p_fo),np.max(p_ob)) * 1.4
    ax5.set_ylim(0,maxy)

    #检验效果图
    # 绘制降水站点实况预报统计表
    ax6 = plt.axes(rect6)
    ax6.axes.set_axis_off()
    ob_mean = np.mean(grd_ob.values)
    fo_mean = np.mean(grd_fo.values)


    maee = nmc_verification.nmc_vf_method.continuous.score.mae(ob, fo)
    mee = nmc_verification.nmc_vf_method.continuous.score.me(ob, fo)
    msee = nmc_verification.nmc_vf_method.continuous.score.mse(ob, fo)
    rmsee = nmc_verification.nmc_vf_method.continuous.score.rmse(ob, fo)
    bias_ce = nmc_verification.nmc_vf_method.continuous.score.bias(ob, fo)
    cor = nmc_verification.nmc_vf_method.continuous.score.corr(ob,fo)

    ob_has = ob[ob >= 0.01]
    fo_has = fo[fo >= 0.01]
    text = "格点检验统计量 n=" + str(len(ob)) + "\n"
    text += "==============================================\n"
    text += "                     实况               预报   \n"
    text += "----------------------------------------------\n"
    text += "平均温度         " + "%8.2f" % (ob_mean) + "%20.2f" % (fo_mean) + "\n\n"
    text += "温度范围    " + "%8.2f" % (ob_min)+ "~%6.2f" % (ob_max) +"%12.2f" % (fo_min)+ "~%6.2f" % (fo_max) + "\n\n"
    text += "==============================================\n\n"
    text += "Mean absolute error:" + "%6.2f" % maee + "\n\n"
    text += "Mean error:" + "%6.2f" % mee + "\n\n"
    text += "Mean-squared error:" + "%6.2f" % msee + "\n\n"
    text += "Root mean-squared error:" + "%6.2f" % rmsee + "\n\n"
    text += "Bias:" + "%6.2f" % bias_ce + "\n\n"
    text += "Correctlation coefficiant:" + "%6.2f" % cor + "\n"
    plt.text(0, 0, text, fontsize=9)

    # 图片显示或保存
    if (filename is None):
        plt.show()
        print()
    else:
        plt.savefig(filename, dpi=300)
    plt.close()
