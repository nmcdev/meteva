import numpy as np

def cr(ob,fo,grade_list=[1e-30],compair = ">="):
    '''
    cr指数，代表集合成员集中且于观测一致的程度，即所有成员及观测在某个阈值以上的落区的交集与并集的比值
    :param ob:实况数据 一维的numpy
    :param fo:预测数据 二维的numpy数组
    :param grade_list:多个阈值同时检验时的等级参数
    :return: 一维numpy数组，其中每个元素为0-1的实数，最优值为1
    '''
    #print(fo.shape)
    if compair not in [">=",">","<","<="]:
        print("compair 参数只能是 >=   >  <  <=  中的一种")
        return
    rmse_list = []
    Fo_shape = fo.shape
    Ob_shape = ob.shape

    Ob_shpe_list = list(Ob_shape)
    size = len(Ob_shpe_list)
    ind = -size
    Fo_Ob_index = list(Fo_shape[ind:])
    if Fo_Ob_index != Ob_shpe_list:
        print('实况数据和观测数据维度不匹配')
        return

    Ob_shpe_list.insert(0, -1)
    new_Fo_shape = tuple(Ob_shpe_list)
    new_Fo = fo.reshape(new_Fo_shape)
    new_Fo_shape = new_Fo.shape


    cr_list = []
    grade_num = len(grade_list)
    ensemble_num = new_Fo_shape[0]
    intersecti = np.zeros_like(ob)
    union = np.zeros_like(ob)

    for g in range(grade_num):
        ob1 = np.zeros_like(ob)
        if compair == ">=":
            ob1[ob >=grade_list[g]] = 1
        elif compair == "<=":
            ob1[ob <=grade_list[g]] = 1
        elif compair == ">":
            ob1[ob > grade_list[g]] = 1
        elif compair == "<":
            ob1[ob < grade_list[g]] = 1



        intersecti[:] = ob1[:]
        union[:] = ob1[:]
        for i in range(ensemble_num):
            fo1 = np.zeros_like(ob)
            if compair == ">=":
                fo1[fo[i,:] >= grade_list[g]] = 1
            elif compair == "<=":
                fo1[fo[i, :] <= grade_list[g]] = 1
            elif compair == ">":
                fo1[fo[i, :] > grade_list[g]] = 1
            elif compair == "<":
                fo1[fo[i, :] < grade_list[g]] = 1

            intersecti[:] = intersecti[:] * fo1[:]
            union[:] = union[:] + fo1[:]
        union[union>0] = 1
        union_num = np.sum(union)
        intersecti_num = np.sum(intersecti)
        cr1 = intersecti_num/(union_num + 1e-30)
        cr_list.append(cr1)
    if len(cr_list)>1:
        crs = np.array(cr_list)
    else:
        crs = cr_list[0]
    return crs


def crps(Ob, Fo):
    '''

    :param Ob:
    :param Fo:
    :return:
    '''
    n = Ob.size
    shape0 = Fo.shape
    m = shape0[0]
    ob0 = Ob.flatten()
    fo0 = Fo.reshape((m, n))
    fo0 = np.sort(fo0)
    minv = min(np.min(ob0), np.min(fo0))
    maxv = max(np.max(ob0), np.max(fo0))

    fo1 = np.zeros((m + 2, n))
    fo1[0, :] = minv
    fo1[1:-1, :] = fo0[:, :]
    fo1[-1, :] = maxv

    crps0 = np.zeros(n)
    for i in range(1, m + 1):
        a = np.zeros(n)
        index1 = np.where((fo1[i, :] < ob0) & (fo1[i + 1] >= ob0))
        a[index1] = ob0[index1] - fo1[i, index1]

        index2 = np.where(fo1[i + 1] < ob0)
        a[index2] = fo1[i + 1, index2] - fo1[i, index2]

        crps0 += a * ((i / m) * (i / m))

    for i in range(0, m):
        b = np.zeros(n)
        index1 = np.where(ob0 <= fo1[i])
        b[index1] = fo1[i + 1, index1] - fo1[i, index1]

        index2 = np.where((fo1[i, :] < ob0) & (fo1[i + 1] >= ob0))
        b[index2] = fo1[i + 1, index2] - ob0[index2]

        crps0 += b * ((1 - i / m) * (1 - i / m))

    crps_mean = np.mean(crps0)
    return crps_mean
