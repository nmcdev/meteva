#!/usr/bin/python3.6
# -*- coding:UTF-8 -*-
#添加一些常量
import pkg_resources
PI = 3.1415926
E = 2.7182818
ER = 6371
OMEGA = 0.00072722
IV = 999999
K = 273.15
dis_1_degree = 111.195
station_国家站 = pkg_resources.resource_filename('meteva', "resources/stations/sta2411_alt.txt")
station_国家站_考核区域站 = pkg_resources.resource_filename('meteva', "resources/stations/stat10461.txt")
station_全球城市 = pkg_resources.resource_filename('meteva', "resources/stations/station_global_alt_11621.txt")
station_全球重点城市 = pkg_resources.resource_filename('meteva', "resources/stations/sta_global_alt_243.txt")
gds_ip_port = None
customized_basemap_list = None
beaufort_scale = [0.0,0.3,1.6,3.4,5.5,8.0,10.8,13.9,17.2,20.8,24.5,28.5,32.7,37,41.5,46.2,51,56.1]
cmadaas_set = None
cimiss_set = None