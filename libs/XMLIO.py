import sys
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement
from lxml import etree
import codecs

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *


import math
XML_EXT='.xml'
ENCODE_METHOD = 'utf-8'

from libs.BoxItem import *




def loadBoxFromXML(xmlpath):
    assert xmlpath.endswith(XML_EXT), "Unsupport file format"


    parser = etree.XMLParser(encoding=ENCODE_METHOD)
    xmltree = ElementTree.parse(xmlpath, parser=parser).getroot()

    boxList=[]

    for object_iter in xmltree.findall('object'):
        box_elem=object_iter.find('bndbox')
        name_elem=object_iter.find('name')
        score_elem=object_iter.find('score')

        xmin=int(float(box_elem.find('xmin').text))
        ymin=int(float(box_elem.find('ymin').text))
        xmax=int(float(box_elem.find('xmax').text))
        ymax=int(float(box_elem.find('ymax').text))

        name=name_elem.text
        score=''
        try:
            score=score_elem.text
        except:
            pass
            
        boxItem=BoxItem()
        boxItem.setName(name)
        boxItem.setScore(score)
        boxItem.setBox(xmin,ymin,xmax,ymax)
        boxList.append(boxItem)

    
    return boxList


def writeBoxToXML(boxList,xmlpath):
    if boxList==[]:
        return

    top=Element('annotation')

    for boxItem in boxList:

        obj=SubElement(top,'object')
        classType=SubElement(obj,'name')
        classType.text=boxItem.name


        bbox=SubElement(obj,'bndbox')
        xmin=SubElement(bbox,'xmin')
        xmax = SubElement(bbox, 'xmax')
        ymin = SubElement(bbox, 'ymin')
        ymax = SubElement(bbox, 'ymax')

        scoreElem=SubElement(obj,'score')
        scoreElem.text=boxItem.score

        xmin.text=str(int(boxItem.bndbox['xmin']))
        ymin.text = str(int(boxItem.bndbox['ymin']))
        xmax.text = str(int(boxItem.bndbox['xmax']))
        ymax.text = str(int(boxItem.bndbox['ymax']))

    out_file=codecs.open(xmlpath,'w',encoding='utf-8')
    rough_string = ElementTree.tostring(top, 'utf8')
    root = etree.fromstring(rough_string)
    prettifyResult=etree.tostring(root,
                                    pretty_print=True,
                                    encoding='utf-8').replace("  ".encode(), "\t".encode())

    out_file.write(prettifyResult.decode('utf8'))
    out_file.close()




        

