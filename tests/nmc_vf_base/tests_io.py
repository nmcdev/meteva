import nmc_verification.nmc_vf_base.io as io
import tests.nmc_vf_base.read_write_jumpe as rwj
import datetime
from nmc_verification.nmc_vf_base.basicdata import sta_data

if __name__ == '__main__':
    data_m3 = io.read_stadata.read_from_micaps3('../data/BT18010101.000')
    print("读取m3文件中............")
    rwj.is_NOne(data_m3)

    data_sevp = io.read_stadata.read_from_sevp('../data/SEVP_NMC_RFFC_SFER_EME_AGLB_L88_P9_20190628000016812.TXT')
    print("读取sevp文件中............")
    rwj.is_NOne(data_sevp)

    data_sta_table = io.read_stadata.read_station('../data/station_table.txt', columns=['id', 'lon', 'lat', 'alt'])
    print('读取sta_table文件中............')
    rwj.is_NOne(data_sta_table)

    data_m1 = io.read_stadata.read_from_micaps1_2_8('../data/19082208.000', column=6)
    print('读取m1文件中')
    rwj.is_NOne(data_m1)

    data_m2 = io.read_stadata.read_from_micaps1_2_8('../data/19082108.000', column=4)
    print('读取m2文件中')
    rwj.is_NOne(data_m2)

    data_m8 = io.read_stadata.read_from_micaps1_2_8('../data/19082108.000', column=4)
    print('读取m8文件中')
    rwj.is_NOne(data_m8)

    data_m4 = io.read_griddata.read_from_micaps4('../data/m4_data/19051708.024')
    print("读取m4文件中............")
    rwj.is_NOne2(data_m4)

    data_nc = io.read_griddata.read_from_nc('../data/BT18010120.012.nc')
    print("读取nc文件中............")
    rwj.is_NOne2(data_nc)

    io.write_stadata.write_to_micaps3(data_m3)
    rwj.file_is_exist()

    io.write_griddata.write_to_micaps4(data_m4, 'b.txt')
    rwj.file_is_exist('b.txt')

    io.write_griddata.write_to_nc(data_nc, 'c.txt')
    rwj.file_is_exist()
