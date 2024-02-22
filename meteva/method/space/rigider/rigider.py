import datetime
import numpy as np
import math
from scipy import optimize as optimize
from . import imomenter, fint2d, rigid_transform, q_loss_rigid
import meteva
import copy

def rigid_optimal(grd_ob,grd_fo, translate=True, rotate=True,stages=True, show=False):
    x = grd_fo.values.squeeze()
    y = grd_ob.values.squeeze()
    result = rigider(x,y,init = None,translate = translate,rotate = rotate,
                         stages = stages,show = show)

    grid0 = meteva.base.get_grid_of_data(grd_fo)
    rire = {}
    rire["grd_fo"] = grd_fo
    rire["grd_ob"] = grd_ob
    rire["grd_fo_shift"] = meteva.base.grid_data(grid0,result["grd_fo_translated"])
    rire["grd_fo_shift_rotate"] = meteva.base.grid_data(grid0,result["grd_fo_transformed"])

    meteva.base.set_griddata_coords(rire["grd_ob"],member_list=["OBS"])
    meteva.base.set_griddata_coords(rire["grd_fo"],member_list=["FST"])
    meteva.base.set_griddata_coords(rire["grd_fo_shift"],member_list=["FST_SHIFT"])
    meteva.base.set_griddata_coords(rire["grd_fo_shift_rotate"],member_list=["FST_SHIFT_ROTATE"])
    if "y" in result["par"].keys():
        rire["delta_lon"] = result["par"]["y"] * grid0.dlon
    else:
        rire["delta_lon"] = 0
    if "x" in result["par"].keys():
        rire["delta_lat"] = result["par"]["x"] * grid0.dlat
    else:
        rire["delta_lat"] = 0
    if "theta" in result["par"].keys():
        rire["delta_angle"] = result["par"]["theta"] * 180 / 3.1415926
    else:
        rire["delta_angle"] = 0
    rire["rmse_before"] = np.sqrt(np.mean(np.power(grd_fo.values - grd_ob.values,2)))
    rire["rmse_after"] = np.sqrt(np.mean(np.power(rire["grd_fo_shift_rotate"].values - grd_ob.values, 2)))

    return rire


def rigid_simple(grd_ob,grd_fo):
    x = grd_fo.values.squeeze()
    y = grd_ob.values.squeeze()
    result = rigider(x,y,func_type="fast",stages=False)

    grid0 = meteva.base.get_grid_of_data(grd_fo)
    rire = {}
    rire["grd_fo"] = grd_fo
    rire["grd_ob"] = grd_ob
    #rire["grd_fo_shift"] = meteva.base.grid_data(grid0,result["grd_fo_translated"])
    rire["grd_fo_shift_rotate"] = meteva.base.grid_data(grid0,result["grd_fo_transformed"])

    meteva.base.set_griddata_coords(rire["grd_ob"],member_list=["OBS"])
    meteva.base.set_griddata_coords(rire["grd_fo"],member_list=["FST"])
    #meteva.base.set_griddata_coords(rire["grd_fo_shift"],member_list=["FST_SHIFT"])
    meteva.base.set_griddata_coords(rire["grd_fo_shift_rotate"],member_list=["FST_SHIFT_ROTATE"])

    if "y" in result["par"].keys():
        rire["delta_lon"] = result["par"]["y"] * grid0.dlon
    else:
        rire["delta_lon"] = 0
    if "x" in result["par"].keys():
        rire["delta_lat"] = result["par"]["x"] * grid0.dlat
    else:
        rire["delta_lat"] = 0
    if "theta" in result["par"].keys():
        rire["delta_angle"] = result["par"]["theta"] * 180 / 3.1415926
    else:
        rire["delta_angle"] = 0
    rire["rmse_before"] = np.sqrt(np.mean(np.power(grd_fo.values - grd_ob.values,2)))
    rire["rmse_after"] = np.sqrt(np.mean(np.power(rire["grd_fo_shift_rotate"].values - grd_ob.values, 2)))

    return rire


