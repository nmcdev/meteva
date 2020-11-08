import os
import meteva
def get_hour_dhour_list(gds_file_list):
    hour_list = []
    dh_list = []
    for path in gds_file_list:
        dati = get_dati_of_path(path)
        hour_list.append(dati.hour)
        file, ftype = os.path.splitext(path)
        dh_list.append(int(ftype[1:]))
    hour_list1 = list(set(hour_list))
    hour_list1.sort()
    dh_list1 = list(set(dh_list))
    dh_list1.sort()
    return hour_list1,dh_list1

def get_dati_of_path(path):
    dir,filename = os.path.split(path)
    filename0 = os.path.splitext(filename)[0]
    a = int(filename0[0:2])
    b = int(filename0[2:4])
    if a ==20:
        if b >12:
            pass
        else:
            filename0 = "20" + filename0
    elif a == 19:
        if b >12:
            pass
        else:
            filename0 = "20" + filename0
    else:
        filename0 = "20" + filename0

    dati = meteva.base.time_tools.str_to_time(filename0)
    return dati
def get_dati_str_of_path(path):
    dir,filename = os.path.split(path)
    filename0 = os.path.splitext(filename)[0]
    a = int(filename0[0:2])
    b = int(filename0[2:4])
    if a ==20:
        if b >12:
            pass
        else:
            filename0 = "20" + filename0
    elif a == 19:
        if b >12:
            pass
        else:
            filename0 = "20" + filename0
    else:
        filename0 = "20" + filename0
    dati_str = filename0[0:8]

    return dati_str