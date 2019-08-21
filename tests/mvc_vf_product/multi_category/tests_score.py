import nmc_verification.nmc_vf_product.multi_category.score as score
import nmc_verification.nmc_vf_base.io as io
import nmc_verification.nmc_vf_base.function.gxy_sxy as gxy_sxy
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
    path = get_tests_path()

    grib_data = io.read_griddata.read_from_nc(path + '/data/BT18010120.012.nc')

    sta_data = io.read_stadata.read_station(path + '/data/station_table.txt', columns=['id', 'lat', 'lon', 'alt'])

    in_sta = gxy_sxy.interpolation_linear(grib_data, sta_data)
    print('accuracy_muti_model评分：')
    print(score.accuracy_muti_model(in_sta, [in_sta, in_sta, in_sta], grade_list=[0, 0.1, 0.3, 0.6, 1]))
    print('hk_muti_model评分：')
    print(score.hk_muti_model(in_sta, [in_sta, in_sta, in_sta], grade_list=[0, 0.1, 0.3, 0.6, 1]))
    print('hss_muti_model评分：')
    print(score.hss_muti_model(in_sta, [in_sta, in_sta, in_sta], grade_list=[0, 0.1, 0.3, 0.6, 1]))
