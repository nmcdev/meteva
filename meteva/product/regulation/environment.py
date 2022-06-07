import meteva
import pandas as pd
import numpy as np
import math
import datetime


def AQI_value_to_grade(value):
    '''
    将AQI的具体值转换成AQI的等级
    :param value: AQI的具体数值
    :return: AQI的等级
    '''
    grade = np.abs(value)
    grade[value<=50] = 1
    index = np.where(value>50&value<=100)
    grade[index] = 2
    index = np.where(value>100&value<=150)
    grade[index] = 3
    index = np.where(value>150&value<=200)
    grade[index] = 4
    index = np.where(value>200&value<=300)
    grade[index] = 5
    grade[value>300] =6
    return grade

def O3_value_to_grade(value):
    '''
    将O3的具体值转换成O3的等级
    :param value: O3的具体数值
    :return: O3的等级
    '''
    grade = np.abs(value)
    grade[value<=160] = 1
    index = np.where(value>160&value<=200)
    grade[index] = 2
    index = np.where(value>200&value<=300)
    grade[index] = 3
    index = np.where(value>300&value<=400)
    grade[index] = 4
    index = np.where(value>400&value<=800)
    grade[index] = 5
    grade[value>800] =6
    return grade

def PM25_value_to_grade(value):
    '''
    将PM2.5的具体值转换成PM2.5的等级
    :param value: PM2.5的具体数值
    :return: PM2.5的等级
    '''
    grade = np.abs(value)
    grade[value<=35] = 1
    index = np.where(value>35&value<=75)
    grade[index] = 2
    index = np.where(value>75&value<=115)
    grade[index] = 3
    index = np.where(value>115&value<=150)
    grade[index] = 4
    index = np.where(value>150&value<=250)
    grade[index] = 5
    grade[value>250] =6
    return grade

def AQI_comprehensive(AQI_primary_type_score,AQI_grade_score,AQI_value_score,O3_grade_score,PM25_grade_score=None):
    '''
    AQI预报综合评分按如下公式进行计算：
    S1=0.2f1+0.2f2+0.2f3+0.2f4+0.2f5（全年）
    S1=0.2f1+0.4f2+0.2f3+0.2f4（5至10月）

    :param AQI_primary_type_score:首要污染物预报准确率评分
    :param AQI_grade_score:AQI级别预报准确率评分
    :param AQI_value_score:AQI级别预报准确率评分
    :param O3_grade_score:AQI级别预报准确率评分
    :param PM25_grade_score:PM2.5等级预报准确率评分
    :return:AQI预报综合评分（取1位小数）
    '''
    if PM25_grade_score is None:
        s1 = 0.25 * AQI_primary_type_score + 0.25 * AQI_grade_score + 0.25 * AQI_value_score + 0.25 * O3_grade_score
    else:
        s1 = 0.2 * AQI_primary_type_score + 0.4 * AQI_grade_score + 0.2 * AQI_value_score + 0.2 * O3_grade_score +0.2 * PM25_grade_score
    score = round(s1, 1)
    return score


def AQI_primary_type_score(ob_type,fo_type):
    '''
    计算首要污染物类型评分
    :param ob_type:  N×6的矩阵， N代表站点，考虑到首要污染物可能同时有多种，因此对于一个站点，用6个数字来表示首要污染物的类型
    6个数字的依次代表SO2,NO2,PM10,CO,O3,PM2.5是否为首要污染物，例如[0,1,0,0,1,0]代表首要污染物是PM10和O3。
    :param fo_type: 形式和观测相同
    :return: 首要污染物类型预报评分
    '''
    correct_rate = AQI_primary_type_correct_rate(ob_type,fo_type)
    score = correct_rate * 100
    return score


def grade_score(ob_grade,fo_grade):
    '''
    适用于计算AQI等级预报评分、O3等级预报评分和PM2.5等级预报评分
    :param ob_grade:  观测的等级
    :param fo_grade:  预报的等级
    :return: 等级预报评分
    '''
    grade_error = np.abs(ob_grade - fo_grade)
    score = np.zeros(grade_error.shape)
    score[grade_error==0] = 100
    score[grade_error==1] = 50
    score[grade_error==2] = 25
    score_mean = np.mean(score)
    return score_mean

def AQI_value_score(ob_value,fo_value):
    '''
    计算AQI 数值预报误差评分
    :param ob_value: AQI观测值
    :param fo_value: AQI预报值
    :return:
    '''

    error = np.abs(ob_value - fo_value)
    score = np.zeros(error.shape)
    score[error<=25] = 100
    index = np.where(error>25&error<=50)
    score[index] = 80
    index = np.where(error>50&error<=100)
    score[index] = 60
    index = np.where(error>100&error<=150)
    score[index] = 30
    score_mean = np.mean(score)
    return score_mean


