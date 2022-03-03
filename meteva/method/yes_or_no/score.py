import numpy as np
import copy
from meteva.base import IV


def ob_fo_hr_hfmc(hfmc_array):
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]
    total = hit+fal+mis+cn
    shape1 = list(hfmc_array.shape)
    if len(hfmc_array.shape) == 2:
        result = np.zeros((2,shape1[0]))
        result[0, :] = (hit + mis) / total
        result[1, :] = (hit + fal) / total
    else:
        result = np.zeros((1+shape1[0],shape1[1]))
        result[0, :] = (hit[0,:] + mis[0,:]) / total[0,:]
        result[1:, :] = (hit + fal) / total
    return result


def ob_fo_hc_hfmc(hfmc_array):
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]
    total = hit+fal+mis+cn
    shape1 = list(hfmc_array.shape)
    if len(hfmc_array.shape) == 2:
        result = np.zeros((2,shape1[0]))
        result[0, :] = (hit + mis)
        result[1, :] = (hit + fal)
    else:
        result = np.zeros((1+shape1[0],shape1[1]))
        result[0, :] = (hit[0,:] + mis[0,:])
        result[1:, :] = (hit + fal)
    return result



def ob_fo_hr(Ob,Fo,grade_list = [1e-30],compare =">=",compair = None):
    '''

    :param Ob:
    :param Fo:
    :param grade_list:
    :return:
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return ob_fo_hr_hfmc(hfmc_array)

def ob_fo_hc(Ob,Fo,grade_list = [1e-30],compare =">=",compair = None):
    '''

    :param Ob:
    :param Fo:
    :param grade_list:
    :return:
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return ob_fo_hc_hfmc(hfmc_array)

def hap_count(Ob,Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    观测发生率，观测的正样本占总样本的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return:  0-1的实数，观测的正样本占总样本的比例
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    result = []
    for grade in grade_list:
        if compare == ">=":
            result.append(Ob[Ob>=grade].size)
        elif compare == "<=":
            result.append(Ob[Ob <= grade].size)
        elif compare == ">":
            result.append(Ob[Ob>grade].size)
        elif compare == "<":
            result.append(Ob[Ob < grade].size)
        else:
            print("compare 参数只能是 >=   >  <  <=  中的一种")
            return
    if len(grade_list) == 1:
        result = result[0]
    else:
        result = np.array(result)
    return result

def s(Ob,Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    观测发生率，观测的正样本占总样本的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return:  0-1的实数，观测的正样本占总样本的比例
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    result = []
    num = Ob.size
    for grade in grade_list:
        if compare == ">=":
            result.append(Ob[Ob>=grade].size/num)
        elif compare == "<=":
            result.append(Ob[Ob <= grade].size / num)
        elif compare == ">":
            result.append(Ob[Ob > grade].size/num)
        elif compare == "<":
            result.append(Ob[Ob < grade].size / num)
        else:
            print("compare 参数只能是 >=   >  <  <=  中的一种")
    if len(grade_list) == 1:
        result = result[0]
    else:
        result = np.array(result)
    return result

def s_hfmc(hfmc_array):
    '''
    观测发生率，观测的正样本占总样本的比例
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return:0-1的实数，观测的正样本占总样本的比例
    '''
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]
    s0 = (hit + mis) / (hit + mis + fal + cn)
    return s0

def r(Ob,Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    预测发生率，预测的正样本占总样本的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0-1的实数，预测的正样本占总样本的比例
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array= hfmc(Ob, Fo,grade_list,compare= compare)
    return r_hfmc(hfmc_array)

def r_hfmc(hfmc_array):
    '''
    观测发生率，预测的正样本占总样本的比例
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return:0-1的实数，预测的正样本占总样本的比例
    '''
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]
    r0 = (hit + fal) / (hit + mis + fal + cn)
    return r0

def pc_of_sun_rain_hfmc(hfmc_array):
    '''
    晴雨准确率
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0到1的实数，最优值为1
    '''

    hit = hfmc_array[...,0]
    fal= hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]
    cr = (hit + cn) / (hit + mis + fal + cn)
    return cr

