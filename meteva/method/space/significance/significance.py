
import  numpy as np
from sklearn.utils import resample
from scipy import stats
import pandas as pd
import meteva
import copy


def CI_fun(CI_field, est_field, replacement=np.nan):
    test = est_field[0.5 * CI_field < abs(est_field)] = replacement
    return test


def inside(DF):
    # result = CI_fun(DF['Upper'] - DF['Lower'], DF['Estimate'])
    aa = DF['Upper'] - DF['Lower']
    bb = DF['Estimate']
    result = 0.5 * aa < abs(bb)  #满足条件代表平均值是显著偏离1的
    return result


def sig_coverage(DF):
    out = {}
    tmp = inside(DF)
    #sum(DF['Estimate'] == None) =0 表示df中的内容是误差均值，否则表示其它暂无支持的统计内容
    # out 是表示均值显著的占比。
    out = sum(tmp[tmp == 1]) / len(tmp) - sum(DF['Estimate'] == None)
    return out


def sig_cor_t(r, Len=40):
    t = abs(r) * np.sqrt((Len - 2) / (1 - r ** 2))
    # qt -> stats.t(df=359).ppf((0.84473448, 0.15382939))
    palpha_cor = 1 - stats.t.cdf(t, df=Len - 2)  # t分布的分布函数
    return palpha_cor


def MCdof(x, ntrials=1000, field_sig=0.05, zfun="rnorm", zfun_args='NULL',
          which_test=["t", "Z", "cor.test"], show=False):

    output = {}
    if len(which_test) > 1:
        which_test = "t"
    x = np.array(x)
    xdim = x.shape
    tlen = xdim[0]
    B_dof_test = np.zeros(ntrials)
    if show:
        print("\n", "Looping through ", ntrials, " times to simulate data and take correlations.  Enjoy!\n")
    for i in range(1, ntrials):
        if show and (i < 100 or i % 100 == 0):
            print(i, " ")
        # rnorm(n, mean = 0, sd = 1)返回值是n个正态分布随机数构成的向量。
        mu, sigma = 0, 1  # mean and standard deviation
        z = np.random.normal(mu, sigma, tlen)  # 正态分布存在差异
        '''
        #绘制正态分布图
        count, bins, ignored = plt.hist(s, 30, density=True)
        plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ),
                 linewidth=2, color='r')
        plt.show()
        '''
        # 判断为否，不执行
        tmp = np.array([])
        if which_test == "cor.test":
            # tmp = apply(x, 2, cortester, y = z)
            tmp = np.corrcoef(x)[1, 0]
        else:
            #默认进行t检验
            # 计算pearson相关系数
            cor = np.array([])
            for j in range(x.shape[1]):  # 循环变量有问题
                x_j = x[:, j]
                xz = np.array([x_j, z])
                cor_0 = np.corrcoef(xz)[1, 0]  # 目前存在偏差是由于z的结果不一致导致，方法本身经过验证是没问题的
                cor = np.append(cor, cor_0)
            cor_value = np.abs(cor)
            # 只翻译默认的第一个参数
            if which_test == "t":
                tmp = sig_cor_t(r=cor_value, Len=tlen)  # 输出结果
            '''
            else if (which.test == "Z") 
                tmp <- sig.cor.Z(cor.value, len = tlen, ...)
            '''

        tmp_small = tmp[field_sig>tmp] #提取显著性超阈值那部分显著性

        # if tmp_small.size == 0:
        #     B_dof_test[i] = 1
        # else:
        #     B_dof_test[i] = np.mean(tmp_small)  # 显著性超阈值部分的均值
        B_dof_test[i] = tmp_small.size / tmp.size

    minsigcov_val = np.quantile(a=B_dof_test, q=1 - field_sig)
    output = {'MCprops': B_dof_test, 'minsigcov': minsigcov_val}
    return output

def is_sig(X, blockboot_result_df, n=1000, fld_sig=0.05, show=False):
    output = {}
    '''
    X = errfield
    blockboot_result_df = hold
    n = ntrials
    fld_sig = field_sig
    '''

    # sig_result 表示利用蒙特卡罗方法测试所有格点和随机数求相关后，表现为具有显著性的格点数占比。
    sig_result = MCdof(X, ntrials=n, field_sig=0.05, show=show)['minsigcov']

    #actual_coverage表示平均值具有显著性的格点数占比。
    actual_coverage = sig_coverage(DF=blockboot_result_df)
    sig = actual_coverage > sig_result  #输出结果
    '''
    output <- list(name = as.character(deparse(substitute(X))), 
                   required = as.numeric(sig.results), actual = as.numeric(actual.coverage), 
                   issig = as.logical(sig))
    '''
    output = {"name": X, "required": sig_result, "actual": actual_coverage, "issig": sig}

    return output


