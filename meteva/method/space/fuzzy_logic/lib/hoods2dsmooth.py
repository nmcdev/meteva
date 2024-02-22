import math
import meteva
from meteva.method.space.fuzzy_logic.lib.kernel2dsmooth import kernel2dsmooth


def  hoods2dsmooth_grd(grd,half_window_size):
    '''
    以网格形式数据作为输入的平滑函数
    :param grd:
    :param level:
    :return:
    '''
    level = half_window_size *2+1
    grid0 = meteva.base.get_grid_of_data(grd)
    x = grd.values.squeeze()
    level_w = hoods2dsmooth(x, level, None, True)
    s_px = hoods2dsmooth(x, level, level_w)
    sm_x = meteva.base.grid_data(grid0, s_px)
    return sm_x



def hoods2dsmooth(x, lambd, w=None, setup=False, **args):
    if math.floor(lambd) != lambd:
        print("hoods2dsmooth: attempting to give an illegal value for the neighborhood length.  Flooring lambd.")
        lambd = math.floor(lambd)

    if lambd % 2 == 0:
        print("hoods2dsmooth: attempting to give an even neighborhood length, subtracting one from it.")
        lambd = lambd - 1

    if lambd < 1:
        print("hoods2dsmooth: attempting to give an illegal value for the neighborhood length.  Setting to one, "
              "and returning x untouched.")
        lambd = 1

    if lambd == 1:
        return x
    else:
        return kernel2dsmooth(x=x, kernel_type="boxcar", n=lambd, w=w, setup=setup, **args)
