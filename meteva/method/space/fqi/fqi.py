import numpy as np
from meteva.method.space.fqi.lib.locmeasures2d_prep import locmeasures2d_prep
from meteva.method.space.fqi.lib.util import get_attributes
from meteva.method.space.fqi.lib.datagrabber_spatialVx import datagrabber_spatialVx
from meteva.method.space.fqi.lib.im import im
from meteva.method.space.fqi.lib.solutionset import solutionset
from meteva.method.space.fqi.lib.cbind import cbind
from meteva.method.space.fqi.uiqi import uiqi
from meteva.method.space.fqi.lib.locperf import locperf
from meteva.method.space.fqi.lib.surrogater2d import surrogater2d
from meteva.method.space.fqi.lib.locperfer import locperfer
#import pyreadr
from meteva.method.space.baddeley_binary_image_metric.lib.make_spatialVx import make_spatialVx
#import rdata
import meteva

def fqi(grd_ob,grd_fo, thresholds):
    obs_array = grd_ob.values.squeeze()
    fst_array = grd_fo.values.squeeze()
    z = surrogater2d(obs_array, zero_down=True, n=10)
    hold = make_spatialVx(obs_array, fst_array,loc=None, thresholds=thresholds)
    result = fqi_origin(hold, surr=z, k=4)
    fqi_array = result["fqi"]
    fqi_array[np.isnan(fqi_array)] = meteva.base.IV
    return result["fqi"]


def fqi_origin(input_object, surr=None, k=4, time_point=0, obs=0, model=0):
    out = {}
    input_object = locmeasures2d_prep(input_object=input_object, k=k)
    attributes = get_attributes(input_object)
    out["attributes"] = attributes
    dat = datagrabber_spatialVx(input_object, time_point=time_point, obs=obs, model=model)
    x = np.array(dat["X"])
    y = np.array(dat["Xhat"])
    out["attributes"]["data_name"] = [attributes["dataname"], attributes["obsname"][obs],
                                      attributes["modelname"][model]]
    thresholds = attributes["thresholds"]
    thresholds = cbind(thresholds[0][:, obs], thresholds[1][:, model])
    out["attributes"]["thresholds"] = thresholds
    if surr is None:
        surr = surrogater2d(im=x)
    xdim = x.shape
    xim = im(x)
    yim = im(y)
    q = np.array(thresholds).shape[0]
    ks = attributes["k"]
    nk = 1
    phd_norm = np.full((nk, q), np.nan)
    fqi = np.full((nk, q), np.nan)
    uiqi_norm = np.full((q, 1), np.nan)
    for threshold in range(q):
        temp_x = xim['v'] >= thresholds[threshold, 0]
        xim['v'] = temp_x
        ix = solutionset(xim)
        temp_y = yim['v'] >= thresholds[threshold, 1]
        yim['v'] = temp_y
        iy = solutionset(yim)
        idx = x >= thresholds[threshold, 0]
        idy = y >= thresholds[threshold, 1]
        x2 = x
        x2[~idx] = 0
        y2 = y
        y2[~idy] = 0
        denom = uiqi(x=x2, xhat=y2, only_nonzero=True)["uiqi"]
        uiqi_norm[threshold] = denom
        for k in range(nk):
            num1 = locperf(X=ix, Y=iy, which_stats="ph", k=ks)["ph"]
            tmp = np.full(surr.shape[2], np.nan, dtype=float)
            for l in range(surr.shape[2]):
                if isinstance(ks, int):
                    tmpK = ks
                else:
                    tmpK = ks[k]
                tmp[l] = locperfer(surr[:, :, 0], ix, thresholds[threshold, 0], tmpK)
            num2 = np.nanmean(tmp)
            if num1 is np.nan or num2 is np.nan or num1 is None or num2 is None:
                num_tmp = np.nan
            else:
                num_tmp = num1 / num2
            phd_norm[k, threshold] = num_tmp
            fqi[k, threshold] = num_tmp / denom
    out["phd_norm"] = phd_norm
    out["uiqi_norm"] = uiqi_norm
    out["fqi"] = fqi
    out["class"] = "fqi"
    return out


if __name__ == '__main__':
    # parsed = rdata.parser.parse_file('/home/andyji/hold.rdata')
    # hold = rdata.conversion.convert(parsed)['hold']
    #
    # h1 = np.fft.ifft(hold)
    # h2 = np.fft.ifft(hold.flatten()).reshape(hold.shape)
    # # temp2 = fft2d(temp, bigdim=(1024, 512), inverse=True) / 301101
    # geom000 = pyreadr.read_r('../fuzzy_logic/data/geom000.Rdata')['geom000']
    # geom001 = pyreadr.read_r('../fuzzy_logic/data/geom001.Rdata')['geom001']
    # ICPg240Locs = pyreadr.read_r('../fuzzy_logic/data/ICPg240Locs.Rdata')['ICPg240Locs']
    # ix = np.array([[0,0,1],[1,0,1],[1,1,1]])
    # iy = np.array([[0, 0, 1], [1, 0, 1], [1, 1, 1]])

    import meteva.base as meb
    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    path_fo_03 = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    path_fo_27 = r'H:\test_data\input\mem\mode\ec\rain03\20072508.027.nc'
    grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo_03 = meb.read_griddata_from_nc(path_fo_03, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")
    grd_fo_27 = meb.read_griddata_from_nc(path_fo_27, grid=grid1, time="2020072508", dtime=27, data_name="ECMWF")
    result = fqi(grd_fo_03,grd_fo_27,thresholds=[0.01,50.01])
    #
    # obs_array = grd_ob.values.squeeze()
    # fst_array = grd_fo_03.values.squeeze()
    # z = surrogater2d(obs_array, zero_down=True, n=10)
    # hold = make_spatialVx(obs_array, fst_array,loc=None, thresholds=[0.01, 50.01])
    # result = fqi(hold, surr=z, k=4)
    print(result)
