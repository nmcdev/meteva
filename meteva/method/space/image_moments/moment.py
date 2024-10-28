import numpy as np
import pandas as pd
import math
import meteva
#import pyreadr


def imomenter_matrix_numpy(x, loc=None):
    out = {}

    if loc is None:
        x_dim = x.shape[0]
        y_dim = x.shape[1]
        range0 = np.tile(np.arange(1, x_dim + 1), y_dim)
        range1 = (np.arange(1, y_dim + 1)).repeat(x_dim)
        loc = np.stack((range0, range1), axis=-1)

    def mij(x, s=None, i=0, j=0):
        x = np.array(x)
        if s is None:
            x_dim = x.shape[0]
            y_dim = x.shape[1]
            range0 = np.tile(np.arange(1, x_dim + 1), y_dim)
            range1 = (np.arange(1, y_dim + 1)).repeat(x_dim)
            s = np.stack((range0, range1), axis=-1)
        s_0 = np.zeros(s.shape)
        s_0[:, 0] = np.power(s[:, 0], i)
        s_0[:, 1] = np.power(s[:, 1], j)
        s = np.prod(s_0, axis=1)
        result = np.sum(s * np.reshape(x, -1, 'F'))
        return result

    M00 = mij(x, s=loc)
    M10 = mij(x, s=loc, i=1, j=0)
    M01 = mij(x, s=loc, i=0, j=1)
    M11 = mij(x, s=loc, i=1, j=1)
    M20 = mij(x, s=loc, i=2, j=0)
    M02 = mij(x, s=loc, i=0, j=2)

    xbar = M10 / M00
    ybar = M01 / M00
    cen = np.array([xbar, ybar])
    #names_cen = pd.DataFrame(cen, columns=["x", "y"])
    mu11 = M11 / M00 - xbar * ybar
    mu20 = M20 / M00 - xbar ** 2
    mu02 = M02 / M00 - ybar ** 2
    theta = 0.5 * math.atan2(2 * mu11, mu20 - mu02)
    raw = np.array([[M00, M10, M01, M11, M20, M02]])
    raw_moments = pd.DataFrame(raw, columns=["M00", "M10", "M01", "M11", "M20", "M02"])
    cov = np.array([[mu20, mu11], [mu11, mu02]])

    out = {'volume': M00, 'centroid': cen, 'OrientationAngle': theta,
           'raw_moments': raw, 'cov': cov, 'class': "imomented"}

    return out


def imomenter_matrix_one(look, label, ob_or_fo):
    grid0 = look["grid"]
    value = None
    if ob_or_fo == "ob":
        tmp = look['grd_ob_features'][label]
        value = look["grd_ob"].values.squeeze()
    elif ob_or_fo == "fo":
        tmp = look['grd_fo_features'][label]
        value = look["grd_fo"].values.squeeze()
    else:
        if label in look["grd_features"].keys():
            tmp = look['grd_features'][label]
        else:
            return None

    x = np.zeros((grid0.nlat, grid0.nlon))
    x[tmp] = 1
    x = x * value

    result_0 = imomenter_matrix_numpy(x.T)  #不带单位的结果
    result = {}
    result["volume"] = result_0["volume"] * grid0.dlon * grid0.dlat
    result["centroid"] = {"x":result_0["centroid"][0] * grid0.dlon + grid0.slon,
                            "y":result_0["centroid"][1] * grid0.dlat + grid0.slat}
    result["OrientationAngle"] = result_0["OrientationAngle"]
    result["cov"] = {
        "cov_xx":result_0["cov"][0,0] *  grid0.dlon * grid0.dlon,
        "cov_yy": result_0["cov"][1, 1] * grid0.dlat * grid0.dlat,
        "cov_xy": result_0["cov"][1, 0] * grid0.dlon* grid0.dlat
    }

    return result

def imomenter_matrix(look_merge):
    nmatch = look_merge["match_count"]
    out = {}
    out["time"] = meteva.base.all_type_time_to_str(look_merge["grd_fo"]["time"].values[0])
    out["dtime"] = int(look_merge["grd_fo"]["dtime"].values[0])
    out["member"] = look_merge["grd_fo"]["member"].values[0]
    out["match_count"] = nmatch


    label_list_matched = look_merge["label_list_matched"]
    out["label_list_matched"] = label_list_matched
    out["unmatched"] = look_merge["unmatched"]

    for i in label_list_matched:
        f_axis_ob = imomenter_matrix_one(look_merge, i, "ob")
        f_axis_fo = imomenter_matrix_one(look_merge, i, "fo")
        out1 = {}
        out1["imomenter_matrix"] = {"ob":f_axis_ob,"fo":f_axis_fo}
        out[i] = out1

    miss_labels = look_merge["unmatched"]['ob']
    for i in miss_labels:
        f_axis_ob = imomenter_matrix_one(look_merge, i, "ob")
        if i in out.keys():
            out1 = out[i]
            out1["imomenter_matrix"] = {"ob": f_axis_ob}
        else:
            out1 = {}
            out1["imomenter_matrix"] = {"ob":f_axis_ob}

        out[i] = out1


    false_alarm_labels = look_merge["unmatched"]["fo"]
    for i in false_alarm_labels:
        f_axis_fo = imomenter_matrix_one(look_merge, i, "fo")
        if i in out.keys():
            out1 = out[i]
            out1["feature_axis"] ={"fo": f_axis_fo}
        else:
            out1 = {}
            out1["feature_axis"] = {"fo": f_axis_fo}

        out[i] = out1

    return out


if __name__ == '__main__':

    import meteva.base as meb
    import meteva.method as mem
    # 读取观测和预报数据
    grid1 = meb.grid([100, 120, 0.05], [24, 40, 0.05])
    path_ob = r'H:\test_data\input\mem\mode\ob\rain03\20072611.000.nc'
    path_fo_03 = r'H:\test_data\input\mem\mode\ec\rain03\20072608.003.nc'
    path_fo_27 = r'H:\test_data\input\mem\mode\ec\rain03\20072508.027.nc'
    grd_ob = meb.read_griddata_from_nc(path_ob, grid=grid1, time="2020072611", dtime=0, data_name="OBS")
    grd_fo_03 = meb.read_griddata_from_nc(path_fo_03, grid=grid1, time="2020072608", dtime=3, data_name="ECMWF")
    grd_fo_27 = meb.read_griddata_from_nc(path_fo_27, grid=grid1, time="2020072508", dtime=27, data_name="ECMWF")
    look_ff = mem.mode.feature_finder(grd_ob, grd_fo_03, smooth=5, threshold=5, minsize=5)
    print("*** 目标识别完成 ***\n")
    look_match = mem.mode.centmatch(look_ff)
    look_merge = mem.mode.merge_force(look_match)
    result = imomenter_matrix(look_merge)
    print(result)