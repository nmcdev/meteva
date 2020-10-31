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
station_国家站 = pkg_resources.resource_filename('meteva', "resources/stations/sta2411_alt.txt")
station_国家站_考核区域站 = pkg_resources.resource_filename('meteva', "resources/stations/stat10461.txt")
station_全球城市 = pkg_resources.resource_filename('meteva', "resources/stations/station_global_alt_11621.txt")
station_全球重点城市 = pkg_resources.resource_filename('meteva', "resources/stations/sta_global_alt_243.txt")
gds_ip_port = None
customized_basemap_list = None