def plot_value(rire,cmap = "rain_1h",clevs = None):
    grd_list = [rire["grd_ob"],rire["grd_fo"],rire["grd_fo_shift_rotate"]]
    vmax = max(np.max(grd_list[0].values),np.max(grd_list[0].values))
    vmin = min(np.min(grd_list[0].values),np.min(grd_list[0].values))
    cmap1, clevs1 = meteva.base.tool.color_tools.def_cmap_clevs(cmap=cmap, clevs=clevs, vmin=vmin, vmax=vmax)
    meteva.base.plot_tools.plot_2d_grid_list(grd_list,cmap=cmap1,clevs = clevs1,ncol= 3,sup_fontsize=8)
    return

def rigider(grd_fo, grd_ob, init=None, func_type="regular", translate=True, rotate=True,
            interp="linear", stages=True, show=False):
    if stages and not (translate and rotate):
        stages = False
    if not translate and not rotate:
        raise Exception("rigider: one of translate or rotate must be true.")
    if show:
        begin_tiid = datetime.datetime.now()
    x_dim = grd_ob.shape[0]
    y_dim = grd_ob.shape[1]
    #range0 = np.tile(np.arange(1, x_dim + 1), y_dim)
    #range1 = (np.arange(1, y_dim + 1)).repeat(x_dim)
    range0 = np.tile(np.arange(0, x_dim), y_dim)
    range1 = (np.arange(0, y_dim)).repeat(x_dim)
    p0 = np.stack((range0, range1), axis=-1)
    out = {}
    if isinstance(func_type, str):
        func_type = func_type.lower()
    elif isinstance(func_type, list):
        func_type = func_type[0].lower()
    p0 = np.array(p0)
    big_n = p0.shape[0]
    grd_fo = np.array(grd_fo)
    # 计算质心
    array_index = np.array(grd_fo.transpose() > 0).reshape((grd_fo.size, 1)).repeat(2, axis=1)
    temp_matrix = p0[array_index]
    temp_array = np.mean(temp_matrix.reshape((int(temp_matrix.size / 2), 2)), axis=0)
    field_center = np.tile(np.array(temp_array), big_n).reshape(big_n, 2, order='C')
    if func_type == "regular":
        xdim = grd_fo.shape
        if xdim != grd_ob.shape:
            raise Exception("rigider: x1 and x0 must have the same dimension.")
        outpar = np.zeros(1) + np.nan
        if init is None:
            if show:
                print("Initial values not passed.  Determining good starting values now.\n")
            # 计算图片运动参数（images movements）, 获取刚体变换的初始平移量和旋转量
            # reference: Hu, M. K. (1962) Visual Pattern Recognition by Moment Invariants. IRE Trans. Info. Theory, IT-8, 179–187.
            hold1 = imomenter.imomenter(grd_fo, loc=p0)
            hold0 = imomenter.imomenter(grd_ob, loc=p0)
            init = [hold1["centroid"]["x"] - hold0["centroid"]["x"], hold1["centroid"]["y"] - hold0["centroid"]["y"],
                  hold1["orientation_angle"] - hold0["orientation_angle"]]
            if not translate:
                init[0] =0
                init[1] =0
            if not rotate:
                init[2] = 0
            if show:
                print("initial values:\n")
                print(init)
        if not stages:
            if translate:
                if show:
                    print("Optimizing translation.\n")
                # 使用优化函数获取最佳变量
                res = optimize.minimize(ofun1, init[0:2],
                                        (p0, grd_fo, grd_ob, interp, big_n, field_center, xdim),"L-BFGS-B")
                if show:
                    print("Optimal translation found to be: ", res["x"], "\nwhere loss value is: ", res["fun"],
                          "\n")
                temp_theta = np.append(res["x"], init[2])
                p1 = rigid_transform.rigid_transform(theta=temp_theta, p0=p0, n=big_n, cen=field_center)
                y1 = fint2d.fint2d(x=grd_fo, ws=p1, s=p0, method=interp)
                res["p1"] = p1
                out["grd_fo_translated"] = y1
                outpar = res["x"]
                outval = res["fun"]
            else:
                out["grd_fo_translated"] = copy.deepcopy(grd_fo)
            if rotate:
                if translate:
                    init2 = np.append(res["x"], init[2])
                else:
                    init2 = init
                if show:
                    print("Optimizing rotation.\n")
                res2 = optimize.minimize(ofun2, init2[2],
                                         (p0, grd_fo, grd_ob, interp, big_n, field_center, xdim,
                                          init2[0:2]), "L-BFGS-B")
                if show:
                    print("Optimal rotation found to be: ", res2["x"], "\nwhere loss value is: ", res2["fun"], "\n")

                if translate:
                    r_center = np.tile(np.array([hold0["centroid"]["x"], hold0["centroid"]["y"]]), big_n).reshape(big_n, 2,
                                                                                                                  order='C')
                else:
                    r_center = np.tile(np.array([hold1["centroid"]["x"], hold1["centroid"]["y"]]), big_n).reshape(big_n, 2,
                                                                                                              order='C')
                p1 = rigid_transform.rigid_transform(theta=np.array([init2[0],init2[1], res2["x"]]), p0=p0, n=big_n,
                                                     cen=r_center)


                y1 = fint2d.fint2d(x=grd_fo, ws=p1, s=p0, method=interp)
                outpar = np.append(outpar, res2["x"])
                outval = res2["fun"]

        else:
            if show:
                print("Optimizing rigid transformation.\n")
            res = optimize.minimize(ofun3, init, (p0, grd_fo, grd_ob, interp, big_n, field_center, xdim),
                                    "L-BFGS-B")
            if show:
                print("Optimal transformation found to be: ", res["x"], "\nwhere loss value is: ", res["fun"], "\n")
            r_center = np.tile(np.array([hold0["centroid"]["x"], hold0["centroid"]["y"]]), big_n).reshape(big_n, 2,
                                                                                                              order='C')
            p1 = rigid_transform.rigid_transform(theta=res["x"], p0=p0, n=big_n, cen=r_center)

            outpar = res["x"]
            outval = res["fun"]

            temp_theta2 = np.array([outpar[0],outpar[1], 0])
            p2 = rigid_transform.rigid_transform(theta=temp_theta2, p0=p0, n=big_n, cen=r_center)
            y2 = fint2d.fint2d(x=grd_fo, ws=p2, s=p0, method=interp)
            out["grd_fo_translated"] = y2



        if translate and (not rotate):
            outpar = {"x": outpar[0], "y": outpar[1]}
        elif (not translate) and rotate:
            outpar = {"angle": outpar[1]} # 注意 前面outpar的设置
        else:
            outpar = {"x": outpar[0], "y": outpar[1], "theta": outpar[2]}
        if not stages:
            if translate:
                out["translation_only"] = res
            if rotate:
                out["rotate"] = res2
        else:
            out["optim_object"] = res
    elif func_type == "fast":
        hold1 = imomenter.imomenter(grd_fo, loc=p0)
        hold0 = imomenter.imomenter(grd_ob, loc=p0)
        #print(hold0)
        #print(hold1)
        if translate:
            tr = [hold1["centroid"]["x"] - hold0["centroid"]["x"],hold1["centroid"]["y"] - hold0["centroid"]["y"]]
        #print(tr)
        if rotate:
            rot = hold1["orientation_angle"] - hold0["orientation_angle"]
        if translate and rotate:
            outpar = np.array([tr[0],tr[1], rot])
            inpar = np.array([tr[0],tr[1], rot])
            outpar = {"x": outpar[0], "y": outpar[1], "theta": outpar[2]}
        elif (not translate) and rotate:
            outpar = rot
            inpar = np.array([0, 0, rot])
            outpar = {"theta": outpar[0]}
        elif translate and (not rotate):
            outpar = tr
            outpar = {"x": outpar[0], "y": outpar[1]}
            inpar = np.array([tr, 0])
        if stages:
            p1_tr = rigid_transform.rigid_transform(theta=tr, p0=p0, n=big_n, cen=field_center)
            y1_tr = fint2d.fint2d(x=grd_fo, ws=p1_tr, s=p0, method=interp)
            out["grd_fo_translated"] = y1_tr
        # 计算刚体变换后的坐标
        #print(field_center)
        ob_center = np.tile(np.array([hold0["centroid"]["x"],hold0["centroid"]["y"]]), big_n).reshape(big_n, 2, order='C')
        p1 = rigid_transform.rigid_transform(theta=inpar, p0=p0, n=big_n, cen=ob_center)
        #p1 = rigid_transform.rigid_transform(theta=inpar, p0=p0, n=big_n, cen=field_center)

    # 计算刚体变换后的x1
    y1 = fint2d.fint2d(x=grd_fo, ws=p1, s=p0, method=interp)
    #y1 = fint2d.fint2d(x=grd_fo, ws=p0, s=p1, method=interp)
    out["func_type"] = func_type
    if func_type == "regular":
        out["initial"] = init
        out["value"] = outval
    out["interp"] = interp
    out["par"] = outpar
    out["grd_ob"] = grd_ob
    out["grd_fo"] = grd_fo
    out["p0"] = p0
    out["p1"] = p1
    out["grd_fo_transformed"] = y1
    if show:
        print(datetime.datetime.now() - begin_tiid)
    return out


