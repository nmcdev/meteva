#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: SignGenUtil.py

'''
Created on Sep 14, 2020

@author: anduin
'''

import hashlib

class SignGenUtil():
    """description of class 
    get sign for url
    """
    
    @staticmethod
    def getSign(params):
        '''
                    生成sign标签
        '''
        try:
            paramString = ""
            if "params" in params:
                paramsVal = params.pop("params")
                keyValList = paramsVal.split("&")
                for keyVal in keyValList:
                    rsts = keyVal.split("=")
                    if len(rsts) > 1:
                        params[rsts[0]] = rsts[1]
                    else:
                        params[rsts[0]] = ""
                        
            keys = sorted(params)
            for key in keys:
                paramString = paramString + key + "=" + str(params.get(key)) + "&"

            if(paramString):
                paramString = paramString[:-1]
            
            #进行MD5运算
            return hashlib.md5(paramString.encode(encoding='UTF-8')).hexdigest().upper()
        except Exception as data:
            print(str(data))
            raise data
            #return None



