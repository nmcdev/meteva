import os
import numpy as np
import meteva



def scd_nasd(nasd_array):
    '''
    基于中间结果计算风向预报评分
    :param nasd_array: 输入nasd函数统计得到的样本数、风向正确样本数、风向评分（分子部分）
    :return: 返回平均的风向预报评分
    '''
    total = nasd_array[...,0]
    sc = nasd_array[...,2]
    scd = sc/total
    return scd

def acd_nasd(nasd_array,unit = 1):
    '''
    基于中间结果计算风向预报准确率，
    :param nasd_array: 输入nasd函数统计得到的样本数、风向正确样本数、风向评分（分子部分）
    :return: 返回平均的风向预报准确率
    '''
    total = nasd_array[...,0]
    sc = nasd_array[...,1]
    acd = sc/total
    if unit =="%":
        acd *= 100
    return acd

def nas_d(d_ob,d_fo,s_ob = None,s_fo = None, ignore_breeze = False):
    '''
    计算风向预报准确率和评分的中间量。
    将输入的观测和预报风向（0-360度），转换成计算风向预报准确率，风向预报评分所需要的中间量
    ，计算的第一步是将预报和观测的风向都转换成8个离散的方位角。
    :param d_ob:观测的风向，numpy数组
    :param s_ob:观测的风速，numpy数组，shape和d_ob完全一致
    :param d_fo:预报的风向，numpy数组，shape可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param s_fo:预报的风速，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param ignore_breeze ： 该参数为True时，若预报和观测的风速都小于等于3级，则认为风向是正确的。
    :return:根据预报和观测的风向数据，统计得到的样本数、风向正确样本数、风向评分（分子部分），d_fo和d_ob的shape一致，则说明只有一家预报，此时返回
             一维的数据，size= 3。 如果d_fo和d_ob的shape不一致，则说明有多个预报，则返回的数据shape = （预报成员数，3）
    '''
    Ob_shape = d_ob.shape
    Fo_shape = d_fo.shape
    nasd_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = d_fo.reshape(new_Fo_shape)
    new_Fo_s = None
    if s_fo is not None:
        new_Fo_s = s_fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape
    ob0 = meteva.base.tool.math_tools.tran_direction_to_8angle(d_ob)
    for line in range(new_Fo_shape[0]):
        fo = meteva.base.tool.math_tools.tran_direction_to_8angle(new_Fo[line, :])
        if ignore_breeze:
            if new_Fo_s is None or s_ob is None:
                print("if need to ignore breeze, s_fo and s_ob must not be None")
            fo_s = new_Fo_s[line,:]
            index = np.where((s_ob >= 5.5)|(fo_s>=5.5))
            breeze_count =d_ob.size - len(index[0])
            ob = ob0[index]
            fo = fo[index]
        else:
            ob = ob0
            breeze_count = 0
        nasd_array = np.zeros(3)
        nasd_array[0] = d_ob.size
        d_angle = np.abs(fo - ob)
        d_angle[d_angle == 6] = 1
        index = np.where(d_angle ==0)
        nasd_array[1] = len(index[0]) + breeze_count
        nasd_array[2] = len(index[0]) + breeze_count
        index = np.where(d_angle == 1)
        nasd_array[2] += len(index[0]) * 0.6

        nasd_list.append(nasd_array)
    nasd_array = np.array(nasd_list)
    shape = list(Fo_shape[:ind])
    shape.append(3)
    nasd_array = nasd_array.reshape(shape)
    return nasd_array

