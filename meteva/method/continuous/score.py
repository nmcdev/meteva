import numpy as np

import meteva.base
from meteva.base.tool.math_tools import sxy_iteration,ss_iteration
from meteva.base import IV
def sample_count(Ob, Fo=None):
    '''
    计算检验的样本数
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 整数，Ob.size
    '''
    return Ob.size


def ob_fo_sum(ob,fo):
    Fo_shape = fo.shape
    Ob_shape = ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return

    if len(fo.shape) == len(ob.shape):
        result = [np.sum(ob),np.sum(fo)]
    else:
        result = [np.sum(ob)]
        for i in range(Fo_shape[0]):
            result.append(np.sum(fo[i,:]))
    result = np.array(result)
    return result

def ob_fo_mean(ob,fo):

    Fo_shape = fo.shape
    Ob_shape = ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return

    if len(fo.shape) == len(ob.shape):
        result = [np.mean(ob),np.mean(fo)]
    else:
        result = [np.mean(ob)]
        for i in range(Fo_shape[0]):
            result.append(np.mean(fo[i,:]))
    result = np.array(result)
    return result


def ob_quantile(ob,fo,grade_list=[0.5]):
    '''
    统计观测数据的百分位
    :param ob:
    :param fo:
    :param grade_list:
    :return:
    '''
    ob1 = np.sort(ob)
    ob1 = ob1.flatten()
    ob1.sort()
    n = len(ob1)
    qu_list = []
    for i in range(len(grade_list)):
        m = int(n * grade_list[i])
        qu_list.append(ob1[m])
    if len(qu_list) ==1:
        return qu_list[0]
    else:
        return np.array(qu_list)

def ob_fo_quantile(ob,fo,grade_list=[0.5]):
    '''
    统计观测数据的百分位
    :param ob:
    :param fo:
    :param grade_list:
    :return:
    '''


    Fo_shape = fo.shape
    Ob_shape = ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])

    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    if len(fo.shape) == len(ob.shape):
        ob1 = np.sort(ob)
        ob1 = ob1.flatten()
        ob1.sort()
        n = len(ob1)
        qu_list_ob = []
        for i in range(len(grade_list)):
            m = int(n * grade_list[i])
            qu_list_ob.append([ob1[m]])

        fo1 = np.sort(fo)
        fo1 = fo1.flatten()
        fo1.sort()
        qu_list_fo = []
        for i in range(len(grade_list)):
            m = int(n * grade_list[i])
            qu_list_fo.append([fo1[m]])

        qu_list = [qu_list_ob,qu_list_fo]
    else:
        ob1 = np.sort(ob)
        ob1 = ob1.flatten()
        ob1.sort()
        n = len(ob1)
        qu_list_ob = []
        for i in range(len(grade_list)):
            m = int(n * grade_list[i])
            qu_list_ob.append([ob1[m]])

        qu_list = [qu_list_ob]
        for k in range(Fo_shape[0]):
            fo1 = np.sort(fo[k,:])
            fo1 = fo1.flatten()
            fo1.sort()
            qu_list_fo = []
            for i in range(len(grade_list)):
                m = int(n * grade_list[i])
                qu_list_fo.append([fo1[m]])
            qu_list.append(qu_list_fo)

    result = np.array(qu_list).squeeze()
    return result



def ob_fo_min(ob,fo,count = 1):
    if count ==1:
        Fo_shape = fo.shape
        Ob_shape = ob.shape

        Ob_shpe_list = list(Ob_shape)
        size = len(Ob_shpe_list)
        ind = -size
        Fo_Ob_index = list(Fo_shape[ind:])
        if Fo_Ob_index != Ob_shpe_list:
            print('预报数据和观测数据维度不匹配')
            return

        if len(fo.shape) == len(ob.shape):
            result = [np.min(ob),np.min(fo)]
        else:
            result = [np.min(ob)]
            for i in range(Fo_shape[0]):
                result.append(np.min(fo[i,:]))
        result = np.array(result)
        return result
    elif count < 1:
        print('para count must be int >=1')
    else:
        Fo_shape = fo.shape
        Ob_shape = ob.shape

        Ob_shpe_list = list(Ob_shape)
        size = len(Ob_shpe_list)
        ind = -size
        Fo_Ob_index = list(Fo_shape[ind:])
        if Fo_Ob_index != Ob_shpe_list:
            print('预报数据和观测数据维度不匹配')
            return
        ob_f = ob.flatten()
        index = ob_f.argsort()[:count]
        ob_mins = ob_f[index]
        result = [ob_mins]
        if len(fo.shape) == len(ob.shape):
            fo_f = fo.flatten()
            index = fo_f.argsort()[:count]
            fo_maxs = fo_f[index]
            result.append(fo_maxs)
        else:
            for i in range(Fo_shape[0]):
                v1 = fo[i, :].flatten()
                index = v1.argsort()[:count]
                fo_maxs = v1[index]
                result.append(fo_maxs)
        result = np.array(result)
        return result

def ob_fo_max(ob,fo, count = 1):
    if count == 1:
        Fo_shape = fo.shape
        Ob_shape = ob.shape

        Ob_shpe_list = list(Ob_shape)
        size = len(Ob_shpe_list)
        ind = -size
        Fo_Ob_index = list(Fo_shape[ind:])
        if Fo_Ob_index != Ob_shpe_list:
            print('预报数据和观测数据维度不匹配')
            return

        if len(fo.shape) == len(ob.shape):
            result = [np.max(ob),np.max(fo)]
        else:
            result = [np.max(ob)]
            for i in range(Fo_shape[0]):
                result.append(np.max(fo[i,:]))
        result = np.array(result)
        return result
    elif count < 1:
        print('para count must be int >=1')
    else:
        Fo_shape = fo.shape
        Ob_shape = ob.shape

        Ob_shpe_list = list(Ob_shape)
        size = len(Ob_shpe_list)
        ind = -size
        Fo_Ob_index = list(Fo_shape[ind:])
        if Fo_Ob_index != Ob_shpe_list:
            print('预报数据和观测数据维度不匹配')
            return
        ob_f = ob.flatten()
        index = ob_f.argsort()[-count:][::-1]
        ob_maxs = ob_f[index]
        result = [ob_maxs]
        if len(fo.shape) == len(ob.shape):
            fo_f = fo.flatten()
            index = fo_f.argsort()[-count:][::-1]
            fo_maxs = fo_f[index]
            result.append(fo_maxs)
        else:
            for i in range(Fo_shape[0]):
                v1 = fo[i, :].flatten()
                index = v1.argsort()[-count:][::-1]
                fo_maxs = v1[index]
                result.append(fo_maxs)
        result = np.array(result)
        return result

def ob_fo_std(ob,fo):
    Fo_shape = fo.shape
    Ob_shape = ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return

    if len(fo.shape) == len(ob.shape):
        result = [np.std(ob),np.std(fo)]
    else:
        result = [np.std(ob)]
        for i in range(Fo_shape[0]):
            result.append(np.std(fo[i,:]))
    result = np.array(result)
    return result

def ob_fo_cv(ob,fo):
    '''
    观测和预报的离差
    :param ob:
    :param fo:
    :return:
    '''
    Fo_shape = fo.shape
    Ob_shape = ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return

    if len(fo.shape) == len(ob.shape):
        result = [np.std(ob)/np.mean(ob),np.std(fo)/np.mean(fo)]
    else:
        result = [np.std(ob)/np.mean(ob)]
        for i in range(Fo_shape[0]):
            result.append(np.std(fo[i,:])/np.mean(fo[i,:]))
    result = np.array(result)
    return result


