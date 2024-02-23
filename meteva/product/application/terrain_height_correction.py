import meteva
import os
import urllib.request

'''
def terrain_height_correction(sta_all,start = 1):
    delta = meteva.base.read_stadata_from_micaps3(meteva.base.terrain_height_correction_data)
    ids = list(set(sta_all["id"].values.tolist()))
    delta = meteva.base.in_id_list(delta,ids)
    #print(delta)
    delta["level"] = meteva.base.IV
    delta["time"] = meteva.base.IV
    delta["dtime"] = meteva.base.IV
    datanames = meteva.base.get_stadata_names(sta_all)
    sta_all_delta = meteva.base.combine_expand_IV(sta_all,delta)
    for i in range(start,len(datanames)):
        name = datanames[i]
        sta_all_delta[name] += sta_all_delta.iloc[:,-1]
    datanames = meteva.base.get_stadata_names(sta_all_delta)
    sta_all_corrected = sta_all_delta.drop(columns = [datanames[-1]])
    return sta_all_corrected
'''

def terrain_height_correct(sta_temp, grid, sta_alt = None, member_list =  None,rate = 0.6):
    '''

    :param sta_temp:
    :param grid:
    :param sta_alt:
    :param member_list:
    :param rate:
    :return:
    '''
    grd_alt_path = meteva.base.terrain_height_grd
    if not os.path.exists(grd_alt_path):
        url = "https://github.com/nmcdev/meteva/raw/master/meteva/resources/stations/dem_0.00833.nc"
        try:
            print("开始从github下载地形高度数据，请稍等")
            urllib.request.urlretrieve(url, filename=grd_alt_path)
        except Exception as e:
            print("从github下载地形高度数据失败，请重试，或者手动从\n"+url+"\n下载文件并保存至\n"+grd_alt_path)
            print(e)


    grd_alt = meteva.base.read_griddata_from_nc(grd_alt_path)
    grd_alt.values[grd_alt.values<0] = 0
    grid_alt = meteva.base.get_grid_of_data(grd_alt)
    grid_inner = meteva.base.get_inner_grid(grid,grid_alt)
    grd_alt = meteva.base.interp_gg_linear(grd_alt,grid_inner)
    if sta_alt is None:
        sta_alt = meteva.base.read_sta_alt_from_micaps3(meteva.base.station_国家站)
    sta_alt = meteva.base.in_grid(sta_alt,grid_inner)
    alt_grd_to_sta = meteva.base.interp_gs_linear(grd_alt, sta_alt)

    delta = sta_alt.copy()
    delta.iloc[:, -1] = (alt_grd_to_sta.iloc[:, -1] - sta_alt.iloc[:, -1]) * rate/100

    ids = list(set(sta_temp["id"].values.tolist()))
    delta = meteva.base.in_id_list(delta, ids)
    delta["level"] = meteva.base.IV
    delta["time"] = meteva.base.IV
    delta["dtime"] = meteva.base.IV
    datanames = meteva.base.get_stadata_names(sta_temp)

    sta_all_delta = meteva.base.combine_expand_IV(sta_temp, delta)
    if member_list is None:member_list = datanames
    for i in range(len(member_list)):
        name = member_list[i]
        sta_all_delta[name] += sta_all_delta.iloc[:, -1]
    datanames = meteva.base.get_stadata_names(sta_all_delta)

    sta_all_corrected = sta_all_delta.drop(columns=[datanames[-1]])
    return sta_all_corrected