import numpy as np
import datetime
import meteva
from scipy.ndimage.filters import uniform_filter


def mesh_lon_time(grd_ob,grd_fo,method = np.mean,grid = None,interval = None,smooth = 1,cmap = "rainbow",clevs = None,ncol = None,annot =None,dpi = 300,
         spasify_xticks = None,sup_fontsize = 10,title ="",width = None,height = None,save_path = None,show = None):

    if grid is not None:
        grd_ob = meteva.base.interp_gg_linear(grd_ob,grid=grid)
        grd_fo = meteva.base.interp_gg_linear(grd_fo,grid = grid)

    grid_ob = meteva.base.get_grid_of_data(grd_ob)
    time_ob = meteva.base.all_type_time_to_datetime(grid_ob.gtime[0])
    dtimes =grd_fo["dtime"].values
    times_all = grd_fo["time"].values
    times_fo = []
    for time1 in times_all:
        times_fo.append(meteva.base.all_type_time_to_datetime(time1))

    member_list = grd_fo["member"].values

    mean_value_array = np.zeros((len(member_list),len(dtimes)+1,len(grd_ob["lon"].values)))
    time_fo_list = []
    for i in range(len(dtimes)):
        k = len(dtimes) - i - 1
        dtime = dtimes[k]
        time_fo = time_ob -  datetime.timedelta(hours=int(dtime))
        if time_fo in times_fo:
            grd_1dtime =grd_fo.isel(dtime=slice(k, k+1))
            grd_1time = meteva.base.in_time_list(grd_1dtime,time_list=[time_fo])
            mean_value_array[:,i, :] = method(grd_1time.values, axis=4).squeeze()
            time_fo_list.append(time_fo)

    time_fo_list.append(time_ob)
    mean_value_array[:,-1,:] = method(grd_ob.values,axis=4)

    name_list_dict = {
        "member":member_list,
        "时间":time_fo_list,
        "经度":grd_ob["lon"].values
    }

    if interval is not None:
        size = int(interval/grid_ob.dlon)
        size_smooth = smooth * size
        mean_value_array1 = np.zeros(mean_value_array.shape)
        for i in range(mean_value_array.shape[0]):
            for j in range(mean_value_array.shape[1]):
                dat = uniform_filter(mean_value_array[i,j,:], size=size_smooth)
                mean_value_array1[i,j,:] = dat
        mean_value_array = mean_value_array1[:,:,::size]
        name_list_dict["经度"] = name_list_dict["经度"][::size]

    col = mean_value_array.shape[1]
    row = mean_value_array.shape[2]
    meteva.base.mesh(mean_value_array,name_list_dict=name_list_dict,save_path=save_path,cmap=cmap,clevs=clevs,
                     ncol =ncol,rect = [-0.5,col-1.5,row,1],annot = annot,spasify_xticks=spasify_xticks,sup_fontsize=sup_fontsize,title=title
                     ,width=width,height=height,dpi=dpi,show=show)



    pass


def mesh_time_lat(grd_ob,grd_fo,method = np.mean,grid = None,interval = None,smooth = 1,cmap = "rainbow",clevs = None,ncol = None,annot =None,dpi = 300,
         spasify_xticks = None,sup_fontsize = 10,title ="",width = None,height = None,save_path = None,show = None):

    if grid is not None:
        grd_ob = meteva.base.interp_gg_linear(grd_ob,grid=grid)
        grd_fo = meteva.base.interp_gg_linear(grd_fo,grid = grid)

    grid_ob = meteva.base.get_grid_of_data(grd_ob)
    time_ob = meteva.base.all_type_time_to_datetime(grid_ob.gtime[0])
    dtimes =grd_fo["dtime"].values
    times_all = grd_fo["time"].values
    times_fo = []
    for time1 in times_all:
        times_fo.append(meteva.base.all_type_time_to_datetime(time1))

    member_list = grd_fo["member"].values

    mean_value_array = np.zeros((len(member_list),len(dtimes)+1,len(grd_ob["lat"].values)))
    time_fo_list = []
    for i in range(len(dtimes)):
        k = len(dtimes) - i - 1
        dtime = dtimes[k]
        time_fo = time_ob -  datetime.timedelta(hours=int(dtime))
        if time_fo in times_fo:
            grd_1dtime =grd_fo.isel(dtime=slice(k, k+1))
            grd_1time = meteva.base.in_time_list(grd_1dtime,time_list=[time_fo])
            mean_value_array[:,i, :] = method(grd_1time.values, axis=5).squeeze()
            time_fo_list.append(time_fo)

    time_fo_list.append(time_ob)
    mean_value_array[:,-1,:] = method(grd_ob.values,axis=5)

    name_list_dict = {
        "member":member_list,
        "时间":time_fo_list,
        "纬度":grd_ob["lat"].values
    }

    if interval is not None:
        size = int(interval/grid_ob.dlon)
        size_smooth = size * smooth
        mean_value_array1 = np.zeros(mean_value_array.shape)
        for i in range(mean_value_array.shape[0]):
            for j in range(mean_value_array.shape[1]):
                dat = uniform_filter(mean_value_array[i,j,:], size=size_smooth)
                mean_value_array1[i,j,:] = dat
        mean_value_array = mean_value_array1[:,:,::size]
        name_list_dict["纬度"] = name_list_dict["纬度"][::size]

    col = mean_value_array.shape[1]
    row = mean_value_array.shape[2]
    meteva.base.mesh(mean_value_array,name_list_dict=name_list_dict,axis_x="时间",axis_y="纬度",
                     save_path=save_path,cmap=cmap,clevs=clevs,ncol =ncol,rect = [col-1.5,-0.5,1,row+1],
                     annot = annot,spasify_xticks=spasify_xticks,sup_fontsize=sup_fontsize,title=title
                     ,width=width,height=height,dpi=dpi,show=show)

    pass