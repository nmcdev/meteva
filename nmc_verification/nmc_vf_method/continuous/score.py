import numpy as np

def me(Ob,Fo):
    '''
    me 求两组数据的误差平均值
    -----------------------------
    :param Ob: 实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return:
    '''
    mean_error = np.mean(Ob - Fo)
    return mean_error

def mae(Ob,Fo):
    '''
    mae对两组数据求平均绝对值误差
    -----------------------
    :param Ob:实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return: mean_abs_error
    '''
    mean_abs_error = np.mean(np.abs(Ob-Fo))
    return mean_abs_error

def mse(Ob,Fo):
    '''
    mse  求两组数据的均方误差
    ----------------------------------
    :param Ob:实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return: mean_sqrt_error
    '''
    mean_sqrt_error = np.mean(np.square(Ob - Fo))
    return  mean_sqrt_error

def rmse(Ob,Fo):
    '''
    rmse 求两组数据的均方根误差
    ------------------------------
    :param Ob:实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return:mean_sqrt_error
    '''
    mean_sqrt_error = np.sqrt(np.mean(np.square(Ob - Fo)))
    return mean_sqrt_error

def bias(Ob,Fo):
    '''
    bias 求预测数据和实况数据的平均值的比
    ------------------------------
    :param Ob:实况数据 一维numpy
    :param Fo:预测数据 一维numpy
    :return:  bias0
    '''
    bias0 = np.mean(Fo) / (np.mean(Ob) + 1e-6)
    return bias0

def corr(Ob,Fo):
    '''
    corr 求实况数据还和预测数据之间的相关系数
    -----------------------------
    :param Ob: 实况数据 不定长维度的numpy
    :param Fo: 测试数据 不定长维度的numpy
    :return: corr0
    '''
    ob_f = Ob.flatten()
    fo_f = Fo.flatten()
    corr0 = np.corrcoef(ob_f,fo_f)[0,1]
    return corr0

#平均相对误差
def are(Ob,Fo):
    s = Ob + Fo
    if np.sum(s) ==0:
        return 0
    else:
        d = Ob - Fo
        s1 = s[s>0]
        d1 = d[s>0]

        are0 = np.mean(np.abs(d1/s1))
        return are0

#FSS
def FSS(Ob,Fo,window_sizes_list = [3],threshold_list = [50],Masker = None):
    shape = Ob.shape
    nw = len(window_sizes_list)
    nt = len(threshold_list)
    fss = np.zeros((nw,nt))
    for i in range(nw):
        kernel = np.ones((nw,nw))
        ws = np.sum(kernel)
        if Masker is not None:
            masker_sum = np.convolve(Masker, kernel,mode= "same") + 1e-10
        else:
            masker_sum = np.ones(shape) * ws + 1e-10
        for j in range(nt):
            ob_hap = np.zeros(shape)
            ob_hap[Ob>threshold_list[j]] = 1
            fo_hap = np.zeros(shape)
            ob_hap[Ob>threshold_list[j]] = 1
            ob_hap_sum = np.convolve(ob_hap,kernel,mode = "same")
            fo_hap_sum = np.convolve(fo_hap,kernel,mode = "same")
            ob_hap_p = ob_hap_sum/masker_sum
            fo_hap_p = fo_hap_sum/masker_sum
            a1 = np.sum(np.power(ob_hap_p - fo_hap_p,2))
            a2 = np.sum(np.power(ob_hap_p,2)) + np.sum(np.power(fo_hap_p,2))
            fss[i,j] = 1 - a1 / (a2 + 1e-10)
    return fss