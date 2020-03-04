#!/usr/bin/env python
# coding=utf8

import httplib2

def get_http_result (host, port, url):
    http_client = None
    try:
        #http_client = httplib.HTTPConnection(host, port, timeout=120)
        #http_client.request('GET', url)
        #response = http_client.getresponse()
        
        http_client = httplib2.Http()
        url = "http://"+str(host)+":"+str(port)+str(url)
        response,content = http_client.request(url,'GET')

        return response.status,  content
    except Exception as e:
        print(e)
        return 0,
    #finally:
    #    if http_client:
    #        http_client.close()