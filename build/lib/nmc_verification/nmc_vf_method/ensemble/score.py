import numpy as np

def cr(ob,fo,grade_list=[1e-300]):
    '''

    :param ob:
    :param fo:
    :param grade_list:
    :return:
    '''
    cr_list = []
    grade_num = len(grade_list)
    ensemble_num = fo.shape[1]
    intersecti = np.zeros_like(ob)
    union = np.zeros_like(ob)
    for g in range(grade_num):
        ob1 = np.zeros_like(ob)
        ob1[ob >=grade_list[g]] = 1
        intersecti[:] = ob1[:]
        union[:] = ob1[:]
        for i in range(ensemble_num):
            fo1 = np.zeros_like(ob)
            fo1[fo[:,i] >= grade_list[g]] = 1
            intersecti[:] = intersecti[:] * fo1[:]
            union[:] = union[:] + fo1[:]
        union[union>0] = 1
        union_num = np.sum(union)
        intersecti_num = np.sum(intersecti)
        cr1 = intersecti_num/(union_num + 1e-30)
        cr_list.append(cr1)
    crs = np.array(cr_list)
    return crs

'''
fo = np.random.rand(10000,4)
ob = np.random.rand(10000)

crs = cr(ob,fo,[0.1,0.5,0.8])
print(crs)
'''