def cscs(Ob,Fo):
    '''
       :param ob: 观测降水序列
       :param fo: 预报降水序列
       :return: 观测和预报各自的平均降水强度计算相关的中间量
       '''
    cscs_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    ob_not_0 = Ob[Ob >= 0.1]
    cob = ob_not_0.size
    sob = np.sum(ob_not_0)

    for line in range(new_Fo_shape[0]):
        foi = new_Fo[line, :]
        fo_not_0 = foi[foi >= 0.1]
        cfo = fo_not_0.size
        sfo = np.sum(fo_not_0)
        cscs_list.append(np.array([cob,sob, cfo,sfo]))

    cscs_np = np.array(cscs_list)
    shape = list(Fo_shape[:ind])
    shape.append(4)

    cscs_array =cscs_np.reshape(shape)
    return cscs_array

def ob_fo_precipitation_strength_cscs(cscs_array):

    if len(cscs_array.shape) == 1:
        cscs_array = cscs_array.reshape(1,1, 4)
    cob = cscs_array[..., 0]
    sob = cscs_array[..., 1]
    cfo = cscs_array[..., 2]
    sfo = cscs_array[..., 3]

    sob[cob==0] = IV
    cob[cob == 0] = 1
    sfo[cfo == 0] =IV
    cfo[cfo == 0] = 1

    shape1 = list(cscs_array.shape)
    if len(cscs_array.shape) == 2:
        result = np.zeros((2, shape1[0]))
        result[0, :] = sob / cob
        result[1, :] = sfo / cfo
    else:
        result = np.zeros((1 + shape1[0], shape1[1]))
        result[0, :] = sob / cob
        result[1, :] = sfo / cfo

    return result


def ob_fo_precipitation_strength(ob,fo):
    '''
    :param ob: 观测降水序列
    :param fo: 预报降水序列
    :return: 观测和预报各自的平均降水强度，平均降水强度等于降水量大于等于0.1mm的站次的降水的平均值
    '''
    Fo_shape = fo.shape
    Ob_shape = ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return

    ob_not_0 = ob[ob >= 0.1]
    result = [np.mean(ob_not_0)]
    if len(fo.shape) == len(ob.shape):
        fo_not_0 = fo[fo>=0.1]
        result.append(np.mean(fo_not_0))
    else:
        for i in range(Fo_shape[0]):
            foi= fo[i,:]
            fo_not_0 = foi[foi >= 0.1]
            result.append(np.mean(fo_not_0))
    result = np.array(result)
    return result


def ob_fo_precipitation_strenght(ob,fo):
    result = ob_fo_precipitation_strength(ob,fo)
    return result



def ob_mean(Ob, Fo=None):
    '''
    计算观测样本的平均
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: None或任意数据，它的存在是为了使得参数规范化，方便更高级的封装
    :return: 实数
    '''
    return np.mean(Ob)


def fo_mean(Ob, Fo):
    '''
    计算观测样本的平均
    -----------------------------
    :param Ob: None或任意数据，它的存在是为了使得参数规范化，方便更高级的封装
    :param Fo: 预报数据  任意维numpy数组
    :return: 实数
    '''
    Fo_mean_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    if len(Fo_shape)> len(Ob_shape):
        Ob_shpe_list.insert(0, -1)
        new_Fo_shape = tuple(Ob_shpe_list)
        new_Fo = Fo.reshape(new_Fo_shape)
        new_Fo_shape = new_Fo.shape
        for line in range(new_Fo_shape[0]):
            Fo_mean = np.mean(new_Fo[line, :])
            Fo_mean_list.append(Fo_mean)
        Fo_mean_array = np.array(Fo_mean_list)
        shape = list(Fo_shape[:ind])
        Fo_mean_array = Fo_mean_array.reshape(shape)
    else:
        Fo_mean_array = np.mean(Fo)
    return Fo_mean_array


def tc_count(Ob, Fo, grade_list = [2]):
    '''
    计算准确率的中间结果
    :param Ob:
    :param Fo:
    :param threshold:
    :return:
    '''
    if not isinstance(grade_list,list):
        grade_list = [grade_list]
    correct_rate_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    for line in range(new_Fo_shape[0]):
        total_count = Ob.size
        error = np.abs(new_Fo[line, :] - Ob)
        count_list = [total_count]
        for grade in grade_list:
            index = np.where(error <= grade)
            count_list.append(len(index[0]))
        correct_rate_list.append(count_list)
    correct_rate_np = np.array(correct_rate_list)
    shape = list(Fo_shape[:ind])
    shape.append(1 + len(grade_list))
    correct_rate_array = correct_rate_np.reshape(shape)
    return correct_rate_array


def correct_rate(Ob, Fo, grade_list = [2]):
    '''
    计算准确率
    :param Ob:
    :param Fo:
    :param threshold:
    :return:
    '''

    tc_array = tc_count(Ob, Fo, grade_list)
    crate = correct_rate_tc(tc_array)
    return crate

def wrong_rate(Ob,Fo,grade_list = [2],unit = 1):
    '''
    计算错误率
    :param Ob:
    :param Fo:
    :param threshold:
    :return:
    '''

    tc_array = tc_count(Ob, Fo, grade_list)
    wrate = wrong_rate_tc(tc_array,unit = unit)

    return wrate


def wrong_rate_tc(tc_count_array,unit = 1):
    '''
    计算错误率
    :param Ob:
    :param Fo:
    :param threshold:
    :return:
    '''
    crate = correct_rate_tc(tc_count_array)
    wrate = 1-crate
    if unit =="%":
        wrate *=100
    return wrate

def correct_rate_tc(tc_count_array):
    '''
    :param tc_count_array:
    :return:
    '''
    if tc_count_array.shape[-1] > 2:
        total_count =  tc_count_array[..., 0]
        total_count = total_count.reshape((-1,1))
        cr1 = tc_count_array[..., 1:] / total_count
    else:
        cr1 = tc_count_array[..., 1] / tc_count_array[..., 0]

    return cr1


def tlfo(Ob,Fo):

    '''
    计算RMSF的中间结果
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 一维numpy数组，其内容依次为总样本数、log(fo/ob)^2 的总和
    '''

    tlfo_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    for line in range(new_Fo_shape[0]):
        fo_ob = np.array([new_Fo[line, :],Ob])
        min_ob_fo = np.min(fo_ob,axis=0)
        max_ob_fo = np.max(fo_ob,axis=0)
        index = np.where((min_ob_fo>=0.1)|(max_ob_fo>=1.0))
        ob_s = Ob[index]
        fo_s = new_Fo[line,:][index]
        ob_s[ob_s<0.1] = 0.1
        fo_s[fo_s<0.1] = 0.1
        total_count = ob_s.size
        e_sum = np.sum(np.power(np.log(fo_s/ob_s),2))
        tlfo_list.append(np.array([total_count, e_sum]))
    tlfo_np = np.array(tlfo_list)
    shape = list(Fo_shape[:ind])
    shape.append(2)

    tlfo_array = tlfo_np.reshape(shape)
    return tlfo_array

def rmsf(Ob,Fo):
    '''

    :param Ob:
    :param Fo:
    :return:
    '''
    tlfo_array = tlfo(Ob,Fo)
    return rmsf_tlfo(tlfo_array)

def rmsf_tlfo(tlfo_array):
    mean_log2 = tlfo_array[..., 1] / tlfo_array[..., 0]
    rmsf = np.exp(np.sqrt(mean_log2))
    return rmsf


