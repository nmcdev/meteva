# _*_ coding: utf-8 _*_
#python setup.py sdist bdist_wheel
#twine upload dist/*
# python setup.py develop  进入meteva目录后执行该命令可将程序库安装为一个开发模式的包

from os import path
from setuptools import find_packages, setup
from codecs import open
name = "meteva"
author ="liucouhua,daikan,wangbaoli,tangbuxing"
version =__import__(name).__version__

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=name,

    version=version,

    description=("A collections of functions for meteorological verification."),
    long_description=long_description,

    # author
    author=author,
    author_email='liucouhua@163.com',

    # LICENSE
    license='GPL3',

    classifiers=[
      'Development Status :: 3 - Alpha',
      'Intended Audience :: Developers',
      'Programming Language :: Python :: 3',
    ],

    packages=find_packages(exclude=['docs', 'tests', 'build', 'dist']),
    include_package_data=True,
    exclude_package_data={'': ['.gitignore']},

    install_requires=[
                      'numpy>=1.12.1',
                      'pandas>=1.0.4',
                      "netCDF4>=1.4.2,<=1.6.5",
                      'scipy>=0.19.0',
                      'xarray>=0.10.0',
                      'scikit-learn>=0.21.2',
                      'matplotlib>=3.2.2',
                      "httplib2>=0.12.0",
                      "protobuf<=3.20.0",
                      "pyshp>=2.1.0",
                      "tables>=3.4.4",
                      "urllib3>=1.21.1",
                      "pynverse>=0.1.4.6",
                      "shapely>=1.8.0"
                      ]
)
