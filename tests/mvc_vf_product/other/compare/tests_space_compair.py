from nmc_verification.nmc_vf_product.other.compare import space_compair
from nmc_verification.nmc_vf_base.io import read_griddata
from nmc_verification.nmc_vf_base.io import read_stadata
from nmc_verification.nmc_vf_base.basicdata.grid import grid
import  nmc_verification.nmc_vf_base as nvb
data_nc = read_griddata.read_from_nc('../../../data/BT18010100.000.nc')
data_nc = nvb.get_grid_of_data(data_nc)
# data_nc = grid([data_nc.lon[0].values, data_nc.lon[-1].values, ((data_nc.lon[-1] - data_nc.lon[0]) / 1400).values],
#                [data_nc.lat[0].values, data_nc.lat[-1].values, ((data_nc.lat[-1] - data_nc.lat[0]) / 900).values],
#                [data_nc.time[0].values, data_nc.time[0].values], data_nc.dtime[0].values, data_nc.level[0].values,
#                data_nc.member.values)
data_m3 = read_stadata.read_from_micaps3('../../../data/BT18010100.000')
space_compair.draw_veri_rain_24(data_nc, data_m3)