def mean_estimate(Z, numrep=1000, alpha=0.05,block_length='NULL', bootfun="mean", show=False):

    booted = {}
    if bootfun == 'mean':
        Z = np.ma.masked_array(Z, np.isnan(Z))
        bootfun = np.mean(Z, axis=0)
        booted_t0 = bootfun
    Z = np.array(Z)
    if len(Z.shape) == 1:
        Z = Z.reshape((Z.size,1))
    zdim = Z.shape

    n = zdim[0]
    m = zdim[1]
    out = pd.DataFrame(np.zeros(shape=(m, 3)), columns=['Lower', 'Estimate', 'Upper'])
    if block_length is 'NULL':
        block_length = np.floor(np.sqrt(n))

    if block_length == 1:
        # 判断为假，不执行
        # booted = boot(Z, bootfun, R = numrep)    #未翻译
        for i in range(Z.shape[1]):
            booted_list = [np.mean(resample(Z[:, i], n_samples=Z.shape[0])) for _ in
                           range(numrep)]  # n_samples是受tseries控制
            booted_0 = np.array(booted_list)
            booted = np.append(booted, booted_0)
    else:
        # booted = tsboot(Z, bootfun, l = block.length, R = numrep, sim = "fixed")
        booted = np.array(())
        for i in range(Z.shape[1]):
            booted_list = [np.mean(resample(Z[:, i], n_samples=Z.shape[0])) for _ in range(numrep)]  # n_samples是受tseries控制
            booted_0 = np.array(booted_list)
            booted = np.append(booted, booted_0)
            # booted = np.stack((booted, booted_0), axis = 1)
    booted_t = booted.reshape(numrep, Z.shape[1], order='F')
    booted = {'t0': booted_t0, 't': booted_t, 'R': numrep}
    out['Estimate'] = booted['t0']
    #print(booted_t)
    if block_length == 1:
        # 判断为假,不执行
        conf = 1 - alpha
        tmp_Lower = np.percentile(a=booted_t, q=100*(1 + conf) / 2, axis=0)
        tmp_Upper = np.percentile(a=booted_t, q=100*(1 - conf) / 2, axis=0)
        out['Lower'] = tmp_Lower
        out['Upper'] = tmp_Upper

        '''
        #原本R的逻辑
        for i in range(1, m):
            tmp = boot_CI(booted, conf = 1-alpha, Type = "bac", index = i)
            out['Lower'][i] = tmp["bca"][:, 4]
            out['Upper'][i] = tmp["bca"][:, 5]
        '''
    else:
        if show:
            print(
                "LocSig: You chose to use the BCa method, but block.length != 1.  Using percentile method with circular block bootstrap instead.")

        conf = 1 - alpha
        tmp_Lower = np.percentile(a=booted_t, q=100*(1 - conf) / 2, axis=0)
        tmp_Upper = np.percentile(a=booted_t, q=100*(1 + conf) / 2, axis=0)
        out['Lower'] = tmp_Lower
        out['Upper'] = tmp_Upper

        '''
        #原本R的逻辑
        for i in range(1, m):
            #计算置信度区间（分位数:np.percentile）
            #可信度=0.90,置信区间宽度=0.05, 置信区间上限=0.07,置信区间下限=0.02,表示:发生在区间(0.02,0.07)这个范围内的可能性为0.90
            tmp = boot_CI(booted, conf = 1-alpha, Type = "perc", index = i)
            out['Lower'[i]] = tmp["prec"][:, 4]
            out['Upper'][i] = tmp["prec"][:, 5]
        '''

    # out['class'] = "LocSig"
    #result = np.array([out["Lower"],out["Estimate"],out["Upper"]]).T

    return out


def local_sig(ob,fo,numrep=1000, alpha=0.05,block_length='NULL', bootfun="mean", show=False):


    if len(fo.shape) == len(ob.shape):
         error = fo - ob
         out = mean_estimate(error,numrep=numrep, alpha=alpha,block_length=block_length, bootfun=bootfun, show=show)
         index = np.abs(out["Estimate"].values) - (out["Upper"].values-out["Lower"].values)/2

    else:
        index_list = []
        for i in range(fo.shape[0]):
            error = fo[i,...] - ob
            out = mean_estimate(error, numrep=numrep, alpha=alpha, block_length=block_length, bootfun=bootfun,
                                show=show)
            index = np.abs(out["Estimate"].values) - (out["Upper"].values - out["Lower"].values) / 2
            index_list.append(index)
        index = np.array(index_list)
    return index