def tase(Ob, Fo,weight = None):
    '''
    计算平均误差、平均绝对误差、均方误差、均方根误差的中间结果
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 一维numpy数组，其内容依次为总样本数、误差总和、绝对误差总和、误差平方总和
    '''

    tase_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    if weight is None:
        for line in range(new_Fo_shape[0]):
            total_count = Ob.size
            e_sum = np.sum(new_Fo[line, :] - Ob)
            ae_sum = np.sum(np.abs(new_Fo[line, :] - Ob))
            se_sum = np.sum(np.square(new_Fo[line, :] - Ob))
            tase_list.append(np.array([total_count, e_sum, ae_sum, se_sum]))
    else:
        for line in range(new_Fo_shape[0]):
            total_count = np.sum(weight)
            e_sum = np.sum((new_Fo[line, :] - Ob) * weight)
            ae_sum = np.sum(np.abs(new_Fo[line, :] - Ob) * weight)
            se_sum = np.sum(np.square(new_Fo[line, :] - Ob)*weight)
            tase_list.append(np.array([total_count, e_sum, ae_sum, se_sum]))

    tase_np = np.array(tase_list)
    shape = list(Fo_shape[:ind])
    shape.append(4)
    tase_array = tase_np.reshape(shape)
    return tase_array



def tasem(Ob, Fo,weight = None):
    '''
    计算平均误差、平均绝对误差、均方误差、均方根误差的中间结果
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 一维numpy数组，其内容依次为总样本数、误差总和、绝对误差总和、误差平方总和
    '''

    tase_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    if weight is None:
        for line in range(new_Fo_shape[0]):
            total_count = Ob.size
            e_sum = np.sum(new_Fo[line, :] - Ob)
            ae_sum = np.sum(np.abs(new_Fo[line, :] - Ob))
            se_sum = np.sum(np.square(new_Fo[line, :] - Ob))
            ob_sum = np.sum(Ob)
            tase_list.append(np.array([total_count, e_sum, ae_sum, se_sum,ob_sum]))
    else:
        for line in range(new_Fo_shape[0]):
            total_count = np.sum(weight)
            e_sum = np.sum((new_Fo[line, :] - Ob) * weight)
            ae_sum = np.sum(np.abs(new_Fo[line, :] - Ob) * weight)
            se_sum = np.sum(np.square(new_Fo[line, :] - Ob)*weight)
            ob_sum = np.sum( Ob* weight)
            tase_list.append(np.array([total_count, e_sum, ae_sum, se_sum,ob_sum]))

    tase_np = np.array(tase_list)
    shape = list(Fo_shape[:ind])
    shape.append(5)
    tasem_array = tase_np.reshape(shape)
    return tasem_array

def max_error(Ob,Fo):
    me_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    if len(Fo_shape)> len(Ob_shape):
        Ob_shpe_list.insert(0, -1)
        new_Fo_shape = tuple(Ob_shpe_list)
        new_Fo = Fo.reshape(new_Fo_shape)
        new_Fo_shape = new_Fo.shape
        for line in range(new_Fo_shape[0]):
            error = np.max(new_Fo[line, :] - Ob)
            me_list.append(error)
        error_array = np.array(me_list)
        shape = list(Fo_shape[:ind])
        error_array = error_array.reshape(shape)
    else:
        error_array  = np.max(Fo - Ob)
    return error_array

def min_error(Ob,Fo):
    me_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    if len(Fo_shape)> len(Ob_shape):
        Ob_shpe_list.insert(0, -1)
        new_Fo_shape = tuple(Ob_shpe_list)
        new_Fo = Fo.reshape(new_Fo_shape)
        new_Fo_shape = new_Fo.shape
        for line in range(new_Fo_shape[0]):
            error = np.min(new_Fo[line, :] - Ob)
            me_list.append(error)
        error_array = np.array(me_list)
        shape = list(Fo_shape[:ind])
        error_array = error_array.reshape(shape)
    else:
        error_array  = np.min(Fo - Ob)
    return error_array


def max_abs_error(Ob,Fo):
    me_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    if len(Fo_shape)> len(Ob_shape):
        Ob_shpe_list.insert(0, -1)
        new_Fo_shape = tuple(Ob_shpe_list)
        new_Fo = Fo.reshape(new_Fo_shape)
        new_Fo_shape = new_Fo.shape
        for line in range(new_Fo_shape[0]):
            error = np.max(np.abs(new_Fo[line, :] - Ob))
            me_list.append(error)
        error_array = np.array(me_list)
        shape = list(Fo_shape[:ind])
        error_array = error_array.reshape(shape)
    else:
        error_array  = np.max(np.abs(Fo - Ob))
    return error_array


def me(Ob, Fo,weight = None):
    '''
    me 求两组数据的误差平均值
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 负无穷到正无穷的实数，最优值为0
    '''

    if weight is None:
        me_list = []
        Fo_shape = Fo.shape
        Ob_shape = Ob.shape

        Ob_shpe_list = list(Ob_shape)
        size = len(Ob_shpe_list)
        ind = -size
        Fo_Ob_index = list(Fo_shape[ind:])
        if Fo_Ob_index != Ob_shpe_list:
            print('预报数据和观测数据维度不匹配')
            return
        if len(Fo_shape)> len(Ob_shape):
            Ob_shpe_list.insert(0, -1)
            new_Fo_shape = tuple(Ob_shpe_list)
            new_Fo = Fo.reshape(new_Fo_shape)
            new_Fo_shape = new_Fo.shape
            for line in range(new_Fo_shape[0]):
                mean_error = np.mean(new_Fo[line, :] - Ob)
                me_list.append(mean_error)
            mean_error_array = np.array(me_list)
            shape = list(Fo_shape[:ind])
            mean_error_array = mean_error_array.reshape(shape)
        else:
            mean_error_array  = np.mean(Fo - Ob)
    else:
        tase_array = tase(Ob,Fo,weight)
        mean_error_array = me_tase(tase_array)

    return mean_error_array


def me_tase(tase_array):
    '''
    me 求两组数据的误差平均值
    :param tase_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（total_count,e_sum,ae_sum,se_sum）
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 负无穷到正无穷的实数，最优值为0
    '''
    mean_error = tase_array[..., 1] / tase_array[..., 0]
    return mean_error


def mae(Ob, Fo,weight = None):
    '''
    me 求两组数据的误差平均值
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 负无穷到正无穷的实数，最优值为0
    '''
    if weight is None:
        mae_list = []
        Fo_shape = Fo.shape
        Ob_shape = Ob.shape

        Ob_shpe_list = list(Ob_shape)
        size = len(Ob_shpe_list)
        ind = -size
        Fo_Ob_index = list(Fo_shape[ind:])
        if Fo_Ob_index != Ob_shpe_list:
            print('预报数据和观测数据维度不匹配')
            return
        if len(Fo_shape) == len(Ob_shape):
            mean_abs_error = np.mean(np.abs(Fo - Ob))
            return mean_abs_error
        else:
            Ob_shpe_list.insert(0, -1)
            new_Fo_shape = tuple(Ob_shpe_list)
            new_Fo = Fo.reshape(new_Fo_shape)
            new_Fo_shape = new_Fo.shape
            for line in range(new_Fo_shape[0]):
                mean_abs_error = np.mean(np.abs(new_Fo[line, :] - Ob))
                mae_list.append(mean_abs_error)
            mean_error_array = np.array(mae_list)
            shape = list(Fo_shape[:ind])
            mean_abs_error_array = mean_error_array.reshape(shape)
            return mean_abs_error_array
    else:
        tase_array = tase(Ob, Fo, weight)
        mean_abs_error_array = mae_tase(tase_array)

        return mean_abs_error_array


def mae_tase(tase_array):
    '''
    mean_abs_error,求两组数据的平均绝对误差
    :param tase_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（total_count,e_sum,ae_sum,se_sum）
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到无穷大，最优值为0
    '''
    mean_abs_error = tase_array[..., 2] / tase_array[..., 0]
    return mean_abs_error


