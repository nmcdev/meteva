import meteva
import datetime

def acc_climate_pre(input_dir,output_path):
    time1 = datetime.datetime(2020,1,1,0)
    grd_list = []
    for i in range(732):
        path = input_dir + r"\\"+str(i+1)+".grib"
        grd = meteva.base.read_griddata_from_grib(path)
        time2 = time1 + datetime.timedelta(hours=12*i)
        meteva.base.set_griddata_coords(grd,gtime=[time2])
        grd_list.append(grd)
    grd_all = meteva.base.concat(grd_list)
    meteva.base.write_griddata_to_nc(grd_all,save_path=output_path)


if __name__ == "__main__":
    input_dir = r"H:\test_data\input\mem\era-dailyclim\t700_mean"
    output_path = r"H:\test_data\input\mem\era-dailyclim\t700_mean.nc"
    acc_climate_pre(input_dir,output_path)