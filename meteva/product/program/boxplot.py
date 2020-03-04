import numpy as np
import matplotlib.pyplot as plt
import datetime
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签\
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
import seaborn as sns
from meteva.nmc_vf_product.base.fun import *
import meteva



def error_boxplot(sta_ob_and_fos,threshold,group_by,group_list_list = None,save_dir = None,title = None,group_name_list = None):
    sta_ob_and_fos_list, group_list_list1 = meteva.base.fun.group(sta_ob_and_fos, group_by, group_list_list)
    if group_name_list is None:
        group_name_list = meteva.nmc_vf_product.base.get_group_name(group_list_list1)

    maxlen = 0
    for i in range(len(group_list_list1)):
        if (len(sta_ob_and_fos_list[i].index) > maxlen):
            maxlen = len(sta_ob_and_fos_list[i].index)

    dfdata = {
    }
    for i in range(len(group_list_list1)):
        dat = np.zeros(maxlen)
        len1 = len(sta_ob_and_fos_list[i].index)
        dat[0:len1] =  sta_ob_and_fos_list[i].values[:,-1] - sta_ob_and_fos_list[i].values[:,-2]
        dfdata[group_name_list[i]] = dat
    dfdata = pd.DataFrame(dfdata)

    sns.boxplot(x=group_name_list, y="要素值", data=dfdata, linewidth=0.5)

    pass

def rmse_boxplot():
    pass

def abs_boxplot():
    pass

#箱体图(min 25% 50% 75% )
def dboxplot(self, sout_abs_path, dfdata, xcol="variable", ycol="value", plottype="box", color="skyblue",
               xticklabels=None, yticks=None, xtick_label_rotation=90, xticks_fontsize=3, ylabel_fontsize=20,
               fliersize=1.0, format="png", dpi=300, figsize=[15,10], xlabel=None, ylabel=None,
               faxhline=2.0, axhline_width=1, axhline_color='red', axhline_linestyle=":",
               mean_line_width=2.0, mean_line_color='red', mean_line_linestyle="--",
               right_data=None, right_yticks=None, right_ycol="Hit", right_ylabel=None, right_color="blue",
               right_markers="*",legend_fontsize=20):

    fig = plt.figure(figsize=figsize)
    if plottype=="swarm":
      ax = sns.swarmplot(x=xcol, y=ycol, data=dfdata)
    elif plottype=="violin":
      ax = sns.violinplot(x=xcol, y=ycol, data=dfdata)
    elif plottype=="cat":
      ax = sns.catplot(x=xcol, y=ycol, data=dfdata)
    else:
      ax = sns.boxplot(x=xcol, y=ycol, data=dfdata, fliersize=fliersize, linewidth=0.5, color=color)
    #画阈值水平线
    ax.axhline(faxhline, linewidth=axhline_width, color=axhline_color, linestyle=axhline_linestyle)
    #画平均线
    fmean=dfdata[ycol].mean()
    print(f"MAE:{fmean:.4f}")
    l2=ax.axhline(fmean, linewidth=mean_line_width, color=mean_line_color, linestyle=mean_line_linestyle)
    l2.set_label('MAE')
    #图例
    h,l = ax.get_legend_handles_labels()
    ltlabel=["MAE"]
    ax.legend(handles=h, labels=l, loc="upper left", fontsize=legend_fontsize, shadow=False)
    #添加右边y轴
    if right_data is not None:
      ax2 = ax.twinx()
      line=sns.lineplot(x=xcol, y=right_ycol, data=right_data, linewidth=axhline_width, markers=True, ax=ax2, legend="brief")
      #HIT平均线
      fmean=right_data[right_ycol].mean()
      fmax=right_data[right_ycol].max()
      fmin=right_data[right_ycol].min()
      ax2.axhline(fmean, linewidth=axhline_width, color=right_color, linestyle="-.")
      print(f"Hit mean:{fmean:.2f}, max:{fmax:.2f}, min:{fmin:.2f}")
      #图例
