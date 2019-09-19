#!/usr/bin/env python
# coding=utf8
from .httpclient import get_http_result

class GDSDataService:
    def __init__(self, gdsIp, gdsPort):
        self.gdsIp = gdsIp
        self.gdsPort = gdsPort #GDS服务器地址

    def getLatestDataName(self, directory, filter):
        return get_http_result(self.gdsIp, self.gdsPort, "/DataService" + self.get_concate_url("getLatestDataName", directory, "", filter))

    def getFileList(self,directory):
        return get_http_result(self.gdsIp,self.gdsPort,"/DataService" + self.get_concate_url("getFileList", directory, "",""))

    def getData(self, directory, fileName):
        return get_http_result(self.gdsIp, self.gdsPort, "/DataService" + self.get_concate_url("getData", directory, fileName, ""))


    # 将请求参数拼接到url
    def get_concate_url(self, requestType, directory, fileName, filter) :
        url = ""
        url += "?requestType=" + requestType
        url += "&directory=" + directory
        url += "&fileName=" + fileName
        url += "&filter=" + filter
        return url