def pc_of_sun_rain(Ob, Fo):
    '''
    晴雨准确率，考虑到T量降水的问题，其统计命中、空报、漏报和正确否定样本数的方法有些特异性，具体见hfmc_of_sun_rain
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 0到1的实数，最优值为1
    '''
    hfmc_array = hfmc_of_sun_rain(Ob, Fo)
    return pc_of_sun_rain_hfmc(hfmc_array)

def hfmc_of_sun_rain(Ob, Fo):
    '''
    晴雨准确率列联表
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: numpy 数组，其内容为 [命中数,空报数,漏报数,正确否定数]
    '''

    Ob_shape = Ob.shape
    Fo_shape = Fo.shape
    hfmc_of_sun_rain_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')

        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    for line in range(new_Fo_shape[0]):
        new_Fo[line, :][new_Fo[line, :] < 0.099] = 0
        shape = Ob.shape
        obhap = np.zeros(shape)
        obhap[Ob > 0] = 1
        fohap = np.zeros(shape)
        fohap[new_Fo[line, :] > 0] = 1
        obhap01 = np.zeros(shape)
        obhap01[Ob >= 0.1] = 1

        hit_threshold = (obhap * fohap)
        mis_threshold = (obhap01 * (1 - fohap))
        fal_threshold = ((1 - obhap) * fohap)
        cn_threshold = 1 - hit_threshold - mis_threshold - fal_threshold

        hit = hit_threshold.sum()
        fal = fal_threshold.sum()
        mis = mis_threshold.sum()
        cn = cn_threshold.sum()
        hfmc_of_sun_rain_list.append(np.array([hit, fal, mis, cn]))
    hfmc_of_sun_rain_array = np.array(hfmc_of_sun_rain_list)
    shape = list(Fo_shape[:ind])
    shape.append(4)
    hfmc_of_sun_rain_array = hfmc_of_sun_rain_array.reshape(shape)
    return hfmc_of_sun_rain_array

def pc(Ob,Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    准确率，反映被正确预报的样本占比
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0-1的实数，最优值为1
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob,Fo,grade_list,compare= compare)
    return pc_hfmc(hfmc_array)

def pc_hfmc(hfmc_array):
    '''
    准确率，反映被正确预报的样本占比
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return:
    '''
    if len(hfmc_array.shape) == 1:
        hfmc_array = hfmc_array.reshape(1,4)
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]
    accurace0 = (hit + cn) / (hit + mis + fal + cn)
    if accurace0.size ==1:
        accurace0 = accurace0[0]
    return accurace0

