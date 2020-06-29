import pandas as pd

def write_array_to_excel(array,save_path,name_dict_list,index = None,columns = None):
    table_data_list = []
    ind = []
    for key in name_dict_list[0]:
        ind = [[key],name_dict_list[0][key]]
    col = []
    for key in name_dict_list[1]:
        col = [[key],name_dict_list[1][key]]
    sh = []
    for key in name_dict_list[2]:
        sh = [key,name_dict_list[2][key]]
    for s in range(array.shape[2]):
       #table_data = pd.DataFrame(array[:,:,s])
        table_data = pd.DataFrame(array[:,:,s],
                                  columns=pd.MultiIndex.from_product(col),
                                  index=pd.MultiIndex.from_product(ind)
                                  )
        table_data_list.append(table_data)
    with pd.ExcelWriter(save_path) as writer:
        for i in range(len(table_data_list)):
            table_data_list[i].to_excel(writer, sheet_name=sh[0] + '_' + str(sh[1][i]))
    print("列联表已以excel表格形式保存至" + save_path)

