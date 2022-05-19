import copy
import pandas as pd
import numpy as np
from .centmatch import centmatch
from .deltamm import deltamm
from .minboundmatch import minboundmatch


def reset_label_id_by_area(look_merge):
    xfeats =look_merge['grd_ob_features']
    yfeats = look_merge['grd_fo_features']
    match_count = look_merge["match_count"]
    area_list = []
    for i in range(match_count):
        area_list.append(xfeats[i+1][0].size)
    area_array = np.array(area_list)
    sort_index = match_count - np.argsort(np.argsort(area_array))

    dlon_dlat = look_merge["grid"].dlon *  look_merge["grid"].dlat
    look_merge_new = copy.deepcopy(look_merge)
    for i in range(match_count):
        j = sort_index[i]
        look_merge_new["grd_ob_label"].values[look_merge["grd_ob_label"].values == i+1] = j
        look_merge_new["grd_fo_label"].values[look_merge["grd_fo_label"].values == i+1] = j
        look_merge_new["grd_ob_features"][j] = look_merge["grd_ob_features"][i+1]
        look_merge_new["grd_fo_features"][j] = look_merge["grd_fo_features"][i+1]

    for j in range(look_merge_new["grd_ob_features"]["label_count"]):
        look_merge_new["grd_ob_features"]["area"].append(look_merge_new["grd_ob_features"][j+1][0].size * dlon_dlat)
    for j in range(look_merge_new["grd_fo_features"]["label_count"]):
        look_merge_new["grd_fo_features"]["area"].append(look_merge_new["grd_fo_features"][j+1][0].size * dlon_dlat)

    return look_merge_new

