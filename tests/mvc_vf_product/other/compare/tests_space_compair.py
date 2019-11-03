from nmc_verification.nmc_vf_product.other.compare import space_compair
from nmc_verification.nmc_vf_base.io import read_griddata
from nmc_verification.nmc_vf_base.io import read_stadata
from nmc_verification.nmc_vf_base.basicdata.grid import grid
import nmc_verification.nmc_vf_base as nvb
import pandas as pd

data_fo = read_griddata.read_from_nc('F:\ppt\ec\grid\/rain24/BT18070108.024.nc')
#data_fo = nvb.get_grid_of_data(data_nc)
# data_nc = grid([data_nc.lon[0].values, data_nc.lon[-1].values, ((data_nc.lon[-1] - data_nc.lon[0]) / 1400).values],
#                [data_nc.lat[0].values, data_nc.lat[-1].values, ((data_nc.lat[-1] - data_nc.lat[0]) / 900).values],
#                [data_nc.time[0].values, data_nc.time[0].values], data_nc.dtime[0].values, data_nc.level[0].values,
#                data_nc.member.values)
data_ob = read_stadata.read_from_micaps3('F:\ppt\ob\sta\/rain24/BT18070208.000')

data_ob = nvb.function.get_from_sta_data.sta_between_value_range(data_ob, 0, 1000)
print(data_fo)
print(data_ob)
space_compair.draw_veri_rain_24(data_fo, data_ob)
