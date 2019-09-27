import nmc_verification.nmc_vf_product.yes_or_no.table as table
import nmc_verification.nmc_vf_base.io as io
import nmc_verification.nmc_vf_base.function.gxy_sxy as gxy_sxy
import nmc_verification.nmc_vf_base.basicdata.sta_data as sta
import os


def get_tests_path(path=__file__):
    path = os.path.dirname(path)

    if path[-5:] == 'tests':
        return path
    elif len(path) == 3:
        return
    else:
        path = get_tests_path(path)
        return path


if __name__ == '__main__':
    # path = get_tests_path()
    # grib_data = io.read_griddata.read_from_nc(path + '/data/BT18010120.012.nc')
    #
    # sta_data = io.read_stadata.read_station(path + '/data/station_table.txt', columns=['id', 'lat', 'lon', 'alt'])
    #
    # in_sta = gxy_sxy.interpolation_linear(grib_data, sta_data)
    #
    # table.contingency_table_multi_mode(in_sta, [in_sta], grade=0.3)
    # print('multi_mode_and_multi_classification_predictive_contingency_table 执行完毕:')
    path = get_tests_path()
    grib_data = io.read_griddata.read_from_nc(path + '\data\BT19060108.024.nc')

    ob_data = io.read_stadata.read_from_micaps3(path + '\data\BT19060208.000')
    # print(sta_data)
    fo_data = gxy_sxy.interpolation_linear(grib_data, ob_data)
    ob_data['time'] = fo_data['time']
    table.contingency_table_multi_mode(ob_data, [fo_data], grade=0.3)