def merge_force(look_match, verbose=False):
    x = copy.deepcopy(look_match)
    out = {}
    if x.__contains__('implicit_merges') and x.__contains__('merges'):
        print('MergeForce: both implicit_merges and merges components found.  Using merges component.')
        m = x['merges']
    elif not x.__contains__('implicit_merges') and not x.__contains__('merges'):
        if verbose:
            print('\nNo merges found.  Returning object x unaltered.\n')
        return x
    elif not x.__contains__('merges'):
        m = x['implicit_merges']
    else:
        m = x['merges']
    grid0 = x["grid"]
    out['grd_ob'] = x['grd_ob']
    out['grd_fo'] = x['grd_fo']
    out["grd_ob_smooth"] = x["grd_ob_smooth"]
    out["grd_fo_smooth"] = x["grd_fo_smooth"]
    #out['identifier_function'] = x['identifier_function']
    out['identifier_label'] = x['identifier_label']
    out['match_type'] = ['MergeForce', x['match_type']]
    out['match_message'] = ''.join((x['match_message'], " (merged) "))
    xdim = x['grd_ob'].values.squeeze().shape
    #print(xdim)
    if m == None:
        nmatches = 0
    else:
        nmatches = len(m)
    out["match_count"] = nmatches

    ar = np.arange(1, nmatches + 1, 1)
    matches = np.vstack((ar, ar)).T
    matches = pd.DataFrame(matches, columns = ["ob", "fo"])
    out['matches'] = matches.values
    #xp = x['Xlabelsfeature']
    #yp = x['Ylabelsfeature']
    xp = x['grd_ob_features']
    yp = x['grd_fo_features']
    #if len(xp.keys())==0 or len(yp.keys()) ==0:
    if xp["label_count"] == 0 or yp["label_count"] ==0:
        out['grd_ob_features'] = x["grd_ob_features"]
        out['grd_fo_features'] = x["grd_fo_features"]
        out['grd_ob_label'] = x["grd_ob_label"]
        out['grd_fo_label'] = x["grd_fo_label"]
        # vxunmatched = 0
        # if len(xp.keys()) >0:
        #     vxunmatched = list(range(1, len(xp.keys()) + 1))
        # fcunmatched=0
        # if len(yp.keys())>0:
        #     fcunmatched = list(range(1, len(yp.keys()) + 1))
        #out['unmatched'] = {'ob': vxunmatched, 'fo': fcunmatched}
        out["unmatched"] = x['unmatched']
        out['MergeForced'] = True
        out["grid"] = copy.deepcopy(look_match["grid"])
    else:

        xfeats = {'Type': xp['Type'], 'xrange': xp['xrange'], 'yrange': xp['yrange'], 'dim': xp['dim'], 'warnings': xp['warnings'],
                  'xstep': xp['xstep'], 'ystep': xp['ystep'], 'area': [], 'xcol': xp['xcol'], 'yrow': xp['yrow']}
        yfeats = {'Type': yp['Type'], 'xrange': yp['xrange'], 'yrange': yp['yrange'], 'dim': yp['dim'], 'warnings': yp['warnings'],
                  'xstep': yp['xstep'], 'ystep': yp['ystep'], 'area': [], 'xcol': yp['xcol'], 'yrow': yp['yrow']}
        xlabeled = np.zeros([xdim[0], xdim[1]], dtype=int)
        ylabeled = np.zeros([xdim[0], xdim[1]], dtype=int)

        if verbose:
            print("Loop through ", nmatches, " components of merges list to set up new (matched) features.\n")
        for i in range(nmatches):
            if verbose:
                print(i, " ")
            tmp = np.array(m[i])-1
            uX = sorted(set(tmp[:, 1]))
            uY = sorted(set(tmp[:, 0]))

            nX = len(uX)
            nY = len(uY)
            xtmp = np.zeros((grid0.nlat,grid0.nlon))
            ytmp = np.zeros((grid0.nlat, grid0.nlon))
            xtmp[xp[uX[0] + 1]] = 1
            ytmp[yp[uY[0] + 1]] = 1

            if nX > 1:
                for j in range(1, nX):
                    xtmp[xp[uX[j] + 1]] = 1

            if nY > 1:
                for k in range(1, nY):
                    ytmp[yp[uY[k] + 1]] = 1

            xfeats[i + 1] = np.where(xtmp>0)
            yfeats[i + 1] = np.where(ytmp>0)
            nozero = np.transpose(np.nonzero(xtmp))
            for j in np.arange(len(nozero)):
                xlabeled[nozero[j][0]][nozero[j][1]] = i + 1
            nozero = np.transpose(np.nonzero(ytmp))
            for j in np.arange(len(nozero)):
                ylabeled[nozero[j][0]][nozero[j][1]] = i + 1
        if x['unmatched']['ob'] == None or x['unmatched']['ob'] == 'NULL':
            unX = x['unmatched']['ob']
            nX2 = 0
        elif type(x['unmatched']['ob']) == int:
            unX = x['unmatched']['ob']-1
            nX2 = 1
        else:
            unX1 = sorted(x['unmatched']['ob'])
            unX = []
            nX2 = len(unX1)
            for nn in range(nX2):
                unX.append(unX1[nn]-1)

        if x['unmatched']['fo'] == None or x['unmatched']['fo'] == 'NULL':
            unY = x['unmatched']['fo']
            nY2 = 0
        elif type(x['unmatched']['fo']) == int:
            unY = x['unmatched']['fo']-1
            nY2 = 1
        else:
            unY1 = sorted(x['unmatched']['fo'])
            nY2 = len(unY1)
            unY = []
            for nn in range(nY2):
                unY.append(unY1[nn]-1)
        if nX2 > 0:
            if verbose:
                print("\nLoop to add/re-label all unmatched observed features.\n")
            vxunmatched = list(range((nmatches + 1), (nmatches + nX2 + 1)))
            for i in range(nX2):
                #xtmp = np.zeros((grid0.nlat,grid0.nlon))
                #xtmp[xp['labels_' + str(unX[i] + 1)]] = 1
                #xfeats[nmatches + i] = xtmp
                xtmp = xp[unX[i] + 1]
                xfeats[i + 1+nmatches] = xtmp
                xlabeled[xtmp] = i + 1+nmatches
                '''
                [rows, cols] = xtmp.shape
                for xi in range(rows):
                    for xj in range(cols):
                        if xtmp[xi, xj]:
                            #xlabeled[xi, xj] = nmatches + i + 1
                            xlabeled[xi, xj] = -1
                            '''
        else:
            vxunmatched = 0

        if nY2 > 0:
            if verbose:
                print("\nLoop to add/re-label all unmatched forecast features.\n")
            fcunmatched = list(range((nmatches + 1), (nmatches + nY2 + 1)))

            for i in range(nY2):
                ytmp = yp[unY[i] + 1]
                #ytmp[yp['labels_' + str(unY[i] + 1)]] = 1
                yfeats[i + 1+nmatches] = ytmp
                #yfeats[nmatches + i] = ytmp
                ylabeled[ytmp] =i + 1+nmatches
                '''
                [rows, cols] = ytmp.shape
                for yi in range(rows):
                    for yj in range(cols):
                        if ytmp[yi, yj]:
                            #ylabeled[yi, yj] = nmatches + i + 1
                            ylabeled[yi, yj] = -1
                            '''

            '''
            for i in range(nY2):
                ytmp = yp['labels_' + str(unY[i] + 1)]
                print(ytmp)
                yfeats['labels_' + str(i + 1)] = ytmp
                #yfeats[nmatches + i] = ytmp
                [rows, cols] = ytmp.shape
                for yi in range(rows):
                    for yj in range(cols):
                        if ytmp[yi, yj]:
                            #ylabeled[yi, yj] = nmatches + i + 1
                            ylabeled[yi, yj] = -1
            '''
        else:
            fcunmatched = 0
        xfeats["label_count"] = nmatches +nX2
        yfeats["label_count"] = nmatches +nY2
        out['grd_ob_features'] = xfeats
        out['grd_fo_features'] = yfeats
        grd_ob_labeled = x["grd_ob_label"]
        grd_ob_labeled.values[:] = xlabeled[:]
        out['grd_ob_label'] = grd_ob_labeled
        grd_fo_labeled = x["grd_fo_label"]
        grd_fo_labeled.values[:] = ylabeled[:]
        out['grd_fo_label'] = grd_fo_labeled
        out['unmatched'] = {'ob': vxunmatched, 'fo': fcunmatched}
        out['MergeForced'] = True
        out["grid"] = x["grid"]
        out = reset_label_id_by_area(out)
    return out



