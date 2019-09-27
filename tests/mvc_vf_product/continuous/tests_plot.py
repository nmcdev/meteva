from nmc_verification.nmc_vf_base import io
import nmc_verification.nmc_vf_base.function.gxy_sxy as gxy_sxy
import nmc_verification.nmc_vf_product.continues.plot as plot
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
    grib_data = io.read_griddata.read_from_nc(path + '\data\BT18010120.012.nc')

    sta_data = io.read_stadata.read_station(path + '\data\station_table.txt', columns=['id', 'lat', 'lon', 'alt'])

    in_sta = gxy_sxy.interpolation_linear(grib_data, sta_data)

    plot.scatter_regress_muti_model(in_sta, [in_sta, in_sta, in_sta])
    plot.box_plot_muti_model(in_sta, [in_sta, in_sta, in_sta])
    plot.sorted_ob_fo_muti_model(in_sta, [in_sta, in_sta, in_sta])

    # path = get_tests_path()
    # grib_data = io.read_griddata.read_from_nc(path + '\data\BT19060108.024.nc')
    #
    # ob_data = io.read_stadata.read_from_micaps3(path + '\data\BT19060208.000')
    # # print(sta_data)
    # fo_data = gxy_sxy.interpolation_linear(grib_data, ob_data)
    # ob_data.rename(columns={'data0': 0})
    # print(fo_data.columns)
    # print(ob_data.columns)
    # print(fo_data)
    # print(ob_data)
    # ob_data['time'] = fo_data['time']
    # # plot.scatter_regress_muti_model(ob_data, [fo_data])
    # plot.scatter_regress_muti_model(ob_data, [fo_data, fo_data, fo_data])
    # plot.box_plot_muti_model(ob_data, [fo_data, fo_data, fo_data])
    # plot.sorted_ob_fo_muti_model(ob_data, [fo_data, fo_data, fo_data])
