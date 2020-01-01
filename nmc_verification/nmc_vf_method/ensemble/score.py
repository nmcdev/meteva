import numpy as np

def cr(ob,fo,grade_list=[1e-300]):
    '''
    cr指数，代表集合成员集中且于观测一致的程度，即所有成员及观测在某个阈值以上的落区的交集与并集的比值
    :param ob:实况数据 一维的numpy
    :param fo:预测数据 二维的numpy数组
    :param grade_list:多个阈值同时检验时的等级参数
    :return: 一维numpy数组，其中每个元素为0-1的实数，最优值为1
    '''
    cr_list = []
    grade_num = len(grade_list)
    ensemble_num = fo.shape[0]
    intersecti = np.zeros_like(ob)
    union = np.zeros_like(ob)
    for g in range(grade_num):
        ob1 = np.zeros_like(ob)
        ob1[ob >=grade_list[g]] = 1
        intersecti[:] = ob1[:]
        union[:] = ob1[:]
        for i in range(ensemble_num):
            fo1 = np.zeros_like(ob)
            fo1[fo[i,:] >= grade_list[g]] = 1
            intersecti[:] = intersecti[:] * fo1[:]
            union[:] = union[:] + fo1[:]
        union[union>0] = 1
        union_num = np.sum(union)
        intersecti_num = np.sum(intersecti)
        cr1 = intersecti_num/(union_num + 1e-30)
        cr_list.append(cr1)
    crs = np.array(cr_list)
    return crs


