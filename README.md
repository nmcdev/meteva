# 全流程检验程序库(whole process evaluation program library of weather forecast)
MetEva程序库由国家气象中心预报技术研发室检验科负责研发，旨在为从数值模式、客观方法、精细化网格预报到预报产品的应用的整个气象产品制作流程中的每个环节进行快速高效的检验，促进跨流程跨部门的检验信息共享，为推进研究型业务和改进预报质量提供技术支撑。  
    The MetEva program library is developed by the Laboratory Division of the Forecast Technology Research and Development Office of the National Meteorological Center. It aims to quickly and efficiently inspect each process in the entire meteorological product production process from numerical models, objective methods, refined grid forecasting to the application of forecast products, promote the sharing of inspection information across processes and departments, and provide technical support for promoting research based operations and improving forecast quality. 
    Aiming at the whole process coverage of the verification algorithm and the comparability of the evaluation results, MetEva adopts a hierarchical architecture including basic layer and functional layer, and designs a modular inspection and calculation process based on a unified data structure. The program library provides over 400 functions around the steps of data reading, data merging and matching, sample selection, sample grouping, inspection calculation and result output for verification. MetEva provides 54 evaluation methods in five categories, which covers most of methods recommended by the World Meteorological Organization and algorithms in domestic specifications. By using matrix calculation in each module and providing parallel scheme for verification algorithms, the operation efficiency is improved.The program library has been released as open source, which can effectively support meteorological departments at all levels to carry out the evaluation of the whole process of weather forecast, so as to promote the development of weather forecast.
 
详细的说明请参见  https://www.showdoc.cc/meteva 

Only Python 3 is supported.

## Dependencies
Other required packages:

   numpy>=1.12.1  
   scipy>=0.19.0  
   pandas>=0.20.0  
   xarray>=0.11.0  
   scikit-learn>=0.21.2  
   matplotlib>=3.3.1  
   httplib2>=0.12.0  
   protobuf>=3.6.1  
   netCDF4>=1.4.2  
   pyshp>=2.1.0  
   seaborn>=0.9.0  
   ipywidgets>=7.5.1

## Install
Using the fellowing command to install packages:
```
  pip install meteva
```
