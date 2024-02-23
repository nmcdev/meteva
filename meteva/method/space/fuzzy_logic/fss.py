from meteva.method.space.fuzzy_logic.lib.hoods2d import hoods2d
#import pyreadr
from meteva.method.space.fuzzy_logic.lib.make_spatialVx import make_spatialVx


def fuzzy_fss(input_object, levels, time_point=1,
          obs=0, model=0, max_n=None, rule=">=", verbose=False):
    result = hoods2d(input_object, which_methods=["fss"], time_point=time_point,
                     obs=obs, model=model, levels=levels, max_n=max_n, rule=rule, verbose=verbose)["fss"]
    result["thresholds"] = input_object["thresholds"][0]
    result["levels"] = levels
    return result


if __name__ == '__main__':
    import meteva.base as meb
    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    path_fo_03 = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    path_fo_27 = r'H:\test_data\input\mem\mode\ec\rain03\20072508.027.nc'
    grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo_03 = meb.read_griddata_from_nc(path_fo_03, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")
    grd_fo_27 = meb.read_griddata_from_nc(path_fo_27, grid=grid1, time="2020072508", dtime=27, data_name="ECMWF")

    obs_array = grd_ob.values.squeeze()
    fst_array = grd_fo_03.values.squeeze()
    hold = make_spatialVx(obs_array,fst_array)
    #look = joint(hold, levels=[1, 3, 9, 17, 33, 65, 129, 257], verbose=True)
    look = fuzzy_fss(hold, levels=[3], verbose=True)
    print(look)