def AQI_primary_type_correct_rate(ob_type,fo_type):
    '''
    计算首要污染物类型准确率
    :param ob_type:  N×6的矩阵， N代表站点，考虑到首要污染物可能同时有多种，因此对于一个站点，用6个数字来表示首要污染物的类型
    6个数字的依次代表SO2,NO2,PM10,CO,O3,PM2.5是否为首要污染物，例如[0,1,0,0,1,0]代表首要污染物是PM10和O3。
    :param fo_type: 形式和观测相同
    :return: 首要污染物类型准确率
    '''
    error = np.sum(np.abs(ob_type - fo_type))
    score = np.zeros(error.shape)
    score[error ==0] = 1 # 首要污染物完全一致是评分为1

    cross = ob_type * fo_type
    cross_sum = np.sum(cross,axis = -1)
    score[cross_sum>0] = 1  # 观测预报点积大于0，说明至少命中了1种
    score_mean = np.mean(score)
    return score_mean


def grade_correct_rate(ob_grade,fo_grade):
    '''
     适用于计算AQI等级准确率、O3等级准确率和PM2.5等级准确率
    :param ob_grade:  观测的等级
    :param fo_grade:  预报的等级
    :return: 等级准确率
    '''
    cr = meteva.method.correct_rate(ob_grade,fo_grade,grade_list=[0.5])
    return cr


def AQI_comprehensive_skill(AQI_primary_type_skill,AQI_grade_skill,O3_grade_skill,PM25_grade_skill=None):
    '''
    AQI预报综合评分技巧如下公式进行计算：
      S2=0.2*f6+0.4*f7+0.2*f8+0.2*f9（全年）
      S2=0.3*f6+0.4*f7+0.3*f8（5至10月）
    :param AQI_primary_type_skill:首要污染物预报准确率技巧
    :param AQI_grade_skill:AQI级别预报准确率技巧
    :param O3_grade_skill:O3级别预报准确率评分
    :param f9:PM2.5级别预报准确率技巧
    :return:
    '''
    if PM25_grade_skill is None:
        s2 = 0.3 * AQI_primary_type_skill + 0.4 * AQI_grade_skill + 0.3 * O3_grade_skill
    else:
        s2 = 0.2 * AQI_primary_type_skill + 0.4 * AQI_grade_skill + 0.2 * O3_grade_skill + 0.2 * PM25_grade_skill

    score = round(s2, 1)
    return score


def skill_of_province_to_nmc(correct_rate_nmc,correct_rate_province):
    '''
    适用于计算省台的AQI首要污染物类型准确率、AQI等级准确率、O3等级准确率或PM2.5等级准确率相对于中央台的技巧
    适用于单个站次上的技巧值，也适用于多个站次（多个时刻或多个站点）上平均的技巧值。
    :param correct_rate_nmc: 中央台的准确率
    :param correct_rate_province: 省台的准确率。
    :return:
    '''
    skill = correct_rate_province - correct_rate_nmc
    return skill


def mean_of_AQI_comprehensive_in_short_range(TTk24,TTk48,TTk72):
    '''

    :param score24:
    :param score48:
    :param score72:
    :return:
    '''
    TT = 0.5 * TTk24 + 0.3 * TTk48 + 0.2 * TTk72
    return TT




if __name__ == "__main__":
    import xarray as xr
    import pandas as pd
    path = r"\\10.20.73.112\hjhss\grid\MME\2022051820\AQI_sites_2564_2022051820.nc"
    dat = xr.open_dataset(path)
    print(dat)
    dtime = dat["time"].values
    lon = dat["sites_lon"].values
    lat = dat["sites_lat"].values
    AQI = dat["AQI"].values.flatten()
    CO = dat["CO"].values.flatten()
    NO2 = dat["NO2"].values.flatten()
    O3 = dat["O3"].values.flatten()
    PM10 = dat["PM10"].values.flatten()
    PM25 = dat["PM25"].values.flatten()
    SO2 = dat["SO2"].values.flatten()
    site = np.arange(len(lon))+1
    dtime_site = np.expand_dims(dtime,1).repeat(len(lon),axis=1).flatten()
    dtime_lon = np.expand_dims(lon,0).repeat(len(dtime),axis=0).flatten()
    dtime_lat = np.expand_dims(lat,0).repeat(len(dtime),axis=0).flatten()
    dtime_id = np.expand_dims(site,0).repeat(len(dtime),axis=0).flatten()
    df = pd.DataFrame({"dtime":dtime_site,"id":dtime_id,"lon":dtime_lon,"lat":dtime_lat,"AQI":AQI,
                       "CO":CO,"NO2":NO2,"O3":O3,"PM10":PM10,"PM25":PM25,"SO2":SO2})
    sta = meteva.base.sta_data(df)
    sta["time"] = datetime.datetime(2022,5,18,20)
    sta["level"] = 0

    sta_part = meteva.base.sele_by_para(sta,dtime = 24)
    meteva.base.scatter_sta(sta_part,save_path=r"H:\test_data\a.png",subplot="member")


