__author__ = "The R & D Center for Weather Forecasting Technology in NMC, CMA"
__version__ = '1.8.3.2'
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif']=["Source Han Sans CN","SimHei"] #用来正常显示中文标签
plt.rcParams['font.serif']=["Times New Roman"] #默认英文字体
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
from . import base
from . import method
from . import perspact
from . import product

