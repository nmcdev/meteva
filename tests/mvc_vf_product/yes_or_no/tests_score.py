import nmc_verification.nmc_vf_product.yes_or_no.score as score

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
    print('求ts_muti_model中......')
    print('ts_muti_model得分：', score.ts_muti_model(in_sta, [in_sta, in_sta, in_sta], grade_list=[0, 0.1, 0.3, 0.6, 1]))

    print('求bias_muti_model中......')
    print('bias_muti_model得分：',
          score.bias_muti_model(in_sta, [in_sta, in_sta, in_sta], grade_list=[0, 0.1, 0.3, 0.6, 1]))

    print('求mis_rate_muti_model中......')
    print('mis_rate_muti_model得分：',
          score.mis_rate_muti_model(in_sta, [in_sta, in_sta, in_sta], grade_list=[0, 0.1, 0.3, 0.6, 1]))

    print('求fal_rate_muti_model中......')
    print('fal_rate_muti_model得分：',
          score.fal_rate_muti_model(in_sta, [in_sta, in_sta, in_sta], grade_list=[0, 0.1, 0.3, 0.6, 1]))

    print('求hmfn_muti_model中......')
    print('hmfn_muti_model得分：',
          score.hmfn_muti_model(in_sta, [in_sta, in_sta, in_sta], grade_list=[0, 0.1, 0.3, 0.6, 1]))

    print('求abcd_muti_model中......')
    print('abcd_muti_model得分：', score.abcd_muti_model(in_sta, [in_sta, in_sta, in_sta]))

    print('求pc_of_sunny_rainy_muti_model中......')
    print('pc_of_sunny_rainy_muti_model得分：',
          score.pc_of_sunny_rainy_muti_model(in_sta, [in_sta, in_sta, in_sta]))

    print('求hit_muti_model中......')
    print('hit_muti_model得分：', score.hit_muti_model(in_sta, [in_sta, in_sta, in_sta], grade_list=[0, 0.1, 0.3, 0.6, 1]))

    print('求bias_extend_muti_model中......')
    print('bias_extend_muti_model得分：',
          score.bias_extend_muti_model(in_sta, [in_sta, in_sta, in_sta], grade_list=[0, 0.1, 0.3, 0.6, 1]))

    print('求ets_muti_model中......')
    print('ets_muti_model得分：', score.ets_muti_model(in_sta, [in_sta, in_sta, in_sta], grade_list=[0, 0.1, 0.3, 0.6, 1]))
