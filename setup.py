# _*_ coding: utf-8 _*_

from os import path
from setuptools import find_packages, setup
from codecs import open
name = "meteva"
author ="liucouhua,daikan,wangbaoli"
version ="1.4.1.2"

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

    install_requires=['numpy>=1.12.1',
                      'scipy>=0.19.0',
                      'pandas>=1.0.1',
                      'xarray>=0.11.0',
                      'scikit-learn>=0.21.2',
                      'matplotlib>=3.3.1',
                      "httplib2>=0.12.0",
                      "protobuf>=3.6.1",
                      "netCDF4>=1.4.2",
                      "seaborn>=0.9.0",
                      "ipywidgets>=7.5.1",
                      "pyshp>=2.1.0",
                      "tables>=3.4.4"
                      ]
)
