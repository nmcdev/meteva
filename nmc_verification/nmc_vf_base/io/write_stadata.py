import copy
import os
import numpy as np
import traceback
import pandas as pd
import datetime
import nmc_verification

def write_to_micaps3(sta0,filename = "a.txt", type = 1,effectiveNum = 4):
    """
    生成micaps3格式的文件
    :param sta0:站点数据信息
    :param filename 需要保存的文件路径和名称
    :param type 类型：默认：1
    :param effectiveNum 有效数字 默认为：4
    :return:保存为micaps3格式的文件
    """
    try:
        sta = copy.deepcopy(sta0)
        dir = os.path.split(os.path.abspath(filename))[0]
        if os.path.isdir(dir):
            br = open(filename,'w')
            end = len(filename)
            start = max(0, end-16)
            nsta =len(sta.index)
            time = sta['time'].iloc[0]
            if isinstance(time,np.datetime64) or isinstance(time,datetime.datetime):
                time_str = nmc_verification.nmc_vf_base.method.time_tools.time_to_str(time)
                time_str = time_str[0:4] + " " +time_str[4:6] + " " + time_str[6:8] + " " + time_str[8:10] + " "
            else:
                time_str = "2099 01 01 0 0 "

            level = int(sta['level'].iloc[0])
            if type<0 or level == np.NaN or level ==pd.NaT:
                level = int(type)

            str1=("diamond 3 " + filename[start:end] + "\n"+ time_str + str(level) +" 0 0 0 0\n1 " + str(nsta) + "\n")
            br.write(str1)
            br.close()
            data_name = nmc_verification.nmc_vf_base.basicdata.get_data_names(sta)[0]
            df = sta[['id','lon','lat','alt',data_name]]
            effectiveNum_str = "%." + '%d'% effectiveNum + "f"
            df.to_csv(filename,mode='a',header=None,sep = "\t",float_format=effectiveNum_str,index = None)

    except (Exception, BaseException) as e:
        exstr = traceback.format_exc()
        print(exstr)
        return None
