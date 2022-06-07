# -*-coding:utf-8-*-

from .distmap import *
from .sma import sma
from . import angles_psp
from . import midpoints_psp
from . import as_psp


def convexHull(rx0):
    max_v = np.max(rx0)
    min_v = np.min(rx0)
    d = rx0[:,0] + (rx0[:,1] - min_v)/max_v
    rx = rx0[d.argsort()]
    #先求下包络线
    # 首先用一根皮筋从头连到尾
    line_low = rx.copy().tolist()
    len0 = -1
    while len(line_low) != len0:
        len0 = len(line_low)
        line_list = [line_low[0]]
        for i in range(1,len0-1):
            dx1 = line_low[i][0] - line_low[i-1][0]
            dy1 = line_low[i][1] - line_low[i-1][1]
            dx2 = line_low[i+1][0] - line_low[i - 1][0]
            dy2 = line_low[i+1][1] - line_low[i - 1][1]
            cross = dx1 * dy2 - dy1 * dx2
            if cross>0:
                line_list.append(line_low[i])  # 相邻两个点是逆时针选择则保留，否则松开
        line_list.append(line_low[-1])
        line_low = line_list

    #再求上包络线
    # 首先用一根皮筋从头连到尾
    line_up = rx.tolist()
    len0 = -1
    while len(line_up) != len0:
        len0 = len(line_up)
        line_list = [line_up[0]]
        for i in range(1,len0-1):
            dx1 = line_up[i][0] - line_up[i-1][0]
            dy1 = line_up[i][1] - line_up[i-1][1]
            dx2 = line_up[i+1][0] - line_up[i - 1][0]
            dy2 = line_up[i+1][1] - line_up[i - 1][1]
            cross = dx1 * dy2 - dy1 * dx2
            if cross<0:
                line_list.append(line_up[i])  # 相邻两个点是顺时针选择则保留，否则松开
        line_list.append(line_up[-1])
        line_up = line_list

    #将上下两根包络线想连

    line_all = []
    for i in range(len0-1,0,-1):
        line_all.append(line_up[i])
    line_all.extend(line_low[0:-1])

    result = np.array(line_all).astype(np.float32)
    return result

def caculate_feature_axis(pts,fac = 1, twixt = False):
    axfit_frame = {'x': pts[:, 0], 'y': pts[:, 1]}
    axfit = sma(axfit_frame)
    axis_x = np.array([axfit['from'], axfit['to']])
    # a = axfit['coef']['slope']
    # b = axfit['coef']['intercept']
    a = axfit["slope"]
    b = axfit["intercept"]
    axis_y = b + a * axis_x

    if axis_x[0] is None or axis_x[1] is None or axis_y[0] is None or axis_y[1] is None:
        return None
    # axwin = owin(xrange = range(axis_x), yrange = range(axis_y))
    axis_frame = {'x0': axis_x[0], 'y0': axis_y[0], 'x1': axis_x[1], 'y1': axis_y[1]}
    # MajorAxis = as.psp(pd.DataFrame(axis_frame), window=axwin)
    theta = angles_psp.angles_psp(axis_frame)
    if 0 <= theta <= math.pi / 2:
        theta2 = math.pi / 2 - theta
    else:
        theta2 = 3 * math.pi / 2 - theta
    tmp = rotate(pts, theta2)
    tmp = boundingbox(tmp, tmp)
    l = float(tmp['x_range'][1] - tmp['x_range'][0])
    theta = theta * 180 / math.pi
    if twixt:
        if 90 < theta <= 270:
            theta = theta - 180
        elif 270 < theta <= 360:
            theta = theta - 360
    MidPoint = midpoints_psp.midpoints_psp(axis_frame)
    #r = lengths_psp.lengths_psp(axis_frame) * fac
    r = float(tmp["y_range"][1] - tmp["y_range"][0])
    phi = angles_psp.angles_psp(rotate(np.array([[axis_x[0], axis_y[0]], [axis_x[1], axis_y[1]]]), math.pi / 2))
    minor_frame = {'xmid': MidPoint['x'], 'ymid': MidPoint['y'], 'length': l/fac, 'angle': phi}
    MinorAxis = as_psp.as_psp(minor_frame)
    phi = phi * 180 / math.pi
    out = {}
    out['phi'] = phi
    out['MajorAxis'] = {'ends': axis_frame}
    out['MinorAxis'] = MinorAxis
    out['OrientationAngle'] = {'MajorAxis': theta, 'MinorAxis': phi}
    out['aspect_ratio'] = l / r
    out["MidPoint"] = {}
    out['MidPoint']["x"] = MidPoint["x"]
    out["MidPoint"]["y"] = MidPoint["y"]
    out["window"] = MidPoint["window"]
    out['lengths'] = {'MajorAxis': r, 'MinorAxis': l}
    out['sma_fit'] = axfit
    return out

def feature_axis(look,label,ob_or_fo = "ob",fac = 1, flipit=False, twixt=False):

    grid0 = look["grid"]
    if ob_or_fo =="ob":
        tmp = look['grd_ob_features'][label]
    elif ob_or_fo == "fo":
        tmp = look['grd_fo_features'][label]
    else:
        if label in look["grd_features"].keys():
            tmp = look['grd_features'][label]
        else:
            return None
    x = np.zeros((grid0.nlat,grid0.nlon))
    x[tmp] = 1
    out = {}
    if flipit:
        x = np.transpose(x)

    rx = getRedDotsCoordinatesFromLeftToRight(x)
    pts = convexHull(rx)
    out['point'] = rx
    out["point"][:,0] = grid0.slon +  out["point"][:,0] * grid0.dlon
    out["point"][:,1] = grid0.slon + out["point"][:,1] * grid0.dlon

    out['pts'] = pts
    out["pts"][:,0] = grid0.slon + out["pts"][:,0] * grid0.dlon
    out["pts"][:,1] = grid0.slat + out["pts"][:,1] * grid0.dlat

    out1 = caculate_feature_axis(pts,fac=fac,twixt=twixt)
    out.update(out1)

    return out

'''
if __name__ == '__main__':
    data = np.load("../../centmatchResult_PA3.npy", allow_pickle=True).tolist()
    XtmpAttributes = utils.get_attributes_for_feat(data['Xlabelsfeature'])
    remove_list = ['Type', 'xrange', 'yrange', 'dim', 'xstep', 'ystep', 'warnings', 'xcol', 'ycol']
    xkeys = utils.remove_key_from_list(list(data['Xlabelsfeature'].keys()), remove_list)
    Xtmp = {"m": data['Xlabelsfeature']['labels_5']}
    Xtmp.update(XtmpAttributes)
    look_feature_axis = feature_axis(Xtmp)

#data = np.load(r'F:\Work\MODEtra_test\FeatureFinder\deltammResult_PA3.npy', allow_pickle = True).tolist()
data = look_deltamm.copy()
XtmpAttributes = utils.get_attributes_for_feat(data['Xlabelsfeature'])
remove_list = ['Type', 'xrange', 'yrange', 'dim', 'xstep', 'ystep', 'warnings', 'xcol', 'ycol']
xkeys = utils.remove_key_from_list(list(data['Xlabelsfeature'].keys(    )), remove_list)
Xtmp = {"m": data['Xlabelsfeature']['labels_5']}
Xtmp.update(XtmpAttributes)
look_feature_axis = feature_axis(Xtmp)
'''