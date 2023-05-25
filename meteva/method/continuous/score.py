import numpy as np
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



def ob_fo_precipitation_strenght(ob,fo):
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


def tase(Ob, Fo):
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
    for line in range(new_Fo_shape[0]):
        total_count = Ob.size
        e_sum = np.sum(new_Fo[line, :] - Ob)
        ae_sum = np.sum(np.abs(new_Fo[line, :] - Ob))
        se_sum = np.sum(np.square(new_Fo[line, :] - Ob))
        tase_list.append(np.array([total_count, e_sum, ae_sum, se_sum]))
    tase_np = np.array(tase_list)
    shape = list(Fo_shape[:ind])
    shape.append(4)

    tase_array = tase_np.reshape(shape)
    return tase_array

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

def me(Ob, Fo):
    '''
    me 求两组数据的误差平均值
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 负无穷到正无穷的实数，最优值为0
    '''
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


def mae(Ob, Fo):
    '''
    me 求两组数据的误差平均值
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 负无穷到正无穷的实数，最优值为0
    '''
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


def mae_tase(tase_array):
    '''
    mean_abs_error,求两组数据的平均绝对误差
    :param tase_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（total_count,e_sum,ae_sum,se_sum）
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到无穷大，最优值为0
    '''
    mean_abs_error = tase_array[..., 2] / tase_array[..., 0]
    return mean_abs_error


def mse(Ob, Fo):
    '''
    mean_sqrt_error, 求两组数据的均方误差
    ----------------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 0到无穷大，最优值为0
    '''

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


def mse_tase(tase_array):
    '''
    mse 求两组数据的均方误差
    :param tase_array:包含命中空报和漏报的多维数组，其中最后一维长度为4，分别记录了（total_count,e_sum,ae_sum,se_sum）
    （样本数，误差和、绝对误差和，误差平方和），它由tase返回
    :return: 0到无穷大，最优值为0
    '''
    mean_squre_error = tase_array[..., 3] / tase_array[..., 0]
    return mean_squre_error


def rmse(Ob, Fo):
    '''
    root_mean_square_error 求两组数据的均方根误差
    ------------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: 0到无穷大，最优值为0
    '''
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


def corr(Ob, Fo):
    '''
    相关系数，求实况数据还和预测数据之间的相关系数
    -----------------------------
    :param Ob: 实况数据  任意维numpy数组
    :param Fo: 预测数据 任意维numpy数组,Fo.shape 和Ob.shape一致
    :return: corr0
    '''
    tmmsss_array = tmmsss(Ob,Fo)
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

def tmmsss(Ob, Fo):
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
    for line in range(new_Fo_shape[0]):
        ob_f = Ob.flatten()
        fo_f = new_Fo[line, :].flatten()
        count = Ob.size
        mx = np.mean(ob_f)
        my = np.mean(fo_f)
        dx = ob_f - mx
        dy = fo_f - my
        sxx = np.mean(np.power(dx, 2))
        syy = np.mean(np.power(dy, 2))
        sxy = np.mean(dx * dy)
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