def spatbiasFS(X, Y, loc='NULL', block_length='NULL', alpha_boot=0.05,
               field_sig=0.05, bootR=1000, ntrials=1000, show=False):
    out = {}
    '''
    if (!is.null(loc)) {
        data.name <- c(as.character(substitute(X)), as.character(substitute(Y)), 
                   as.character(substitute(loc)))
        names(data.name) <- c("verification", "forecast", "locations")
        }
    else {
        data.name <- c(as.character(substitute(X)), as.character(substitute(Y)))
        names(data.name) <- c("verification", "forecast")
        }
    out$data.name <- data.name
    '''
    errfield = Y - X
    hold = mean_estimate(Z=errfield, numrep=bootR, block_length=block_length,
                         alpha=alpha_boot)
    res = is_sig(errfield, hold, n=ntrials, fld_sig=field_sig, show=show)
    out['block_boot_results'] = hold
    out['sig_results'] = res
    out['field_significance'] = field_sig
    out['alpha_boot'] = alpha_boot
    out['bootR'] = bootR
    out['ntrials'] = ntrials
    out['class'] = "spatbiasFS"

    return out


def field_sig(ob, fo, member_list = None,numrep=1000,alpha=0.05, block_length='NULL',return_mid = False):

    index_list = []
    if len(fo.shape) == len(ob.shape):
        index = local_sig(ob,fo, numrep=numrep, alpha=alpha,block_length=block_length)
        rate0 = len(index[index>0])/len(index)
        errfield = fo - ob
        rate1 = MCdof(errfield, ntrials=numrep, field_sig=0.05)['minsigcov']
        index_dict = {"sig_rate":rate0,"rate_threshold":rate1,"is_sig":rate0>=rate1}
        index_list.append(index)
    else:
        index_dict = {"sig_rate": [], "rate_threshold": [], "is_sig": []}
        for i in range(fo.shape[0]):
            fo1= fo[i, ...]
            index = local_sig(ob, fo1, numrep=numrep, alpha=alpha, block_length=block_length)
            rate0 = len(index[index > 0]) / len(index)
            errfield = fo1- ob
            rate1 = MCdof(errfield, ntrials=numrep, field_sig=0.05)['minsigcov']
            index_dict["sig_rate"].append(rate0)
            index_dict["rate_threshold"].append(rate1)
            index_dict["is_sig"].append(rate0>=rate1)
            index_list.append(index)

    index_f =pd.DataFrame(index_dict)
    if member_list is not None:
        index_f.index = member_list

    if return_mid:
        index_l = np.array(index_list)
        return index_f,index_l
    else:
        return index_f

def field_sig_id(sta_all,s = None,numrep=1000,alpha=0.05,plot = None,save_path = None,show = False, block_length='NULL',**kwargs):

    sta_all1 = meteva.base.sele_by_dict(sta_all, s=s)

    level = set(sta_all1["level"].values.tolist())
    if len(level)>1:
        print("暂时不支持同时多个层次开展显著性检验，可以先用s参数选取某一层的数据进行检验")

    sta_with_IV = sta_all1.drop_duplicates("id")
    index_station = meteva.base.in_member_list(sta_with_IV,member_list=[1,2],name_or_index="index")
    nid = len(sta_with_IV.index)
    sta_with_IV["time"] =meteva.base.IV
    sta_with_IV["dtime"] = meteva.base.IV
    sta_with_IV = meteva.base.in_member_list(sta_with_IV,[0],name_or_index="index")

    for i in range(1,3):
        sta_expand = []
        value_list = list(set(sta_all1.iloc[:,i].values.tolist()))
        if i == 1:
            for j in range(len(value_list)):
                value_list[j] = meteva.base.tool.all_type_time_to_time64(value_list[j])
        for value in value_list:
            sta1 = copy.deepcopy(sta_with_IV)
            sta1.iloc[:,i] = value
            sta_expand.append(sta1)
        sta_with_IV = meteva.base.concat(sta_expand)

    sta_combine = meteva.base.combine_on_level_time_dtime_id(sta_all1, sta_with_IV,how = 'outer')
    sta_combine = sta_combine.fillna(value=0)
    sta_combine.sort_values(by=["time","dtime","id"])
    nt = int(len(sta_combine.index)/nid)
    data_names  = meteva.base.get_stadata_names(sta_combine)
    nmember = len(sta_combine.columns)
    #sta_ob = meteva.base.sele_by_para(sta_combine,member=[data_names[0]])
    obs = sta_combine.iloc[:,6].values.reshape((nt,nid))
    fst = sta_combine.iloc[:,7:nmember-1].values.reshape(nmember-8,nt,nid)

    index_f,index_l = field_sig(obs,fst,member_list=data_names[1:-1],numrep = numrep,alpha = alpha,block_length=block_length,return_mid=True)


    for i in range(len(data_names)-2):
        index_station.iloc[:,6+i] = index_l[i,:]
    if plot == "scatter":
        if save_path is None:
            show = True
        meteva.base.tool.plot_tools.scatter_sta(index_station,cmap="me",subplot="member",sup_title="单点偏差显著性指标",show=show,save_path=save_path,**kwargs)

    return index_f,index_station

