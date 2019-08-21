from nmc_verification.nmc_vf_base import io
from nmc_verification.nmc_vf_base.function import gxy_sxy
from nmc_verification.nmc_vf_product.continues import score
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

    grib_data = io.read_griddata.read_from_nc(path+'/data/BT18010120.012.nc')
    sta_data = io.read_stadata.read_station(path+'/data/station_table.txt', columns=['id', 'lat', 'lon', 'alt'])
    in_sta = gxy_sxy.interpolation_linear(grib_data, sta_data)
    print('mre_muti_model得分为：')
    print(score.mre_muti_model(in_sta, [in_sta, in_sta, in_sta]))
    print('bias_muti_model得分为：')
    print(score.bias_muti_model(in_sta, [in_sta, in_sta, in_sta]))
    print('corr_muti_model得分为：')
    print(score.corr_muti_model(in_sta, [in_sta, in_sta, in_sta]))
    print('mae_muti_model得分为：')
    print(score.mae_muti_model(in_sta, [in_sta, in_sta, in_sta]))
    print('mse_muti_model得分为：')
    print(score.mse_muti_model(in_sta, [in_sta, in_sta, in_sta]))
    print('rmse_muti_model得分为：')
    print(score.rmse_muti_model(in_sta, [in_sta, in_sta, in_sta]))
