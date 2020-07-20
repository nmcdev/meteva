from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count,Process, freeze_support
import time

def multi_operation(process_id,method,**kwargs):
    print("start running the " + str(process_id) + "th sub process")
    paras = method.__code__.co_varnames

    #找出那些需要循环技术的参数
    list_para_name_dict = {}
    for para_name in kwargs.keys():
        for para in paras:
            if para_name.lower() == para.lower():
                if para_name != para:
                    #list_para_name_dict的key记录kwargs中输入参数名称
                    # list_para_name_dict的value记录method需要的参数名称
                    list_para_name_dict[para_name] = para

    op_count = 0
    for key in list_para_name_dict.keys():
        para_value = kwargs[key]
        op_count = len(para_value)


    num = op_count
    start = time.time()
    kwargs_one = {}

    for key in kwargs.keys():
        if key in list_para_name_dict.keys():
            key_new = list_para_name_dict[key]  # 获取method的实际参数名称
            kwargs_one[key_new] = None
        else:
            kwargs_one[key] = kwargs[key]  # 其它参数照常保留

    for i in range(num):
        for key in list_para_name_dict.keys():
            key_new = list_para_name_dict[key]  # 获取method的实际参数名称
            kwargs_one[key_new] = kwargs[key][i]
        method(**kwargs_one)
        #print("***********")
        if process_id == 0:
            end = time.time()
            left_minutes = int((end - start) * (num - i - 1) / ((i + 1) * 60)) + 1
            print("剩余" + str(left_minutes) + "分钟")



def multi_run(process_count,method,** kwargs):
    # 判断那些需要并行的参数
    #
    freeze_support()
    paras = method.__code__.co_varnames
    list_para_name_dict = {}
    op_count_max = 0
    for para_name in kwargs.keys():
        for para in paras:
            if para_name.lower() == para.lower():
                if para_name != para:
                    #list_para_name_dict的key记录了原始的输入参数名称
                    # list_para_name_dict的value记录了更改后的输入参数名称
                    # 如果输入参数已经和method参数大小写不一致，key 和value就相同
                    list_para_name_dict[para_name] = para_name
                    op_count_max = len(kwargs[para_name])

    if len(list_para_name_dict.keys()) ==0:
        #从所有的参数中，找出参数值为列表的参数，并挑选出列表长度最大值

        for para_name in kwargs.keys():
            para_value = kwargs[para_name]
            if isinstance(para_value,list):
                op_count = len(para_value)
                if op_count_max < op_count:
                    op_count_max = op_count
        if op_count_max ==0:
            print("未指定需要并行的参数列表")

        #认为列表长度最大值对应的参数为需要并行的参数名称
        for para_name in kwargs.keys():
            para_value = kwargs[para_name]
            if isinstance(para_value,list):
                op_count = len(para_value)
                if op_count_max == op_count:
                    #list_para_name_dict的key记录了原始的输入参数名称
                    # list_para_name_dict的value记录了更改后的输入参数名称
                    # 如果输入参数已经和method参数大小一致，则对参数名称的大小写进行转换作为传入下一级函数的输入参数名称
                    list_para_name_dict[para_name] = para_name.swapcase()

    #确定可用或需要的线程数
    if process_count<1:
        process_count = 1
    if process_count>cpu_count() -2:
        process_count = cpu_count() -2
    if process_count> op_count_max:
        process_count = op_count_max

    #将执行参数拆解成threed_count份
    kwargs_list =[]
    for k in range(process_count):
        kwargs_k = {"process_id":k,
                    "method":method}
        for key in kwargs.keys():
            if key in list_para_name_dict.keys():
                key_new = list_para_name_dict[key]  #采用大小写和method中不一致的参数名称
                kwargs_k[key_new] = kwargs[key][k::process_count]  #提取部分待运算的参数列表
            else:
                kwargs_k[key] = kwargs[key]  #其它参数照常保留
        kwargs_list.append(kwargs_k)

    PP = []  # 记录进程
    for k in range(process_count):
        tmpp = Process(target=multi_operation, kwargs=kwargs_list[k])
        PP.append(tmpp)

    print('Waiting for all subprocesses done...')
    for pc in PP:
        pc.start()
    for pp in PP:
        pp.join()
    print('All subprocesses done.')