def scd(d_ob,d_fo,s_ob = None,s_fo = None, ignore_breeze = False):
    '''
    计算风向预报评分。
    基于原始风向数组，计算风向预报评分。计算的第一步是将预报和观测的风向都转换成8个离散的方位角，
    当一个样本的预报观测方位角正好相同时，得1分，方位角差1级，得0.6分，否则得0分。风向评分等于所有样本得分的平均。
    :param d_ob:观测的风向，numpy数组
    :param s_ob:观测的风速，numpy数组，shape和d_ob完全一致
    :param d_fo:预报的风向，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param s_fo:预报的风速，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param ignore_breeze ： 该参数为True时，若预报和观测的风速都小于等于3级，则认为风向是正确的。
    :return: 风向预报评分，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    nasd_array = nas_d(d_ob,d_fo,s_ob = s_ob,s_fo = s_fo,ignore_breeze= ignore_breeze)
    scd0 = scd_nasd(nasd_array)
    return scd0

def acd(d_ob,d_fo,s_ob = None,s_fo = None, ignore_breeze = False,unit = 1):
    '''
    计算风向预报准确率。
    基于原始风向数组，计算风向预报准确率，计算的第一步是将预报和观测的风向都转换成8个离散的方位角，
    当预报和观测的方位角正好相同时，就记为正确，否则记为错误，风向预报准确率时正确样本数/总样本数。
    :param d_ob:观测的风向，numpy数组
    :param s_ob:观测的风速，numpy数组，shape和d_ob完全一致
    :param d_fo:预报的风向，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param s_fo:预报的风速，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param ignore_breeze ： 该参数为True时，若预报和观测的风速都小于等于3级，则认为风向是正确的。
    :return: 风向预报准确率，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    nasd_array = nas_d(d_ob,d_fo,s_ob = s_ob,s_fo = s_fo,ignore_breeze= ignore_breeze)
    acd0 = acd_nasd(nasd_array,unit=unit)
    return acd0

def nas_uv(u_ob,u_fo,v_ob,v_fo, ignore_breeze = False):
    '''
    根据u，v分量计算风向预报准确率和评分的中间量。
    将输入的观测和预报风向（0-360度），转换成计算风向预报准确率，风向预报评分所需要的中间量
    ，计算的第一步是将预报和观测的风向都转换成8个离散的方位角。
    :param u_ob: 观测的u分量，numpy数组
    :param u_fo: 预报的u分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），u_fo.shape低维与u_ob.shape保持一致
    :param v_ob: 观测的u分量，numpy数组，shape 和u_ob完全一致
    :param v_fo: 预报的v分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），v_fo.shape低维与v_ob.shape保持一致
    :param ignore_breeze:  该参数为True时，若预报和观测的风速都小于等于3级，则认为风向是正确的。
    :return: 根据预报和观测的风向数据，统计得到的样本数、风向正确样本数、风向评分（分子部分），d_fo和d_ob的shape一致，则说明只有一家预报，此时返回
             一维的数据，size= 3。 如果d_fo和d_ob的shape不一致，则说明有多个预报，则返回的数据shape = （预报成员数，3）
    '''
    s_ob,d_ob = meteva.base.math_tools.u_v_to_s_d(u_ob,v_ob)
    s_fo,d_fo = meteva.base.math_tools.u_v_to_s_d(u_fo,v_fo)
    return nas_d(d_ob,d_fo,s_ob = s_ob,s_fo = s_fo,ignore_breeze= ignore_breeze)

