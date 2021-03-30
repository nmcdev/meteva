#!/usr/bin/env python
# coding=utf8
import urllib3
import httplib2
import meteva

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


def get_http_result_cimiss(interface_id, params, data_format='json',show_url = False):
    """
    Get the http result from CIMISS REST api service.
    :param interface_id: MUSIC interface id.
    :param params: dictionary for MUSIC parameters.
    :param data_format: MUSIC server data format.
    :return:
    """


    dns = meteva.base.cimiss_set[0]
    user_id = meteva.base.cimiss_set[1]
    pwd = meteva.base.cimiss_set[2]

    # construct url
    url = 'http://' + dns + '/cimiss-web/api?userId=' + user_id + \
          '&pwd=' + pwd + '&interfaceId=' + interface_id

    # params
    for key in params:
        url += '&' + key + '=' + params[key].strip()

    # data format
    url += '&dataFormat=' + data_format
    if show_url:print(url)
    # request http contents
    http = urllib3.PoolManager()
    req = http.request('GET', url)
    if req.status != 200:
        print('Can not access the url: ' + url)
        return None
    return req.data