def mse(Ob, Fo,weight = None):
    '''
    mean_sqrt_error, 求两组数据的均方误差
    ----------------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 0到无穷大，最优值为0
    '''
    if weight is None:
        mse_list = []
        Fo_shape = Fo.shape
        Ob_shape = Ob.shape

        Ob_shpe_list = list(Ob_shape)
        size = len(Ob_shpe_list)
        ind = -size
        Fo_Ob_index = list(Fo_shape[ind:])
        if Fo_Ob_index != Ob_shpe_list:
            print('预报数据和观测数据维度不匹配')
            return
        if len(Fo_shape) == len(Ob_shape):
            mean_square_error = np.mean(np.square(Fo - Ob))
            return mean_square_error
        else:
            Ob_shpe_list.insert(0, -1)
            new_Fo_shape = tuple(Ob_shpe_list)
            new_Fo = Fo.reshape(new_Fo_shape)
            new_Fo_shape = new_Fo.shape
            for line in range(new_Fo_shape[0]):
                mean_square_error = np.mean(np.square(new_Fo[line, :] - Ob))
                mse_list.append(mean_square_error)
            mean_sqrt_array = np.array(mse_list)
            shape = list(Fo_shape[:ind])
            mean_sqrt_error_array = mean_sqrt_array.reshape(shape)
            return mean_sqrt_error_array
    else:
        tase_array = tase(Ob, Fo, weight)
        mean_squre_error = mse_tase(tase_array)

        return mean_squre_error

def mse_tase(tase_array):
    '''
    mse 求两组数据的均方误差
    :param tase_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（total_count,e_sum,ae_sum,se_sum）
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到无穷大，最优值为0
    '''
    mean_squre_error = tase_array[..., 3] / tase_array[..., 0]
    return mean_squre_error


def rmse(Ob, Fo,weight = None):
    '''
    root_mean_square_error 求两组数据的均方根误差
    ------------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 0到无穷大，最优值为0
    '''
    if weight is None:
        rmse_list = []
        Fo_shape = Fo.shape
        Ob_shape = Ob.shape

        Ob_shpe_list = list(Ob_shape)
        size = len(Ob_shpe_list)
        ind = -size
        Fo_Ob_index = list(Fo_shape[ind:])
        if Fo_Ob_index != Ob_shpe_list:
            print('预报数据和观测数据维度不匹配')
            return
        if len(Fo_shape) == len(Ob_shape):
            mean_square_error = np.sqrt(np.mean(np.square(Fo - Ob)))
            return mean_square_error
        else:
            Ob_shpe_list.insert(0, -1)
            new_Fo_shape = tuple(Ob_shpe_list)
            new_Fo = Fo.reshape(new_Fo_shape)
            new_Fo_shape = new_Fo.shape
            for line in range(new_Fo_shape[0]):
                root_mean_sqrt_error = np.sqrt(np.mean(np.square(new_Fo[line, :] - Ob)))
                rmse_list.append(root_mean_sqrt_error)
            root_mean_sqrt_array = np.array(rmse_list)
            shape = list(Fo_shape[:ind])
            root_mean_sqrt_error_array = root_mean_sqrt_array.reshape(shape)
            return root_mean_sqrt_error_array
    else:
        tase_array = tase(Ob, Fo, weight)
        root_mean_sqrt_error = rmse_tase(tase_array)

        return root_mean_sqrt_error

def rmse_tase(tase_array):
    '''
    mse 求两组数据的均方根误差
    :param tase_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（total_count,e_sum,ae_sum,se_sum）
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到无穷大，最优值为0
    '''
    root_mean_sqrt_error = np.sqrt(tase_array[..., 3] / tase_array[..., 0])
    return root_mean_sqrt_error

def si(Ob,Fo):
    '''

    :param Ob:
    :param Fo:
    :return: 均方根误差/观测平均
    '''
    si_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    mean_ob = np.mean(Ob)
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    if len(Fo_shape) == len(Ob_shape):
        root_mean_sqrt_error = np.sqrt(np.mean(np.square(Fo - Ob)))

        si = root_mean_sqrt_error/mean_ob
        return si
    else:
        Ob_shpe_list.insert(0, -1)
        new_Fo_shape = tuple(Ob_shpe_list)
        new_Fo = Fo.reshape(new_Fo_shape)
        new_Fo_shape = new_Fo.shape
        for line in range(new_Fo_shape[0]):
            root_mean_sqrt_error = np.sqrt(np.mean(np.square(new_Fo[line, :] - Ob)))
            si = root_mean_sqrt_error/mean_ob
            si_list.append(si)
        si_array = np.array(si_list)
        shape = list(Fo_shape[:ind])
        si_array = si_array.reshape(shape)
        return si_array


def bias_m(Ob, Fo):
    '''
    均值偏差 求预测数据和实况数据的平均值的比
    ------------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return:  0到正无穷，最优值为1
    '''
    mean_ob = np.mean(Ob)
    if mean_ob == 0:
        bias0 = IV
    else:
        bias_m_list = []
        Fo_shape = Fo.shape
        Ob_shape = Ob.shape

        Ob_shpe_list = list(Ob_shape)
        size = len(Ob_shpe_list)
        ind = -size
        Fo_Ob_index = list(Fo_shape[ind:])
        if Fo_Ob_index != Ob_shpe_list:
            print('预报数据和观测数据维度不匹配')
            return
        if len(Fo_shape) == len(Ob_shape):
            bias0 = np.mean(Fo) / mean_ob
        else:
            Ob_shpe_list.insert(0, -1)
            new_Fo_shape = tuple(Ob_shpe_list)
            new_Fo = Fo.reshape(new_Fo_shape)
            new_Fo_shape = new_Fo.shape
            for line in range(new_Fo_shape[0]):
                bias_piece = np.mean(new_Fo[line, :]) / mean_ob
                bias_m_list.append(bias_piece)
            bias_m_np = np.array(bias_m_list)
            shape = list(Fo_shape[:ind])
            bias0 = bias_m_np.reshape(shape)
    return bias0

def bias_tmmsss(tmmsss_array):
    '''
    均值偏差 求预测数据和实况数据的平均值的比
    :param tmmsss_array: 包含命中空报和漏报的多维数组，其中最后一维长度为6，分别记录了（count,mx,my,sxx,syy,sxy）
    :return:
    '''
    mean_ob = tmmsss_array[..., 1] + 0
    mean_fo = tmmsss_array[..., 2]
    if mean_ob.size == 1:
        if mean_ob == 0:
            bias0 = IV
        else:
            bias0 = mean_fo / mean_ob
    else:
        mean_ob[mean_ob == 0] = IV
        bias0 = mean_ob / mean_fo
        bias0[mean_ob == IV] = IV
    return bias0


def corr(Ob, Fo,weight = None):
    '''
    相关系数，求实况数据还和预测数据之间的相关系数
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: corr0
    '''
    tmmsss_array = tmmsss(Ob,Fo,weight = weight)
    corr0 = corr_tmmsss(tmmsss_array)
    return corr0

def corr_rank(Ob,Fo):
    rcc_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])

    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    if len(Fo_shape) == len(Ob_shape):

        r_ob = np.argsort(np.argsort(Ob.flatten()))
        r_fo = np.argsort(np.argsort(Fo.flatten()))
        n = r_ob.size
        rcc = 1 - 6 * np.sum(np.power(r_fo-r_ob,2))/(n * (n*n-1))

        #rcc = 12*np.sum(r_fo * r_fo)/(n * (n*n-1)) - 3*(n+1)/(n-1)
        return rcc
    else:
        Ob_shpe_list.insert(0, -1)
        new_Fo_shape = tuple(Ob_shpe_list)
        new_Fo = Fo.reshape(new_Fo_shape)
        new_Fo_shape = new_Fo.shape
        r_ob = np.argsort(np.argsort(Ob.flatten()))
        n = r_ob.size
        for line in range(new_Fo_shape[0]):
            r_fo = np.argsort(np.argsort(new_Fo[line, :].flatten()))
            rcc = 1 - 6 * np.sum(np.power(r_fo-r_ob,2))/(n * (n*n-1))
            rcc_list.append(rcc)
        rcc_array = np.array(rcc_list)
        shape = list(Fo_shape[:ind])
        rcc_array = rcc_array.reshape(shape)
        return rcc_array


