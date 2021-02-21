#!/usr/bin/python
# -*- coding: utf-8 -*-
#Filename: httpconn.py

'''
Created on Sep 14, 2020

@author: anduin
'''

import zlib
from urllib.parse import urlparse
from urllib.parse import urljoin
from urllib.parse import urlencode
from http.client import HTTPConnection
from http.client import HTTPSConnection
import json
import urllib.request
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

from .loglib import *

class HttpConn():
    @staticmethod
    def joinUrl(url, path):
        return urljoin(url, path)
    
    @staticmethod
    def parseUrl(url):
        try:
            prse = urlparse(url)
            ishttp = False
            if prse.scheme.upper() == 'HTTP':
                ishttp = True

            start = url.find(prse.netloc)
            path = url[start + len(prse.netloc):]
            if len(path) == 0:
                path = r'/'
                
            return prse.netloc, path, ishttp
        except Exception as data:
            LogLib.logger.error('parseUrl except ' + str(data))
            print(data)
            return '', '', ''
    
    
    @staticmethod
    def getHeaderValue(headers, name):
        for header in headers:
            if header[0].lower() == name.lower():
                return header[1]
            
        return None
    
    @staticmethod
    def getHeaderValues(headers, name):
        values = []
        for header in headers:
            if header[0].lower() == name.lower():
                values.append(header[1])
            
        return values
    
    @staticmethod
    def getWebPage(host, url, headers = None, ishttp = True):
        conn = None
        try:
            if ishttp:
                conn=HTTPConnection(host, timeout = 60)
            else:
                conn=HTTPSConnection(host, timeout = 60)
            
            if headers == None:
                conn.request('GET', url)
            else:
                conn.request('GET', url, headers = headers)
            result = conn.getresponse()
            rststatus = result.status
            rstheaders = result.getheaders()
            rstcontent_org = result.read()
            
            encoding = HttpConn.getHeaderValue(rstheaders, 'content-encoding')
            if encoding != None and encoding.lower() == 'gzip':
                decomp = zlib.decompressobj(16+zlib.MAX_WBITS)
                rstcontent = decomp.decompress(rstcontent_org)
            else:
                rstcontent = rstcontent_org
##            if __name__ == '__main__':
##                print host
##                print url
##                print rststatus
##                print rstheaders
##                print rstcontent
                
            conn.close()
            
            return (rststatus, rstcontent, rstheaders)
        except Exception as data:
            LogLib.logger.error('getWebPage except ' + str(data))
            if conn != None:
                conn.close()
            
            return (0, None, None)
        
    @staticmethod
    def postData(host, url, headers, params, ishttp = True):
        conn = None
        try:
            if ishttp:
                conn=HTTPConnection(host, timeout = 60)
            else:
                conn=HTTPSConnection(host, timeout = 60)
                
            if headers == None:
                conn.request('POST', url, body = params)
            else:
                conn.request('POST', url, body = params, headers = headers)
            
            result = conn.getresponse()
            rststatus = result.status
            rstheaders = result.getheaders()
            rstcontent_org = result.read()
            
            encoding = HttpConn.getHeaderValue(rstheaders, 'content-encoding')
            if encoding != None and encoding.lower() == 'gzip':
                decomp = zlib.decompressobj(16+zlib.MAX_WBITS)
                rstcontent = decomp.decompress(rstcontent_org)
            else:
                rstcontent = rstcontent_org
                
            conn.close()
            
            return (rststatus, rstcontent, rstheaders)
        except Exception as data:
            LogLib.logger.error('postData except ' + str(data))
            if conn != None:
                print('conn is None')
                conn.close()
            
            return (0, None, None)
    
    @staticmethod
    def getWebPageWithProxy(url, proxyhost, proxyport, headers = {}):
        try:
            proxyurl = "http://" + proxyhost + ":" + "%d"%proxyport
            proxy_support = urllib.request.ProxyHandler({"http": proxyurl, "https": proxyurl})
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)
            req = urllib.request.Request(url)
            if headers != None:
                for header in headers:
                    req.add_header(header, headers[header])
                
            result = urllib.request.urlopen(req)
            rststatus = result.status
            rstheaders = result.getheaders()
            rstcontent_org = result.read()
            
            encoding = HttpConn.getHeaderValue(rstheaders, 'content-encoding')
            if encoding != None and encoding.lower() == 'gzip':
                decomp = zlib.decompressobj(16+zlib.MAX_WBITS)
                rstcontent = decomp.decompress(rstcontent_org)
            else:
                rstcontent = rstcontent_org
##            if __name__ == '__main__':
##                print host
##                print url
##                print rststatus
##                print rstheaders
##                print rstcontent
                
            return (rststatus, rstcontent, rstheaders)
        except Exception as data:
            LogLib.logger.error('getWebPageWithProxy except ' + str(data))
            
            return (0, None, None)
        
    @staticmethod
    def postDataWithProxy(url, proxyhost, proxyport, params, headers = {} ):
        try:
            proxyurl = "http://" + proxyhost + ":" + "%d"%proxyport
            proxy_support = urllib.request.ProxyHandler({"http": proxyurl, "https": proxyurl})
            opener = urllib.request.build_opener(proxy_support)
            urllib.request.install_opener(opener)
            pdata = params.encode(encoding='UTF8')
            req = urllib.request.Request(url, pdata, headers, method='POST')
                
            result = urllib.request.urlopen(req)
            rststatus = result.status
            rstheaders = result.getheaders()
            rstcontent_org = result.read()
            
            encoding = HttpConn.getHeaderValue(rstheaders, 'content-encoding')
            if encoding != None and encoding.lower() == 'gzip':
                #compressedstream = StringIO.StringIO(rstcontent_org)
                #gzipper = gzip.GzipFile(fileobj=compressedstream)      
                #rstcontent = gzipper.read()
                decomp = zlib.decompressobj(16+zlib.MAX_WBITS)
                rstcontent = decomp.decompress(rstcontent_org)
            else:
                rstcontent = rstcontent_org
                
            return (rststatus, rstcontent, rstheaders)
        except Exception as data:
            LogLib.logger.error('postDataWithProxy except ' + str(data))
            
            return (0, None, None)
    
    @staticmethod
    def downloadFileWithWget(url, fullpath):
        try:
            import subprocess
            res = subprocess.Popen('wget ' + '"' + url + '" -O ' + fullpath, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=True)
            return res.stdout.readlines()
        except Exception as data:
            return None

if __name__ == '__main__':
    print(HttpConn.downloadFileWithWget(r'https://confluence.ecmwf.int/download/attachments/8650755/ecFlow-5.5.3-Source.tar.gz?api=v2', r'c:\workdoc\ecFlow-5.5.3-Source.tar.gz'))


    print('test done')