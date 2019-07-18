import numpy as np
import nmc_verification
import math

def interpolation_linear(grd, grid, other_info='left'):
    '''
    格点到格点插值
    :param grd:左边的网格数据信息
    :param grid :右边的网格数据信息
    :other_info:网格数据除了xy方向的数值之外，还有time,dtime，leve member 等维度的值，如果other_info= 'left’则返回结果中这些维度的值就采用grd里的值，
    否则采用grid里的值，默认为：left
    :return:双线性插值之后的结果
    
    '''
    if (grd is None):
        return None

    # 六维转换为二维的值
    dat0 = grd.values
    dat = np.squeeze(dat0)

    grd0 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd)
    if (grd0.dlon * grd0.nlon >= 360):
        grd1 = nmc_verification.nmc_vf_base.basicdata.grid([grd0.slon, grd0.elon + grd0.dlon,grd0.dlon],[grd0.slat, grd0.elat, grd0.dlat])
        dat1 = np.zeros((grd1.nlat,grd1.nlon))
        dat1[:,0:-1] = dat[:,:]
        dat1[:, -1] = dat[:, 0]
    else:
        dat1 = dat
        grd1 = grd0
    if other_info=='left':
        grd2 = nmc_verification.nmc_vf_base.basicdata.grid(grid.glon,grid.glat,grd0.gtime,grd0.dtimes,grd0.levels,grd0.members)
    else:
        grd2 = grid.copy()

    if (grd2.elon > grd1.elon or grd2.slon < grd1.slon or grd2.elat > grd1.elat or grd2.slat < grd1.slat):
        print("object grid is out range of original grid")
        return None

    #插值处理
    x = ((np.arange(grd2.nlon) * grd2.dlon + grd2.slon - grd1.slon) / grd1.dlon)
    ig = x[:].astype(dtype='int16')
    dx = x - ig
    y = (np.arange(grd2.nlat) * grd2.dlat + grd2.slat - grd1.slat) / grd1.dlat
    jg = y[:].astype(dtype='int16')
    dy = y[:] - jg
    ii, jj = np.meshgrid(ig, jg)
    ii1 = np.minimum(ii + 1, grd1.nlon - 1)
    jj1 = np.minimum(jj + 1, grd1.nlat - 1)
    ddx, ddy = np.meshgrid(dx, dy)
    c00 = (1 - ddx) * (1 - ddy)
    c01 = ddx * (1 - ddy)
    c10 = (1 - ddx) * ddy
    c11 = ddx * ddy
    dat2 = (c00 *dat1[jj, ii] + c10 * dat1[jj1, ii] + c01 * dat1[jj, ii1] + c11 * dat1[jj1, ii1])
    grd_new = nmc_verification.nmc_vf_base.basicdata.grid_data(grd2,dat2)
    return grd_new

def add(grd1,grd2,other_info = 'left'):
    '''
    将插值之后的多个结果在原有存储数据结构的基础上进行追加。
    :param grd1:左边的网格数据信息
    :param grd1 :右边的网格数据信息
    :other_info:网格数据除了xy方向的数值之外，还有time,dtime，leve member 等维度的值，如果other_info= 'left’则返回结果中这些维度的值就采用grd里的值，
    否则采用grid里的值，默认为：left
    :return:多个网格数据双线性插值之后的结果的追加
    '''
    if(grd1 is None):
        return grd2
    elif(grd2 is None):
        return grd1
    else:
        grid1 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd1)
        grid2 = nmc_verification.nmc_vf_base.basicdata.get_grid_of_data(grd2)
        slon = max(grid1.slon,grid2.slon)
        elon = min(grid1.elon,grid2.elon)
        slat = max(grid1.slat,grid2.slat)
        elat = min(grid1.elat,grid2.elat)
        if other_info == 'left':
            grid_in = nmc_verification.nmc_vf_base.basicdata.grid([slon,elon,grid1.dlon],[slat,elat,grid1.dlat],grid1.gtime,grid1.dtimes,grid1.levels,grid1.members)
        else:
            grid_in = nmc_verification.nmc_vf_base.basicdata.grid([slon, elon, grid2.dlon], [slat, elat, grid2.dlat], grid2.gtime, grid2.dtimes, grid2.levels,
                              grid2.members)
        grd1_in = interpolation_linear(grd1, grid_in)
        grd2_in = interpolation_linear(grd2, grid_in)
        grd = nmc_verification.nmc_vf_base.basicdata.grid_data(grid_in,grd1_in.values + grd2_in.values)
        return grd



def mean_convolve(grd, half_window_size, skip=1):
    # 该函数计算网格点附近矩形方框内的平均值
    # 使用同规格的场，确保网格范围和分辨率一致
    # window_size 窗口尺度，为了避免窗口较大时计算太慢，可选择跳点取平均，再插值回到原始分辨率
    if (skip > half_window_size):
        print("pdf_skip is larger than half pdf_window_size")
        return None
    grid0 = nmc_verification.nmc_vf_base.get_grid_of_data(grd)

    step_num_lon = int(math.ceil((grid0.nlon - 1) / skip)) + 1
    dlon_skip = grid0.dlon * skip
    elon_skip = grid0.slon + dlon_skip * (step_num_lon - 1)

    step_num_lat = int(math.ceil((grid0.nlat - 1) / skip)) + 1
    dlat_skip = grid0.dlat * skip
    elat_skip = grid0.slat + dlat_skip * (step_num_lat - 1)

    grid_skip = nmc_verification.nmc_vf_base.grid([grid0.slon, elon_skip, dlon_skip],
                                                  [grid0.slat, elat_skip, dlat_skip])
    dat0 = grd.values.squeeze()
    dat = np.zeros((step_num_lat, step_num_lon))

    cycle0 = step_num_lat * step_num_lon
    cycle1 = (half_window_size * 2 + 1) * (half_window_size * 2 + 1)

    if cycle0 < cycle1:
        for j in range(step_num_lat):
            j_start = max(0,j * skip - half_window_size)
            j_end = min(grid0.nlat,j * skip + half_window_size)+1
            for i in range(step_num_lon):
                i_start = max(0, i * skip - half_window_size)
                i_end = min(grid0.nlon, i * skip + half_window_size)+1
                dat[j,i] = np.mean(dat0[j_start:j_end,i_start:i_end])
    else:
        for p in range(-half_window_size, half_window_size + 1):
            j = np.arange(step_num_lat) * skip + p
            j[j < 0] = 0
            j[j > grid0.nlat - 1] = grid0.nlat - 1
            for q in range(-half_window_size, half_window_size + 1):
                i = np.arange(step_num_lon) * skip + q
                i[i < 0] = 0
                i[i > grid0.nlon - 1] = grid0.nlon - 1
                ii, jj = np.meshgrid(i, j)
                dat += dat0[jj, ii]
        dat /= cycle1

    grd_mean_skip = nmc_verification.nmc_vf_base.grid_data(grid_skip, dat)
    grd_mean = nmc_verification.nmc_vf_base.function.gxy_gxy.interpolation_linear(grd_mean_skip, grid0)

    return grd_mean