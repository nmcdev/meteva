import numpy as np
import copy
from meteva.base import IV



def hap_count(Ob,Fo, grade_list=[1e-30]):
    '''
    观测发生率，观测的正样本占总样本的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return:  0-1的实数，观测的正样本占总样本的比例
    '''
    result = []
    for grade in grade_list:
        result.append(Ob[Ob>grade].size)
    result = np.array(result)
    return result


def s(Ob,Fo, grade_list=[1e-30]):
    '''
    观测发生率，观测的正样本占总样本的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return:  0-1的实数，观测的正样本占总样本的比例
    '''
    result = []
    num = Ob.size
    for grade in grade_list:
        result.append(Ob[Ob>grade].size/num)
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

def r(Ob,Fo, grade_list=[1e-30]):
    '''
    预测发生率，预测的正样本占总样本的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0-1的实数，预测的正样本占总样本的比例
    '''
    hfmc_array= hfmc(Ob, Fo,grade_list)
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
    fo1 = copy.deepcopy(Fo)
    fo1[fo1 < 0.099] = 0
    shape = Ob.shape
    obhap = np.zeros(shape)
    obhap[Ob > 0] = 1
    fohap = np.zeros(shape)
    fohap[fo1 > 0] = 1
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
    return np.array([hit, fal,mis,  cn])

def pc(Ob,Fo, grade_list=[1e-30]):
    '''
    准确率，反映被正确预报的样本占比
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0-1的实数，最优值为1
    '''
    hfmc_array = hfmc(Ob,Fo,grade_list)
    return pc_hfmc(hfmc_array)

def pc_hfmc(hfmc_array):
    '''
    准确率，反映被正确预报的样本占比
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return:
    '''
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]
    accurace0 = (hit + cn) / (hit + mis + fal + cn)
    return accurace0

def pod(Ob, Fo, grade_list=[1e-30]):
    '''
    命中率，反映观测的正样本中多少被预报
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0到1的实数，完美值为1
    '''
    hfmc_array = hfmc(Ob, Fo, grade_list)
    return pod_hfmc(hfmc_array)

def pod_hfmc(hfmc_array):
    '''
    命中率，反映观测的正样本中多少被预报
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0到1的实数，完美值为1
    '''
    hit = hfmc_array[...,0]
    mis = hfmc_array[...,2]
    sum = hit + mis
    sum[sum ==0] = 1e-10
    pod0 = hit / sum
    pod0[sum<1] = IV
    return pod0

def sr(Ob, Fo, grade_list=[1e-30]):
    '''
    报中率，反映预报的正样本中实际发生的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return:0-1,最优值为1
    '''
    hfmc_array = hfmc(Ob, Fo, grade_list)
    return sr_hfmc(hfmc_array)

def sr_hfmc(hfmc_array):
    '''
    报中率，反映预报的正样本中实际发生的比例
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0-1,最优值为1
    '''
    hit = hfmc_array[..., 0]
    fal = hfmc_array[..., 1]
    sum = hit + fal
    sum[sum ==0] = 1e-10
    sr0 = hit / sum
    sr0[sum < 1] = IV
    return sr0

def far(Ob, Fo, grade_list=[1e-30]):
    '''
    空报率, 反映预报的正样本中多少未发生
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0到1的实数，最优值为0
    '''
    hfmc_array = hfmc(Ob, Fo, grade_list)
    return far_hfmc(hfmc_array)

def far_hfmc(hfmc_array):
    '''
    空报率, 反映预报的正样本中多少实况未发生
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0到1的实数，最优值为0
    '''
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    sum = hit + fal
    sum[sum == 0] = 1e-10
    far0 = fal / sum
    far0[sum < 1] = IV
    return far0

def pofd(Ob,Fo,grade_list=[1e-30]):
    '''
    报空率, 事件未发生样本被预报为会发生的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0到1的实数，最优值为0
    '''
    hfmc_array = hfmc(Ob,Fo,grade_list)
    return pofd_hfmc(hfmc_array)

def pofd_hfmc(hfmc_array):
    '''
    报空率,事件未发生样本被预报为会发生的比例
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0到1的实数，最优值为0
    '''
    cn = hfmc_array[...,3]
    fal = hfmc_array[...,1]
    sum = cn +fal
    sum[sum == 0] = 1e-10
    podf0 = fal / sum
    podf0[sum < 1] = IV
    return podf0

