import copy
import os
import numpy as np
import traceback
import pandas as pd
import datetime
import meteva

def write_stadata_to_micaps3(sta0,save_path = "a.txt",creat_dir = False, type = -1,effectiveNum = 4,show = False):
    """
    生成micaps3格式的文件
    :param sta0:站点数据信息
    :param save_path 需要保存的文件路径和名称
    :param type 类型：默认：1
    :param effectiveNum 有效数字 默认为：4
    :return:保存为micaps3格式的文件
    """
    try:
        sta = copy.deepcopy(sta0)
        dir = os.path.split(os.path.abspath(save_path))[0]
        if not os.path.isdir(dir):
            if not creat_dir:
                print("文件夹：" + dir + "不存在")
                return False
            else:
                meteva.base.tool.path_tools.creat_path(save_path)

        br = open(save_path,'w')
        end = len(save_path)
        start = max(0, end-16)
        nsta =len(sta.index)
        time = sta['time'].iloc[0]
        if isinstance(time,np.datetime64) or isinstance(time,datetime.datetime):
            time_str = meteva.base.tool.time_tools.time_to_str(time)
            time_str = time_str[0:4] + " " +time_str[4:6] + " " + time_str[6:8] + " " + time_str[8:10] + " "
        else:
            time_str = "2099 01 01 0 0 "

        if np.isnan(sta['level'].iloc[0]):
            level = 0
        else:
            level = int(sta['level'].iloc[0])
        if type<0 or level == np.NaN or level ==pd.NaT:
            level = int(type)

        str1=("diamond 3 " + save_path[start:end] + "\n"+ time_str + str(level) +" 0 0 0 0\n1 " + str(nsta) + "\n")
        br.write(str1)
        br.close()
        data_name = meteva.base.basicdata.get_stadata_names(sta)[0]
        df = copy.deepcopy(sta[['id','lon','lat',data_name]])
        df['alt'] = 0
        df = df.reindex(columns = ['id','lon','lat','alt',data_name])
        effectiveNum_str = "%." + '%d'% effectiveNum + "f"
        df.to_csv(save_path,mode='a',header=None,sep = "\t",float_format=effectiveNum_str,index = None)
        if show:
            print('Create [%s] success' % save_path)
        return True
    except:
        exstr = traceback.format_exc()
        print(exstr)
        return False

