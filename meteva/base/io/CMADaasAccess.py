#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: CMADaasAccess.py

'''
Created on Sep 15, 2020

@author: anduin
'''
import meteva
import datetime
import json
from .loglib import *
from .httpconn import HttpConn
from .SignGenUtil import SignGenUtil
import numpy as np

class CMADaasAccess():
    """description of class 
    cmadaas data access
    """    
    @staticmethod
    def get_times(dts):       
        try:
            if type(dts) is list:
                return ','.join(dt.strftime('%Y%m%d%H%M%S') for dt in dts)
            else:
                return dts.strftime('%Y%m%d%H%M%S')
        except Exception as data:
            #print(str(data))           
            LogLib.error('CMADaasAccess get_times except %s %s' % (str(dts), str(data)))
            raise data
            #return None
    
    @staticmethod
    def set_times_in_params(dts, params, deep_copy=True):
        try:
            rst = params
            if deep_copy:
                import copy
                rst = copy.deepcopy(params)

            rst['times'] = CMADaasAccess.get_times(dts)

            return rst
        except Exception as data:
            #print(str(data))
            LogLib.error('CMADaasAccess set_times_in_params except %s %s' % (str(dts), str(data)))
            raise data
            #return None
    
    @staticmethod
    def get_timerange(dts):
        try:
            rst = ''
            if type(dts) is list:
                rst = ','.join(dt.strftime('%Y%m%d%H%M%S') for dt in dts)
            else:
                rst = dts.strftime('%Y%m%d%H%M%S')

            return '[' + rst + ']'
        except Exception as data:
            #print(str(data)) 
            LogLib.error('CMADaasAccess get_timerange except %s %s' % (str(dts), str(data)))
            raise data
            #return None
    
    @staticmethod
    def set_timerange_in_params(dts, params, deep_copy=True):
        try:
            rst = params
            if deep_copy:
                import copy
                rst = copy.deepcopy(params)

            rst['timeRange'] = CMADaasAccess.get_timerange(dts)

            return rst
        except Exception as data:
            #print(str(data))
            LogLib.error('CMADaasAccess set_timerange_in_params except %s %s' % (str(dts), str(data)))
            raise data
            #return None
    
    @staticmethod
    def get_query(params):
        '''
        生成url中query部分
        '''
        try:
            querystr = ''
            for key,item in params.items():
                querystr += key + "=" + str(item) + "&"

            if(querystr):
                querystr = querystr[:-1]
            
            return querystr
        except Exception as data:
            #print(str(data))
            LogLib.error('CMADaasAccess get_query except %s %s' % (str(params), str(data)))
            raise data
            #return None
            
    @staticmethod
    def get_url(url, qparams):
        '''
        生成url
        '''
        #import copy
        try:
            #signParams = copy.deepcopy(qparams)
            signParams = qparams
            signString = SignGenUtil.getSign(signParams)
            if signString is None:
                LogLib.error('CMADaasAccess getUrl getSign error %s %s' % (url, str(qparams)))
                return None

            signParams['sign'] = signString
            signParams.pop('pwd')

            
            querystr = CMADaasAccess.get_query(signParams)
            
            return url + querystr
        except Exception as data:
            #print(str(data))  
            LogLib.error('CMADaasAccess getUrl except %s %s %s' % (url, str(qparams), str(data)))
            raise data
            #return None
            
    @staticmethod
    def get_default_headers():
        return { 'Accept' : 'application/json, text/plain, */*',
                'Accept-Encoding' : 'gzip, deflate, br',
                'Accept-Language' : 'zh-CN,zh;q=0.9',
                'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36' }
            
    #only json is supported
    #从cmadaas获得json格式数据，使用json库解析，构建一个dataframe返回。
    @staticmethod
    def read_data_from_cmadaas(fullurl):
        try:
            LogLib.info('CMADaasAccess read_data_from_cmadaas start %s' % (str(fullurl)))
            headers = CMADaasAccess.get_default_headers()
            host, url, ishttp = HttpConn.parseUrl(fullurl)
            rststatus, rstcontent, rstheaders = HttpConn.getWebPage(host, url, headers=headers, ishttp=ishttp)
            if rststatus != 200:
                LogLib.error('CMADaasAccess read_data_from_cmadaas net error %d %s' % (rststatus, str(fullurl)))
                return None

            jsonobj = json.loads(rstcontent)
            if jsonobj is None:
                LogLib.error('CMADaasAccess read_data_from_cmadaas json loads error %s %s' % (rstcontent, str(fullurl)))
                return None

            if 'returnCode' not in jsonobj:
                LogLib.error('CMADaasAccess read_data_from_cmadaas json no returnCode %s %s' % (rstcontent, str(fullurl)))
                return None

            if jsonobj['returnCode'] != '0':
                if jsonobj['returnCode'] == '-1':
                    LogLib.info('CMADaasAccess read_data_from_cmadaas json no data %s %s' % (rstcontent, str(fullurl)))
                    return []
                else:
                    LogLib.error('CMADaasAccess read_data_from_cmadaas json no returnCode or returnCode != 0 %s %s' % (rstcontent, str(fullurl)))
                    return None

            return jsonobj['DS']
        except Exception as data:
            LogLib.error('CMADaasAccess read_data_from_cmadaas except %s %s' % (str(fullurl), str(data)))
            return None
    
    @staticmethod
    def read_griddata_from_cmadaas(fullurl,time=None,dtime=None):
        try:
            LogLib.info('CMADaasAccess read_data_from_cmadaas start %s' % (str(fullurl)))
            headers = CMADaasAccess.get_default_headers()
            host, url, ishttp = HttpConn.parseUrl(fullurl)
            rststatus, rstcontent, rstheaders = HttpConn.getWebPage(host, url, headers=headers, ishttp=ishttp)
            if rststatus != 200:
                LogLib.error('CMADaasAccess read_data_from_cmadaas net error %d %s' % (rststatus, str(fullurl)))
                return None

            jsonobj = json.loads(rstcontent)
            if jsonobj is None:
                LogLib.error('CMADaasAccess read_data_from_cmadaas json loads error %s %s' % (rstcontent, str(fullurl)))
                return None

            if 'returnCode' not in jsonobj:
                LogLib.error('CMADaasAccess read_data_from_cmadaas json no returnCode %s %s' % (rstcontent, str(fullurl)))
                return None
            
            griddata = CMADaasAccess.griddata_from_cmadaas_json(jsonobj,time=time, dtime=dtime)
            return griddata
        except Exception as data:
            LogLib.error('CMADaasAccess read_data_from_cmadaas except %s %s' % (str(fullurl), str(data)))
            return None


    @staticmethod
    def griddata_from_cmadaas_json(json,time=None,dtime=None):
        try:
            lonS = round(json['startLon'],4)
            # lonE = round(json['endLon'],3)
            latS = round(json['startLat'],4)
            # latE = round(json['endLat'],3)
            dlon = round(json['lonStep'],4)
            dlat = round(json['latStep'],4)
            nlon = int(json['lonCount'])
            nlat = int(json['latCount'])
            lonE = lonS + (nlon-1)*dlon
            latE = latS + (nlat-1)*dlat
            #print(lonS,dlon,nlon,lonE)
            data = np.array(json['DS'])
            
            #data
            # print(data.shape)

            if time is not None:
                if not isinstance(time,list): 
                    time = [time]#确保time为列表
            if dtime is not None:
                if not isinstance(dtime,list): 
                    dtime = [dtime]#确保dtime为列表
            # print(time,dtime)
            grid_info = meteva.base.grid([lonS,lonE,dlon],[latS,latE,dlat]
                                 ,gtime = time
                                 ,dtime_list=dtime)
            #print(grid_info)
            grid = meteva.base.grid_data(grid_info,data)
        except Exception as data:
            print(json)
            return None
        return grid
            
                
    
    @staticmethod
    def dataframe_from_dict_json(j_dict,default=np.nan):
        import pandas as pd
        try:
            LogLib.info('CMADaasAccess Convert dataFrame from JSON_dict {0}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M")))
            pddata = pd.DataFrame.from_dict(j_dict)
            ## 更改dataframe
            sta = meteva.base.sta_data(pddata, columns=['time','id','lat','lon','data0'])
            sta.level = 0
            sta.dtime=0
            sta.time = pd.to_datetime(sta.time)
            sta.level = sta.level.astype(np.int16)
            sta.id = sta.id.astype(np.int32)
            sta.dtime = sta.dtime.astype(np.int16)
            sta.lon = sta.lon.astype(np.float32)
            sta.lat = sta.lat.astype(np.float32)
            try:
                sta.data0 = sta.data0.astype(np.float32)
                sta.data0[sta.data0>=990000]=default
            except:
                pass
            return(sta)            
        except Exception as data:
            LogLib.error('CMADaasAccess Convert dataFrame from JSON_dict {0}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M")))
            return(None)
            
        
        
    #从cmadaas获得文件数据。
    @staticmethod
    def read_file_from_cmadaas(fullurl):
        try:
            LogLib.info('CMADaasAccess read_file_from_cmadaas start %s' % (str(fullurl)))
            headers = CMADaasAccess.get_default_headers()
            host, url, ishttp = HttpConn.parseUrl(fullurl)
            rststatus, rstcontent, rstheaders = HttpConn.getWebPage(host, url, headers=headers, ishttp=ishttp)
            if rststatus != 200:
                LogLib.error('CMADaasAccess read_file_from_cmadaas net error %d %s' % (rststatus, str(fullurl)))
                return None
            return (rstcontent, rstheaders)
        except Exception as data:
            LogLib.error('CMADaasAccess read_file_from_cmadaas except %s %s' % (str(fullurl), str(data)))
            return None
        
    @staticmethod    
    def write_data_to_file(save_path,grd,creat_dir=True):
        import os
        try:
            LogLib.info('FixWriteData write_data_to_file start %s' % (save_path))            
            if creat_dir:
                path,file = os.path.split(save_path)
                if not os.path.exists(path):
                   os.makedirs(path)
            with open(save_path, 'wb') as f:
                f.write(grd)
            LogLib.info('FixWriteData write_data_to_file over %s' % (save_path))
            return True
        except Exception as data:
            LogLib.error('FixWriteData write_data_to_file except %s' % (str(save_path)))
            raise data
            
    ## 生成datetime类
    def get_datetime_from_str(dt='202011110200'):#dt可以为任意长度字符串，也可为datetime类
        if type(dt) == str:
            #用户输入2019041910十位字符，后面补全加0000，为14位统一处理
            if len(dt) == 4:
                num1=dt + "0101000000"
            elif len(dt) == 6:
                num1=dt + "01000000"
            elif len(dt) == 8:
                num1=dt + "000000"
            elif len(dt) == 10:
                num1=dt + "0000"
            elif len(dt) == 12:
                num1=dt + "00"
            elif len(dt) == 14:
                num1=dt
            else:
                print("输入日期有误，请检查！")
            #统一将日期变为datetime类型
            time = datetime.datetime.strptime(num1, '%Y%m%d%H%M%S')
        else:
            time = dt
        return(time)
    

    ## 根据参数字典，生成REST格式url。            
    @staticmethod
    def combine_url_from_para(qprams, time=datetime.datetime(2020,11,27,0,0), url=None,
                              SN_id="NMIC_MUSIC_CMADAAS", dataFormat='json', userId=None, pwd=None,
                                     defaultNan=9999, show_url=False, time_name='times'):
        """
        dt： 可以为字符串str，如“202011110200”；也可以为datetime类时间数据
        userID: 业务账号，必须填
        pwd： 业务账户密码，必须填
        dataFormat: 返回数据格式，默认为json
        show_url:  是否完整显示url，默认为不显示
        url: cmadaas的url前面固定部分，默认'http://10.40.17.54/music-ws/api?'
        SN_id: cmadaas服务节点代码，默认'NMIC_MUSIC_CMADAAS'
        time_name:时间参数的字典名(time或者times)
        """
        import copy
        params = copy.copy(qprams)
        LogLib.info('OBS Download from CmaDaas: {0}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M"))) 
            
        ## 账户处理
        if userId is None:
            userId = meteva.base.cmadaas_set[2]
            LogLib.warning('NO userID input,Using default USER: {0}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M")))
        if pwd is None:
            pwd = meteva.base.cmadaas_set[3]
            LogLib.warning('NO Password input,Using default pwd: {0}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M")))
        ## 添加字典变量要素   
        if "timeRange" in params:
            params['timeRange'] = (str(params['timeRange']).replace(' ',''))
        if "userId" not in params:
            params["userId"] = userId
#            params = params.pop("userId")
        if "pwd" not in params:
            params["pwd"] = pwd
        if not (("times" in params) or ("time" in params) or ("timeRange" in params)):
            params[time_name] = CMADaasAccess.get_times(time)
        if "serviceNodeId" not in params: params["serviceNodeId"] = SN_id
        if "timestamp" not in params : params["timestamp"]= str(int(datetime.datetime.now().timestamp()*1000))  
        if "nonce" not in params : params["nonce"] = '3696663f-d202-4570-b39d-16306f419575'
        if "dataFormat" not in params : params['dataFormat'] = dataFormat
        ## 生成url
        
        #print(params['timeRange'])
        if url is None:
            url = "http://"+meteva.base.cmadaas_set[0]+':'+meteva.base.cmadaas_set[1]+"/music-ws/api?"

        urlstr = CMADaasAccess.get_url(url, params)
        if show_url is True : print(urlstr)
        ## 返回url
        return(urlstr)
        
        
            
    
    @staticmethod            
    def get_obs_micaps3_from_cmadaas(qparams, time="202011110200",save_path=None, filename=None, defaultNan=9999,show = False,
                                     **kargs):
        """
        函数返回：meteva形式的pandas.DataFrame格式；如果申明sava_path变量，可直接输出Micaps3文件
        ###
        qparams: 包含数据、列表、下载要素的字典容器
        time： 可以为字符串str，如“202011110200”；也可以为datetime类时间数据
        userID: 业务账号，必须填
        pwd： 业务账户密码，必须填
        save_path: 存储文件目录，若不填写则不输出
        filename:  存储文件名,可以使用通配符(如YYYYMMDDHHFF.TTT即表示“年(四位)月(两位)日(两位)时(两位)分(两位).时效(三位)”；缺省-YYYYMMDDHHFF.000.m3)
        show_url:  是否完整显示url，默认为不显示
        defaultNan: 缺测显示值，默认缺测存成9999
        dataFormat: 返回数据格式，默认为json
        url: cmadaas的url前面固定部分，默认'http://10.40.17.54/music-ws/api?'
        SN_id: cmadaas服务节点代码，默认'NMIC_MUSIC_CMADAAS'
        ###
        """
        import os
        ## 根据参数字典，生成url
        LogLib.info('CMADaasAccess OBS output Starts: {0}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M")))
        time = CMADaasAccess.get_datetime_from_str(time)
        #print(time)
        urlstr = CMADaasAccess.combine_url_from_para(qparams,time,**kargs)
        if show:print(urlstr)
        ## 得到url返回结果
        json = CMADaasAccess.read_data_from_cmadaas(urlstr)
        ## 生成meteva数据
        sta = CMADaasAccess.dataframe_from_dict_json(json,default=defaultNan)
        ## 输出micaps3格式
        if save_path is not None:
            try:
                if filename is None: filename="YYYYMMDDHHFF.000.m3"
                output_name = os.path.join(save_path, filename)
                output_name = meteva.base.get_path(output_name,time)
                print('OUTPUT: ', output_name)
                meteva.base.write_stadata_to_micaps3(sta, save_path=output_name, effectiveNum=2)
            except Exception as data:
                LogLib.error('{0} CMADaasAccess OBS output ERROR!: {1}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M"),data))        
        return(sta)


            
    @staticmethod
    def get_files_from_cmadaas(qparams, time='202011110200', save_path=None, filename=None, show_files=True, is_new=True,
                               **kargs):
        """
        time： 可以为字符串str，如“202011110200”；也可以为datetime类时间数据 
        save_path: 存储文件目录，若不填写则不存储
        filename:  存储文件名,可以使用通配符(如YYYYMMDDHHFF.TTT即表示“年(四位)月(两位)日(两位)时(两位)分(两位).时效(三位)”；缺省-使用云平台原始文件名)
        show_url: 是否完整显示url，默认为不显示
        show_files: 是否完整显示待下载文件，默认为不显示
        is_new    ；True-只处理下载最新入库时间的一个文件;Fales-处理所有文件
        """
        import os
        import pandas as pd
        import datetime
        ## 根据参数字典，生成url
        time = CMADaasAccess.get_datetime_from_str(time)
        urlstr = CMADaasAccess.combine_url_from_para(qparams,time,**kargs)
        ## 得到url返回结果
        json = CMADaasAccess.read_data_from_cmadaas(urlstr)
        df = pd.DataFrame(json)
        try:
            df.sort_values(by='IYMDHM',inplace=True,ascending=False)#按入库时间降序排列，新更新的在上方
        except:
            print("no key IYMDHM")
        df.reset_index(drop=True,inplace=True)
        if is_new : df = df.loc[0].to_frame().T
        if show_files : print(df,type(df))
        
        try:
            LogLib.info('FixWriteData write_data_to_file start %s' % (save_path))
            if save_path is None: return(json)#save_path为None，不存储文件，直接返回json信息
            
            for index in range(len(df)):
                fname = df.loc[index,'FILE_NAME']
                url = df.loc[index,'FILE_URL']
                datetime = df.loc[index, 'Datetime']
                ## url内容读取并文件保存
                file_time = CMADaasAccess.get_datetime_from_str(datetime)
                # 原url文件名
                if filename is None:
                    output_name = os.path.join(save_path, fname)
                # 自定义文件名格式
                else:
                    output_name = os.path.join(save_path, filename)
                output_name = meteva.base.get_path(output_name,file_time)
                # 文件存储
                grd,header = CMADaasAccess.read_file_from_cmadaas(url)
                print('WriteFile : ',output_name)
                CMADaasAccess.write_data_to_file(output_name,grd,creat_dir=True)
                
        except Exception as data:
            print("ERROR:",data)
            LogLib.error('{0} CMADaasAccess Files output ERROR!: {1}'.format(datetime.datetime.now().strftime("%Y%m%d%H%M"),data))
        
        return(json)
#        
        
            
            
        

if __name__ == '__main__':

    dati_list = [datetime.datetime(2021,12,1,0,0),datetime.datetime(2021,12,1,1,0)]
    qparams = {'serviceNodeId':'NMIC_MUSIC_CMADAAS',
            'userId':'NMC_SGFV',
            'interfaceId':'getSateFileByTimeRange',
            'dataCode':'SATE_FY4A_STA_L1',
            'timeRange':CMADaasAccess.get_timerange(dati_list),
            'pwd':'NMC_yfsjyk_601'
            }
    save_dir = r"H:\test_data\output\meb\get_files"
    urlstr = CMADaasAccess.get_files_from_cmadaas(qparams,show_url=True,save_path=save_dir)
    print(urlstr)