def scd_uv(u_ob,u_fo,v_ob,v_fo, ignore_breeze = False):
    '''
    计算风向预报评分。
    基于原始风向数组，计算风向预报评分。计算的第一步是将预报和观测的风向都转换成8个离散的方位角，
    当一个样本的预报观测方位角正好相同时，得1分，方位角差1级，得0.6分，否则得0分。风向评分等于所有样本得分的平均。
    :param u_ob: 观测的u分量，numpy数组
    :param u_fo: 预报的u分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），u_fo.shape低维与u_ob.shape保持一致
    :param v_ob: 观测的u分量，numpy数组，shape 和u_ob完全一致
    :param v_fo: 预报的v分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），v_fo.shape低维与v_ob.shape保持一致
    :param ignore_breeze ： 该参数为True时，若预报和观测的风速都小于等于3级，则认为风向是正确的。
    :return: 风向预报评分，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    s_ob,d_ob = meteva.base.math_tools.u_v_to_s_d(u_ob,v_ob)
    s_fo,d_fo = meteva.base.math_tools.u_v_to_s_d(u_fo,v_fo)
    #print(d_ob)
    nasd_array = nas_d(d_ob, d_fo, s_ob=s_ob, s_fo=s_fo, ignore_breeze=ignore_breeze)
    scd0 = scd_nasd(nasd_array)
    return scd0

def acd_uv(u_ob,u_fo,v_ob,v_fo, ignore_breeze = False,unit = 1):
    '''
    计算风向预报准确率。
    基于u,v风分量，计算风向预报准确率。计算的第一步是将预报和观测的风向都转换成8个离散的方位角，
    当一个样本的预报观测方位角正好相同时，得1分，方位角差1级，得0.6分，否则得0分。风向评分等于所有样本得分的平均。
    :param u_ob: 观测的u分量，numpy数组
    :param u_fo: 预报的u分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），u_fo.shape低维与u_ob.shape保持一致
    :param v_ob: 观测的v分量，numpy数组，shape 和u_ob完全一致
    :param v_fo: 预报的v分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），v_fo.shape低维与v_ob.shape保持一致
    :param ignore_breeze ： 该参数为True时，若预报和观测的风速都小于等于3级，则认为风向是正确的。
    :return: 风向预报准确率，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    s_ob,d_ob = meteva.base.math_tools.u_v_to_s_d(u_ob,v_ob)
    s_fo,d_fo = meteva.base.math_tools.u_v_to_s_d(u_fo,v_fo)
    nasd_array = nas_d(d_ob, d_fo, s_ob=s_ob, s_fo=s_fo, ignore_breeze=ignore_breeze)
    acd0 = acd_nasd(nasd_array,unit=unit)
    return acd0


def nasws_s(s_ob,s_fo,min_s = 0,max_s = 300):
    '''
    将输入的观测和预报风速（m/s），转换成计算风速预报准确率，风向预报评分所需要的中间量
    :param s_ob:观测的风向，numpy数组，计算的第一步是将预报和观测的风速都转换成14个离散的等级，
    :param s_fo:预报的风向，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param min_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :param max_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :return:根据预报和观测的风速数据，统计得到的样本数、风速等级正确样本数、风速评分（分子部分）,偏弱样本数，偏强样本数，d_fo和d_ob的shape一致，则说明只有一家预报，此时返回
             一维的数据，size= 5。 如果d_fo和d_ob的shape不一致，则说明有多个预报，则返回的数据shape = （预报成员数，5）
    '''
    Ob_shape = s_ob.shape
    Fo_shape = s_fo.shape
    nass_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = s_fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape

    ob0 = meteva.base.tool.math_tools.tran_speed_to_14grade(s_ob)
    #print(ob0)
    for line in range(new_Fo_shape[0]):
        fo = new_Fo[line, :]
        #print(fo)
        if min_s>0 or max_s < 300:
            index = np.where(((s_ob>=min_s) & (s_ob < max_s)) | ((fo >= min_s) & (fo < max_s)))
            ob = ob0[index]
            fo = fo[index]
        else:
            ob = ob0

        fo = meteva.base.tool.math_tools.tran_speed_to_14grade(fo)
        nass_array = np.zeros(5)
        d_grade = np.abs(fo - ob)
        nass_array[0] = ob.size
        index = np.where(d_grade ==0)
        nass_array[1] = len(index[0])
        nass_array[2] = len(index[0])
        index = np.where(d_grade == 1)
        nass_array[2] += len(index[0]) * 0.6
        index = np.where(d_grade == 2)
        nass_array[2] += len(index[0]) * 0.4
        index = np.where(fo < ob)
        nass_array[3] += len(index[0])
        index = np.where(fo > ob)
        nass_array[4] += len(index[0])
        nass_list.append(nass_array)


    nass_array = np.array(nass_list)
    shape = list(Fo_shape[:ind])
    shape.append(5)
    nass_array = nass_array.reshape(shape)



    return nass_array


