import nmc_verification

def put_uv_into_wind(u,v):
    grid0 = nmc_verification.nmc_vf_base.get_grid_of_data(u)
    grid1 = nmc_verification.nmc_vf_base.grid(grid0.glon,grid0.glat,grid0.gtime,grid0.dtimes,grid0.levels,members=["u","v"])
    wind = nmc_verification.nmc_vf_base.grid_data(grid1)
    wind.name = "wind"
    wind.values[0, :, :, :, :, :] = u.values[0, :, :, :, :, :]
    wind.values[1, :, :, :, :, :] = v.values[0, :, :, :, :, :]
    return wind