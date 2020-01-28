import nmc_verification.nmc_vf_base as nvb
import datetime
import time
import numpy as np
from nmc_verification.nmc_vf_base import DataBlock_pb2
from nmc_verification.nmc_vf_base import GDSDataService
import pandas as pd
import os
import copy


def read_stadata_from_gds(ip, port, filename0,element_id0,station = None,data_name='data0'):
    """

    """
    directory, filename = os.path.split(filename0)
    # connect to data service
    service = GDSDataService(ip, port)

    # get data file name
    element_id_str0 = str(element_id0)
    try:
        status, response = service.getData(directory, filename)
    except ValueError:
        print('Can not retrieve data' + filename + ' from ' + directory)
        return None
    ByteArrayResult = DataBlock_pb2.ByteArrayResult()
    if status == 200:
        ByteArrayResult.ParseFromString(response)
        if ByteArrayResult is not None:
            byteArray = ByteArrayResult.byteArray
            # define head structure
            head_dtype = [('discriminator', 'S4'), ('type', 'i2'),
                          ('description', 'S100'),
                          ('level', 'f4'), ('levelDescription', 'S50'),
                          ('year', 'i4'), ('month', 'i4'), ('day', 'i4'),
                          ('hour', 'i4'), ('minute', 'i4'), ('second', 'i4'),
                          ('Timezone', 'i4'), ('extent', 'S100')]

            # read head information
            head_info = np.frombuffer(byteArray[0:288], dtype=head_dtype)
            ind = 288
            # read the number of stations
            station_number = np.frombuffer(
                byteArray[ind:(ind+4)], dtype='i4')[0]
            ind += 4

            # read the number of elements
            element_number = np.frombuffer(
                byteArray[ind:(ind+2)], dtype='i2')[0]
            ind += 2

            # construct record structure
            element_type_map = {
                1: 'b1', 2: 'i2', 3: 'i4', 4: 'i8', 5: 'f4', 6: 'f8', 7: 'S1'}
            element_map = {}
            element_map_len = {}
            for i in range(element_number):
                element_id = str(np.frombuffer(byteArray[ind:(ind+2)], dtype='i2')[0])
                ind += 2
                element_type = np.frombuffer(
                    byteArray[ind:(ind+2)], dtype='i2')[0]
                ind += 2
                element_map[element_id] = element_type_map[element_type]
                element_map_len[element_id] = int(element_type_map[element_type][1])

            dtype_str = element_map[element_id_str0]

            # loop every station to retrieve record
            record_head_dtype = [
                ('id', 'i4'), ('lon', 'f4'), ('lat', 'f4'), ('numb', 'i2')]
            records = []
            if station is None or len(station.index) * 100 > station_number:
                for i in range(station_number):
                    record_head = np.frombuffer(
                        byteArray[ind:(ind+14)], dtype=record_head_dtype)
                    ind += 14
                    record = {
                        'id': record_head['id'][0], 'lon': record_head['lon'][0],
                        'lat': record_head['lat'][0]}
                    for j in range(record_head['numb'][0]):    # the record element number is not same, missing value is not included.
                        element_id = str(np.frombuffer(byteArray[ind:(ind + 2)], dtype='i2')[0])
                        ind += 2
                        element_len = element_map_len[element_id]
                        if element_id == element_id_str0:
                            record[data_name] = np.frombuffer(
                                byteArray[ind:(ind + element_len)],
                                dtype=dtype_str)[0]
                            records.append(record)
                        ind += element_len
                records = pd.DataFrame(records)
                records.set_index('id')
                # get time
                time1 = datetime.datetime(
                    head_info['year'][0], head_info['month'][0],
                    head_info['day'][0], head_info['hour'][0],
                    head_info['minute'][0], head_info['second'][0])
                records['time'] = time1
                records['level'] = head_info["level"][0]
                filename1 = os.path.split(filename)[1].split(".")
                records['dtime'] = int(filename1[1])
                new_columns = ['level', 'time', 'dtime', 'id', 'lon', 'lat', data_name]
                records = records.reindex(columns=new_columns)
                if station is None:
                    return records
                else:
                    sta = nvb.put_stadata_on_station(records, station)
                    return sta
            else:
                sta = copy.deepcopy(station)
                byte_num = len(byteArray)
                i4_num = (byte_num - ind -4) //4
                ids = np.zeros((i4_num,4),dtype=np.int32)

                ids[:, 0] = np.frombuffer(byteArray[ind:(ind + i4_num * 4)], dtype='i4')
                ids[:, 1] = np.frombuffer(byteArray[(ind +1):(ind + 1 + i4_num * 4)], dtype='i4')
                ids[:, 2] = np.frombuffer(byteArray[(ind + 2):(ind + 2 + i4_num * 4)], dtype='i4')
                ids[:, 3] = np.frombuffer(byteArray[(ind + 3):(ind + 3 + i4_num * 4)], dtype='i4')
                ids = ids.flatten()
                station_ids = station["id"].values
                dat = np.zeros(station_ids.size)

                for k in range(dat.size):
                    id1 = station_ids[k]
                    indexs = np.where(ids == id1)
                    if len(indexs) >=1:
                        for n in range(len(indexs)):
                            ind1 =ind +  indexs[n][0]
                            record_head = np.frombuffer(byteArray[ind1:(ind1 + 14)], dtype=record_head_dtype)
                            if(record_head['lon'][0] >=-180 and record_head['lon'][0] <= 360 and
                                    record_head['lat'][0] >= -90 and record_head['lat'][0] <= 90):
                                ind1 += 14
                                record = {
                                    'id': record_head['id'][0], 'lon': record_head['lon'][0],
                                    'lat': record_head['lat'][0]}
                                for j in range(record_head['numb'][0]):  # the record element number is not same, missing value is not included.
                                    element_id = str(np.frombuffer(byteArray[ind1:(ind1 + 2)], dtype='i2')[0])
                                    ind1 += 2
                                    element_len = element_map_len[element_id]
                                    if element_id == element_id_str0:
                                        sta.iloc[k,-1] = np.frombuffer(byteArray[ind1:(ind1 + element_len)],dtype=dtype_str)[0]
                                    ind1 += element_len
                nvb.set_stadata_names(sta,[data_name])
                time1 = datetime.datetime(
                    head_info['year'][0], head_info['month'][0],
                    head_info['day'][0], head_info['hour'][0],
                    head_info['minute'][0], head_info['second'][0])
                sta['time'] = time1
                sta['level'] = head_info["level"][0]
                filename1 = os.path.split(filename)[1].split(".")
                sta['dtime'] = int(filename1[1])
                return sta
        else:
            return None
    else:
        return None




print(nvb.gds_element_id.温度)
dir =  r"SURFACE/PLOT_ALL/YYYYMMDDHH0000.000"
time0 = datetime.datetime(2020,1,28,8,0)
path = nvb.get_path(dir,time0)
ip,port  = nvb.read_gds_ip_port(r"H:\test_data\input\nvb\ip_port.txt")
#print(path)

#nvb.print_gds_file_values_names(ip,port,path)
df = pd.DataFrame({"id":[811739],"lon":[114.0942],"lat":[30.5319]})
station = nvb.sta_data(df)
begin = time.time()
time1 = datetime.datetime(2019,1,28,8,0)
sta = nvb.read_stadata_from_gds(ip,port,path,nvb.gds_element_id.温度,time = time1)
print(time.time() - begin)
print(sta)