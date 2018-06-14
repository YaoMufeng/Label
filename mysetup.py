import sys
from cx_Freeze import setup,Executable


build_exe_options={'packages':['numpy','PyQt5','gdal'],'excludes':[]}


setup(name='Label',
version='3.0',
description='test cx_freeze',
options={'build_exe':build_exe_options},
executables=[Executable('Label.py')])