def pod(Ob, Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    命中率，反映观测的正样本中多少被预报
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0到1的实数，完美值为1
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return pod_hfmc(hfmc_array)

def pod_hfmc(hfmc_array):
    '''
    命中率，反映观测的正样本中多少被预报
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0到1的实数，完美值为1
    '''
    if len(hfmc_array.shape) == 1:
        hfmc_array = hfmc_array.reshape(1,4)
    hit = hfmc_array[...,0]
    mis = hfmc_array[...,2]
    sum = hit + mis
    sum[sum ==0] = -1
    pod0 = hit / sum
    pod0[sum == -1] = IV
    if pod0.size == 1:
        pod0 = pod0[0]

    return pod0

def sr(Ob, Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    报中率，反映预报的正样本中实际发生的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return:0-1,最优值为1
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return sr_hfmc(hfmc_array)

def sr_hfmc(hfmc_array):
    '''
    报中率，反映预报的正样本中实际发生的比例
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0-1,最优值为1
    '''
    if len(hfmc_array.shape) == 1:
        hfmc_array = hfmc_array.reshape(1,4)
    hit = hfmc_array[..., 0]
    fal = hfmc_array[..., 1]
    sum = hit + fal
    sum[sum ==0] = -1
    sr0 = hit / sum
    sr0[sum == -1] = IV
    if sr0.size ==1:
        sr0 = sr0[0]
    return sr0

def far(Ob, Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    空报率, 反映预报的正样本中多少未发生
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0到1的实数，最优值为0
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return far_hfmc(hfmc_array)

def far_hfmc(hfmc_array):
    '''
    空报率, 反映预报的正样本中多少实况未发生
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0到1的实数，最优值为0
    '''
    if len(hfmc_array.shape) == 1:
        hfmc_array = hfmc_array.reshape(1,4)
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    sum = hit + fal
    sum[sum == 0] = 0.1  # sum=0 是主动追求低空报的行为，所以应该给其空报率=0
    far0 = fal / sum
    if far0.size == 1:
        far0 = far0[0]
    return far0

def pofd(Ob,Fo,grade_list=[1e-30],compare =">=",compair = None):
    '''
    报空率, 事件未发生样本被预报为会发生的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0到1的实数，最优值为0
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob,Fo,grade_list,compare= compare)
    return pofd_hfmc(hfmc_array)

def pofd_hfmc(hfmc_array):
    '''
    报空率,事件未发生样本被预报为会发生的比例
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0到1的实数，最优值为0
    '''
    if len(hfmc_array.shape) == 1:
        hfmc_array = hfmc_array.reshape(1,4)
    cn = hfmc_array[...,3]
    fal = hfmc_array[...,1]
    sum = cn +fal
    sum[sum == 0] = -1
    podf0 = fal / sum
    podf0[sum ==-1] = IV
    if podf0.size ==1:
        podf0 = podf0[0]
    return podf0

def mr(Ob, Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    漏报率，观测的正样本被漏报的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0到1的实数，最优值为0
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return mr_hfmc(hfmc_array)

def mr_hfmc(hfmc_array):
    '''
    漏报率，观测的正样本被漏报的比例
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0到1的实数，最优值为0
    '''
    if len(hfmc_array.shape) == 1:
        hfmc_array = hfmc_array.reshape(1,4)
    hit = hfmc_array[...,0]
    mis = hfmc_array[...,2]
    sum = hit + mis
    sum[sum ==0]= -1
    mr0 = mis / sum
    mr0[sum == -1] = IV
    if mr0.size == 1:
        mr0 = mr0[0]
    return mr0

def bias(Ob, Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    样本偏差，预报的正样本数 和 观测的正样本数的比值
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0到正无穷的实数，完美值为1
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return bias_hfmc(hfmc_array)

def bias_hfmc(hfmc_array):
    '''
    样本偏差
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0到正无穷的实数，完美值为1
    '''
    if len(hfmc_array.shape) == 1:
        hfmc_array = hfmc_array.reshape(1,4)
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    sum = hit +mis
    sum[sum==0] = 1e-10
    bias0 = (hit + fal) / sum
    delta = fal - mis
    bias0[delta ==0] = 1
    bias0[bias0 > 1e9] = IV
    if bias0.size ==1:
        bias0 = bias0[0]
    return bias0

def bias_extend_linear(bias_array):
    '''

    :param bias_array:
    :return:
    '''
    bias_extend0 = np.abs(bias_array - 1)
    if isinstance(bias_array,float):
        if bias_array==IV:
            bias_extend0 = IV
    else:
        bias_extend0[bias_array == IV] = IV
    return bias_extend0

def bias_extend_log(bias_array):
    '''

    :param bias_array:
    :return:
    '''
    if bias_array.size ==1 :
        if bias_array == 0 or bias_array == IV:
            bias_extend0 = IV
        else:
            bias_extend0 = np.abs(np.log(bias_array))
    else:
        bias1 = np.zeros_like(bias_array)
        bias1[...] = bias_array[...]
        bias1[bias_array ==0] = IV
        bias_extend0 = np.abs(np.log(bias1))
        bias_extend0[bias_array == 0] = IV
        bias_extend0[bias_array == IV] = IV
    return bias_extend0


def ts(Ob, Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    ts评分
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0-1的实数，0代表没有技巧，完美值为1
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array =hfmc(Ob, Fo, grade_list,compare= compare)
    return ts_hfmc(hfmc_array)


def hfmdt(Ob, Fo, dtime, grade_list=[1e-30],compare =">=",compair = None):

    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    if compair not in [">=",">","<","<="]:
        print("compare 参数只能是 >=   >  <  <=  中的一种")
        return

    Ob_shape = Ob.shape
    Fo_shape = Fo.shape
    hfmdt_array_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    for line in range(new_Fo_shape[0]):
        hfmdt_array = np.zeros((len(grade_list), 4))
        tn = Ob.size
        for i in range(len(grade_list)):
            threshold = grade_list[i]
            obhap = np.zeros_like(Ob)
            fohap = np.zeros_like(new_Fo[line, :])
            if compare == ">=":
                obhap[Ob >= threshold] = 1
                fohap[new_Fo[line, :] >= threshold] = 1
            elif compare == "<=":
                obhap[Ob <= threshold] = 1
                fohap[new_Fo[line, :] <= threshold] = 1
            elif compare == ">":
                obhap[Ob > threshold] = 1
                fohap[new_Fo[line, :] > threshold] = 1
            elif compare == "<":
                obhap[Ob < threshold] = 1
                fohap[new_Fo[line, :] < threshold] = 1

            hit_threshold = (obhap * fohap)
            mis_threshold = (obhap * (1 - fohap))
            fal_threshold = ((1 - obhap) * fohap)
            cn_threshold = hit_threshold * dtime - fal_threshold * 0.2 * dtime
            hfmdt_array[i, 0] = hit_threshold.sum()
            hfmdt_array[i, 1] = fal_threshold.sum()
            hfmdt_array[i, 2] = mis_threshold.sum()
            hfmdt_array[i, 3] = cn_threshold.sum()
        hfmdt_array_list.append(hfmdt_array)
    hfmdt_array = np.array(hfmdt_array_list)
    shape = list(Fo_shape[:ind])
    shape.append(len(grade_list))
    shape.append(4)
    hfmdt_array = hfmdt_array.reshape(shape)
    return hfmdt_array


def effective_dtime_hfmdt(hfmdt_array):
    '''

    :param hfmdt_array:
    :return:
    '''
    if len(hfmdt_array.shape) == 1:
        hfmc_array = hfmdt_array.reshape(1,4)
    efdt = hfmdt_array[...,3]
    hit = hfmdt_array[...,0]
    fal = hfmdt_array[...,1]
    mis = hfmdt_array[...,2]
    sum = hit +mis + fal
    sum[sum ==0] = 1e-10
    edt_array =efdt / sum
    return edt_array

def effective_dtime(Ob,Fo,dtime,grade_list = [1e-30],compare =">=",compair = None):
    '''

    :param Ob: ob
    :param Fo: fo
    :param dtime: 预报时效
    :param grade_list: 等级
    :return:  有效预报时效
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmdt_array = hfmdt(Ob,Fo,dtime,grade_list,compare= compare)
    edt_array =effective_dtime_hfmdt(hfmdt_array)
    return edt_array


def ts_hfmc(hfmc_array):
    '''
    ts评分
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    倒数第2维或为等级维度
    :return: 0-1的实数，0代表没有技巧，完美值为1
    '''
    if len(hfmc_array.shape) == 1:
        hfmc_array = hfmc_array.reshape(1,4)
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    sum = hit +mis + fal
    sum[sum ==0] = -1
    ts_array =hit / sum
    ts_array[sum == -1] = IV
    if ts_array.size ==1:
        ts_array = ts_array[0]
    return ts_array

def ets(Ob, Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    ets评分
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: -1/3 到1 的实数，完美值为1, 0代表没有技巧
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return ets_hfmc(hfmc_array)

def ets_hfmc(hfmc_array):
    '''
    ets评分
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    倒数第2维或为等级维度
    :return: -1/3 到1 的实数，完美值为1, 0代表没有技巧
    '''
    if len(hfmc_array.shape) == 1:
        hfmc_array = hfmc_array.reshape(1,4)
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]

    total = hit + mis + fal + cn
    hit_random = (hit + mis) * (hit + fal) / total
    sum = hit + mis + fal - hit_random
    sum[sum == 0] = -1
    ets_array = (hit - hit_random) / sum
    ets_array[sum == -1] = IV
    if ets_array.size ==1:
        ets_array = ets_array[0]
    return ets_array

def hfmc(Ob, Fo, grade_list=[1e-30],compare =">=",compair = None):
    '''
    预报列联表
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: python numpy数组，其中最后一维长度为4，分别记录了（命中数，漏报数，空报数，正确否定数）
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    if compare not in [">=",">","<","<="]:
        print("compare 参数只能是 >=   >  <  <=  中的一种")
        return
    Ob_shape = Ob.shape
    Fo_shape = Fo.shape
    hfmc_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    for line in range(new_Fo_shape[0]):
        fo = new_Fo[line, :]
        hfmc_array = np.zeros((len(grade_list), 4))
        for i in range(len(grade_list)):
            threshold = grade_list[i]
            obhap = np.zeros_like(Ob)
            fohap = np.zeros_like(fo)
            if compare ==">=":
                obhap[Ob >= threshold] = 1
                fohap[fo >= threshold] = 1
            elif compare =="<=":
                obhap[Ob <= threshold] = 1
                fohap[fo <= threshold] = 1
            elif compare ==">":
                obhap[Ob > threshold] = 1
                fohap[fo > threshold] = 1
            elif compare =="<":
                obhap[Ob < threshold] = 1
                fohap[fo < threshold] = 1

            hit_threshold = (obhap * fohap)
            mis_threshold = (obhap * (1 - fohap))
            fal_threshold = ((1 - obhap) * fohap)
            cn_threshold = ((1 - obhap) * (1 - fohap))
            hfmc_array[i, 0] = hit_threshold.sum()
            hfmc_array[i, 1] = fal_threshold.sum()
            hfmc_array[i, 2] = mis_threshold.sum()
            hfmc_array[i, 3] = cn_threshold.sum()
        hfmc_list.append(hfmc_array)
    hfmc_array = np.array(hfmc_list)
    shape = list(Fo_shape[:ind])
    shape.append(len(grade_list))
    shape.append(4)
    hfmc_array = hfmc_array.reshape(shape)
    return hfmc_array


def hk_yesorno(Ob,Fo,grade_list=[1e-30],compare =">=",compair = None):
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return hk_yesorno_hfmc(hfmc_array)

def hk_yesorno_hfmc(hfmc_array):
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]

    sum_hm = hit + mis
    sum_hm[sum_hm == 0] = -1
    sum_fc = fal + cn
    sum_fc[sum_fc == 0] = -1
    hk = hit/sum_hm - fal/sum_fc
    hk[sum_hm == -1] = IV
    hk[sum_fc == -1] = IV
    if hk.size ==1:
        hk = hk[0]
    return hk


def hss_yesorno(Ob,Fo,grade_list= [1e-30],compare =">=",compair = None):
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return hss_yesorno_hfmc(hfmc_array)

def hss_yesorno_hfmc(hfmc_array):
    if len(hfmc_array.shape) == 1:
        hfmc_array = hfmc_array.reshape(1,4)
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]

    sum = hit+fal +mis + cn
    correct_random = ((hit + mis) * (hit + fal) + (cn+mis)*(cn+fal))/sum
    sum_rc = sum - correct_random
    sum_rc[sum_rc == 0] = -1
    hss = (hit + cn - correct_random) / sum_rc
    hss[sum_rc ==-1] = IV
    if hss.size ==1:
        hss = hss[0]
    return hss


def odds_ratio_hfmc(hfmc_array):
    '''
    The odds ratio (or评分) gives the ratio of the odds of making a hit to the odds of making a false alarm,
    and takes prior probability into account.
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    倒数第2维或为等级维度
    :return: 0 到无穷大的实数，完美值为无穷大, 0代表没有技巧
    '''
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]
    ors = hit*cn/(mis * fal + 1e-8)
    if ors.size ==1:
        ors = ors[0]
    return ors

def odds_ratio(Ob,Fo,grade_list= [1e-30],compare =">=",compair = None):
    '''

    :param Ob:
    :param Fo:
    :param grade_list:
    :param compair:
    :return: 0 到无穷大的实数，完美值为无穷大, 0代表没有技巧
    '''

    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return odds_ratio_hfmc(hfmc_array)


def orss_hfmc(hfmc_array):
    '''
    The odds ratio (or评分) gives the ratio of the odds of making a hit to the odds of making a false alarm,
    and takes prior probability into account.
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    倒数第2维或为等级维度
    :return: 0 到无穷大的实数，完美值为无穷大, 0代表没有技巧
    '''
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]
    ors = (hit*cn -mis * fal)/ (hit*cn + mis * fal)
    if ors.size ==1:
        ors = ors[0]
    return ors

def orss(Ob,Fo,grade_list= [1e-30],compare =">=",compair = None):
    '''

    :param Ob:
    :param Fo:
    :param grade_list:
    :param compair:
    :return: -1 到1， 完美值为1
    '''
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return orss_hfmc(hfmc_array)

def fscore(Ob,Fo,grade_list = [1e-30],compare =">=",compair = None,belta = 1):
    '''
    = (1+belta^2)*(pod*sr)/(belta^2 * sr + pod)
    :param Ob:
    :param Fo:
    :param grade_list:
    :param compair:
    :param belta:
    :return:
    '''
    #precision = sr(Ob,Fo,grade_list=grade_list,compair=compare)
    #recall = pod(Ob,Fo,grade_list=grade_list,compair=compare)

    #f_score = (1 + belta * belta) * (precision * recall)/(belta * belta * precision + recall)
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array= hfmc(Ob,Fo,grade_list,compare)
    f_score = fscore_hfmc(hfmc_array,belta)

    return f_score

def fscore_hfmc(hfmc_array,belta = 1):
    #precision = sr_hfmc(hfmc_array)
    #recall = pod_hfmc(hfmc_array)

    #f_score = (1 + belta * belta) * (precision * recall) / (belta * belta * precision + recall)
    #if f_score.size ==1:
    #    f_score = f_score[0]


    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]

    sum = (1+belta*belta)*hit + belta * belta* mis + fal
    sum[sum == 0] = -1
    fscore_array =(1+belta*belta)*hit/ sum
    fscore_array[sum == -1] = IV
    if fscore_array.size ==1:
        fscore_array = fscore_array[0]

    return fscore_array

def dts(Ob,Fo,grade_list= [1e-30],compare =">=",compair = None):
    if compair is not None:
        print("warning: the argument compair will be abolished, please use compare instead\n警告：参数compair 将被废除，以后请使用参数compare代替")
        compare = compair
    hfmc_array = hfmc(Ob, Fo, grade_list,compare= compare)
    return dts_hfmc(hfmc_array)

def dts_hfmc(hfmc_array):
    if len(hfmc_array.shape) == 1:
        hfmc_array = hfmc_array.reshape(1,4)
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]

    sum1 = hit +mis + fal
    sum1[sum1 ==0] = -1
    sum2 = mis + fal + cn
    sum2[sum2 ==0] = -1

    dts_array =(hit / sum1 + cn/sum2)/2
    dts_array[sum1 ==-1] = IV
    dts_array[sum2 ==-1] = IV
    if dts_array.size ==1:
        dts_array = dts_array[0]
    return dts_array




