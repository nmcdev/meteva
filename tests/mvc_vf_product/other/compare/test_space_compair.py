from nmc_verification.nmc_vf_product.continuous.space_compare import *
import nmc_verification.nmc_vf_base as nvb

grid = nvb.grid([73,135,0.25],[18,53,0.25])

#grid = nvb.grid([110,120,0.25],[20,45,0.25])
data_fo = nvb.io.read_griddata.read_from_nc('I:/ppt/ec/grid/rain24/BT18070108.024.nc')
#nvb.set_coords(data_fo,dtime= [24],member= "ecmwf")
data_ob = nvb.io.read_stadata.read_from_micaps3('I:/ppt/ob/sta/rain24/BT18070208.000')
data_ob = nvb.function.get_from_sta_data.sta_between_value_range(data_ob, 0, 1000)
#space_compair.rain_24h_sg(data_fo, data_ob) #简单对比图
#space_compair.rain_24h_comprehensive_sg(data_ob,data_fo, filename="H:/rain24.png") #综合对比图

data_fo = nvb.function.gxy_gxy.interpolation_linear(data_fo,grid)
#space_compair.rain_24h_comprehensive_sg(data_ob, data_fo,filename="H:/rain24.png") #改变区域后，重新制作综合对比图
rain_24h_comprehensive_chinaland_sg(data_ob,data_fo,filename=r"H:\test_data\output\nmc_vf_produce\continue\rain24_china.png") # 显示范围锁定为中国陆地的综合对比图，布局进行了针对性优化
#grid = None

#grd_fo = nvb.io.read_griddata.read_from_nc(r"H:\test_data\ecmwf\temp_2m\19111608.024.nc",grid=grid)
#print(grd_fo)
#nvb.set_coords(grd_fo,dtime= [24],member= "ecmwf")
#grd_ob = nvb.io.read_griddata.read_from_nc(r"H:\task\develop\python\git\nmc_verification\tests\data\ecmwf\temp_2m\19111708.000.nc",grid=grid)

#space_compare.temper_gg(grd_ob, grd_fo, "H:/temp.png")

