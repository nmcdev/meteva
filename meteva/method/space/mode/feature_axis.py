# -*-coding:utf-8-*-
import pandas as pd
import cv2
import copy
#import sys
#sys.path.append(r'F:\Work\MODE\Submit')
from . import utils
from .distmap import *
from .sma import sma
from . import angles_psp
from . import lengths_psp
from . import midpoints_psp
from . import as_psp



def feature_axis(look,label,ob_or_fo = "ob",fac = 1, flipit=False, twixt=False):

    grid0 = look["grid"]
    if ob_or_fo =="ob":
        tmp = look['grd_ob_features'][label]
    else:
        tmp = look['grd_fo_features'][label]
    x = np.zeros((grid0.nlat,grid0.nlon))
    x[tmp] = 1
    out = {}
    if flipit:
        x = np.transpose(x)

    out['point'] = getRedDotsCoordinatesFromLeftToRight(x)
    out["point"][:,0] = grid0.slon +  out["point"][:,0] * grid0.dlon
    out["point"][:,1] = grid0.slon + out["point"][:,1] * grid0.dlon
    # img = Image.fromarray(x['labels_1']).convert('RGB')
    ch = cv2.convexHull(getRedDotsCoordinatesFromLeftToRight(x))
    #out['chull'] = ch
    # pts = np.hstack(ch['bdry'][[1]][["x"]], ch['bdry'][[1]][["y"]])
    pts = np.zeros([len(ch), 2])
    for index in range(len(ch)):
        pts[index] = (ch[index][0])



    out['pts'] = pts
    out["pts"][:,0] = grid0.slon + out["pts"][:,0] * grid0.dlon
    out["pts"][:,1] = grid0.slat + out["pts"][:,1] * grid0.dlat

    axfit_frame = {'x': pts[:, 0], 'y': pts[:, 1]}
    axfit = sma(axfit_frame)
    axis_x = np.array([axfit['from'], axfit['to']])
    a = axfit['coef']['slope']
    b = axfit['coef']['intercept']
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
    l = tmp['x_range'][1] - tmp['x_range'][0]
    theta = theta * 180 / math.pi
    if twixt:
        if 90 < theta <= 270:
            theta = theta - 180
        elif 270 < theta <= 360:
            theta = theta - 360
    MidPoint = midpoints_psp.midpoints_psp(axis_frame)

    r = lengths_psp.lengths_psp(axis_frame) * fac
    phi = angles_psp.angles_psp(rotate(np.array([[axis_x[0], axis_y[0]], [axis_x[1], axis_y[1]]]), math.pi / 2))
    minor_frame = {'xmid': MidPoint['x'], 'ymid': MidPoint['y'], 'length': l/fac, 'angle': phi}
    MinorAxis = as_psp.as_psp(minor_frame)
    phi = phi * 180 / math.pi
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