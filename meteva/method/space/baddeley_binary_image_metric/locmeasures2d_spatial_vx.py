from meteva.method.space.baddeley_binary_image_metric.locmeasures2d_prep import locmeasures2d_prep
from meteva.method.space.baddeley_binary_image_metric.lib.datagrabber_spatialVx import datagrabber_spatialVx
from meteva.method.space.baddeley_binary_image_metric.lib.deltametric import deltametric
from meteva.method.space.baddeley_binary_image_metric.lib.im import im
from meteva.method.space.baddeley_binary_image_metric.lib.loc_list_setup import loc_list_setup
from meteva.method.space.baddeley_binary_image_metric.lib.locperf import locperf
from meteva.method.space.baddeley_binary_image_metric.lib.solutionset import solutionset
import numpy as npy
import copy
#import pyreadr
from meteva.method.space.baddeley_binary_image_metric.lib.make_spatialVx import make_spatialVx


def locmeasures2d_spatial_vx(input_object, which_stats=None,
                             k=None, alpha=None, bdconst=None,
                             p=None, time_point=1, obs=1, model=1):
    if p is None:
        p = [2]
    if alpha is None:
        alpha = [0.1]
    if which_stats is None:
        which_stats = ["bdelta", "haus", "qdmapdiff", "med", "msd", "ph", "fom"]
    distfun = "distmapfun"
    distfun_params = None
    input_object = locmeasures2d_prep(input_object=input_object, k=k, alpha=alpha, bdconst=bdconst, p=p)
    a = input_object
    thresholds = a["thresholds"]
    q = thresholds[0].shape[0]
    if a["k"] is None and "qdmapdiff" in which_stats:
        print("locmeasures2d: must supply k in call to locmeasures2dPrep to do qdmapdiff method.")
        return
    try:
        nk = len(a["k"])
    except Exception:
        nk = 1
    try:
        np = len(a["p"])
    except Exception:
        np = 1
    try:
        nalpha = 1
    except Exception:
        nalpha = len(a["alpha"])
    out = loc_list_setup(a=a, which_stats=which_stats, nthresh=q, n_p=np, nk=nk, nalpha=nalpha)
    out["time_point"] = time_point
    out["model"] = model - 1
    dat = datagrabber_spatialVx(input_object, time_point=time_point, obs=obs - 1, model=model - 1)
    Obs = dat["X"]
    Fcst = dat["Xhat"]
    mainname = a["dataname"]
    vxname = a["obsname"][obs - 1]
    out["dataname"] = [mainname, vxname, a['modelname']]
    out["thresholds"] = {'X': thresholds[0][:, obs - 1], 'Xhat': thresholds[1][:, model - 1]}
    xdim = a["xdim"]
    x_id = im(Obs)
    y_id = im(Fcst)
    for threshold in range(0, q):
        x_res = copy.deepcopy(x_id)
        y_res = copy.deepcopy(y_id)
        x_res['v'] = x_id['v'] >= thresholds[0][threshold, obs - 1]
        y_res['v'] = y_id['v'] >= thresholds[1][threshold, model - 1]
        Ix = solutionset(x_res)
        Iy = solutionset(y_res)
        if "bdelta" in which_stats:
            for p in range(0, np):
                tmpDelta = deltametric(Iy, Ix, p=a['p'][p], c=a['bdconst'])
                if type(tmpDelta) != "try-error":
                    out['bdelta'][p, threshold] = tmpDelta
        if "haus" in which_stats:
            out['haus'][threshold] = deltametric(Iy, Ix, p=float("inf"), c=float("inf"))
        if "qdmapdiff" in which_stats:
            for k in range(0, nk):
                out['qdmapdiff'][k, threshold] = \
                    locperf(X=Ix, Y=Iy, which_stats="qdmapdiff", k=a['k'][k], distfun=distfun,
                            distfun_params=distfun_params)['qdmapdiff']
        w_id = ("med" in which_stats or "msd" in which_stats)
        if w_id:
            tmp = locperf(X=Ix, Y=Iy, which_stats=["med", "msd"], distfun=distfun, distfun_params=distfun_params)
            if "med" in which_stats:
                out['medMiss'][threshold] = tmp['medMiss']
                out['medFalseAlarm'][threshold] = tmp['medFalseAlarm']

            if "msd" in which_stats:
                out['msdMiss'][threshold] = tmp['msdMiss']
                out['msdFalseAlarm'][threshold] = tmp['msdFalseAlarm']

        if "fom" in which_stats:
            for i in range(1, nalpha):
                out['fom'][i, threshold] = locperf(X=Ix, Y=Iy, which_stats="fom", alpha=a['alpha'][i], distfun=distfun,
                                                   distfun_params=distfun_params)['fom']

    return out


if __name__ == '__main__':
    # geom000 = pyreadr.read_r('./data/geom000.Rdata')['geom000']
    # geom001 = pyreadr.read_r('./data/geom001.Rdata')['geom001']
    # ICPg240Locs = pyreadr.read_r('./data/ICPg240Locs.Rdata')['ICPg240Locs']

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

    hold = make_spatialVx(obs_array, fst_array, loc=None,
                          fieldtype="Geometric Objects Pretending to be Precipitation",
                          units="mm/h", thresholds=[0.01, 50.01],
                          dataname="ICP Geometric Cases", obsname="geom000", modelname="geom001")
    look = locmeasures2d_spatial_vx(hold, k=[4, 0.975], alpha=0.1)
    print("hj")
