import matplotlib.pyplot as plt
import math
import meteva
import numpy as np


def bootstrap(data, B, c, func):
    """
    计算bootstrap置信区间
    :param data: array 保存样本数据
    :param B: 抽样次数 通常B>=1000
    :param c: 置信水平
    :param func: 样本估计量
    :return: bootstrap置信区间上下限
    """
    array = np.array(data)
    n = len(array)
    sample_result_arr = []
    for i in range(B):
        index_arr = np.random.randint(0, n, size=n)
        data_sample = array[index_arr]
        sample_result = func(data_sample)
        sample_result_arr.append(sample_result)
    a = 1 - c
    k1 = int(B * a / 2)
    k2 = int(B * (1 - a / 2))
    auc_sample_arr_sorted = sorted(sample_result_arr)
    lower = auc_sample_arr_sorted[k1]
    higher = auc_sample_arr_sorted[k2]

    return lower, higher


def plot_confidence(result_tdt ,B = 10000 ,c = 0.95
                    ,ncol = 1 ,title_list = None ,vmax = None ,vmin = None ,vmax_delta = None,
                    sparsify_xticks = 1, sup_fontsize = 12 ,xlabel ="时效(单位:hour)" ,ylabel = "Score" ,
                    ylabel_delta = "Score Delta" ,width = 10
                    ,height = 6,
                    dpi=300 ,legend_loc =  "upper center" ,wspace = None ,hspace = None,save_path = None,show = False):

    fig = plt.figure(figsize=(width, height), dpi=dpi)
    spasify = sparsify_xticks

    if isinstance(result_tdt ,list):
        result_tdt_list = result_tdt
    else:
        result_tdt_list = [result_tdt]

    member_list = meteva.base.get_stadata_names(result_tdt_list[0])


    nplot = len(result_tdt_list)
    h_title = sup_fontsize * 0.025
    h_xlabel = sup_fontsize * 0.025
    w_ylabel =  sup_fontsize * 0.05
    w_right =  0.1


    nrow = int(math.ceil(nplot / ncol))
    w_plot = (width -w_right - ncol * w_ylabel) / ncol
    h_plot = (height - nrow * (h_xlabel + h_title)) / nrow


    if wspace is None:
        wspace = w_ylabel
    if hspace is None:
        hspace = h_title + h_xlabel

    for p in range(nplot):

        result1 = meteva.base.sele_by_para(result_tdt_list[p], drop_IV=True)
        result_list, dtime_list = meteva.base.group(result1, g="dtime")
        ndtime = len(result_list)
        x = np.arange(ndtime)

        confi = np.zeros(ndtime)
        score_ctrl = np.zeros(ndtime)
        score_test = np.zeros(ndtime)

        for i in range(len(result_list)):
            result1 = result_list[i]
            score_ctrl[i] = np.mean(result1.iloc[:, -2].values)
            score_test[i] = np.mean(result1.iloc[:, -1].values)
            delta = result1.iloc[:, -1].values - result1.iloc[:, -2].values
            lower, higher = bootstrap(delta, B, c, np.nanmean)
            confi[i] = (higher - lower) / 2

        dscore = score_test - score_ctrl

        vmax0 = np.max(np.array([score_ctrl, score_test]))
        vmin0 = np.min(np.array([score_ctrl, score_test]))


        d0 = (vmax0 - vmin0)
        if vmax is None:
            vmax1 = vmax0 + d0 * 0.3
        else:
            vmax1 = vmax

        if vmin is None:
            vmin1 = vmin0 - d0 * 0.1
        else:
            vmin1 = vmin



        pi = p % ncol
        pj = int(p / ncol)
        rect1 = [(w_ylabel + pi * (wspace + w_plot)) / width,
                 (h_xlabel + (nrow - 1 - pj) * (hspace + h_plot) + 0.4 * h_plot) / height,
                 w_plot / width, 0.6 * h_plot / height]

        score_ctrl[score_ctrl == meteva.base.IV] = 0
        score_test[score_test == meteva.base.IV] = 0
        ax1 = plt.axes(rect1)
        plt.bar(x - 0.2, score_ctrl, width=0.4, label=member_list[0], color="k")
        plt.bar(x + 0.2, score_test, width=0.4, label=member_list[1], color="r")
        plt.legend(fontsize=sup_fontsize * 0.8, ncol=2, loc=legend_loc)
        plt.ylim(vmin1, vmax1)
        plt.ylabel(ylabel, fontsize=sup_fontsize * 0.8)
        plt.xlim(-0.5, ndtime - 0.5)
        if title_list is not None:
            plt.title(title_list[p])

        rect2 = [(w_ylabel + pi * (wspace + w_plot)) / width,
                 (h_xlabel + (nrow - 1 - pj) * (hspace + h_plot)) / height,
                 w_plot / width, 0.4 * h_plot / height]
        ax2 = plt.axes(rect2)
        plt.bar(x, -confi, width=0.4, color="w", edgecolor="k")
        plt.bar(x, confi, width=0.4, color="w", edgecolor="k")
        plt.plot(x, dscore, color="r")
        plt.axhline(y=0, color="k", linewidth=0.5)

        vmax1 = np.max(np.array([confi, np.abs(dscore)]))
        if vmax_delta is None:
            vmax_delta = vmax1 * 1.5

        plt.ylim(-vmax_delta, vmax_delta)
        plt.xlim(-0.5, ndtime - 0.5)
        xticks = x[spasify - 1::spasify]
        xticks_labels = dtime_list[spasify - 1::spasify]
        plt.xticks(xticks, xticks_labels, fontsize=sup_fontsize * 0.7)
        plt.xlabel(xlabel, fontsize=sup_fontsize * 0.8)
        plt.ylabel(ylabel_delta, fontsize=sup_fontsize * 0.8)



