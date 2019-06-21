import numpy as np

def accuracy(ob,fo,grade_list = None):
    '''
    accuracy 求多分类预报准确率
    :param ob: 实况数据 一维numpy
    :param fo:  预测数据 一维numpy
    :param grade_list:等级
    :return:
    '''
    #多分类预报准确率
    if grade_list is None:
        #ob 和fo是n×1的numpy数组，其中每个值是代表分类的类别，如果能够兼容字符型更

        ob1 = ob.reshape((-1))
        fo1 = fo.reshape((-1))
    else:
        # ob 和fo 是连续的变量，通过 threshold_list 将ob 和fo划分成连续的等级之后再计算等级准确性
        ob1 = None #此处需修改
        fo1 = None #此处需修改

    ob_len = len(ob1)
    true_num = 0

    #为了提高计算效率，此处需修改为不用循环的方式实现计算，后续其他开发也需要如此
    for i in range(ob_len):
        if ob1[i] == fo1[i]:
            true_num += 1
    accuracy_score = true_num / ob_len
    return accuracy_score

def hss(ob,fo,grade_list = None):
    '''
    hss heidke技能得分
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :return:
    '''
    #参考accuracy 做扩展修改

    accuracy_score = accuracy(ob,fo,grade_list)
    ob_len = len(ob)
    ob1 = ob.reshape((-1))
    fo1 = fo.reshape((-1))
    ob2 = set(ob1)
    fo2 = set(fo1)
    results  = list(ob2|fo2)


    f_mult_o_sum = 0

    for result in results:
        NF = np.sum(ob1 == result)
        NO = np.sum(fo1 == result )
        f_mult_o = NF*NO
        f_mult_o_sum += f_mult_o
    n_2 = ob_len**2
    HSS = (accuracy_score - (f_mult_o_sum/n_2))/(1-f_mult_o_sum/n_2)
    return  HSS

def hk(ob,fo,grade_list = None):
    '''
    hk Hanssen和Kuipers判别
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :return:
    '''
    # 多分类预报hss技巧评分

    # 参考accuracy 做扩展修改

    accuracy_score = accuracy(ob, fo)
    ob_len = len(ob)
    ob1 = ob.reshape((-1))
    fo1 = fo.reshape((-1))
    ob2 = set(ob1)
    fo2 = set(fo1)
    results = list(ob2 | fo2)
    f_mult_o_sum = 0
    No_2_sum = 0

    for result in results:
        NO = np.sum(ob1 == result)
        NF = np.sum(fo1 == result)
        f_mult_o = NF * NO
        f_mult_o_sum += f_mult_o
        No_2_sum +=  NO**2
    N_2 = ob_len ** 2
    HK_score = (accuracy_score- (f_mult_o_sum/N_2))/(1-No_2_sum/N_2)
    return  HK_score
