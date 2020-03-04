from meteva.base.fun import *
from meteva.product.program.fun import *

def plot(sta_ob_and_fos,method,group_by = None,group_list_list = None,save_dir = None,title = None,para1 = None):

    discription_uni = get_unique_coods(sta_ob_and_fos)
    sta_ob_and_fos_list,group_list_list1 = group(sta_ob_and_fos,group_by,group_list_list)
    data_name = meteva.base.get_stadata_names(sta_ob_and_fos)
    fo_num = len(data_name) -1
    ensemble_score_method = [meteva.method.box_plot_ensemble]
    group_num = len(sta_ob_and_fos_list)

    valid_group_list_list = []
    if type(method) == str:
        method =  globals().get(method)
    if method in ensemble_score_method:
        for i in range(group_num):
            sta = sta_ob_and_fos_list[i]
            if(len(sta.index) == 0):
                pass
            else:
                valid_group_list = None
                if group_list_list1 is None:
                    valid_group_list_list = None
                else:
                    valid_group_list = group_list_list1[i]
                    valid_group_list_list.append(group_list_list1[i])
                ob = sta[data_name[0]].values
                fo = sta[data_name[1:]].values
                save_path = get_save_path(save_dir,method,group_by,valid_group_list,"",".png",title)
                title1 = get_title(method,group_by,valid_group_list,"",title,discription_uni)
                if para1 is None:
                    method(ob, fo,save_path = save_path,title = title1,member_list = data_name[1:])
                else:
                    method(ob, fo,para1,save_path = save_path,title = title1,member_list = data_name[1:])
    else:
        for i in range(group_num):
            sta = sta_ob_and_fos_list[i]
            if(len(sta.index) == 0):
                pass
            else:
                valid_group_list = None
                if group_list_list1 is None:
                    valid_group_list_list = None
                else:
                    valid_group_list = group_list_list1[i]
                    valid_group_list_list.append(group_list_list1[i])
                ob = sta[data_name[0]].values

                for j in range(fo_num):
                    fo = sta[data_name[j+1]].values
                    save_path = get_save_path(save_dir,method,group_by,valid_group_list,data_name[j+1],".png",title)
                    title1 = get_title(method,group_by,valid_group_list,data_name[j+1],title,discription_uni)
                    if para1 is None:
                        method(ob, fo,save_path = save_path,title = title1)
                    else:
                        method(ob, fo,para1,save_path = save_path,title = title1)


    return valid_group_list_list
