import nmc_verification.nmc_vf_base.function.put_into_sta_data as pisd
import nmc_verification.nmc_vf_method.yes_or_no as yon
import  string

def contingency_table_multi_mode(ob, fo_list, grade=None, save_path='contingency_table.xls', sheet_name='sheet1'):
    '''

    :param ob_sta:  一个实况数据  类型  dataframe
    :param fo_sta_list: 多模式预测数据 列表  类型list  list中的类型是dataframe
    每个dataframe 中的最后一列列名不能相同，表示时空数据的列为在前，列名相同
    :param grade_list: 等级
    :param save_path: 保存地址
    :param sheet_name: xls 的sheet名
    :return:
    '''
    fo_list.append(ob)
    meger_df_data = pisd.merge_on_id_and_obTime(fo_list)
    ob_data = meger_df_data.iloc[:, -1]
    ob_data = ob_data.values

    colnums = ['level', 'id', 'time']
    title = ''
    for colnum in colnums:
        the_duplicate_values = meger_df_data[colnum].unique()
        if len(the_duplicate_values) == 1:
            title = title + str(the_duplicate_values[0])
        if ':' in title:
            title = title[:-13]
            title = title.translate(str.maketrans(':', ':', string.punctuation))
        save_path = title + '.xls'
    for fo_of_colnum in meger_df_data.iloc[:, 7:-1]:
        fo_of_data = meger_df_data[fo_of_colnum].values
        yon.table.contingency_table(ob_data, fo_of_data, grade=grade, save_path=save_path,
                                    sheet_name=fo_of_colnum)