def merge(look_ff,match_method = centmatch,criteria = 1, const = 14, areafac = 1
          , p = 2, mindist = float('inf'),show = False):
    if match_method == centmatch:
        look_match = centmatch(look_ff,criteria = criteria, const = const,  show = show)
    elif match_method == deltamm:
        look_match = deltamm(look_ff, p = p,show=show)
    else:
        look_match = minboundmatch(look_ff,mindist = mindist, show=show)

    look_merge = merge_force(look_match)
    return look_merge


'''
if __name__ == '__main__':
    data = np.load(r"F:\Work\MODE\tra_test\centmatch\centmatchResult_PA3.npy", allow_pickle=True).tolist()
    look2 = merge_force(data)
    pyplot.imshow(look2['Xlabeled'])
    pyplot.colorbar()
    pyplot.figure(2)
    pyplot.imshow(look2['Ylabeled'])
    pyplot.colorbar()

    levels=np.linspace(0.5,np.max((look2['Xlabeled'], look2['Ylabeled'])) + 0.5,
                       np.max((look2['Xlabeled'], look2['Ylabeled']))+1)
    fig, ax = plt.subplots(1, 2, figsize = (10, 5))
    ax = ax.flatten()
    im1 = ax[0].contourf(look2['Xlabeled'], cmap = 'jet', levels = levels)
    im2 = ax[1].contourf(look2['Ylabeled'], cmap = 'jet', levels = levels)
    fig.colorbar(im2, ax=[ax[0], ax[1]], fraction=0.03, pad=0.05)
    pyplot.show()
    print("hello")
'''