def residual_error(Ob,Fo):
    '''
    线性回归的残差， 它等于残差率 *  观测数据的方差
    :param Ob:
    :param Fo:
    :return:
    '''
    tmmsss_array = tmmsss(Ob, Fo)
    re = residual_error_tmmsss(tmmsss_array)
    return re

def residual_error_tmmsss(tmmsss_array):
    '''
    线性回归的残差， 它等于残差率 *  观测数据的方差
    :param tmmsss_array:
    :return:
    '''
    rer = residual_error_rate_tmmsss(tmmsss_array)
    sxx = tmmsss_array[..., 3]
    re = rer * np.sqrt(sxx)
    return re

def residual_error_rate(Ob, Fo):
    '''
    线性回归的残差率，等于 1 - corr * corr
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: corr0
    '''
    tmmsss_array = tmmsss(Ob,Fo)
    rer = residual_error_rate_tmmsss(tmmsss_array)
    return rer

def residual_error_rate_tmmsss(tmmsss_array):
    '''
    线性回归的残差率，等于 1 - corr * corr
    :param tmmsss_array:
    :return:
    '''
    corr0 = corr_tmmsss(tmmsss_array)
    rer = np.sqrt(1 - np.power(corr0, 2))
    return rer


def corr_tmmsss(tmmsss_array):
    '''
    相关系数，求实况数据还和预测数据之间的相关系数
    :param tmmsss_array: 包含命中空报和漏报的多维数组，其中最后一维长度为6，分别记录了（count,mx,my,sxx,syy,sxy）
    :return:
    '''
    sxx = tmmsss_array[..., 3]
    syy = tmmsss_array[..., 4]
    sxy = tmmsss_array[..., 5]
    sxxsyy = np.sqrt(sxx * syy)
    if sxxsyy.size == 1:
        if sxxsyy == 0:
            sxxsyy = 1e-10
    else:
        sxxsyy[sxxsyy == 0] = 1e-10
    corr = sxy / sxxsyy
    return corr

def ob_fo_sum_tmmsss(tmmsss_array):
    '''
    相关系数，求实况数据还和预测数据之间的相关系数
    :param tmmsss_array: 包含命中空报和漏报的多维数组，其中最后一维长度为6，分别记录了（count,mx,my,sxx,syy,sxy）
    :return:
    '''
    if len(tmmsss_array.shape) == 1:
        tmmsss_array = tmmsss_array.reshape(1, 1, 6)
    mx = tmmsss_array[..., 1]
    my = tmmsss_array[..., 2]
    shape1 = list(tmmsss_array.shape)
    if len(tmmsss_array.shape) == 2:
        result = np.zeros((2, shape1[0]))
        result[0, :] = mx * tmmsss_array[..., 0]
        result[1, :] = my * tmmsss_array[..., 0]
    else:
        result = np.zeros((1 + shape1[0], shape1[1]))
        result[0, :] = mx * tmmsss_array[..., 0]
        result[1:, :] = my * tmmsss_array[..., 0]
    return result



def ob_fo_mean_tmmsss(tmmsss_array):
    '''
    相关系数，求实况数据还和预测数据之间的相关系数
    :param tmmsss_array: 包含命中空报和漏报的多维数组，其中最后一维长度为6，分别记录了（count,mx,my,sxx,syy,sxy）
    :return:
    '''

    if len(tmmsss_array.shape) == 1:
        tmmsss_array = tmmsss_array.reshape(1, 1, 6)
    mx = tmmsss_array[..., 1]
    my = tmmsss_array[..., 2]
    shape1 = list(tmmsss_array.shape)
    if len(tmmsss_array.shape) == 2:
        result = np.zeros((2, shape1[0]))
        result[0, :] = mx
        result[1, :] = my
    else:
        result = np.zeros((1 + shape1[0], shape1[1]))
        result[0, :] = mx
        result[1:, :] = my
    return result


def ob_fo_mean_tasem(tasem_array):
    '''
    相关系数，求实况数据还和预测数据之间的相关系数
    :param tmmsss_array: 包含命中空报和漏报的多维数组，其中最后一维长度为6，分别记录了（T,E,A,S,M）
    :return:
    '''

    if len(tasem_array.shape) == 1:
        tasem_array = tasem_array.reshape(1, 1, 5)
    mx = tasem_array[..., -1] / tasem_array[..., 0]
    my = (tasem_array[..., -1]+tasem_array[..., 1]) / tasem_array[..., 0]
    shape1 = list(tasem_array.shape)
    if len(tasem_array.shape) == 2:
        result = np.zeros((2, shape1[0]))
        result[0, :] = mx
        result[1, :] = my
    else:
        result = np.zeros((1 + shape1[0], shape1[1]))
        result[0, :] = mx
        result[1:, :] = my
    return result


def ob_fo_std_tmmsss(tmmsss_array):
    '''
    相关系数，求实况数据还和预测数据之间的相关系数
    :param tmmsss_array: 包含命中空报和漏报的多维数组，其中最后一维长度为6，分别记录了（count,mx,my,sxx,syy,sxy）
    :return:
    '''

    if len(tmmsss_array.shape) == 1:
        tmmsss_array = tmmsss_array.reshape(1, 1, 6)
    sx = tmmsss_array[..., 3]
    sy = tmmsss_array[..., 4]
    shape1 = list(tmmsss_array.shape)
    if len(tmmsss_array.shape) == 2:
        result = np.zeros((2, shape1[0]))
        result[0, :] = sx
        result[1, :] = sy
    else:
        result = np.zeros((1 + shape1[0], shape1[1]))
        result[0, :] = sx
        result[1:, :] = sy
    result = np.sqrt(result)
    return result

def tmmsss(Ob, Fo,weight = None):
    '''
    统计相关系数等检验量所需的中间变量
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: numpy 一维数组，其元素为根据Ob和Fo
    计算出的（样本数，观测平均值，预报平均值，观测方差，预报方差，协方差
    '''
    tmmsss_array_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    ob_f = Ob.flatten()
    if weight is None:
        count = Ob.size
        mx = np.mean(ob_f)
        for line in range(new_Fo_shape[0]):
            fo_f = new_Fo[line, :].flatten()
            my = np.mean(fo_f)
            dx = ob_f - mx
            dy = fo_f - my
            sxx = np.mean(np.power(dx, 2))
            syy = np.mean(np.power(dy, 2))
            sxy = np.mean(dx * dy)
            tmmsss_array_list.append(np.array([count, mx, my, sxx, syy, sxy]))
    else:
        weight_f = weight.flatten()
        count = np.sum(weight_f)
        mx = np.sum(ob_f * weight_f) /count
        for line in range(new_Fo_shape[0]):
            fo_f = new_Fo[line, :].flatten()
            my = np.sum(fo_f * weight_f) /count
            dx = ob_f - mx
            dy = fo_f - my
            sxx = np.sum(np.power(dx, 2) * weight_f)/count
            syy = np.sum(np.power(dy, 2) * weight_f)/count
            sxy = np.sum(dx * dy * weight_f) / count
            tmmsss_array_list.append(np.array([count, mx, my, sxx, syy, sxy]))
    tmmsss_array = np.array(tmmsss_array_list)
    shape = list(Fo_shape[:ind])
    shape.append(6)
    tmmsss_array = tmmsss_array.reshape(shape)
    return tmmsss_array


