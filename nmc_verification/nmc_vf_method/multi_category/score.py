import nmc_verification
import numpy as np

def accuracy(ob, fo, grade_list=None):
    '''
    accuracy 求多分类预报准确率
    :param ob: 实况数据 不确定维numpy
    :param fo:  预测数据 不确定维numpy
    :param grade_list:等级，如果grade_list= None则ob和fo里的值代表类别，否则，根据grade_list来进行分类
    :return: 0-1的实数，0代表无技巧，最优预报为1
    '''
    total_count, correct_count = total_and_correct_count(ob,fo,grade_list)
    accuracy_score = correct_count / total_count
    return accuracy_score

def accuracy_tc(tc_list):
    tc_array = np.array(tc_list)
    tc_array_sum = np.sum(tc_array,axis=0)
    total_count = tc_array_sum[0]
    correct_count = tc_array_sum[1]
    accuracy_score = correct_count / total_count
    return accuracy_score

def total_and_correct_count(ob, fo, grade_list=None):
    '''
    accuracy 求多分类预报准确率
    :param ob: 实况数据 不确定维numpy
    :param fo:  预测数据 不确定维numpy
    :param grade_list:等级，如果grade_list= None则ob和fo里的值代表类别，否则，根据grade_list来进行分类
    :return: 返回python 元组数据（总样本数，正确数）
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
    return ob.size, correct_num

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

def hk_tcof(tcof_list):
    tc_list = []
    cc_list = []
    obn_list = []
    fon_list = []
    for tsof in tcof_list:
        tc_list.append(tsof[0])
        cc_list.append(tsof[1])
        obn_list.append(tsof[2])
        fon_list.append(tsof[3])
    tc_array = np.array(tc_list)
    cc_array = np.array(cc_list)
    obn_array = np.array(obn_list)
    fon_array = np.array(fon_list)
    #print(tc_array)
    tc_sum = np.sum(tc_array)
    cc_sum = np.sum(cc_array)
    obn_sum = np.sum(obn_array,axis=0)
    fon_sum = np.sum(fon_array,axis=0)
    accuracy_score = cc_sum/tc_sum
    random_score = np.dot(fon_sum,obn_sum) /(tc_sum * tc_sum)
    ob_rate = np.dot(obn_sum,obn_sum) /(tc_sum * tc_sum)
    HK = (accuracy_score - random_score)/(1 - ob_rate)
    return HK

def hss_tcof(tcof_list):
    tc_list = []
    cc_list = []
    obn_list = []
    fon_list = []
    for tsof in tcof_list:
        tc_list.append(tsof[0])
        cc_list.append(tsof[1])
        obn_list.append(tsof[2])
        fon_list.append(tsof[3])
    tc_array = np.array(tc_list)
    cc_array = np.array(cc_list)
    obn_array = np.array(obn_list)
    fon_array = np.array(fon_list)
    tc_sum = np.sum(tc_array)
    cc_sum = np.sum(cc_array)
    obn_sum = np.sum(obn_array,axis=0)
    fon_sum = np.sum(fon_array,axis=0)
    accuracy_score = cc_sum/tc_sum
    random_score = np.dot(fon_sum,obn_sum) /(tc_sum * tc_sum)
    HSS = (accuracy_score - random_score)/(1 - random_score)
    return HSS

def tcof(ob,fo,grade_list = None):
    total_count, correct_count = total_and_correct_count(ob, fo, grade_list)
    conf_mx = nmc_verification.nmc_vf_method.multi_category.table.frequency_table(ob, fo, grade_list)
    obn_array = conf_mx[0,:]
    fon_array = conf_mx[1,:]
    return total_count,correct_count,obn_array,fon_array