def nasws_uv(u_ob,u_fo,v_ob,v_fo,min_s = 0,max_s = 300):
    '''
    根据u，v分量计算风速预报准确率和评分的中间量。
    将输入的观测和预报风向（0-360度），转换成计算风向预报准确率，风向预报评分所需要的中间量
    ，计算的第一步是将预报和观测的风向都转换成8个离散的方位角。
    :param u_ob: 观测的u分量，numpy数组
    :param u_fo: 预报的u分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），u_fo.shape低维与u_ob.shape保持一致
    :param v_ob: 观测的u分量，numpy数组，shape 和u_ob完全一致
    :param v_fo: 预报的v分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），v_fo.shape低维与v_ob.shape保持一致
    :param min_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :param max_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :return: 根据预报和观测的风向数据，统计得到的样本数、风向正确样本数、风向评分（分子部分），d_fo和d_ob的shape一致，则说明只有一家预报，此时返回
             一维的数据，size= 3。 如果d_fo和d_ob的shape不一致，则说明有多个预报，则返回的数据shape = （预报成员数，3）
    '''
    s_ob,d_ob = meteva.base.math_tools.u_v_to_s_d(u_ob,v_ob)
    s_fo,d_fo = meteva.base.math_tools.u_v_to_s_d(u_fo,v_fo)
    return nasws_s(s_ob,s_fo,min_s = min_s,max_s = max_s)


def scs_nasws(nass_array):
    '''
    基于中间结果计算风速预报评分
    :param nasd_array: 输入nass函数统计得到的样本数、风速等级正确样本数、风速预报评分（分子部分），偏弱样本数，偏强样本数
    :return: 返回平均的风速预报评分
    '''
    total = nass_array[...,0]
    sc = nass_array[...,2]
    scs = sc/total
    return scs

def scs(s_ob,s_fo,min_s = 0,max_s = 300):
    '''
    基于原始风速（m/s)数组，计算风速预报评分。计算的第一步是将预报和观测的风向都转换成14个离散的风速等级，
    当一个样本的预报和观测风速等级正好相同时，得1分，等级差1级，得0.6分，等级差2级得0.4分,否则不得分。风速评分等于所有样本得分的平均。
    :param s_ob:观测的风向，numpy数组，
    :param s_fo:预报的风向，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param min_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :param max_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :return: 风向预报评分，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    nass_array = nasws_s(s_ob,s_fo,min_s = min_s,max_s =max_s)
    scs0 = scs_nasws(nass_array)
    return scs0

def scs_uv(u_ob, u_fo, v_ob, v_fo, min_s = 0,max_s = 300):
    '''
    风速预报评分。
    基于原始u，v风（m/s)数组，计算风速预报评分。计算的第一步是将预报和观测的风向都转换成14个离散的风速等级，
    当一个样本的预报和观测风速等级正好相同时，得1分，等级差1级，得0.6分，等级差2级得0.4分,否则不得分。风速评分等于所有样本得分的平均。
    :param u_ob: 观测的u分量，numpy数组
    :param u_fo: 预报的u分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），u_fo.shape低维与u_ob.shape保持一致
    :param v_ob: 观测的u分量，numpy数组，shape 和u_ob完全一致
    :param v_fo: 预报的v分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），v_fo.shape低维与v_ob.shape保持一致
    :param min_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :param max_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :return: 风速预报评分，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    s_ob, d_ob = meteva.base.math_tools.u_v_to_s_d(u_ob, v_ob)
    s_fo, d_fo = meteva.base.math_tools.u_v_to_s_d(u_fo, v_fo)
    nass_array = nasws_s(s_ob,s_fo,min_s = min_s,max_s =max_s)
    scs0 = scs_nasws(nass_array)
    return scs0


def acs_nasws(nass_array,unit = 1):
    '''
    基于中间结果计算风速预报准确率，
    :param nasd_array: 输入nasd函数统计得到的样本数、风速正确样本数、风速评分（分子部分），偏弱样本数，偏强样本数
    :return: 返回平均的风速预报准确率
    '''
    total = nass_array[...,0]
    sc = nass_array[...,1]
    acs = sc/total
    if unit =="%":
        acs *= 100
    return acs