def tmmsss_merge(tmmsss0, tmmsss1):
    '''
    将两份包含样本数、平均值和方差、协方差的中间结果合并
    :param tmmsss0: 长度6的一维数组，分别记录了（count,mx,my,sxx,syy,sxy）
    :param tmmsss1: 长度6的一维数组，分别记录了（count,mx,my,sxx,syy,sxy）
    :return: 长度6的一维数组，分别记录了（count,mx,my,sxx,syy,sxy）
    '''
    if np.isnan(tmmsss0[0]).any():
        return tmmsss1
    elif np.isnan(tmmsss1[0]).any():
        return tmmsss0
    tmmsss_array_list = []
    tmmsss0_shape = list(tmmsss0.shape)
    tmmsss1_shape = list(tmmsss1.shape)
    if tmmsss0_shape != tmmsss1_shape:
        print('tmmsss0和tmmsss1维度不匹配')
        return
    tmmsss0 = tmmsss0.reshape((-1, 6))
    tmmsss1 = tmmsss1.reshape((-1, 6))
    new_tmmsss1_shape = tmmsss1.shape
    for line in range(new_tmmsss1_shape[0]):
        tmmsss1_piece = tmmsss1[line, :]
        tmmsss0_piece = tmmsss0[line, :]
        count_0 = tmmsss0_piece[0]
        mx_0 = tmmsss0_piece[1]
        my_0 = tmmsss0_piece[2]
        sxx_0 = tmmsss0_piece[3]
        syy_0 = tmmsss0_piece[4]
        sxy_0 = tmmsss0_piece[5]
        count_1 = tmmsss1_piece[0]
        mx_1 = tmmsss1_piece[1]
        my_1 = tmmsss1_piece[2]
        sxx_1 = tmmsss1_piece[3]
        syy_1 = tmmsss1_piece[4]
        sxy_1 = tmmsss1_piece[5]
        _, _, sxx_total = ss_iteration(count_0, mx_0, sxx_0, count_1, mx_1, sxx_1)
        _, _, syy_total = ss_iteration(count_0, my_0, syy_0, count_1, my_1, syy_1)
        count_total, mx_total, my_total, sxy_total = sxy_iteration(count_0, mx_0, my_0, sxy_0,
                                                                   count_1, mx_1, my_1, sxy_1)

        tmmsss_array_list.append(np.array([count_total, mx_total, my_total, sxx_total, syy_total, sxy_total]))
    tmmsss_array = np.array(tmmsss_array_list)
    tmmsss_array = tmmsss_array.reshape(tmmsss0_shape)
    return tmmsss_array


def tmmsss_merge_all(tmmsss_array):
    '''
    快速实现批量分块数据的合并
    :param tmmsss_array: 分块的中间量
    :return:
    '''
    count = tmmsss_array[:,0]
    mx = tmmsss_array[:,1]
    my = tmmsss_array[:,2]

    Tcount = np.sum(count)
    Tsumx = np.sum(count * mx)
    Tsumy = np.sum(count * my)

    Tmx = Tsumx/Tcount
    Tmy = Tsumy/Tcount

    ssx = tmmsss_array[:,3]
    ssy = tmmsss_array[:,4]

    Tssx =np.sum(count * ( ssx+np.power(mx - Tmx,2)))/Tcount
    Tssy = np.sum(count * ( ssy+np.power(my - Tmy,2)))/Tcount

    sxy = tmmsss_array[:,5]

    Tsxy = np.sum(count * (sxy+(mx - Tmx) * (my - Tmy)))/Tcount

    result = np.array([Tcount,Tmx,Tmy,Tssx,Tssy,Tsxy])
    return result






# ????
def mre(Ob, Fo):
    '''
    mre  精细化网格预报竞赛检验办法中的降水量定量相对误差检验指标
    :param Ob: 实况数据 不定长维度的numpy
    :param Fo: 测试数据 不定长维度的numpy
    :return: mre
    '''
    mre_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return

    s = Ob + Fo
    d = Ob - Fo
    if len(Fo_shape) == len(Ob_shape):
        if np.sum(s) == 0:
            return 0
        else:
            s1 = s[s > 0]
            d1 = d[s > 0]
            are0 = np.mean(np.abs(d1 / s1))
            return are0
    else:
        Ob_shpe_list.insert(0, -1)
        new_Fo_shape = tuple(Ob_shpe_list)
        new_s = s.reshape(new_Fo_shape)
        new_d = d.reshape(new_Fo_shape)
        new_Fo_shape = new_s.shape
        for line in range(new_Fo_shape[0]):
            s_piece = new_s[line, :]
            d_piece = new_d[line, :]
            if np.sum(s_piece) == 0:
                are0 = 0
            else:
                s1 = s_piece[s_piece > 0]
                d1 = d_piece[s_piece > 0]
                are0 = np.mean(np.abs(d1 / s1))
            mre_list.append(are0)
        mre_array = np.array(mre_list)
        shape = list(Fo_shape[:ind])
        mre_array = mre_array.reshape(shape)
        return mre_array


def mre_toar(toar_array):
    '''
    mre  精细化网格预报竞赛检验办法中的降水量定量相对误差检验指标
    :param toar_array: 包含命中空报和漏报的多维数组，其中最后一维长度为2，分别记录了（预报和观测值之和大于0样本数,各点相对误差绝对值总和）
    （预报和观测值之和大于0样本数、各点相对误差绝对值总和），它由toar返回
    :return:
    '''
    count = toar_array[..., 0] + 0
    if count.size == 1:
        if count == 0:
            mre0 = IV
        else:
            mre0 = toar_array[..., 1] / count
    else:
        count[count < 0] = 1e-10
        ar = toar_array[..., 1]
        mre0 = ar / count
        mre0[count < 1] = IV
    return mre0


def toar(Ob, Fo):
    '''
    相对误差检验指标的中间结果量
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 一维numpy数组，其内容依次为预报和观测值之和大于0样本数、各点相对误差绝对值总和
    '''

    toar_array_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    s = Ob + Fo
    d = Ob - Fo
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    s = s.reshape(new_Fo_shape)
    d = d.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    for line in range(new_Fo_shape[0]):
        s_piece = s[line, :]
        d_piece = d[line, :]
        s1 = s_piece[s_piece > 0]
        d1 = d_piece[s_piece > 0]
        ar = np.sum(np.abs(d1 / s1))
        toar_array_list.append(np.array([s1.size, ar]))
    toar_array = np.array(toar_array_list)
    shape = list(Fo_shape[:ind])
    shape.append(2)
    toar_array = toar_array.reshape(shape)
    return toar_array


def nse(Ob, Fo):
    '''
    nse纳什系数, 常用于计算两个非正态序列的相对误差情况，
    :param Ob:实况数据 不定长维度的numpy
    :param Fo:测试数据 不定长维度的numpy
    :return:负无穷至1，最优值为1
    '''
    nse_array_list = []
    Fo_shape = Fo.shape
    Ob_shape = Ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return

    mob = np.mean(Ob)
    qdob = np.mean(np.power(Ob - mob, 2))
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = Fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    for line in range(new_Fo_shape[0]):
        if qdob == 0:
            nse = IV
        else:
            nse = 1 - np.mean(np.power(Ob - new_Fo[line, :], 2)) / qdob
        nse_array_list.append(nse)
    if len(nse_array_list) == 1:
        return nse_array_list[0]
    else:
        nse_array = np.array(nse_array_list)
        shape = list(Fo_shape[:ind])
        nse_array = nse_array.reshape(shape)
        return nse_array


def nse_tase_tmmsss(tase_array, tmmsss_array):
    '''
    :param tase_array:
    :param tmmsss_array:
    :return:
    '''
    sxx = tmmsss_array[..., 3] + 0
    if sxx.size == 1:
        if sxx == 0:
            nse0 = IV
        else:
            nse0 = 1 - tase_array[..., 3] / tase_array[..., 0] / sxx
    else:
        sum = sxx + 0
        sum[sxx == 0] = 1e-10
        mse0 = tase_array[..., 3] / tase_array[..., 0]
        nse0 = 1 - mse0 / sum
        nse0[sxx == 0] = IV
    return nse0

