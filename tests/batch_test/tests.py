# from batch_test.nmc_vf_base.tests_function import *
# from batch_test.nmc_vf_method import *

import subprocess
import sys
import nmc_verification.nmc_vf_base.tool.path_tools as path_tools
import os


def get_tests_path(path=__file__):
    path = os.path.dirname(path)

    if path[-5:] == 'tests':
        return path
    elif len(path) == 3:
        return
    else:
        path = get_tests_path(path)
        return path


path = get_tests_path()

path_list = path_tools.get_path_list_in_dir(path)

# 挑选出 .py文件路径
py_list = []
for path in path_list:
    if path[-3:] == '.py' and path[-8:] != 'tests.py':
        py_list.append(path)

        print(path + '运行中')
        cmd = ['python', path, 'b', 'c']
        subprocess.call(cmd, 0, None, None, None, None)