def acs(s_ob,s_fo,min_s = 0,max_s = 300,unit = 1):
    '''
    基于原始风速（m/s)数组，计算风速预报准确率。计算的第一步是将预报和观测的风向都转换成14个离散的风速等级，
    当一个样本的预报和观测风速等级正好相同时，记为正确，否则记为错误。风速评分等于所有样本得分的平均。
    :param s_ob:观测的风向，numpy数组，
    :param s_fo:预报的风向，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param min_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :param max_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :return: 风速预报准确率，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    nass_array = nasws_s(s_ob, s_fo,min_s = min_s,max_s =max_s)
    acs0 = acs_nasws(nass_array,unit = unit)
    return acs0


def acs_uv(u_ob, u_fo, v_ob, v_fo, min_s = 0,max_s = 300,unit = 1):
    '''
    风速预报准确率。
    基于原始u，v风（m/s)数组，计算风速预报准确率。计算的第一步是将预报和观测的风向都转换成14个离散的风速等级，
    当一个样本的预报和观测风速等级正好相同时，记为正确，否则记为错误。风速评分等于所有样本得分的平均。
    :param u_ob: 观测的u分量，numpy数组
    :param u_fo: 预报的u分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），u_fo.shape低维与u_ob.shape保持一致
    :param v_ob: 观测的u分量，numpy数组，shape 和u_ob完全一致
    :param v_fo: 预报的v分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），v_fo.shape低维与v_ob.shape保持一致
    :param min_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :param max_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :return: 风速预报准确率，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    s_ob, d_ob = meteva.base.math_tools.u_v_to_s_d(u_ob, v_ob)
    s_fo, d_fo = meteva.base.math_tools.u_v_to_s_d(u_fo, v_fo)
    nass_array = nasws_s(s_ob, s_fo,min_s = min_s,max_s =max_s)
    acs0 = acs_nasws(nass_array,unit = unit)
    return acs0


def wind_severer_rate_nasws(nasws_array,unit = 1):
    '''
    基于中间结果计算风速预报偏强率，
    :param nasd_array: 输入nasd函数统计得到的样本数、风速正确样本数、风速评分（分子部分），偏弱样本数，偏强样本数
    :return: 返回平均的风速预报准确率
    '''
    total = nasws_array[...,0]
    sc = nasws_array[...,4]
    rs = sc/total
    if unit == "%":
        rs *= 100
    return rs

def wind_severer_rate(s_ob,s_fo,min_s = 0,max_s = 300,unit = 1):
    '''
    基于原始风向数组，计算风速预报偏强率，计算的第一步是将预报和观测的风向都转换成14个离散的风速等级，
    当预报风速等级大于观测风速等级时记为1，否则记为0，偏强率是偏强的样本数/总样本数
    :param u_ob: 观测的u分量，numpy数组
    :param u_fo: 预报的u分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），u_fo.shape低维与u_ob.shape保持一致
    :param v_ob: 观测的u分量，numpy数组，shape 和u_ob完全一致
    :param v_fo: 预报的v分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），v_fo.shape低维与v_ob.shape保持一致
    :param min_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :param max_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :return: 风向预报准确率，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    nass_array = nasws_s(s_ob, s_fo,min_s = min_s,max_s =max_s)
    rs = wind_severer_rate_nasws(nass_array,unit = unit)
    return rs

def wind_severer_rate_uv(u_ob, u_fo, v_ob, v_fo, min_s = 0,max_s = 300,unit = 1):
    '''
    基于原始u，v风（m/s)数组，计算风速预报偏强率，计算的第一步是将预报和观测的风向都转换成14个离散的风速等级，
    当预报风速等级大于观测风速等级时记为1，否则记为0，偏强率是偏强的样本数/总样本数
    :param s_ob:观测的风向，numpy数组，
    :param s_fo:预报的风向，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param min_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :param max_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :return: 风向预报准确率，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    s_ob, d_ob = meteva.base.math_tools.u_v_to_s_d(u_ob, v_ob)
    s_fo, d_fo = meteva.base.math_tools.u_v_to_s_d(u_fo, v_fo)
    nass_array = nasws_s(s_ob, s_fo,min_s = min_s,max_s =max_s)
    rs = wind_severer_rate_nasws(nass_array,unit = unit)
    return rs