def mr(Ob, Fo, grade_list=[1e-30]):
    '''
    漏报率，观测的正样本被漏报的比例
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0到1的实数，最优值为0
    '''
    hfmc_array = hfmc(Ob, Fo, grade_list)
    return mr_hfmc(hfmc_array)

def mr_hfmc(hfmc_array):
    '''
    漏报率，观测的正样本被漏报的比例
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0到1的实数，最优值为0
    '''

    hit = hfmc_array[...,0]
    mis = hfmc_array[...,2]
    sum = hit + mis
    sum[sum ==0]= 1e-10
    mr0 = mis / sum
    mr0[sum < 1] = IV
    return mr0

def bias(Ob, Fo, grade_list=[1e-30]):
    '''
    样本偏差，预报的正样本数 和 观测的正样本数的比值
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0到正无穷的实数，完美值为1
    '''
    hfmc_array = hfmc(Ob, Fo, grade_list)
    return bias_hfmc(hfmc_array)

def bias_hfmc(hfmc_array):
    '''
    样本偏差
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    :return: 0到正无穷的实数，完美值为1
    '''
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    sum = hit +mis
    sum[sum==0] = 1e-10
    bias0 = (hit + fal) / sum
    delta = fal - mis
    bias0[delta ==0] = 1
    bias0[bias0 > 1e9] = IV
    return bias0

def bias_extend_linear(bias_array):
    '''

    :param bias_array:
    :return:
    '''
    bias_extend0 = np.abs(bias_array - 1)
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


def ts(Ob, Fo, grade_list=[1e-30]):
    '''
    ts评分
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: 0-1的实数，0代表没有技巧，完美值为1
    '''
    hfmc_array =hfmc(Ob, Fo, grade_list)
    return ts_hfmc(hfmc_array)

def ts_hfmc(hfmc_array):
    '''
    ts评分
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    倒数第2维或为等级维度
    :return: 0-1的实数，0代表没有技巧，完美值为1
    '''
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    sum = hit +mis + fal
    sum[sum ==0] = 1e-10
    ts_array =hit / sum
    return ts_array

def ets(Ob, Fo, grade_list=[1e-30]):
    '''
    ets评分
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: -1/3 到1 的实数，完美值为1, 0代表没有技巧
    '''
    hfmc_array = hfmc(Ob, Fo, grade_list)
    return ets_hfmc(hfmc_array)

def ets_hfmc(hfmc_array):
    '''
    ets评分
    :param hfmc_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（命中数，空报数，漏报数，正确否定数）
    倒数第2维或为等级维度
    :return: -1/3 到1 的实数，完美值为1, 0代表没有技巧
    '''
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]

    total = hit + mis + fal + cn
    hit_random = (hit + mis) * (hit + fal) / total
    sum = hit + mis + fal - hit_random
    sum[sum == 0] = 1e-10
    ets_array = (hit - hit_random) / sum
    return ets_array

def hfmc(Ob, Fo, grade_list=[1e-30]):
    '''
    预报列联表
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :param grade_list: 多个阈值同时检验时的等级参数
    :return: python numpy数组，其中最后一维长度为4，分别记录了（命中数，漏报数，空报数，正确否定数）
    '''
    hfmc_array = np.zeros((len(grade_list),4))
    for i in range(len(grade_list)):
        threshold = grade_list[i]
        num = np.size(Ob)
        obhap = np.zeros_like(Ob)
        obhap[Ob >= threshold] = 1
        fohap = np.zeros_like(Fo)
        fohap[Fo >= threshold] = 1
        hit_threshold = (obhap * fohap)
        mis_threshold = (obhap * (1 - fohap))
        fal_threshold = ((1 - obhap) * fohap)
        cn_threshold = ((1 - obhap) * (1 - fohap))
        hfmc_array[i, 0] = hit_threshold.sum()
        hfmc_array[i, 1] = fal_threshold.sum()
        hfmc_array[i, 2] = mis_threshold.sum()
        hfmc_array[i, 3] = cn_threshold.sum()
    return hfmc_array




def hk_yesorno(Ob,Fo,grade_list=[1e-30]):
    hfmc_array = hfmc(Ob, Fo, grade_list)
    return hk_yesorno_hfmc(hfmc_array)

