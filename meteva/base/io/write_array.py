import pandas as pd
import numpy as np
def write_array_to_excel(array,save_path,name_list_dict,columns = None,index = None):


    shape = array.shape
    keys = list(name_list_dict.keys())
    if len(shape) ==1:
        rows = [[keys[0]],name_list_dict[keys[0]]]
        table_data = pd.DataFrame(array,index=pd.MultiIndex.from_product(rows))
        table_data.to_excel(save_path, sheet_name='sheet1')
    elif len(shape)==2:
        dat = None
        if columns is None:
            if index is None:
                columns = keys[0]
                index = keys[1]
            else:
                if index != keys[0]:
                    columns = keys[0]
                else:
                    columns = keys[1]
                    dat = array.T
        if dat is None:
            dat = array
        if columns not in keys:
            print("legend 参数的取值必须是name_list_dict的key")
        if index not in keys:
            print("axis 参数的取值必须是name_list_dict的key")
        cols = [[columns],name_list_dict[columns]]
        rows = [[index],name_list_dict[index]]
        table_data = pd.DataFrame(dat,columns=pd.MultiIndex.from_product(cols),
                                  index=pd.MultiIndex.from_product(rows))
        table_data.to_excel(save_path, sheet_name='sheet1')
    elif len(shape)==3:
        if name_list_dict is None:
            name_list_dict["z"] = np.arange(shape[0])
            name_list_dict["y"] = np.arange(shape[1])
            name_list_dict["x"] = np.arange(shape[2])
            columns = "y"
            index = "x"
            sheet = "z"
        keys = list(name_list_dict.keys())
        if columns is None:
            if index is None:
                columns = keys[1]
                index = keys[2]
                sheet = keys[0]
            else:
                if index == keys[2]:
                    columns = keys[1]
                    sheet = keys[0]
                elif index == keys[1]:
                    columns = keys[2]
                    sheet = keys[0]
                else:
                    columns = keys[2]
                    sheet = keys[1]
        else:
            if index is None:
                if columns == keys[0]:
                    index = keys[2]
                    sheet = keys[1]
                elif columns == keys[1]:
                    index = keys[2]
                    sheet = keys[0]
                else:
                    index = keys[1]
                    sheet = keys[0]
            else:
                indexlist = [0,1,2]
                indexlist.remove(keys.index(columns))
                indexlist.remove(keys.index(index))
                sheet = keys[indexlist[0]]
        if columns not in keys:
            print("legend 参数的取值必须是name_list_dict的key")
        if index not in keys:
            print("axis 参数的取值必须是name_list_dict的key")
        newshape = (keys.index(sheet),keys.index(index),keys.index(columns))
        data = array.transpose(newshape)
        table_data_list = []
        cols= [[columns],name_list_dict[columns]]
        rows = [[index],name_list_dict[index]]
        sheet_list = name_list_dict[sheet]

        for s in range(len(sheet_list)):
            # table_data = pd.DataFrame(array[:,:,s])
            table_data = pd.DataFrame(data[s,:, :],
                                      columns=pd.MultiIndex.from_product(cols),
                                      index=pd.MultiIndex.from_product(rows)
                                      )
            table_data_list.append(table_data)
        with pd.ExcelWriter(save_path) as writer:
            for i in range(len(sheet_list)):
                table_data_list[i].to_excel(writer, sheet_name=sheet + '_' + str(name_list_dict[sheet][i]))
    else:
        print("array不能超过3维")
        return


    print("数据已以excel表格形式保存至" + save_path)