def nse_tmmsss(tmmsss_array):
    '''
    :param tase_array:
    :param tmmsss_array:
    :return:
    '''

    sxx = tmmsss_array[..., 3] + 0
    syy = tmmsss_array[..., 4] + 0
    sxy = tmmsss_array[..., 5] + 0
    mx = tmmsss_array[..., 1] + 0
    my = tmmsss_array[..., 2] + 0
    exy = sxx + syy - 2 * sxy + (mx - my) * (mx - my)



    if sxx.size == 1:
        if sxx == 0:
            nse0 = IV
        else:
            nse0 = 1 - exy / sxx
    else:
        sum = sxx + 0
        sum[sxx == 0] = 1e-10
        mse0 = exy
        nse0 = 1 - mse0 / sum
        nse0[sxx == 0] = IV
    return nse0



def pmse(ob,fo):
    '''

    :param ob: 一维numpy数组
    :param fo:  一维或者两维numpy数组，当fo是两维时，表示有多种预报进行对比
    :return:  实数
    '''
    #如果fo只包含一个预报成员
    if len(ob.shape) == len(fo.shape):
        fo = fo[np.newaxis,:]
    nfo = fo.shape[0]
    list1 = []
    result_list = []
    nsta = ob.size
    #print("---")
    #print(nsta)
    #对多个预报进行循环
    for i in range(nfo):
        foi = fo[i,:]
        #ob3 = np.power(ob,0.33333)
        #fo3 = np.power(foi,0.333333)
        e = ob - foi
        e1 = e[e>=0]
        mse1 = np.sum(0.91*0.91* np.power(e1,0.66666))
        e2 = e[e<0]
        mse2 = np.sum(np.power(-0.7+0.57*np.power(-e2,0.3333),2))
        mse = mse1 + mse2
        result_list.append(mse/nsta)
    #result_mid = np.array(list1)
    result = np.array(result_list)

    return result



def pas_mid(ob0,fo,grade_list = [0.1]):
    '''

    :param ob: 一维numpy数组
    :param fo:  一维或者两维numpy数组，当fo是两维时，表示有多种预报进行对比
    :return:  实数,pas评分
    '''
    #如果fo只包含一个预报成员
    if len(ob0.shape) == len(fo.shape):
        fo = fo[np.newaxis,:]
    nfo = fo.shape[0]

    result_list_list = []
    ob_0 = ob0.flatten()
    #对多个预报进行循环
    for i in range(nfo):
        foi_0 = fo[i,:].flatten()
        result_list = []
        for g in range(len(grade_list)):
            grade = grade_list[g]
            # 情况1， 实况降水u=0mm，预报降水x>0mm
            index0 = np.where((ob_0>=grade)|(foi_0>=grade))
            #print(index0[0].size)
            if index0[0].size > 0:
                nsample = index0[0].size
                ob  = ob_0[index0]
                foi = foi_0[index0]

                score = 0
                index1 = np.where((ob >= 0) &(ob<0.1))
                if index1[0].size>0:
                    #情况1
                    fo1 = foi[index1]
                    score += 0.6 * np.sum(np.exp(-np.power(fo1/10,2)))


                # 情况2，1 实况降水u>=0.1mm u<10mm，预报降水xi>=0 xi<0.1
                index2 = np.where((ob >= 0.1)&(ob<10)&(foi>=0)&(foi<0.1))
                if index2[0].size>0:
                    ob2 = ob[index2]
                    score += 0.6 * np.sum(np.sin(0.05 * np.pi * (10 - ob2)))

                # 情况2，2 实况降水u>=0.1mm u<10mm，预报降水xi>=0.1 xi<u
                index2 = np.where((ob >= 0.1) & (ob < 10) & (foi >= 0.1) & (foi < ob))
                if index2[0].size > 0:
                    ob2 = ob[index2]
                    fo2 = foi[index2]
                    score += np.sum(np.sin(0.05 * np.pi * (fo2 - ob2 + 10)))

                # 情况2，3 实况降水u>=0.1mm u<10mm，预报降水x>u
                index2 = np.where((ob >= 0.1) & (ob < 10) & (foi >= ob))
                if index2[0].size > 0:
                    ob2 = ob[index2]
                    fo2 = foi[index2]
                    score += np.sum(np.exp(-np.power((fo2- ob2)/10,2)))

                # 情况3.1， 实况降水u>=10，预报降水x<u x>=0
                index3 = np.where((ob >=10)&(foi<ob)&(foi>=0))
                if index3[0].size >0:
                    ob3 = ob[index3]
                    fo3 = foi[index3]
                    score += np.sum(np.sin(0.5*np.pi*(fo3/ob3)))

                # 情况3.2， 实况降水u>=10mm，预报降水x>=u
                index3 = np.where((ob >= 10) & (foi >= ob))
                if index3[0].size > 0:
                    ob3 = ob[index3]
                    fo3 = foi[index3]
                    score += np.sum(np.exp(-np.power((fo3- ob3)/ob3,2)))

                result_list.append([nsample,score])

            else:
                result_list.append([0, 0])
        result_list_list.append(result_list)

    result = np.array(result_list_list)

    return result


def pas(ob0,fo,grade_list = [0.1]):
    '''

    :param ob0: 实况
    :param fo: 预报
    :param grade_list: 等级
    :return: pas评分
    '''
    result =  pas_mid(ob0,fo,grade_list=grade_list)
    count_array = result[:,:,0]
    score_array = result[:,:,1]

    score = score_array/(count_array+1e-30)
    score[count_array==0] = meteva.base.IV
    score = score.squeeze()
    if score.size ==1:
        score = score.item()
    return score

def pasc(ob0,fo):
    '''
    PAS晴雨预报评分
    :param ob0:实况
    :param fo:预报
    :return:
    '''
    result =  pas_mid(ob0,fo,grade_list=[0.1])
    count_array = result[:,:,0]
    score_array = result[:,:,1]
    # 如果fo只包含一个预报成员
    if len(ob0.shape) == len(fo.shape):
        fo = fo[np.newaxis, :]
    nfo = fo.shape[0]


    score_list = []
    ob_0 = ob0.flatten()
    # 对多个预报进行循环
    for i in range(nfo):
        foi = fo[i, :].flatten()
        index0 = np.where((ob_0 >=0) &(ob_0 <0.1) &(foi>=0)& (foi<0.1))
        nsample = index0[0].size  #实况和预报都是晴

        score1 = (score_array[i] + nsample)/(count_array[i] + nsample)
        score_list.append(score1)

    score =  np.array(score_list)
    score = score.squeeze()
    if score.size ==1:
        score = score.item()
    return  score


