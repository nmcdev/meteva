
def get_encoding_of_file(filename,read_rows = 0):
    encoding = None
    strs = ""
    try:
        encoding = "GBK"
        file = open(filename, encoding="GBK")
        if read_rows == 0:
            strs = file.read()
        else:
            if read_rows == 1:
                strs = file.readline()
            else:
                strs = []
                for i in range(read_rows):
                    strs.append(file.readline())
        file.close()

    except:
        try:
            encoding = "UTF-8"
            file = open(filename, encoding="UTF-8")
            if read_rows == 0:
                strs = file.read()
            else:
                if read_rows == 1:
                    strs = file.readline()
                else:
                    strs = []
                    for i in range(read_rows):
                        strs.append(file.readline())
            file.close()
        except:
            try:
                encoding = "GB2312"
                file = open(filename, encoding="GB2312")
                if read_rows == 0:
                    strs = file.read()
                else:
                    if read_rows == 1:
                        strs = file.readline()
                    else:
                        strs = []
                        for i in range(read_rows):
                            strs.append(file.readline())
                file.close()
            except:
                print(filename + "文件编码不是GBK、GB2312或者UTF-8格式，程序暂时不能识别")
                return None
    return encoding,strs