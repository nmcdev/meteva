# 采用以下形式将所有.py 模块导入到rigider 目录下
from . import fint2d
from . import imomenter
from . import mij
from . import  q_loss_rigid
from . import rigid_transform
from . import rigider
from . import zapsmall

# 采用如下形式将5个用户必要的函数导入到mode模块下
from .rigider import rigid_optimal,rigid_simple
from .rigider import plot_value