def wind_weaker_rate_nasws(nasws_array,unit = 1):
    '''
    基于中间结果计算风速预报偏弱率，
    :param nasd_array: 输入nasd函数统计得到的样本数、风速正确样本数、风速评分（分子部分），偏弱样本数，偏强样本数
    :return: 风速预报偏弱率
    '''
    total = nasws_array[...,0]
    sc = nasws_array[...,3]
    rw = sc/total
    if unit =="%":
        rw *= 100
    return rw

def wind_weaker_rate(s_ob,s_fo,min_s = 0,max_s = 300,unit = 1):
    '''
    基于原始风向数组，计算风速预报偏弱率，计算的第一步是将预报和观测的风向都转换成14个离散的风速等级，
    当预报风速等级小于观测风速等级时记为1，否则记为0，偏强率是偏弱的样本数/总样本数
    :param s_ob:观测的风向，numpy数组，
    :param s_fo:预报的风向，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param min_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :param max_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :return: 风速预报偏弱率，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    nass_array = nasws_s(s_ob, s_fo,min_s = min_s,max_s =max_s)
    rw = wind_weaker_rate_nasws(nass_array,unit=unit)
    return rw


def wind_weaker_rate_uv(u_ob, u_fo, v_ob, v_fo, min_s = 0,max_s = 300,unit = 1):
    '''
    基于原始风向数组，计算风速预报偏弱率，计算的第一步是将预报和观测的风向都转换成14个离散的风速等级，
    当预报风速等级小于观测风速等级时记为1，否则记为0，偏强率是偏弱的样本数/总样本数
    :param u_ob: 观测的u分量，numpy数组
    :param u_fo: 预报的u分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），u_fo.shape低维与u_ob.shape保持一致
    :param v_ob: 观测的u分量，numpy数组，shape 和u_ob完全一致
    :param v_fo: 预报的v分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），v_fo.shape低维与v_ob.shape保持一致
    :param min_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :param max_s:  过滤参数，当样本的预报或者观测的风速位于[min_s,max_s)区间时，会将样本纳入统计样本，否则会将样本删除
    :return: 风速预报偏弱率，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    s_ob, d_ob = meteva.base.math_tools.u_v_to_s_d(u_ob, v_ob)
    s_fo, d_fo = meteva.base.math_tools.u_v_to_s_d(u_fo, v_fo)
    nass_array = nasws_s(s_ob, s_fo,min_s = min_s,max_s =max_s)
    rw = wind_weaker_rate_nasws(nass_array,unit = unit)
    return rw


def na_ds(d_ob,d_fo,s_ob,s_fo):
    '''
    计算风预报综合检验所需的中间量。
        将输入的观测和预报风向（0-360度）和风速（m/s），转换成计算风预报综合准确率所需要的中间量，
        ，计算的第一步是将预报和观测的风向都转换成8个离散的方位角，将观测和预报的风速转换成等级
        :param d_ob:观测的风向，numpy数组
        :param s_ob:观测的风速，numpy数组，shape和d_ob完全一致
        :param d_fo:预报的风向，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
        :param s_fo:预报的风速，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
        :return:根据预报和观测的风向风速数据，统计得到的样本数、风向和风速都正确样本数，d_fo和d_ob的shape一致，则说明只有一家预报，此时返回
                 一维的数据，size= 2。 如果d_fo和d_ob的shape不一致，则说明有多个预报，则返回的数据shape = （预报成员数，2）
        '''
    Ob_shape = d_ob.shape
    Fo_shape = d_fo.shape
    nasd_list = []
    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('预报数据和观测数据维度不匹配')
        return
    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo_d = d_fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo_d.shape
    new_Fo_s = s_fo.reshape(new_Fo_shape)


    ob_d = meteva.base.tool.math_tools.tran_direction_to_8angle(d_ob)
    ob_s = meteva.base.tool.math_tools.tran_speed_to_14grade(s_ob)
    for line in range(new_Fo_shape[0]):
        fo_d = meteva.base.tool.math_tools.tran_direction_to_8angle(new_Fo_d[line, :])
        fo_s = meteva.base.tool.math_tools.tran_speed_to_14grade(new_Fo_s[line,:])
        nasd_array = np.zeros(2)
        nasd_array[0] = d_ob.size
        index = np.where((fo_d == ob_d)&(fo_s == ob_s))
        nasd_array[1] += len(index[0])
        nasd_list.append(nasd_array)
    nrag_array = np.array(nasd_list)
    shape = list(Fo_shape[:ind])
    shape.append(2)
    nrag_array = nrag_array.reshape(shape)
    return nrag_array


