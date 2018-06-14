

from osgeo import gdal
import numpy as np

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

def isSupportedRasterFile(fileName):
    dotIndex = fileName.rfind('.')
    rear = fileName[dotIndex + 1:len(fileName)]

    supportedType = ['tif', 'img']

    if rear in supportedType:
        return True
    else:
        return False


def readGDALFromFile(dataset, b3=3, b2=2, b1=1):
    # dataset=gdal.Open(fileName,gdal.GA_ReadOnly)

    if not dataset:
        print("fail to open gdal file")
        return

    rasterCount = dataset.RasterCount
    if rasterCount < b1 or rasterCount < b2 or rasterCount < b3:
        print("所选波段越界")
        return

    band1 = dataset.GetRasterBand(b1)

    thresh = 10000
    scale = thresh / band1.XSize
    width = band1.XSize
    height = band1.YSize

    x = width
    y = height

    # 缩放图像
    if scale < 1:
        x = thresh
        y = int(scale * band1.YSize)

    bandCount = dataset.RasterCount

    data1 = band1.ReadAsArray(0, 0, width, height, x, y)
    data1 = data1.reshape(y, x, 1).astype(np.uint8)

    img_arr = []
    print("function call")
    if bandCount == 1:
        img_arr = data1
        print("single band call")
        img = QtGui.QImage(img_arr[:, :], img_arr.shape[1],
                           img_arr.shape[0], img_arr.shape[1],
                           QtGui.QImage.Format_Indexed8)

        """mp=QPixmap.fromImage(img)
        print("single band")"""
        return (img)

    elif bandCount == 3:
        print("three band call")

        band2 = dataset.GetRasterBand(b2)
        band3 = dataset.GetRasterBand(b3)
        data2 = band2.ReadAsArray(0, 0, width, height, x, y).astype(np.uint8)
        data3 = band3.ReadAsArray(0, 0, width, height, x, y).astype(np.uint8)

        # data2=band2.ReadAsArray(0,0,width,height)
        # data3=band3.ReadAsArray(0,0,width,height)

        print('width,height=', width, height)
        print('x,y=', x, y)
        data2 = data2.reshape(y, x, 1)
        data3 = data3.reshape(y, x, 1)

        img_arr = data1
        img_arr = np.append(img_arr, data2, axis=2)
        img_arr = np.append(img_arr, data3, axis=2)

        print("Initialize QImage")
        img = QImage(img_arr[:, :], img_arr.shape[1],
                           img_arr.shape[0], img_arr.shape[1] * 3,
                           QImage.Format_RGB888)
        return (img)


    elif bandCount > 3:
        print("three band call")

        band2 = dataset.GetRasterBand(b2)
        band3 = dataset.GetRasterBand(b3)
        data2 = band2.ReadAsArray(0, 0, width, height, x, y).astype(np.uint8)
        data3 = band3.ReadAsArray(0, 0, width, height, x, y).astype(np.uint8)

        # data2=band2.ReadAsArray(0,0,width,height)
        # data3=band3.ReadAsArray(0,0,width,height)

        print('width,height=', width, height)
        print('x,y=', x, y)
        data2 = data2.reshape(y, x, 1)
        data3 = data3.reshape(y, x, 1)

        img_arr = data3
        img_arr = np.append(img_arr, data2, axis=2)
        img_arr = np.append(img_arr, data1, axis=2)

        print("Initialize QImage")
        img = QtGui.QImage(img_arr[:, :], img_arr.shape[1],
                           img_arr.shape[0], img_arr.shape[1] * 3,
                           QtGui.QImage.Format_RGB888)
        return (img)
        """print("Initialize QPixmap")

        mp=QPixmap.fromImage(img)
        print("three band")
        return(mp)"""
    else:
        return


