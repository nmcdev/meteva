# nmc_verification
提供气象产品检验相关程序  
打包pip可以下载的python安装包   
1.注册一个pypi账号  
2.编写一个自己的python 项目要发布项目，必须得先有一个自己的项目  
3.建立一个setup.py文件,这个文件是用来打包的.  
4.本地打包项目文件,在命令行上先 cd 到存放setup.py文件的目录，然后用下面的命令:python setup.py sdist bdist_wheel  
5.上传项目到pypi服务器,在setup.py这一级的目录下建立一个系统文件 .pypirc,命令：twine upload dist/*  
6.下载上传的库.pip install nmc_verification  