def ofun1(theta, p0, x1, x0, interp, n, cen, xdim, tr=None):
    if theta[0] > xdim[0] / 2 + 1 or theta[1] > xdim[1] / 2 + 1:
        return 1e+16
    theta = np.array(theta)
    theta = np.append(theta, 0)
    p1 = rigid_transform.rigid_transform(theta=theta, p0=p0, n=n, cen=cen)
    y1 = fint2d.fint2d(x=x1, ws=p1, s=p0, method=interp)
    res = q_loss_rigid.q_loss_rigid(y1, x0, p1, p0)
    return res


def ofun2(theta, p0, x1, x0, interp, n, cen, xdim, tr):
    if theta > math.pi / 2 or theta < -math.pi / 2:
        return 1e+16
    theta = np.array(theta)
    theta = np.append(tr, theta)
    p1 = rigid_transform.rigid_transform(theta=theta, p0=p0, n=n, cen=cen)
    y1 = fint2d.fint2d(x=x1, ws=p1, s=p0, method=interp)
    res = q_loss_rigid.q_loss_rigid(y1, x0, p1, p0)
    return res


def ofun3(theta, p0, x1, x0, interp, n, cen, xdim, tr=None):
    if theta[0] > xdim[0] / 2 + 1 or theta[1] > xdim[1] / 2 + 1:
        return 1e+16
    condition_a = theta > math.pi / 2
    condition_b = theta < -math.pi / 2
    condition = condition_a + condition_b
    if condition.all():
        #if theta > math.pi / 2 or theta < -math.pi / 2:
        return 1e+16
    p1 = rigid_transform.rigid_transform(theta=theta, p0=p0, n=n, cen=cen)
    y1 = fint2d.fint2d(x=x1, ws=p1, s=p0, method=interp)
    res = q_loss_rigid.q_loss_rigid(y1, x0, p1, p0)
    return res


if __name__ == '__main__':
    import meteva.base as meb
    import meteva.method as mem
    # 生成方形的测试数据
    grid_ob = meb.grid([100, 130, 1], [15, 45, 1], gtime=["2021080408"], dtime_list=[0], member_list=["OBS"])
    x = np.zeros((31, 31))
    x[8:10, 10:17] = 10
    grd_ob = meb.grid_data(grid_ob, x)

    grid_fo = meb.grid([100, 130, 1], [15, 45, 1], gtime=["2021080308"], dtime_list=[24], member_list=["ECMWF"])
    y = np.zeros((31, 31))
    for i in range(y.shape[0]):
        for j in range(y.shape[1]):
            a = (i - 15) * math.sin(math.pi / 4) - (j - 15) * math.cos(math.pi / 4)
            b = (i - 15) * math.sin(math.pi / 4) + (j - 15) * math.cos(math.pi / 4)
            if abs(a) < 3 and abs(b) < 5:
                y[i, j] = 5
    grd_fo = meb.grid_data(grid_fo, y)
    rire = mem.rigider.rigid_simple(grd_ob, grd_fo)
    mem.rigider.plot_value(rire)