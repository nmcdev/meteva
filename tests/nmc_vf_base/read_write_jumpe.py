import  os
def is_NOne(data):
    if data is None:
        print('读取失败')
    else:
        print('读取成功')
        print(data.head())

def is_NOne2(data):
    if data is None:
        print('读取失败')
    else:
        print('读取成功')
        print(data)
def file_is_exist(file_path='a.txt'):
    if os.path.exists(file_path):
        print(file_path,'文件存在')
