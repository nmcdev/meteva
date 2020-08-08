import matplotlib as mpl
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import numpy  as np
from meteva.base.tool.plot_tools import add_china_map_2basemap
from sklearn.linear_model import LinearRegression
import meteva
from meteva.base import IV
import math
import copy

def rain_24h_sg(sta_ob,grd_fo,save_path=None,show  = False,dpi = 200,add_county_line = False):
    '''
    #绘制24小时降水实况与预报对比图
    :param grd_fo: 输入的网格数据，包含一个平面的网格场
    :param sta_ob:  输入的站点数据，包含一个时刻的站点数据列表
    :param filename: 图片输出路径，缺省时会以调试窗口形式弹出
    :return: 无返回值
    '''
    grid_fo = meteva.base.get_grid_of_data(grd_fo)
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

    rect6 = [(left_plots_width + 0.5 * map_width - 0.5 * width_bar + 0.5 * width_ob_fo_str) / width, 0.00,
             width_bar / width, 0.02]  # 预报colorbar
    rect7 = [(left_plots_width + 0.5 * map_width - 0.5 * width_bar - 0.5 * width_ob_fo_str) / width, 0.00,
             width_ob_fo_str / width, 0.3]  # 观测文字


    ax = plt.axes(rect1)
    # 设置地图背景
    add_china_map_2basemap(ax, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "省界"
    ax.set_xlim((grid_fo.slon, grid_fo.elon))
    ax.set_ylim((grid_fo.slat, grid_fo.elat))

    # 绘制格点预报场
    x = np.arange(grid_fo.nlon) * grid_fo.dlon + grid_fo.slon
    y = np.arange(grid_fo.nlat) * grid_fo.dlat + grid_fo.slat
    clevs = [0.1, 10, 25, 50, 100, 250, 1000]
    colors_grid = ["#D0DEEA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    dat = grd_fo.values.squeeze()
    # print(x)
    # print(y)
    # print(dat)
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plot_grid = ax.contourf(x, y, dat, clevs, colors=colors_grid)  # 填色图
    time_str = meteva.base.tool.time_tools.time_to_str(grid_fo.gtime[0])
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
    sta_ob_in = meteva.base.in_grid_xy(sta_ob, grid=grid_fo)
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
                    ax.scatter(x, y, c=colors_sta[i],  s=3, label=cleves_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i], s=1, label=cleves_name[i],
                               linewidths=0.1, edgecolor="k")
    ax.legend(facecolor='whitesmoke', loc="lower center", ncol=4, edgecolor='whitesmoke',
              prop={'size': sta_legend_size},
              bbox_to_anchor=(0.5 + 0.5 * width_ob_fo_str / map_width, -0.08))
    ax7 = plt.axes(rect7)
    ax7.axes.set_axis_off()
    plt.text(0, 0.00, "观测\n\n预报", fontsize=7)

    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()
    return

def rain_24h_comprehensive_sg(sta_ob,grd_fo, save_path=None,show = False,dpi = 200,add_county_line = False):
    '''
    #绘制24小时降水实况与预报综合对比检验图，画幅中央为预报实况的对比，左右两侧为各类检验指标
    :param grd_fo: 输入的网格数据，包含一个平面的网格场
    :param sta_ob:  输入的站点数据，包含一个时刻的站点数据列表
    :param filename: 图片输出路径，缺省时会以调试窗口形式弹出
    :return:无返回值
    '''
    grid_fo = meteva.base.get_grid_of_data(grd_fo)
    #通过经纬度范围设置画幅
    hight = 5.6
    title_hight = 0.3
    legend_hight = 0.6
    left_plots_width  = 3
    right_plots_width = 2.3
    width = (hight - title_hight - legend_hight) * grid_fo.nlon / grid_fo.nlat + left_plots_width + right_plots_width
    map_width = width - left_plots_width - right_plots_width
    map_area = (hight - title_hight - legend_hight) *map_width

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

    ax = plt.axes(rect1)
    # 设置地图背景
    add_china_map_2basemap(ax, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "省界"
    ax.set_xlim((grid_fo.slon, grid_fo.elon))
    ax.set_ylim((grid_fo.slat, grid_fo.elat))

    # 绘制格点预报场
    x = np.arange(grid_fo.nlon) * grid_fo.dlon + grid_fo.slon
    y = np.arange(grid_fo.nlat) * grid_fo.dlat + grid_fo.slat
    clevs = [0.1, 10, 25, 50, 100, 250, 1000]
    colors_grid = ["#D0DEEA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    dat = grd_fo.values.squeeze()
    #print(x)
    #print(y)
    #print(dat)
    plt.xticks([])
    plt.yticks([])
    plot_grid = ax.contourf(x, y, dat, clevs, colors=colors_grid)  # 填色图
    time_str = meteva.base.tool.time_tools.time_to_str(grid_fo.gtime[0])
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
    sta_ob_in = meteva.base.in_grid_xy(sta_ob, grid=grid_fo)
    colors_sta = ['#FFFFFF', '#0055FF', '#00FFB4', '#F4FF00', '#FE1B00', '#910000', '#B800BA']
    dat = sta_ob_in.values[:, -1]
    dat[dat > 1000] = 0
    clevs = [0, 0.1, 10, 25, 50, 100, 250, 1000]
    cleves_name = ["0", "0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"]
    pointsize = int(100*map_area / len(dat))
    if(pointsize >30):pointsize = 30
    if(pointsize<1):pointsize = 1
    for i in range(len(clevs) - 1):
        index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
        if (len(index0[0]) > 0):
            x = np.squeeze(sta_ob_in["lon"].values[index0])
            y = np.squeeze(sta_ob_in["lat"].values[index0])
            if (len(index0) == 1):
                x = np.array([x])
                y = np.array([y])
                if (i > 0):
                    ax.scatter(x, y, c=colors_sta[i], s=3*pointsize, label=cleves_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i], s=3*pointsize, label=cleves_name[i],linewidths=0.0,edgecolor = "k")
    ax.legend(facecolor='gainsboro', loc="lower center",ncol=4, edgecolor='whitesmoke',prop={'size':sta_legend_size},
              bbox_to_anchor=(0.5 + 0.5 *width_ob_fo_str/map_width, -0.08))
    ax7 = plt.axes(rect7)
    ax7.axes.set_axis_off()
    plt.text(0, 0.00,"观测\n\n预报", fontsize=7)

    #ax.legend(loc="lower right", ncol=4, facecolor='whitesmoke', title="观测", edgecolor='whitesmoke', fontsize=9,
    #          bbox_to_anchor=(0, -0.32))
    # 散点回归图
    ax2 = plt.axes(rect2)
    sta_fo = meteva.base.interp_gs_linear(grd_fo, sta_ob_in)
    #print(sta_fo)
    data_name = meteva.base.get_stadata_names(sta_ob_in)
    ob = sta_ob_in[data_name[0]].values
    data_name = meteva.base.get_stadata_names(sta_fo)
    fo = sta_fo[data_name[0]].values
    ob_fo = ob + fo
    index = np.where(~np.isnan(ob_fo))
    ob = ob[index]
    fo = fo[index]
    ax2.plot(ob, fo, '.', color='k')
    maxy = max(np.max(ob), np.max(fo)) + 5

    # 绘制比例线
    rate = np.sum(fo) / (np.sum(ob) + 1e-30)
    ob_line = np.arange(0, (maxy+1), (maxy+1) / 30)
    fo_rate = ob_line * 1
    ax2.plot(ob_line[0:30], fo_rate[0:30], 'b', linestyle='dashed')


    # 绘制回归线
    X = np.zeros((len(ob), 1))
    X[:, 0] = ob[:]
    clf = LinearRegression().fit(X, fo)
    X = np.zeros((len(ob_line), 1))
    X[:, 0] = ob_line[:]
    fo_rg = clf.predict(X)
    ax2.plot(ob_line, fo_rg, color='r')
    cor = np.corrcoef(ob,fo)
    rg_text1 = "R = " + '%.2f' % (cor[0, 1])
    rg_text2 = "y = " + '%.2f' % (clf.coef_[0]) + "* x + " + '%.2f' % (clf.intercept_)

    plt.xlim(0, maxy)
    plt.ylim(0, maxy)
    plt.text(0.05 * maxy, 0.9 * maxy, rg_text1, fontsize=10)
    plt.text(0.05 * maxy, 0.8 * maxy, rg_text2, fontsize=10)
    maxy = max(np.max(ob), np.max(fo))
    ax2.set_xlabel("观测", fontsize=9)
    ax2.set_ylabel("预报", fontsize=9)
    ax2.set_title("Obs.vs Pred. Scatter plot", fontsize=12)
    # 设置次刻度间隔

    # 设置次刻度间隔
    if(maxy <5):
        xmi = 0.1
        Xmi = 1
    elif(maxy <50):
        xmi = 1
        if(maxy >25):
            Xmi = 10
        else:
            Xmi = 5
    elif (maxy <100):
        xmi = 2
        if(maxy >50):
            Xmi = 20
        else:
            Xmi = 10
    elif (maxy <250):
        xmi = 5
        if(maxy >100):
            Xmi = 50
        else:
            Xmi = 20
    elif (maxy <1000):
        xmi = 20
        if(maxy >500):
            Xmi = 200
        else:
            Xmi = 100
    else:
        xmi = 50
        Xmi = 250
    xmajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将x主刻度标签设置为次刻度10倍
    ymajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将y主刻度标签设置为次刻度10倍
    ax2.xaxis.set_major_locator(xmajorLocator)
    ax2.yaxis.set_major_locator(ymajorLocator)
    xminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将x轴次刻度标签设置xmi
    yminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将y轴次刻度标签设置ymi
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
    mean_fo = 0
    max_fo = 0
    mean_ob = 0
    max_ob = 0
    if len(fo_has)>1:
        mean_fo = np.mean(fo_has)
        max_fo = np.max(fo_has)
    if len(ob_has)>1:
        mean_ob = np.mean(ob_has)
        max_ob = np.max(ob_has)

    text = "降水站点实况和预报 n=" + str(len(ob)) + "\n"
    text += "=============================================\n"
    text += "                         观测           预报\n"
    text += "---------------------------------------------\n"
    text += "有降水站点数(>=0.01)     " + "%4d" % len(ob_has) + "           %4d" % len(fo_has) + "\n"
    text += "有降水站点数百分比%    " + "%6.1f" % (len(ob_has) / len(ob)) + "%15.1f" % (len(fo_has) / len(fo)) + "\n"
    text += "平均降水量(排除无降水) " + "%6.1f" % (mean_ob) + "%15.1f" % (mean_fo) + "\n"
    text += "最大降水量             " + "%6.1f" % (max_ob) + "%15.1f" % (max_fo)+"\n"
    text += "---------------------------------------------"
    plt.text(0, 0, text, fontsize=9)

    # 绘制统计检验结果

    ax5 = plt.axes(rect5)
    ax5.axes.set_axis_off()

    mae = meteva.method.continuous.score.mae(ob, fo)
    me = meteva.method.continuous.score.me(ob, fo)
    mse = meteva.method.continuous.score.mse(ob, fo)
    rmse = meteva.method.continuous.score.rmse(ob, fo)
    bias_c = meteva.method.continuous.score.bias_m(ob, fo)
    cor = meteva.method.continuous.score.corr(ob, fo)
    pc_sun_rain = meteva.method.pc_of_sun_rain(ob,fo)
    hfmc = meteva.method.yes_or_no.score.hfmc(ob, fo, clevs[1:])
    ts = meteva.method.yes_or_no.score.ts(ob, fo, clevs[1:])
    ets = meteva.method.yes_or_no.score.ets(ob, fo, clevs[1:])
    bias = meteva.method.yes_or_no.score.bias(ob, fo, clevs[1:])
    hit_rate = meteva.method.yes_or_no.score.pod(ob, fo, clevs[1:])
    mis_rate = meteva.method.yes_or_no.score.mr(ob, fo, clevs[1:])
    fal_rate = meteva.method.yes_or_no.score.far(ob, fo, clevs[1:])

    text = str(len(ob)) + "评分站点预报检验统计量\n"
    text += "Mean absolute error:" + "%6.2f" % mae + "\n"
    text += "Mean error:" + "%6.2f" % me + "\n"
    text += "Mean-squared error:" + "%6.2f" % mse + "\n"
    text += "Root mean-squared error:" + "%6.2f" % rmse + "\n"
    text += "Bias:" + "%6.2f" % bias_c + "\n"
    text += "Correctlation coefficiant:" + "%6.2f" % cor + "\n"
    text += "晴雨准确率:" + "%6.2f" % pc_sun_rain + "\n\n"
    leves_name = ["0.1-10-", "10-25--", "25-50--", "50-100-", "100-250", ">=250-"]
    for i in range(len(leves_name)):
        text += ":" + leves_name[i] + "---------------------------\n"
        text += "正确:" + "%-4d" % hfmc[i,0] + " 空报:" + "%-4d" % hfmc[i,1] + " 漏报:" + "%-4d" % hfmc[i,2] + "\n"
        if ts[i] == IV:
            ts_str = " NULL"
        else:
            ts_str = "%5.3f" % ts[i]
        if ets[i] == IV:
            ets_str = " NULL"
        else:
            ets_str = "%5.3f" % ets[i]
        text += "TS:" + ts_str + "                  ETS:" + ets_str + "\n"
        if hit_rate[i] == IV:
            hit_rate_str = " NULL"
        else:
            hit_rate_str = "%5.3f" % hit_rate[i]
        if mis_rate[i] == IV:
            mis_rate_str = " NULL"
        else:
            mis_rate_str = "%5.3f" % mis_rate[i]
        text += "Hit rate:" + hit_rate_str + "     Miss rate: " + mis_rate_str + "\n"

        if fal_rate[i] == IV:
            fal_rate_str = " NULL"
        else:
            fal_rate_str = "%5.3f" % fal_rate[i]
        if bias[i] == IV:
            bias_str = " NULL"
        else:
            bias_str = "%5.3f" % bias[i]
        text += "False alarm ratio:" + fal_rate_str + "  Bias:" + bias_str + "\n\n"
    plt.text(0, 0.00, text, fontsize=9)

    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()

    return

def rain_24h_comprehensive_chinaland_sg(sta_ob,grd_fo,  save_path=None,show = False,dpi = 200,add_county_line = False):
    '''
    #绘制24小时降水实况与预报综合对比检验图，专为为全国区域设置的画面布局，画面更加紧凑
    :param grd_fo: 输入的网格数据，包含一个平面的网格场
    :param sta_ob:  输入的站点数据，包含一个时刻的站点数据列表
    :param filename: 图片输出路径，缺省时会以调试窗口形式弹出
    :return:无返回值
    '''

    grid_fo = meteva.base.get_grid_of_data(grd_fo)
    fig = plt.figure(figsize=(10, 7))
    # 平面对比图
    rect1 = [0.05, 0.43, 0.65, 0.53]  # 左下宽高
    map_area = 70 * 0.41 * 0.55
    ax = plt.axes(rect1)
    # 设置地图背景
    map_extent = [73, 135, 18, 54]
    add_china_map_2basemap(ax, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax.set_xlim((73, 135))
    ax.set_ylim((18, 54))

    # 绘制格点预报场
    x = np.arange(grid_fo.nlon) * grid_fo.dlon + grid_fo.slon
    y = np.arange(grid_fo.nlat) * grid_fo.dlat + grid_fo.slat
    clevs = [0.1, 10, 25, 50, 100, 250, 1000]
    colors_grid = ["#E0EEFA", "#B4D3E9", "#6FB0D7", "#3787C0", "#105BA4", "#07306B", "#07306B"]
    dat = grd_fo.values.squeeze()
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plot_grid = ax.contourf(x, y, dat, clevs, colors=colors_grid)  # 填色图

    colorbar_position_grid = fig.add_axes([0.085, 0.93, 0.25, 0.015])  # 位置[左,下,宽,高]
    plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='horizontal')
    plt.text(0.035, 0.955, "预报(mm)", fontsize=9)
    # 绘制填色站点值
    sta_ob_in = meteva.base.in_grid_xy(sta_ob, grid=grid_fo)
    colors_sta = ['#FFFFFF', '#0055FF', '#00FFB4', '#F4FF00', '#FE1B00', '#910000', '#B800BA']
    dat = sta_ob_in.values[:, -1]
    dat[dat > 1000] = 0
    clevs = [0, 0.1, 10, 25, 50, 100, 250, 1000]
    cleves_name = ["0", "0.1-10", "10-25", "25-50", "50-100", "100-250", ">=250"]

    pointsize = int(100 * map_area / len(dat))
    if (pointsize > 30): pointsize = 30
    if (pointsize < 1): pointsize = 1

    for i in range(len(clevs) - 1):
        index0 = np.where((dat >= clevs[i]) & (dat < clevs[i + 1]))
        if (len(index0[0]) > 0):
            x = np.squeeze(sta_ob_in["lon"].values[index0])
            y = np.squeeze(sta_ob_in["lat"].values[index0])
            if (len(index0) == 1):
                x = np.array([x])
                y = np.array([y])
                if (i > 0):
                    ax.scatter(x, y, c=colors_sta[i], s=3*pointsize, label=cleves_name[i],
                               linewidths=0.3, edgecolor='k')
                else:
                    ax.scatter(x, y, c=colors_sta[i],  s=pointsize, label=cleves_name[i],
                               linewidths=0.1, edgecolor="k")
    ax.legend(loc="lower left", facecolor='whitesmoke', title="观测",  edgecolor='whitesmoke',fontsize=9)

    #设置图片标题
    time_str = meteva.base.tool.time_tools.time_to_str(grid_fo.gtime[0])
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
    sta_fo = meteva.base.interp_gs_nearest(grd_fo, sta_ob_in)
    # print(sta_fo)
    data_name = meteva.base.get_stadata_names(sta_ob_in)
    ob = sta_ob_in.loc[:,data_name[0]].values
    data_name = meteva.base.get_stadata_names(sta_fo)
    fo = sta_fo.loc[:,data_name[0]].values
    ob_fo = ob + fo
    index = np.where(~np.isnan(ob_fo))
    ob = ob[index]
    fo = fo[index]
    ax2.plot(ob, fo, '.', color='k')
    maxy = max(np.max(ob), np.max(fo)) + 5

    # 绘制比例线
    rate = np.sum(fo) / (np.sum(ob) + 1e-30)
    ob_line = np.arange(0, (maxy + 1), (maxy + 1) / 30)
    fo_rate = ob_line * 1
    ax2.plot(ob_line[0:30], fo_rate[0:30], 'b', linestyle='dashed')

    # 绘制回归线
    X = np.zeros((len(ob), 1))
    X[:, 0] = ob[:]
    clf = LinearRegression().fit(X, fo)
    X = np.zeros((len(ob_line), 1))
    X[:, 0] = ob_line[:]
    fo_rg = clf.predict(X)
    ax2.plot(ob_line, fo_rg, color='r')
    cor = np.corrcoef(ob, fo)
    rg_text1 = "R = " + '%.2f' % (cor[0, 1])
    rg_text2 = "y = " + '%.2f' % (clf.coef_[0]) + "* x + " + '%.2f' % (clf.intercept_)

    plt.xlim(0, maxy)
    plt.ylim(0, maxy)
    plt.text(0.05 * maxy, 0.9 * maxy, rg_text1, fontsize=10)
    plt.text(0.05 * maxy, 0.8 * maxy, rg_text2, fontsize=10)
    maxy = max(np.max(ob), np.max(fo))
    ax2.set_xlabel("观测", fontsize=9)
    ax2.set_ylabel("预报", fontsize=9)
    ax2.set_title("Obs.vs Pred. Scatter plot", fontsize=12)
    # 设置次刻度间隔
    if(maxy <5):
        xmi = 0.1
        Xmi = 1
    elif(maxy <50):
        xmi = 1
        if(maxy >25):
            Xmi = 10
        else:
            Xmi = 5
    elif (maxy <100):
        xmi = 2
        if(maxy >50):
            Xmi = 20
        else:
            Xmi = 10
    elif (maxy <250):
        xmi = 5
        if(maxy >100):
            Xmi = 50
        else:
            Xmi = 20
    elif (maxy <1000):
        xmi = 20
        if(maxy >500):
            Xmi = 200
        else:
            Xmi = 100
    else:
        xmi = 50
        Xmi = 250



    xmajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将x主刻度标签设置为次刻度10倍
    ymajorLocator = mpl.ticker.MultipleLocator(Xmi)  # 将y主刻度标签设置为次刻度10倍
    ax2.xaxis.set_major_locator(xmajorLocator)
    ax2.yaxis.set_major_locator(ymajorLocator)
    xminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将x轴次刻度标签设置xmi
    yminorLocator = mpl.ticker.MultipleLocator(xmi)  # 将y轴次刻度标签设置ymi
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
    rect4 = [0.35, 0.235, 0.4, 0.10]  # 左下宽高
    ax4 = plt.axes(rect4)
    ax4.axes.set_axis_off()

    ob_has = ob[ob >= 0.01]
    fo_has = fo[fo >= 0.01]
    mean_fo = 0
    max_fo = 0
    mean_ob = 0
    max_ob = 0
    if len(fo_has)>1:
        mean_fo = np.mean(fo_has)
        max_fo = np.max(fo_has)
    if len(ob_has)>1:
        mean_ob = np.mean(ob_has)
        max_ob = np.max(ob_has)

    text = "降水站点实况和预报 n=" + str(len(ob)) + "\n"
    text += "====================================================\n"
    text += "                              观测           预报  \n"
    text += "----------------------------------------------------\n"
    text += "有降水站点数(>=0.01)     " + "%9d" % len(ob_has) + "           %4d" % len(fo_has) + "\n"
    text += "有降水站点数百分比%    " + "%11.1f" % (len(ob_has) / len(ob)) + "%15.1f" % (len(fo_has) / len(fo)) + "\n"
    text += "平均降水量(排除无降水) " + "%11.1f" % (mean_ob) + "%15.1f" % (mean_fo) + "\n"
    text += "最大降水量             " + "%11.1f" % (max_ob) + "%15.1f" % (max_fo)+"\n"
    text += "----------------------------------------------------"
    plt.text(0, 0, text, fontsize=9)


    # 绘制统计检验结果
    rect5 = [0.705, 0.08, 0.28, 0.85]  # 左下宽高
    ax5 = plt.axes(rect5)
    ax5.axes.set_axis_off()

    mae = meteva.method.continuous.score.mae(ob, fo)
    me = meteva.method.continuous.score.me(ob, fo)
    mse = meteva.method.continuous.score.mse(ob, fo)
    rmse = meteva.method.continuous.score.rmse(ob, fo)
    bias_c = meteva.method.continuous.score.bias_m(ob, fo)
    cor = meteva.method.continuous.score.corr(ob, fo)
    pc_sun_rain = meteva.method.pc_of_sun_rain(ob, fo)
    hfmc = meteva.method.yes_or_no.score.hfmc(ob, fo, clevs[1:])
    ts = meteva.method.yes_or_no.score.ts(ob, fo, clevs[1:])
    ets = meteva.method.yes_or_no.score.ets(ob, fo, clevs[1:])
    bias = meteva.method.yes_or_no.score.bias(ob, fo, clevs[1:])
    hit_rate = meteva.method.yes_or_no.score.pod(ob, fo, clevs[1:])
    mis_rate = meteva.method.yes_or_no.score.mr(ob, fo, clevs[1:])
    fal_rate = meteva.method.yes_or_no.score.far(ob, fo, clevs[1:])
    text = str(len(ob)) + "评分站点预报检验统计量\n"
    text += "Mean absolute error:" + "%6.2f" % mae + "\n"
    text += "Mean error:" + "%6.2f" % me + "\n"
    text += "Mean-squared error:" + "%6.2f" % mse + "\n"
    text += "Root mean-squared error:" + "%6.2f" % rmse + "\n"
    text += "Bias:" + "%6.2f" % bias_c + "\n"
    text += "Correctlation coefficiant:" + "%6.2f" % cor + "\n"
    text += "晴雨准确率:" + "%6.2f" % pc_sun_rain + "\n\n"
    leves_name = ["0.1-10-", "10-25--", "25-50--", "50-100-", "100-250", ">=250-"]
    for i in range(len(leves_name)):
        text += ":" + leves_name[i] + "---------------------------\n"
        text += "正确:" + "%-4d" % hfmc[i, 0] + " 空报:" + "%-4d" % hfmc[i, 1] + " 漏报:" + "%-4d" % hfmc[i, 2] + "\n"
        if ts[i] == IV:
            ts_str = " NULL"
        else:
            ts_str = "%5.3f" % ts[i]
        if ets[i] == IV:
            ets_str = " NULL"
        else:
            ets_str = "%5.3f" % ets[i]
        text += "TS:" + ts_str + "                  ETS:" + ets_str + "\n"
        if hit_rate[i] == IV:
            hit_rate_str = " NULL"
        else:
            hit_rate_str = "%5.3f" % hit_rate[i]
        if mis_rate[i] == IV:
            mis_rate_str = " NULL"
        else:
            mis_rate_str = "%5.3f" % mis_rate[i]
        text += "Hit rate:" + hit_rate_str + "     Miss rate: " + mis_rate_str + "\n"

        if fal_rate[i] == IV:
            fal_rate_str = " NULL"
        else:
            fal_rate_str = "%5.3f" % fal_rate[i]
        if bias[i] == IV:
            bias_str = " NULL"
        else:
            bias_str = "%5.3f" % bias[i]
        text += "False alarm ratio:" + fal_rate_str + "  Bias:" + bias_str + "\n\n"
    plt.text(0, 0.00, text, fontsize=10)

    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()
    return

def temper_gg(grd_ob,grd_fo,save_path = None,show = False,dpi = 200,add_county_line = False,grd_ob_name = "实况",grd_fo_name = "预报"):

    ob_min = np.min(grd_ob.values)
    fo_min = np.min(grd_fo.values)
    ob_max = np.max(grd_ob.values)
    fo_max = np.max(grd_fo.values)

    ob_fo_max = max(ob_max,fo_max)
    ob_fo_min = min(ob_min,fo_min)
    if ob_fo_max > 120:
        clevs_temp, cmap_temp = meteva.base.tool.color_tools.clev_cmap_temper_2m_k()
    else:
        clevs_temp, cmap_temp = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("temp")

    clevs,cmap = meteva.base.tool.color_tools.get_part_clev_and_cmap(clevs_temp,cmap_temp,ob_fo_max,ob_fo_min)

    width = 9  #整个画面的宽度
    width_colorbar = 0.6
    height_title = 0.3
    height_veri_plot = 0.5

    grid0 = meteva.base.get_grid_of_data(grd_fo)
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




    # 设置地图背景
    ax1 = plt.axes(rect1)
    add_china_map_2basemap(ax1, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax1, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax1.set_xlim((grid0.slon, grid0.elon))
    ax1.set_ylim((grid0.slat, grid0.elat))



    # 绘制格点预报场
    x = np.arange(grid0.nlon) * grid0.dlon + grid0.slon
    y = np.arange(grid0.nlat) * grid0.dlat + grid0.slat
    #clevs = [-10,0,15,20,22,24,26,28,30,32,34,35]
    #colors_grid = ["#00AAAA","#009500","#808000", "#BFBF00","#FFFF00","#FFD400","#FFAA00","#FF7F00","#FF0000","#FF002A","#FF0055","#FF0055"]
    error = grd_fo.values.squeeze() - grd_ob.values.squeeze()
    plt.xticks([])
    plt.yticks([])
    plot_grid = ax1.contourf(x, y, grd_ob.values.squeeze(), levels=clevs, cmap=cmap)  # 填色图
    ax1.set_title(grd_ob_name,fontsize=18,loc="left",y = 0.0)
    colorbar_position_grid = fig.add_axes(ob_fo_colorbar_box)  # 位置[左,下,宽,高]
    plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='vertical')
    #plt.title("温度(℃)", fontsize=8,verticalalignment='bottom')

    ax2 = plt.axes(rect2)
    add_china_map_2basemap(ax2, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax2, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax2.set_xlim((grid0.slon, grid0.elon))
    ax2.set_ylim((grid0.slat, grid0.elat))
    plt.xticks([])
    plt.yticks([])
    ax2.contourf(x, y, grd_fo.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    ax2.set_title(grd_fo_name, fontsize=18, loc="left",y = 0.0)

    clevs1 = [-5,-4,-3,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,3,4,5]


    ax3 = plt.axes(rect3)
    add_china_map_2basemap(ax3, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax3, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax3.set_xlim((grid0.slon, grid0.elon))
    ax3.set_ylim((grid0.slat, grid0.elat))
    plt.rcParams['xtick.direction'] = 'in'
    plt.rcParams['ytick.direction'] = 'in'
    plot_grid1 = ax3.contourf(x, y,error , clevs1,cmap = "bwr")  # 填色图
    colorbar_position_grid1 = fig.add_axes(error_colorbar_box)  # 位置[左,下,宽,高]
    title_error = grd_fo_name + ' - ' + grd_ob_name
    ax3.set_title(title_error,fontsize=18, loc="left",y = 0.0)
    plt.colorbar(plot_grid1, cax=colorbar_position_grid1, orientation='vertical')
    plt.title("误差(℃)", fontsize=8, verticalalignment='bottom')

    time_str = meteva.base.tool.time_tools.time_to_str(grid0.gtime[0])
    dati_str = time_str[0:4] + "年" + time_str[4:6] + "月" + time_str[6:8] + "日" + time_str[8:10] + "时"
    if type(grid0.members[0]) == str:
        model_name = grid0.members[0]
    else:
        model_name = str(grid0.members[0])

    title = model_name + " " + dati_str + "起报" + str(grid0.dtimes[0]) + "H时效预报和实况对比及误差"
    ax_title = plt.axes(rect_title)
    ax_title.axes.set_axis_off()
    ax_title.set_title(title)


    # 图片显示或保存
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()

def temper_comprehensive_gg(grd_ob,grd_fo,save_path = None,show = False,dpi = 200,add_county_line = False,grd_ob_name = "实况",grd_fo_name = "预报"):

    ob_min = np.min(grd_ob.values)
    fo_min = np.min(grd_fo.values)
    ob_max = np.max(grd_ob.values)
    fo_max = np.max(grd_fo.values)

    ob_fo_max = max(ob_max,fo_max)
    ob_fo_min = min(ob_min,fo_min)
    #clevs_temp, cmap_temp = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("temp")

    if ob_fo_max > 120:
        clevs_temp, cmap_temp = meteva.base.tool.color_tools.clev_cmap_temper_2m_k()
    else:
        clevs_temp, cmap_temp = meteva.base.tool.color_tools.get_clev_and_cmap_by_element_name("temp")

    clevs,cmap = meteva.base.tool.color_tools.get_part_clev_and_cmap(clevs_temp,cmap_temp,ob_fo_max,ob_fo_min)

    width = 9  #整个画面的宽度
    width_colorbar = 0.6
    height_title = 0.3
    height_veri_plot = 3

    grid0 = meteva.base.get_grid_of_data(grd_fo)
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



    # 设置地图背景

    ax1 = plt.axes(rect1)
    add_china_map_2basemap(ax1, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax1, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax1.set_xlim((grid0.slon, grid0.elon))
    ax1.set_ylim((grid0.slat, grid0.elat))


    # 绘制格点预报场
    x = np.arange(grid0.nlon) * grid0.dlon + grid0.slon
    y = np.arange(grid0.nlat) * grid0.dlat + grid0.slat
    #clevs = [-10,0,15,20,22,24,26,28,30,32,34,35]
    #colors_grid = ["#00AAAA","#009500","#808000", "#BFBF00","#FFFF00","#FFD400","#FFAA00","#FF7F00","#FF0000","#FF002A","#FF0055","#FF0055"]
    plt.xticks([])
    plt.yticks([])
    plot_grid = ax1.contourf(x, y, grd_ob.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    ax1.set_title(grd_ob_name,fontsize=18,loc="left",y = 0.0)
    colorbar_position_grid = fig.add_axes(ob_fo_colorbar_box)  # 位置[左,下,宽,高]
    plt.colorbar(plot_grid, cax=colorbar_position_grid, orientation='vertical')
    plt.title("温度(℃)", fontsize=8,verticalalignment='bottom')

    ax2 = plt.axes(rect2)
    plt.xticks([])
    plt.yticks([])
    add_china_map_2basemap(ax2, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax2, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax2.set_xlim((grid0.slon, grid0.elon))
    ax2.set_ylim((grid0.slat, grid0.elat))
    ax2.contourf(x, y, grd_fo.values.squeeze(), levels = clevs,cmap=cmap)  # 填色图
    ax2.set_title(grd_fo_name, fontsize=18, loc="left",y = 0.0)

    clevs1 = [-5,-4,-3,-2,-1.5,-1,-0.5,0,0.5,1,1.5,2,3,4,5]
    error = grd_fo.values.squeeze() - grd_ob.values.squeeze()

    ax3 = plt.axes(rect3)
    add_china_map_2basemap(ax3, name='province', edgecolor='k', lw=0.3,encoding = 'gbk')  #"省界"
    if add_county_line:
        add_china_map_2basemap(ax3, name="county", edgecolor='k', lw=0.2, encoding='gbk')  # "县界"
    ax3.set_xlim((grid0.slon, grid0.elon))
    ax3.set_ylim((grid0.slat, grid0.elat))

    plot_grid1 = ax3.contourf(x, y,error , clevs1,cmap = "bwr")  # 填色图
    colorbar_position_grid1 = fig.add_axes(error_colorbar_box)  # 位置[左,下,宽,高]
    title_error = grd_fo_name + ' - ' + grd_ob_name
    ax3.set_title(title_error,fontsize=18, loc="left",y = 0.0,color = "k")
    plt.colorbar(plot_grid1, cax=colorbar_position_grid1, orientation='vertical')
    plt.title("误差(℃)", fontsize=8, verticalalignment='bottom')

    time_str = meteva.base.tool.time_tools.time_to_str(grid0.gtime[0])
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
    X = np.zeros((len(fo), 1))
    X[:, 0] = fo
    clf = LinearRegression().fit(X, ob)
    num_max = max(np.max(ob), np.max(fo))
    num_min = min(np.min(ob), np.min(fo))
    dmm = num_max - num_min
    if (num_min != 0):
        num_min -= 0.1 * dmm
    num_max += dmm * 0.1
    dmm = num_max - num_min
    ob_line = np.arange(num_min, num_max, dmm / 30)
    X = np.zeros((len(ob_line), 1))
    X[:, 0] = ob_line
    fo_rg = clf.predict(X)
    ax2.plot(fo, ob, '.', color='b',markersize=1)
    ax2.plot(ob_line, fo_rg, color="r")
    ax2.plot(ob_line, ob_line, '--', color="k")
    ax2.set_xlim(num_min, num_max)
    ax2.set_ylim(num_min, num_max)
    ax2.set_xlabel("预报",fontsize=10)
    ax2.set_ylabel("观测",fontsize=10)
    rg_text2 = "Y = " + '%.2f' % (clf.coef_[0]) + "* X + " + '%.2f' % (clf.intercept_)
    ax2.text(num_min + 0.05 * dmm, num_min + 0.90 * dmm, rg_text2, fontsize=15, color="r")

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
    #ax5.set_title("频率统计图", fontsize=10)
    ax5.yaxis.set_minor_locator(mpl.ticker.MultipleLocator(1000))
    maxy = max(np.max(p_fo),np.max(p_ob)) * 1.4
    ax5.set_ylim(0,maxy)

    #检验效果图
    # 绘制降水站点实况预报统计表
    ax6 = plt.axes(rect6)
    ax6.axes.set_axis_off()
    ob_mean = np.mean(grd_ob.values)
    fo_mean = np.mean(grd_fo.values)


    maee = meteva.method.continuous.score.mae(ob, fo)
    mee = meteva.method.continuous.score.me(ob, fo)
    msee = meteva.method.continuous.score.mse(ob, fo)
    rmsee = meteva.method.continuous.score.rmse(ob, fo)
    bias_ce = meteva.method.continuous.score.bias_m(ob, fo)
    cor = meteva.method.continuous.score.corr(ob,fo)


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
    if(save_path is not None):
        plt.savefig(save_path, dpi=dpi,bbox_inches='tight')
    else:
        show = True
    if show:
        plt.show()
    plt.close()



