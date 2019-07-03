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