def hk_yesorno_hfmc(hfmc_array):
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]

    sum_hm = hit + mis
    sum_hm[sum_hm == 0] = 1e-10
    sum_fc = fal + cn
    sum_fc[sum_fc == 0] = 1e-10
    hk = hit/sum_hm - fal/sum_fc
    return hk


def hss_yesorno(Ob,Fo,grade_list= [1e-30]):
    hfmc_array = hfmc(Ob, Fo, grade_list)
    return hss_yesorno_hfmc(hfmc_array)

def hss_yesorno_hfmc(hfmc_array):
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]

    sum = hit+fal +mis + cn
    correct_random = ((hit + mis) * (hit + fal) + (cn+mis)*(cn+fal))/sum
    sum_rc = sum - correct_random
    sum_rc[sum_rc == 0] = 1e-10
    hss = (hit + cn - correct_random) / sum_rc

    return hss

def dts(Ob,Fo,grade_list= [1e-30]):
    hfmc_array = hfmc(Ob, Fo, grade_list)
    return dts_hfmc(hfmc_array)

def dts_hfmc(hfmc_array):
    hit = hfmc_array[...,0]
    fal = hfmc_array[...,1]
    mis = hfmc_array[...,2]
    cn = hfmc_array[...,3]

    sum1 = hit +mis + fal
    sum1[sum1 ==0] = 1e-10
    sum2 = mis + fal + cn
    sum2[sum2 ==0] = 1e-10

    dts_array =(hit / sum1 + cn/sum2)/2

    return dts_array



def FSS_time(Ob,Fo,grade_list = [1e-30],window_size = None):
    '''
    :param Ob: 二维numpy数组Ob[i,j]，其中i取值为0  - 站点数， j为取值为0 - 时效维度的size
    :param Fo: 二维numpy数组Fo[i,j]，其中i取值为0  - 站点数， j为取值为0 - 时效维度的size
    :param window_size:
    :param grade_list:
    :return:
    '''
    mid_array = mid_FSS_time(Ob,Fo,grade_list,window_size)
    result = FSS_time_base_on_mid(mid_array)
    return result

def FSS_time_base_on_mid(mid_array):
    '''

    :param mid_array:
    :return:
    '''
    result = 1 - mid_array[...,0]/(mid_array[...,1]+1e-30)
    return result

def merge_mid_FSS_time(mid_array1,mid_array2):
    '''

    :param mid_array1:
    :param mid_array2:
    :return:
    '''
    if mid_array1 is None:
        return mid_array2
    if mid_array2 is None:
        return mid_array1
    return mid_array1 + mid_array2

def mid_FSS_time(Ob,Fo,grade_list = [1e-30],window_size = None):
    '''
    :param Ob: 二维numpy数组Ob[i,j]，其中i取值为0  - 站点数， j为取值为0 - 时效维度的size
    :param Fo: 二维numpy数组Fo[i,j]，其中i取值为0  - 站点数， j为取值为0 - 时效维度的size
    :param window_size:
    :param grade_list:
    :return:
    '''
    shape = Ob.shape
    if len(shape) == 1:
        Ob = Ob.reshape(1,shape[0])
        Fo = Fo.reshape(1,shape[0])
        shape = Ob.shape
    if window_size is None:
        window_size = shape[1]//3
    left_size = shape[1] - window_size
    ng = len(grade_list)
    result = np.zeros((ng,window_size,left_size,2))
    for i in range(1,1+window_size):
        for j in range(left_size):
            for g in range(ng):
                ob1 = np.zeros((shape[0],i))
                fo1 = np.zeros((shape[0],i))
                ob1[Ob[:, j + window_size -i:j+window_size] >= grade_list] = 1
                fo1[Fo[:, j + window_size -i:j+window_size] >= grade_list] = 1
                ob_hap_p =np.sum(ob1,axis=1)
                fo_hap_p =np.sum(fo1,axis=1)
                result[g,i - 1, j,  0] = np.sum(np.power(ob_hap_p - fo_hap_p, 2))
                result[g,i - 1, j,  1] = np.sum(np.power(ob_hap_p, 2)) + np.sum(np.power(fo_hap_p, 2))
    return result