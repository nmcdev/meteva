import nmc_verification
import numpy as np

def accuracy(ob, fo, grade_list=None):
    '''
    accuracy 求多分类预报准确率
    :param ob: 实况数据 不确定维numpy
    :param fo:  预测数据 不确定维numpy
    :param grade_list:等级，如果grade_list= None则ob和fo里的值代表类别，否则，根据grade_list来进行分类
    :return:
    '''
    # 多分类预报准确率
    if grade_list is None:
        # ob 和fo是不确定维的numpy数组，其中每个值是代表分类的类别
        ob1 = ob.reshape((-1))
        fo1 = fo.reshape((-1))
    else:
        ob1 = np.zeros_like(ob)
        fo1 = np.zeros_like(fo)
        # ob 和fo 是连续的变量，通过 threshold_list 将ob 和fo划分成连续的等级之后再计算等级准确性
        for index in range(len(grade_list) - 1):
            ob_index_list = np.where((grade_list[index] <= ob) & (ob < grade_list[index + 1]))
            ob1[ob_index_list] = index+1
            fo_index_list = np.where((grade_list[index] <= fo) & (fo < grade_list[index + 1]))
            fo1[fo_index_list] = index+1
        ob_index_list = np.where(grade_list[-1] <= ob)
        ob1[ob_index_list] = len(grade_list)
        fo_index_list = np.where(grade_list[-1] <= fo)
        fo1[fo_index_list] = len(grade_list)
    correct_num = np.sum(fo1 == ob1)
    accuracy_score = correct_num / ob.size
    return accuracy_score

def hss(ob,fo,grade_list = None):
    '''
    hss heidke技能得分,它表现实际的预报的分类准确性相对于随机分类达到的准确性的技巧
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :return:
    '''
    conf_mx = nmc_verification.nmc_vf_method.multi_category.table.contingency_table(ob,fo,grade_list)
    accuracy_score = accuracy(ob, fo, grade_list)
    total_num = ob.size
    NF_array = conf_mx[0:-1,-1]
    NO_array = conf_mx[-1,0:-1]
    random_score = np.dot(NF_array,NO_array) /(total_num * total_num)
    HSS = (accuracy_score - random_score)/(1 - random_score)
    return HSS



def hk(ob, fo, grade_list=None):
    '''
    hk Hanssen和Kuipers判别
    :param ob: 实况数据 一维numpy
    :param fo: 预测数据 一维numpy
    :param grade_list: 等级
    :return:
    '''
    # 多分类预报hk技巧评分

    conf_mx = nmc_verification.nmc_vf_method.multi_category.table.contingency_table(ob,fo,grade_list)
    accuracy_score = accuracy(ob, fo, grade_list)
    total_num = ob.size
    NF_array = conf_mx[0:-1,-1]
    NO_array = conf_mx[-1,0:-1]
    random_score = np.dot(NF_array,NO_array) /(total_num * total_num)
    ob_rate = np.dot(NO_array,NO_array)/(total_num * total_num)
    HK = (accuracy_score - random_score)/(1 - ob_rate)

    return HK


