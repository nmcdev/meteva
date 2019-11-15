#初始化io下边的四个模块，分别为读出格点数据，写入格点数据，读出站点数据，写入站点数据
from . import read_griddata
from . import write_griddata
from . import read_stadata
from . import write_stadata
from . import DataBlock_pb2
from .GDS_data_service import GDSDataService