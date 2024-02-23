from meteva.method.space.baddeley_binary_image_metric.locmeasures2d_spatial_vx import locmeasures2d_spatial_vx
from meteva.method.space.baddeley_binary_image_metric.lib.make_spatialVx import make_spatialVx
#import pyreadr


def locmeasures2d_default(grd_ob, grd_fo, thresholds, which_stats=None, k=None, alpha=None, bdconst=None, p=None):
    # ph 并没有进行计算
    if p is None:
        p = [2]
    if alpha is None:
        alpha = [0.1]
    if which_stats is None:
        which_stats = ["bdelta", "haus", "qdmapdiff", "med", "msd", "ph", "fom"]
    if grd_fo.shape != grd_ob.shape:
        raise Exception("locmeasures2d: dim of observed field (", grd_ob.shape, ") must equal dim of forecast field (",
                        grd_fo.shape, ")")
    obj = make_spatialVx(grd_ob=grd_ob, grd_fo=grd_fo, loc=None, thresholds=thresholds)
    out = locmeasures2d_spatial_vx(input_object=obj, which_stats=which_stats, k=k, alpha=alpha, bdconst=bdconst, p=p)
    return out


if __name__ == '__main__':
    # geom000 = pyreadr.read_r('./data/geom000.Rdata')['geom000']
    # geom001 = pyreadr.read_r('./data/geom001.Rdata')['geom001']

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

    look = locmeasures2d_default(obs_array, fst_array, [0.01, 50.01, 99.01], k=[4, 0.975], alpha=0.1)
    print("j")