def na_uv(u_ob,u_fo,v_ob,v_fo):

    '''
    将输入的观测和预报u,v分量（m/s)，转换成计算风向预报准确率，风向预报评分所需要的中间量
    ，计算的第一步是将预报和观测的风向都转换成8个离散的方位角。
    :param u_ob: 观测的u分量，numpy数组
    :param u_fo: 预报的u分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），u_fo.shape低维与u_ob.shape保持一致
    :param v_ob: 观测的u分量，numpy数组，shape 和u_ob完全一致
    :param v_fo: 预报的v分量，numpy数组，shape和u_ob完全一致或比u_ob高一维（用于同时进行多家预报结果检验），v_fo.shape低维与v_ob.shape保持一致
    :return:根据预报和观测的风向风速数据，统计得到的样本数、风向和风速都正确样本数，d_fo和d_ob的shape一致，则说明只有一家预报，此时返回
                 一维的数据，size= 2。 如果d_fo和d_ob的shape不一致，则说明有多个预报，则返回的数据shape = （预报成员数，2）
    '''
    s_ob,d_ob = meteva.base.math_tools.u_v_to_s_d(u_ob,v_ob)
    s_fo,d_fo = meteva.base.math_tools.u_v_to_s_d(u_fo,v_fo)
    return na_ds(d_ob,d_fo,s_ob,s_fo)


def acz_na(na_array):
    '''
    基于中间结果计算风预报综合准确率，
    :param nrag_array: 输入nrag函数统计得到的样本数、风向风速都正确的样本数
    :return: 返回风预报综合准确率
    '''
    total = na_array[...,0]
    sc = na_array[...,1]
    ac = sc/total
    return ac

def acz(d_ob,d_fo,s_ob,s_fo):
    '''
    根据输入的观测和预报风向（0-360度）和风速（m/s），计算风雨吧综合准确率，
    ，计算的第一步是将预报和观测的风向都转换成8个离散的方位角，将观测和预报的风速转换成等级，
    观测预报的风向方位角一致且风速等级一致则记为正确，否则记为错误，风预报综合准确率= 正确样本数/总样本数
    :param d_ob:观测的风向，numpy数组
    :param s_ob:观测的风速，numpy数组，shape和d_ob完全一致
    :param d_fo:预报的风向，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param s_fo:预报的风速，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :return:返回风预报综合准确率，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    narg_array = na_ds(d_ob,d_fo,s_ob,s_fo)
    acz1 = acz_na(narg_array)
    return acz1

def acz_uv(u_ob,u_fo,v_ob,v_fo):
    '''
    根据输入的观测和预报u,v分量（m/s)，计算风预报综合准确率，
    ，计算的第一步是将预报和观测的风向都转换成8个离散的方位角，将观测和预报的风速转换成等级，
    观测预报的风向方位角一致且风速等级一致则记为正确，否则记为错误，风预报综合准确率= 正确样本数/总样本数
    :param d_ob:观测的风向，numpy数组
    :param s_ob:观测的风速，numpy数组，shape和d_ob完全一致
    :param d_fo:预报的风向，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :param s_fo:预报的风速，numpy数组，numpy可以比d_ob高一维（用于同时进行多家预报结果检验），fo.shape低维与ob.shape保持一致
    :return:返回风预报综合准确率，如果d_fo和d_ob的shape一致，说明只有一家预报，则返回实数，否则说明是在同时检验多家预报，返回结果为一维数组。
    '''
    s_ob,d_ob = meteva.base.math_tools.u_v_to_s_d(u_ob,v_ob)
    s_fo,d_fo = meteva.base.math_tools.u_v_to_s_d(u_fo,v_fo)
    narg_array = na_ds(d_ob,d_fo,s_ob,s_fo)
    acz1 = acz_na(narg_array)
    return acz1