def pas(ob0,fo,grade_list = [0.1]):
    '''

    :param ob: 一维numpy数组
    :param fo:  一维或者两维numpy数组，当fo是两维时，表示有多种预报进行对比
    :return:  实数,pas评分
    '''
    #如果fo只包含一个预报成员
    if len(ob0.shape) == len(fo.shape):
        fo = fo[np.newaxis,:]
    nfo = fo.shape[0]
    list1 = []
    result_list = []
    ob_0 = ob0.flatten()
    #对多个预报进行循环
    for i in range(nfo):
        nsample = 0
        score = 0
        foi = fo[i,:].flatten()
        # 情况1， 实况降水u=0mm，预报降水x>0mm
        index0 = np.where((ob_0>=grade_list[0])|(foi>=grade_list[0]))
        #print(index0[0].size)

        ob  = ob_0[index0]
        foi = foi[index0]
        index1 = np.where((ob == 0)&(foi>0))
        score1 = 0
        if index1[0].size>0:
            fo1 = foi[index1]
            nsample += index1[0].size
            fo11 = fo1[fo1<5]         # 预报 0<x<5mm的情况
            score1  += 0.5* fo11.size
            fo12 = fo1[fo1>=5]        #预报 x>=5mm的情况
            if fo12.size>0:
                score1 += 0.5 * np.sum(np.exp(-(fo12 - 5) ** 2 / 25))
            # print("情况1：")
            # print(index1[0].size)
            #print(score1)

        # 情况2， 实况降水u>0mm，预报降水x=0mm
        index2 = np.where((ob > 0)&(ob<10)&(foi == 0))
        score2 = 0
        if index2[0].size>0:
            ob2 = ob[index2]
            nsample += index2[0].size
            score2 += 0.5 * np.sum(np.sin(0.05 * np.pi * (10 + ob2)))
            # print("情况2：")
            # print(index2[0].size)
            #print(score2)

        # 情况3， 实况降水0<u<5mm，预报降水x>0mm
        index3 = np.where((ob>0)&(ob<5)&(foi>0))
        score3 =0
        if index3[0].size >0:
            nsample += index3[0].size
            ob3 = ob[index3]
            fo3 = foi[index3]
            ob31 = ob3[fo3<ob3]   #情况3.1  0<x<u,0<u<5
            if ob31.size>0:
                fo31 = fo3[fo3 < ob3]
                score3 += np.sum(np.sin(0.05*np.pi*(10+ob31-fo31)))
            ob32 = ob3[np.where((fo3<5)&(ob3<=fo3))]   #情况3.2  0<x<5,0<u<x
            score3 += ob32.size
            ob33 = ob3[fo3>=5]  #情况3.3  x>=5,0<u<5
            if ob33.size>0:
                fo33 = fo3[fo3>=5]
                score3 += np.sum(np.exp(-(fo33-5)**2/25))
            # print("情况3：")
            # print(index3[0].size)
            #print(score3)

        # 情况4， 实况降水5<u<10mm，预报降水x>0mm
        index4 = np.where((ob>=5)&(ob<10)&(foi>0))
        score4 = 0
        if index4[0].size>0:
            nsample+= index4[0].size
            ob4 = ob[index4]
            fo4 = foi[index4]
            ob41 = ob4[fo4<ob4]  #情况4.1 0<x<u,5<u<10
            if ob41.size>0:
                fo41 = fo4[fo4<ob4]
                score4 += np.sum(np.sin(0.05*np.pi*(10+ob41-fo41)))
            ob42 = ob4[fo4>=ob4]  #情况4.2 u<x,5<u<10
            if ob42.size>0:
                fo42 = fo4[fo4>=ob4]
                score4 += np.sum(np.exp(-(fo42-ob42)**2/ob42**2))
            # print("情况4：")
            # print(index4[0].size)
            #print(score4)


        # 情况5， 实况降水u>=10mm，预报降水x>0mm
        index5 = np.where((ob >=10)  & (foi >= 0))
        score5 = 0
        if index5[0].size >0:
            nsample += index5[0].size
            ob5 = ob[index5]
            fo5 = foi[index5]
            ob51 = ob5[fo5<ob5]  #情况5.1, 0<=x<u,u>=10
            if ob51.size>0:
                fo51 = fo5[fo5<ob5]
                score5 += np.sum(np.sin(0.5*np.pi*fo51/ob51))
            ob52 = ob5[fo5>=ob5]  #情况5.2, u<=x,u>=10
            if ob52.size>0:
                fo52 = fo5[fo5>=ob5]
                score5 += np.sum(np.exp(-(fo52-ob52)**2/ob52**2))
            # print("情况5：")
            # print(index5[0].size)
            #print(score5)
        score = score1 + score2+score3+score4+score5
        #print(score)
        #计算
        if nsample==0:
            result1 = IV
        else:
            result1 = score/nsample
        list1.append([nsample,score])
        result_list.append(result1)

    #result_mid = np.array(list1)
    result = np.array(result_list)


    return result


if __name__=="__main__":
    import pandas as pd
    import datetime
    import meteva
    import xarray as xr
    # grid0 = meteva.base.grid([111.025, 122.975, 0.05], [28.025, 37.975, 0.05])
    #
    # grd0 = xr.open_dataset(r"H:\task\paper\word\w20-ElR\2020080312yb\WRF3.2020080312012.grb2",
    #                        filter_by_keys={'typeOfLevel': 'surface'})
    #
    # sta = pd.DataFrame({"level": 0, "time": datetime.datetime(2022, 1, 1, 8), "dtime": 0,
    #                     "lon": grd0.coords["longitude"].values.flatten(),
    #                     "lat": grd0.coords["latitude"].values.flatten(),
    #                     "id": np.arange(grd0.coords["latitude"].values.size),
    #                     "tp": grd0.variables["tp"].values.flatten()
    #                     })
    #
    # fo = meteva.base.interp_sg_idw(sta, grid=grid0, nearNum=1, effectR=200)  # 将站点数据插值到网格上
    #
    # ob = meteva.base.grid_data(grid0)
    # for i in range(1, 13):
    #     ob1 = meteva.base.read_griddata_from_nc(r"H:\task\paper\word\w20-ElR\2020080400sk\surfr" + str(i).zfill(2) + "h.nc",
    #                                     grid=grid0)
    #     ob.values += ob1
    # #print(ob)
    #
    # value = meteva.method.pas(ob.values, fo.values, grade_list=[0.1])
    # print("pas01_value=" + str(value[0]))
    #meteva.base.read_stadata_from_csv()

    sta = pd.read_csv(r"C:\Users\admin\Documents\WeChat Files\wxid_54saim7nonz321\FileStorage\File\2023-04\a.txt",
                      skiprows = 0,header = None,sep="\s+")
    ob = sta.iloc[:,0].values
    fo = sta.iloc[:,1].values
    value = meteva.method.pas(ob, fo, grade_list=[0.1])
    print("pas01_value=" + str(value[0]))
    value = meteva.method.pas(ob, fo, grade_list=[10])
    print("pas10_value=" + str(value[0]))
    value = meteva.method.pas(ob, fo, grade_list=[25])
    print("pas25_value=" + str(value[0]))
    value = meteva.method.pas(ob, fo, grade_list=[50])
    print("pas50_value=" + str(value[0]))