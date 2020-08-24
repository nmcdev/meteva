import meteva
import pandas as pd


def p2p_vto01(sta_all,threshold = 1e-30,compair = ">="):
    '''

    :param sta_fo_all: 将预报数据处理成0-1数据
    :param threshold: 大于等于该阈值参数的站点值将转换成1，否则转换成0，缺省值仍然保持为缺省值
    :return:
    '''
    if compair not in [">=",">","<","<="]:
        print("compair 参数只能是 >=   >  <  <=  中的一种")
        return

    sta_happen_all = sta_all.copy()
    fo_names = meteva.base.get_stadata_names(sta_all)

    if isinstance(threshold,pd.DataFrame):
        sta_compair = meteva.base.combine_expand_IV(sta_happen_all,threshold)
        for i in range(len(fo_names)):
            name = fo_names[i]
            if compair == ">=":
                sta_happen_all.loc[:,name] = 0 + (sta_compair.loc[:,name] >= sta_compair.iloc[:,-1])
            elif compair =="<=":
                sta_happen_all.loc[:, name] = 0 + (sta_compair.loc[:, name] <= sta_compair.iloc[:, -1])
            elif compair ==">":
                sta_happen_all.loc[:, name] = 0 + (sta_compair.loc[:, name] > sta_compair.iloc[:, -1])
            else:
                sta_happen_all.loc[:, name] = 0 + (sta_compair.loc[:, name] < sta_compair.iloc[:, -1])


            sta_happen_all.loc[sta_compair.loc[:,name] == meteva.base.IV, name] = meteva.base.IV
    else:
        for i in range(len(fo_names)):
            name = fo_names[i]
            if compair == ">=":
                sta_happen_all.loc[:,name] = 0 + (sta_happen_all.loc[:,name] >= threshold)
            elif compair ==">":
                sta_happen_all.loc[:,name] = 0 + (sta_happen_all.loc[:,name] > threshold)
            elif compair =="<=":
                sta_happen_all.loc[:,name] = 0 + (sta_happen_all.loc[:,name] <= threshold)
            else:
                sta_happen_all.loc[:,name] = 0 + (sta_happen_all.loc[:,name] < threshold)
            sta_happen_all.loc[sta_all[name] == meteva.base.IV, name] = meteva.base.IV
    return sta_happen_all


def p2a_vto01(sta_all,r = 40,threshold = 1e-30,compair = ">="):
    '''

    :param sta_ob_all: 原始输入的观测站点数据,其中可以包含多个时刻的观测数据
    :param r: 临域半径，默认值为40km
    :param threshold: 半径璠r范围内观测值大于threshold的样本记为发生。
    :return: 采用临域法处理后的观测数据,其站点列表和sta_ob_all 一致
    '''

    # 将sta_ob_all 拆解成一个列表，列表中的每个元素为仅包含单个时刻观测的站点数据
    sta_all_01 = p2p_vto01(sta_all,threshold=threshold,compair = compair)
    sta_01_list = meteva.base.split(sta_all_01)
    npic = len(sta_01_list)
    sta_hapend_list = []
    for i in range(npic):
        sta_one = sta_01_list[i]                        # 提取单个时刻的观测数据
        sta_one_no_iv = meteva.base.not_IV(sta_one)     # 将其中的缺省数据删除
        #对于sta_one中的每个点，从不包含缺省值的数据sta_one_no_iv中找到半径r范围内的最大值
        #查询结果sta_happen的站点顺序和sta_one 一致
        sta_happen = meteva.base.max_in_r_of_sta(sta_one,r = r, sta_from = sta_one_no_iv)
        sta_hapend_list.append(sta_happen)
    sta_happen_all = pd.concat(sta_hapend_list,axis=0)
    return sta_happen_all



def sta_ob_fos_to_01(sta_of,sta_fo_list = None,r = 40, threshold_ob = 1e-30, threhold_fo = 1e-30):
    if sta_fo_list is None:
    # 将观测转为dtim0 = 0的形式
        data_names = meteva.base.get_stadata_names(sta_of)
        sta_ob = meteva.base.sele_by_para(sta_of, member=[data_names[0]])
        dhours = sta_ob["dtime"].values
        sta_ob = meteva.base.move_fo_time(sta_ob,dhours)
        sta_ob = sta_ob.drop_duplicates()
        sta_ob_01 = p2a_vto01(sta_ob,r= r,threshold = threshold_ob)
        sta_fo = meteva.base.sele_by_para(sta_of, member=[data_names[0]])
        sta_fo_01 = p2p_vto01(sta_fo,threshold= threhold_fo)
        sta_all_01 = meteva.base.combine_on_obTime_id(sta_ob_01,sta_fo_01)
    else:
        sta_ob_01 = p2a_vto01(sta_of, r=r, threshold=threshold_ob)
        sta_fo_01_list =[]
        for sta_fo in sta_fo_list:
            sta_fo_01 = p2p_vto01(sta_fo,threshold= threhold_fo)
            sta_fo_01_list.append(sta_fo_01)
        sta_all_01 = meteva.base.combine_on_obTime_id(sta_ob_01,sta_fo_01_list)
    return sta_all_01

