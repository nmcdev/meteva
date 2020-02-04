import nmc_verification
import numpy as np
from scipy.spatial import cKDTree
from scipy.interpolate import LinearNDInterpolator
import copy


#格点到站点的插值
def interp_gs_nearest(grd,sta,used_coords = "xy"):
    '''
    :param grd:
    :param sta:
    :return:
    '''
    levels = copy.deepcopy(grd["level"].values)
    times = copy.deepcopy(grd["time"].values)
    dtimes = copy.deepcopy(grd["dtime"].values)
    members = copy.deepcopy(grd["member"].values)
    column_list1 = ['lon', 'lat']
    column_list1.extend(members)
    column_list2 = ['level','time','dtime','id', 'lon', 'lat']
    column_list2.extend(members)
    grid = nmc_verification.nmc_vf_base.get_grid_of_data(grd)
    sta_all = None
    if used_coords == "xy":
        sta1 = nmc_verification.nmc_vf_base.sele.in_grid_xy(sta, grid)
        ig = np.round((sta1['lon'].values - grid.slon) // grid.dlon).astype(dtype = 'int16')
        jg = np.round((sta1['lat'].values - grid.slat) // grid.dlat).astype(dtype = 'int16')
        for i in range(len(levels)):
            for j in range(len(times)):
                for k in range(len(dtimes)):
                    sta = sta1.loc[:,["id","lon","lat"]]
                    sta.loc[:,'time'] = times[j]
                    sta.loc[:,'dtime'] = dtimes[k]
                    sta.loc[:,'level'] = levels[i]
                    for m in range(len(members)):
                        dat = grd.values[m,i,j,k,:,:]
                        dat_sta= dat[jg,ig]
                        sta.loc[:,members[m]] = dat_sta
                    sta_all = nmc_verification.nmc_vf_base.combine_join(sta_all,sta)
        sta_all = sta_all.reindex(columns=column_list2)
        return sta_all


#格点到站点的插值,线性
def interp_gs_linear(grd,sta,used_coords = "xy"):
    #print("**0")
    levels = copy.deepcopy(grd["level"].values)
    times = copy.deepcopy(grd["time"].values)
    dtimes = copy.deepcopy(grd["dtime"].values)
    members = copy.deepcopy(grd["member"].values)
    column_list1 = ['lon', 'lat']
    column_list1.extend(members)
    column_list2 = ['level','time','dtime','id', 'lon', 'lat']
    column_list2.extend(members)
    grid = nmc_verification.nmc_vf_base.get_grid_of_data(grd)
    sta_all = None
    if used_coords == "xy":
        sta1 = nmc_verification.nmc_vf_base.sele.in_grid_xy(sta, grid)
        ig = ((sta1['lon'].values - grid.slon) // grid.dlon).astype(dtype = 'int16')
        jg = ((sta1['lat'].values - grid.slat) // grid.dlat).astype(dtype = 'int16')
        dx = (sta1['lon'].values - grid.slon) / grid.dlon - ig
        dy = (sta1['lat'].values - grid.slat) / grid.dlat - jg
        c00 = (1 - dx) * (1 - dy)
        c01 = dx * (1 - dy)
        c10 = (1-dx) * dy
        c11 = dx * dy
        ig1 = np.minimum(ig + 1, grid.nlon - 1)
        jg1 = np.minimum(jg + 1, grid.nlat - 1)

        for i in range(len(levels)):
            for j in range(len(times)):
                for k in range(len(dtimes)):
                    sta = sta1.loc[:,[ "id", "lon", "lat"]]
                    sta['time'] = times[j]
                    sta.loc[:,'dtime'] = dtimes[k]
                    sta.loc[:,'level'] = levels[i]
                    for m in range(len(members)):
                        dat = grd.values[m,i,j,k,:,:]
                        dat_sta= c00 * dat[jg,ig] + c01 * dat[jg,ig1] + c10 * dat[jg1,ig] + c11 * dat[jg1,ig1]
                        sta.loc[:,members[m]] = dat_sta
                    sta_all = nmc_verification.nmc_vf_base.combine_join(sta_all,sta)
        sta_all = sta_all.reindex(columns=column_list2)
        return sta_all

    elif used_coords == "xyz":
        sta1 = nmc_verification.nmc_vf_base.sele.in_grid_xyz(sta, grid)
        lev_s = sta1["level"].values[:]
        lev_g = np.array(grid.levels)
        kg = nmc_verification.nmc_vf_base.tool.math_tools.get_index(lev_s,grid.levels)
        kg1 = np.minimum(kg + 1, len(grid.levels) - 1)
        ig = ((sta1['lon'] - grid.slon) // grid.dlon).astype(dtype='int16')
        jg = ((sta1['lat'] - grid.slat) // grid.dlat).astype(dtype='int16')
        dx = (sta1['lon'] - grid.slon) / grid.dlon - ig
        dy = (sta1['lat'] - grid.slat) / grid.dlat - jg
        dz = (lev_s - lev_g[kg])/(lev_g[kg1] - lev_g[kg] + 1e-30)
        c00 = (1 - dx) * (1 - dy)
        c01 = dx * (1 - dy)
        c10 = (1 - dx) * dy
        c11 = dx * dy
        ig1 = np.minimum(ig + 1, grid.nlon - 1)
        jg1 = np.minimum(jg + 1, grid.nlat - 1)
        sta_all = None
        for j in range(len(times)):
            for k in range(len(dtimes)):
                sta = sta1[["level","id","lon","lat"]]
                sta.loc[:,'time'] = times[j]
                sta.loc[:,'dtime'] = dtimes[k]
                for m in range(len(members)):
                    dat = grd.values[m,:,j,k,:,:]
                    dat_sta= (c00 * dat[kg,jg,ig] + c01 * dat[kg,jg,ig1] + c10 * dat[kg,jg1,ig] + c11 * dat[kg,jg1,ig1]) * (1-dz)
                    dat_sta += (c00 * dat[kg1, jg, ig] + c01 * dat[kg1, jg, ig1] + c10 * dat[kg1, jg1, ig] + c11 * dat[
                        kg1, jg1, ig1]) *  dz
                    sta.loc[:,members[m]] = dat_sta
                sta_all = nmc_verification.nmc_vf_base.combine_join(sta_all,sta)
        sta_all = sta_all.reindex(columns=column_list2)
        return sta_all

    elif used_coords =="xydt":
        if(len(grid.dtimes) == 1):
            print("dtime维度size = 1,无法开展dtime维度插值")
            return
        '''
        还有问题
        '''
        sta1 = nmc_verification.nmc_vf_base.sele.in_grid_xy(sta, grid)
        sta1 = nmc_verification.nmc_vf_base.sele.between_dtime_range(sta1,grid.dtimes[0],grid.dtimes[-1])
        dtime_g = np.array(grid.dtimes)
        lon_g = grd["lon"].values
        lat_g = grd["lat"].values

        coords_g = np.zeros((dtime_g.size, lat_g.size, lat_g.size, 3))
        coords_g[..., 0] = dtime_g.reshape((dtime_g.size,1, 1))
        coords_g[..., 1] = lat_g.reshape((1, lat_g.size, 1))
        coords_g[..., 2] = lon_g.reshape((1,1, lon_g.size))
        coords_g = coords_g.reshape((dtime_g.size * lat_g.size * lat_g.size, 3))

        coords_s = np.zeros((len(sta1.index), 3))
        coords_s[:, 0] = sta1["dtime"].values
        coords_s[:, 1] = sta1["lat"].values
        coords_s[:, 2] = sta1["lon"].values
        sta_all = None
        for j in range(len(times)):
            for k in range(len(levels)):
                sta = sta1.loc[:,["dtime","id","lon","lat"]]
                sta.loc[:,'time'] = times[j]
                sta.loc[:,'level'] = levels[k]
                for m in range(len(members)):
                    dat_g = grd.values[m,k,j,:,:,:]
                    interpolator = LinearNDInterpolator(coords_g, dat_g.reshape((dat_g.size)))
                    dat_s = interpolator(coords_s)
                    sta.loc[:, members[m]] = dat_s
                sta_all = nmc_verification.nmc_vf_base.combine_join(sta_all,sta)
        sta_all = sta_all.reindex(columns=column_list2)
        return sta_all


#格点到站点的插值，三次
def interp_gs_cubic(grd,sta,used_coords = "xy"):
    levels = grd["level"].values
    times = grd["time"].values
    dtimes = grd["dtime"].values
    members = grd["member"].values
    column_list1 = ['lon', 'lat']
    column_list1.extend(members)
    column_list2 = ['level','time','dtime','id', 'lon', 'lat']
    column_list2.extend(members)
    grid = nmc_verification.nmc_vf_base.get_grid_of_data(grd)
    sta_all = None
    if used_coords == "xy":
        sta1 = nmc_verification.nmc_vf_base.sele.in_grid_xy(sta, grid)
        ig = ((sta1['lon'] - grid.slon) // grid.dlon).astype(dtype='int16')
        jg = ((sta1['lat'] - grid.slat) // grid.dlat).astype(dtype='int16')
        dx = (sta1['lon'] - grid.slon) / grid.dlon - ig
        dy = (sta1['lat'] - grid.slat) / grid.dlat - jg
        for i in range(len(levels)):
            for j in range(len(times)):
                for k in range(len(dtimes)):
                    sta = sta1[["id","lon","lat"]]
                    sta.loc[:,'time'] = times[j]
                    sta.loc[:,'dtime'] = dtimes[k]
                    sta.loc[:,'level'] = levels[i]
                    for m in range(len(members)):
                        dat = grd.values[m,i,j,k,:,:]
                        sum = np.zeros(len(sta.index))
                        for p in range(-1, 3, 1):
                            iip = np.minimum(np.maximum(ig + p, 0), grid.nlon - 1)
                            fdx = cubic_f(p, dx)
                            for q in range(-1, 3, 1):
                                jjq = np.minimum(np.maximum(jg + q, 0), grid.nlat - 1)
                                fdy = cubic_f(q, dy)
                                fdxy = fdx * fdy
                                sum[:] += fdxy * dat[jjq, iip]
                        sta.loc[:, members[m]] =sum
                    sta_all = nmc_verification.nmc_vf_base.combine_join(sta_all,sta)
        sta_all = sta_all.reindex(columns=column_list2)
        return sta_all


    grid = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd)
    sta1 = nmc_verification.nmc_vf_base.sele.in_grid_xy(sta, grid)
    dat0 = grd.values
    dat = np.squeeze(dat0)
    ig = ((sta1['lon'] - grid.slon) // grid.dlon).astype(dtype = 'int16')
    jg = ((sta1['lat'] - grid.slat) // grid.dlat).astype(dtype = 'int16')
    dx = (sta1['lon'] - grid.slon) / grid.dlon - ig
    dy = (sta1['lat'] - grid.slat) / grid.dlat - jg
    data_name = nmc_verification.nmc_vf_base.get_stadata_names(sta1)[0]
    for p in range(-1,3,1):
        iip = np.minimum(np.maximum(ig+p,0),grid.nlon-1)
        fdx = cubic_f(p, dx)
        for q in range(-1,3,1):
            jjq = np.minimum(np.maximum(jg+q,0),grid.nlat-1)
            fdy = cubic_f(q,dy)
            fdxy = fdx * fdy
            sta1[data_name] +=  fdxy * dat[jjq,iip]
    sta1['time'] = grid.stime
    sta1['dtime'] = grid.dtimes[0]
    sta1['level'] = grid.levels[0]
    nmc_verification.nmc_vf_base.basicdata.set_stadata_names(sta1,grid.members)
    return sta1


def interp_sg_idw(sta, grid1, background=None, effectR=1000, nearNum=8):

    data_name = nmc_verification.nmc_vf_base.get_stadata_names(sta)
    index0 = sta.index[0]
    grid2 = nmc_verification.nmc_vf_base.basicdata.grid(grid1.glon, grid1.glat, [sta.loc[index0, 'time']],
                                                       [sta.loc[index0, 'dtime']],
                                                       [sta.loc[index0, 'level']], data_name)
    xyz_sta = nmc_verification.nmc_vf_base.tool.math_tools.lon_lat_to_cartesian(sta['lon'].values,
                                                                                sta['lat'].values,
                                                                                R=nmc_verification.nmc_vf_base.basicdata.const.ER)
    lon = np.arange(grid2.nlon) * grid2.dlon + grid2.slon
    lat = np.arange(grid2.nlat) * grid2.dlat + grid2.slat
    grid_lon, grid_lat = np.meshgrid(lon, lat)
    xyz_grid = nmc_verification.nmc_vf_base.tool.math_tools.lon_lat_to_cartesian(grid_lon.flatten(),
                                                                                 grid_lat.flatten(),
                                                                                 R=nmc_verification.nmc_vf_base.basicdata.const.ER)
    tree = cKDTree(xyz_sta)
    # d,inds 分别是站点到格点的距离和id
    if nearNum > len(sta.index):
        nearNum = len(sta.index)
    d, inds = tree.query(xyz_grid, k=nearNum)
    d += 1e-6
    w = 1.0 / d ** 2
    input_dat = sta.values[:,-1]
    dat = np.sum(w * input_dat[inds], axis=1) / np.sum(w, axis=1)
    bg = nmc_verification.nmc_vf_base.basicdata.grid_data(grid2)
    if (background is not None):
        bg = interp_gg_linear(background, grid2)
    bg_dat = bg.values.flatten()
    dat = np.where(d[:, 0] > effectR, bg_dat, dat)
    grd = nmc_verification.nmc_vf_base.basicdata.grid_data(grid2, dat)
    grd.name = "data0"
    return grd


def interp_gg_linear(grd, grid1,used_coords = "xy"):
    '''
    格点到格点插值
    :param grd:左边的网格数据信息
    :param grid1 :右边的网格数据信息
    :other_info:网格数据除了xy方向的数值之外，还有time,dtime，leve member 等维度的值，如果other_info= 'left’则返回结果中这些维度的值就采用grd里的值，
    否则采用grid里的值，默认为：left
    :return:双线性插值之后的结果
    '''
    if (grd is None):
        return None

    levels = grd["level"].values
    times = grd["time"].values
    dtimes = grd["dtime"].values
    members = grd["member"].values
    lons = grd['lon'].values
    lats = grd['lat'].values
    grid0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd)

    grd_new = None
    if used_coords == "xy":
        if (grid0.dlon * grid0.nlon >= 360):
            grid_1 = nmc_verification.nmc_vf_base.basicdata.grid([grid0.slon, grid0.elon + grid0.dlon, grid0.dlon],
                [grid0.slat, grid0.elat, grid0.dlat],grid0.gtime,grid0.dtimes,grid0.levels,grid0.members)
        else:
            grid_1 = grid0
        grid2 = nmc_verification.nmc_vf_base.basicdata.grid(grid1.glon, grid1.glat, grid0.gtime, grid0.dtimes, grid0.levels,
                                                           grid1.members)
        if (grid2.elon > grid_1.elon or grid2.slon < grid_1.slon or grid2.elat > grid_1.elat or grid2.slat < grid_1.slat):
            print("object grid is out range of original grid")
            return None
        grd_new = nmc_verification.nmc_vf_base.grid_data(grid2)
        for i in range(len(levels)):
            for j in range(len(times)):
                for k in range(len(dtimes)):
                    for m in range(len(members)):
                        # 六维转换为二维的值
                        dat = grd.values[m,i,j,k,:,:]
                        if (grid0.dlon * grid0.nlon >= 360):
                            dat1[:,0:-1] = dat[:,:]
                            dat1[:, -1] = dat[:, 0]
                        else:
                            dat1 = dat
                        #插值处理
                        x = ((np.arange(grid2.nlon) * grid2.dlon + grid2.slon - grid_1.slon) / grid_1.dlon)
                        ig = x[:].astype(dtype='int16')
                        dx = x - ig
                        y = (np.arange(grid2.nlat) * grid2.dlat + grid2.slat - grid_1.slat) / grid_1.dlat
                        jg = y[:].astype(dtype='int16')
                        dy = y - jg
                        ii, jj = np.meshgrid(ig, jg)
                        ii1 = np.minimum(ii + 1, grid_1.nlon - 1)
                        jj1 = np.minimum(jj + 1, grid_1.nlat - 1)
                        ddx, ddy = np.meshgrid(dx, dy)
                        c00 = (1 - ddx) * (1 - ddy)
                        c01 = ddx * (1 - ddy)
                        c10 = (1 - ddx) * ddy
                        c11 = ddx * ddy
                        dat2 = (c00 *dat1[jj, ii] + c10 * dat1[jj1, ii] + c01 * dat1[jj, ii1] + c11 * dat1[jj1, ii1])
                        grd_new.values[m,i,j,k,:,:] = dat2
    return grd_new


def cubic_f(n, dx):
    if (n == -1):
        return -dx * (dx - 1) * (dx - 2) / 6
    elif (n == 0):
        return (dx + 1) * (dx - 1) * (dx - 2) / 2
    elif (n == 1):
        return -(dx + 1) * dx * (dx - 2) / 2
    else:
        return (dx + 1) * dx * (dx - 1) / 6