def score_compare(sta_ob_and_fos0,method,grade_list = None,compare = ">=",s = None,B = 1000 ,c = 0.95
                    ,ncol = 1 ,title_list = None ,vmax = None ,vmin = None ,vmax_delta = None,
                    sparsify_xticks = 1, sup_fontsize = 12 ,xlabel =None ,ylabel = "Score" ,
                    ylabel_delta = "Score Delta" ,width = 10
                    ,height = 6,
                    dpi=300 ,legend_loc =  "upper center" ,wspace = None ,
                         hspace = None,save_path = None,show = False):
    if grade_list is not None:
        result_tdt,_ = meteva.product.score_tdt(sta_ob_and_fos0,method,s = s,plot=None,grade_list= grade_list,compare = compare)
    else:
        result_tdt, _ = meteva.product.score_tdt(sta_ob_and_fos0, method, s=s, plot=None)

    plot_confidence(result_tdt,B = B,c = c,ncol = ncol ,title_list=title_list,vmax = vmax,vmin = vmin,vmax_delta=vmax_delta,
                    sparsify_xticks=sparsify_xticks,sup_fontsize=sup_fontsize,xlabel=xlabel,ylabel= ylabel,
                    ylabel_delta=ylabel_delta,width=width,height=height,
                    dpi = dpi,legend_loc=legend_loc,wspace=wspace,hspace=hspace,save_path=save_path,show=show)


def score_confidence(sta_ob_and_fos0,method,grade_list = None,compare = ">=",s = None,B = 1000 ,c = 0.95,
                   plot = "bar",**kwargs):

    sta_sele = meteva.base.sele_by_dict(sta_ob_and_fos0,s = s)
    if grade_list is not  None:
        result_tdt_list,_ = meteva.product.score_tdt(sta_sele,method,plot=None,grade_list= grade_list,compare = compare)
        result_dt, dtime_list = meteva.product.score(sta_sele, method, g="dtime",
                                                     plot=None,grade_list= grade_list,compare = compare)
        member_list = meteva.base.get_stadata_names(result_tdt_list[0])
        ngrade = len(grade_list)
        ndtime = len(dtime_list)
        nmember = len(member_list)

        name_list_dict = {
            "dtime": dtime_list,
            "member":member_list,
            "grade": grade_list,
        }
        lower = np.zeros((ndtime, nmember,ngrade))
        higher = np.zeros((ndtime, nmember,ngrade))

        for g in  range(len(grade_list)):
            result_tdt = result_tdt_list[g]
            for i in range(ndtime):
                result1 = meteva.base.sele_by_para(result_tdt, dtime=dtime_list[i],drop_IV=True)
                for k in range(len(member_list)):
                    member = member_list[k]
                    score = result1[member].values
                    lower1, higher1 = bootstrap(score, B, c, np.nanmean)
                    lower[i, k,g] = lower1
                    higher[i, k,g] = higher1
        score = result_dt

    else:
        result_tdt, _ = meteva.product.score_tdt(sta_sele, method,  plot=None)
        result_dt,dtime_list = meteva.product.score(sta_sele, method,g = "dtime",  plot=None)


        member_list = meteva.base.get_stadata_names(result_tdt)
        ndtime = len(dtime_list)
        nmember = len(member_list)
        lower = np.zeros((ndtime,nmember))
        higher = np.zeros((ndtime, nmember))
        for i in range(ndtime):
            result1 = meteva.base.sele_by_para(result_tdt,dtime = dtime_list[i])
            for k in range(len(member_list)):
                member = member_list[k]
                score = result1[member].values

                lower1, higher1 = bootstrap(score, B, c, np.nanmean)
                lower[i,k] =lower1
                higher[i,k] = higher1

        name_list_dict = {
            "dtime":dtime_list,
            "member": member_list,
        }
        score = result_dt

    delta = (higher - lower)/2
    lower = score - delta
    higher = score + delta
    if plot =="bar":
        meteva.base.bar(score,name_list_dict,axis="dtime",lower = lower,higher = higher, **kwargs)
    elif plot =="line":
        meteva.base.plot(score, name_list_dict,axis="dtime",lower = lower,higher = higher, **kwargs)