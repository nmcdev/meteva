import nmc_verification

def interpolation_linear(grd, grid):
    members = grd["member"]
    num = len(members)
    grid_old = nmc_verification.nmc_vf_base.get_grid_of_data(grd)
    grid_new = nmc_verification.nmc_vf_base.grid(grid.glon,grid.glat,members=members)
    grd_new = nmc_verification.nmc_vf_base.grid_data(grid_new)
    grid_xy = nmc_verification.nmc_vf_base.grid(grid_old.glon,grid_old.glat)
    for m in range(num):
        member = members[m]
        grd0 = grd.loc[dict(member=member)]
        grd1 = nmc_verification.nmc_vf_base.grid_data(grid_xy)
        grd1.values[0,0,0,0,:,:] = grd0.values.squeeze()
        #print(grd1)
        #print(grid)
        grd2 = nmc_verification.nmc_vf_base.function.gxy_gxy.interpolation_linear(grd1,grid)
        #print(grd2)
        grd_new.values[m,:,:,:,:,:] = grd2.values

    return grd_new