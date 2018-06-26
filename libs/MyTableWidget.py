import sys
import codecs
import re
import subprocess
import sip
import os.path
import shutil

from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from libs.MyGraphicView import *
from libs.ChooseNameForm import *
from libs.XMLIO import *
from libs.Settings import *





class MyTableWidget(QTableWidget):
    def __init__(self,mainWindow):
        super().__init__()
        self.mainWindow=mainWindow
        self.initVariables()

    
    def initVariables(self):
        self.KEY_DELETE=16777223

    def keyPressEvent(self,event):
        if event.key()==self.KEY_DELETE:
            self.mainWindow.graphicView.deleteItem()