import numpy as np
import pandas as pd
import copy
import itertools
import  read
import  sta_data1

def screen(dframe, condits):
    # condits={'time':{'iscont':'cont','type':'fould','data':[50246,50247,50349]}}
    dframe0 = copy.deepcopy(dframe)
    dframe0['time'] = pd.to_datetime(dframe0['time'],infer_datetime_format=True)
    df_list = []
    if 'time' in condits:
        if condits['time']['iscont'] != 'cont': # 判断time筛选条件是否为连续
            con_data = condits['time']['data'] #取出时间筛选条件
            for  key in con_data:
                con_data[key].update(iscont='uncont') # 给散点时间筛选条件加一个元素为不连续
                condits.update({key:con_data[key]}) # 并将新的筛选条件放到筛选条件字典中
            condits.pop('time')# 将time弹出
            # 加入几列
            dframe0['year'] = dframe0['time'].dt.year
            dframe0['month'] = dframe0['time'].dt.month
            dframe0['day'] = dframe0['time'].dt.day
            dframe0['hour'] = dframe0['time'].dt.hour
    dframe0.set_index("time", inplace=True)

    sizes = []  # 每个筛选条件的长度
    vals = []  # 存放筛选条件列表的列表
    isconts = []  # 存放筛选条件是连续 还是散点的列表
    for key in condits:
        #求出size？？？
        con_data = condits[key]
        isconts.append(con_data['iscont'])
        type = con_data['type']
        if type == 'fould':
            val = [list(dframe[:, key])]

        elif type == 'unfould':
            val = [list(dframe[:, key])]

        else:
            val = con_data['data']
        vals.append(val)
    vals = tuple(vals)
    filter_sets = []

    for filter_set  in itertools.product(vals):
        filter_set = list(filter_set)
    #     filter_sets.append(filter_set)
    #
    # for filter_set in  filter_sets :
        dframe1 = copy.deepcopy(dframe0)
        for single,key,iscont in zip(filter_set,condits,isconts):
            if iscont == 'cont':

                dframe1 = dframe1.loc[dframe1[key].isin(single)]

            else:
                if 'time' == key:
                    dframe1 = dframe1[single[0]:single[1]]
                else:
                    dframe1 = dframe1.loc[(dframe1[key] < single[1])]
                    dframe1 = dframe1.loc[single[0] < dframe1[key]]
        df_list.append(dframe1)
        print(df_list)



if __name__ == '__main__':
    filename = 'D:\work\ku\/2019010103.000'
    sta = read.read_from_micaps3(filename=filename,columns=['lon','lat','data'])
    print(sta)
    a = sta_data1.sta_data(sta, ['sta', 'lon', 'lat', 'data', 'level', 'time', 'dtime'])
    print(a)
    # condits={'time':{'iscont':'cont','type':'fould','data':[50246,50247,50349]}}
    screen(a,{'sta':{'iscont':'cont','type':'other','data':[50246,50247,50349]}})






    # # time = condits['time']  # 将time数据拿出来
    # condits.pop('time')
    # for key in condits:
    #     # sizes.append(len(condits[key]))#求出数据的size
    #     con_data = condits[key]
    #     isconts.append(con_data['iscont'])
    #     type = con_data['type']
    #     vals = []
    #     val = None
    #     if type != 'unfould':
    #         val = [list(dframe[:, key])]
    #         val = con_data['data']
    #     elif type == 'unfould':
    #         val = list(dframe[:, key])
    #         val = np.array(val)
    #         val = val.reshape(val.shape[0], 1)
    #     else:
    #         val = con_data['data']
    #     vals.append(val)