def iepi_mid(ob0,fo):
    # 如果fo只包含一个预报成员
    if len(ob0.shape) == len(fo.shape):
        fo = fo[np.newaxis, :]
    nfo = fo.shape[0]
    count_list_ipi = []
    score_list_ipi = []

    count_list_epi = []
    score_list_epi = []

    ob_0 = ob0.flatten()
    # 对多个预报进行循环
    for i in range(nfo):
        foi_0 = fo[i, :].flatten()
        # 基本条件
        index0 = np.where((foi_0 >= 0.1) | (ob_0 >= 0.1))
        # print(index0[0].size)
        nsample = index0[0].size
        score_epi = 0
        score_ipi = 0
        nsample_epi = 0
        nsample_ipi =0
        if nsample > 0:
            ob = ob_0[index0]
            foi = foi_0[index0]

            #情况1
            index1 = np.where((ob >= 0) & (ob < 0.1))
            if index1[0].size > 0:
                fo_1 = foi[index1]
                score_epi += np.sum(1 - 0.6 * np.exp(- np.power(fo_1/10,2)))
                nsample_epi += index1[0].size

            # 情况2，1
            index2 = np.where((ob >= 0.1) & (ob < 10) & (foi >= 0) & (foi < 0.1))
            if index2[0].size > 0:
                ob2 = ob[index2]
                score_ipi += np.sum(0.6 * np.sin(0.05 * np.pi * (10 - ob2)) - 1)
                nsample_ipi += index2[0].size

            # 情况2，2 实况降水u>=0.1mm u<10mm，预报降水xi>=0.1 xi<u
            index2 = np.where((ob >= 0.1) & (ob < 10) & (foi >= 0.1) & (foi < ob))
            if index2[0].size > 0:
                ob2 = ob[index2]
                fo2 = foi[index2]
                score_ipi += np.sum(np.sin(0.05 * np.pi * (fo2 - ob2 + 10)) - 1)
                nsample_ipi += index2[0].size

            # 情况2，3 实况降水u>=0.1mm u<10mm，预报降水x>u
            index2 = np.where((ob >= 0.1) & (ob < 10) & (foi >= ob))
            if index2[0].size > 0:
                ob2 = ob[index2]
                fo2 = foi[index2]
                score_epi += np.sum(1 - np.exp(-np.power((fo2 - ob2) / 10, 2)))
                nsample_epi += index2[0].size

            # 情况3.1， 实况降水u>=10，预报降水x<u x>=0
            index3 = np.where((ob >= 10) & (foi < ob) & (foi >= 0))
            if index3[0].size > 0:
                ob3 = ob[index3]
                fo3 = foi[index3]
                score_ipi += np.sum(np.sin(0.5 * np.pi * (fo3 / ob3)) - 1)
                nsample_ipi += index3[0].size

            # 情况3.2， 实况降水u>=10mm，预报降水x>=u
            index3 = np.where((ob >= 10) & (foi >= ob))
            if index3[0].size > 0:
                ob3 = ob[index3]
                fo3 = foi[index3]
                score_epi += np.sum(1- np.exp(-np.power((fo3 - ob3) / ob3, 2)))
                nsample_epi += index3[0].size

            count_list_ipi.append(nsample_ipi)
            score_list_ipi.append(score_ipi)
            count_list_epi.append(nsample_epi)
            score_list_epi.append(score_epi)


    score_array_ipi = np.array(score_list_ipi)
    count_array_ipi = np.array(count_list_ipi)
    score_array_epi = np.array(score_list_epi)
    count_array_epi = np.array(count_list_epi)


    return score_array_ipi,count_array_ipi,score_array_epi,count_array_epi




def ipi(ob0,fo):

    score_array_ipi, count_array_ipi, _, _ = iepi_mid(ob0,fo)
    score = score_array_ipi / (count_array_ipi + 1e-30)
    score[count_array_ipi == 0] = meteva.base.IV
    score = score.squeeze()
    if score.size == 1:
        score = score.item()
    return score






def epi(ob0,fo):

    _,_,score_array_epi, count_array_epi = iepi_mid(ob0,fo)
    score = score_array_epi / (count_array_epi + 1e-30)
    score[count_array_epi == 0] = meteva.base.IV
    score = score.squeeze()
    if score.size == 1:
        score = score.item()
    return score


def iepi(ob0,fo):
    score_array_ipi, count_array_ipi,score_array_epi, count_array_epi = iepi_mid(ob0,fo)
    count = count_array_ipi+count_array_epi
    score = (score_array_ipi + score_array_epi) / (count + 1e-30)
    score[count == 0] = meteva.base.IV
    score = score.squeeze()
    if score.size == 1:
        score = score.item()
    return score




if __name__=="__main__":
    pass
    import math
    # import pandas as pd
    # path = r"H:\test_data\input\mem\pas\1_Two_Typical_Processes_data\1_3Results\1_3_1Results_GCEM\result.txt"
    # df = pd.read_csv(path,sep="\\s+",header=None)
    # nsta = len(df.index)
    #
    # for i in range(47999):
    #     ob = np.array([df.iloc[i,0]])
    #     fo = np.array([df.iloc[i,1]])
    #     pas1 = pas(ob,fo,grade_list=[0.1])
    #     pas01 = round(pas1[0,0], 3)
    #     if pas01 == meteva.base.IV:
    #         if df.iloc[i,6] ==1 and df.iloc[i,7] ==0:
    #             pass
    #         else:
    #             print(i)
    #             print(df.iloc[i, 6])
    #             print(ob)
    #             print(fo)
    #             print()
    #     else:
    #         if abs(pas1 - df.iloc[i,6])>0.001:
    #             print(i)
    #             print(df.iloc[i,6])
    #             print(ob)
    #             print(fo)
    #             # xi = fo[0]
    #             # ui = ob[0]
    #             # pas2 = math.exp(-1 * ((xi - ui) / ui) ** 2)
    #
    #             print()
    #

    # import pandas as pd
    # import datetime
    # import meteva
    # import xarray as xr
    # path  = r"H:\test_data\input\mem\pas\1_Two_Typical_Processes_data\1_2Forecasted_precipitation_data\2019071612\WRF3.2019071600012.nc"
    # grd = xr.open_dataset(path)
    # print(grd["APCP_P8_L1_GLC0_acc"])
    #
    # time1 = datetime.datetime(2019,7,16,0)
    # sta = pd.DataFrame({"level": 0, "time": time1, "dtime": 12,
    #                     "id": np.arange(grd.coords["gridlat_0"].values.size),
    #                     "lon": grd.coords["gridlon_0"].values.flatten(),
    #                     "lat": grd.coords["gridlat_0"].values.flatten(),
    #                     "RAINC": grd.variables["APCP_P8_L1_GLC0_acc"].values.flatten()
    #                     })
    # print(sta)
    #
    # grd_list = []
    # time1 = datetime.datetime(2019,7,16,0)
    # for dh in range(1,13,1):
    #     time_ob = time1 + datetime.timedelta(hours=dh)
    #     path = r"H:\test_data\input\mem\pas\1_Two_Typical_Processes_data\1_1Observed_precipitation_data\2019071612\surfr"+str(dh).zfill(2)+"h.nc"
    #     grd1 = meteva.base.read_griddata_from_nc(path,time=time_ob)
    #     grd_list.append(grd1)
    #
    # grd_all = meteva.base.concat(grd_list)
    # grd_ob = meteva.base.sum_of_grd(grd_all,used_coords=["time"])
    # print(grd_ob.values[0,0,0,0,262,1028])
    #
    # grid0 = meteva.base.get_grid_of_data(grd_ob)
    # #grid1 = meteva.base.grid([111.025,122.975,0.05],[28.025,37.975,0.05])
    # grd_fo = meteva.base.interp_sg_idw(sta,grid0,nearNum=1)
    #
    # #grd_ob1 = meteva.base.interp_gg_linear(grd_ob,grid = grid1)
    # #grd_fo1 = meteva.base.interp_gg_linear(grd_fo,grid = grid1)
    #
    # # meteva.base.contourf_xy(grd_ob1,save_path=r"H:\a.png")
    # # meteva.base.contourf_xy(grd_fo1, save_path=r"H:\b.png")
    # # print()
    #
    # ob_ = grd_ob.values[0,0,0,0,261:461,821:1061]
    # fo_ = grd_fo.values[0, 0, 0, 0, 261:461, 821:1061]
    # pas_list = pas(ob_,fo_,grade_list=[0.1,10,25,50])
    # print(pas_list)
    #
    # pasc1 = pasc(ob_,fo_)
    # print(pasc1)
    # #
    #
    #
    #
    # ipi1 = ipi(ob_,fo_)
    # epi1 = epi(ob_,fo_)
    # iepi1 = iepi(ob_,fo_)
    # print(ipi1)
    # print(epi1)
    # print(iepi1)
    # print()

