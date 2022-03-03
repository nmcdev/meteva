# 采用以下形式将所有.py 模块导入到fss 目录下
from . import fss
from .fss import *
#
#
# # FSS
# def FSS(Ob, Fo, window_sizes_list=[3], threshold_list=[50], Masker=None):
#     '''
#     :param Ob: 实况数据 2维的numpy
#     :param Fo: 实况数据 2维的numpy
#     :param window_sizes_list: 卷积窗口宽度的列表，以格点数为单位
#     :param threshold_list:  事件发生的阈值
#     :param Masker:  2维的numpy检验的关注区域，在Masker网格值取值为0或1，函数只对网格值等于1的区域的数据进行计算。
#     :return:
#     '''
#     shape = Ob.shape
#     nw = len(window_sizes_list)
#     # print(nw)
#     nt = len(threshold_list)
#     fss = np.zeros((nw, nt))
#     for i in range(nw):
#         kernel = np.ones((nw, nw))
#         # print(kernel)
#         ws = np.sum(kernel)
#         if Masker is not None:
#             masker_sum = np.convolve(Masker, kernel, mode="same") + 1e-10
#         else:
#             masker_sum = np.ones(shape) * ws + 1e-10
#         for j in range(nt):
#             ob_hap = np.zeros(shape)
#             ob_hap[Ob > threshold_list[j]] = 1
#             fo_hap = np.zeros(shape)
#             fo_hap[Fo > threshold_list[j]] = 1
#             ob_hap_sum = np.convolve(ob_hap, kernel, mode="same")
#             fo_hap_sum = np.convolve(fo_hap, kernel, mode="same")
#             ob_hap_p = ob_hap_sum / masker_sum
#             fo_hap_p = fo_hap_sum / masker_sum
#             a1 = np.sum(np.power(ob_hap_p - fo_hap_p, 2))
#             a2 = np.sum(np.power(ob_hap_p, 2)) + np.sum(np.power(fo_hap_p, 2))
#             fss[i, j] = 1 - a1 / (a2 + 1e-10)
#     return fss
#
